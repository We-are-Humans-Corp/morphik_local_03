#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы ColPali с PDF документами
"""

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import os

def create_test_pdf():
    """Создает тестовый PDF с несколькими страницами"""
    filename = "test_document.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Страница 1
    story.append(Paragraph("Test Document for ColPali", styles['Title']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Page 1: Introduction", styles['Heading1']))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(
        "This is the first page of the test document. "
        "It contains information about artificial intelligence and machine learning. "
        "ColPali should process this page as an image.", 
        styles['Normal']
    ))
    story.append(PageBreak())
    
    # Страница 2
    story.append(Paragraph("Page 2: Technical Details", styles['Heading1']))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(
        "This is the second page with technical specifications. "
        "The system uses Modal for GPU processing and MinIO for storage. "
        "This page should be converted to an image for ColPali processing.",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(
        "Important: ColPali processes PDF pages as images, not text.",
        styles['Normal']
    ))
    story.append(PageBreak())
    
    # Страница 3
    story.append(Paragraph("Page 3: Results and Conclusions", styles['Heading1']))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(
        "Final page with conclusions and test results. "
        "The search should return references like [test_document.pdf, page 3]. "
        "This verifies that the page numbering works correctly.",
        styles['Normal']
    ))
    
    doc.build(story)
    print(f"Created test PDF: {filename}")
    return filename

if __name__ == "__main__":
    pdf_file = create_test_pdf()
    print(f"Test PDF created: {os.path.abspath(pdf_file)}")