import sys
sys.path.append("e:/projets QT/AssistanPM")
from PySide6.QtWidgets import QApplication, QMainWindow
import sys
from components.DocBar.DocumentationViewer import DocumentationViewer

if __name__ == "__main__":
    app = QApplication(sys.argv)

    docs = [
        {"title": "Doc", "subtitle": "Fonctionnelle", "icon": "assets/icons/list-check.svg", "ready": True},
        {"title": "Documentation", "subtitle": "Technique", "icon": "assets/icons/code.svg", "ready": True},
        {"title": "Doc", "subtitle": "Architecture", "icon": "assets/icons/layers.svg", "ready": False},
        {"title": "Doc", "subtitle": "Tests", "icon": "assets/icons/test-tube.svg", "ready": False},
    ]

    html_docs = {
        "Doc Fonctionnelle": "<h2>Documentation Fonctionnelle</h2><p>Contenu généré...</p>",
        "Documentation Technique": "<h2>Technique</h2><p>Détails de l'implémentation...</p>",
        "Doc Architecture": "<h2>Architecture</h2><p>À venir</p>",
        "Doc Tests": "<h2>Tests</h2><p>Scénarios en attente</p>",
    }

    window = QMainWindow()
    window.setStyleSheet("background-color: #FEFCFD;")  # Couleur de fond gris clair
    viewer = DocumentationViewer(docs, html_docs)
    window.setCentralWidget(viewer)
    window.setWindowTitle("Documentation AI")
    window.resize(1000, 700)
    window.show()

    sys.exit(app.exec())
