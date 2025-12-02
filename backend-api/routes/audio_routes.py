from fastapi import APIRouter, UploadFile, Form,File
from fastapi.responses import JSONResponse, FileResponse
import uuid, os, json
import openai
from config import OPENAI_API_KEY, OPENAI_MODEL, TRANSCRIBE_MODEL
from tts_utils import tts_save_bytes, convert_bytes_to_wav
from routes.cv_routes import SESSIONS

router = APIRouter()

@router.post("/audio")
async def receive_audio(session_id: str = Form(...), audio_file: UploadFile = File(...)):
    if session_id not in SESSIONS:
        return JSONResponse({"error":"invalid session_id"}, status_code=400)

    raw = await audio_file.read()
    ext = audio_file.filename.split(".")[-1].lower()
    wav_bytes = convert_bytes_to_wav(raw, input_format=ext) if ext in ("webm","ogg","m4a","mp4") else raw

    transcript = ""
    if OPENAI_API_KEY:
        tmp_in = f"/tmp/audio_{uuid.uuid4().hex}.wav"
        with open(tmp_in, "wb") as f:
            f.write(wav_bytes)
        with open(tmp_in, "rb") as audio_f:
            resp = openai.Audio.transcribe(TRANSCRIBE_MODEL, audio_f)
        transcript = resp.get("text","").strip()
        try: os.remove(tmp_in)
        except: pass

    sess = SESSIONS[session_id]
    sess["history"].append({"candidate_audio_filename": audio_file.filename, "transcript": transcript})

    # LLM prompt
    system_prompt = "You are an objective interviewing assistant. Use the candidate summary to drive tailored interview questions.\n"
    candidate_summary = sess["summary"]
    last_answer = transcript or "[candidate did not speak or transcription failed]"

    user_prompt = (
        f"Candidate summary:\n{candidate_summary}\n\n"
        f"Job title: {sess['job_title']}\n\n"
        f"Last candidate answer:\n{last_answer}\n\n"
        "1) Provide a short 1-2 sentence evaluation of that answer.\n"
        "2) Provide one follow-up interview question.\n"
        "Return JSON with keys: evaluation, question, score_hint (1-5).\n"
    )

    llm_resp_text = ""
    try:
        resp = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[{"role":"system","content":system_prompt},{"role":"user","content":user_prompt}],
            max_tokens=300,
            temperature=0.2,
        )
        llm_resp_text = resp["choices"][0]["message"]["content"].strip()
    except:
        llm_resp_text = json.dumps({
            "evaluation": "LLM call failed",
            "question": "Can you tell me more about your most recent role?",
            "score_hint": 3
        })

    try:
        payload = json.loads(llm_resp_text)
        evaluation = payload.get("evaluation","")
        question = payload.get("question","Tell me about a time you solved a difficult problem.")
        score_hint = payload.get("score_hint", None)
    except:
        evaluation = llm_resp_text.split("\n")[0]
        question = llm_resp_text.split("\n")[-1] if "\n" in llm_resp_text else llm_resp_text
        score_hint = None

    sess["history"][-1].update({"evaluation": evaluation, "follow_up_question": question, "score_hint": score_hint})

    audio_bytes = tts_save_bytes(question)
    out_name = f"tts_{uuid.uuid4().hex}.mp3"
    out_path = f"/tmp/{out_name}"
    with open(out_path,"wb") as f: f.write(audio_bytes)

    return {"transcript": transcript, "evaluation": evaluation, "question": question, "audio_url": f"/tts/{out_name}"}

@router.get("/tts/{fname}")
async def get_tts(fname: str):
    path = f"/tmp/{fname}"
    if not os.path.exists(path):
        return JSONResponse({"error":"file not found"}, status_code=404)
    return FileResponse(path, media_type="audio/mpeg")
