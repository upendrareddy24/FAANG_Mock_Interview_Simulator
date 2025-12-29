import os
import json
from typing import Dict, Any, List
import google.generativeai as genai
from .models import CandidateSession, InterviewState
from .personas import COMPANY_PERSONAS
from dotenv import load_dotenv

load_dotenv()

from .offline_engine import OfflineEngine

class InterviewEngine:
    def __init__(self):
        self.offline_engine = OfflineEngine()
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        # Dynamic Model Discovery
        try:
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            print(f"Available models: {available_models}")
            
            # Substrings to look for in order of preference
            preferences = [
                "gemini-2.0-flash-exp",
                "gemini-2.0-flash",
                "gemini-1.5-flash",
                "gemini-1.5-pro",
                "gemini-pro",
                "gemini-1.0-pro"
            ]
            
            self.prioritized_models = []
            for pref in preferences:
                for model_name in available_models:
                    if pref in model_name and model_name not in self.prioritized_models:
                        self.prioritized_models.append(model_name)
            
            # Fallback if discovery fails or finds nothing suitable
            if not self.prioritized_models:
                 print("Warning: No preferred models found. Using hardcoded fallbacks.")
                 self.prioritized_models = ["gemini-1.5-flash", "gemini-pro"]
                 
        except Exception as e:
            print(f"Failed to list models: {e}. Using fallbacks.")
            self.prioritized_models = ["gemini-1.5-flash", "gemini-pro"]

        self.current_model_index = 0
        print(f"Using models: {self.prioritized_models}")

    def _get_model(self, model_name: str, system_prompt: str = None):
        return genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_prompt
        )

    def _generate_with_retry(self, func, *args, **kwargs):
        """
        Executes a Gemini API call with automatic fallback to the next model on 429 errors.
        """
        original_index = self.current_model_index
        attempts = 0
        max_attempts = len(self.prioritized_models)

        while attempts < max_attempts:
            current_model_name = self.prioritized_models[self.current_model_index]
            try:
                # Update the model instance in the arguments if it's passed, 
                # or rely on the caller to use the current model name.
                # Here we expect 'func' to be a lambda that creates the model/chat and runs it.
                return func(current_model_name)
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "Quota exceeded" in error_str or "Resource exhausted" in error_str:
                    print(f"Rate limit hit on {current_model_name}. Switching model...")
                    self.current_model_index = (self.current_model_index + 1) % len(self.prioritized_models)
                    attempts += 1
                else:
                    # Non-retriable error
                    raise e
        
        # Reset index if all failed (to try best one again next time)
        self.current_model_index = original_index
        raise Exception("All models exhausted due to rate limits.")

    def _generate_system_prompt(self, session: CandidateSession) -> str:
        persona = COMPANY_PERSONAS.get(session.target_company)
        
        prompt = f"""
You are an interviewer from {session.target_company}.
Your Persona: {persona.personality}
Focus Areas: {', '.join(persona.focus_areas)}
Style Guidelines: {', '.join(persona.style_guidelines)}

Candidate Profile:
- Role: {session.target_role}
- Level: {session.target_level}
- Experience: {session.years_of_experience} years
- Language: {session.preferred_language}

Current Interview State:
- Round Progress: {len(session.current_state.history) // 2} / {session.current_state.total_rounds} messages
- Phase: {session.current_state.current_phase}

Your Goal:
Conduct a realistic, challenging FAANG-level interview.
1. Start with a relevant technical question based on the role and company.
2. If the candidate answers poorly, probe deeper or give a small hint (not the answer).
3. If they answer well, add a constraint or scale the problem (e.g., "Now handle 1B users").
4. Be professional but strict. Do NOT be a tutor.
5. Keep responses concise (under 200 words) to mimic a real chat.
"""
        return prompt

    def get_interviewer_response(self, session: CandidateSession, user_input: str) -> str:
        system_prompt = self._generate_system_prompt(session)
        
        # Prepare history
        history = []
        for msg in session.current_state.history[:-1]:
             role = "user" if msg["role"] == "candidate" else "model"
             history.append({"role": role, "parts": [msg["content"]]})

        def run_chat(model_name):
            model = self._get_model(model_name, system_prompt)
            chat = model.start_chat(history=history)
            response = chat.send_message(user_input)
            return response.text

        try:
            return self._generate_with_retry(run_chat)
        except Exception as e:
            print(f"API Error in get_interviewer_response: {e}. Switching to Offline Mode.")
            return self.offline_engine.get_interviewer_response(session, user_input)

    def evaluate_round(self, session: CandidateSession) -> Dict[str, Any]:
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
        def run_eval(model_name):
            model = self._get_model(model_name)
            response = model.generate_content(
                evaluation_prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            return json.loads(response.text)

        try:
            return self._generate_with_retry(run_eval)
        except Exception as e:
            print(f"API Error in evaluate_round: {e}. Switching to Offline Mode.")
            return self.offline_engine.evaluate_round(session)
