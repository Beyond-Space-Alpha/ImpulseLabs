import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3:8b"

def ask_ollama(prompt: str) -> str:
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()

        data = response.json()
        return data.get("response", "No response from model.")

    except requests.exceptions.ConnectionError:
        return "Error: Ollama is not running. Start it using 'ollama serve'."

    except Exception as e:
        return f"Error: {str(e)}"
