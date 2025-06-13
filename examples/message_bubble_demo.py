#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Exemple de démonstration des animations de MessageBubble
"""

import os
import sys

# Ajouter le chemin racine du projet pour résoudre les importations
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton
from PySide6.QtCore import QTimer

from project.structure.ui.widgets.message_bubble import MessageBubble


class MessageBubbleDemoWindow(QMainWindow):
    """Fenêtre de démonstration des animations de MessageBubble"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Démonstration des bulles de message")
        self.setGeometry(100, 100, 600, 500)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        
        # Zone de chat
        self.chat_layout = QVBoxLayout()
        chat_widget = QWidget()
        chat_widget.setLayout(self.chat_layout)
        main_layout.addWidget(chat_widget, 1)
        
        # Zone de boutons
        buttons_layout = QHBoxLayout()
        
        # Bouton pour ajouter un message IA
        add_ai_button = QPushButton("Ajouter message IA")
        add_ai_button.clicked.connect(self.add_ai_message)
        buttons_layout.addWidget(add_ai_button)
        
        # Bouton pour ajouter un message utilisateur
        add_user_button = QPushButton("Ajouter message utilisateur")
        add_user_button.clicked.connect(self.add_user_message)
        buttons_layout.addWidget(add_user_button)
        
        # Bouton pour l'animation de typing
        typing_button = QPushButton("Animation typing")
        typing_button.clicked.connect(self.show_typing_animation)
        buttons_layout.addWidget(typing_button)
        
        # Bouton pour mettre à jour le dernier message
        update_button = QPushButton("Mettre à jour message")
        update_button.clicked.connect(self.update_last_message)
        buttons_layout.addWidget(update_button)
        
        # Bouton pour ajouter un message temporaire
        temp_button = QPushButton("Message temporaire")
        temp_button.clicked.connect(self.add_temporary_message)
        buttons_layout.addWidget(temp_button)
        
        main_layout.addLayout(buttons_layout)
        
        # Liste pour stocker les références aux bulles de message
        self.messages = []
        
        # Compteur pour les messages
        self.message_counter = 0
        
    def add_ai_message(self):
        """Ajoute un message IA au chat"""
        self.message_counter += 1
        message = MessageBubble(
            message=f"Message IA #{self.message_counter}",
            user=False,
            parent=self
        )
        self.chat_layout.addWidget(message)
        self.messages.append(message)
        
    def add_user_message(self):
        """Ajoute un message utilisateur au chat"""
        self.message_counter += 1
        message = MessageBubble(
            message=f"Message utilisateur #{self.message_counter}",
            user=True,
            parent=self
        )
        self.chat_layout.addWidget(message)
        self.messages.append(message)
        
    def show_typing_animation(self):
        """Ajoute un message IA avec animation de typing"""
        message = MessageBubble(
            message="Message initial qui sera remplacé",
            user=False,
            parent=self
        )
        self.chat_layout.addWidget(message)
        self.messages.append(message)
        
        # Démarrer l'animation de typing
        message.typing_animation(duration=3000)
        
        # Après 3 secondes, mettre à jour avec le message final
        QTimer.singleShot(3000, lambda: message.update_message("Voici le message final après l'animation de typing!"))
        
    def update_last_message(self):
        """Met à jour le dernier message avec animation"""
        if self.messages:
            last_message = self.messages[-1]
            self.message_counter += 1
            last_message.update_message(f"Message mis à jour #{self.message_counter}")
            
    def add_temporary_message(self):
        """Ajoute un message temporaire qui disparaît automatiquement après 2 secondes"""
        self.message_counter += 1
        message = MessageBubble(
            message=f"Message temporaire #{self.message_counter} (disparaît dans 2s)",
            user=False,
            temporary=True,
            timeout=2000,  # 2000 ms = 2 secondes
            parent=self
        )
        self.chat_layout.addWidget(message)
        # Ne pas ajouter à self.messages car il va disparaître


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MessageBubbleDemoWindow()
    window.show()
    sys.exit(app.exec())
