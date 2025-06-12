# ui_agent_ia.py
import sys
from PySide6.QtWidgets import ( QApplication,QWidget,QVBoxLayout, QHBoxLayout,
    QSplitter, QFileDialog, QGridLayout,
)
from PySide6.QtCore import (  Qt,    QThread,    Slot,  QTimer)
from PySide6.QtGui import (
    QPixmap,
    QFont,
    QColor,
    QPalette,
    QIcon,
    QAction,
    QPainter,
    QFontMetrics,
    QDesktopServices,
    QKeyEvent,
)
from PySide6.QtSvg import QSvgRenderer
import json
import os
import datetime
import uuid

# Import du CommandProcessor
import sys
import os

# Ajouter le répertoire parent au chemin d'importation
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import des classes depuis les fichiers séparés
from chat_bubble import ChatBubble
from interactive_chat_bubble import InteractiveChatBubble
#from input_chat_bubble import InputChatBubble
from path_confirmation_buttons import PathConfirmationButtons
from action_confirmation_bubble import ActionConfirmationBubble

from project_creator import ProjectCreator
from project.structure.core.migration_adapter import ChatArboWidgetMigrationMixin

# Import du FileTreeWidget depuis le module local
from project.structure.file_tree_widget import (
    FileTreeWidget,
    FORBIDDEN_PATHS,
    SYSTEM_DRIVES,
)
from project_type_card import ProjectTypeCard
from project.structure.ui.widgets.chat_panel import ChatPanel
import sys
import os

# Ajouter le répertoire parent au chemin d'importation
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from ui.ui_utils import load_colored_svg


