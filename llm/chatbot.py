import sys
import json
import requests
import threading
import markdown

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel
)
from PySide6.QtWebEngineWidgets import QWebEngineView


# ── CONFIG ─────────────────────────

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3:8b"

SYSTEM_PROMPT = """You are a propulsion engineering AI assistant.

Provide detailed, structured explanations.
Use Markdown formatting.
Use LaTeX for equations.
Explain step-by-step when possible.
Include reasoning and intermediate steps.
Only be concise if the user explicitly asks for brevity.
"""


# ── CHATBOT WIDGET ─────────────────────────

class ChatbotWidget(QWidget):

    reply_signal = Signal(str)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("ImpulseLabs AI")
        self.setGeometry(300, 200, 900, 700)

        self.history = []
        self.chat_html = ""

        self.init_ui()
        self.reply_signal.connect(self.finish_reply)

    # ── UI SETUP ─────────────────────────

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("ImpulseLabs")
        title.setAlignment(Qt.AlignCenter)

        title.setStyleSheet("""
            font-size: 12px;
            font-weight: 400;
            color: #aaa;
            margin: 2px;
        """)

        layout.addWidget(title)

        self.chat_view = QWebEngineView()
        layout.addWidget(self.chat_view)

        self.render_chat()

        bottom = QHBoxLayout()

        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Ask something...")
        bottom.addWidget(self.input_box)

        self.send_btn = QPushButton("Send")
        bottom.addWidget(self.send_btn)

        layout.addLayout(bottom)

        self.setLayout(layout)

        self.setStyleSheet("""
            QWidget {
                background-color: #000000;
                color: #ffffff;
            }
        """)

        self.send_btn.clicked.connect(self.send_message)
        self.input_box.returnPressed.connect(self.send_message)

        self.add_message("assistant", "ImpulseLabs AI online")

        self.resize(500, 700)

    # ── RENDER HTML ─────────────────────────

    def render_chat(self):

        html = f"""
        <html>
        <head>

        <script>
        window.MathJax = {{
            tex: {{
                inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
                displayMath: [['$$', '$$']]
            }}
        }};
        </script>

        <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>

        <style>
        body {{
            background:#111;
            color:white;
            font-family:Segoe UI;
            padding:20px;
        }}
        .user {{
            color:#4fc3f7;
            font-weight:bold;
        }}
        .assistant {{
            color:#ff8a65;
            font-weight:bold;
        }}
        .msg {{
            margin-bottom:20px;
            padding-bottom:10px;
            border-bottom:1px solid #333;
        }}
        code {{
            background:#222;
            padding:3px 6px;
            border-radius:5px;
        }}
        pre {{
            background:#222;
            padding:10px;
            border-radius:8px;
            overflow-x:auto;
        }}
        </style>

        </head>

        <body>
        {self.chat_html}
        </body>
        </html>
        """

        self.chat_view.setHtml(html)

    # ── FORMAT MESSAGE ─────────────────────────

    def format_msg(self, role, text):

        html = markdown.markdown(
            text,
            extensions=["fenced_code", "tables", "nl2br"]
        )

        return f"""
        <div class="msg">
            <div class="{role}">{role.capitalize()}:</div>
            <div>{html}</div>
        </div>
        """

    def add_message(self, role, text):

        self.chat_html += self.format_msg(role, text)
        self.render_chat()

    # ── SEND MESSAGE ─────────────────────────

    def send_message(self):

        user_text = self.input_box.text().strip()

        if not user_text:
            print("EMPTY INPUT")
            return

        self.input_box.clear()

        self.add_message("user", user_text)

        self.history.append({
            "role": "user",
            "content": user_text
        })

        self.send_btn.setEnabled(False)
        self.input_box.setEnabled(False)

        threading.Thread(
            target=self.ask_ollama,
            daemon=True
        ).start()

    # ── OLLAMA CALL ─────────────────────────

    def ask_ollama(self):

        payload = {
            "model": MODEL,
            "stream": False,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                *self.history
            ]
        }

        try:
            response = requests.post(
                OLLAMA_URL,
                json=payload,
                timeout=120
            )

            print("STATUS:", response.status_code)
            print("RAW:", response.text)

            data = response.json()

            reply = data.get("message", {}).get("content", None)

            if not reply:
                reply = "No response from model"

            self.reply_signal.emit(reply)

        except Exception as e:
            print("ERROR:", e)
            self.reply_signal.emit(f"Error: {e}")

    # ── UPDATE UI SAFELY ─────────────────────────

    def finish_reply(self, reply):

        self.add_message("assistant", reply)

        self.history.append({
            "role": "assistant",
            "content": reply
        })

        self.send_btn.setEnabled(True)
        self.input_box.setEnabled(True)
        self.input_box.setFocus()


# ── STANDALONE TEST (optional) ─────────────────────────

if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = ChatbotWidget()
    window.show()

    sys.exit(app.exec())