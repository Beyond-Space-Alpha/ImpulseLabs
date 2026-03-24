import sys
import requests
import markdown
import re

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QLabel
)

from PyQt5.QtWebEngineWidgets import QWebEngineView


#model

MODEL = "llama3:8b"

SYSTEM_PROMPT = """
You are an aerospace engineering assistant.

Rules:
- Use Markdown
- Use LaTeX for equations
- Use $$ for equations
- Use \\cdot
- Use \\frac
- Use \\pi
- Keep answers structured
"""


#theme option

Theme = {
    "dark": {
        "chat_bg": "#1e1e1e",
        "text": "#ffffff"
    },
    "light": {
        "chat_bg": "#ffffff",
        "text": "#000000"
    }
}


#latex

class LatexFixer:

    @staticmethod
    def fix(text):
        text = re.sub(r'cdot', r'\\cdot', text)
        text = re.sub(r'rac\{', r'\\frac{', text)
        text = re.sub(r'pi', r'\\pi', text)
        return text


#markdown renderer?

class MarkdownRenderer:

    @staticmethod
    def protect_latex(text):

        blocks = []

        def repl(match):
            blocks.append(match.group(0))
            return f"LATEX_BLOCK_{len(blocks)-1}"

        text = re.sub(r"\$\$.*?\$\$", repl, text, flags=re.DOTALL)
        text = re.sub(r"\$.*?\$", repl, text)

        return text, blocks

    @staticmethod
    def restore_latex(html, blocks):

        for i, block in enumerate(blocks):
            block = LatexFixer.fix(block)
            html = html.replace(f"LATEX_BLOCK_{i}", block)

        return html

    @staticmethod
    def to_html(text):

        protected, blocks = MarkdownRenderer.protect_latex(text)

        html = markdown.markdown(
            protected,
            extensions=["fenced_code", "tables", "nl2br"]
        )

        html = MarkdownRenderer.restore_latex(html, blocks)

        return html


#render?

class ChatRenderer:

    @staticmethod
    def format(role, text):

        html = MarkdownRenderer.to_html(text)

        return f"""
        <div class="msg">
            <div class="{role}">{role.capitalize()}:</div>
            <div class="content">{html}</div>
        </div>
        """


#ollama

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
            }
        )

        data = response.json()
        return data["message"]["content"]


#ui

class ChatApp(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Aerospace AI")
        self.setGeometry(200, 200, 900, 700)

        self.theme = "dark"
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.chat_html = ""

        self.init_ui()

    #layout

    def init_ui(self):

        layout = QVBoxLayout(self)

        header = QHBoxLayout()

        self.title = QLabel("Aerospace Assistant")

        self.theme_btn = QPushButton("Toggle Theme")
        self.theme_btn.clicked.connect(self.toggle_theme)

        header.addWidget(self.title)
        header.addStretch()
        header.addWidget(self.theme_btn)

        layout.addLayout(header)

        self.browser = QWebEngineView()
        layout.addWidget(self.browser)

        self.set_html()

        input_layout = QHBoxLayout()

        self.input = QLineEdit()
        self.input.returnPressed.connect(self.send)

        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.send)

        input_layout.addWidget(self.input)
        input_layout.addWidget(self.send_btn)

        layout.addLayout(input_layout)

    #html

    def set_html(self):

        t = Theme[self.theme]

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
            background:{t['chat_bg']};
            color:{t['text']};
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
            border-bottom:1px solid #444;
            padding-bottom:10px;
        }}

        </style>

        </head>

        <body>

        <div id="chat">
        {self.chat_html}
        </div>

        </body>
        </html>
        """

        self.browser.setHtml(html)

    #to send message

    def send(self):

        text = self.input.text().strip()

        if not text:
            return

        self.input.clear()

        self.messages.append({
            "role": "user",
            "content": text
        })

        self.chat_html += ChatRenderer.format("user", text)
        self.set_html()

        QApplication.processEvents()

        reply = OllamaClient.ask(self.messages)

        self.messages.append({
            "role": "assistant",
            "content": reply
        })

        self.chat_html += ChatRenderer.format("assistant", reply)
        self.set_html()
    #theme
    def toggle_theme(self):

        if self.theme == "dark":
            self.theme = "light"
        else:
            self.theme = "dark"

        self.set_html()


#main

if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = ChatApp()
    window.show()

    sys.exit(app.exec_())