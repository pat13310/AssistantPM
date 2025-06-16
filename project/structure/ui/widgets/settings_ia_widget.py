#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module pour le composant SettingsIAWidget - Widget de configuration des paramètres d'IA
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QLineEdit,
    QSizePolicy,
    QStackedWidget
)
from PySide6.QtGui import QIcon
from project.structure.top_bar_widget import get_svg_icon
from PySide6.QtCore import Qt, Signal, QSize, QObject, QSettings
from PySide6.QtGui import QIcon, QPixmap
import os
import json

class SettingsIAWidget(QWidget):
    """
    Widget pour configurer les paramètres d'IA (type, modèle et clé API)
    """
    
    # Signaux
    ia_type_selected = Signal(str)  # Signal émis quand un type d'IA est sélectionné
    ia_model_selected = Signal(str)  # Signal émis quand un modèle d'IA est sélectionné
    api_key_saved = Signal(str)  # Signal émis quand une clé API est sauvegardée
    
    def __init__(self, parent=None):
        """
        Initialise le widget de configuration d'IA
        
        Args:
            parent (QWidget): Widget parent
        """
        super().__init__(parent)
        
        # Charger les types d'IA depuis le fichier JSON
        json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "ia_types.json")
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                self.ia_types = json.load(f)
        except Exception as e:
            print(f"Erreur lors du chargement des types d'IA: {e}")
            # Valeurs par défaut en cas d'erreur
            self.ia_types = [
                {"id": "openai", "name": "OpenAI", "description": "API OpenAI (ChatGPT, GPT-4, etc.)", "icon": "brain"},
                {"id": "anthropic", "name": "Anthropic", "description": "API Anthropic (Claude)", "icon": "bot"},
                {"id": "google", "name": "Google", "description": "API Google (Gemini)", "icon": "globe"},
                {"id": "deepseek", "name": "Deepseek", "description": "API Deepseek (Deepseek-Chat)", "icon": "search"},
                {"id": "local", "name": "Local", "description": "Modèles locaux (Ollama, LM Studio)", "icon": "home"}
            ]
        
        # Définir les modèles disponibles par type d'IA
        self.ia_models = {
            "openai": [
                {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "Rapide et économique"},
                {"id": "gpt-4", "name": "GPT-4", "description": "Puissant et précis"},
                {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "description": "Version améliorée de GPT-4"},
                {"id": "gpt-4o", "name": "GPT-4o", "description": "Dernière version de GPT-4"}
            ],
            "anthropic": [
                {"id": "claude-3-opus", "name": "Claude 3 Opus", "description": "Modèle le plus puissant"},
                {"id": "claude-3-sonnet", "name": "Claude 3 Sonnet", "description": "Bon équilibre performance/coût"},
                {"id": "claude-3-haiku", "name": "Claude 3 Haiku", "description": "Rapide et économique"}
            ],
            "google": [
                {"id": "gemini-pro", "name": "Gemini Pro", "description": "Modèle standard"},
                {"id": "gemini-ultra", "name": "Gemini Ultra", "description": "Modèle le plus avancé"}
            ],
            "deepseek": [
                {"id": "deepseek-chat", "name": "Deepseek Chat", "description": "Modèle conversationnel standard"},
                {"id": "deepseek-coder", "name": "Deepseek Coder", "description": "Spécialisé pour le code"},
                {"id": "deepseek-llm", "name": "Deepseek LLM", "description": "Modèle de langage avancé"}
            ],
            "local": [
                {"id": "ollama", "name": "Ollama", "description": "Interface pour modèles locaux"},
                {"id": "lmstudio", "name": "LM Studio", "description": "Interface graphique pour modèles locaux"}
            ]
        }
        
        # Variables pour stocker les sélections
        self.selected_ia_type = None
        self.selected_ia_model = None
        self.api_key = None
        
        # Créer l'interface utilisateur
        self._setup_ui()
    
    # Méthode pour gérer la sélection d'un type d'IA
    def _on_ia_type_selected(self, item):
        """Gère la sélection d'un type d'IA dans la liste"""
        # Récupérer l'ID du type d'IA sélectionné
        ia_type_id = item.data(Qt.UserRole)
        self.selected_ia_type = ia_type_id
        
        # Afficher les modèles pour ce type d'IA
        self._show_models_for_type(ia_type_id)
        
        # Charger la clé API sauvegardée pour ce type d'IA
        self._load_saved_api_key(ia_type_id)
    
    def _setup_ui(self):
        # Créer un widget pour contenir toute la bulle avec la flèche
        self.container = QWidget()
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        
        # Créer la barre de titre avec icône
        title_bar = QWidget()
        title_bar.setFixedHeight(40)
        title_bar.setStyleSheet(
            """
            background: transparent;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            """
        )
        
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(0, 0, 10, 0)
        title_layout.setAlignment(Qt.AlignLeft)
        
        # Icône
        icon_label = QLabel()
        # Utiliser la fonction get_svg_icon pour charger l'icône de manière sécurisée
        from project.structure.top_bar_widget import get_svg_icon
        icon_pixmap = get_svg_icon("settings", size=24, color="#FFFFFF")
        icon_label.setPixmap(icon_pixmap)
        title_layout.addWidget(icon_label)
        
        # Texte du titre
        title_text = QLabel("Configuration des paramètres d'IA")
        title_text.setStyleSheet("font-weight: bold; color: #FFFFFF; font-size: 14px;")
        title_layout.addWidget(title_text)
        
        # Layout principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Créer un widget pour contenir la bulle
        self.bubble = QFrame()
        self.bubble.setObjectName("settings_bubble")
        self.bubble.setStyleSheet(
            """
            QFrame#settings_bubble {
                background: #2D2D2D;
                border-radius: 8px;
                padding-left: 16px;
            }
            """
        )
        
        # Layout pour la bulle
        bubble_layout = QVBoxLayout(self.bubble)
        bubble_layout.setContentsMargins(0, 0, 10, 8)
        
        # Ajouter la barre de titre à la bulle
        bubble_layout.addWidget(title_bar)
        
        # Layout horizontal pour la liste à gauche et les détails à droite
        content_layout = QHBoxLayout()
        
        # Liste des types d'IA à gauche
        self.ia_list = QListWidget()
        self.ia_list.setMaximumWidth(150)
        self.ia_list.setStyleSheet(
            """
            QListWidget {
                background-color: rgba(30, 30, 30, 150);
                border-radius: 5px;
                border: 1px solid #4CAF50;
                color: white;
            }
            QListWidget::item {
                padding: 5px;
                border: none;
                color: white;
            }
            QListWidget::item:hover {
                background-color: rgba(76, 175, 80, 0.3);
            }
            QListWidget::item:selected {
                background-color: #4ef4a4;
                color: #044928;
            }
            """
        )
        
        # Remplir la liste des types d'IA
        for ia_type in self.ia_types:
            item = QListWidgetItem(ia_type["name"])
            item.setData(Qt.UserRole, ia_type["id"])
            item.setToolTip(ia_type["description"])
            self.ia_list.addItem(item)
        
        # Connecter le signal de sélection
        self.ia_list.itemClicked.connect(self._on_ia_type_selected)
        
        content_layout.addWidget(self.ia_list)
        
        # Panneau de détails à droite (utiliser QStackedWidget pour changer de contenu)
        self.details_stack = QStackedWidget()
        
        # Page d'accueil (instructions)
        welcome_page = QWidget()
        welcome_layout = QVBoxLayout(welcome_page)
        welcome_label = QLabel("Sélectionnez un type d'IA dans la liste à gauche pour configurer ses paramètres.")
        welcome_label.setWordWrap(True)
        welcome_label.setStyleSheet("color: #e0e0e0;")
        welcome_layout.addWidget(welcome_label)
        welcome_layout.addStretch(1)
        
        self.details_stack.addWidget(welcome_page)
        
        # Ajouter le QStackedWidget au layout
        content_layout.addWidget(self.details_stack, 1)  # Stretch factor 1
        
        bubble_layout.addLayout(content_layout)
        
        # Ajouter la bulle au layout principal
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.bubble)
        h_layout.addStretch(1)  # Cela pousse la bulle vers la gauche
        
        self.main_layout.addLayout(h_layout)
        
    def _on_ia_type_selected(self, item):
        """Gère la sélection d'un type d'IA"""
        ia_type_id = item.data(Qt.UserRole)
        self.selected_ia_type = ia_type_id
        
        # Émettre le signal
        self.ia_type_selected.emit(ia_type_id)
        
        # Afficher les modèles correspondants
        self._show_models_for_type(ia_type_id)
        
        # Charger la clé API sauvegardée pour ce type d'IA
        self._load_saved_api_key(ia_type_id)
        
    def _load_saved_api_key(self, ia_type_id):
        """Charge la clé API sauvegardée pour le type d'IA sélectionné"""
        settings = QSettings("AssistantPM", "IASettings")
        saved_key = settings.value(f"api_key/{ia_type_id}", "")
        
        if saved_key:
            # Afficher un placeholder indiquant qu'une clé existe
            self.api_key_input.setPlaceholderText("Clé API déjà enregistrée (cliquez sur Enregistrer pour modifier)")
            # Pré-remplir le champ avec la clé sauvegardée
            self.api_key_input.setText(saved_key)
        else:
            # Réinitialiser le placeholder
            self.api_key_input.setPlaceholderText("Entrez votre clé API ici")
            self.api_key_input.clear()
    
    def _show_models_for_type(self, ia_type_id):
        """Affiche les modèles disponibles pour le type d'IA sélectionné"""
        # Créer un nouveau widget pour cette page
        models_page = QWidget()
        models_layout = QVBoxLayout(models_page)
        
        # Titre
        title = next((t["name"] for t in self.ia_types if t["id"] == ia_type_id), "Modèles")
        models_title = QLabel(f"<b>Modèles {title}</b>")
        models_title.setStyleSheet("font-size: 13px; color: #4CAF50; margin-bottom: 8px;")
        models_layout.addWidget(models_title)
        
        # Liste des modèles
        models_list = QListWidget()
        models_list.setMinimumWidth(250)
        models_list.setStyleSheet(
            """
            QListWidget {
                background-color: rgba(30, 30, 30, 150);
                border-radius: 5px;
                border: 1px solid #4CAF50;
                color: white;
            }
            QListWidget::item {
                padding: 5px;
                border: none;
                color: white;
            }
            QListWidget::item:hover {
                background-color: rgba(76, 175, 80, 0.3);
            }
            QListWidget::item:selected {
                background-color: #4ef4a4;
                color: #044928;
            }
            """
        )
        
        # Remplir la liste des modèles
        if ia_type_id in self.ia_models:
            for model in self.ia_models[ia_type_id]:
                item = QListWidgetItem(model["name"])
                item.setData(Qt.UserRole, model["id"])
                item.setToolTip(model["description"])
                models_list.addItem(item)
        
        # Connecter le signal de sélection
        models_list.itemClicked.connect(self._on_ia_model_selected)
        
        models_layout.addWidget(models_list)
        
        # Champ pour la clé API
        api_frame = QFrame()
        api_frame.setStyleSheet("background-color: rgba(30, 30, 30, 150); border-radius: 5px; padding: 5px; border: 1px solid #4CAF50;")
        api_layout = QVBoxLayout(api_frame)
        
        api_title = QLabel("<b>Clé API</b>")
        api_title.setStyleSheet("color: #4CAF50;border:none;background-color: transparent;")
        api_layout.addWidget(api_title)
        
        api_input_layout = QHBoxLayout()
        self.api_key_input = QLineEdit()
        self.api_key_input.setMinimumWidth(650)
        self.api_key_input.setPlaceholderText("Entrez votre clé API ici")
        self.api_key_input.setToolTip("Entrez la clé API fournie par le service sélectionné (OpenAI, Anthropic, Google, etc.)\nCette clé sera sauvegardée localement et utilisée pour les requêtes API.")

        self.api_key_input.setEchoMode(QLineEdit.Password)  # Masquer la clé
        
        # Bouton pour afficher/masquer la clé
        self.toggle_visibility_button = QPushButton()
        self.toggle_visibility_button.setFixedSize(30, 30)
        self.toggle_visibility_button.setIcon(QIcon(get_svg_icon("eye", color="#4CAF50")))
        self.toggle_visibility_button.setStyleSheet(
            """
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 3px;
            }
            QPushButton:hover {
                background-color: rgba(76, 175, 80, 0.2);
                border-radius: 3px;
            }
            QPushButton:pressed {
                background-color: rgba(76, 175, 80, 0.3);
            }
            """
        )
        self.toggle_visibility_button.clicked.connect(self._toggle_password_visibility)
        self.api_key_input.setStyleSheet(
            """
            QLineEdit {
                background-color: #263238;
                color: #4CAF50;
                border: 1px solid #4CAF50;
                border-radius: 3px;
                padding: 5px;
                font-size: 9px;
            }
            QLineEdit:focus {
                border: 1px solid #82f2a9;
            }
            """
        )
        
        save_button = QPushButton("Enregistrer")
        save_button.setStyleSheet(
            """
            QPushButton {
                background-color: #43824a;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #43624a;
            }
            """
        )
        save_button.clicked.connect(self._on_save_api_key)
        
        api_input_layout.addWidget(self.api_key_input)
        api_input_layout.addWidget(self.toggle_visibility_button)
        api_input_layout.addWidget(save_button)
        
        api_layout.addLayout(api_input_layout)
        models_layout.addWidget(api_frame)
        
        # Ajouter un espace extensible en bas
        models_layout.addStretch(1)
        
        # Ajouter la page au stack et l'afficher
        self.details_stack.addWidget(models_page)
        self.details_stack.setCurrentWidget(models_page)
    
    def _on_ia_model_selected(self, item):
        """Gère la sélection d'un modèle d'IA"""
        # Récupérer l'ID du modèle sélectionné
        model_id = item.data(Qt.UserRole)
        self.selected_ia_model = model_id
        
        # Émettre le signal
        self.ia_model_selected.emit(model_id)
    
    def _toggle_password_visibility(self):
        """Bascule entre l'affichage et le masquage de la clé API"""
        if self.api_key_input.echoMode() == QLineEdit.Password:
            self.api_key_input.setEchoMode(QLineEdit.Normal)
            self.toggle_visibility_button.setIcon(QIcon(get_svg_icon("eye-off", color="#4CAF50")))
        else:
            self.api_key_input.setEchoMode(QLineEdit.Password)
            self.toggle_visibility_button.setIcon(QIcon(get_svg_icon("eye", color="#4CAF50")))
    
    def _on_save_api_key(self):
        """Sauvegarde la clé API dans QSettings"""
        api_key = self.api_key_input.text()
        if api_key and self.selected_ia_type:
            # Sauvegarder la clé API dans QSettings
            settings = QSettings("AssistantPM", "IASettings")
            settings.setValue(f"api_key/{self.selected_ia_type}", api_key)
            settings.sync()
            
            # Émettre le signal
            self.api_key_saved.emit(api_key)
            print(f"Clé API sauvegardée pour {self.selected_ia_type}")
            
            # Mettre à jour le placeholder
            self.api_key_input.setPlaceholderText("Clé API enregistrée")
            self.api_key_input.clear()
