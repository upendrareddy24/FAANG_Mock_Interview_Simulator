import os
import json
from typing import Dict, Any, List
import google.generativeai as genai
from .models import CandidateSession, InterviewState
from .personas import COMPANY_PERSONAS
from dotenv import load_dotenv

load_dotenv()

class InterviewEngine:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model_name = self._get_available_model()
        print(f"Selected Gemini Model: {self.model_name}")
        self.model = genai.GenerativeModel(self.model_name)

    def _get_available_model(self) -> str:
        """
        Dynamically selects the best available Gemin model from a prioritized list.
        """
        prioritized_models = [
            "models/gemini-2.0-flash",
            "models/gemini-1.5-flash",
            "models/gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-pro"
        ]
        
        try:
            available_models = [m.name for m in genai.list_models()]
            for model in prioritized_models:
                if model in available_models:
                    return model
            
            # Fallback if strict match fails (try partial match or default)
            return prioritized_models[0]
        except Exception as e:
            print(f"Warning: Could not list models ({e}). Defaulting to {prioritized_models[0]}")
            return prioritized_models[0]







    def _generate_system_prompt(self, session: CandidateSession) -> str:
        persona = COMPANY_PERSONAS.get(session.target_company)
        level_guidance = {
            "L3": "Focus on strong coding fundamentals, clear communication, and correct output. Expect them to need a bit more guidance than senior levels.",
            "L4": "Expect independent contributors who can handle ambiguity. Focus on tradeoffs and how they handle edge cases without being prompted.",
            "L5": "Expect technical leaders. Focus on system ownership, deep architectural tradeoffs, and the impact of their decisions on the broader system. Push them hard on scalability and long-term maintenance."
        }
        
        prompt = f"""
You are a Principal Engineer and Hiring Manager at {session.target_company}. 
Your personality: {persona.personality}
Focus areas: {', '.join(persona.focus_areas)}

Style Guidelines:
{chr(10).join(['- ' + s for s in persona.style_guidelines])}

Level expectations for {session.target_level}:
{level_guidance.get(session.target_level, "")}

Role: {session.target_role}
Candidate Resume Context: {session.resume_text if session.resume_text else "Not provided"}
Job Description Context: {session.job_description if session.job_description else "Not provided"}

ABSORB THESE CORE BEHAVIOR RULES:
1. DO NOT act like a tutor or teacher.
2. DO NOT give direct answers or solutions.
3. Be realistic and professional. Use the company's specific jargon or style if applicable.
4. If the candidate is vague, push back.
5. If the candidate over-engineers, interrupt and ask them to focus on the core problem.
6. Use "progressive guidance": Start silent, then use subtle nudges, then leading questions. Only give a partial hint if they are completely stuck.
7. Change constraints or add complexity mid-interview if they are moving too fast (especially for L4/L5).

Current Interview State: {session.current_state.state}
"""
        return prompt

    def get_interviewer_response(self, session: CandidateSession, user_input: str) -> str:
        system_prompt = self._generate_system_prompt(session)
        
        # Initialize model with system prompt
        model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=system_prompt
        )





        
        # Prepare history for Gemini
        history = []
        for msg in session.current_state.history[:-1]: # All except the current user input which we'll send
             role = "user" if msg["role"] == "candidate" else "model"
             history.append({"role": role, "parts": [msg["content"]]})
        
        try:
            chat = model.start_chat(history=history)
            response = chat.send_message(user_input)
            return response.text
        except Exception as e:
            return f"Interviewer connection error: {str(e)}"

        evaluation_prompt = f"""
As a Principal Engineer at {session.target_company}, evaluate the following interview transcript for an {session.target_level} {session.target_role} position.

Transcript:
{json.dumps(session.current_state.history, indent=2)}

Provide a detailed evaluation in JSON format with the following fields:
- "scorecard": {{ 
    "Technical Correctness": 1-5, 
    "Communication": 1-5, 
    "Judgment/Tradeoffs": 1-5, 
    "Problem Understanding": 1-5,
    "Role-Specific depth": 1-5 (e.g., ML Rigor if AI role, System Scalability if SDE)
  }}
- "strong_signals": list of things they did well.
- "weak_signals": list of things they struggled with.
- "interviewer_expectation_met": boolean.
- "detailed_feedback": summary for the candidate.
- "hiring_recommendation": "Strong Hire", "Hire", "Lean Hire", "No Hire".
- "ideal_solution_summary": a brief explanation of how a top candidate would have handled this specific scenario, including common AI interview mistakes to avoid if applicable.
- "improvement_plan": "A 14-day roadmap focusing on the missing depth areas identified."
"""
        try:
            response = self.model.generate_content(
                evaluation_prompt,
                generation_config={"response_mime_type": "application/json"}
            )

            return json.loads(response.text)
        except Exception as e:
            return {"error": f"Evaluation failed: {str(e)}"}

