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
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QScrollArea
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon
from PySide6.QtSvgWidgets import QSvgWidget
from components.layout.FlowLayout import FlowLayout
from project.quickaccess.QuickAccessItemCard import QuickAccessItemCard

class QuickAccessWidget(QWidget):
    # Signal émis lorsqu'une action est sélectionnée, avec le nom de l'action et le nom du projet
    action_selected = Signal(str, str)
    
    def __init__(self, project_name=""):
        super().__init__()
        self.setWindowTitle("Accès Rapide")
        self.resize(800, 500)
        self.project_name = project_name

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Créer un widget de contenu qui sera placé dans le ScrollArea
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # En-tête avec icône et titre du projet
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #e6f7e6;
                border-radius: 10px;
                border: 1px solid #86efac;
                padding: 10px;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(15,15, 15, 15)
        header_layout.setSpacing(15)
        
        # Utiliser un widget SVG pour l'icône
        from ui.ui_utils import load_colored_svg
        
        # Chemin vers le fichier SVG
        icon_path = os.path.join(PROJECT_ROOT, "assets", "icons", "boxes.svg")
        
        # Créer un conteneur pour l'icône
        icon_container = QWidget()
        icon_container.setFixedSize(48, 48)
        icon_container.setStyleSheet("background-color: #e6f7e6; border: none;")
        
        # Layout pour centrer l'icône
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(8, 8, 8, 8)  # Marges pour que l'icône ne touche pas les bords
        icon_layout.setAlignment(Qt.AlignCenter)
        
        # Créer un widget SVG coloré en vert
        svg_data = load_colored_svg(icon_path, "#22c55e")  # Couleur verte
        icon_widget = QSvgWidget()
        icon_widget.load(svg_data)
        icon_widget.setFixedSize(28, 28)  # Taille de l'icône
        
        # Ajouter l'icône au conteneur
        icon_layout.addWidget(icon_widget)
        
        # Ajouter le conteneur au layout de l'en-tête
        header_layout.addWidget(icon_container)
        
        # Titre du projet en vert
        self.project_title = QLabel(f"Accès Rapide - Projet  " + (f"{project_name}" if project_name else ""))
        self.project_title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.project_title.setStyleSheet("color: #22c55e; margin-left: 10px; border:none;")
        header_layout.addWidget(self.project_title)
        header_layout.addStretch(1)
        
        layout.addWidget(header_frame)

        # Sous-titre
        subtitle = QLabel("Sélectionnez une action rapide :")
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setStyleSheet("color: #666; margin-top: 10px; margin-bottom: 5px;")
        layout.addWidget(subtitle)
        
        # Conteneur avec FlowLayout
        card_container = QFrame()
        card_container.setStyleSheet("""
            QFrame {
                background-color: #f9fafb;
                border-radius: 8px;
                border: 1px solid #e5e7eb;
                padding: 15px;
            }
        """)
        container_layout = QVBoxLayout(card_container)
        container_layout.setContentsMargins(15, 15, 15, 15)
        
        self.flow_layout = FlowLayout(spacing=15) # Espacement augmenté
        container_layout.addLayout(self.flow_layout)
        layout.addWidget(card_container)

        # Données des cartes d'accès rapide avec descriptions
        self.phases_data = [
            ("Documentation", "assets/icons/book-open.svg", "Accéder à la documentation complète du projet"),
            ("Code Source", "assets/icons/code.svg", "Explorer et modifier le code source du projet"),
            ("Architecture", "assets/icons/folder-tree.svg", "Visualiser la structure et l'architecture du projet"),
            ("Tests", "assets/icons/test-tube.svg", "Exécuter et gérer les tests du projet"),
            ("Déploiement", "assets/icons/rocket.svg", "Gérer les paramètres de déploiement"),
            ("Monitoring", "assets/icons/eye.svg", "Surveiller les performances et l'état du projet"),
            ("Paramètres", "assets/icons/settings.svg", "Configurer les options du projet"),
            ("Retour", "assets/icons/arrow-left.svg", "Retourner à la liste des projets"),
        ]
        
        self.create_cards()
        
        # Ajouter un espacement en bas
        layout.addStretch(1)
        
        # Créer un ScrollArea pour permettre le défilement
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(content_widget)
        
        # Style du ScrollArea
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background: #f0f0f0;
                width: 12px;
                margin: 0px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
        # Ajouter le ScrollArea au layout principal
        main_layout.addWidget(scroll_area)
        
    def create_cards(self):
        """Crée les cartes d'accès rapide"""
        # Effacer les cartes existantes
        while self.flow_layout.count():
            item = self.flow_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Créer les nouvelles cartes avec descriptions
        for item in self.phases_data:
            if len(item) >= 3:
                label, icon_path, description = item
            else:
                label, icon_path = item
                description = None
                
            card = QuickAccessItemCard(label, icon_path, description)
            card.clicked.connect(lambda checked=False, l=label: self.handle_card_click(l))
            self.flow_layout.addWidget(card)
    
    def handle_card_click(self, label):
        """Gère le clic sur une carte"""
        print(f"Carte '{label}' cliquée pour le projet '{self.project_name}'")
        
        # Signal à émettre lorsqu'une action spécifique est sélectionnée
        if hasattr(self, "action_selected"):
            self.action_selected.emit(label, self.project_name)
        
    def set_project(self, project_name):
        """Définit le projet actif"""
        self.project_name = project_name
        self.project_title.setText(f"Accès Rapide du Projet : '{project_name}'")
        
        # Rafraîchir l'interface
        self.update()


if __name__ == '__main__':
    # sys est déjà importé en haut
    app = QApplication(sys.argv)
    win = QuickAccessWidget()
    win.show()
    sys.exit(app.exec())
