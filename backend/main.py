from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import uuid

from .models import CandidateSession, InterviewState, InterviewState
from .engine import InterviewEngine
from .personas import COMPANY_PERSONAS

app = FastAPI(title="FAANG Interview Simulator API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session storage
sessions: Dict[str, CandidateSession] = {}
engine = InterviewEngine()

@app.post("/session/start")
async def start_session(
    target_company: str = Body(...),
    target_role: str = Body(...),
    target_level: str = Body(...),
    years_of_experience: int = Body(...),
    preferred_language: str = Body(...),
    resume_text: str = Body(None),
    job_description: str = Body(None)
):
    if target_company not in COMPANY_PERSONAS:
        raise HTTPException(status_code=400, detail="Invalid company")
    
    session_id = str(uuid.uuid4())
    initial_state = InterviewState(
        total_rounds=3 if target_level == "L3" else (4 if target_level == "L4" else 5)
    )
    
    session = CandidateSession(
        session_id=session_id,
        target_company=target_company,
        target_role=target_role,
        target_level=target_level,
        years_of_experience=years_of_experience,
        preferred_language=preferred_language,
        resume_text=resume_text,
        job_description=job_description,
        current_state=initial_state
    )
    
    # Generate initial greeting from interviewer
    greeting = engine.get_interviewer_response(session, "Start the interview. Introduce yourself and the round, then ask the first question or ask for clarifications.")
    
    session.current_state.history.append({"role": "interviewer", "content": greeting})
    sessions[session_id] = session
    
    return {"session_id": session_id, "interviewer_message": greeting}

@app.post("/session/{session_id}/respond")
async def respond(session_id: str, candidate_message: str = Body(...)):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    session.current_state.history.append({"role": "candidate", "content": candidate_message})
    
    interviewer_response = engine.get_interviewer_response(session, candidate_message)
    session.current_state.history.append({"role": "interviewer", "content": interviewer_response})
    
    return {"interviewer_message": interviewer_response}

@app.post("/session/{session_id}/evaluate")
async def evaluate(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    evaluation = engine.evaluate_round(session)
    
    return evaluation

# Mount frontend static files
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Serve index.html at root
@app.get("/")
async def read_index():
    return FileResponse('frontend/index.html')

# Mount the entire frontend directory for assets/css/js
app.mount("/", StaticFiles(directory="frontend"), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
