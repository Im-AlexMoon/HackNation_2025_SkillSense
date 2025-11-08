"""
PDF Extractor Module
Extracts text content from CV PDFs with section detection
"""
import pymupdf as fitz  # PyMuPDF
import re
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class CVSection:
    """Represents a section in a CV"""
    title: str
    content: str
    page_number: int


class PDFExtractor:
    """Extracts and structures text from CV PDFs"""

    # Common CV section headers
    SECTION_PATTERNS = [
        r'\b(education|academic background|qualifications)\b',
        r'\b(experience|work experience|employment|professional experience)\b',
        r'\b(skills|technical skills|competencies|expertise)\b',
        r'\b(projects|personal projects|portfolio)\b',
        r'\b(certifications|certificates|licenses)\b',
        r'\b(publications|papers|research)\b',
        r'\b(awards|honors|achievements)\b',
        r'\b(languages|language proficiency)\b',
        r'\b(summary|profile|objective|about me)\b',
        r'\b(volunteer|volunteering|community service)\b',
    ]

    def __init__(self):
        self.sections: List[CVSection] = []

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract all text from a PDF file

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Extracted text as a single string
        """
        try:
            doc = fitz.open(pdf_path)
            text = ""

            for page_num, page in enumerate(doc, start=1):
                text += f"\n--- Page {page_num} ---\n"
                text += page.get_text()

            doc.close()
            return text.strip()

        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")

    def detect_sections(self, text: str) -> List[CVSection]:
        """
        Detect and extract CV sections based on common headers

        Args:
            text: Full CV text

        Returns:
            List of detected sections
        """
        sections = []
        lines = text.split('\n')
        current_section = None
        current_content = []
        current_page = 1

        for line in lines:
            # Check for page markers
            page_match = re.match(r'--- Page (\d+) ---', line)
            if page_match:
                current_page = int(page_match.group(1))
                continue

            # Check if line matches a section header
            is_section_header = False
            for pattern in self.SECTION_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    # Save previous section
                    if current_section:
                        sections.append(CVSection(
                            title=current_section,
                            content='\n'.join(current_content).strip(),
                            page_number=current_page
                        ))

                    # Start new section
                    current_section = line.strip()
                    current_content = []
                    is_section_header = True
                    break

            # Add line to current section content
            if not is_section_header and current_section:
                current_content.append(line)

        # Add final section
        if current_section:
            sections.append(CVSection(
                title=current_section,
                content='\n'.join(current_content).strip(),
                page_number=current_page
            ))

        return sections

    def extract_structured_cv(self, pdf_path: str) -> Dict[str, any]:
        """
        Extract CV with section detection and metadata

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Dictionary with structured CV data
        """
        full_text = self.extract_text_from_pdf(pdf_path)
        sections = self.detect_sections(full_text)

        # Organize sections by category
        structured_data = {
            'raw_text': full_text,
            'sections': {},
            'metadata': {
                'source': pdf_path,
                'total_sections': len(sections)
            }
        }

        for section in sections:
            # Categorize section
            section_type = self._categorize_section(section.title)
            structured_data['sections'][section_type] = {
                'title': section.title,
                'content': section.content,
                'page': section.page_number
            }

        return structured_data

    def _categorize_section(self, title: str) -> str:
        """Categorize section title into standard types"""
        title_lower = title.lower()

        if re.search(r'\b(education|academic|qualification)', title_lower):
            return 'education'
        elif re.search(r'\b(experience|work|employment|professional)', title_lower):
            return 'experience'
        elif re.search(r'\b(skills|technical|competenc|expertise)', title_lower):
            return 'skills'
        elif re.search(r'\b(project)', title_lower):
            return 'projects'
        elif re.search(r'\b(certification|certificate|license)', title_lower):
            return 'certifications'
        elif re.search(r'\b(publication|paper|research)', title_lower):
            return 'publications'
        elif re.search(r'\b(award|honor|achievement)', title_lower):
            return 'awards'
        elif re.search(r'\b(language)', title_lower):
            return 'languages'
        elif re.search(r'\b(summary|profile|objective|about)', title_lower):
            return 'summary'
        elif re.search(r'\b(volunteer)', title_lower):
            return 'volunteer'
        else:
            return 'other'

    def extract_contact_info(self, text: str) -> Dict[str, Optional[str]]:
        """
        Extract contact information from CV text

        Args:
            text: CV text

        Returns:
            Dictionary with email, phone, and LinkedIn if found
        """
        contact_info = {
            'email': None,
            'phone': None,
            'linkedin': None,
            'github': None
        }

        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact_info['email'] = email_match.group(0)

        # Phone pattern (various formats)
        phone_pattern = r'\b(?:\+?1[-.]?)?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}\b'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            contact_info['phone'] = phone_match.group(0)

        # LinkedIn pattern
        linkedin_pattern = r'(?:linkedin\.com/in/|linkedin\.com/pub/)([A-Za-z0-9-]+)'
        linkedin_match = re.search(linkedin_pattern, text, re.IGNORECASE)
        if linkedin_match:
            contact_info['linkedin'] = linkedin_match.group(0)

        # GitHub pattern
        github_pattern = r'github\.com/([A-Za-z0-9-]+)'
        github_match = re.search(github_pattern, text, re.IGNORECASE)
        if github_match:
            contact_info['github'] = github_match.group(1)

        return contact_info


# Example usage
if __name__ == "__main__":
    extractor = PDFExtractor()

    # Example: Extract from a CV PDF
    # cv_data = extractor.extract_structured_cv("path/to/cv.pdf")
    # print(f"Found {cv_data['metadata']['total_sections']} sections")
    # for section_type, section_data in cv_data['sections'].items():
    #     print(f"\n{section_type.upper()}: {section_data['title']}")

    print("PDF Extractor module loaded successfully")
