from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtGui import QColor, QPixmap
from PySide6.QtCore import QSize, Qt
from StepItem import StepItem  # chemin correct

class StepFlowWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        self.steps = [
            {
                "title": "Analyse des Besoins",
                "desc": "Identification et documentation des exigences du projet",
                "icon": "assets/icons/search.svg",
                "color": QColor("#2563EB"),
                "active": True
            },
            {
                "title": "Conception",
                "desc": "Élaboration de l'architecture et des spécifications détaillées",
                "icon": "assets/icons/pen-tool.svg",
                "color": QColor("#9333EA")
            },
            {
                "title": "Développement",
                "desc": "Implémentation du code et des fonctionnalités",
                "icon": "assets/icons/code.svg",
                "color": QColor("#14B8A6")
            },
            {
                "title": "Tests",
                "desc": "Validation et vérification de la qualité",
                "icon": "assets/icons/test-tube.svg",
                "color": QColor("#F59E0B")
            },
            {
                "title": "Déploiement",
                "desc": "Mise en production et maintenance",
                "icon": "assets/icons/rocket.svg",
                "color": QColor("#22C55E")
            },
        ]

        for i, step in enumerate(self.steps):
            item = StepItem(
            title=step["title"],
            subtitle=step["desc"],
            icon_path=step["icon"],
            color=step["color"],
        )
            layout.addWidget(item)

            # Ajouter flèche sauf après le dernier
            if i < len(self.steps) - 1:
                arrow = QLabel()
                arrow.setPixmap(QPixmap("assets/icons/arrow-right.svg").scaled(QSize(24, 24), Qt.KeepAspectRatio, Qt.SmoothTransformation))
                layout.addWidget(arrow)