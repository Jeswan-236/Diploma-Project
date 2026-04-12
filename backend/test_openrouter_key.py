import os
import httpx
from dotenv import load_dotenv

load_dotenv()
KEY = os.getenv("OPENROUTER_API_KEY")

def test_key():
    url = "https://openrouter.ai/api/v1/embeddings"
    headers = {
        "Authorization": f"Bearer {KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://skillstalker.app",
        "X-Title": "SkillStalker RAG Pipeline"
    }
    payload = {
        "model": "openai/text-embedding-3-small",
        "input": ["test sentence"]
    }
    
    print(f"Testing key: {KEY[:10]}...")
    try:
        with httpx.Client(timeout=10) as client:
            res = client.post(url, headers=headers, json=payload)
            print(f"Status: {res.status_code}")
            print(f"Response: {res.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_key()
