import os
import uuid 
import io
from pydub import AudioSegment
import pyttx3

def tts_save_bytes(text:str) -> bytes:
    engine = pyttx3.init()
    tmp_filename = f"/tmp/tts_{uuid.uuid4().hex}.mp3"
    engine.save_to_file(text, tmp_filename)
    engine.runAndWait()
    with open(tmp_filename, "rb") as f:
        audio_bytes = f.read()
        try:
            os.remove(tmp_filename)
        except:
            pass
        return audio_bytes
    
def convert_bytes_to_wav(input_bytes: bytes, input_format: str="webm") -> bytes:
    audio = AudioSegment.from_file(io.BytesIO(input_bytes), format=input_format)
    out_io = io.BytesIO()
    audio.export(out_io, format="wav")
    return out_io.getvalue()