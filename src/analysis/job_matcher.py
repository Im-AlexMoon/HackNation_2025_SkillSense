"""
Job Matcher
Matches skill profiles to job roles and identifies skill gaps
"""
import json
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from dataclasses import dataclass
import sys

sys.path.append(str(Path(__file__).parent.parent))
from skill_extraction.confidence_scorer import ScoredSkill


@dataclass
class JobRole:
    """Represents a job role with required skills"""
    title: str
    description: str
    required_skills: List[str]
    preferred_skills: List[str]
    category: str


@dataclass
class JobMatch:
    """Represents a match between a profile and a job role"""
    job_title: str
    match_score: float
    matched_skills: List[str]
    missing_required: List[str]
    missing_preferred: List[str]
    skill_gaps: List[str]
    recommendation: str


class JobMatcher:
    """Matches skill profiles to job opportunities and identifies gaps"""

    def __init__(self, job_roles_path: Optional[str] = None):
        """
        Initialize job matcher

        Args:
            job_roles_path: Path to job roles database
        """
        self.job_roles = self._load_job_roles(job_roles_path)

    def _load_job_roles(self, path: Optional[str]) -> List[JobRole]:
        """Load job roles from configuration"""
        # If no path provided, use default job roles
        if path is None:
            return self._get_default_job_roles()

        try:
            with open(path, 'r') as f:
                data = json.load(f)
                return [JobRole(**role) for role in data['roles']]
        except:
            return self._get_default_job_roles()

    def _get_default_job_roles(self) -> List[JobRole]:
        """Get default job role templates"""
        return [
            JobRole(
                title="Full Stack Developer",
                description="Build and maintain web applications using modern frameworks",
                required_skills=["JavaScript", "HTML", "CSS", "React", "Node.js", "SQL"],
                preferred_skills=["TypeScript", "Docker", "AWS", "Git", "REST API"],
                category="Software Engineering"
            ),
            JobRole(
                title="Data Scientist",
                description="Analyze data and build ML models",
                required_skills=["Python", "Machine Learning", "Statistics", "SQL", "Pandas"],
                preferred_skills=["TensorFlow", "PyTorch", "R", "Big Data", "Data Visualization"],
                category="Data Science"
            ),
            JobRole(
                title="Frontend Developer",
                description="Create responsive user interfaces",
                required_skills=["JavaScript", "HTML", "CSS", "React", "TypeScript"],
                preferred_skills=["Vue.js", "Angular", "Tailwind CSS", "Webpack", "Git"],
                category="Software Engineering"
            ),
            JobRole(
                title="Backend Developer",
                description="Build server-side applications and APIs",
                required_skills=["Python", "Node.js", "SQL", "REST API", "Docker"],
                preferred_skills=["MongoDB", "Redis", "Kubernetes", "AWS", "GraphQL"],
                category="Software Engineering"
            ),
            JobRole(
                title="Machine Learning Engineer",
                description="Design and deploy ML systems",
                required_skills=["Python", "Machine Learning", "TensorFlow", "PyTorch", "Docker"],
                preferred_skills=["Kubernetes", "MLOps", "AWS", "Spark", "Deep Learning"],
                category="AI/ML"
            ),
            JobRole(
                title="DevOps Engineer",
                description="Automate infrastructure and deployment pipelines",
                required_skills=["Linux", "Docker", "Kubernetes", "CI/CD", "AWS"],
                preferred_skills=["Terraform", "Ansible", "Jenkins", "Python", "Bash"],
                category="Infrastructure"
            ),
            JobRole(
                title="Product Manager",
                description="Define product strategy and roadmap",
                required_skills=["Product Management", "Agile Methodologies", "Stakeholder Management", "Data Analysis"],
                preferred_skills=["SQL", "User Research", "A/B Testing", "Wireframing", "Market Research"],
                category="Product"
            ),
            JobRole(
                title="UX/UI Designer",
                description="Design user experiences and interfaces",
                required_skills=["UI/UX Design", "Figma", "Prototyping", "User Research", "Wireframing"],
                preferred_skills=["Adobe XD", "Sketch", "HTML", "CSS", "Graphic Design"],
                category="Design"
            ),
            JobRole(
                title="Data Analyst",
                description="Extract insights from data",
                required_skills=["SQL", "Data Analysis", "Excel", "Data Visualization", "Statistics"],
                preferred_skills=["Python", "Tableau", "Power BI", "R", "Business Analysis"],
                category="Data"
            ),
            JobRole(
                title="Cloud Architect",
                description="Design cloud infrastructure solutions",
                required_skills=["AWS", "Azure", "Cloud Architecture", "Networking", "Security"],
                preferred_skills=["Terraform", "Kubernetes", "Docker", "Python", "Cost Optimization"],
                category="Cloud"
            )
        ]

    def match_profile_to_jobs(
        self,
        user_skills: List[ScoredSkill],
        top_n: int = 5
    ) -> List[JobMatch]:
        """
        Match user's skill profile to job roles

        Args:
            user_skills: List of user's ScoredSkill objects
            top_n: Number of top matches to return

        Returns:
            List of JobMatch objects sorted by match score
        """
        # Create skill name set for quick lookup
        user_skill_names = {skill.skill_name for skill in user_skills}

        matches = []

        for job in self.job_roles:
            match = self._calculate_match(job, user_skill_names, user_skills)
            matches.append(match)

        # Sort by match score
        matches.sort(key=lambda x: x.match_score, reverse=True)

        return matches[:top_n]

    def _calculate_match(
        self,
        job: JobRole,
        user_skill_names: set,
        user_skills: List[ScoredSkill]
    ) -> JobMatch:
        """Calculate match score for a specific job"""
        # Find matched skills
        matched_required = [s for s in job.required_skills if s in user_skill_names]
        matched_preferred = [s for s in job.preferred_skills if s in user_skill_names]

        # Find missing skills
        missing_required = [s for s in job.required_skills if s not in user_skill_names]
        missing_preferred = [s for s in job.preferred_skills if s not in user_skill_names]

        # Calculate match score
        required_weight = 0.7
        preferred_weight = 0.3

        required_score = len(matched_required) / len(job.required_skills) if job.required_skills else 0
        preferred_score = len(matched_preferred) / len(job.preferred_skills) if job.preferred_skills else 0

        match_score = (required_score * required_weight) + (preferred_score * preferred_weight)

        # Generate skill gaps (prioritize required)
        skill_gaps = missing_required + missing_preferred

        # Generate recommendation
        recommendation = self._generate_recommendation(match_score, len(missing_required))

        return JobMatch(
            job_title=job.title,
            match_score=round(match_score, 3),
            matched_skills=matched_required + matched_preferred,
            missing_required=missing_required,
            missing_preferred=missing_preferred,
            skill_gaps=skill_gaps,
            recommendation=recommendation
        )

    def _generate_recommendation(self, match_score: float, missing_required_count: int) -> str:
        """Generate recommendation text based on match"""
        if match_score >= 0.8:
            return "Excellent match! You meet most requirements for this role."
        elif match_score >= 0.6:
            return "Good match! Consider developing a few more skills to strengthen your candidacy."
        elif match_score >= 0.4:
            return f"Moderate match. Focus on acquiring {missing_required_count} required skill(s)."
        else:
            return "This role may require significant upskilling."

    def identify_skill_gaps(
        self,
        user_skills: List[ScoredSkill],
        target_job: str
    ) -> Dict[str, any]:
        """
        Identify skill gaps for a specific target job

        Args:
            user_skills: User's skills
            target_job: Target job title

        Returns:
            Dictionary with gap analysis
        """
        # Find the job role
        job = next((j for j in self.job_roles if j.title.lower() == target_job.lower()), None)

        if not job:
            return {"error": f"Job role '{target_job}' not found"}

        user_skill_names = {skill.skill_name for skill in user_skills}

        matched_required = [s for s in job.required_skills if s in user_skill_names]
        matched_preferred = [s for s in job.preferred_skills if s in user_skill_names]
        missing_required = [s for s in job.required_skills if s not in user_skill_names]
        missing_preferred = [s for s in job.preferred_skills if s not in user_skill_names]

        return {
            'target_role': job.title,
            'description': job.description,
            'readiness_score': len(matched_required) / len(job.required_skills) if job.required_skills else 0,
            'matched_required': matched_required,
            'matched_preferred': matched_preferred,
            'gaps': {
                'critical': missing_required,
                'beneficial': missing_preferred
            },
            'recommendations': self._generate_learning_path(missing_required, missing_preferred)
        }

    def _generate_learning_path(
        self,
        missing_required: List[str],
        missing_preferred: List[str]
    ) -> List[Dict[str, str]]:
        """Generate learning recommendations"""
        recommendations = []

        # Prioritize required skills
        for i, skill in enumerate(missing_required[:3], 1):
            recommendations.append({
                'priority': 'High',
                'skill': skill,
                'action': f'Focus on learning {skill} - this is a required skill'
            })

        # Add some preferred skills
        for skill in missing_preferred[:2]:
            recommendations.append({
                'priority': 'Medium',
                'skill': skill,
                'action': f'Consider learning {skill} to strengthen your profile'
            })

        return recommendations

    def get_career_paths(self, user_skills: List[ScoredSkill]) -> Dict[str, List[str]]:
        """
        Suggest career paths based on current skills

        Args:
            user_skills: User's skills

        Returns:
            Dictionary with career path suggestions
        """
        matches = self.match_profile_to_jobs(user_skills, top_n=10)

        # Group by category
        paths = {}
        for match in matches:
            # Find job category
            job = next((j for j in self.job_roles if j.title == match.job_title), None)
            if job:
                category = job.category
                if category not in paths:
                    paths[category] = []
                paths[category].append({
                    'title': match.job_title,
                    'match_score': match.match_score,
                    'skill_gaps': len(match.skill_gaps)
                })

        return paths


# Example usage
if __name__ == "__main__":
    matcher = JobMatcher()
    print(f"Loaded {len(matcher.job_roles)} job roles")
    print("Job Matcher module loaded successfully")
