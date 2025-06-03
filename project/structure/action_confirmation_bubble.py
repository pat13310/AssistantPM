from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget
from PySide6.QtSvgWidgets import QSvgWidget
import os
import sys

# Import de la fonction utilitaire pour charger les SVG colorés
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ui.ui_utils import load_colored_svg

class ActionConfirmationBubble(QFrame):
    """Bulle interactive pour afficher une action proposée par l'IA avec des boutons de validation et de refus"""
    
    # Signaux émis lorsqu'un bouton est cliqué
    actionAccepted = Signal()
    actionRejected = Signal()
    
    def __init__(self, action_text, icon_name=None, icon_color="#FFFFFF", icon_size=20, parent=None):
        """Initialise une bulle de confirmation d'action
        
        Args:
            action_text (str): Le texte décrivant l'action proposée
            icon_name (str, optional): Nom de l'icône SVG à afficher. Defaults to None.
            icon_color (str, optional): Couleur de l'icône au format CSS. Defaults to "#FFFFFF".
            icon_size (int, optional): Taille de l'icône en pixels. Defaults to 20.
            parent (QWidget, optional): Widget parent. Defaults to None.
        """
        super().__init__(parent)
        
        # Style de la bulle (bleu pour l'IA)
        self.setStyleSheet("""
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                             stop:0 #2196F3, stop:1 #1976D2);
            border-radius: 10px;
            margin: 2px;
            padding: 8px;
            border: 1px solid #42A5F5;
            font-family: 'Roboto';
            font-size: 11px;
            color: white;
        """)
        
        # Layout principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        
        # Créer un layout horizontal pour l'icône et le texte
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(8)
        
        # Ajouter l'icône si spécifiée
        if icon_name:
            # Chemin vers le fichier SVG
            icon_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                "assets",
                "icons",
                f"{icon_name}.svg",
            )
            
            if os.path.exists(icon_path):
                # Charger le SVG avec la couleur spécifiée
                svg_content = load_colored_svg(icon_path, color_str=icon_color)
                
                # Créer un widget SVG
                icon_widget = QSvgWidget()
                icon_widget.load(svg_content)
                icon_widget.setFixedSize(icon_size, icon_size)
                icon_widget.setStyleSheet("background-color: transparent; border:none;")
                
                # Ajouter l'icône au layout
                content_layout.addWidget(icon_widget)
        
        # Texte de l'action
        action_label = QLabel(action_text)
        action_label.setWordWrap(True)
        action_label.setStyleSheet("""
            font-weight: bold;
            font-size: 12px;
            border: none;
            background: transparent;
        """)
        content_layout.addWidget(action_label, 1)  # 1 = stretch factor
        
        # Ajouter le layout de contenu au layout principal
        self.main_layout.addLayout(content_layout)
        
        # Layout pour les boutons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        # Bouton Valider
        self.accept_button = QPushButton("Valider les actions")
        self.accept_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4CAF50, stop:1 #388E3C);
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 15px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #66BB6A, stop:1 #43A047);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #388E3C, stop:1 #2E7D32);
            }
        """)
        self.accept_button.setCursor(Qt.PointingHandCursor)
        self.accept_button.clicked.connect(self.on_accept)
        buttons_layout.addWidget(self.accept_button)
        
        # Bouton Refuser
        self.reject_button = QPushButton("Refuser")
        self.reject_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.5);
                border-radius: 4px;
                padding: 6px 15px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.1);
            }
            QPushButton:pressed {
                background: rgba(255, 255, 255, 0.2);
            }
        """)
        self.reject_button.setCursor(Qt.PointingHandCursor)
        self.reject_button.clicked.connect(self.on_reject)
        buttons_layout.addWidget(self.reject_button)
        
        # Ajouter le layout des boutons au layout principal
        self.main_layout.addLayout(buttons_layout)
    
    def on_accept(self):
        """Émet le signal d'acceptation de l'action"""
        self.actionAccepted.emit()
    
    def on_reject(self):
        """Émet le signal de rejet de l'action"""
        self.actionRejected.emit()
