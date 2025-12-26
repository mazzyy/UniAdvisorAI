import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("No API key found")
else:
    print(f"API Key found: {api_key[:5]}...")
    genai.configure(api_key=api_key)
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Hello")
        print("GenAI Response:", response.text)
    except Exception as e:
        print("Error:", e)
