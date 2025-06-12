#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module pour le composant ActionBubble - Bulle de message avec deux boutons d'action
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize, QObject
from PySide6.QtGui import QIcon

class ActionBubble(QWidget):
    """
    Widget de bulle de message avec des boutons d'action paramétrables
    """
    
    # Signal émis lorsqu'un bouton est cliqué, avec l'index du bouton
    button_clicked = Signal(int)
    
    def __init__(
        self,
        message,
        buttons=None,  # Liste de dictionnaires avec 'text' et 'color'
        icon_name="user",
        icon_color="#2196F3",
        icon_size=20,
        parent=None
    ):
        """
        Initialise une bulle de message avec deux boutons d'action
        
        Args:
            message (str): Message à afficher
            button1_text (str): Texte du premier bouton
            button2_text (str): Texte du second bouton
            button1_color (str): Couleur du premier bouton (format CSS)
            button2_color (str): Couleur du second bouton (format CSS)
            icon_name (str): Nom de l'icône SVG à utiliser
            icon_color (str): Couleur de l'icône (format CSS)
            icon_size (int): Taille de l'icône en pixels
            parent (QWidget): Widget parent
        """
        super().__init__(parent)
        
        # Layout principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 10)
        
        # Aligner la bulle à gauche avec un layout horizontal
        h_layout = QHBoxLayout()
        h_layout.setContentsMargins(0, 0, 0, 0)
        
        # Créer un widget pour contenir la bulle
        self.bubble = QFrame()
        self.bubble.setObjectName("ai_bubble")
        self.bubble.setStyleSheet(
            f"""
            QFrame#ai_bubble {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #E3F2FD, stop:1 #BBDEFB);
                border-radius: 15px;
                border-bottom-left-radius: 0px;
                padding: 10px;
            }}
            """
        )
        
        # Layout pour la bulle
        bubble_layout = QVBoxLayout(self.bubble)
        bubble_layout.setContentsMargins(10, 8, 10, 8)
        
        # Layout pour l'icône et le message
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Icône SVG vectorielle
        try:
            from project.structure.ui.ui_utils import load_colored_svg
        except ImportError:
            # Fallback si le module n'est pas trouvable via l'importation relative
            import sys
            import os
            sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))
            from project.structure.ui.ui_utils import load_colored_svg
            
        from PySide6.QtSvgWidgets import QSvgWidget
        import os
        
        # Chemin vers la racine du projet
        project_root = os.path.dirname(
            os.path.dirname(
                os.path.dirname(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                )
            )
        )
        icon_path = os.path.join(
            project_root,
            "assets",
            "icons",
            f"{icon_name}.svg",
        )
        
        if os.path.exists(icon_path):
            try:
                # Créer un widget SVG
                svg_widget = QSvgWidget()
                
                # Charger le SVG avec la couleur spécifiée
                svg_data = load_colored_svg(icon_path, icon_color)
                if not svg_data.isEmpty():
                    # Charger les données SVG dans le widget
                    svg_widget.load(svg_data)
                    
                    # Définir la taille fixe
                    svg_widget.setFixedSize(QSize(icon_size, icon_size))
                    content_layout.addWidget(svg_widget)
                else:
                    # Fallback si le SVG ne peut pas être chargé
                    icon_label = QLabel()
                    icon_label.setFixedSize(icon_size, icon_size)
                    content_layout.addWidget(icon_label)
            except Exception as e:
                print(f"[Erreur] Impossible de charger l'icône {icon_name}: {str(e)}")
                icon_label = QLabel()
                icon_label.setFixedSize(icon_size, icon_size)
                content_layout.addWidget(icon_label)
        else:
            # Fallback si l'icône n'est pas trouvée
            icon_label = QLabel()
            icon_label.setFixedSize(icon_size, icon_size)
            content_layout.addWidget(icon_label)
            
        # Texte
        self.label = QLabel(message)
        self.label.setStyleSheet(
            """
            color: #0D47A1; 
            font-size: 12px;
            background: transparent;
            margin-left: 10px;
            """
        )
        self.label.setWordWrap(True)
        self.label.setMinimumWidth(300)
        self.label.setMaximumWidth(400)  # Limiter la largeur pour éviter les lignes trop longues
        
        content_layout.addWidget(self.label)
        bubble_layout.addLayout(content_layout)
        
        # Layout pour les boutons
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 10, 0, 0)
        
        # Valeurs par défaut pour les boutons si non spécifiés
        if buttons is None:
            buttons = [
                {"text": "Accepter", "color": "#4CAF50"},  # Vert
                {"text": "Refuser", "color": "#F44336"}   # Rouge
            ]
        
        # Créer les boutons à partir du tableau
        self.buttons = []
        for i, btn_info in enumerate(buttons):
            button = QPushButton(btn_info.get("text", f"Bouton {i+1}"))
            color = btn_info.get("color", "#2196F3")
            
            button.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {color};
                    border: none;
                    border-radius: 5px;
                    color: white;
                    padding: 5px 10px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {self._darken_color(color)};
                }}
                QPushButton:pressed {{
                    background-color: {self._darken_color(color, factor=0.2)};
                }}
                """
            )
            
            # Utiliser une fonction lambda avec une variable locale pour éviter les problèmes de closure
            button.clicked.connect(lambda checked, idx=i: self.button_clicked.emit(idx))
            
            # Ajouter le bouton au layout et à la liste
            buttons_layout.addWidget(button)
            self.buttons.append(button)
        
        buttons_layout.addStretch(1)  # Espace à droite des boutons
        
        bubble_layout.addLayout(buttons_layout)
        
        h_layout.addWidget(self.bubble)
        h_layout.addStretch(1)  # Cela pousse la bulle vers la gauche
        
        self.main_layout.addLayout(h_layout)
    
    def _darken_color(self, color, factor=0.1):
        """
        Assombrit une couleur hexadécimale
        
        Args:
            color (str): Couleur au format hexadécimal (#RRGGBB)
            factor (float): Facteur d'assombrissement (0-1)
            
        Returns:
            str: Couleur assombrie au format hexadécimal
        """
        if not color.startswith('#') or len(color) != 7:
            return color
            
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        
        r = max(0, int(r * (1 - factor)))
        g = max(0, int(g * (1 - factor)))
        b = max(0, int(b * (1 - factor)))
        
        return f"#{r:02x}{g:02x}{b:02x}"
