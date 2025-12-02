from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import uuid
from nlp_utils import extract_text, summarize_cv

router = APIRouter()

SESSIONS = {}  # simple in-memory session store


@router.post("/upload-cv")
async def upload_cv(
    file: UploadFile = File(...),
    job_title: str = Form(...)
):
    # Read file contents
    file_bytes = await file.read()

    # Try extracting text
    try:
        text = extract_text(file_bytes, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Summarize CV
    summary = summarize_cv(text)

    # Manage session
    session_id = uuid.uuid4().hex
    SESSIONS[session_id] = {
        "cv_text": text,
        "summary": summary,
        "job_title": job_title,
        "history": [],
    }

    # Return session data
    return {
        "session_id": session_id,
        "summary": summary
    }
