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

def extract_text(file_bytes: bytes, filename: str) -> str:
    """
    Decides whether to parse as PDF or DOCX based on file extension.
    """
    ext = filename.lower().split(".")[-1]

    if ext == "pdf":
        return extract_text_from_pdf(file_bytes)
    elif ext == "docx":
        return extract_text_from_docx(file_bytes)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
    

def summarize_cv(text: str, max_sentences: int = 4) -> str:
    doc = nlp(text)
    sents = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
    summary = " ".join(sents[:max_sentences])
    
    # fallback to LLM
    if len(summary.split()) < 20 and OPENAI_API_KEY:
        prompt = (
            f"Summarize this CV into 4 short bullet points:\n\n{text[:4000]}"
        )
        
        resp = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
        )
        summary = resp["choices"][0]["message"]["content"].strip()

    return summary
    
