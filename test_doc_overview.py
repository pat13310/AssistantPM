import sys
import os

# Ajouter le répertoire racine au chemin Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication, QMainWindow
from project.documents.DocumentationOverviewWidget import DocumentationOverviewWidget

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Documentation Overview")
        self.setStyleSheet("background-color: #f3f6fb;")
        self.setMinimumSize(800, 600)
        
        # Créer le widget de documentation
        self.doc_overview = DocumentationOverviewWidget()
        
        # Connecter le signal docTypeClicked
        self.doc_overview.docTypeClicked.connect(self.handle_doc_type_clicked)
        
        # Définir comme widget central
        self.setCentralWidget(self.doc_overview)
    
    def handle_doc_type_clicked(self, doc_type):
        print(f"Type de document cliqué: {doc_type.value}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())
