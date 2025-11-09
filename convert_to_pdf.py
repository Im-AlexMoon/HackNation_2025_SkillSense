#!/usr/bin/env python3
"""
Convert PROJECT_RETROSPECTIVE.md to a formatted PDF using ReportLab
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY, TA_CENTER
import markdown2
import os
import re

# Read the markdown file
markdown_file = "docs/PROJECT_RETROSPECTIVE.md"
with open(markdown_file, "r", encoding="utf-8") as f:
    md_content = f.read()

# Create PDF
output_file = "docs/PROJECT_RETROSPECTIVE.pdf"
doc = SimpleDocTemplate(output_file, pagesize=letter, topMargin=0.75*inch, bottomMargin=0.75*inch)

# Define styles
styles = getSampleStyleSheet()
story = []

# Custom styles
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=28,
    textColor=colors.HexColor('#1f2937'),
    spaceAfter=20,
    alignment=TA_CENTER,
    fontName='Helvetica-Bold'
)

heading_style = ParagraphStyle(
    'CustomHeading',
    parent=styles['Heading2'],
    fontSize=18,
    textColor=colors.HexColor('#1f2937'),
    spaceAfter=12,
    spaceBefore=12,
    fontName='Helvetica-Bold'
)

heading3_style = ParagraphStyle(
    'CustomHeading3',
    parent=styles['Heading3'],
    fontSize=14,
    textColor=colors.HexColor('#374151'),
    spaceAfter=10,
    spaceBefore=10,
    fontName='Helvetica-Bold'
)

body_style = ParagraphStyle(
    'CustomBody',
    parent=styles['BodyText'],
    fontSize=11,
    alignment=TA_JUSTIFY,
    spaceAfter=12,
    leading=16
)

# Parse and add content
lines = md_content.split('\n')
i = 0
while i < len(lines):
    line = lines[i]

    # Title (H1)
    if line.startswith('# ') and not line.startswith('## '):
        title = line.replace('# ', '').strip()
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 0.3*inch))
        i += 1

    # Heading 2
    elif line.startswith('## '):
        heading = line.replace('## ', '').strip()
        story.append(Paragraph(heading, heading_style))
        story.append(Spacer(1, 0.1*inch))
        i += 1

    # Heading 3
    elif line.startswith('### '):
        heading = line.replace('### ', '').strip()
        story.append(Paragraph(heading, heading3_style))
        story.append(Spacer(1, 0.08*inch))
        i += 1

    # Horizontal rule / Page break
    elif line.strip() == '---':
        story.append(Spacer(1, 0.2*inch))
        story.append(PageBreak())
        i += 1

    # Empty line
    elif line.strip() == '':
        story.append(Spacer(1, 0.1*inch))
        i += 1

    # Regular paragraph (including bold/italic)
    elif not line.startswith('|'):
        # Skip code blocks for now (they'll be regular text)
        if not line.startswith('```'):
            text = line.strip()
            if text:
                # Convert markdown bold/italic
                text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
                text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
                text = re.sub(r'__(.*?)__', r'<b>\1</b>', text)
                text = re.sub(r'_(.*?)_', r'<i>\1</i>', text)

                story.append(Paragraph(text, body_style))
            i += 1
        else:
            i += 1
    else:
        i += 1

# Build PDF
try:
    doc.build(story)
    print("PDF successfully created:", output_file)
    file_size = os.path.getsize(output_file) / 1024
    print("File size:", f"{file_size:.2f} KB")
    print("Location:", os.path.abspath(output_file))
except Exception as e:
    print("Error creating PDF:", e)
    import traceback
    traceback.print_exc()