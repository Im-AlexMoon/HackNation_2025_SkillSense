"""
Skill Extraction Engine
Extracts both explicit and implicit skills using NLP and semantic analysis
"""
import json
import re
from typing import Dict, List, Set, Tuple, Optional
from pathlib import Path
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer
import numpy as np


@dataclass
class ExtractedSkill:
    """Represents an extracted skill with metadata"""
    skill_name: str
    category: str
    detection_method: str  # 'explicit', 'contextual', 'semantic'
    confidence: float
    evidence: List[str]  # Text snippets showing evidence
    source: str  # Where the skill was found


class SkillExtractor:
    """Extracts skills from text using multiple methods"""

    def __init__(self, skill_taxonomy_path: Optional[str] = None):
        """
        Initialize skill extractor

        Args:
            skill_taxonomy_path: Path to skill taxonomy JSON file
        """
        # Load skill taxonomy
        if skill_taxonomy_path is None:
            skill_taxonomy_path = Path(__file__).parent.parent.parent / 'config' / 'skill_taxonomy.json'

        with open(skill_taxonomy_path, 'r') as f:
            self.taxonomy = json.load(f)

        # Build skill sets
        self.technical_skills = self._flatten_skills(self.taxonomy.get('technical_skills', {}))
        self.soft_skills = self._flatten_skills(self.taxonomy.get('soft_skills', {}))
        self.domain_skills = self._flatten_skills(self.taxonomy.get('domain_knowledge', {}))
        self.all_skills = self.technical_skills | self.soft_skills | self.domain_skills

        # Load synonyms
        self.synonyms = self.taxonomy.get('skill_synonyms', {})

        # Initialize sentence transformer for semantic similarity
        # Using a lightweight model for hackathon speed
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

        # Pre-compute skill embeddings
        self.skill_embeddings = self._compute_skill_embeddings()

    def _flatten_skills(self, skill_dict: Dict) -> Set[str]:
        """Flatten nested skill dictionary into a set"""
        skills = set()
        for category, skill_list in skill_dict.items():
            if isinstance(skill_list, list):
                skills.update(skill_list)
        return skills

    def _compute_skill_embeddings(self) -> Dict[str, np.ndarray]:
        """Pre-compute embeddings for all skills"""
        skill_list = list(self.all_skills)
        embeddings = self.model.encode(skill_list)
        return {skill: emb for skill, emb in zip(skill_list, embeddings)}

    def extract_explicit_skills(self, text: str, source: str = 'unknown') -> List[ExtractedSkill]:
        """
        Extract explicitly mentioned skills using keyword matching

        Args:
            text: Text to analyze
            source: Source identifier

        Returns:
            List of ExtractedSkill objects
        """
        extracted = []
        text_lower = text.lower()

        # Check for each skill in taxonomy
        for skill in self.all_skills:
            skill_lower = skill.lower()

            # Direct match
            pattern = r'\b' + re.escape(skill_lower) + r'\b'
            matches = list(re.finditer(pattern, text_lower, re.IGNORECASE))

            if matches:
                # Extract evidence (context around match)
                evidence = []
                for match in matches[:3]:  # Limit to 3 examples
                    start = max(0, match.start() - 50)
                    end = min(len(text), match.end() + 50)
                    context = text[start:end].strip()
                    evidence.append(f"...{context}...")

                # Determine category
                category = self._categorize_skill(skill)

                extracted.append(ExtractedSkill(
                    skill_name=skill,
                    category=category,
                    detection_method='explicit',
                    confidence=1.0,  # Will be adjusted by confidence scorer
                    evidence=evidence,
                    source=source
                ))

        # Check for synonyms
        for canonical, synonym_list in self.synonyms.items():
            for synonym in synonym_list:
                pattern = r'\b' + re.escape(synonym.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    category = self._categorize_skill(canonical)
                    extracted.append(ExtractedSkill(
                        skill_name=canonical,
                        category=category,
                        detection_method='explicit',
                        confidence=0.95,  # Slightly lower for synonyms
                        evidence=[f"Found synonym: {synonym}"],
                        source=source
                    ))

        return extracted

    def extract_implicit_skills(self, text: str, source: str = 'unknown', threshold: float = 0.5) -> List[ExtractedSkill]:
        """
        Extract implicit skills using semantic similarity

        Args:
            text: Text to analyze
            source: Source identifier
            threshold: Similarity threshold (0-1)

        Returns:
            List of ExtractedSkill objects
        """
        extracted = []

        # Split text into sentences or chunks
        sentences = self._split_into_chunks(text)

        # Encode text chunks
        chunk_embeddings = self.model.encode(sentences)

        # Compare with skill embeddings
        for skill, skill_emb in self.skill_embeddings.items():
            max_similarity = 0
            best_evidence = ""

            for chunk, chunk_emb in zip(sentences, chunk_embeddings):
                # Calculate cosine similarity
                similarity = np.dot(skill_emb, chunk_emb) / (
                    np.linalg.norm(skill_emb) * np.linalg.norm(chunk_emb)
                )

                if similarity > max_similarity:
                    max_similarity = similarity
                    best_evidence = chunk

            # If similarity exceeds threshold and skill not already explicitly found
            if max_similarity >= threshold:
                category = self._categorize_skill(skill)

                extracted.append(ExtractedSkill(
                    skill_name=skill,
                    category=category,
                    detection_method='semantic',
                    confidence=float(max_similarity),
                    evidence=[f"Inferred from: {best_evidence[:100]}..."],
                    source=source
                ))

        return extracted

    def extract_contextual_skills(self, text: str, source: str = 'unknown') -> List[ExtractedSkill]:
        """
        Extract skills based on contextual patterns

        Args:
            text: Text to analyze
            source: Source identifier

        Returns:
            List of ExtractedSkill objects
        """
        extracted = []

        # Define contextual patterns that indicate skills
        patterns = [
            (r'experience (?:with|in) ([^.,]+)', 'contextual', 0.8),
            (r'proficient (?:with|in) ([^.,]+)', 'contextual', 0.9),
            (r'skilled (?:with|in|at) ([^.,]+)', 'contextual', 0.85),
            (r'expertise (?:with|in) ([^.,]+)', 'contextual', 0.9),
            (r'knowledge of ([^.,]+)', 'contextual', 0.75),
            (r'familiar with ([^.,]+)', 'contextual', 0.7),
            (r'worked with ([^.,]+)', 'contextual', 0.75),
            (r'using ([A-Z][a-z]+(?:[A-Z][a-z]+)*)', 'contextual', 0.7),  # CamelCase
        ]

        for pattern, method, base_confidence in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)

            for match in matches:
                skill_text = match.group(1).strip()

                # Check if extracted text matches known skills
                for skill in self.all_skills:
                    if skill.lower() in skill_text.lower() or skill_text.lower() in skill.lower():
                        category = self._categorize_skill(skill)

                        # Extract context
                        start = max(0, match.start() - 30)
                        end = min(len(text), match.end() + 30)
                        context = text[start:end].strip()

                        extracted.append(ExtractedSkill(
                            skill_name=skill,
                            category=category,
                            detection_method=method,
                            confidence=base_confidence,
                            evidence=[f"...{context}..."],
                            source=source
                        ))

        return extracted

    def extract_all_skills(self, text: str, source: str = 'unknown') -> List[ExtractedSkill]:
        """
        Extract skills using all methods

        Args:
            text: Text to analyze
            source: Source identifier

        Returns:
            Combined list of ExtractedSkill objects (deduplicated)
        """
        explicit = self.extract_explicit_skills(text, source)
        contextual = self.extract_contextual_skills(text, source)

        # Combine and deduplicate
        all_skills = explicit + contextual

        # Remove duplicates (keep highest confidence)
        skill_map = {}
        for skill in all_skills:
            key = (skill.skill_name, skill.source)
            if key not in skill_map or skill.confidence > skill_map[key].confidence:
                skill_map[key] = skill

        return list(skill_map.values())

    def _categorize_skill(self, skill: str) -> str:
        """Determine the category of a skill"""
        if skill in self.technical_skills:
            # Find specific subcategory
            for category, skills in self.taxonomy.get('technical_skills', {}).items():
                if skill in skills:
                    return f"technical_{category}"
            return "technical"
        elif skill in self.soft_skills:
            for category, skills in self.taxonomy.get('soft_skills', {}).items():
                if skill in skills:
                    return f"soft_{category}"
            return "soft"
        elif skill in self.domain_skills:
            for category, skills in self.taxonomy.get('domain_knowledge', {}).items():
                if skill in skills:
                    return f"domain_{category}"
            return "domain"
        return "other"

    def _split_into_chunks(self, text: str, chunk_size: int = 200) -> List[str]:
        """Split text into chunks for semantic analysis"""
        # Split by sentences first
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        # Group into chunks
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) < chunk_size:
                current_chunk += " " + sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks if chunks else [text]


# Example usage
if __name__ == "__main__":
    extractor = SkillExtractor()

    sample_text = """
    I have extensive experience with Python and JavaScript, particularly in web development
    using React and Node.js. I've worked on machine learning projects using TensorFlow and
    have strong knowledge of data analysis with pandas. I'm proficient in cloud technologies
    including AWS and Docker.
    """

    # skills = extractor.extract_all_skills(sample_text, source='cv')
    # for skill in skills[:5]:
    #     print(f"{skill.skill_name} ({skill.category}) - {skill.detection_method}")

    print("Skill Extractor module loaded successfully")
