# core/text_processing.py
from PyPDF2 import PdfReader
import docx2txt

def extract_text_from_file(file):
    """Extract raw text from uploaded PDF, TXT, or DOCX."""
    if file.name.endswith(".pdf"):
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    elif file.name.endswith(".docx"):
        return docx2txt.process(file)
    elif file.name.endswith(".txt"):
        return file.read().decode("utf-8", errors="ignore")
    else:
        raise ValueError(f"Unsupported file type: {file.name}")

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50):
    """Split long text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks
