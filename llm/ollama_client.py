import requests

MODEL = "llama3:8b"

class OllamaClient:

    def chat(self, messages):

        try:
            response = requests.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": MODEL,
                    "messages": messages,
                    "stream": False
                },
                timeout=120
            )

            data = response.json()
            return data["message"]["content"]

        except Exception as e:
            return f"Error: {e}"