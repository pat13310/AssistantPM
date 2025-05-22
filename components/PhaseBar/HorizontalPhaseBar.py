from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QMainWindow
)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QColor, QPixmap, QPainter, QPen, QPainterPath
from PySide6.QtSvg import QSvgRenderer

from components.PhaseBar.PhaseWidget import PhaseWidget



class HorizontalPhaseBar(QWidget):
    def __init__(self):
        super().__init__()
        self.phases = [
            {
                "name": "Analyse des Besoins",
                "icon": "assets/icons/search.svg",
                "color": "#3B82F6",
                "border": "#B3DDF2",
                "description": "Identification et documentation des exigences du projet"
            },
            {
                "name": "Conception",
                "icon": "assets/icons/pen-tool.svg",
                "color": "#A855F7",
                "border": "#D8B4FE",
                "description": "Élaboration de l'architecture et des spécifications détaillées"
            },
            {
                "name": "Développement",
                "icon": "assets/icons/code.svg",
                "color": "#059669",
                "border": "#A7F3D0",
                "description": "Implémentation du code et des fonctionnalités"
            },
            {
                "name": "Tests",
                "icon": "assets/icons/test-tube.svg",
                "color": "#D97706",
                "border": "#FDE68A",
                "description": "Validation et vérification de la qualité"
            },
            {
                "name": "Déploiement",
                "icon": "assets/icons/rocket.svg",
                "color": "#16A34A",
                "border": "#BBF7D0",
                "description": "Mise en production et maintenance"
            },
        ]
        self.phase_widgets = []
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(50)

        for phase in self.phases:
            widget = PhaseWidget(phase)
            widget.phaseClicked.connect(self.on_phase_clicked)
            self.phase_widgets.append(widget)
            #widget.setValidated(True)  # Simule la validation de la phase
            layout.addWidget(widget)

    def on_phase_clicked(self, phase_name: str):
        for widget in self.phase_widgets:
            widget.set_active(widget.phase["name"] == phase_name)
        print(f"Phase cliquée : {phase_name}")

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pen = QPen(QColor("#D1D5DB"), 2)
        painter.setPen(pen)
        painter.setBrush(QColor("#D1D5DB"))

        for i in range(len(self.phase_widgets) - 1):
            w1 = self.phase_widgets[i]
            w2 = self.phase_widgets[i + 1]

            g1 = w1.geometry()
            g2 = w2.geometry()

            x1 = g1.right() + 5
            x2 = g2.left() - 15
            y = g1.center().y()

            painter.drawLine(x1, y, x2, y)

            path = QPainterPath()
            path.moveTo(x2, y)
            path.lineTo(x2 - 6, y - 6)
            path.lineTo(x2 - 6, y + 6)
            path.closeSubpath()
            painter.drawPath(path)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Phases du Projet")
        self.setMinimumSize(1000, 600)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        title = QLabel("Phases du Projet")
        title.setStyleSheet("font-size: 22px; font-weight: 600; color: #1F2937;")
        title.setAlignment(Qt.AlignLeft)

        bar = HorizontalPhaseBar()

        layout.addWidget(title)
        layout.addWidget(bar)
        self.setCentralWidget(central)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
