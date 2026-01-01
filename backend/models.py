from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class CompanyPersona(BaseModel):
    name: str
    personality: str
    focus_areas: List[str]
    style_guidelines: List[str]

class Scenario(BaseModel):
    title: str
    description: str
    constraints: List[str]
    target_level: str  # L3, L4, L5
    role: str

class InterviewState(BaseModel):
    current_round: int = 1
    total_rounds: int
    state: str = "INITIALIZATION" # INITIALIZATION, CLARIFICATION, TECHNICAL_PROBING, FOLLOW_UP, EVALUATION
    current_phase: str = "Intro" # Added missing field
    pressure_level: int = 0
    struggle_meter: int = 0
    history: List[Dict[str, str]] = []

class CandidateSession(BaseModel):
    session_id: str
    resume_text: Optional[str]
    job_description: Optional[str]
    years_of_experience: int
    target_company: str
    target_role: str
    target_level: str
    preferred_language: str
    round_type: str  # "coding" or "design"
    current_state: InterviewState
