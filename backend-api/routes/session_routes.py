from fastapi import APIRouter
from fastapi.responses import JSONResponse
from routes.cv_routes import SESSIONS

router = APIRouter()

@router.get("/session/{session_id}")
async def get_session(session_id: str):
    if session_id not in SESSIONS:
        return JSONResponse({"error":"invalid session_id"}, status_code=400)
    return SESSIONS[session_id]
