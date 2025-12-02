from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def index():
     with open("static/index.html", "r", encoding="utf-8") as f:
           return HTMLResponse(f.read())