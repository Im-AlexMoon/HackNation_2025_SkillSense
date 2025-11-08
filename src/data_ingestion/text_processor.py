"""
Text Processor Module
Handles manual text input for personal statements, reference letters, and other text sources
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import re


@dataclass
class TextDocument:
    """Represents a text document"""
    content: str
    doc_type: str  # 'personal_statement', 'reference_letter', 'cover_letter', etc.
    metadata: Dict[str, any]


class TextProcessor:
    """Processes and structures text input from various sources"""

    DOCUMENT_TYPES = [
        'personal_statement',
        'reference_letter',
        'cover_letter',
        'blog_post',
        'article',
        'other'
    ]

    def __init__(self):
        self.documents: List[TextDocument] = []

    def process_text(self, content: str, doc_type: str, metadata: Optional[Dict] = None) -> TextDocument:
        """
        Process and structure text input

        Args:
            content: Text content
            doc_type: Type of document
            metadata: Optional metadata (author, date, etc.)

        Returns:
            TextDocument object
        """
        if doc_type not in self.DOCUMENT_TYPES:
            doc_type = 'other'

        if metadata is None:
            metadata = {}

        # Add processing timestamp
        metadata['processed_at'] = datetime.now().isoformat()

        # Basic text cleaning
        cleaned_content = self._clean_text(content)

        # Extract basic stats
        metadata['word_count'] = len(cleaned_content.split())
        metadata['char_count'] = len(cleaned_content)
        metadata['paragraph_count'] = len(self._split_paragraphs(cleaned_content))

        document = TextDocument(
            content=cleaned_content,
            doc_type=doc_type,
            metadata=metadata
        )

        self.documents.append(document)
        return document

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace
        text = text.strip()
        return text

    def _split_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs"""
        paragraphs = re.split(r'\n\s*\n', text)
        return [p.strip() for p in paragraphs if p.strip()]

    def analyze_writing_style(self, content: str) -> Dict[str, any]:
        """
        Analyze writing style for communication skill assessment

        Args:
            content: Text content

        Returns:
            Dictionary with writing style metrics
        """
        words = content.split()
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]

        # Calculate metrics
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        avg_sentence_length = len(words) / len(sentences) if sentences else 0

        # Vocabulary richness (unique words / total words)
        unique_words = set(word.lower() for word in words if word.isalnum())
        vocabulary_richness = len(unique_words) / len(words) if words else 0

        # Detect professional language patterns
        professional_indicators = [
            r'\b(demonstrate|implement|develop|achieve|deliver|manage|lead)\b',
            r'\b(experience|expertise|proficiency|knowledge|skill)\b',
            r'\b(collaborate|coordinate|facilitate|execute|optimize)\b'
        ]

        professional_score = 0
        for pattern in professional_indicators:
            matches = re.findall(pattern, content, re.IGNORECASE)
            professional_score += len(matches)

        # Normalize professional score (0-1 scale)
        professional_score = min(professional_score / len(words) * 100, 1.0) if words else 0

        return {
            'total_words': len(words),
            'total_sentences': len(sentences),
            'avg_word_length': round(avg_word_length, 2),
            'avg_sentence_length': round(avg_sentence_length, 2),
            'vocabulary_richness': round(vocabulary_richness, 2),
            'professional_language_score': round(professional_score, 2),
            'readability_assessment': self._assess_readability(avg_sentence_length, avg_word_length)
        }

    def _assess_readability(self, avg_sentence_length: float, avg_word_length: float) -> str:
        """
        Assess readability level

        Simple heuristic based on sentence and word length
        """
        if avg_sentence_length > 25 or avg_word_length > 6:
            return 'complex'
        elif avg_sentence_length > 15 or avg_word_length > 5:
            return 'moderate'
        else:
            return 'simple'

    def extract_key_phrases(self, content: str, top_n: int = 10) -> List[str]:
        """
        Extract key phrases from text (simple frequency-based approach)

        Args:
            content: Text content
            top_n: Number of top phrases to return

        Returns:
            List of key phrases
        """
        # Remove common stop words (simplified list)
        stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'the', 'this', 'but', 'they', 'have',
            'had', 'what', 'when', 'where', 'who', 'which', 'why', 'how'
        }

        # Extract words
        words = re.findall(r'\b[a-z]+\b', content.lower())

        # Filter stop words and short words
        meaningful_words = [
            word for word in words
            if word not in stop_words and len(word) > 3
        ]

        # Count frequency
        word_freq = {}
        for word in meaningful_words:
            word_freq[word] = word_freq.get(word, 0) + 1

        # Get top N
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:top_n]]

    def process_personal_statement(self, content: str) -> Dict[str, any]:
        """
        Process personal statement with specific analysis

        Args:
            content: Personal statement text

        Returns:
            Structured data with analysis
        """
        document = self.process_text(content, 'personal_statement')
        writing_analysis = self.analyze_writing_style(content)
        key_phrases = self.extract_key_phrases(content)

        return {
            'source': 'personal_statement',
            'content': content,
            'writing_analysis': writing_analysis,
            'key_phrases': key_phrases,
            'metadata': document.metadata,
            'soft_skills_indicators': self._extract_soft_skills_indicators(content)
        }

    def process_reference_letter(self, content: str, author: Optional[str] = None) -> Dict[str, any]:
        """
        Process reference letter with specific analysis

        Args:
            content: Reference letter text
            author: Optional author name

        Returns:
            Structured data with analysis
        """
        metadata = {'author': author} if author else {}
        document = self.process_text(content, 'reference_letter', metadata)
        writing_analysis = self.analyze_writing_style(content)

        # Extract positive endorsements
        endorsement_patterns = [
            r'\b(excellent|outstanding|exceptional|remarkable|impressive)\b',
            r'\b(highly recommend|strongly recommend|without hesitation)\b',
            r'\b(demonstrated|proven|shown|exhibited)\b'
        ]

        endorsements = []
        for pattern in endorsement_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            endorsements.extend(matches)

        return {
            'source': 'reference_letter',
            'content': content,
            'author': author,
            'writing_analysis': writing_analysis,
            'endorsements': endorsements,
            'metadata': document.metadata,
            'soft_skills_indicators': self._extract_soft_skills_indicators(content)
        }

    def _extract_soft_skills_indicators(self, content: str) -> Dict[str, List[str]]:
        """
        Extract indicators of soft skills from text

        Args:
            content: Text content

        Returns:
            Dictionary mapping soft skill categories to evidence
        """
        soft_skill_patterns = {
            'leadership': [
                r'\b(lead|led|leading|leadership|manage|managed|managing)\b',
                r'\b(mentor|mentored|mentoring|coach|coached|coaching)\b',
                r'\b(direct|directed|directing|supervise|supervised)\b'
            ],
            'communication': [
                r'\b(present|presented|presenting|presentation)\b',
                r'\b(communicate|communicated|communication)\b',
                r'\b(write|wrote|writing|written|documentation)\b',
                r'\b(explain|explained|articulate|articulated)\b'
            ],
            'teamwork': [
                r'\b(collaborate|collaborated|collaboration|team|teamwork)\b',
                r'\b(cooperate|cooperated|cooperation)\b',
                r'\b(work with|worked with|working with)\b'
            ],
            'problem_solving': [
                r'\b(solve|solved|solving|solution)\b',
                r'\b(analyze|analyzed|analysis|analytical)\b',
                r'\b(troubleshoot|debug|debugged|resolve|resolved)\b'
            ],
            'adaptability': [
                r'\b(adapt|adapted|adaptable|flexible|flexibility)\b',
                r'\b(learn|learned|learning|quick learner)\b',
                r'\b(change|changed|transition|transitioned)\b'
            ]
        }

        indicators = {}
        for skill, patterns in soft_skill_patterns.items():
            matches = []
            for pattern in patterns:
                found = re.findall(pattern, content, re.IGNORECASE)
                matches.extend(found)
            if matches:
                indicators[skill] = list(set(matches))  # Remove duplicates

        return indicators


# Example usage
if __name__ == "__main__":
    processor = TextProcessor()

    # Example personal statement
    sample_statement = """
    I am a passionate software engineer with 5 years of experience in developing
    scalable web applications. Throughout my career, I have demonstrated strong
    leadership skills by managing cross-functional teams and delivering complex
    projects on time. I excel at problem-solving and have a proven track record
    of implementing innovative solutions.
    """

    # result = processor.process_personal_statement(sample_statement)
    # print(f"Writing analysis: {result['writing_analysis']}")
    # print(f"Soft skills: {result['soft_skills_indicators']}")

    print("Text Processor module loaded successfully")
