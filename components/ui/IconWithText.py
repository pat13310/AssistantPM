import os
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont
from PySide6.QtSvgWidgets import QSvgWidget

from ui.ui_utils import load_colored_svg

class IconWithText(QWidget):
    """
    Composant réutilisable pour afficher une icône SVG et un texte de la même couleur.
    """
    
    def __init__(self, text, icon_name, color="#03b541", font_size=14, icon_size=24, y_text=0,parent=None):
        """
        Initialise un composant avec une icône et un texte de la même couleur.
        
        Args:
            text (str): Le texte à afficher
            icon_name (str): Le nom du fichier SVG dans assets/icons (sans l'extension .svg)
            color (str): La couleur en hexadécimal (par défaut: vert)
            font_size (int): Taille de la police en points
            icon_size (int): Taille de l'icône en pixels
            parent (QWidget): Widget parent
        """
        super().__init__(parent)
        
        # Layout principal horizontal
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)  # Espacement entre l'icône et le texte
        
        # Chemin vers le fichier SVG
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                                "assets", "icons", f"{icon_name}.svg")
        
        # Créer un widget SVG coloré
        try:
            svg_data = load_colored_svg(icon_path, color)
            icon_widget = QSvgWidget()
            icon_widget.load(svg_data)
            icon_widget.setFixedSize(QSize(icon_size, icon_size))
            icon_widget.setStyleSheet("background: transparent; border:none; margin-top:0px")
            layout.addWidget(icon_widget)
        except Exception as e:
            print(f"Erreur lors du chargement de l'icône SVG {icon_name}: {e}")
            # Fallback en cas d'erreur - utiliser un label vide
            placeholder = QWidget()
            placeholder.setFixedSize(QSize(icon_size, icon_size))
            layout.addWidget(placeholder)
        
        # Ajout du texte
        self.text_label = QLabel(text)
        self.text_label.setFont(QFont("Segoe UI", font_size, QFont.Bold))
        self.text_label.setStyleSheet(f"color: {color}; border:none; margin-top:{y_text}px")
        layout.addWidget(self.text_label)
        
        # Ajouter un espace extensible à la fin pour aligner à gauche
        layout.addStretch()
    
    def set_text(self, text):
        """
        Modifie le texte.
        
        Args:
            text (str): Le nouveau texte
        """
        self.text_label.setText(text)
        
    def set_color(self, color):
        """
        Modifie la couleur du texte et de l'icône.
        
        Args:
            color (str): La nouvelle couleur en hexadécimal
        """
        self.text_label.setStyleSheet(f"color: {color}; border:none;margin-top:0px")
        
        # Recharger l'icône avec la nouvelle couleur
        icon_name = self.icon_name  # On suppose que l'icône est stockée comme attribut
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                                "assets", "icons", f"{icon_name}.svg")
        
        try:
            svg_data = load_colored_svg(icon_path, color)
            self.icon_widget.load(svg_data)
            self.icon_widget.setStyleSheet(f"color: {color}; border:none;margin-top:0px")
        except Exception as e:
            print(f"Erreur lors du rechargement de l'icône SVG avec la nouvelle couleur: {e}")
