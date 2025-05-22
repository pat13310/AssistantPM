from PySide6.QtWidgets import QApplication, QMainWindow
from StepFlowWidget import StepFlowWidget
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Phases du Projet")
        self.setCentralWidget(StepFlowWidget())
        self.setStyleSheet("background-color: #F9FAFB;")
        self.resize(1000, 300)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())