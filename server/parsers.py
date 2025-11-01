import os
import PyPDF2
import docx
import tempfile

def extract_text(file_path):
    """Extract text from various file formats"""
    file_ext = os.path.splitext(file_path)[1].lower()
    
    try:
        if file_ext == '.pdf':
            return extract_from_pdf(file_path)
        elif file_ext in ['.docx', '.doc']:
            return extract_from_docx(file_path)
        elif file_ext == '.txt':
            return extract_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
    except Exception as e:
        raise Exception(f"Failed to extract text from {file_path}: {str(e)}")

def extract_from_pdf(file_path):
    """Extract text from PDF files"""
    text = ""
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text.strip()

def extract_from_docx(file_path):
    """Extract text from DOCX files"""
    doc = docx.Document(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text.strip()

def extract_from_txt(file_path):
    """Extract text from TXT files"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read().strip()