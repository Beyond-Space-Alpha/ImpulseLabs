import sys
import requests
import markdown
import re
import threading

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel
)
from PySide6.QtCore import QTimer
from PySide6.QtWebEngineWidgets import QWebEngineView


# -------------------------
# Config
# -------------------------
MODEL = "llama3:8b"

SYSTEM_PROMPT = """
You are an aerospace engineering assistant.

Rules:
- Use Markdown
- Use LaTeX for equations
- Use $$ for block equations, $ for inline
- Use \\cdot for multiplication
- Use \\frac for fractions
- Use \\pi for pi
- Keep answers structured
"""

THEMES = {
    "dark": {
        "chat_bg": "#1e1e1e",
        "text": "#ffffff"
    },
    "light": {
        "chat_bg": "#f5f5f5",
        "text": "#111111"
    }
}


# -------------------------
# LaTeX fixer
# -------------------------
class LatexFixer:

    @staticmethod
    def fix(content):
        content = re.sub(r'(?<!\\)\bfrac\{', r'\\frac{', content)
        content = re.sub(r'(?<!\\)\bcdot\b',  r'\\cdot',  content)
        content = re.sub(r'(?<!\\)\bpi\b',    r'\\pi',    content)
        return content


# -------------------------
# Markdown + LaTeX renderer
# -------------------------
class MarkdownRenderer:

    @staticmethod
    def protect_latex(content):
        """Pull LaTeX blocks out before markdown parsing so they aren't mangled."""
        blocks = []

        def repl(match):
            blocks.append(match.group(0))
            return f"LATEX_BLOCK_{len(blocks) - 1}"

        # Block equations first, then inline
        content = re.sub(r"\$\$.*?\$\$", repl, content, flags=re.DOTALL)
        content = re.sub(r"\$.*?\$",     repl, content)

        return content, blocks

    @staticmethod
    def restore_latex(html, blocks):
        for i, block in enumerate(blocks):
            block = LatexFixer.fix(block)
            html = html.replace(f"LATEX_BLOCK_{i}", block)
        return html

    @staticmethod
    def to_html(content):
        # FIX: only escape backslashes OUTSIDE latex blocks.
        # The original code did text.replace("\\", "\\\\") on the whole string
        # BEFORE protecting latex — that doubled backslashes inside equations.
        protected, blocks = MarkdownRenderer.protect_latex(content)

        # Escape backslashes only in the non-latex parts
        protected = protected.replace("\\", "\\\\")

        html = markdown.markdown(
            protected,
            extensions=["fenced_code", "tables", "nl2br"]
        )

        html = MarkdownRenderer.restore_latex(html, blocks)
        return html


# -------------------------
# Chat message formatter
# -------------------------
class ChatRenderer:

    @staticmethod
    def format(role, content):
        html_body = MarkdownRenderer.to_html(content)
        return f"""
        <div class="msg">
            <div class="{role}">{role.capitalize()}:</div>
            <div class="content">{html_body}</div>
        </div>
        """


# -------------------------
# Ollama API client
# -------------------------
class OllamaClient:

    @staticmethod
    def ask(messages):
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": MODEL,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_ctx": 4096
                }
            },
            timeout=120   # FIX: was missing — hangs forever if Ollama is slow
        )
        response.raise_for_status()  # FIX: was missing — silent failures on HTTP errors
        return response.json()["message"]["content"]


# -------------------------
# Main UI
# -------------------------
class ChatApp(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Aerospace AI")
        self.setGeometry(200, 200, 900, 700)

        self.theme = "dark"
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.chat_html = ""

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Header
        header = QHBoxLayout()
        self.title = QLabel("Aerospace Assistant")
        self.theme_btn = QPushButton("Toggle Theme")
        self.theme_btn.clicked.connect(self.toggle_theme)
        header.addWidget(self.title)
        header.addStretch()
        header.addWidget(self.theme_btn)
        layout.addLayout(header)

        # Chat view
        self.browser = QWebEngineView()
        layout.addWidget(self.browser)
        self.set_html()

        # Input row
        input_layout = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("Ask an aerospace question...")
        self.input.returnPressed.connect(self.send)
        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.send)
        input_layout.addWidget(self.input)
        input_layout.addWidget(self.send_btn)
        layout.addLayout(input_layout)

    def set_html(self):
        t = THEMES[self.theme]

        html = f"""
        <html>
        <head>
        <script>
        window.MathJax = {{
            tex: {{
                inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
                displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']]
            }}
        }};
        </script>
        <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
        <style>
        body {{
            background: {t['chat_bg']};
            color: {t['text']};
            font-family: Segoe UI, sans-serif;
            padding: 20px;
        }}
        .user      {{ color: #4fc3f7; font-weight: bold; }}
        .assistant {{ color: #ff8a65; font-weight: bold; }}
        .msg {{
            margin-bottom: 20px;
            border-bottom: 1px solid #444;
            padding-bottom: 10px;
        }}
        code {{
            background: #2d2d2d;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: monospace;
        }}
        pre code {{
            display: block;
            padding: 12px;
        }}
        </style>
        </head>
        <body>
        <div id="chat">{self.chat_html}</div>
        </body>
        </html>
        """

        self.browser.setHtml(html)

    def send(self):
        user_text = self.input.text().strip()   # FIX: renamed from `text` (shadows builtins)
        if not user_text:
            return

        self.input.clear()
        self.send_btn.setEnabled(False)         # FIX: disable while waiting for reply
        self.input.setEnabled(False)

        self.messages.append({"role": "user", "content": user_text})
        self.chat_html += ChatRenderer.format("user", user_text)
        self.set_html()

        threading.Thread(target=self.get_bot_reply, daemon=True).start()  # FIX: daemon=True

    def toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        self.set_html()

    def get_bot_reply(self):
        try:
            reply = OllamaClient.ask(self.messages)
            self.messages.append({"role": "assistant", "content": reply})
            QTimer.singleShot(0, lambda: self.update_ui(reply))

        except requests.exceptions.ConnectionError:
            err = "⚠️ Cannot connect to Ollama. Run `ollama serve` first."
            QTimer.singleShot(0, lambda: self.update_ui(err))

        except Exception as e:
            err = f"⚠️ Error: {e}"
            QTimer.singleShot(0, lambda: self.update_ui(err))

    def update_ui(self, reply):
        self.chat_html += ChatRenderer.format("assistant", reply)
        self.set_html()
        self.send_btn.setEnabled(True)    # FIX: re-enable after reply arrives
        self.input.setEnabled(True)
        self.input.setFocus()


# -------------------------
# Entry point
# -------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatApp()
    window.show()
    sys.exit(app.exec())   # FIX: PySide6 uses .exec() not .exec_()