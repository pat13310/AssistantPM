from PySide6.QtWidgets import (
    QWidget, 
    QVBoxLayout, 
    QHBoxLayout, 
    QFrame, 
    QLabel, 
    QLineEdit, 
    QPushButton,
    QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QPixmap, QPainter
from PySide6.QtSvg import QSvgRenderer

# Import de la fonction utilitaire pour charger les SVG colorés
import os
import sys

# Import direct car désormais dans le même package
from ui.ui_utils import load_colored_svg

class InputChatBubble(QWidget):
    """Classe pour créer des bulles de chat avec des champs de saisie interactifs"""
    
    # Signal émis lorsque le nom du projet est soumis
    projectNameSubmitted = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.initUI()
        
    def initUI(self):
        """Initialise l'interface utilisateur de base"""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
    def get_svg_icon(self, icon_name, size=16, color=None):
        """
        Fonction utilitaire pour charger une icône SVG et la convertir en QPixmap avec fond transparent
        en utilisant directement load_colored_svg avec anti-aliasing pour éviter la pixelisation

        Args:
            icon_name (str): Nom du fichier SVG sans extension
            size (int): Taille de l'icône en pixels (peut être doublée pour une meilleure qualité)
            color (str): Couleur à appliquer à l'icône (format CSS, ex: '#4CAF50')

        Returns:
            QPixmap: L'icône chargée ou None si le fichier n'existe pas
        """
        # Chemin des icônes vers la racine du projet
        # Trouver la racine du projet (en remontant au niveau approprié)
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
        
        icon_path = os.path.join(
            root_dir,
            "assets",
            "icons",
            f"{icon_name}.svg",
        )

        if not os.path.exists(icon_path):
            print(f"[Erreur] Fichier SVG introuvable : {icon_path}")
            return None

        try:
            # Doubler la taille pour un meilleur rendu puis redimensionner
            render_size = size * 2

            # Créer un QPixmap de la taille doublée avec fond transparent
            pixmap = QPixmap(render_size, render_size)
            pixmap.fill(Qt.transparent)

            # Charger le SVG avec la couleur spécifiée
            svg_data = load_colored_svg(icon_path, color)
            if svg_data.isEmpty():
                print(f"[Erreur] SVG vide ou incorrect : {icon_path}")
                return None

            # Créer un QSvgRenderer pour dessiner le SVG
            renderer = QSvgRenderer(svg_data)

            # Dessiner le SVG sur le pixmap avec anti-aliasing
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing, True)
            painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
            painter.setRenderHint(QPainter.TextAntialiasing, True)

            # Dessiner le SVG en utilisant tout l'espace disponible
            renderer.render(painter)
            painter.end()

            # Redimensionner à la taille finale avec une transformation lisse
            if render_size != size:
                return pixmap.scaled(
                    size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )

            return pixmap
        except Exception as e:
            print(f"[Erreur] Impossible de charger l'icône {icon_name}: {str(e)}")
            return None
    
    def add_project_name_input(self):
        """Ajoute une bulle interactive pour saisir le nom du projet"""
        # Créer un conteneur pour la bulle
        bubble_container = QWidget()
        # Définir une hauteur maximale fixe pour le conteneur
        bubble_container.setMaximumHeight(200)  # Limiter explicitement la hauteur
        container_layout = QVBoxLayout(bubble_container)
        container_layout.setContentsMargins(0, 0, 0, 10)
        
        # Aligner la bulle à gauche avec un layout horizontal
        h_layout = QHBoxLayout()
        
        # Créer un widget pour contenir la bulle avec une largeur limitée
        bubble_wrapper = QWidget()
        bubble_wrapper.setFixedWidth(500)  # Largeur réduite de moitié (environ)
        # Définir la politique de taille pour limiter la hauteur au contenu
        bubble_wrapper.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        wrapper_layout = QVBoxLayout(bubble_wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        
        h_layout.addWidget(bubble_wrapper)
        h_layout.addStretch(1)  # Espace à droite pour pousser la bulle à gauche
        container_layout.addLayout(h_layout)
        
        # Créer une bulle de chat pour contenir l'input
        bubble = QFrame()
        bubble.setObjectName("input_bubble")
        bubble.setStyleSheet("""
            QFrame#input_bubble {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(227, 242, 253, 0.8), stop:1 rgba(187, 222, 251, 0.8));
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;
                border-bottom-left-radius: 0px; /* Angle droit en bas à gauche */
                border: 2px solid #1976D2;
                padding: 2px 5px 10px 5px;
            }
        """)
        
        # Layout pour la bulle
        bubble_layout = QVBoxLayout(bubble)
        bubble_layout.setContentsMargins(10, 10, 10, 10)
        bubble_layout.setSpacing(6)
        
        # Titre de la section avec icône
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 8)
        title_layout.setSpacing(12)
        
        # Icône de configuration
        title_icon = QLabel()
        title_icon.setFixedSize(18, 18)
        title_icon.setStyleSheet("background: transparent; border: none;")
        config_pixmap = self.get_svg_icon("settings", size=18, color="#1976D2")
        if config_pixmap:
            title_icon.setPixmap(config_pixmap)
        title_layout.addWidget(title_icon)
        
        title_label = QLabel("Configuration du projet")
        title_label.setStyleSheet("""
            color: #1976D2; 
            font-weight: bold; 
            font-size: 14px;
            background: transparent;
        """)
        title_layout.addWidget(title_label)
        title_layout.addStretch(1)
        
        bubble_layout.addLayout(title_layout)
        
        # Champ de saisie pour le nom du projet
        input_layout = QHBoxLayout()
        project_name_label = QLabel("Nom du projet :")
        project_name_label.setStyleSheet("""
            color: #1976F2; 
            font-weight: bold;
            font-size: 12px;
            background: transparent;
        """)
        input_layout.addWidget(project_name_label)
        
        self.project_name_input = QLineEdit()
        self.project_name_input.setPlaceholderText("Entrez le nom de votre projet")
        self.project_name_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #BBDEFB;
                border-radius: 4px;
                padding: 2px 8px;
                background-color: rgba(255, 255, 255, 0.9);
                color: #0D47A1;
                font-size: 12px;
                selection-background-color: #2196F3;
                selection-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #2196F3;
                background-color: white;
            }
        """)
        self.project_name_input.setFixedHeight(24)
        input_layout.addWidget(self.project_name_input, 1)  # 1 = stretch factor
        
        # Bouton de validation
        confirm_btn = QPushButton("Valider")
        confirm_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2196F3, stop:1 #1976D2);
                color: white;
                border: none;
                border-radius: 4px;
                padding: 3px 15px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #42A5F5, stop:1 #1E88E5);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1976D2, stop:1 #1565C0);
            }
        """)
        confirm_btn.setFixedHeight(24)
        confirm_btn.setCursor(Qt.PointingHandCursor)  # Changer le curseur au survol
        confirm_btn.clicked.connect(self.on_project_name_submitted)
        input_layout.addWidget(confirm_btn)
        
        bubble_layout.addLayout(input_layout)
        wrapper_layout.addWidget(bubble)
        
        # Ajouter la bulle au layout principal
        self.layout.addWidget(bubble_container)
        
        # Connecter la touche Entrée pour soumettre le nom du projet
        self.project_name_input.returnPressed.connect(self.on_project_name_submitted)
        
        return bubble_container
    
    def on_project_name_submitted(self):
        """Gère la soumission du nom du projet"""
        project_name = self.project_name_input.text().strip()
        if project_name:
            # Émettre le signal avec le nom du projet
            self.projectNameSubmitted.emit(project_name)
