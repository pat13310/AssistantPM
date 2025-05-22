import sys
from PySide6.QtWidgets import QApplication
from project.documents.DocumentationWidget import DocumentationWidget
from project.documents.DocType import DocType

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Créer un type de document de test
    class TestDocType(DocType):
        def __init__(self):
            self.value = "CAHIER_DES_CHARGES_FONCTIONNEL"
            self.name = "CAHIER_DES_CHARGES_FONCTIONNEL"

    # Créer et afficher le widget
    widget = DocumentationWidget(TestDocType())
    widget.show()
    
    sys.exit(app.exec())
