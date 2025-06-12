#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Exemple d'utilisation du composant ActionBubble
"""

import sys
import os

# Ajouter le répertoire racine du projet au chemin de recherche Python
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from project.structure.ui.widgets.chat_panel import ChatPanel
from project.structure.ui.widgets.action_bubble import ActionBubble

class ExempleActionBubble(QMainWindow):
    """Fenêtre d'exemple pour démontrer l'utilisation du composant ActionBubble"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Exemple ActionBubble")
        self.resize(600, 800)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        
        # Créer le panneau de chat
        self.chat_panel = ChatPanel()
        main_layout.addWidget(self.chat_panel)
        
        # Ajouter quelques messages pour l'exemple
        self.chat_panel.add_ai_message("Bienvenue dans l'exemple d'ActionBubble !")
        
        # Ajouter une bulle d'action pour confirmer une action
        action_bubble1 = self.chat_panel.add_action_message(
            "Voulez-vous créer un nouveau projet ?",
            buttons=[
                {"text": "Oui, créer", "color": "#4CAF50"},  # Vert
                {"text": "Non, annuler", "color": "#F44336"}   # Rouge
            ],
            icon_name="folder",
            icon_color="#2196F3",
        )
        
        # Connecter le signal du bouton avec l'index
        action_bubble1.button_clicked.connect(self.on_project_button_clicked)
        
        # Ajouter une autre bulle d'action avec des couleurs différentes
        action_bubble2 = self.chat_panel.add_action_message(
            "Souhaitez-vous configurer les paramètres avancés ?",
            buttons=[
                {"text": "Configurer", "color": "#FF9800"},  # Orange
                {"text": "Plus tard", "color": "#9E9E9E"},   # Gris
                {"text": "Jamais", "color": "#607D8B"}      # Bleu-gris
            ],
            icon_name="settings",
            icon_color="#673AB7",
        )
        
        # Connecter le signal du bouton avec l'index
        action_bubble2.button_clicked.connect(self.on_settings_button_clicked)
    
    def on_project_button_clicked(self, index):
        """Réaction au clic sur un bouton de la bulle de projet
        
        Args:
            index (int): Index du bouton cliqué (0 pour 'Oui, créer', 1 pour 'Non, annuler')
        """
        if index == 0:  # Bouton 'Oui, créer'
            self.chat_panel.add_ai_message("Création du projet en cours...")
        elif index == 1:  # Bouton 'Non, annuler'
            self.chat_panel.add_ai_message("Création du projet annulée.")
    
    def on_settings_button_clicked(self, index):
        """Réaction au clic sur un bouton de la bulle de paramètres
        
        Args:
            index (int): Index du bouton cliqué (0 pour 'Configurer', 1 pour 'Plus tard', 2 pour 'Jamais')
        """
        if index == 0:  # Bouton 'Configurer'
            self.chat_panel.add_ai_message("Ouverture des paramètres avancés...")
        elif index == 1:  # Bouton 'Plus tard'
            self.chat_panel.add_ai_message("Configuration reportée à plus tard.")
        elif index == 2:  # Bouton 'Jamais'
            self.chat_panel.add_ai_message("Les paramètres avancés ne seront pas configurés.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExempleActionBubble()
    window.show()
    sys.exit(app.exec())
