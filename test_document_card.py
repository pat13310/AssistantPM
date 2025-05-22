import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QGridLayout
from components.ui.DocumentCard import DocumentCard

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test DocumentCard")
        self.setMinimumSize(800, 600)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.setStyleSheet("background-color: #f9fafb;")

        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Grille pour les cartes
        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)
        
        # Définition des types de documents avec leurs descriptions et icônes
        doc_types_info = [
            {
                "title": "Cahier des Charges Fonctionnel",
                "description": "Définit les besoins et objectifs du projet",
                "icon": "list-checks"
            },
            {
                "title": "Spécifications Fonctionnelles Détaillées",
                "description": "Décrit en détail les fonctionnalités du projet",
                "icon": "layers"
            },
            {
                "title": "Spécifications Techniques Détaillées",
                "description": "Définit l'architecture et les technologies utilisées",
                "icon": "code"
            },
            {
                "title": "Stratégie de Tests et Recette",
                "description": "Plan de tests et critères de validation du projet",
                "icon": "test-tube"
            },
            {
                "title": "Dossier d'Architecture Technique",
                "description": "Détaille l'infrastructure et les composants techniques",
                "icon": "rocket"
            },
        ]
        
        # Positions pour la grille
        positions = [(i, j) for i in range(3) for j in range(2)]
        
        # Créer les cartes
        for i, doc_info in enumerate(doc_types_info):
            card = DocumentCard(
                title=doc_info["title"],
                description=doc_info["description"],
                icon_name=doc_info["icon"]
            )
            
            # Connecter le signal clicked
            card.clicked.connect(lambda title, t=doc_info["title"]: print(f"Carte cliquée: {t}"))
            
            # Ajouter à la grille
            if i < len(positions):
                grid_layout.addWidget(card, positions[i][0], positions[i][1])
            else:
                grid_layout.addWidget(card, i // 2, i % 2)
        
        main_layout.addLayout(grid_layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())
