"""
Confidence Scorer
Calculates confidence scores for extracted skills based on source reliability and detection method
"""
import json
from typing import Dict, List
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass
class ScoredSkill:
    """Skill with calculated confidence score"""
    skill_name: str
    category: str
    final_confidence: float
    sources: List[str]
    evidence: List[str]
    confidence_breakdown: Dict[str, float]


class ConfidenceScorer:
    """Calculates and adjusts confidence scores for extracted skills"""

    def __init__(self, source_weights_path: str = None):
        """
        Initialize confidence scorer

        Args:
            source_weights_path: Path to source weights configuration
        """
        if source_weights_path is None:
            source_weights_path = Path(__file__).parent.parent.parent / 'config' / 'source_weights.json'

        with open(source_weights_path, 'r') as f:
            self.config = json.load(f)

        self.source_weights = self.config['source_reliability_weights']
        self.method_weights = self.config['skill_detection_methods']
        self.thresholds = self.config['confidence_thresholds']

    def score_skill(self, skill_name: str, category: str, detections: List[Dict]) -> ScoredSkill:
        """
        Calculate confidence score for a skill based on multiple detections

        Args:
            skill_name: Name of the skill
            category: Skill category
            detections: List of detection instances with source, method, and evidence

        Returns:
            ScoredSkill with calculated confidence
        """
        if not detections:
            return ScoredSkill(
                skill_name=skill_name,
                category=category,
                final_confidence=0.0,
                sources=[],
                evidence=[],
                confidence_breakdown={}
            )

        # Aggregate confidence from all detections
        total_confidence = 0
        sources = set()
        all_evidence = []
        breakdown = {}

        for detection in detections:
            source = detection.get('source', 'unknown')
            method = detection.get('detection_method', 'explicit')
            evidence = detection.get('evidence', [])
            base_confidence = detection.get('confidence', 1.0)

            # Get source weight for this skill category
            source_weight = self._get_source_weight(source, category)

            # Get method weight
            method_weight = self.method_weights.get(method, {}).get('weight', 0.7)

            # Calculate weighted confidence for this detection
            detection_confidence = base_confidence * source_weight * method_weight

            total_confidence += detection_confidence
            sources.add(source)
            all_evidence.extend(evidence)

            # Track breakdown
            key = f"{source}_{method}"
            breakdown[key] = detection_confidence

        # Calculate final confidence (average with boost for multiple sources)
        avg_confidence = total_confidence / len(detections)

        # Apply multi-source bonus (up to 20% boost)
        source_bonus = min(0.2, (len(sources) - 1) * 0.1)
        final_confidence = min(1.0, avg_confidence + source_bonus)

        # Determine confidence level
        breakdown['average'] = avg_confidence
        breakdown['multi_source_bonus'] = source_bonus
        breakdown['final'] = final_confidence
        breakdown['level'] = self._get_confidence_level(final_confidence)

        return ScoredSkill(
            skill_name=skill_name,
            category=category,
            final_confidence=round(final_confidence, 3),
            sources=list(sources),
            evidence=all_evidence[:5],  # Limit evidence to top 5
            confidence_breakdown=breakdown
        )

    def _get_source_weight(self, source: str, category: str) -> float:
        """
        Get source reliability weight for a specific category

        Args:
            source: Source identifier (github, cv, linkedin, etc.)
            category: Skill category (technical, soft, domain)

        Returns:
            Weight value (0-1)
        """
        source_config = self.source_weights.get(source.lower(), {})

        # Determine category type
        if category.startswith('technical'):
            category_key = 'technical_skills'
        elif category.startswith('soft'):
            category_key = 'soft_skills'
        elif category.startswith('domain'):
            category_key = 'domain_knowledge'
        else:
            category_key = 'technical_skills'  # Default

        return source_config.get(category_key, 0.5)

    def _get_confidence_level(self, confidence: float) -> str:
        """
        Categorize confidence score into levels

        Args:
            confidence: Confidence score (0-1)

        Returns:
            Confidence level string
        """
        if confidence >= self.thresholds['high']:
            return 'high'
        elif confidence >= self.thresholds['medium']:
            return 'medium'
        elif confidence >= self.thresholds['low']:
            return 'low'
        else:
            return 'very_low'

    def score_skill_profile(self, extracted_skills: List) -> List[ScoredSkill]:
        """
        Score all skills in a profile

        Args:
            extracted_skills: List of ExtractedSkill objects

        Returns:
            List of ScoredSkill objects
        """
        # Group skills by name
        skill_groups = {}
        for skill in extracted_skills:
            skill_name = skill.skill_name
            if skill_name not in skill_groups:
                skill_groups[skill_name] = {
                    'category': skill.category,
                    'detections': []
                }

            skill_groups[skill_name]['detections'].append({
                'source': skill.source,
                'detection_method': skill.detection_method,
                'confidence': skill.confidence,
                'evidence': skill.evidence
            })

        # Score each skill
        scored_skills = []
        for skill_name, data in skill_groups.items():
            scored = self.score_skill(
                skill_name=skill_name,
                category=data['category'],
                detections=data['detections']
            )
            scored_skills.append(scored)

        # Sort by confidence (highest first)
        scored_skills.sort(key=lambda x: x.final_confidence, reverse=True)

        return scored_skills

    def filter_by_confidence(self, scored_skills: List[ScoredSkill], min_confidence: float = 0.3) -> List[ScoredSkill]:
        """
        Filter skills by minimum confidence threshold

        Args:
            scored_skills: List of ScoredSkill objects
            min_confidence: Minimum confidence threshold

        Returns:
            Filtered list of skills
        """
        return [skill for skill in scored_skills if skill.final_confidence >= min_confidence]

    def get_top_skills(self, scored_skills: List[ScoredSkill], top_n: int = 20) -> List[ScoredSkill]:
        """
        Get top N skills by confidence

        Args:
            scored_skills: List of ScoredSkill objects
            top_n: Number of top skills to return

        Returns:
            Top N skills
        """
        return scored_skills[:top_n]

    def export_to_dict(self, scored_skill: ScoredSkill) -> Dict:
        """Export ScoredSkill to dictionary"""
        return asdict(scored_skill)


# Example usage
if __name__ == "__main__":
    scorer = ConfidenceScorer()

    # Example detections
    sample_detections = [
        {
            'source': 'github',
            'detection_method': 'explicit',
            'confidence': 1.0,
            'evidence': ['Found in repository languages']
        },
        {
            'source': 'cv',
            'detection_method': 'contextual',
            'confidence': 0.8,
            'evidence': ['Experience with Python mentioned']
        }
    ]

    # scored = scorer.score_skill('Python', 'technical_programming_languages', sample_detections)
    # print(f"Skill: {scored.skill_name}")
    # print(f"Final Confidence: {scored.final_confidence}")
    # print(f"Confidence Level: {scored.confidence_breakdown['level']}")

    print("Confidence Scorer module loaded successfully")
