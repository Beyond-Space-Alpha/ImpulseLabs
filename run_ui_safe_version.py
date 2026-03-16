import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window_safe_version import MainWindow


app = QApplication(sys.argv)

window = MainWindow()

window.show()

sys.exit(app.exec_())