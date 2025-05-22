import sys
import os

# Ajouter le répertoire racine au chemin Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from components.ui.ProjectCard import ProjectCard

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Carte Projet")
        self.setMinimumSize(600, 400)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)
        
        # Exemples de projets
        projects_data = [
            {
                "title": "Paye",
                "description": "Un logiciel de gestion des comptes",
                "creation_date": "10 mai 2025 à 18:11",
                "icon": "presentation"
            },
            {
                "title": "Site Web E-commerce",
                "description": "Plateforme de vente en ligne pour produits artisanaux",
                "creation_date": "15 avril 2025 à 14:30",
                "icon": "shopping-cart"
            },
            {
                "title": "Application Mobile",
                "description": "Application de suivi de fitness pour sportifs",
                "creation_date": "22 mars 2025 à 09:45",
                "icon": "smartphone"
            }
        ]
        
        # Créer les cartes de projet
        for project in projects_data:
            card = ProjectCard(
                title=project["title"],
                description=project["description"],
                creation_date=project["creation_date"],
                icon_name=project["icon"]
            )
            
            # Connecter le signal clicked
            card.clicked.connect(lambda t=project["title"]: print(f"Projet cliqué: {t}"))
            
            # Ajouter au layout
            main_layout.addWidget(card)
        
        main_layout.addStretch()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())
