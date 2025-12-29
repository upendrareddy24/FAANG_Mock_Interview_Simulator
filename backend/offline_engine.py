from typing import Dict, Any, List
from .models import CandidateSession
import random

class OfflineEngine:
    def __init__(self):
        print("Initializing Offline Engine (Static Mode)")
        self.question_bank = {
            "default": [
                "Could you walk me through a challenging project you worked on recently?",
                "What were the key technical trade-offs you had to make?",
                "How did you handle testing and deployment for that system?",
                "Reflecting on it now, what would you have done differently?"
            ],
            "AI / ML Engineer": [
                "Let's discuss a machine learning system you designed. How did you select your model architecture?",
                "How did you handle data preprocessing and feature engineering?",
                "What metrics did you use to evaluate offline vs online performance?",
                "How did you monitor this model for concept drift in production?"
            ],
            "Software Engineer": [
                "Describe a complex system architecture you designed.",
                "How did you ensure scalability and fault tolerance?",
                "Tell me about a time you debugged a critical production issue.",
                "How do you approach code quality and code reviews?"
            ]
        }

    def get_interviewer_response(self, session: CandidateSession, user_input: str) -> str:
        # Simple state machine based on history length
        history_len = len(session.current_state.history)
        
        # 0: Greeting (handled by main.py usually, but if called here)
        # 2: Candidate answered greeting -> Ask Q1
        # 4: Candidate answered Q1 -> Ask Q2
        # ...
        
        # Role-specific or default questions
        questions = self.question_bank.get(session.target_role, self.question_bank["default"])
        
        # Calculate which question index we are at
        # History has [Interviewer, Candidate, Interviewer, Candidate...]
        # Index = len // 2
        q_index = history_len // 2
        
        if q_index < len(questions):
            response = questions[q_index]
            if q_index > 0:
                transitions = [
                    "That makes sense. Moving on...",
                    "I see. Let's pivot slightly.",
                    "Understood. Let's go deeper into that.",
                    "Okay, good point."
                ]
                transition = random.choice(transitions)
                response = f"{transition} {response}"
            return response
        else:
            return "We have covered the main topics. Let's wrap up. Do you have any final questions for me?"

    def evaluate_round(self, session: CandidateSession) -> Dict[str, Any]:
        return {
            "scorecard": {
                "Technical Correctness": 3,
                "Communication": 4,
                "Judgment/Tradeoffs": 3,
                "Problem Understanding": 4,
                "Role-Specific depth": 3
            },
            "strong_signals": [
                "Good structured communication.",
                "Clear understanding of basic concepts."
            ],
            "weak_signals": [
                "Could have gone deeper into edge cases.",
                "System design details were high-level."
            ],
            "interviewer_expectation_met": True,
            "detailed_feedback": "This is an automated offline evaluation. You demonstrated good communication and general competence. To get specific technical feedback, please ensure the Live AI mode is valid.",
            "hiring_recommendation": "Lean Hire",
            "ideal_solution_summary": "In a real interview, top candidates would deep dive into scalability bottlenecks and specific technology choices relevant to the problem.",
            "improvement_plan": "Focus on system design patterns, specific algorithmic optimizations, and behavioral stories using the STAR method."
        }
