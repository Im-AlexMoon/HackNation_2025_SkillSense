"""
Profile Builder
Generates comprehensive skill profiles from multiple data sources
"""
import json
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from data_ingestion.pdf_extractor import PDFExtractor
from data_ingestion.github_collector import GitHubCollector
from data_ingestion.text_processor import TextProcessor
from skill_extraction.skill_extractor import SkillExtractor
from skill_extraction.confidence_scorer import ConfidenceScorer, ScoredSkill


@dataclass
class SkillProfile:
    """Complete skill profile for an individual"""
    name: Optional[str]
    summary: str
    skills: List[ScoredSkill]
    top_skills: List[ScoredSkill]
    skill_categories: Dict[str, List[ScoredSkill]]
    data_sources: List[str]
    metadata: Dict
    raw_data: Dict


class ProfileBuilder:
    """Builds comprehensive skill profiles from multiple sources"""

    def __init__(self):
        self.pdf_extractor = PDFExtractor()
        self.github_collector = GitHubCollector()
        self.text_processor = TextProcessor()
        self.skill_extractor = SkillExtractor()
        self.confidence_scorer = ConfidenceScorer()

    def build_profile(
        self,
        name: Optional[str] = None,
        cv_path: Optional[str] = None,
        cv_paths: Optional[List[str]] = None,
        github_username: Optional[str] = None,
        personal_statement: Optional[str] = None,
        reference_letter: Optional[str] = None,
        linkedin_data: Optional[Dict] = None
    ) -> SkillProfile:
        """
        Build a comprehensive skill profile from available sources

        Args:
            name: Person's name
            cv_path: Path to single CV PDF (deprecated, use cv_paths)
            cv_paths: List of paths to CV PDFs (supports multiple CVs)
            github_username: GitHub username
            personal_statement: Personal statement text
            reference_letter: Reference letter text
            linkedin_data: LinkedIn profile data (simulated or extracted)

        Returns:
            SkillProfile object
        """
        all_extracted_skills = []
        data_sources = []
        raw_data = {}

        # Handle backward compatibility: convert single cv_path to list
        if cv_path and not cv_paths:
            cv_paths = [cv_path]

        # Process CV(s) - supports multiple files
        if cv_paths:
            print(f"📄 Processing {len(cv_paths)} CV file(s)...")
            all_cv_data = []
            combined_cv_text = []

            for idx, cv_file_path in enumerate(cv_paths):
                try:
                    print(f"   Processing CV {idx + 1}/{len(cv_paths)}: {cv_file_path}")
                    cv_data = self.pdf_extractor.extract_structured_cv(cv_file_path)
                    cv_skills = self.skill_extractor.extract_all_skills(
                        cv_data['raw_text'],
                        source=f'cv_{idx + 1}'
                    )
                    all_extracted_skills.extend(cv_skills)
                    all_cv_data.append(cv_data)
                    combined_cv_text.append(cv_data['raw_text'])
                    print(f"      Found {len(cv_skills)} skills from CV {idx + 1}")
                except Exception as e:
                    print(f"      Error processing CV {idx + 1}: {str(e)}")

            if all_cv_data:
                data_sources.append('cv')
                # Store all CVs with combined text for RAG
                raw_data['cv'] = {
                    'files': all_cv_data,
                    'raw_text': '\n\n'.join(combined_cv_text),
                    'count': len(all_cv_data)
                }
                print(f"   Total CV skills extracted: {sum(1 for s in all_extracted_skills if s.source.startswith('cv'))}")

        # Process GitHub
        if github_username:
            print(f"🐙 Fetching GitHub profile for {github_username}...")
            try:
                github_data = self.github_collector.get_comprehensive_profile(github_username)

                # Extract skills from GitHub data
                github_text = self._format_github_for_extraction(github_data)
                github_skills = self.skill_extractor.extract_all_skills(
                    github_text,
                    source='github'
                )
                all_extracted_skills.extend(github_skills)
                data_sources.append('github')
                raw_data['github'] = github_data
                print(f"   ✓ Found {len(github_skills)} skills from GitHub")
            except Exception as e:
                print(f"   ✗ Error processing GitHub: {str(e)}")

        # Process Personal Statement
        if personal_statement:
            print("📝 Processing personal statement...")
            try:
                statement_data = self.text_processor.process_personal_statement(personal_statement)
                statement_skills = self.skill_extractor.extract_all_skills(
                    personal_statement,
                    source='personal_statement'
                )
                all_extracted_skills.extend(statement_skills)
                data_sources.append('personal_statement')
                raw_data['personal_statement'] = statement_data
                print(f"   ✓ Found {len(statement_skills)} skills from statement")
            except Exception as e:
                print(f"   ✗ Error processing statement: {str(e)}")

        # Process Reference Letter
        if reference_letter:
            print("✉️ Processing reference letter...")
            try:
                reference_data = self.text_processor.process_reference_letter(reference_letter)
                reference_skills = self.skill_extractor.extract_all_skills(
                    reference_letter,
                    source='reference_letter'
                )
                all_extracted_skills.extend(reference_skills)
                data_sources.append('reference_letter')
                raw_data['reference_letter'] = reference_data
                print(f"   ✓ Found {len(reference_skills)} skills from reference")
            except Exception as e:
                print(f"   ✗ Error processing reference: {str(e)}")

        # Process LinkedIn data (if provided)
        if linkedin_data:
            print("💼 Processing LinkedIn data...")
            try:
                linkedin_text = self._format_linkedin_for_extraction(linkedin_data)
                linkedin_skills = self.skill_extractor.extract_all_skills(
                    linkedin_text,
                    source='linkedin'
                )
                all_extracted_skills.extend(linkedin_skills)
                data_sources.append('linkedin')
                raw_data['linkedin'] = linkedin_data
                print(f"   ✓ Found {len(linkedin_skills)} skills from LinkedIn")
            except Exception as e:
                print(f"   ✗ Error processing LinkedIn: {str(e)}")

        # Score all skills
        print("\n🎯 Calculating confidence scores...")
        scored_skills = self.confidence_scorer.score_skill_profile(all_extracted_skills)

        # Filter low confidence skills
        filtered_skills = self.confidence_scorer.filter_by_confidence(scored_skills, min_confidence=0.3)

        # Get top skills
        top_skills = self.confidence_scorer.get_top_skills(filtered_skills, top_n=20)

        # Categorize skills
        skill_categories = self._categorize_skills(filtered_skills)

        # Generate summary
        summary = self._generate_summary(filtered_skills, data_sources)

        print(f"✅ Profile complete! Total skills identified: {len(filtered_skills)}")

        return SkillProfile(
            name=name,
            summary=summary,
            skills=filtered_skills,
            top_skills=top_skills,
            skill_categories=skill_categories,
            data_sources=data_sources,
            metadata={
                'created_at': datetime.now().isoformat(),
                'total_skills': len(filtered_skills),
                'sources_count': len(data_sources)
            },
            raw_data=raw_data
        )

    def _format_github_for_extraction(self, github_data: Dict) -> str:
        """Format GitHub data into text for skill extraction"""
        text_parts = []

        # Profile info
        profile = github_data.get('profile', {})
        if profile.get('bio'):
            text_parts.append(profile['bio'])

        # Skills from repository analysis
        skills = github_data.get('extracted_skills', {})

        # Languages
        languages = skills.get('primary_languages', [])
        if languages:
            text_parts.append(f"Primary programming languages: {', '.join(languages)}")

        # Topics
        topics = skills.get('topics', [])
        if topics:
            text_parts.append(f"Areas of expertise: {', '.join(topics)}")

        # Repository descriptions
        for repo in github_data.get('repositories', [])[:10]:
            if repo.get('description'):
                text_parts.append(repo['description'])

        return '\n'.join(text_parts)

    def _format_linkedin_for_extraction(self, linkedin_data: Dict) -> str:
        """Format LinkedIn data into text for skill extraction"""
        text_parts = []

        # Headline
        if linkedin_data.get('headline'):
            text_parts.append(linkedin_data['headline'])

        # Summary
        if linkedin_data.get('summary'):
            text_parts.append(linkedin_data['summary'])

        # Experience
        for exp in linkedin_data.get('experience', []):
            text_parts.append(exp.get('title', ''))
            text_parts.append(exp.get('description', ''))

        # Skills (if listed)
        if linkedin_data.get('skills'):
            text_parts.append(f"Skills: {', '.join(linkedin_data['skills'])}")

        return '\n'.join(text_parts)

    def _categorize_skills(self, scored_skills: List[ScoredSkill]) -> Dict[str, List[ScoredSkill]]:
        """Organize skills by category"""
        categories = {}

        for skill in scored_skills:
            category = skill.category
            if category not in categories:
                categories[category] = []
            categories[category].append(skill)

        return categories

    def _generate_summary(self, skills: List[ScoredSkill], sources: List[str]) -> str:
        """Generate a text summary of the skill profile"""
        if not skills:
            return "No skills identified from available sources."

        # Count by category
        category_counts = {}
        for skill in skills:
            cat = skill.category
            if cat not in category_counts:
                category_counts[cat] = 0
            category_counts[cat] += 1

        # Get top categories
        top_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:3]

        # Build summary
        summary_parts = [
            f"Analyzed {len(sources)} data source(s) and identified {len(skills)} distinct skills.",
            f"Top skill areas: {', '.join([cat for cat, _ in top_categories])}.",
            f"Primary strengths: {', '.join([s.skill_name for s in skills[:5]])}."
        ]

        return ' '.join(summary_parts)

    def export_profile(self, profile: SkillProfile, output_path: str, format: str = 'json'):
        """
        Export profile to file

        Args:
            profile: SkillProfile object
            output_path: Output file path
            format: Output format ('json' or 'txt')
        """
        if format == 'json':
            # Convert to dict
            profile_dict = {
                'name': profile.name,
                'summary': profile.summary,
                'skills': [self.confidence_scorer.export_to_dict(s) for s in profile.skills],
                'top_skills': [s.skill_name for s in profile.top_skills],
                'data_sources': profile.data_sources,
                'metadata': profile.metadata
            }

            with open(output_path, 'w') as f:
                json.dump(profile_dict, f, indent=2)

        elif format == 'txt':
            with open(output_path, 'w') as f:
                f.write(f"Skill Profile: {profile.name or 'Unknown'}\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"{profile.summary}\n\n")
                f.write("Top Skills:\n")
                for i, skill in enumerate(profile.top_skills, 1):
                    f.write(f"{i}. {skill.skill_name} (Confidence: {skill.final_confidence:.2f})\n")


# Example usage
if __name__ == "__main__":
    builder = ProfileBuilder()

    # Example usage
    # profile = builder.build_profile(
    #     name="John Doe",
    #     github_username="octocat"
    # )
    # print(f"\nTop Skills: {[s.skill_name for s in profile.top_skills[:5]]}")

    print("Profile Builder module loaded successfully")
