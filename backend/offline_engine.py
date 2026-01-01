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
        # Check round type first
        if session.round_type == "coding":
            # Return specific Coding Problems if it's the first message or explicitly requested
            if "START_ROUND_CODING" in user_input or len(session.current_state.history) <= 2:
                return """**Problem**: Invert Binary Tree
**Description**: Given the root of a binary tree, invert the tree, and return its root.
**Example**: Input: root = [4,2,7,1,3,6,9], Output: [4,7,2,9,6,3,1]
**Constraints**: The number of nodes in the tree is in the range [0, 100]."""
            else:
                return "That looks correct. Can you optimize the space complexity?"

        elif session.round_type == "design":
            if "START_ROUND_DESIGN" in user_input or len(session.current_state.history) <= 2:
                 return """**Design Task**: Design a URL Shortener (like Bit.ly)
**Scale**: 100M daily active users.
**Instructions**: Focus on the data model and hash function."""
            else:
                return "Good. How would you handle hash collisions?"

        # Fallback to old logic if no specific round type (shouldn't happen)
        return "I am ready. Let's begin."

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
