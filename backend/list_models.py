import os
from dotenv import load_dotenv
load_dotenv()
from google import genai

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("NO API KEY")
    exit(1)

client = genai.Client(api_key=api_key)
try:
    models = client.models.list()
    for m in models:
        print(m.name, m.supported_actions)
except Exception as e:
    print("Error:", e)
