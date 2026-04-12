import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
KEY = os.getenv("GEMINI_API_KEY")

def test_gemini():
    print(f"Testing Gemini key: {KEY[:10]}...")
    try:
        genai.configure(api_key=KEY)
        model = 'models/text-embedding-004'
        result = genai.embed_content(
            model=model,
            content="test sentence",
            task_type="retrieval_document"
        )
        print("Success!")
        print(f"Embedding length: {len(result['embedding'])}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_gemini()
