from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtSvgWidgets import QSvgWidget
import os
import sys

# Ajouter le répertoire parent au chemin d'importation pour accéder à ui_utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ui.ui_utils import load_colored_svg

def get_svg_path(icon_name):
    """
    Fonction utilitaire pour obtenir le chemin complet vers un fichier SVG
    
    Args:
        icon_name (str): Nom du fichier SVG sans extension
        
    Returns:
        str: Chemin complet vers le fichier SVG ou None si le fichier n'existe pas
    """
    icon_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "assets",
        "icons",
        f"{icon_name}.svg",
    )
    
    if not os.path.exists(icon_path):
        print(f"[Erreur] Fichier SVG introuvable : {icon_path}")
        return None
    
    return icon_path

class ChatBubble(QFrame):
    def __init__(self, text, is_user=False, word_wrap=True, icon_name=None, icon_color=None, icon_size=24):
        super().__init__()
        # Couleurs avec dégradés pour un effet plus moderne adaptées au fond sombre
        if is_user:
            # Dégradé de vert plus vif pour les messages utilisateur
            self.setStyleSheet(
                "background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, "
                "stop:0 #4CAF50, stop:1 #388E3C); "
                "border-radius: 10px; "
                "margin: 2px; "
                "padding: 4px; "
                "border: 1px solid #66BB6A;"
                "font-family: 'Roboto';"
                "font-size: 11px;"
                "color: white;"
            )
        else:
            # Dégradé de bleu plus vif pour les messages IA
            self.setStyleSheet(
                "background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, "
                "stop:0 #2196F3, stop:1 #1976D2); "
                "border-radius: 10px; "
                "margin: 2px; "
                "padding: 4px; "
                "border: 1px solid #42A5F5;"
                "font-family: 'Roboto';"
                "font-size: 11px;"
                "color: white;"
            )

        # Layout principal plus compact
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(8, 8, 8, 8)
        self.main_layout.setSpacing(2)  # Espacement réduit entre les éléments
        
        # Contenu du message
        self.label = QLabel(text)  # Stocker une référence au label
        self.label.setWordWrap(word_wrap)
        font = QFont()
        font.setPointSize(11)
        self.label.setFont(font)
        self.label.setStyleSheet("border: none; background: transparent;")
        self.label.setTextFormat(Qt.RichText)  # Pour supporter le HTML dans les messages
        
        # Si une icône est spécifiée, l'ajouter à côté du texte (si une seule ligne) ou en haut (si plusieurs lignes)
        if icon_name:
            # Obtenir le chemin de l'icône SVG
            icon_path = get_svg_path(icon_name)
            
            if icon_path:
                # Charger le SVG avec la couleur spécifiée
                svg_content = load_colored_svg(icon_path, color_str=icon_color)
                
                # Créer un widget SVG
                icon_widget = QSvgWidget()
                icon_widget.load(svg_content)
                icon_widget.setFixedSize(icon_size, icon_size)
                icon_widget.setStyleSheet("background-color: transparent; border:none;")
                
                # Toujours mettre l'icône à gauche du texte, indépendamment de la longueur du texte
                # Créer un layout horizontal pour l'icône et le texte
                content_layout = QHBoxLayout()
                content_layout.setContentsMargins(0, 0, 0, 0)
                content_layout.setSpacing(5)
                content_layout.setAlignment(Qt.AlignVCenter)
                
                # Ajouter l'icône
                content_layout.addWidget(icon_widget, 0, Qt.AlignVCenter)
                
                # Ajouter le texte
                content_layout.addWidget(self.label, 1)  # 1 = stretch factor pour que le texte prenne l'espace disponible
                
                # Ajouter le layout au layout principal
                self.main_layout.addLayout(content_layout)
            else:
                # Pas d'icône trouvée, ajouter simplement le texte
                self.main_layout.addWidget(self.label)
        else:
            # Pas d'icône demandée, ajouter simplement le texte
            self.main_layout.addWidget(self.label)
        # Note: La configuration du label est déjà faite plus haut
        
        # Définir une largeur minimale pour les bulles de l'IA
        if not is_user:
            self.setMinimumWidth(300)  # Largeur minimale pour les bulles de l'IA
            self.setMaximumWidth(500)  # Largeur maximale pour éviter que les bulles ne soient trop larges
