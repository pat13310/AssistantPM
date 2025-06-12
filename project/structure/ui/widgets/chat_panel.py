"""
Composant de chat avec l'IA
Ce module définit un widget Qt pour gérer l'interface de chat avec l'IA
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QFrame,
    QPushButton,
    QGridLayout,
    QLabel,
    QPlainTextEdit,
    QSizePolicy,
)
from PySide6.QtCore import Qt, Signal, Slot, QTimer, QSize
from PySide6.QtGui import QIcon

from project.structure.ui.widgets.message_input import MessageInputField
from project.structure.chat_bubble import ChatBubble
from project.structure.top_bar_widget import TopBarWidget
from project.structure.ui.widgets.help_system import HelpDialog
from project.structure.ui.widgets.help_card import HelpCard
from project.structure.ui.widgets.project_types_grid import ProjectTypesGrid
from project.structure.ui.widgets.project_actions_grid import ProjectActionsGrid
from project.structure.ui.widgets.action_bubble import ActionBubble
import os


class ChatPanel(QWidget):
    """Widget de chat avec l'IA"""

    # Signaux
    message_sent = Signal(str)  # Signal émis quand un message est envoyé
    clear_requested = (
        Signal()
    )  # Signal émis quand l'utilisateur demande d'effacer la conversation
    project_type_selected = Signal(
        str
    )  # Signal émis quand un type de projet est sélectionné
    technology_selected = Signal(
        str, str
    )  # Signal émis lorsqu'une technologie est sélectionnée (tech_id, project_type_id)
    language_selected = Signal(
        str, str
    )  # Signal émis lorsqu'un langage est sélectionné (lang_id, tech_id)
    project_name_submitted = Signal(
        str
    )  # Signal émis lorsqu'un nom de projet est soumis
    chat_panel_clicked = Signal()  # Signal émis lorsque le panneau de chat est cliqué

    def __init__(self, parent=None):
        """Initialisation du panneau de chat"""
        super().__init__(parent)
        
        # Initialiser l'état de connexion au serveur
        self.server_connected = False
        
        # Layout principal vertical
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

        # Barre supérieure avec les contrôles (modèle, effacer, etc.)
        self.top_bar = TopBarWidget()
        self.main_layout.addWidget(self.top_bar)

        # Connecter les signaux de la barre supérieure
        self.top_bar.clearClicked.connect(self._on_clear_clicked)
        self.top_bar.modelChanged.connect(self._on_model_changed)
        self.top_bar.infoClicked.connect(self._show_help_dialog)

        # Séparateur horizontal
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #e0e0e0; margin: 5px 0;")
        self.main_layout.addWidget(separator)

        # Zone défilante pour les bulles de chat
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_widget)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.scroll.setWidget(self.chat_widget)
        self.main_layout.addWidget(self.scroll, 4)  # Proportion 4

        # Zone de saisie avec bouton d'envoi
        input_layout = QHBoxLayout()

        # Champ de saisie
        self.user_input = MessageInputField()
        self.user_input.setFixedHeight(40)
        self.user_input.setPlaceholderText("Votre message...")
        self.user_input.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.user_input.setLineWrapMode(MessageInputField.NoWrap)
        self.user_input.enterPressed.connect(self._on_send_message)

        # Style avec bordure verte lors du focus
        self.user_input.setStyleSheet(
            """
            QPlainTextEdit {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 8px;
                background-color: white;
            }
            QPlainTextEdit:focus {
                border: 1px solid #4CAF50;
            }
        """
        )

        # Bouton d'envoi avec l'icône SVG
        self.send_button = QPushButton()
        self.send_button.setFixedSize(40, 40)  # Bouton rond
        # Charger l'icône SVG
        from project.structure.top_bar_widget import get_svg_icon

        send_icon = get_svg_icon("send-horizontal", size=20, color="#FFFFFF")
        if send_icon:
            self.send_button.setIcon(QIcon(send_icon))
            self.send_button.setIconSize(QSize(20, 20))
        self.send_button.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                border: none;
                border-radius: 20px;
                color: white;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """
        )
        self.send_button.setToolTip("Envoyer")
        self.send_button.clicked.connect(self._on_send_message)

        # Ajouter les widgets à la disposition de saisie
        input_layout.addWidget(self.user_input, 7)  # Proportion 7
        input_layout.addWidget(self.send_button, 1)  # Proportion 1

        # Ajouter la disposition de saisie au layout principal
        self.main_layout.addLayout(input_layout)

        # Modèle sélectionné
        self.selected_model = ""

    @Slot()
    def _on_send_message(self, message_text):
        """Gère l'envoi d'un message utilisateur"""
        message_text = self.user_input.toPlainText().strip()
        if message_text:
            self.add_user_message(message_text)
            self.message_sent.emit(message_text)
            self.user_input.clear()

        self.on_message_sent(message_text)

    @Slot()
    def _on_clear_clicked(self):
        """Effacer la conversation"""
        # Effacer toutes les bulles de chat
        while self.chat_layout.count():
            child = self.chat_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Émettre le signal de demande d'effacement
        self.clear_requested.emit()

    @Slot(str)
    def _on_model_changed(self, model_name):
        """Réaction au changement de modèle"""
        self.selected_model = model_name

    def add_user_message(self, text):
        """Ajoute un message utilisateur à la conversation avec alignement à droite"""
        # Créer un conteneur pour placer la bulle complètement à droite
        container = QWidget()
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)  # Pas de marges
        container_layout.addStretch(
            1
        )  # Espace extensible à gauche pour pousser vers la droite

        # Créer la bulle utilisateur
        bubble = ChatBubble(text, True)  # True pour message utilisateur

        # Ajouter la bulle au conteneur avec alignement à droite
        container_layout.addWidget(bubble, 0, Qt.AlignRight)

        # Ajouter le conteneur au layout principal
        self.chat_layout.addWidget(container)
        QTimer.singleShot(100, self._scroll_to_bottom)

    def _get_svg_icon(self, icon_name, size=16, color=None):
        """Charge une icône SVG et la retourne comme QSvgWidget

        Args:
            icon_name (str): Nom du fichier SVG sans extension
            size (int): Taille de l'icône en pixels
            color (str): Couleur de l'icône (format CSS)

        Returns:
            QSvgWidget: Widget de l'icône SVG ou None si le fichier n'existe pas
        """
        import os
        from PySide6.QtSvgWidgets import QSvgWidget
        from PySide6.QtCore import QSize
        from ui.ui_utils import load_colored_svg

        # Chemin vers la racine du projet
        project_root = os.path.dirname(
            os.path.dirname(
                os.path.dirname(
                    os.path.dirname(
                        os.path.dirname(os.path.abspath(__file__))
                    )
                )
            )
        )
        icon_path = os.path.join(
            project_root,
            "assets",
            "icons",
            f"{icon_name}.svg",
        )

        if not os.path.exists(icon_path):
            print(f"[Erreur] Fichier SVG introuvable : {icon_path}")
            return None

        try:
            # Créer un widget SVG
            svg_widget = QSvgWidget()

            # Charger le SVG avec la couleur spécifiée si demandé
            svg_data = load_colored_svg(icon_path, color)
            if svg_data.isEmpty():
                print(f"[Erreur] SVG vide ou incorrect : {icon_path}")
                return None

            # Charger les données SVG dans le widget
            svg_widget.load(svg_data)

            # Définir la taille fixe
            svg_widget.setFixedSize(QSize(size, size))

            return svg_widget
        except Exception as e:
            print(f"[Erreur] Impossible de charger l'icône {icon_name}: {str(e)}")
            return None

    def add_ai_message(
        self,
        message,
        word_wrap=True,
        icon_name="user",
        icon_color="#2196F3",
        icon_size=20,
    ):
        """Ajoute un message IA simple dans le chat

        Args:
            message (str): Message à afficher
            word_wrap (bool, optional): Activer le retour à la ligne automatique. Par défaut True.
            icon_name (str, optional): Nom de l'icône. Par défaut "robot".
            icon_color (str, optional): Couleur de l'icône. Par défaut "#2196F3".
            icon_size (int, optional): Taille de l'icône. Par défaut 20.

        Returns:
            QWidget: Le widget de la bulle de chat créée
        """
        # Créer un conteneur pour la bulle
        bubble_container = QWidget()
        container_layout = QVBoxLayout(bubble_container)
        container_layout.setContentsMargins(0, 0, 0, 10)

        # Aligner la bulle à gauche avec un layout horizontal
        h_layout = QHBoxLayout()
        h_layout.setContentsMargins(0, 0, 0, 0)

        # Créer un widget pour contenir la bulle
        bubble = QFrame()
        bubble.setObjectName("ai_bubble")
        bubble.setStyleSheet(
            """
            QFrame#ai_bubble {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #E3F2FD, stop:1 #BBDEFB);
                border-radius: 15px;
                border-bottom-left-radius: 0px;
                padding: 10px;
                
            }
        """
        )

        # Layout pour la bulle
        bubble_layout = QHBoxLayout(bubble)
        bubble_layout.setContentsMargins(10, 8, 10, 8)

        # Icône SVG vectorielle
        svg_widget = self._get_svg_icon(icon_name, size=icon_size, color=icon_color)
        if svg_widget:
            bubble_layout.addWidget(svg_widget)
        else:
            # Fallback si l'icône n'est pas trouvée
            icon_label = QLabel()
            icon_label.setFixedSize(icon_size, icon_size)
            bubble_layout.addWidget(icon_label)
        # Texte
        label = QLabel(message)
        label.setStyleSheet(
            """
            color: #0D47A1; 
            font-size: 12px;
            background: transparent;
            margin-left: 10px;
        """
        )
        if not word_wrap:
            label.setStyleSheet(label.styleSheet() + "white-space: nowrap;")
        else:
            label.setWordWrap(True)
            label.setMinimumWidth(300)
            label.setMaximumWidth(
                400
            )  # Limiter la largeur pour éviter les lignes trop longues

        bubble_layout.addWidget(label)

        h_layout.addWidget(bubble)
        h_layout.addStretch(1)  # Cela pousse la bulle vers la gauche
        container_layout.addLayout(h_layout)

        # Ajouter la bulle au layout de chat
        self.chat_layout.addWidget(bubble_container)

        # Faire défiler vers le bas
        self._scroll_to_bottom()

        return bubble_container

    def _scroll_to_bottom(self):
        """Fait défiler la zone de chat vers le bas"""
        # Utiliser QTimer.singleShot pour s'assurer que le défilement se produit après le rendu
        QTimer.singleShot(0, lambda: self.scroll.verticalScrollBar().setValue(
            self.scroll.verticalScrollBar().maximum()
        ))

    def add_action_message(
        self,
        message,
        buttons=None,
        icon_name="user",
        icon_color="#2196F3",
        icon_size=20,
    ):
        """Ajoute un message avec des boutons d'action
        
        Args:
            message (str): Message à afficher
            buttons (list): Liste de dictionnaires avec 'text' et 'color' pour chaque bouton
                           Exemple: [{'text': 'Accepter', 'color': '#4CAF50'}, {'text': 'Refuser', 'color': '#F44336'}]
            icon_name (str): Nom de l'icône SVG à utiliser
            icon_color (str): Couleur de l'icône (format CSS)
            icon_size (int): Taille de l'icône en pixels
            
        Returns:
            ActionBubble: Le widget de la bulle d'action créée
        """
        # Valeurs par défaut pour les boutons si non spécifiés
        if buttons is None:
            buttons = [
                {"text": "Accepter", "color": "#4CAF50"},  # Vert
                {"text": "Refuser", "color": "#F44336"}   # Rouge
            ]
            
        # Créer la bulle d'action
        action_bubble = ActionBubble(
            message=message,
            buttons=buttons,
            icon_name=icon_name,
            icon_color=icon_color,
            icon_size=icon_size,
            parent=self
        )
        
        # Ajouter la bulle au layout de chat
        self.chat_layout.addWidget(action_bubble)
        
        # Faire défiler vers le bas
        self._scroll_to_bottom()
        
        return action_bubble

    def display_project_name_input(self):
        """Affiche une bulle de saisie pour le nom du projet en utilisant InputChatBubble"""
        # Indiquer qu'on est en mode création de projet pour éviter les messages de bienvenue
        self.is_creating_project = True

        # Nettoyer le chat si nécessaire
        self._clear_chat_area()

        # Ajouter un message explicatif
        self.add_ai_message(
            "Je vais vous aider à créer un projet. Commençons par définir le nom de votre projet :"
        )

        # Importer et créer une instance de InputChatBubble
        from project.structure.ui.widgets.input_chat_bubble import InputChatBubble

        # Créer le composant InputChatBubble
        self.input_chat_bubble = InputChatBubble(self)
        bubble_container = self.input_chat_bubble.add_project_name_input()
        self.chat_layout.addWidget(bubble_container)

        # Connecter le signal projectNameSubmitted au signal project_name_submitted de ChatPanel
        # pour le propager vers l'extérieur
        self.input_chat_bubble.projectNameSubmitted.connect(
            self._on_project_name_submitted
        )

        # Faire défiler vers le bas après un court délai
        from PySide6.QtCore import QTimer

        QTimer.singleShot(50, self._scroll_to_bottom)

        # Mettre le focus sur le champ de saisie
        self.input_chat_bubble.project_name_input.setFocus()

    def get_selected_model(self):
        """Renvoie le modèle actuellement sélectionné"""
        return self.selected_model

    def _show_help_dialog(self):
        """Affiche le dialogue d'aide avec les cartes de rubriques"""
        # Effacer temporairement les messages existants pour afficher l'aide
        # Sauvegarde de l'état actuel des messages
        self._save_current_chat_state()

        # Effacer la zone de chat pour afficher l'aide
        self._clear_chat_area()

        # Créer et afficher le dialogue d'aide directement dans la zone de chat
        self.help_dialog = HelpDialog()
        self.chat_layout.addWidget(self.help_dialog)

        # Connecter le signal pour retourner à la conversation
        self.help_dialog.back_requested.connect(self._restore_chat_state)
        self.help_dialog.topic_selected.connect(self._on_help_topic_selected)

    def display_project(self):
        """Affiche la grille d'actions pour les projets (alias pour display_project_actions)"""
        self.display_project_actions()

    def display_project_actions(self):
        """Affiche la grille d'actions pour les projets"""
        # Sauvegarder l'état actuel du chat
        self._save_current_chat_state()

        # Effacer la zone de chat pour afficher les actions du projet
        self._clear_chat_area()

        # Créer et afficher la grille d'actions projet
        self.project_actions_grid = ProjectActionsGrid()
        self.chat_layout.addWidget(self.project_actions_grid)

        # Connecter les signaux
        self.project_actions_grid.back_requested.connect(self._restore_chat_state)
        self.project_actions_grid.action_selected.connect(
            self._on_project_action_selected
        )

    def _on_project_action_selected(self, action):
        """Gère la sélection d'une action projet"""
        action_id = action.get("id", "")

        # Restaurer l'état du chat
        # self._restore_chat_state()

        # Ajouter un message IA pour indiquer l'action choisie
        self.add_ai_message(
            f"Vous avez choisi de {action.get('title', 'Action projet')}"
        )

        # Traiter l'action selon son type
        if action_id == "create":
            # Appeler la méthode d'affichage du formulaire de saisie du nom du projet
            self.display_project_name_input()
        elif action_id == "edit":
            # Logique pour modifier un projet
            self.add_ai_message(
                "Veuillez sélectionner le projet à modifier dans l'arborescence"
            )
        elif action_id == "delete":
            # Logique pour supprimer un projet
            self.add_ai_message(
                "Veuillez sélectionner le projet à supprimer dans l'arborescence"
            )
        elif action_id == "archive":
            # Logique pour archiver un projet
            self.add_ai_message(
                "Veuillez sélectionner le projet à archiver dans l'arborescence"
            )
        elif action_id == "version":
            # Logique pour versionner un projet
            self.add_ai_message(
                "Veuillez sélectionner le projet à versionner dans l'arborescence"
            )

    def _on_send_message(self, *args):
        """Récupère le message saisi et l'envoie au traitement"""
        message = self.user_input.toPlainText().strip()
        if message:
            # Effacer l'entrée utilisateur après envoi
            self.user_input.clear()
            # Traiter le message
            self.on_message_sent(message)

    def __init_command_processor(self):
        """Initialise le processeur de commandes"""
        from project.structure.core.command_processor import CommandProcessor

        self.command_processor = CommandProcessor()

    @Slot(str)
    def on_message_sent(self, message_text):
        """Gère l'envoi d'un message utilisateur"""
        # Vérifier que le message n'est pas vide
        if not message_text.strip():
            return

        # Initialiser le processeur de commandes si nécessaire
        if not hasattr(self, "command_processor"):
            self.__init_command_processor()

        # Analyser le message pour détecter les commandes
        cmd_result = self.command_processor.process_command(message_text)

        # Traiter la commande d'aide spéciale
        if cmd_result.is_help_command:
            # Utiliser la méthode du ChatPanel pour afficher les cartes d'aide
            self.show_help_cards()
            return

        # Traiter la commande projet pour afficher la grille d'actions projet
        if cmd_result.is_project_actions_command:
            # Afficher la grille d'actions projet
            self.display_project()
            return

        # Le message utilisateur est déjà ajouté par le ChatPanel

        # Si le serveur n'est pas connecté, afficher un message d'erreur
        if not self.server_connected:
            self.add_ai_message(
                "<span style='color: #ff6060;'>Le serveur IA n'est pas connecté. Veuillez vérifier la connexion.</span>"
            )
            return

        # Ajouter le message à la conversation actuelle
        self.current_conversation.append({"role": "user", "content": message_text})

        # Vérifier si nous avons une commande à traiter avant d'envoyer à l'IA
        if cmd_result.is_command:
            # Récupérer l'icône pour l'action
            from core.command_processor import ActionType

            action_icon, action_color = ActionType.get_icon_for_action(
                cmd_result.category, cmd_result.action
            )

            # Vous pouvez ajouter ici le code pour traiter les différents types de commandes
            # selon cmd_result.category et cmd_result.action
            # ...

        # Si ce n'est pas une commande ou après traitement, envoyer à l'IA
        # Pour l'exemple, ajoutons une réponse simple
        response = "J'ai reçu votre message: " + message_text
        self.chat_panel.add_ai_message(response)

        # Ajouter la réponse à la conversation
        self.current_conversation.append({"role": "assistant", "content": response})
        QTimer.singleShot(100, self._scroll_to_bottom)

    def _save_current_chat_state(self):
        """Sauvegarde l'état actuel du chat avant d'afficher l'aide"""
        # Sauvegarder les widgets actuels
        self.saved_widgets = []
        for i in range(self.chat_layout.count()):
            item = self.chat_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                self.saved_widgets.append(widget)
                # Détacher sans détruire
                self.chat_layout.removeWidget(widget)
                widget.setParent(None)
                widget.hide()

    def _restore_chat_state(self):
        """Restaure l'état du chat sauvegardé"""
        # Supprimer le dialogue d'aide
        if hasattr(self, "help_dialog") and self.help_dialog:
            self.help_dialog.deleteLater()
            self.help_dialog = None

        # Effacer complètement l'écran d'abord
        self._clear_chat_area()

        # Après un court délai, restaurer l'état précédent
        QTimer.singleShot(100, self._restore_saved_chat_area)

    def show_help_cards(self):
        """Affiche les cartes d'aide directement dans la fenêtre de chat"""
        # Effacer temporairement les messages existants pour afficher l'aide
        self._save_current_chat_state()
        self._clear_chat_area()

        # Importer le composant ici pour éviter les imports circulaires
        from project.structure.ui.widgets.help_cards_grid import HelpCardsGrid

        # Créer le composant de grille de cartes d'aide
        self.help_cards_grid = HelpCardsGrid(self)

        # Connecter les signaux du composant
        self.help_cards_grid.topic_selected.connect(self._show_topic_content)
        self.help_cards_grid.back_requested.connect(self._restore_chat_state)

        # Ajouter le composant au layout de chat
        self.chat_layout.addWidget(self.help_cards_grid)

        # Faire défiler vers le bas après un court délai
        QTimer.singleShot(100, self._scroll_to_bottom)

    def _show_topic_content(self, topic):
        """Affiche le contenu d'une rubrique d'aide"""
        if isinstance(topic, dict) and topic.get("title") == "Création de projet":
            # Afficher la grille des types de projets
            self.display_project_types()
        else:
            # Pour les autres rubriques, afficher le contenu normal
            # Effacer les cartes d'aide
            self._clear_chat_area()

            # Afficher le titre de la rubrique
            title_bubble = ChatBubble(f"<b>{topic['title']}</b>", is_user=False)
            self.chat_layout.addWidget(title_bubble)

            # Afficher le contenu de la rubrique
            content_bubble = ChatBubble(topic["content"], is_user=False)
            self.chat_layout.addWidget(content_bubble)

        QTimer.singleShot(100, self._scroll_to_bottom)

    def display_project_types(self):
        """Affiche les types de projets disponibles"""
        try:
            # Importer ProjectCreatorShow
            from project.structure.project_creator_show import ProjectCreatorShow

            # Initialiser ProjectCreatorShow si ce n'est pas déjà fait
            if not hasattr(self, "project_show") or self.project_show is None:
                self.project_show = ProjectCreatorShow()

                # N'essayons pas de connecter les signaux ici car ils peuvent ne pas exister
                # dans la classe ChatPanel. Laissons la classe dérivée s'en charger.
                # La classe ChatPanel n'a que la méthode _on_technology_selected
                if hasattr(self, "_on_technology_selected"):
                    # Vérifier si le signal est bien connecté avant de déconnecter
                    # utilisation de blocksignals pour éviter les warnings
                    old_state = self.project_show.blockSignals(True)
                    try:
                        # Déconnecter seulement si nécessaire
                        if hasattr(self.project_show, "technology_selected"):
                            from PySide6.QtCore import QObject

                            if (
                                QObject.receivers(self.project_show.technology_selected)
                                > 0
                            ):
                                self.project_show.technology_selected.disconnect(
                                    self._on_technology_selected
                                )
                    except Exception as e:
                        print(
                            f"[INFO] Signal déjà déconnecté ou jamais connecté: {str(e)}"
                        )

                    # Rétablir l'état des signaux
                    self.project_show.blockSignals(old_state)

                    # Connecter le signal (est toujours sécurisé)
                    self.project_show.technology_selected.connect(
                        self._on_technology_selected
                    )

            # Obtenir les données des types de projets
            project_types = self.project_show.get_project_types_data()

            # Effacer les bulles précédentes
            self._save_current_chat_state()
            self._clear_chat_area()

            # Utiliser notre composant ProjectTypesGrid pour afficher les projets
            from project.structure.ui.widgets.project_types_grid import ProjectTypesGrid

            self.project_types_grid = ProjectTypesGrid(project_types, self)

            # Connecter les signaux - utiliser les méthodes qui existent dans cette classe
            self.project_types_grid.project_type_selected.connect(
                self.on_project_type_selected
            )
            # Utiliser une méthode spécifique pour revenir aux cartes d'aide
            self.project_types_grid.back_requested.connect(self._back_to_help_cards)

            # Ajouter le composant au layout de chat
            self.chat_layout.addWidget(self.project_types_grid)

            # Faire défiler vers le bas après un court délai
            QTimer.singleShot(100, self._scroll_to_bottom)

        except Exception as e:
            print(f"Erreur lors de l'affichage des types de projet: {str(e)}")
            # En cas d'erreur, restaurer l'état précédent
            self._restore_chat_state()

    def _on_help_topic_selected(self, topic):
        """Gère la sélection d'une rubrique d'aide"""
        # Vérifier si c'est la rubrique "Création de projet"
        if isinstance(topic, dict) and topic.get("title") == "Création de projet":
            # Afficher la grille des types de projets
            self.display_project_types()
        else:
            # Pour les autres rubriques, on pourrait ajouter des actions spécifiques ici
            pass

    def on_project_type_selected(self, project_type_id):
        """Gère la sélection d'un type de projet"""
        # Émettre le signal pour que ui_agent_ia.py puisse le traiter
        self.project_type_selected.emit(project_type_id)

    def _restore_saved_chat_area(self):
        """Restaure les widgets sauvegardés dans la zone de chat"""
        for widget in self.saved_widgets:
            self.chat_layout.addWidget(widget)
            widget.setParent(self.chat_widget)  # Reparenting
            widget.show()

        # Vider la liste sauvegardée
        self.saved_widgets = []

        # Faire défiler vers le bas après restauration
        QTimer.singleShot(100, self._scroll_to_bottom)

    def _clear_chat_area(self):
        """Efface la zone de chat sans émettre de signal"""
        # Supprimer tous les widgets du chat sans les détruire
        while self.chat_layout.count():
            child = self.chat_layout.takeAt(0)
            if child:
                widget = child.widget()
                if widget:
                    widget.setParent(None)
                    widget.hide()

    def on_project_type_selected(self, project_type_id):
        """Gère la sélection d'un type de projet"""
        # Émettre le signal pour la classe parente
        self.project_type_selected.emit(project_type_id)

        # Si la méthode n'est pas surchargeée par la classe parente,
        # on peut afficher les technologies avec des valeurs par défaut
        try:
            from project.structure.project_creator_show import ProjectCreatorShow

            project_show = ProjectCreatorShow()
            tech_data = project_show.get_technologies_data(project_type_id)
            technologies = tech_data["technologies"]
            project_type_name = tech_data.get("project_type_name", "Projet")
            project_color = tech_data.get("project_color", "#2E7D32")

            self.display_technologies(
                technologies, project_type_id, project_type_name, project_color
            )
        except Exception as e:
            print(f"Erreur lors de l'affichage des technologies: {str(e)}")
            # Utiliser des valeurs par défaut en cas d'erreur
            # Normalement, cette méthode sera surchargeée par la classe parente

    def display_technologies(
        self, technologies, project_type_id, project_type_name, project_color
    ):
        """Affiche les technologies disponibles pour un type de projet"""
        # Effacer les widgets existants
        self._clear_chat_area()

        # Importer le composant TechnologiesGrid
        from project.structure.ui.widgets.technologies_grid import TechnologiesGrid

        # Créer le composant de grille de technologies
        self.technologies_grid = TechnologiesGrid(
            technologies, project_type_id, project_type_name, project_color, self
        )

        # Connecter les signaux du composant
        self.technologies_grid.technology_selected.connect(self._on_technology_selected)
        # Le retour depuis les technologies doit revenir à la grille des types de projets
        self.technologies_grid.back_requested.connect(self._back_to_project_types)

        # Ajouter le composant au layout de chat
        self.chat_layout.addWidget(self.technologies_grid)

        # Faire défiler vers le bas après un court délai
        QTimer.singleShot(100, self._scroll_to_bottom)

    def _on_technology_selected(self, tech_id, project_type_id):
        """Gère la sélection d'une technologie"""
        # Nettoyer spécifiquement le composant de technologies s'il existe
        if hasattr(self, "technologies_grid") and self.technologies_grid is not None:
            try:
                # Déconnecter les signaux
                self.technologies_grid.technology_selected.disconnect(
                    self._on_technology_selected
                )
                self.technologies_grid.back_requested.disconnect(
                    self._back_to_project_types
                )

                # Supprimer le widget du layout
                self.chat_layout.removeWidget(self.technologies_grid)
                self.technologies_grid.deleteLater()
                self.technologies_grid = None
            except Exception as e:
                print(
                    f"[ATTENTION] Erreur lors du nettoyage du composant technologies_grid: {str(e)}"
                )
        # Affiche les langages pour la technologie sélectionnée
        self.display_languages(tech_id, project_type_id)

        # Émettre le signal pour la classe parente
        self.technology_selected.emit(tech_id, project_type_id)

    def _back_to_project_types(self):
        """Revient à l'affichage des types de projets"""
        # Débrancher les signaux de technologies_grid si présent
        if hasattr(self, "technologies_grid") and self.technologies_grid is not None:
            try:
                self.chat_layout.removeWidget(self.technologies_grid)
                self.technologies_grid.deleteLater()
                self.technologies_grid = None
            except Exception as e:
                print(
                    f"Erreur lors du nettoyage de la grille de technologies: {str(e)}"
                )

        # Afficher la grille des types de projets
        self.display_project_types()

    def display_languages(self, tech_id, project_type_id):
        """Affiche les langages de programmation disponibles pour une technologie

        Args:
            tech_id (str): Identifiant de la technologie sélectionnée
            project_type_id (str): Identifiant du type de projet parent
        """
        # Nettoyer l'espace de chat
        self._clear_chat_area()

        # Importer le composant ProgrammingLanguagesGrid
        from project.structure.ui.widgets.programming_languages_grid import (
            ProgrammingLanguagesGrid,
        )

        # Obtenir les langages pour cette technologie via ProjectCreatorShow
        from project.structure.project_creator_show import ProjectCreatorShow

        project_show = ProjectCreatorShow()
        languages_data = project_show.get_programming_languages_data(tech_id)

        # Extraire les données
        languages = languages_data.get("languages", [])
        tech_name = languages_data.get("tech_name", "Technologie")
        tech_color = languages_data.get("tech_color", "#2196F3")

        # Créer le composant de grille de langages
        self.languages_grid = ProgrammingLanguagesGrid(
            languages, tech_id, tech_name, tech_color, self
        )

        # Connecter les signaux
        self.languages_grid.language_selected.connect(self._on_language_selected)
        # Le signal back_requested doit revenir aux technologies avec le bon project_type_id
        self.languages_grid.back_requested.connect(
            lambda: self._back_to_technologies(project_type_id)
        )

        # Ajouter le composant au layout de chat
        self.chat_layout.addWidget(self.languages_grid)

        # Faire défiler vers le bas après un court délai
        QTimer.singleShot(100, self._scroll_to_bottom)

    def add_ai_infos(
        self,
        message,
        word_wrap=True,
        icon_name="info",
        icon_color="#64B5F6",
        icon_size=20,
    ):
        """Ajoute une bulle d'informations en mode sombre avec une icône d'info

        Args:
            message (str): Message d'information à afficher
            word_wrap (bool, optional): Activer le retour à la ligne automatique. Par défaut True.
            icon_name (str, optional): Nom de l'icône. Par défaut "info".
            icon_color (str, optional): Couleur de l'icône. Par défaut "#64B5F6".
            icon_size (int, optional): Taille de l'icône. Par défaut 20.

        Returns:
            QWidget: Le widget de la bulle d'info créée
        """
        # Créer un conteneur pour la bulle
        bubble_container = QWidget()
        container_layout = QVBoxLayout(bubble_container)
        container_layout.setContentsMargins(0, 0, 0, 10)

        # Aligner la bulle à gauche avec un layout horizontal
        h_layout = QHBoxLayout()
        h_layout.setContentsMargins(0, 0, 0, 0)

        # Créer un widget pour contenir la bulle
        bubble = QFrame()
        bubble.setObjectName("info_bubble")
        bubble.setStyleSheet(
            """
            QFrame#info_bubble {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #263238, stop:1 #37474F);
                border-radius: 15px;
                border-bottom-left-radius: 5px;
                padding: 10px;
                border-left: 3px solid #64B5F6;
            }
        """
        )

        # Layout pour la bulle
        bubble_layout = QHBoxLayout(bubble)
        bubble_layout.setContentsMargins(10, 10, 10, 10)

        #  Icône SVG vectorielle
        svg_widget = self._get_svg_icon(icon_name, size=icon_size, color=icon_color)
        if svg_widget:
            bubble_layout.addWidget(svg_widget)
        else:
            # Fallback si l'icône n'est pas trouvée
            icon_label = QLabel()
            icon_label.setFixedSize(icon_size, icon_size)
            bubble_layout.addWidget(icon_label)

        # Texte
        label = QLabel(message)
        label.setStyleSheet(
            """
            color: #E3F2FD; 
            font-size: 12px;
            background: transparent;
        """
        )
        if not word_wrap:
            label.setStyleSheet(label.styleSheet() + "white-space: nowrap;")
        else:
            label.setWordWrap(True)
            label.setMinimumWidth(300)
            label.setMaximumWidth(500)  # Plus large pour les informations

        bubble_layout.addWidget(label)

        h_layout.addWidget(bubble)
        h_layout.addStretch(1)  # Cela pousse la bulle vers la gauche
        container_layout.addLayout(h_layout)

        # Ajouter la bulle au layout de chat
        self.chat_layout.addWidget(bubble_container)

        # Faire défiler vers le bas
        self._scroll_to_bottom()

        return bubble_container
        # Créer un conteneur pour la bulle
        bubble_container = QWidget()
        container_layout = QVBoxLayout(bubble_container)
        container_layout.setContentsMargins(0, 0, 0, 10)

        # Aligner la bulle à gauche avec un layout horizontal
        h_layout = QHBoxLayout()
        h_layout.setContentsMargins(0, 0, 0, 0)

        # Créer un widget pour contenir la bulle
        bubble = QFrame()
        bubble.setObjectName("info_bubble")
        bubble.setStyleSheet(
            """
            QFrame#info_bubble {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #263238, stop:1 #37474F);
                border-radius: 15px;
                border-bottom-left-radius: 5px;
                padding: 10px;
                border-left: 3px solid #64B5F6;
            }
        """
        )

        # Layout pour la bulle
        bubble_layout = QHBoxLayout(bubble)
        bubble_layout.setContentsMargins(10, 10, 10, 10)

        #  Icône SVG vectorielle
        svg_widget = self._get_svg_icon(icon_name, size=icon_size, color=icon_color)
        if svg_widget:
            bubble_layout.addWidget(svg_widget)
        else:
            # Fallback si l'icône n'est pas trouvée
            icon_label = QLabel()
            icon_label.setFixedSize(icon_size, icon_size)
            bubble_layout.addWidget(icon_label)

        # Texte
        label = QLabel(message)
        label.setStyleSheet(
            """
            color: #E3F2FD; 
            font-size: 12px;
            background: transparent;
        """
        )
        if not word_wrap:
            label.setStyleSheet(label.styleSheet() + "white-space: nowrap;")
        else:
            label.setWordWrap(True)
            label.setMinimumWidth(300)
            label.setMaximumWidth(500)  # Plus large pour les informations

        bubble_layout.addWidget(label)

        h_layout.addWidget(bubble)
        h_layout.addStretch(1)  # Cela pousse la bulle vers la gauche
        container_layout.addLayout(h_layout)

        # Ajouter la bulle au layout de chat
        self.chat_layout.addWidget(bubble_container)

        # Faire défiler vers le bas
        self._scroll_to_bottom()

        return bubble_container

    def _on_language_selected(self, lang_id, tech_id):
        """Gère la sélection d'un langage"""
        # Nettoyer spécifiquement le composant de langages s'il existe
        if hasattr(self, "languages_grid") and self.languages_grid is not None:
            try:
                # Déconnecter les signaux
                self.languages_grid.language_selected.disconnect(
                    self._on_language_selected
                )
                # Déconnecter le signal back_requested en utilisant un bloc try/except
                try:
                    # Le signal peut être connecté à une lambda fonction
                    self.languages_grid.back_requested.disconnect()
                except Exception:
                    pass

                # Supprimer le widget du layout
                self.chat_layout.removeWidget(self.languages_grid)
                self.languages_grid.deleteLater()
                self.languages_grid = None
            except Exception as e:
                print(
                    f"[ATTENTION] Erreur lors du nettoyage du composant languages_grid: {str(e)}"
                )

        # Émettre le signal pour la classe parente

        # Affiche un recap des infos
        self.add_ai_infos(
            f"<b>Information:</b><br>Vous avez choisi <b>{tech_id}</b> pour la technologie<br>et <b>{lang_id}</b> pour le langage de programmation."
        )

        # Nous utilisons un nouveau signal language_selected que nous allons ajouter
        if hasattr(self, "language_selected"):
            self.language_selected.emit(lang_id, tech_id)

    def _back_to_technologies(self, project_type_id):
        """Revient à l'affichage des technologies après nettoyage du composant languages_grid"""
        # Nettoyer d'abord l'espace de chat
        self._clear_chat_area()

        # Nettoyer spécifiquement le composant de langages s'il existe
        if hasattr(self, "languages_grid") and self.languages_grid is not None:
            try:
                # Déconnecter les signaux
                self.languages_grid.language_selected.disconnect(
                    self._on_language_selected
                )
                # Déconnecter le signal back_requested en utilisant un bloc try/except
                try:
                    self.languages_grid.back_requested.disconnect()
                except Exception:
                    pass

                # Supprimer le widget du layout s'il n'a pas déjà été supprimé
                try:
                    self.chat_layout.removeWidget(self.languages_grid)
                except Exception:
                    pass

                self.languages_grid.deleteLater()
                self.languages_grid = None
            except Exception as e:
                print(
                    f"[DEBUG] Erreur lors du nettoyage du composant languages_grid: {str(e)}"
                )

        # Obtenir les données du projet
        from project.structure.project_creator_show import ProjectCreatorShow

        project_show = ProjectCreatorShow()

        try:
            # Récupérer directement les technologies pour ce type de projet
            technologies = project_show.get_technologies_for_project_type(
                project_type_id
            )

            # Trouver les autres infos du type de projet si disponible
            project_name = "Type de projet"
            project_color = "#4CAF50"

            # Essayer de récupérer le nom et la couleur du projet depuis get_project_types
            for pt in project_show.get_project_types():
                if pt["id"] == project_type_id:
                    project_name = pt.get("name", "Type de projet")
                    project_color = pt.get("color", "#4CAF50")
                    break

            # Afficher les technologies pour ce type de projet
            print(
                f"[DEBUG] Retour aux technologies pour {project_name} ({project_type_id}): {len(technologies)} technologies"
            )

            # Afficher les technologies pour ce type de projet
            self.display_technologies(
                technologies, project_type_id, project_name, project_color
            )
        except Exception as e:
            print(f"[ERREUR] Erreur lors du retour aux technologies: {str(e)}")
            # En cas d'erreur, revenir à la liste des types de projets
            self._back_to_project_types()

    def _back_to_help_cards(self):
        """Revient à l'affichage des cartes d'aide"""
        # Nettoyer les widgets actuels
        if hasattr(self, "project_types_grid") and self.project_types_grid is not None:
            try:
                self.chat_layout.removeWidget(self.project_types_grid)
                self.project_types_grid.deleteLater()
                self.project_types_grid = None
            except Exception as e:
                print(
                    f"Erreur lors du nettoyage de la grille de types de projet: {str(e)}"
                )

        # Afficher les cartes d'aide
        self.show_help_cards()

    def on_project_type_selected(self, project_type_id):
        """Gère la sélection d'un type de projet"""
        print(f"ChatPanel: Type de projet sélectionné: {project_type_id}")
        # Cette méthode peut être surchargée par les classes dérivées
        # Pour ChatPanel, nous allons simplement afficher les technologies
        try:
            # Par défaut, utiliser le projet sélectionné sans méta-données supplémentaires
            project_name = None
            project_color = "#4CAF50"  # Vert par défaut
            technologies = []

            # Si nous avons accès à ProjectCreatorShow, essayons d'obtenir les données du projet
            if hasattr(self, "project_show") and self.project_show is not None:
                try:
                    # Récupérer les données du type de projet
                    project_types = self.project_show.get_project_types_data()
                    for project_type in project_types:
                        if project_type.get("id") == project_type_id:
                            project_name = project_type.get("name")
                            project_color = project_type.get("color", "#4CAF50")
                            break

                    # Récupérer les technologies pour ce type de projet
                    tech_data = self.project_show.get_technologies_data(project_type_id)
                    technologies = tech_data.get("technologies", [])
                except Exception as e:
                    print(
                        f"Erreur lors de la récupération des données du type de projet: {str(e)}"
                    )

            # Afficher les technologies pour ce type de projet
            self.display_technologies(
                technologies, project_type_id, project_name, project_color
            )

            # Émettre le signal pour la classe parente
            self.project_type_selected.emit(project_type_id)

        except Exception as e:
            print(f"Erreur lors de la sélection d'un type de projet: {str(e)}")

    def _on_project_name_submitted(self, project_name):
        """Gère la soumission du nom du projet"""
        print(f"Nom du projet soumis: {project_name}")
        self.project_name_submitted.emit(project_name)
