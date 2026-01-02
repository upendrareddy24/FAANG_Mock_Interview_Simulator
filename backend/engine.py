import os
import requests
import json
import random
import google.generativeai as genai
from typing import Dict, Any, List
from .models import CandidateSession

class InterviewEngine:
    def __init__(self):
        print("Initializing Interview Engine...")
        self.mode = "CHECKING"
        
        # 1. Try External API (Gemini)
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                # Simple health check
                self.model.generate_content("Hello")
                self.mode = "CLOUD_AI"
                print(">> Mode: CLOUD AI (Gemini)")
            except Exception as e:
                print(f"!! Cloud AI Failed: {e}")
                self.mode = "FALLBACK_CHECK"
        else:
            self.mode = "FALLBACK_CHECK"

        # 2. Try Local LLM (Ollama)
        if self.mode == "FALLBACK_CHECK":
            try:
                # Check if Ollama is running on default port
                resp = requests.get("http://localhost:11434/", timeout=2)
                if resp.status_code == 200:
                    self.mode = "LOCAL_LLM"
                    print(">> Mode: LOCAL LLM (Ollama)")
                else:
                    self.mode = "STATIC"
            except:
                self.mode = "STATIC"
                
        if self.mode == "STATIC":
            print(">> Mode: STATIC (Offline / In-Built)")
            self.load_static_data()

    def load_static_data(self):
        """Loads the pre-generated 'Best in Industry' offline content."""
        base_path = os.path.dirname(__file__)
        data_dir = os.path.join(base_path, "data")
        
        try:
            with open(os.path.join(data_dir, "coding_problems.json"), "r") as f:
                self.coding_problems = json.load(f)
            with open(os.path.join(data_dir, "system_design.json"), "r") as f:
                self.design_problems = json.load(f)
            with open(os.path.join(data_dir, "behavioral.json"), "r") as f:
                self.behavioral_problems = json.load(f)
        except Exception as e:
            print(f"!! Failed to load static data: {e}. Ensure 'backend/data/' JSON files exist.")
            self.coding_problems = []
            self.design_problems = []
            self.behavioral_problems = []

    def get_interviewer_response(self, session: CandidateSession, user_input: str) -> str:
        """Dispatcher for generating responses based on active mode."""
        # Check for mode reset if Cloud AI fails mid-stream (quota exhaustion)
        try:
            if self.mode == "CLOUD_AI":
                return self._generate_cloud_response(session, user_input)
            elif self.mode == "LOCAL_LLM":
                return self._generate_local_response(session, user_input)
            else:
                return self._generate_static_response(session, user_input)
        except Exception as e:
            print(f"Error in {self.mode}: {e}. Falling back to STATIC.")
            self.mode = "STATIC"
            if not hasattr(self, 'coding_problems'):
                self.load_static_data()
            return self._generate_static_response(session, user_input)

    def _generate_cloud_response(self, session: CandidateSession, user_input: str) -> str:
        chat = self.model.start_chat(history=[])
        # Construct context
        context = f"You are a strict {session.target_company} {session.target_role} interviewer. " \
                  f"Round: {session.round_type}. Candidate Level: {session.target_level}. " \
                  f"User says: {user_input}"
        try:
            response = chat.send_message(context)
            return response.text
        except Exception as e:
            raise e

    def _generate_local_response(self, session: CandidateSession, user_input: str) -> str:
        # Using Ollama API standard endpoint
        prompt = f"System: Strict {session.target_company} interviewer. Context: {session.round_type}. Candidate: {user_input}. Reply:"
        
        payload = {
            "model": "llama3", # Default to llama3, user can change
            "prompt": prompt,
            "stream": False
        }
        resp = requests.post("http://localhost:11434/api/generate", json=payload)
        return resp.json().get("response", "Internal Error in Local LLM")

    def _generate_static_response(self, session: CandidateSession, user_input: str) -> str:
        """
        The 'Super Powerful' Static Engine.
        Uses keywords, state tracking, and pre-generated deep content.
        """
        history_len = len(session.current_state.history)
        
        # --- CODING ROUND LOGIC ---
        if session.round_type == "coding":
            # 1. Start: Give problem
            if "START_ROUND" in user_input or history_len <= 1:
                if not self.coding_problems: return "Error: No problems loaded."
                problem = random.choice(self.coding_problems)
                session.current_state.history.append({"role": "system", "content": f"PROBLEM_ID:{problem['id']}"})
                return f"## {problem['title']}\n\n{problem['description']}\n\n**Example**: {problem['example']}\n\n**Start Coding** in the editor. Explain your thought process first."
            
            # 2. Hints
            if "hint" in user_input.lower() or "stuck" in user_input.lower():
                # Find current problem ID from history (simple hack)
                for msg in reversed(session.current_state.history):
                    if msg.get("role") == "system" and "PROBLEM_ID" in msg["content"]:
                        pid = msg["content"].split(":")[1]
                        prob = next((p for p in self.coding_problems if p["id"] == pid), None)
                        if prob: return f"**Hint**: {prob['hint']}"
                return "Consider the time complexity. Can you optimize it?"

            # 3. Code Execution Feedback (from main.py context)
            if "I ran this code" in user_input:
                if "Error" in user_input:
                    return "It seems there's a syntax or runtime error. Check your logic carefully."
                return "The code runs. Now, what is the Time Complexity of your solution? Is it optimal?"

            return "Go on. I'm listening."

        # --- SYSTEM DESIGN LOGIC ---
        elif session.round_type == "design":
            # Start
            if "START_ROUND" in user_input or history_len <= 1:
                 if not self.design_problems: return "Error: No design problems loaded."
                 problem = random.choice(self.design_problems)
                 session.current_state.history.append({"role": "system", "content": f"PROBLEM_ID:{problem['id']}"})
                 return f"## Design Task: {problem['title']}\n\n{problem['description']}\n\nRequirements:\n" + "\n".join(f"- {r}" for r in problem['requirements']) + "\n\nWhere would you like to start?"

            # Simple State Machine based on keywords
            if "?" in user_input:
                return "That's a good question to clarify. Assume massive scale (100M+ users). Focus on availability."
            
            if "database" in user_input.lower() or "store" in user_input.lower():
                return "Good choice. relational or NoSQL? How do you handle schemas?"
            
            if "load balancer" in user_input.lower():
                return "Where exactly do you place the Load Balancer? Layer 4 or Layer 7?"

            return "Makes sense. Draw the high-level architecture on the whiteboard."

        # --- BEHAVIORAL LOGIC ---
        elif session.round_type == "behavioral":
            if "START_ROUND" in user_input or history_len <= 1:
                if not self.behavioral_problems: return "Error: No behavioral questions loaded."
                q = self.behavioral_problems[0]
                return f"Let's start. **{q['question']}**\n\n(Use the STAR method: Situation, Task, Action, Result)"
            
            # Just cycle through prompts or ask specific STAR follow-ups
            if len(user_input) < 50:
                return "Can you elaborate? That seems a bit brief for a senior role."
            
            return "Interesting. What was the specific outcome of your ACTIONS? ( The 'R' in STAR)"

        return "I am listening."

    def evaluate_round(self, session: CandidateSession) -> Dict[str, Any]:
        return {
            "scorecard": {
                "Technical Correctness": 3,
                "Communication": 4,
                "Problem Solving": 3,
                "Code Quality": 4,
                "System Design Scale": 3
            },
            "strong_signals": [
                "Good understanding of the problem statement.",
                "Clear communication."
            ],
            "weak_signals": [
                "Could optimize time complexity further.",
                "Detail in system components was high-level."
            ],
            "hiring_recommendation": "Lean Hire",
            "detailed_feedback": "This is a STATIC evaluation (Offline Mode). In a real interview, you should focus on driving the conversation. Since this is an offline simulation, please review your code against standard solutions.",
            "ideal_solution_summary": "Ideally, utilize a HashMap for O(1) lookups or a distributed cache like Redis for the system design component.",
            "improvement_plan": "Practice 5 more Medium LeetCode problems this week. Review 'Designing Data-Intensive Applications' Chapter 5 (Replication).",
            "mode": self.mode
        }
