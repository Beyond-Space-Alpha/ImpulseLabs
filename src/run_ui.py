import sys
import qdarkstyle
from PySide6.QtWidgets import QApplication
from gui.main_window import ImpulseLabsWindow

def start():
    app = QApplication(sys.argv)

    app.setStyleSheet(qdarkstyle.load_stylesheet())

    window = ImpulseLabsWindow()
    window.show()

    sys.exit(app.exec())
    
if __name__ == "__main__":
    start()