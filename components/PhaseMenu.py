from components.PhaseLabel import PhaseLabel
from PySide6.QtWidgets import QVBoxLayout, QWidget


class PhaseMenu(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(8)

        # Ajuster les chemins des icônes pour qu'ils soient relatifs
        phases = [
            ("Analyse des Besoins", "assets/icons/search.svg"),
            ("Conception", "assets/icons/pen-tool.svg"),
            ("Développement", "assets/icons/code.svg"),
            ("Tests", "assets/icons/test-tube.svg"),
            ("Déploiement", "assets/icons/rocket.svg"),
        ]

        self.labels = []

        for text, icon in phases:
            label = PhaseLabel(text, icon_path=icon, on_click=self.label_clicked)
            self.layout.addWidget(label)
            self.labels.append(label)

        self.layout.addStretch()

    def label_clicked(self, clicked_label):
        for label in self.labels:
            if label is not clicked_label:
                label.reset()

    def toggle_text_visibility(self, show_text: bool):
        for label in self.labels:
            label.show_only_icon(show_text)
