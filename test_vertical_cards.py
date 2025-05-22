import sys
import os

# Ajouter le répertoire racine au chemin Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from components.ui.DocumentCard import DocumentCard
from components.ui.ContainerCard import ContainerCard

class VerticalCardsTest(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Cartes Verticales")
        self.setMinimumSize(600, 800)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(30)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Définition des cartes avec leurs icônes correspondantes
        cards_data = [
            ("Cahier des Charges Fonctionnel", "Définit les besoins et objectifs du projet", "list-checks"),
            ("Spécifications Fonctionnelles Détaillées", "Décrit en détail les fonctionnalités du projet", "layers"),
            ("Spécifications Techniques Détaillées", "Définit l'architecture et les technologies utilisées", "code"),
            ("Stratégie de Tests et Recette", "Plan de tests et critères de validation du projet", "test-tube"),
            ("Dossier d'Architecture Technique", "Détaille l'infrastructure et les composants techniques", "rocket"),
        ]
        
        for title, desc, icon in cards_data:
            # Créer la carte de document
            doc_card = DocumentCard(title, desc, icon)
            
            # Créer le conteneur
            container = ContainerCard()
            container.addWidget(doc_card)
            
            # Connecter le signal clicked
            container.clicked.connect(lambda t=title: print(f"Carte cliquée: {t}"))
            
            # Ajouter au layout
            layout.addWidget(container)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VerticalCardsTest()
    window.show()
    sys.exit(app.exec())
