from PySide6.QtWidgets import QWidget, QHBoxLayout
from PySide6.QtCore import Signal
from components.DocBar.DocTypeBubble import DocTypeBubble


class HorizontalDocBar(QWidget):
    bubbleClicked = Signal(str, bool)  # Signal avec identifiant + état

    def __init__(self, doc_definitions: list[dict]):
        super().__init__()

        # 🎨 Fond légèrement sombre
        self.setStyleSheet("""
            background-color: #E3E4E6;
            border-radius: 2px;
        """)
        self.setFixedHeight(160)

        layout = QHBoxLayout(self)
        layout.setSpacing(40)
        layout.setContentsMargins(20, 20, 20, 20)

        for doc in doc_definitions:
            title = doc["title"]
            subtitle = doc["subtitle"]
            is_ready = doc.get("ready", False)
            icon = doc.get("icon", None)

            bubble = DocTypeBubble(title, subtitle, icon_path=icon, is_ready=is_ready)

            # Connexion avec état et identifiant
            doc_key = f"{title} {subtitle}"
            bubble.clicked.connect(lambda key=doc_key, ready=is_ready: self.bubbleClicked.emit(key, ready))

            layout.addWidget(bubble)
