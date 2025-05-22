from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGridLayout, QSizePolicy
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QPixmap
from project.documents.DocType import DocType
from components.widgets.HeaderTitle import HeaderTitle


class DocumentationOverviewWidget(QWidget):
    docTypeClicked = Signal(DocType)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Aperçu de la Documentation")

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Titre avec icône
        self.header_title = HeaderTitle(title="Types de Documents du Projet", icon_path="assets/icons/book-open.svg")
        main_layout.addWidget(self.header_title)

        grid_layout = QGridLayout()
        grid_layout.setSpacing(16)

        self.doc_buttons = {}
        doc_types = [
            "Cahier des Charges Fonctionnel",
            "Spécifications Fonctionnelles Détaillées",
            "Spécifications Techniques Détaillées",
            "Stratégie de Tests et Recette",
            "Dossier d'Architecture Technique",
        ]

        positions = [(i, j) for i in range(3) for j in range(2)]  # Pour une grille 3x2

        for i, doc_type in enumerate(doc_types):
            button = QPushButton(doc_type)
            button.setMinimumHeight(60)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred) # Permettre l'expansion horizontale
            button.setStyleSheet(
                """
                QPushButton {
                    font-size: 14px;
                    padding: 10px;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    background-color: #ffffff;
                    color: #374151;
                    text-align: left;
                    padding-left: 20px;
                }
                QPushButton:hover {
                    background-color: #f9fffb;
                    border: 1px solid #1bffe0;
                }
            """
            )
            # Connecter le signal clicked du bouton à l'émission du signal docTypeClicked avec le type de document
            button.clicked.connect(lambda checked, doc_type=doc_type: self.docTypeClicked.emit(DocType(doc_type)))
            self.doc_buttons[doc_type] = button
            if i < len(positions):
                grid_layout.addWidget(button, positions[i][0], positions[i][1])
            else: # Au cas où il y aurait plus de boutons que de positions définies
                grid_layout.addWidget(button, i // 2, i % 2)

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
