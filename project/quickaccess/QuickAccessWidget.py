import sys
import os

# Détermine le chemin racine du projet et l'ajoute à sys.path
# Cela doit être fait AVANT les imports qui dépendent de ce chemin.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, os.pardir, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
print(f"[DEBUG] QuickAccessWidget.py - PROJECT_ROOT: {PROJECT_ROOT}") # Pour vérification
print(f"[DEBUG] QuickAccessWidget.py - sys.path: {sys.path}") # Pour vérification

# test_flow_widget.py
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt
from components.layout.FlowLayout import FlowLayout
from components.widgets.QuickAccessItemCard import QuickAccessItemCard

class QuickAccessWidget(QWidget): # Renommé pour correspondre au nom de fichier, mais c'est un widget de test
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FlowLayout Test avec QuickAccessItemCard")
        self.resize(700, 400)

        layout = QVBoxLayout(self)
        title = QLabel("Accès Rapide (Test FlowLayout)")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-weight: bold; font-size: 14px; padding-bottom: 8px;")
        layout.addWidget(title)

        # Conteneur avec FlowLayout
        card_container = QWidget()
        self.flow_layout = FlowLayout(card_container, spacing=10) # Ajusté spacing
        card_container.setLayout(self.flow_layout)
        layout.addWidget(card_container)

        # Données test
        phases_data = [
            ("Accueil", "assets/icons/house.svg"),
            ("Documentation", "assets/icons/book-open.svg"),
            ("Code", "assets/icons/code.svg"),
            ("Architecture", "assets/icons/folder-tree.svg"),
            ("Tests", "assets/icons/test-tube.svg"),
            ("Déploiement", "assets/icons/rocket.svg"),
            ("Monitoring", "assets/icons/eye.svg"),
        ]
        for label, icon_path in phases_data:
            # Simuler un callback simple
            card = QuickAccessItemCard(label, icon_path)
            card.clicked.connect(lambda l=label: print(f"Carte '{l}' cliquée!"))
            self.flow_layout.addWidget(card)


if __name__ == '__main__':
    # sys est déjà importé en haut
    app = QApplication(sys.argv)
    win = QuickAccessWidget()
    win.show()
    sys.exit(app.exec())
