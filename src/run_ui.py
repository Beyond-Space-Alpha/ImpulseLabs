import sys
import qdarkstyle
from PySide6.QtWidgets import QApplication
from gui.main_window import ImpulseLabsWindow

app = QApplication(sys.argv)

app.setStyleSheet(qdarkstyle.load_stylesheet())

window = ImpulseLabsWindow()
window.show()

sys.exit(app.exec())