def get_svg_icon(icon_name, size=16, color=None):
    """
    Fonction utilitaire pour charger une icône SVG et la convertir en QPixmap avec fond transparent
    en utilisant directement load_colored_svg avec anti-aliasing pour éviter la pixelisation

    Args:
        icon_name (str): Nom du fichier SVG sans extension
        size (int): Taille de l'icône en pixels (peut être doublée pour une meilleure qualité)
        color (str): Couleur à appliquer à l'icône (format CSS, ex: '#4CAF50')

    Returns:
        QPixmap: L'icône chargée ou None si le fichier n'existe pas
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

    try:
        # Doubler la taille pour un meilleur rendu puis redimensionner
        render_size = size * 2

        # Créer un QPixmap de la taille doublée avec fond transparent
        pixmap = QPixmap(render_size, render_size)
        pixmap.fill(Qt.transparent)

        # Charger le SVG avec la couleur spécifiée
        svg_data = load_colored_svg(icon_path, color)
        if svg_data.isEmpty():
            print(f"[Erreur] SVG vide ou incorrect : {icon_path}")
            return None

        # Créer un QSvgRenderer pour dessiner le SVG
        renderer = QSvgRenderer(svg_data)

        # Dessiner le SVG sur le pixmap avec anti-aliasing
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)

        # Dessiner le SVG en utilisant tout l'espace disponible
        renderer.render(painter)
        painter.end()

        # Redimensionner à la taille finale avec une transformation lisse
        if render_size != size:
            return pixmap.scaled(
                size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )

        return pixmap
    except Exception as e:
        print(f"[Erreur] Impossible de charger l'icône {icon_name}: {str(e)}")
        return None

# Import des classes depuis les fichiers séparés
from project.structure.conversation_manager import ConversationManager
from project.structure.connection_worker import ConnectionWorker
from project.structure.project_creator import ProjectCreator


class ChatArboWidget(QWidget, ChatArboWidgetMigrationMixin):
    def __init__(self, root_path=None):
        super().__init__()
        # Initialiser le système de migration d'état
        self._initialize_migration()
        self.setWindowTitle("Assistant IA - Gestion de Projets")
        self.resize(1400, 800)

        # Variables pour stocker les chemins sélectionnés
        self.selected_project_path = None
        self.path_root = None  # Pour stocker le chemin complet de l'élément cliqué
        self.project_name = None  # Pour stocker le nom du projet
        self.wait_for_path = False  # Flag pour attendre la sélection d'un dossier

        # Variables pour stocker les informations du projet
        self.selected_project_type = None
        self.project_type_name = None
        self.selected_technology = None
        self.technology_name = None
        self.selected_language = None
        self.selected_language_name = None
        self.selected_app_type = None
        self.selected_app_type_name = None

        # Utiliser une icône existante pour l'application
        icon_path = os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            ),
            "assets",
            "icons",
            "brain.svg",
        )
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Statut du serveur IA
        self.server_connected = False

        splitter = QSplitter(Qt.Horizontal)

        # Utiliser notre composant déporté FileTreeWidget pour l'arborescence
        self.file_tree = FileTreeWidget()
        # Définir le chemin racine après la création si un chemin est fourni
        if root_path:
            self.file_tree.set_root_path(root_path)

        # Connecter les signaux aux slots
        self.file_tree.item_clicked.connect(self.on_tree_item_clicked)
        self.file_tree.file_operation.connect(self.on_file_operation)
        # self.file_tree.item_double_clicked.connect(self.on_tree_item_double_clicked)
        # self.file_tree.search_text_changed.connect(self.on_tree_search_changed)

        # Widget d'arborescence prêt à être utilisé
        tree_widget = self.file_tree

        # Chat Area - Utiliser le nouveau composant ChatPanel
        self.chat_panel = ChatPanel()

        # Connecter les signaux du chat_panel aux méthodes de la fenêtre principale
        #self.chat_panel.message_sent.connect(self.on_message_sent)
        self.chat_panel.clear_requested.connect(self.clear_conversation)
        self.chat_panel.project_name_submitted.connect(self.on_project_name_submitted)

        # Reconnexion des signaux de la barre supérieure qui étaient dans l'ancien code
        self.chat_panel.top_bar.exportClicked.connect(self.export_conversation)
        #self.chat_panel.top_bar.skeletonClicked.connect(self.start_app_skeleton_wizard)
        self.chat_panel.top_bar.historyClicked.connect(self.show_history)
        #self.chat_panel.top_bar.infoClicked.connect(self.show_project_info)
        self.chat_panel.top_bar.checkConnectionClicked.connect(
            self.check_server_connection
        )

        # Layout pour contenir le composant ChatPanel
        chat_panel = QVBoxLayout()
        chat_panel.addWidget(self.chat_panel)

        chat_right = QWidget()
        chat_right.setLayout(chat_panel)

        splitter.addWidget(
            tree_widget
        )  # Utiliser le widget contenant l'arborescence et la recherche
        splitter.addWidget(chat_right)
        splitter.setSizes([330, 900])

        main_layout = QHBoxLayout(self)
        main_layout.addWidget(splitter)

        self.stream_thread = None

        # Variables pour gestion actions à valider
        self.pending_actions = {}

        # Historique des conversations
        self.conversation_history = []
        self.current_conversation_id = str(uuid.uuid4())
        self.current_conversation = []

        # Vérifier la connexion au démarrage
        self.check_server_connection()

        # Ajouter un message de bienvenue après avoir initialisé toutes les variables
        welcome_message = "<b>Bienvenue dans l'Assistant IA !</b><br><br>Vous pouvez naviguer dans l'arborescence à gauche et discuter avec l'IA à droite.<br>N'hésitez pas à poser des questions ou à demander de l'aide."
        self.chat_panel.add_ai_message(welcome_message)

    
    def on_project_name_submitted(self, project_name):
        """
        Gère la soumission du nom de projet depuis InputChatBubble
        """
        # Stocker le nom du projet
        self.project_name = project_name
        
        # Vérifier si un chemin racine a été sélectionné
        if not self.path_root:
            # Aucun chemin sélectionné, demander à l'utilisateur d'en sélectionner un
            self.chat_panel.add_ai_message(
                "<span style='color:#c9530a'>Veuillez d'abord sélectionner un dossier dans l'arborescence à gauche pour y créer votre projet.</span>"
            )
            self.file_tree.highlight_tree_view()
            self.wait_for_path = True
            return

        # Afficher un message de confirmation sans réinitialiser la conversation
        confirmation_message = f"<b>Projet '{project_name}' créé.</b><br>Vous pouvez maintenant commencer à travailler sur votre projet."
        self.chat_panel.add_ai_message(confirmation_message)
        
        # Réinitialiser le flag is_creating_project dans ChatPanel
        self.chat_panel.is_creating_project = False

    def clear_conversation(self):
        """
        Efface la conversation actuelle et remet à zéro l'historique
        """
        # Réinitialiser la conversation courante
        self.current_conversation = []
        self.current_conversation_id = str(uuid.uuid4())

        # Ajouter un message de bienvenue
        welcome_message = "<b>Nouvelle conversation commencée.</b><br>Comment puis-je vous aider aujourd'hui?"
        self.chat_panel.add_ai_message(welcome_message)
    
    def on_file_operation(self, action, path, success, is_dir):
        """Gère les signaux d'opérations sur les fichiers/dossiers

        Args:
            action (str): Type d'action effectuée ("create", "delete", etc.)
            path (str): Chemin du fichier/dossier concerné
            success (bool): Indique si l'opération a réussi
            is_dir (bool): Indique si l'élément est un dossier (True) ou un fichier (False)
        """
        # Définir les messages et icônes en fonction de l'action et du résultat
        icon_color = (
            "#4CAF50" if success else "#F44336"
        )  # Vert si succès, rouge si échec

        # Obtenir le nom du fichier/dossier sans le chemin complet
        item_name = os.path.basename(path)

        # Déterminer le type d'élément (fichier ou dossier) à partir du paramètre is_dir
        item_type = "dossier" if is_dir else "fichier"

        # Créer un message différent selon l'action
        if action == "delete":
            if success:
                message = (
                    f"Le {item_type} <b>{item_name}</b> a été supprimé avec succès."
                )
                if is_dir:
                    self.selected_project_path = None
                    self.selected_app_type = None
                    self.selected_app_name = None
                    self.selected_app_path = None
                    self.selected_language_name = None
                    self.selected_language_path = None
                    self.selected_technology = None
                    self.selected_technology_path = None
                    self.path_root = None
                    self.wait_for_path = False
            else:
                message = f"Échec de la suppression du {item_type} <b>{item_name}</b>."
        elif action == "create":
            if success:
                message = f"Le {item_type} <b>{item_name}</b> a été créé avec succès."
            else:
                message = f"Échec de la création du {item_type} <b>{item_name}</b>."
        else:
            # Pour d'autres types d'actions
            if success:
                message = (
                    f"Opération '{action}' réussie sur {item_type} <b>{item_name}</b>."
                )
            else:
                message = f"Échec de l'opération '{action}' sur {item_type} <b>{item_name}</b>."

        # Afficher une notification via le ChatPanel
        # Pas besoin de clear_bubbles ici, juste ajouter le nouveau message
        self.chat_panel.add_ai_message(message)

    def on_tree_item_clicked(self, path, is_dir):
        """Gère le clic sur un élément de l'arborescence"""
        # self.clear_bubbles()

        # Afficher le chemin sélectionné dans la barre d'état
        print(f"Chemin sélectionné: {os.path.basename(path)}")

        # Utiliser la nouvelle méthode pour afficher le chemin sélectionné
        if not is_dir:
            # Si c'est un fichier, afficher le chemin du répertoire parent
            self.chat_panel.top_bar.update_selected_path(os.path.dirname(path), is_dir)
            self.path_root = os.path.dirname(path)
        else:
            # Si c'est un répertoire, afficher le chemin complet
            self.chat_panel.top_bar.update_selected_path(path, is_dir)
            self.path_root = path

        self.selected_project_path = os.path.join(self.path_root, self.project_name)

        # Si on attend la sélection d'un dossier pour la création de projet
        if hasattr(self, "wait_for_path") and self.wait_for_path:
            # Mettre en évidence l'arborescence avec un timer pour éviter l'exécution immédiate
            QTimer.singleShot(100, self.file_tree.highlight_tree_view)

            # Confirmer que le dossier a bien été sélectionné
            self.chat_panel.add_ai_message(
                f"<span >Le dossier <b>{os.path.basename(path)}</b> a été sélectionné pour votre projet.</span>",
                icon_name="folder",
            )
            
            # Marquer que nous avons géré l'attente du chemin
            self.wait_for_path = False
            # on creer le repertoire on appelle une classe spécialisée
            result = ProjectCreator.create_root_directory(self.selected_project_path)
            message = ""
            if result['status'] == 0:
                # affiche message ia
                message = f"<span>Le dossier <b>{os.path.basename(path)}</b> a été créé avec succès pour votre projet.</span>"
            elif result['status'] == 1:
                message = f"<span >Le dossier <b>{os.path.basename(path)}</b> existe déjà pour votre projet.</span>"
            else:
                message = f"<span style='color:#FFFFFF'>Erreur lors de la création du dossier <b>{os.path.basename(path)}</b> pour votre projet: {result['error']}</span>"

            self.chat_panel.add_ai_message(
                    message,
                    icon_name="folder",
                )

            if result['status'] == 0 :
                # on creer le repertoire on appelle une classe spécialisée
                result_structure=ProjectCreator.create_project_structure(self.selected_project_path, self.selected_project_type, self.selected_technology, self.project_name)
                message=""
                if result_structure['status'] == 0 :
                    # affiche message ia
                    message=f"<span style='color:#FFFFFF'>La structure du projet <b>{self.project_name}</b> a été créée avec succès.</span>"
                elif result_structure['status']==1:
                    message=f"<span style='color:#FFFFFF'>La structure du projet <b>{self.project_name}</b> existe déjà.</span>"
                else:
                    message=f"<span style='color:#FFFFFF'>Erreur lors de la création de la structure du projet <b>{self.project_name}</b>.</span>"

                self.chat_panel.add_ai_message(
                        message,
                        icon_name="folder",
                        icon_color="#4CAF50",
                        icon_size=24,
                    )

            # Rafraîchir l'arborescence
            self.file_tree.refresh_tree_view() 
            # expande le dossier du projet
            self.file_tree.select_item(self.selected_project_path)
            self.file_tree.expand_item(self.selected_project_path)
            
        else:
            # Pour les autres cas de clic sur le TreeView, on ne fait rien de spécial
            pass
    
    
    def get_project_root_path(self):
        # Si un chemin est déjà sélectionné, l'utiliser
        if self.selected_project_path and os.path.isdir(self.selected_project_path):
            return self.selected_project_path

        # Sinon, demander à l'utilisateur de sélectionner un dossier
        path = QFileDialog.getExistingDirectory(
            self,
            "Sélectionner le dossier racine du projet",
            os.path.expanduser("~"),
            QFileDialog.ShowDirsOnly,
        )

        if path:
            self.selected_project_path = path
            return path

        return None

    def check_server_connection(self):
        """Démarre un thread pour vérifier la connexion au serveur sans bloquer l'UI"""
        # Créer un thread pour exécuter la vérification en arrière-plan
        self.connection_thread = QThread()
        self.connection_worker = ConnectionWorker("http://localhost:8000/health")
        self.connection_worker.moveToThread(self.connection_thread)

        # Connecter les signaux
        self.connection_thread.started.connect(self.connection_worker.check_connection)
        self.connection_worker.connection_result.connect(self.on_connection_result)
        self.connection_worker.finished.connect(self.connection_thread.quit)
        self.connection_worker.finished.connect(self.connection_worker.deleteLater)
        self.connection_thread.finished.connect(self.connection_thread.deleteLater)

        # Démarrer le thread
        self.connection_thread.start()

    def on_connection_result(self, is_connected, message):
        """Gère le résultat de la vérification de connexion"""
        self.server_connected = is_connected
        try:
            if hasattr(self, "top_bar") and self.top_bar:
                self.top_bar.update_connection_status(is_connected, message)
        except RuntimeError:
            # L'objet a déjà été supprimé, ignorer silencieusement
            print(
                "Impossible de mettre à jour le statut de connexion : top_bar a été supprimé"
            )
        except Exception as e:
            print(f"Erreur lors de la mise à jour du statut de connexion : {e}")
        
    def display_project_subtypes(self, project_type_id, technology_id, language_id):
        """Affiche les sous-types de projets spécifiques pour la combinaison choisie"""
        # Nettoyer l'espace de travail actuel directement
        while self.chat_layout.count() > 0:
            item = self.chat_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Ajouter un bouton de retour pour revenir à la sélection des langages
        from project.structure.back_button import BackButton

        back_button = BackButton("« Retour aux langages")
        
        # Ajouter le bouton au layout
        back_container = QWidget()
        back_layout = QHBoxLayout(back_container)
        back_layout.setContentsMargins(10, 5, 10, 5)
        back_layout.addWidget(back_button)
        back_layout.addStretch(1)

        self.chat_layout.addWidget(back_container)

        # Liste des sous-types de projets selon la combinaison choisie
        # Cette liste pourrait être dynamique en fonction du type de projet, de la technologie et du langage
        project_subtypes = [
            {
                "id": "webapp",
                "name": "Application Web",
                "description": "Application web complète avec frontend et backend",
                "icon": "globe",
            },
            {
                "id": "static",
                "name": "Site Statique",
                "description": "Site web simple sans backend",
                "icon": "file-code",
            },
            {
                "id": "api",
                "name": "API REST",
                "description": "Interface de programmation pour services web",
                "icon": "cloud",
            },
            {
                "id": "dashboard",
                "name": "Tableau de bord",
                "description": "Interface d'administration avec visualisations",
                "icon": "chart-line",
            },
        ]

        # Création d'un conteneur pour les cartes de sous-types
        project_subtype_container = QWidget()
        project_subtype_container.setObjectName("project_subtype_container")
        grid_layout = QGridLayout(project_subtype_container)
        grid_layout.setHorizontalSpacing(10)
        grid_layout.setVerticalSpacing(10)

        # Ajouter les cartes de sous-types
        row, col = 0, 0
        max_cols = 4  # Nombre maximum de colonnes (aligné avec les autres affichages)

        for subtype in project_subtypes:
            try:
                # Créer une fonction de gestionnaire pour ce sous-type spécifique
                def create_subtype_click_handler(subtype_id):
                    return lambda: self.on_project_subtype_selected(
                        subtype_id, project_type_id, technology_id, language_id
                    )

                # Créer la carte
                card = ProjectTypeCard(subtype)
                card.setProperty("project_subtype_bubble", True)
                card.setProperty("project_subtype_id", subtype["id"])
                card.clicked.connect(create_subtype_click_handler(subtype["id"]))

                # Ajouter la carte à la grille
                grid_layout.addWidget(card, row, col)

                # Passer à la colonne/ligne suivante
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
            except Exception as e:
                print(f"Erreur lors de la création de la carte de sous-type: {e}")

        # Si la dernière ligne n'est pas complète, ajouter des widgets vides pour maintenir l'alignement
        if col > 0 and col < max_cols:
            # Ajouter des widgets vides pour compléter la ligne
            for i in range(max_cols - col):
                empty_widget = QWidget()
                empty_widget.setFixedSize(250, 150)  # Taille approximative d'une carte
                empty_widget.setStyleSheet("background-color: transparent;")
                empty_widget.setProperty("project_subtype_bubble", True)
                grid_layout.addWidget(empty_widget, row, col + i)

        # Ajouter le conteneur au layout principal
        self.chat_layout.addWidget(project_subtype_container)
    
    def on_project_subtype_selected(
        self, subtype_id, project_type_id, technology_id, language_id
    ):
        """Gère la sélection d'un sous-type de projet"""
        # Désactiver et mettre en évidence les cartes
        for widget in self.findChildren(QWidget):
            if widget.property("project_subtype_bubble") and isinstance(
                widget, ProjectTypeCard
            ):
                if widget.property("project_subtype_id") == subtype_id:
                    widget.set_selected(True)
                else:
                    widget.setEnabled(False)
                    widget.set_selected(False)

        # Récupérer les informations du projet
        subtype_name = next(
            (
                pt["name"]
                for pt in [
                    {"id": "webapp", "name": "Application Web"},
                    {"id": "static", "name": "Site Statique"},
                    {"id": "api", "name": "API REST"},
                    {"id": "dashboard", "name": "Tableau de bord"},
                ]
                if pt["id"] == subtype_id
            ),
            "Type spécifique inconnu",
        )

        # Mise à jour des informations du projet
        self.selected_project_subtype = subtype_id

        # Afficher un message de confirmation
        project_type_name = next(
            (
                pt["name"]
                for pt in self.project_show.get_project_types()
                if pt["id"] == project_type_id
            ),
            "Type de projet inconnu",
        )
        lang_data = self.project_show.get_programming_languages_data(technology_id)
        language_name = next(
            (
                lang["name"]
                for lang in lang_data["languages"]
                if lang["id"] == language_id
            ),
            "",
        )
        technology_name = lang_data["technology_name"]
        
    def update_tree_view_and_select_folder(self, folder_path):
        """Met à jour la vue d'arborescence et sélectionne un dossier"""
        if not os.path.exists(folder_path):
            self.status_bar.showMessage(f"Le dossier {folder_path} n'existe pas", 3000)
            return

        # Utiliser la méthode du composant déporté pour mettre à jour l'arborescence
        self.file_tree.update_tree_view_and_select_folder(folder_path)    
    
    @Slot(str)
    def update_ia_bubble(self, text):
        self.current_ia_text += text
        # Vérifier si ia_bubble existe et est un ChatBubble
        if hasattr(self, "ia_bubble") and self.ia_bubble is not None:
            # Accéder directement au label stocké dans la bulle
            if hasattr(self.ia_bubble, "label"):
                self.ia_bubble.label.setText(self.current_ia_text)
        
    def extract_actions(self, ia_text):
        # Extraction JSON [ ... ] (fiabilise selon format de ton agent)
        import re, json

        m = re.search(r"Actions:\s*(\[.*?\])(?:\s|$)", ia_text, re.DOTALL)
        if m:
            try:
                actions_json = m.group(1)
                return json.loads(actions_json)
            except json.JSONDecodeError:
                return []
        return []

    def export_conversation(self):
        """Exporter la conversation actuelle dans un fichier"""
        ConversationManager.export_conversation(self)

    def clear_conversation(self):
        """Effacer la conversation actuelle"""
        ConversationManager.clear_conversation(self)

    def save_current_conversation(self):
        """Sauvegarder la conversation actuelle dans l'historique"""
        ConversationManager.save_current_conversation(self)

    def get_conversation_preview(self):
        """Obtenir un aperçu de la conversation pour l'historique"""
        return ConversationManager.get_conversation_preview(self)

    def show_history(self):
        """Afficher l'historique des conversations"""
        ConversationManager.show_history(self)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Utiliser la racine des lecteurs par défaut
    widget = ChatArboWidget()
    widget.show()
    sys.exit(app.exec())
