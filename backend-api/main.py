from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routes.home import router as home_router
from routes.cv_routes import router as cv_router
from routes.audio_routes import router as audio_router
from routes.session_routes import router as session_router

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(home_router)
app.include_router(cv_router)
app.include_router(audio_router)
app.include_router(session_router)
