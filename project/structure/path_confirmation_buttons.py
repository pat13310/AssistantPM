from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
)
from PySide6.QtCore import Qt, Signal, QTimer
from project.structure.chat_bubble import ChatBubble

class PathConfirmationButtons(ChatBubble):
    """Classe pour gérer les boutons de confirmation de chemin"""
    
    # Signaux
    pathConfirmed = Signal()
    pathRejected = Signal()
    
    def __init__(self, message_text, parent=None):
        """Initialise la bulle de confirmation de chemin avec boutons intégrés
        
        Args:
            message_text (str): Le texte à afficher dans la bulle
            parent (QWidget, optional): Widget parent. Defaults to None.
        """
        # Initialiser la bulle de chat avec le message et une icône
        super().__init__(message_text, is_user=False, word_wrap=True, 
                         icon_name="folder", icon_color="#FFFFFF", icon_size=20)
        
        # Pas d'espacement entre le texte et les boutons pour éviter la ligne horizontale
        
    def add_confirmation_buttons(self):
        """Ajoute des boutons pour confirmer ou modifier le chemin du projet directement dans la bulle"""
        # Créer un layout horizontal pour les boutons
        buttons_layout = QHBoxLayout()
        
        # Bouton Oui
        btn_yes = QPushButton("Oui, ce chemin me convient")
        btn_yes.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2196F3, stop:1 #1976D2);
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 10px;
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
        btn_yes.setFixedHeight(26)
        btn_yes.setCursor(Qt.PointingHandCursor)
        btn_yes.clicked.connect(self.on_path_confirmed)
        buttons_layout.addWidget(btn_yes)
        
        # Bouton Non
        btn_no = QPushButton("Non, je veux modifier le chemin")
        btn_no.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2196F3, stop:1 #1976D2);
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 10px;
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
        btn_no.setFixedHeight(26)
        btn_no.setCursor(Qt.PointingHandCursor)
        btn_no.clicked.connect(self.on_path_rejected)
        buttons_layout.addWidget(btn_no)
        
        # Ajouter le layout des boutons au layout principal de la bulle
        self.main_layout.addLayout(buttons_layout)
        
        # Retourner la bulle elle-même
        return self
    
    def on_path_confirmed(self):
        """Émet le signal de confirmation du chemin"""
        self.pathConfirmed.emit()
    
    def on_path_rejected(self):
        """Émet le signal de rejet du chemin"""
        self.pathRejected.emit()
