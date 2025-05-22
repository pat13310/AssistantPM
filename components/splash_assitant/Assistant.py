from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QGridLayout,
    QLabel, QPushButton, QTextBrowser, QMessageBox
)
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QCursor
import sys, os

class CloseButton(QLabel):
    def __init__(self):
        super().__init__("×")
        self.setFont(QFont("Lucida Sans", 16))
        self.setStyleSheet("color: #666;")
        self.setFixedSize(24, 24)
        self.setAlignment(Qt.AlignCenter)
        self.setCursor(QCursor(Qt.PointingHandCursor))

    def enterEvent(self, event):
        self.setStyleSheet("color: red;")

    def leaveEvent(self, event):
        self.setStyleSheet("color: #666;")

    def mousePressEvent(self, event):
        self.window().close()

class AssistantWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Assistant IA - Gestion de Projet")
        self.setFixedSize(580, 500)
        self.setStyleSheet("background-color: white; color: #000;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # === BARRE DU HAUT : grille 3 colonnes ===
        header_layout = QGridLayout()
        header_layout.setColumnStretch(0, 1)
        header_layout.setColumnStretch(1, 3)
        header_layout.setColumnStretch(2, 1)

        icon_path = os.path.join("assets", "icons", "info.svg")
        svg_info = QSvgWidget(icon_path)
        svg_info.setFixedSize(26, 26)
        header_layout.addWidget(svg_info, 0, 0, alignment=Qt.AlignLeft)

        title = QLabel("Assistant IA pour la Gestion de Projet")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title, 0, 1, alignment=Qt.AlignCenter)

        close_btn = CloseButton()
        header_layout.addWidget(close_btn, 0, 2, alignment=Qt.AlignRight)
        
        layout.addLayout(header_layout)
        layout.addSpacing(30)

        # === TEXTE HTML CENTRAL ===
        html = """
        <p style="font-size: 19px; font-weight: 600; margin-bottom: 6px;margin-left: 1rem;">
  Bienvenue dans votre assistant de gestion de projet
</p>
<p style="font-size: 14px;color:#444"> Cet outil vous guidera à travers les différentes phases de votre projet informatique :</p>
<ul style="font-size: 14px;padding-left: 1rem; list-style: none; color:#555;">
  <li style="margin-bottom: 6px"><span style="font-size: 17px;color: #9ca3af;">•</span> <b>Analyse des Besoins</b> – Documentation détaillée des exigences</li>
  <li style="margin-bottom: 6px"><span style="font-size: 17px; color: #9ca3af;">•</span> <b>Conception</b> – Architecture et spécifications techniques</li>
  <li style="margin-bottom: 6px"><span style="font-size: 17px; color: #9ca3af;">•</span> <b>Développement</b> – Implémentation et bonnes pratiques</li>
  <li style="margin-bottom: 6px"><span style="font-size: 17px; color: #9ca3af;">•</span> <b>Tests</b> – Stratégies de validation et qualité</li>
  <li style="margin-bottom: 6px"><span style="font-size: 17px; color: #9ca3af;">•</span> <b>Déploiement</b> – Mise en production et maintenance</li>
</ul>
<p style="font-size: 14px;color:#666">Pour chaque phase, vous serez guidé par des questions pertinentes et des suggestions adaptées à votre contexte.</p>

        """

        browser = QTextBrowser()
        browser.setHtml(html)
        browser.setStyleSheet("border: none;")
        layout.addWidget(browser)

        # === BOUTON COMMENCER ===
        start_btn = QPushButton("Commencer")
        start_btn.setFixedWidth(140)
        start_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1e4fd1;
            }
        """)
        start_btn.clicked.connect(self.handle_start_clicked)
        layout.addWidget(start_btn, alignment=Qt.AlignRight)

    def handle_start_clicked(self):
        QMessageBox.information(self, "Assistant IA", "L'assistant démarre ici...")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AssistantWindow()
    window.show()
    sys.exit(app.exec())
