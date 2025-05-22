from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt

class InfosButton(QPushButton):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(40)
        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #4CAF50, stop: 1 #81C784
                );
                color: white;
                font-weight: bold;
                border-radius: 8px;
                padding: 8px 20px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #43A047, stop: 1 #66BB6A
                );
            }
            QPushButton:disabled {
                background-color: #d1d5db;
                color: #9ca3af;
            }
        """)

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
import sys

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Exemple de StyledButton")

        from InfosButton import InfosButton  # si séparé
        btn = InfosButton("Valider")

        layout = QVBoxLayout(self)
        layout.addWidget(btn)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

