import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

try:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    print("Direct initialization success")
except Exception as e:
    print(f"Direct initialization failed: {e}")

try:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"), vertexai=False)
    print("With vertexai=False success")
except Exception as e:
    print(f"With vertexai=False failed: {e}")
