import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
KEY = os.getenv("GEMINI_API_KEY")

def list_models():
    genai.configure(api_key=KEY)
    print("Listing available models for the given API key...")
    try:
        for m in genai.list_models():
            if 'embedContent' in m.supported_generation_methods:
                print(f"Model ID: {m.name}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_models()
