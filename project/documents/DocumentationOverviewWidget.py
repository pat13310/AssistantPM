from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QSizePolicy
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QPixmap
from project.documents.DocType import DocType
from components.ui.IconWithText import IconWithText
from project.documents.DocumentCard import DocumentCard
from components.ui.ContainerCard import ContainerCard


class DocumentationOverviewWidget(QWidget):
    docTypeClicked = Signal(DocType)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Aperçu de la Documentation")

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Titre avec icône en utilisant notre nouveau composant IconWithText en vert
        self.header_title = IconWithText(
            text="Types de Documents du Projet",
            icon_name="book-open",
            color="#03b541",  # Couleur verte
            font_size=16,  # Taille réduite
            icon_size=24,   # Taille réduite
            y_text=-8
        )
        main_layout.addWidget(self.header_title)

        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)  # Augmenter l'espacement entre les cartes

        self.doc_cards = {}
        
        # Définition des types de documents avec leurs descriptions, icônes et statut
        doc_types_info = [
            {
                "title": "Cahier des Charges Fonctionnel",
                "description": "Définit les besoins et objectifs du projet",
                "icon": "list-checks",
                "completed": True  # Exemple : ce document est complété
            },
            {
                "title": "Spécifications Fonctionnelles Détaillées",
                "description": "Décrit en détail les fonctionnalités du projet",
                "icon": "layers",
                "completed": False  # Exemple : ce document est en attente
            },
            {
                "title": "Spécifications Techniques Détaillées",
                "description": "Définit l'architecture et les technologies utilisées",
                "icon": "code",
                "completed": False  # Exemple : ce document est en attente
            },
            {
                "title": "Stratégie de Tests et Recette",
                "description": "Plan de tests et critères de validation du projet",
                "icon": "test-tube",
                "completed": False  # Exemple : ce document est en attente
            },
            {
                "title": "Dossier d'Architecture Technique",
                "description": "Détaille l'infrastructure et les composants techniques",
                "icon": "rocket",
                "completed": False  # Exemple : ce document est en attente
            },
        ]

        positions = [(i, j) for i in range(3) for j in range(2)]  # Pour une grille 3x2

        for i, doc_info in enumerate(doc_types_info):
            # Créer le contenu de la carte
            doc_card = DocumentCard(
                title=doc_info["title"],
                description=doc_info["description"],
                icon_name=doc_info["icon"],
                is_completed=doc_info["completed"]  # Indiquer si le document est complété
            )
            
            # Créer le conteneur avec cadre et ombre
            container = ContainerCard()
            container.addWidget(doc_card)
            
            # Connecter le signal clicked du conteneur à l'émission du signal docTypeClicked
            container.clicked.connect(lambda title=doc_info["title"]: self.docTypeClicked.emit(DocType(title)))
            
            # Stocker la carte dans le dictionnaire
            self.doc_cards[doc_info["title"]] = container
            
            # Ajouter la carte à la grille
            if i < len(positions):
                grid_layout.addWidget(container, positions[i][0], positions[i][1])
            else: # Au cas où il y aurait plus de cartes que de positions définies
                grid_layout.addWidget(container, i // 2, i % 2)

        main_layout.addLayout(grid_layout)
        self.setLayout(main_layout)

    # def handle_doc_type_clicked(self, doc_type_name):
    #     print(f"Bouton de document cliqué : {doc_type_name}")
        # Ici, on pourrait ouvrir un éditeur, un visualiseur PDF, etc.


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = DocumentationOverviewWidget()
    window.resize(600, 400)
    window.show()
    sys.exit(app.exec())
