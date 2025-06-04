#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import QPushButton

class BackButton(QPushButton):
    """
    Composant de bouton retour réutilisable avec un style prédéfini
    """
    
    def __init__(self, text="« Retour", parent=None):
        """
        Initialise le bouton retour avec un style prédéfini
        
        Args:
            text (str): Texte à afficher sur le bouton
            parent (QWidget): Widget parent
        """
        super().__init__(text, parent)
        
        # Appliquer le style
        self.setStyleSheet(
            """
            QPushButton {
                background-color: #444444;
                color: white;
                border: 1px solid #CCCCCC ;
                border-radius: 6px;
                padding: 8px 15px;
                font-weight: bold;
            
            }
            QPushButton:hover {
                background-color: #555555;
            }
            QPushButton:pressed {
                background-color: #333333;
            }
            """
        )
