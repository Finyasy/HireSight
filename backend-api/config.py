import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY","")
OPENAI_MODEL = os.getenv("OPENAI_MODEL","gpt-4o-mini")
TRANSCRIBE_MODEL = os.getenv("TRANSCRIBE_MODEL","whisper-1")
PORT = os.getenv("PORT",8000)