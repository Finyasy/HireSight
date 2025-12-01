import io
import pdfplumber
import docx
import spacy
import openai   
from config import OPENAI_API_KEY, OPENAI_MODEL

nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(file_bytes: bytes) -> str:
    text_parts = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text_parts.append(page.extract_text())
    return "\n".join(text_parts)

    
def extract_text_from_docx(file_bytes: bytes) -> str:
    """
    Extract text from a DOCX file using python-docx.
    """
    file_stream = io.BytesIO(file_bytes)
    doc = docx.Document(file_stream)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)

