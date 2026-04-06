from llm.ollama_client import OllamaClient

SYSTEM_PROMPT = """
You are an aerospace engineering assistant.
Explain clearly and structured.
"""

class LLMConnection:

    def __init__(self):

        self.client = OllamaClient()

        self.messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]

    def ask(self, user_text):

        self.messages.append({
            "role": "user",
            "content": user_text
        })

        reply = self.client.chat(self.messages)

        self.messages.append({
            "role": "assistant",
            "content": reply
        })

        return reply