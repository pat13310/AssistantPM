from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class CollapsibleSection(QWidget):
    def __init__(self, title: str):
        super().__init__()

        self.is_expanded = True

        # Layout principal du composant
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Titre cliquable
        self.title = title
        self.header = QLabel(f"▼ {self.title}")
        self.header.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.header.setStyleSheet("padding: 6px;")
        self.header.setCursor(Qt.PointingHandCursor)
        self.header.mousePressEvent = self.toggle_content

        # Conteneur pliable
        self.container = QFrame()
        self.container.setFrameShape(QFrame.NoFrame)
        self.container.setVisible(True)  # ← très important

        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(2, 0, 0, 0)
        self.container_layout.setSpacing(0)

        # Assemblage
        self.main_layout.addWidget(self.header)
        self.main_layout.addWidget(self.container)

    def add_widget(self, widget: QWidget):
        self.container_layout.addWidget(widget)

    def toggle_content(self, event=None):
        self.is_expanded = not self.is_expanded
        self.container.setVisible(self.is_expanded)
        arrow = "▼" if self.is_expanded else "▶"
        self.header.setText(f"{arrow} {self.title}")

    def collapse(self):
        self.is_expanded = False
        self.container.setVisible(False)
        self.header.setText(f"▶ {self.title}")

    def expand(self):
        self.is_expanded = True
        self.container.setVisible(True)
        self.header.setText(f"▼ {self.title}")
