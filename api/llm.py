import os, requests

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "phi3:mini")

def chat(prompt: str, system: str = "You are a helpful finance analyst.") -> str:
    url = f"{OLLAMA_HOST}/api/chat"
    payload = {
        "model": DEFAULT_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
    }
    r = requests.post(url, json=payload, timeout=120)
    r.raise_for_status()
    data = r.json()
    return data.get("message", {}).get("content", "")