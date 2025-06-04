# ui_agent_ia.py
import sys
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QTreeView,
    QTextEdit,
    QPushButton,
    QFileSystemModel,
    QComboBox,
    QLabel,
    QFrame,
    QScrollArea,
    QSizePolicy,
    QPlainTextEdit,
    QProgressBar,
    QMenu,
    QFileDialog,
    QMessageBox,
    QTabWidget,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QGridLayout,
    QStatusBar,
)
from PySide6.QtCore import (
    Qt,
    QThread,
    Signal,
    Slot,
    QDateTime,
    QSize,
    QTimer,
    QPoint,
    QEvent,
    QUrl,
    QObject,
    QModelIndex,
)
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
)
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtGui import QKeyEvent
import httpx
import json
import os
import datetime
import uuid
import re
import shutil

# Import des classes depuis les fichiers séparés
from topic_card import TopicCard
from chat_bubble import ChatBubble
from interactive_chat_bubble import InteractiveChatBubble
from input_chat_bubble import InputChatBubble
from path_confirmation_buttons import PathConfirmationButtons
from action_confirmation_bubble import ActionConfirmationBubble
from action_types import (
    ActionType,
    ActionCategory,
    DirectoryAction,
    FileAction,
    ProjectAction,
    SystemAction,
    UIAction,
    DatabaseAction,
    NetworkAction,
    SecurityAction,
)
from project_creator import ProjectCreator
from project_creator_show import ProjectCreatorShow
# Import du FileTreeWidget depuis le module local
from project.structure.file_tree_widget import FileTreeWidget, FORBIDDEN_PATHS, SYSTEM_DRIVES
from project_types_widget import ProjectTypesWidget
from project_type_card import ProjectTypeCard
from top_bar_widget import TopBarWidget
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


class MessageInputField(QPlainTextEdit):
    enterPressed = Signal()

    def keyPressEvent(self, event):
        # Si la touche Entrée est pressée sans modificateur Shift, envoyer le message
        if event.key() == Qt.Key_Return and not event.modifiers() & Qt.ShiftModifier:
            self.enterPressed.emit()
        else:
            # Sinon, comportement normal
            super().keyPressEvent(event)


# Import des classes depuis les fichiers séparés
from project.structure.stream_thread import StreamThread
from project.structure.conversation_manager import ConversationManager
from project.structure.connection_worker import ConnectionWorker


class ChatArboWidget(QWidget):
    def __init__(self, root_path=None):
        super().__init__()
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
        self.file_tree.item_double_clicked.connect(self.on_tree_item_double_clicked)
        self.file_tree.search_text_changed.connect(self.on_tree_search_changed)

        # Widget d'arborescence prêt à être utilisé
        tree_widget = self.file_tree

        # Chat Area
        chat_panel = QVBoxLayout()

        # Barre supérieure avec le composant TopBarWidget
        self.top_bar = TopBarWidget()
        # Connexion des signaux aux méthodes appropriées
        self.top_bar.exportClicked.connect(self.export_conversation)
        self.top_bar.clearClicked.connect(self.clear_conversation)
        self.top_bar.skeletonClicked.connect(self.start_app_skeleton_wizard)
        self.top_bar.historyClicked.connect(self.show_history)
        self.top_bar.infoClicked.connect(self.show_project_info)
        self.top_bar.checkConnectionClicked.connect(self.check_server_connection)
        self.top_bar.modelChanged.connect(self.on_model_changed)

        chat_panel.addWidget(self.top_bar)

        # Séparateur horizontal
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #e0e0e0; margin: 5px 0;")
        chat_panel.addWidget(separator)

        # Scrollable chat bubbles
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_widget)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.scroll.setWidget(self.chat_widget)
        chat_panel.addWidget(self.scroll, 4)

        # Zone de saisie avec bouton d'envoi à droite
        input_layout = QHBoxLayout()

        # Zone de saisie sur une seule ligne avec hauteur réduite et gestion de la touche Entrée
        self.user_input = MessageInputField()
        self.user_input.setFixedHeight(40)  # Hauteur réduite
        self.user_input.setPlaceholderText("Votre message...")
        self.user_input.setVerticalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )  # Désactiver la barre de défilement verticale
        self.user_input.setLineWrapMode(
            QPlainTextEdit.NoWrap
        )  # Désactiver le retour à la ligne automatique
        self.user_input.enterPressed.connect(
            self.send_message
        )  # Connecter le signal enterPressed à send_message

        # Style avec bordure verte lors du focus
        self.user_input.setStyleSheet(
            """
            QPlainTextEdit {
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 4px;
                background-color: #2a2a2a;
                color: #e0e0e0;
            }
            QPlainTextEdit:focus {
                border: 2px solid #4CAF50;
            }
        """
        )
        input_layout.addWidget(
            self.user_input, 1
        )  # Stretch factor 1 pour prendre l'espace disponible

        # Bouton d'envoi à droite avec icône verte
        self.send_btn = QPushButton()
        self.send_btn.setFixedSize(40, 40)  # Carré pour un design plus moderne
        send_pixmap = get_svg_icon("send-horizontal", size=24, color="#AAA")
        if send_pixmap:
            self.send_btn.setIcon(QIcon(send_pixmap))
        self.send_btn.setIconSize(QSize(22, 22))

        # Style du bouton d'envoi avec fond transparent et effet de survol pastel
        self.send_btn.setStyleSheet(
            """
            QPushButton {
                background-color: transparent;
                border-radius: 20px;
                border: 1px solid #AAA;
            }
            QPushButton:hover {
                background-color: rgba(76, 175, 80, 0.15); /* Vert pastel transparent */
                border: 2px solid #66BB6A;
            }
            QPushButton:pressed {
                background-color: rgba(76, 175, 80, 0.3);
                border: 2px solid #388E3C;
            }
        """
        )

        input_layout.addWidget(self.send_btn)
        chat_panel.addLayout(input_layout)

        # Les boutons d'action ont été déplacés dans la barre supérieure

        # Le bouton d'envoi a été déplacé à droite de la zone de saisie

        chat_right = QWidget()
        chat_right.setLayout(chat_panel)

        splitter.addWidget(
            tree_widget
        )  # Utiliser le widget contenant l'arborescence et la recherche
        splitter.addWidget(chat_right)
        splitter.setSizes([330, 900])

        main_layout = QHBoxLayout(self)
        main_layout.addWidget(splitter)

        self.send_btn.clicked.connect(self.send_message)
        # Le signal clicked est déjà connecté via le composant déporté dans le constructeur

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
        self.add_chat_bubble(welcome_message, is_user=False)

        # Style global moderne et professionnel
        self.setStyleSheet(
            """
            QWidget {
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: 12pt;
                color: #e0e0e0;
                background-color: #2d2d2d;
            }
            QSplitter::handle {
                background: #555555;
            }
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4CAF50, stop:1 #388E3C);
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #66BB6A, stop:1 #43A047);
            }
            QPushButton:pressed {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #388E3C, stop:1 #2E7D32);
            }
            QComboBox {
                background-color: #2a2a2a;
                color: #e0e0e0;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 4px;
                font-weight: bold;
            }
            QComboBox:hover {
                border: 1px solid #4CAF50;
            }
            QComboBox:focus {
                border: 2px solid #4CAF50;
            }
            QComboBox QAbstractItemView {
                background-color: #2a2a2a;
                color: #e0e0e0;
                selection-background-color: #4CAF50;
                selection-color: white;
                border: 1px solid #555555;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #4CAF50;
                color: white;
            }
            
            QPlainTextEdit, QTextEdit {
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 4px;
                background-color: #2a2a2a;
                color: #e0e0e0;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QTreeView {
                background-color: #2a2a2a;
                alternate-background-color: #333333;
                border: 1px solid #444444;
                color: #e0e0e0;
            }
            QTreeView::item:selected {
                background-color: #4CAF50;
                color: white;
            }
        """
        )

    def on_tree_item_clicked(self, path, is_dir):
        """Gère le clic sur un élément de l'arborescence"""
        self.clear_bubbles()
        # Stocker le chemin sélectionné pour la création de projet
        self.selected_project_path = path
        # Mettre à jour également path_root pour la génération de squelette d'application
        self.path_root = path

        # Afficher le chemin sélectionné dans la barre d'état
        print(f"Chemin sélectionné: {os.path.basename(path)}")
        # Utiliser la nouvelle méthode pour afficher le chemin sélectionné
        self.top_bar.update_selected_path(path, is_dir)

        # Rétablir le message normal après 3 secondes
        # QTimer.singleShot(3000, self.check_server_connection)

        # Si on attend la sélection d'un dossier pour la création de projet
        if hasattr(self, "wait_for_path") and self.wait_for_path:
            # Mettre en évidence l'arborescence avec un timer pour éviter l'exécution immédiate
            QTimer.singleShot(100, self.file_tree.highlight_tree_view)

            # Confirmer que le dossier a bien été sélectionné
            self.add_chat_bubble(
                f"<span style='color:#FFFFFF'>Le dossier <b>{os.path.basename(path)}</b> a été sélectionné pour votre projet.</span>",
                is_user=False,
                icon_name="folder",
                icon_color="#4CAF50",
                icon_size=24,
                word_wrap=False,
            )

            # Afficher les types de projets disponibles
            self.display_project_types()

            # Marquer que nous avons géré l'attente du chemin
            self.wait_for_path = False
        else:
            # Pour les autres cas de clic sur le TreeView, on ne fait rien de spécial
            pass

    def on_tree_item_double_clicked(self, path, is_dir):
        """Gère le double-clic sur un élément de l'arborescence"""
        if not is_dir:
            # Afficher le contenu du fichier
            self.display_file_content(path)

    def display_file_content(self, file_path):
        """Affiche le contenu d'un fichier dans une bulle de chat"""
        try:
            # Vérifier si le fichier existe
            if not os.path.isfile(file_path):
                self.add_chat_bubble(
                    f"Le fichier n'existe pas: {file_path}", is_user=False
                )
                return

            # Déterminer le type de fichier
            _, ext = os.path.splitext(file_path)

            # Extensions de fichiers texte courants
            text_extensions = [
                ".txt",
                ".py",
                ".js",
                ".html",
                ".css",
                ".json",
                ".xml",
                ".md",
                ".log",
                ".csv",
                ".h",
                ".c",
                ".cpp",
            ]

            # Taille maximale pour l'affichage (pour éviter de charger des fichiers volumineux)
            max_size = 500 * 1024  # 500 Ko

            if os.path.getsize(file_path) > max_size:
                self.add_chat_bubble(
                    f"<b>Fichier trop volumineux</b><br>Le fichier '{os.path.basename(file_path)}' est trop grand pour être affiché (> 500 Ko).",
                    is_user=False,
                )
                return

            if ext.lower() in text_extensions:
                # Lire le contenu du fichier texte
                with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()

                # Ajouter une bulle avec le contenu du fichier
                file_name = os.path.basename(file_path)
                self.add_chat_bubble(
                    f"<b>Fichier: {file_name}</b><br><pre style='background-color: #f5f5f5; padding: 10px; border-radius: 5px;'>{content}</pre>",
                    is_user=False,
                    word_wrap=True,
                )
            else:
                # Pour les fichiers non texte, afficher un message
                self.add_chat_bubble(
                    f"<b>Fichier non texte</b><br>Le fichier '{os.path.basename(file_path)}' ({ext}) n'est pas un fichier texte et ne peut pas être affiché.",
                    is_user=False,
                )
        except Exception as e:
            self.add_chat_bubble(
                f"<b>Erreur lors de la lecture du fichier</b><br>{str(e)}",
                is_user=False,
            )

    def update_preview(self, selected, deselected):
        """Met à jour l'aperçu du fichier sélectionné dans l'arborescence"""
        # Récupérer les indices sélectionnés
        indices = selected.indexes()

        if not indices:
            # Aucune sélection, effacer l'aperçu
            self.preview.clear()
            return

        # Prendre le premier indice sélectionné (colonne 0 = nom)
        index = indices[0]

        # Récupérer le chemin du fichier sélectionné
        path = self.file_tree.model.filePath(index)

        # Vérifier si c'est un fichier
        if os.path.isfile(path):
            try:
                # Déterminer le type de fichier
                _, ext = os.path.splitext(path)

                # Taille maximale pour l'aperçu (pour éviter de charger des fichiers volumineux)
                max_size = 100 * 1024  # 100 Ko

                if os.path.getsize(path) > max_size:
                    self.preview.setPlainText(
                        f"Le fichier est trop volumineux pour un aperçu (> 100 Ko).\nChemin: {path}"
                    )
                    return

                # Extensions de fichiers texte courants
                text_extensions = [
                    ".txt",
                    ".py",
                    ".js",
                    ".html",
                    ".css",
                    ".json",
                    ".xml",
                    ".md",
                    ".log",
                    ".csv",
                    ".h",
                    ".c",
                    ".cpp",
                ]

                if ext.lower() in text_extensions:
                    # Lire le contenu du fichier texte
                    with open(path, "r", encoding="utf-8", errors="replace") as f:
                        content = f.read()

                    # Afficher le contenu dans l'aperçu
                    self.preview.setPlainText(content)
                else:
                    # Pour les fichiers non texte, afficher un message
                    self.preview.setPlainText(
                        f"Aperçu non disponible pour ce type de fichier ({ext}).\nChemin: {path}"
                    )
            except Exception as e:
                self.preview.setPlainText(
                    f"Erreur lors de la lecture du fichier: {str(e)}\nChemin: {path}"
                )
        else:
            # Pour les dossiers, afficher des informations sur le dossier
            try:
                # Compter les fichiers et sous-dossiers
                files = []
                dirs = []

                try:
                    with os.scandir(path) as entries:
                        for entry in entries:
                            if entry.is_file():
                                files.append(entry.name)
                            elif entry.is_dir():
                                dirs.append(entry.name)
                except PermissionError:
                    self.preview.setPlainText(
                        f"Accès refusé au dossier.\nChemin: {path}"
                    )
                    return

                # Préparer le message à afficher
                message = f"Dossier: {path}\n\n"
                message += f"Contient {len(files)} fichier(s) et {len(dirs)} sous-dossier(s)\n\n"

                if dirs:
                    message += "Sous-dossiers:\n"
                    for d in sorted(dirs)[:10]:  # Limiter à 10 dossiers
                        message += f"- {d}\n"
                    if len(dirs) > 10:
                        message += f"... et {len(dirs) - 10} autres\n"
                    message += "\n"

                if files:
                    message += "Fichiers:\n"
                    for f in sorted(files)[:10]:  # Limiter à 10 fichiers
                        message += f"- {f}\n"
                    if len(files) > 10:
                        message += f"... et {len(files) - 10} autres\n"

                self.preview.setPlainText(message)
            except Exception as e:
                self.preview.setPlainText(
                    f"Erreur lors de la lecture du dossier: {str(e)}\nChemin: {path}"
                )

        # Si on attend la sélection d'un dossier pour la création de projet
        if self.wait_for_path:
            # Afficher le nom du chemin en entier dans un bubblechat
            self.add_chat_bubble(
                f"<b>Chemin sélectionné :</b> {path}{self.project_name}",
                is_user=True,
                word_wrap=False,
            )

            # Stocker le chemin pour une utilisation ultérieure
            self.wait_for_path = False

        self.wait_for_path = False

    # La seconde méthode reset_status_message a également été supprimée
    # car elle faisait double emploi avec top_bar.update_connection_status

    def clear_project_type_bubbles(self):
        """Efface les bulles de types de projets précédentes pour éviter les doublons"""
        # Parcourir tous les widgets dans le chat_layout et supprimer ceux qui contiennent des types de projets
        if hasattr(self, "chat_layout"):
            for i in range(self.chat_layout.count()):
                widget = self.chat_layout.itemAt(i).widget()
                if (
                    widget
                    and hasattr(widget, "project_type_bubble")
                    and widget.project_type_bubble
                ):
                    widget.setVisible(False)
                    widget.deleteLater()

    
    def display_project_types(self):
        """Affiche les types de projets disponibles en grille de 4 colonnes avec ProjectTypeCard"""

        # Initialiser ProjectCreatorShow si ce n'est pas déjà fait
        if not hasattr(self, "project_show") or self.project_show is None:
            self.project_show = ProjectCreatorShow()
            self.project_show.technology_selected.connect(self.on_technology_selected)
            self.project_show.app_type_selected.connect(self.on_app_type_selected)
            self.project_show.feature_selected.connect(self.on_feature_selected)
            self.project_show.project_creation_requested.connect(
                self.on_project_creation_requested
            )

        # Effacer les bulles précédentes
        self.clear_project_type_bubbles()

        # Obtenir les données des types de projets
        project_types = self.project_show.get_project_types_data()

        # Créer un message pour introduire les types de projets
        intro_bubble = self.add_chat_bubble(
            "Sélectionnez un type de projet :",
            is_user=False,
            word_wrap=False,
            icon_name="hand-helping",
            icon_color="#FFFFFF",
            icon_size=24,
        )
        intro_bubble.setProperty("project_type_bubble", True)

        # Créer un conteneur pour la grille
        grid_container = QWidget()
        grid_container.setStyleSheet("background-color: transparent;")
        grid_container.setProperty("project_type_bubble", True)
        grid_layout = QGridLayout(grid_container)
        grid_layout.setContentsMargins(8, 8, 8, 8)
        grid_layout.setSpacing(10)
        grid_layout.setHorizontalSpacing(
            15
        )  # Plus d'espace horizontal entre les colonnes

        # Ajouter le conteneur au chat
        self.chat_layout.addWidget(grid_container)

        # Créer les cartes de types de projet pour la grille
        num_columns = 4  # Nombre de colonnes dans la grille (2 colonnes pour des cartes plus larges)
        for i, project_type in enumerate(project_types):
            print(
                f"Traitement du type de projet {i+1}/{len(project_types)}: {project_type['name']}"
            )

            # Calculer la position dans la grille (row, column)
            row = i // num_columns
            col = i % num_columns

            try:
                # Créer une carte pour le type de projet
                card = ProjectTypeCard(project_type)

                # Stocker l'ID du type de projet dans la propriété de la carte
                card.setProperty("project_type_id", project_type["id"])

                # Connecter le signal de clic de la carte
                # Utiliser une fonction spécifique pour éviter les problèmes de portée avec lambda
                def create_project_type_click_handler(pt_id):
                    return lambda: self.on_project_type_selected(pt_id)

                card.clicked.connect(
                    create_project_type_click_handler(project_type["id"])
                )

                # Stocker l'ID du type de projet dans la propriété de la carte pour le nettoyage
                card.setProperty("project_type_bubble", True)

                # Ajouter la carte à la grille
                grid_layout.addWidget(card, row, col)
            except Exception as e:
                pass

        # Ajouter des widgets vides pour compléter la dernière ligne et maintenir l'alignement à gauche
        total_items = len(project_types)
        if total_items % num_columns != 0:
            # Calculer combien de widgets vides il faut ajouter
            empty_slots = num_columns - (total_items % num_columns)
            last_row = total_items // num_columns
            # Ajouter les widgets vides
            for i in range(empty_slots):
                empty_widget = QWidget()
                empty_widget.setFixedSize(200, 150)  # Taille approximative d'une carte
                empty_widget.setStyleSheet("background-color: transparent;")
                empty_widget.setProperty("project_type_bubble", True)
                grid_layout.addWidget(
                    empty_widget, last_row, (total_items % num_columns) + i
                )

    def on_project_type_selected(self, project_type_id):
        """Appelé lorsqu'un type de projet est sélectionné"""
        # Appliquer un effet visuel aux cartes pour montrer celle qui est sélectionnée
        # et désactiver les autres
        for widget in self.findChildren(QWidget):
            if widget.property("project_type_bubble") and isinstance(
                widget, ProjectTypeCard
            ):
                if widget.property("project_type_id") == project_type_id:
                    # Mettre en évidence la carte sélectionnée
                    widget.set_selected(True)
                else:
                    # Désactiver les autres cartes
                    widget.setEnabled(False)
                    widget.set_selected(False)

        # Vérifier si ProjectCreatorShow est initialisé
        if not hasattr(self, "project_show"):
            self.project_show = ProjectCreatorShow()
            # Connecter les signaux
            self.project_show.technology_selected.connect(self.on_technology_selected)
            self.project_show.app_type_selected.connect(self.on_app_type_selected)
            self.project_show.feature_selected.connect(self.on_feature_selected)
            self.project_show.project_creation_requested.connect(
                self.on_project_creation_requested
            )

        # Stocker le type de projet sélectionné
        self.selected_project_type = project_type_id

        # Utiliser ProjectCreatorShow pour sélectionner le type de projet
        technologies = self.project_show.select_project_type(project_type_id)

        # Effacer les messages précédents pour éviter les doublons
        self.clear_bubbles()


        # Afficher les technologies disponibles pour ce type de projet
        self.display_technologies_for_project_type(project_type_id)

    def display_technologies_for_project_type(self, project_type_id):
        """Affiche les technologies disponibles pour un type de projet en utilisant ProjectTypeCard"""
        # Effacer les bulles de technologies précédentes
        self.clear_bubbles()
        
        # Ajouter un bouton de retour pour revenir à la sélection des types de projets
        from project.structure.back_button import BackButton
        back_button = BackButton("« Retour aux types de projets")
        back_button.clicked.connect(self.handle_back_to_project_types)

        # Ajouter le bouton au layout
        back_container = QWidget()
        back_layout = QHBoxLayout(back_container)
        back_layout.setContentsMargins(10, 5, 10, 5)
        back_layout.addWidget(back_button)
        back_layout.addStretch(1)

        back_container.setProperty("tech_bubble", True)
        self.chat_layout.addWidget(back_container)

        # Obtenir les données des technologies
        tech_data = self.project_show.get_technologies_data(project_type_id)
        technologies = tech_data["technologies"]
        project_type_name = tech_data["project_type_name"]
        project_color = tech_data["project_color"]
        
        # Créer un message pour introduire les technologies
        intro_bubble = self.add_chat_bubble(
            f"Sélectionnez une technologie pour {project_type_name} :",
            is_user=False,
            word_wrap=False,
            icon_name="hand-helping",
            icon_color="#FFFFFF",
            icon_size=24,
        )
        intro_bubble.setProperty("tech_bubble", True)

        # Créer un conteneur pour la grille
        grid_container = QWidget()
        grid_container.setStyleSheet("background-color: transparent;")
        grid_container.setProperty("tech_bubble", True)
        grid_layout = QGridLayout(grid_container)
        grid_layout.setContentsMargins(8, 8, 8, 8)
        grid_layout.setSpacing(10)
        grid_layout.setHorizontalSpacing(
            15
        )  # Plus d'espace horizontal entre les colonnes

        # Ajouter le conteneur au chat
        self.chat_layout.addWidget(grid_container)

        # Créer les cartes de technologies pour la grille
        num_columns = 4  # Nombre de colonnes dans la grille
        for i, tech in enumerate(technologies):
            # Calculer la position dans la grille (row, column)
            row = i // num_columns
            col = i % num_columns

            try:
                # Adapter la technologie au format attendu par ProjectTypeCard
                tech_data_for_card = {
                    "id": tech["id"],
                    "name": tech["name"],
                    "description": tech.get("description", ""),
                    "icon": tech.get("icon", "code"),
                    "color": project_color,  # Utiliser la couleur du type de projet parent
                }

                # Créer une carte pour la technologie
                card = ProjectTypeCard(tech_data_for_card)

                # Stocker les ID dans les propriétés de la carte
                card.setProperty("tech_id", tech["id"])
                card.setProperty("project_type_id", project_type_id)

                # Connecter le signal de clic de la carte à la méthode de sélection de technologie
                # Utiliser une fonction spécifique pour éviter les problèmes de portée avec lambda
                def create_tech_click_handler(tech_id, pt_id):
                    return lambda: self.on_technology_selected_with_project_type(
                        tech_id, pt_id
                    )

                card.clicked.connect(
                    create_tech_click_handler(tech["id"], project_type_id)
                )

                # Stocker les ID pour le nettoyage
                card.setProperty("tech_bubble", True)
                card.setProperty("tech_id", tech["id"])
                card.setProperty("project_type_id", project_type_id)

                # Ajouter la carte à la grille
                grid_layout.addWidget(card, row, col)

                print(f"Carte de technologie ajoutée: {tech['name']}")
            except Exception as e:
                print(
                    f"[ERREUR] Échec de création de la carte pour {tech['name']}: {str(e)}"
                )

        # Ajouter des widgets vides pour compléter la dernière ligne et maintenir l'alignement à gauche
        total_items = len(technologies)
        if total_items % num_columns != 0:
            # Calculer combien de widgets vides il faut ajouter
            empty_slots = num_columns - (total_items % num_columns)
            last_row = total_items // num_columns
            # Ajouter les widgets vides
            for i in range(empty_slots):
                empty_widget = QWidget()
                empty_widget.setFixedSize(200, 150)  # Taille approximative d'une carte
                empty_widget.setStyleSheet("background-color: transparent;")
                empty_widget.setProperty("tech_bubble", True)
                grid_layout.addWidget(
                    empty_widget, last_row, (total_items % num_columns) + i
                )

        # Code obsolète supprimé

    def on_technology_selected_with_project_type(self, tech_id, project_type_id):
        """Appelé lorsqu'une carte de technologie est cliquée"""
        # Appliquer un effet visuel aux cartes pour montrer celle qui est sélectionnée
        # et désactiver les autres
        for widget in self.findChildren(QWidget):
            if widget.property("tech_bubble") and isinstance(
                widget, ProjectTypeCard
            ):
                if widget.property("tech_id") == tech_id:
                    # Mettre en évidence la carte sélectionnée
                    widget.set_selected(True)
                else:
                    # Désactiver les autres cartes
                    widget.setEnabled(False)
                    widget.set_selected(False)

        print(
            f"Carte de technologie cliquée: {tech_id} pour le type de projet: {project_type_id}"
        )
        self.selected_project_type = project_type_id
        self.selected_technology = tech_id

        # Trouver les noms du type de projet et de la technologie
        project_type_name = next(
            (
                pt["name"]
                for pt in self.project_show.get_project_types()
                if pt["id"] == project_type_id
            ),
            "",
        )

        # Continuer avec le traitement de la sélection de technologie
        self.on_technology_selected(tech_id)

    def on_technology_card_clicked(self, project_type_id, technology_id):
        """Méthode de compatibilité pour l'ancienne implémentation"""
        print(
            f"[DEPRECATED] Utiliser on_technology_selected_with_project_type à la place"
        )
        self.on_technology_selected_with_project_type(technology_id, project_type_id)
        project_type_name = next(
            (
                pt["name"]
                for pt in self.project_show.get_project_types()
                if pt["id"] == project_type_id
            ),
            "Type de projet inconnu", # Valeur par défaut si non trouvé
        )
        technology_name = next(
            (
                tech["name"]
                for tech in self.project_show.get_technologies_for_project_type(
                    project_type_id
                )
                if tech["id"] == technology_id
            ),
            "",
        )
        print(
            f"Nom du type de projet: {project_type_name}, Nom de la technologie: {technology_name}"
        )

        # Afficher un message de confirmation
        self.add_chat_bubble(
            f"<b>Type de projet :</b> {project_type_name}<br><b>Technologie :</b> {technology_name}<br><b>Chemin :</b> {self.path_root}",
            is_user=True,
            word_wrap=True,
            icon_name="check",
            icon_color="#4CAF50",
        )

        # Demander confirmation pour créer le projet
        self.add_chat_bubble(
            "Créer le projet avec les paramètres sélectionnés ?",
            is_user=False,
            word_wrap=True,
            icon_name="help-circle",
            icon_color="#2196F3",
        )

        # Ajouter des boutons de confirmation
        self.add_action_confirmation_bubble(
            "Créer le projet",
            "Annuler",
            lambda: self.create_app_skeleton(project_type_id, technology_id),
            lambda: self.add_chat_bubble(
                "Création du projet annulée",
                is_user=False,
                icon_name="x",
                icon_color="#F44336",
            ),
        )

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

    # La méthode reset_status_message a été supprimée car elle faisait double emploi avec check_server_connection

    def check_server_connection(self):
        """Démarre un thread pour vérifier la connexion au serveur sans bloquer l'UI"""
        # Créer un thread pour exécuter la vérification en arrière-plan
        self.connection_thread = QThread()
        self.connection_worker = ConnectionWorker("http://localhost:8000/health")
        self.connection_worker.moveToThread(self.connection_thread)
        
        # Connecter les signaux
        self.connection_thread.started.connect(self.connection_worker.check_connection)
        self.connection_worker.connection_result.connect(self.handle_connection_result)
        self.connection_worker.finished.connect(self.connection_thread.quit)
        self.connection_worker.finished.connect(self.connection_worker.deleteLater)
        self.connection_thread.finished.connect(self.connection_thread.deleteLater)
        
        # Démarrer le thread
        self.connection_thread.start()
    
    def handle_connection_result(self, is_connected, message):
        """Gère le résultat de la vérification de connexion"""
        self.server_connected = is_connected
        try:
            if hasattr(self, 'top_bar') and self.top_bar:
                self.top_bar.update_connection_status(is_connected, message)
        except RuntimeError:
            # L'objet a déjà été supprimé, ignorer silencieusement
            print("Impossible de mettre à jour le statut de connexion : top_bar a été supprimé")
        except Exception as e:
            print(f"Erreur lors de la mise à jour du statut de connexion : {e}")



    @Slot()
    def send_message(
        self,
        message=None,
        word_wrap=True,
        icon_name=None,
        icon_color=None,
        icon_size=20,
    ):
        user_text = message or self.user_input.toPlainText().strip()
        self.wait_for_path = False
        self.user_input.clear()

        # Ajout bulle utilisateur
        self.add_chat_bubble(
            user_text,
            is_user=True,
            word_wrap=word_wrap,
            icon_name=icon_name,
            icon_color=icon_color,
            icon_size=icon_size,
        )

        # Convertir le texte en minuscules pour la comparaison
        text_lower = user_text.lower()

        # Déterminer l'action à effectuer en fonction du message
        action_category = None
        action = None

        # Définir les patterns pour les différentes actions
        # Format: (regex_pattern, category, action)
        action_patterns = [
            # Patterns pour les projets
            (r"créer\s+(le|un)\s+projet", ActionCategory.PROJECT, ProjectAction.CREATE),
            (
                r"générer\s+(un|le)\s+projet",
                ActionCategory.PROJECT,
                ProjectAction.CREATE,
            ),
            (r"nouveau\s+projet", ActionCategory.PROJECT, ProjectAction.CREATE),
            (
                r"supprimer\s+(le|un)\s+projet",
                ActionCategory.PROJECT,
                ProjectAction.DELETE,
            ),
            (r"ouvrir\s+(le|un)\s+projet", ActionCategory.PROJECT, ProjectAction.OPEN),
            # Patterns pour les répertoires
            (
                r"créer\s+(un|le)\s+(répertoire|dossier)",
                ActionCategory.DIRECTORY,
                DirectoryAction.CREATE,
            ),
            (
                r"nouveau\s+(répertoire|dossier)",
                ActionCategory.DIRECTORY,
                DirectoryAction.CREATE,
            ),
            (
                r"supprimer\s+(un|le)\s+(répertoire|dossier)",
                ActionCategory.DIRECTORY,
                DirectoryAction.DELETE,
            ),
            (
                r"renommer\s+(un|le)\s+(répertoire|dossier)",
                ActionCategory.DIRECTORY,
                DirectoryAction.RENAME,
            ),
            (
                r"déplacer\s+(un|le)\s+(répertoire|dossier)",
                ActionCategory.DIRECTORY,
                DirectoryAction.MOVE,
            ),
            # Patterns pour les fichiers
            (r"créer\s+(un|le)\s+fichier", ActionCategory.FILE, FileAction.CREATE),
            (r"nouveau\s+fichier", ActionCategory.FILE, FileAction.CREATE),
            (r"supprimer\s+(un|le)\s+fichier", ActionCategory.FILE, FileAction.DELETE),
            (r"ouvrir\s+(un|le)\s+fichier", ActionCategory.FILE, FileAction.OPEN),
            (r"éditer\s+(un|le)\s+fichier", ActionCategory.FILE, FileAction.EDIT),
            (r"modifier\s+(un|le)\s+fichier", ActionCategory.FILE, FileAction.EDIT),
            # Patterns pour l'aide
            (r"aide|help", ActionCategory.UI, UIAction.SHOW),
        ]

        # Vérifier chaque pattern
        import re

        for pattern, category, act in action_patterns:
            if re.search(pattern, text_lower):
                action_category = category
                action = act
                break

        # Traiter les cas spéciaux
        if (
            action_category == ActionCategory.UI
            and action == UIAction.SHOW
            and ("aide" in text_lower or "help" in text_lower)
        ):
            # Afficher les cartes de rubriques sans message de salutation
            self.add_topic_cards_bubble()
            return

        # Exécuter l'action si elle a été identifiée
        if action_category and action:
            # Récupérer l'icône pour l'action
            action_icon, action_color = ActionType.get_icon_for_action(
                action_category, action
            )

            # Traiter l'action en fonction de sa catégorie
            if (
                action_category == ActionCategory.PROJECT
                and action == ProjectAction.CREATE
            ):
                # Récupérer le chemin racine pour la création du projet
                project_path = self.get_project_root_path()
                if not project_path:
                    self.add_chat_bubble(
                        "<span style='color:orange'>Veuillez sélectionner un dossier pour la création du projet.</span>",
                        is_user=False,
                        word_wrap=True,
                        icon_name="alert-triangle",
                        icon_color="#FFA500",
                    )
                    return

                # Ajouter le chemin au message pour le serveur IA
                user_text += f"\nChemin du projet: {project_path}"

                # Créer directement le projet si le message est "Créer le projet avec le chemin sélectionné"
                if "avec le chemin sélectionné" in text_lower:
                    self.create_app_skeleton()
                    return

            # Pour les autres actions, on pourrait ajouter d'autres cas spécifiques ici
            # ...

        # Si aucune action spécifique n'a été identifiée ou si l'action nécessite l'IA
        # Vérifier si le message concerne la création d'un projet (cas général)
        if (
            ("créer" in text_lower or "générer" in text_lower)
            and (
                "projet" in text_lower
                or "structure" in text_lower
                or "dossier" in text_lower
            )
            and not action
        ):  # Seulement si aucune action spécifique n'a été identifiée
            # Récupérer le chemin racine pour la création du projet
            project_path = self.get_project_root_path()
            if not project_path:
                self.add_chat_bubble(
                    "<span style='color:orange'>Veuillez sélectionner un dossier pour la création du projet.</span>",
                    is_user=False,
                    word_wrap=True,
                    icon_name="alert-triangle",
                    icon_color="#FFA500",
                )
                return

            # Ajouter le chemin au message pour le serveur IA
            user_text += f"\nChemin du projet: {project_path}"

        # Vérifier si le serveur IA est en cours d'exécution
        if not self.check_server_connection():
            # Démarrer le serveur IA s'il n'est pas en cours d'exécution
            self.add_chat_bubble(
                "<span style='color:orange'>Tentative de démarrage du serveur IA...</span>",
                is_user=False,
                icon_name="server",
                icon_color="#FFA500",
            )
            try:
                # Essayer de démarrer le serveur en arrière-plan (à adapter selon votre configuration)
                os.system(
                    'start cmd /c "cd {} && python agent_ia_stream.py"'.format(
                        os.path.dirname(os.path.abspath(__file__))
                    )
                )
                # Attendre un peu que le serveur démarre
                import time

                time.sleep(2)

                # Vérifier à nouveau la connexion
                if not self.check_server_connection():
                    self.add_chat_bubble(
                        "<span style='color:red'>⚠️ Impossible de démarrer le serveur IA.</span>",
                        is_user=False,
                        icon_name="server-off",
                        icon_color="#FF0000",
                    )
                    return
            except Exception as e:
                self.add_chat_bubble(
                    f"<span style='color:red'>⚠️ Erreur: {str(e)}</span>",
                    is_user=False,
                    icon_name="alert-circle",
                    icon_color="#FF0000",
                )
                return

        # Continuer avec le traitement normal
        self.add_chat_bubble(
            "⏳ L'IA réfléchit...",
            is_user=False,
            icon_name="brain",
            icon_color="#FFFFFF",
        )
        model = self.model_choice.currentText().lower()
        self.stream_thread = StreamThread(user_text, model)
        self.stream_thread.message.connect(self.update_ia_bubble)
        self.stream_thread.finished.connect(self.handle_ia_finished)
        self.current_ia_text = ""
        self.stream_thread.start()

    def add_chat_bubble(
        self,
        text,
        is_user=False,
        word_wrap=True,
        icon_name=None,
        icon_color="#FFFFFF",
        icon_size=20,
    ):
        """Ajoute une bulle de chat au fil de discussion

        Args:
            text (str): Le texte à afficher dans la bulle
            is_user (bool, optional): True si c'est un message de l'utilisateur. Defaults to False.
            word_wrap (bool, optional): True pour activer le retour à la ligne automatique. Defaults to True.
            icon_name (str, optional): Nom de l'icône SVG à afficher (sans extension). Defaults to None.
            icon_color (str, optional): Couleur de l'icône au format CSS (ex: '#FFFFFF'). Defaults to None.
            icon_size (int, optional): Taille de l'icône en pixels. Defaults to 20.

        Returns:
            QWidget: Le conteneur de la bulle de chat
        """
        # Créer la bulle avec ou sans icône
        if icon_name:  # Les icônes sont uniquement pour les messages de l'IA
            bubble = ChatBubble(
                text, is_user, word_wrap, icon_name, icon_color, icon_size
            )
        else:
            bubble = ChatBubble(text, is_user, word_wrap)

        # Créer un layout horizontal pour aligner la bulle
        bubble_layout = QHBoxLayout()
        bubble_layout.setContentsMargins(0, 0, 0, 0)

        # Ajouter des espaces pour aligner la bulle à gauche ou à droite
        if is_user:
            bubble_layout.addStretch(1)  # Espace à gauche pour aligner à droite
            bubble_layout.addWidget(bubble)
        else:
            bubble_layout.addWidget(bubble)
            bubble_layout.addStretch(1)  # Espace à droite pour aligner à gauche

        # Ajouter le layout horizontal au chat
        bubble_container = QWidget()
        bubble_container.setLayout(bubble_layout)
        self.chat_layout.addWidget(bubble_container)

        # Stocker la référence pour le streaming
        if not is_user:
            self.ia_bubble = bubble  # Pour stream

        # Ajouter le message à la conversation courante
        message_data = {
            "text": text,
            "is_user": is_user,
            "timestamp": datetime.datetime.now().isoformat(),
            "icon_name": icon_name,  # Stocker l'information sur l'icône
        }
        self.current_conversation.append(message_data)

        # Faire défiler vers le bas après un court délai pour s'assurer que le widget est complètement rendu
        QTimer.singleShot(50, self.scroll_to_bottom)

        return bubble_container

    def add_topic_cards_bubble(self):
        """Affiche des bulles individuelles pour chaque rubrique d'aide"""
        # Définir les rubriques disponibles
        topics = [
            {
                "title": "Création de projet",
                "description": "Créer un nouveau squelette de projet avec différentes technologies",
                "icon": "code",
            },
            {
                "title": "Navigation fichiers",
                "description": "Explorer et interagir avec les fichiers de votre projet",
                "icon": "folder-code",
            },
            {
                "title": "Aide au codage",
                "description": "Obtenir de l'aide pour résoudre des problèmes de code",
                "icon": "circle-help",
            },
            {
                "title": "Suggestions d'amélioration",
                "description": "Recevoir des suggestions pour améliorer votre code",
                "icon": "brain",
            },
            {
                "title": "Documentation",
                "description": "Générer de la documentation pour votre code",
                "icon": "file-text",
            },
        ]

        # Ajouter un titre pour les options d'aide
        title_bubble = ChatBubble(
            "<b>Comment puis-je vous aider aujourd'hui ?</b>", is_user=False
        )
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.addWidget(title_bubble)
        title_layout.addStretch(1)  # Espace à droite pour aligner à gauche

        title_container = QWidget()
        title_container.setLayout(title_layout)
        self.chat_layout.addWidget(title_container)

        # Créer un conteneur principal pour toutes les bulles de topics
        main_container = QWidget()
        main_layout = QHBoxLayout(
            main_container
        )  # Layout vertical pour empiler les cartes
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(8)

        # Créer une bulle pour chaque topic
        for topic in topics:
            # Créer une carte pour le topic
            icon_name = topic.get("icon", "circle-help")

            # Chemin vers le fichier SVG original
            icon_path = os.path.join(
                os.path.dirname(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                ),
                "assets",
                "icons",
                f"{icon_name}.svg",
            )

            # Créer un fichier SVG temporaire coloré en vert
            # temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
            # svg_path = os.path.join(icon_path, f"{icon_name}.svg")

            # Créer la carte avec l'icône SVG verte
            card = TopicCard(
                title=topic["title"],
                description=topic["description"],
                icon_pixmap=icon_path,
            )

            card.clicked.connect(
                lambda checked=False, t=topic["title"]: self.handle_topic_selection(t)
            )

            # Conteneur horizontal pour centrer la bulle
            card_layout = QHBoxLayout()
            card_layout.setContentsMargins(0, 0, 0, 0)
            card_layout.addStretch(1)  # Espace à gauche pour centrer
            card_layout.addWidget(card)
            card_layout.addStretch(1)  # Espace à droite pour centrer

            # Ajouter le layout horizontal au layout principal
            card_container = QWidget()
            card_container.setLayout(card_layout)
            main_layout.addWidget(card_container)

        # Ajouter le conteneur principal au chat
        self.chat_layout.addWidget(main_container)

        # Faire défiler vers le bas
        QTimer.singleShot(50, self.scroll_to_bottom)

    def handle_topic_selection(self, topic):
        """Gère la sélection d'une rubrique"""
        # Ajouter le choix de l'utilisateur comme message
        self.clear_bubbles()
        
        self.add_chat_bubble(
            f"Je souhaite de l'aide sur : {topic}",
            is_user=True,
            word_wrap=False,
            icon_name="circle-help",
            icon_color="#ffffff",
            icon_size=24,
        )

        # Traiter la sélection en fonction de la rubrique choisie
        if topic == "Création de projet":
            self.start_app_skeleton_wizard()
        elif topic == "Navigation fichiers":
            self.add_chat_bubble(
                "Pour naviguer dans vos fichiers, utilisez l'explorateur à gauche.\n "
                "Vous pouvez cliquer sur un fichier pour le sélectionner ou double-cliquer pour l'ouvrir. "
                "La barre de recherche en haut vous permet de filtrer les fichiers.",
                is_user=False,
            )
        elif topic == "Aide au codage":
            self.add_chat_bubble(
                "Je peux vous aider à résoudre des problèmes de code.\n "
                "Décrivez-moi le problème que vous rencontrez ou posez-moi une question spécifique sur votre code.",
                is_user=False,
                word_wrap=False,
            )
        elif topic == "Suggestions d'amélioration":
            self.add_chat_bubble(
                "Je peux analyser votre code et vous suggérer des améliorations.\n "
                "Sélectionnez un fichier dans l'explorateur et demandez-moi de l'analyser.",
                is_user=False,
                word_wrap=False,
            )
        elif topic == "Documentation":
            self.add_chat_bubble(
                "Je peux générer de la documentation pour votre code.\n "
                "Sélectionnez un fichier ou une fonction spécifique et demandez-moi de documenter.",
                is_user=False,
                word_wrap=False,
            )
        else:
            self.add_chat_bubble(
                f"Je vais vous aider concernant '{topic}'. \nQue souhaitez-vous savoir exactement ?",
                is_user=False,
                word_wrap=False,
            )

    def add_interactive_bubble(self, title, options, bubble_type="technology"):
        """Ajoute une bulle interactive avec des boutons pour sélectionner des options"""
        # Créer la bulle interactive
        interactive_bubble = InteractiveChatBubble(title, options, bubble_type)

        # Créer un layout horizontal pour aligner la bulle (toujours du côté IA)
        bubble_layout = QHBoxLayout()
        bubble_layout.setContentsMargins(0, 0, 0, 0)
        bubble_layout.addWidget(interactive_bubble)
        bubble_layout.addStretch(1)  # Espace à droite pour aligner à gauche

        # Ajouter le layout horizontal au chat
        bubble_container = QWidget()
        bubble_container.setLayout(bubble_layout)
        self.chat_layout.addWidget(bubble_container)

        # Connecter le signal de sélection
        interactive_bubble.choiceSelected.connect(self.on_interactive_choice)

        # Faire défiler vers le bas après un court délai
        QTimer.singleShot(50, self.scroll_to_bottom)

    def add_action_confirmation_bubble(
        self, action_text, icon_name="code", icon_color="#FFFFFF", icon_size=20
    ):
        """Ajoute une bulle de confirmation d'action proposée par l'IA

        Args:
            action_text (str): Le texte décrivant l'action proposée
            icon_name (str, optional): Nom de l'icône SVG à afficher. Defaults to "code".
            icon_color (str, optional): Couleur de l'icône au format CSS. Defaults to "#FFFFFF".
            icon_size (int, optional): Taille de l'icône en pixels. Defaults to 20.

        Returns:
            ActionConfirmationBubble: La bulle de confirmation créée
        """
        # Créer la bulle de confirmation d'action
        action_bubble = ActionConfirmationBubble(
            action_text, icon_name, icon_color, icon_size
        )

        # Créer un layout horizontal pour aligner la bulle (toujours du côté IA)
        bubble_layout = QHBoxLayout()
        bubble_layout.setContentsMargins(0, 0, 0, 0)
        bubble_layout.addWidget(action_bubble)
        bubble_layout.addStretch(1)  # Espace à droite pour aligner à gauche

        # Ajouter le layout horizontal au chat
        bubble_container = QWidget()
        bubble_container.setLayout(bubble_layout)
        self.chat_layout.addWidget(bubble_container)

        # Faire défiler vers le bas après un court délai
        QTimer.singleShot(50, self.scroll_to_bottom)

        return action_bubble

    def on_interactive_choice(self, bubble_type, choice):
        """Gère la sélection d'une option dans une bulle interactive"""
        # Initialiser ProjectCreatorShow si ce n'est pas déjà fait
        if not hasattr(self, "project_show"):
            self.project_show = ProjectCreatorShow()
            # Connecter les signaux
            self.project_show.technology_selected.connect(self.on_technology_selected)
            self.project_show.app_type_selected.connect(self.on_app_type_selected)
            self.project_show.feature_selected.connect(self.on_feature_selected)
            self.project_show.project_creation_requested.connect(
                self.on_project_creation_requested
            )

        # Ajouter le choix de l'utilisateur comme message
        self.add_chat_bubble(f"J'ai choisi: {choice}", is_user=True, word_wrap=False)

        if bubble_type == "technology":
            # L'utilisateur a choisi une technologie, proposer les types d'applications
            app_types = self.project_show.select_technology(choice)
            self.add_interactive_bubble(
                f"Quel type d'application {choice} souhaitez-vous créer ?",
                app_types,
                bubble_type="app_type",
            )

        elif bubble_type == "app_type":
            # L'utilisateur a choisi un type d'application, proposer des fonctionnalités
            features = self.project_show.select_app_type(choice)
            self.add_interactive_bubble(
                f"Quelles fonctionnalités souhaitez-vous inclure dans votre {choice} ?",
                features,
                bubble_type="features",
            )

        elif bubble_type == "features":
            # L'utilisateur a choisi une fonctionnalité, la basculer et mettre à jour la liste
            self.project_show.toggle_feature(choice)

            # Afficher un message pour indiquer que la fonctionnalité a été ajoutée/retirée
            if choice in self.project_show.selected_features:
                self.add_chat_bubble(f"Fonctionnalité '{choice}' ajoutée")
            else:
                self.add_chat_bubble(f"Fonctionnalité '{choice}' retirée")

            # Ajouter un bouton pour finaliser la sélection des fonctionnalités
            if (
                not hasattr(self, "finalize_button_added")
                or not self.finalize_button_added
            ):
                self.add_chat_bubble(
                    "Cliquez sur d'autres fonctionnalités pour les ajouter/retirer, "
                    "puis cliquez sur 'Finaliser' pour générer votre projet."
                )
                self.add_action_confirmation_bubble(
                    "Finaliser la sélection",
                    self.finalize_features_selection,
                    "Annuler",
                    self.cancel_features_selection,
                )
                self.finalize_button_added = True

    def finalize_features_selection(self):
        """Finalise la sélection des fonctionnalités et lance la génération du projet"""
        self.finalize_button_added = False

        # Afficher un résumé des sélections
        self.add_chat_bubble(
            f"Technologie: {self.project_show.selected_technology}\n"
            f"Type d'application: {self.project_show.selected_app_type}\n"
            f"Fonctionnalités: {', '.join(self.project_show.selected_features)}"
        )

        self.add_chat_bubble(
            "Je vais maintenant générer un squelette d'application basé sur vos choix. "
            "Veuillez patienter un instant..."
        )
        # Simuler un délai pour la génération
        QTimer.singleShot(1500, self.generate_app_skeleton)

    def cancel_features_selection(self):
        """Annule la sélection des fonctionnalités"""
        self.finalize_button_added = False
        self.project_show.reset_selections()
        self.add_chat_bubble("Sélection annulée. Vous pouvez recommencer.")

    def on_technology_selected(self, technology_id):
        """Gère la sélection d'une technologie"""
        print(f"Technologie sélectionnée: {technology_id}")

        # Afficher les langages de programmation disponibles pour cette technologie
        self.display_programming_languages(technology_id)

        # Ajouter une action pour afficher les détails de la technologie
        # self.add_action_confirmation_bubble(
        #     "Afficher les détails de la technologie",
        #     self.display_technology_details,
        #     "Annuler",
        #     self.cancel_technology_details,
        # )

    def display_technology_details(self):
        """Affiche les détails de la technologie sélectionnée"""
        # Récupérer les détails de la technologie
        technology_details = self.project_show.get_technology_details()

        # Afficher les détails
        self.add_chat_bubble(
            f"Nom de la technologie: {technology_details['name']}\n"
            f"Description: {technology_details['description']}\n"
            f"Avantages: {', '.join(technology_details['advantages'])}\n"
            f"Inconvénients: {', '.join(technology_details['disadvantages'])}"
        )

    def cancel_technology_details(self):
        """Annule l'affichage des détails de la technologie"""
        self.add_chat_bubble("Affichage des détails annulé.")

    def display_programming_languages(self, technology_id):
        """Affiche les langages de programmation disponibles pour une technologie en utilisant ProjectTypeCard"""
        # Nettoyer les anciennes bulles de langages
        self.clear_bubbles()
        

        # Ajouter un bouton de retour pour revenir à la sélection des technologies
        from project.structure.back_button import BackButton
        back_button = BackButton("« Retour aux technologies")
        back_button.clicked.connect(lambda: self.handle_back_to_technologies())

        # Ajouter le bouton au layout
        back_container = QWidget()
        back_layout = QHBoxLayout(back_container)
        back_layout.setContentsMargins(10, 5, 10, 5)
        back_layout.addWidget(back_button)
        back_layout.addStretch(1)

        back_container.setProperty("language_bubble", True)
        self.chat_layout.addWidget(back_container)

        # Obtenir les données des langages de programmation
        lang_data = self.project_show.get_programming_languages_data(technology_id)
        languages = lang_data["languages"]
        technology_name = lang_data["technology_name"]
        color = lang_data["color"]

        print(f"Affichage de {len(languages)} langages pour {technology_name}")

        # Si aucun langage n'est disponible, afficher un message et terminer
        if not languages:
            message = self.add_chat_bubble(
                f"Aucun langage spécifique n'est nécessaire pour {technology_name}. Passons à l'étape suivante.",
                is_user=False,
            )
            message.setProperty("language_bubble", True)
            return

        # Créer un message pour introduire les langages
        intro_bubble = self.add_chat_bubble(
            f"Sélectionnez un langage de programmation pour {technology_name} :",
            is_user=False,
            icon_name="hand-helping",
            icon_color="#FFFFFF",
            icon_size=24,
            word_wrap=False,
        )
        intro_bubble.setProperty("language_bubble", True)

        # Créer un conteneur pour la grille
        grid_container = QWidget()
        grid_container.setStyleSheet("background-color: transparent;")
        grid_container.setProperty("language_bubble", True)
        grid_layout = QGridLayout(grid_container)
        grid_layout.setContentsMargins(8, 8, 8, 8)
        grid_layout.setSpacing(10)
        grid_layout.setHorizontalSpacing(
            15
        )  # Plus d'espace horizontal entre les colonnes

        # Ajouter le conteneur au chat
        self.chat_layout.addWidget(grid_container)

        # Créer les cartes de langages pour la grille
        num_columns = 4  # Nombre de colonnes dans la grille
        for i, lang in enumerate(languages):
            # Calculer la position dans la grille (row, column)
            row = i // num_columns
            col = i % num_columns

            try:
                # Adapter le langage au format attendu par ProjectTypeCard
                lang_data_for_card = {
                    "id": lang["id"],
                    "name": lang["name"],
                    "description": lang.get("description", ""),
                    "icon": lang.get("icon", "code"),
                    "color": color,  # Utiliser la couleur de la technologie parent
                }

                # Créer une carte pour le langage
                card = ProjectTypeCard(lang_data_for_card)

                # Stocker les ID dans les propriétés de la carte
                card.setProperty("language_id", lang["id"])
                card.setProperty("technology_id", technology_id)

                # Connecter le signal de clic de la carte à la méthode de sélection de langage
                # Utiliser une fonction spécifique pour éviter les problèmes de portée avec lambda
                def create_language_click_handler(lang_id, tech_id):
                    return lambda: self.on_language_selected(lang_id, tech_id)

                card.clicked.connect(
                    create_language_click_handler(lang["id"], technology_id)
                )

                # Stocker les ID pour le nettoyage
                card.setProperty("language_bubble", True)
                card.setProperty("language_id", lang["id"])
                card.setProperty("technology_id", technology_id)

                # Ajouter la carte à la grille
                grid_layout.addWidget(card, row, col)

                print(f"Carte de langage ajoutée: {lang['name']}")
            except Exception as e:
                print(
                    f"[ERREUR] Échec de création de la carte pour {lang['name']}: {str(e)}"
                )

        # Ajouter des widgets vides pour compléter la dernière ligne et maintenir l'alignement à gauche
        total_items = len(languages)
        if total_items % num_columns != 0:
            # Calculer combien de widgets vides il faut ajouter
            empty_slots = num_columns - (total_items % num_columns)
            last_row = total_items // num_columns
            # Ajouter les widgets vides
            for i in range(empty_slots):
                empty_widget = QWidget()
                empty_widget.setFixedSize(200, 150)  # Taille approximative d'une carte
                empty_widget.setStyleSheet("background-color: transparent;")
                empty_widget.setProperty("language_bubble", True)
                grid_layout.addWidget(
                    empty_widget, last_row, (total_items % num_columns) + i
                )

    def clear_language_bubbles(self):
        """Supprime toutes les bulles de langages"""
        for widget in self.findChildren(QWidget):
            if widget.property("language_bubble"):
                widget.deleteLater()

    def on_language_selected(self, lang_id, technology_id):
        """Gère la sélection d'un langage de programmation"""
        # Appliquer un effet visuel aux cartes pour montrer celle qui est sélectionnée
        # et désactiver les autres
        for widget in self.findChildren(QWidget):
            if widget.property("language_bubble") and isinstance(
                widget, ProjectTypeCard
            ):
                if widget.property("language_id") == lang_id:
                    # Mettre en évidence la carte sélectionnée
                    widget.set_selected(True)
                else:
                    # Désactiver les autres cartes
                    widget.setEnabled(False)
                    widget.set_selected(False)

        print(f"Langage sélectionné: {lang_id} pour la technologie {technology_id}")

        # Trouver les noms du langage, de la technologie et du type de projet
        lang_data = self.project_show.get_programming_languages_data(technology_id)
        language_name = next(
            (lang["name"] for lang in lang_data["languages"] if lang["id"] == lang_id),
            "",
        )
        technology_name = lang_data["technology_name"]

        # Stocker les noms pour utilisation ultérieure
        self.selected_language_name = language_name
        self.technology_name = technology_name
        self.project_type_name = next(
            (
                pt["name"]
                for pt in self.project_show.get_project_types()
                if pt["id"] == self.selected_project_type
            ),
            "Type de projet inconnu",
        )

        # Ajouter un délai pour permettre à l'interface de se mettre à jour
        QTimer.singleShot(
            500,
            lambda: self.display_project_subtypes(
                self.selected_project_type, technology_id, lang_id
            ),
        )

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
        back_button.clicked.connect(
            lambda: self.handle_back_to_languages(technology_id)
        )

        # Ajouter le bouton au layout
        back_container = QWidget()
        back_layout = QHBoxLayout(back_container)
        back_layout.setContentsMargins(10, 5, 10, 5)
        back_layout.addWidget(back_button)
        back_layout.addStretch(1)

        self.chat_layout.addWidget(back_container)

        # Message d'introduction pour les sous-types de projets
        self.add_chat_bubble(
            "Veuillez choisir un type de projet spécifique :",
            is_user=False,
            word_wrap=True,
        )

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
                grid_layout.addWidget(
                    empty_widget, row, col + i
                )

        # Ajouter le conteneur au layout principal
        self.chat_layout.addWidget(project_subtype_container)

    def clear_bubbles(self):
        """Efface tous les widgets du chat"""
        while self.chat_layout.count() > 0:
            item = self.chat_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def handle_back_to_project_types(self):
        """Gère le retour à la sélection des types de projets en effaçant d'abord le contenu"""
        # Effacer tous les widgets dans le chat
        self.clear_bubbles()

        # Afficher les types de projets
        self.display_project_types()

    def handle_back_to_technologies(self):
        """Gère le retour à la sélection des technologies en effaçant d'abord le contenu"""
        # Effacer tous les widgets dans le chat
        self.clear_bubbles()

        # Afficher les technologies pour le type de projet sélectionné
        self.display_technologies_for_project_type(self.selected_project_type)

    def handle_back_to_languages(self, technology_id):
        """Gère le retour à la sélection des langages en effaçant d'abord le contenu"""
        # Effacer tous les widgets dans le chat
        self.clear_bubbles()

        # Afficher les langages pour la technologie sélectionnée
        self.display_programming_languages(technology_id)

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

        # Afficher le résumé complet des choix
        self.add_chat_bubble(
            f"<b>Type de projet :</b> {project_type_name}<br>"
            + f"<b>Technologie :</b> {technology_name}<br>"
            + f"<b>Langage :</b> {language_name}<br>"
            + f"<b>Type spécifique :</b> {subtype_name}",
            is_user=False   ,
            word_wrap=True,
            icon_name="info",
            icon_color="#FFFFFF",
        )

        # Continuer avec la prochaine étape (à définir selon les besoins)
        # Par exemple, afficher un message sur la génération du projet
        QTimer.singleShot(1000, lambda: self.display_project_generation_message())

    def display_project_generation_message(self):
        """Affiche un message indiquant que le projet est en cours de génération"""
        self.add_chat_bubble(
            "Je vais maintenant générer le projet selon vos choix. Veuillez patienter...",
            is_user=False,
            word_wrap=True,
        )

    def on_app_type_selected(self, app_type):
        """Gère la sélection d'un type d'application via le signal"""
        print(f"Signal app_type_selected reçu: {app_type}")
        # Cette méthode est appelée lorsque le signal app_type_selected est émis
        pass

    def on_feature_selected(self, feature):
        """Gère la sélection d'une fonctionnalité"""
        # Cette méthode est appelée lorsque le signal feature_selected est émis
        pass

    def on_project_creation_requested(self, technology, app_type, features):
        """Gère la demande de création d'un projet"""
        # Cette méthode est appelée lorsque le signal project_creation_requested est émis
        # On peut l'utiliser pour des actions supplémentaires si nécessaire
        pass

    
    def update_tree_view_and_select_folder(self, folder_path):
        """Met à jour la vue d'arborescence et sélectionne un dossier"""
        if not os.path.exists(folder_path):
            self.status_bar.showMessage(f"Le dossier {folder_path} n'existe pas", 3000)
            return

        # Utiliser la méthode du composant déporté pour mettre à jour l'arborescence
        self.file_tree.update_tree_view_and_select_folder(folder_path)

        QTimer.singleShot(100, self.file_tree.highlight_tree_view)
    def add_project_name_input(self):
        """Ajoute une bulle interactive pour saisir le nom du projet"""
        # Créer un conteneur pour la bulle
        bubble_container = QWidget()
        container_layout = QVBoxLayout(bubble_container)
        container_layout.setContentsMargins(0, 0, 0, 10)

        # Créer une bulle de chat pour contenir l'input
        bubble = QFrame()
        bubble.setObjectName("input_bubble")
        bubble.setStyleSheet(
            """
            QFrame#input_bubble {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(227, 242, 253, 0.8), stop:1 rgba(187, 222, 251, 0.8));
                border-radius: 10px;
                border: 3px solid #1976D2;
                padding: 15px;
            }
        """
        )

        # Layout pour la bulle
        bubble_layout = QVBoxLayout(bubble)
        bubble_layout.setContentsMargins(15, 15, 15, 15)

        # Titre de la section avec icône
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 15)

        # Icône de configuration
        title_icon = QLabel()
        title_icon.setFixedSize(24, 24)
        title_icon.setStyleSheet("background: transparent; border: none;")
        config_pixmap = get_svg_icon("settings", size=24, color="#1976D2")
        if config_pixmap:
            title_icon.setPixmap(config_pixmap)
        title_layout.addWidget(title_icon)

        title_label = QLabel("Configuration du projet")
        title_label.setStyleSheet(
            """
            color: #1976D2; 
            font-weight: bold; 
            font-size: 16px;
            background: transparent;
        """
        )
        title_layout.addWidget(title_label)
        title_layout.addStretch(1)

        bubble_layout.addLayout(title_layout)

        # Champ de saisie pour le nom du projet
        input_layout = QHBoxLayout()
        project_name_label = QLabel("Nom du projet :")
        project_name_label.setStyleSheet(
            """
            color: #1976F2; 
            font-weight: bold;
            font-size: 14px;
            background: transparent;
        """
        )
        input_layout.addWidget(project_name_label)

        self.project_name_input = QLineEdit()
        self.project_name_input.setPlaceholderText("Entrez le nom de votre projet")
        self.project_name_input.setStyleSheet(
            """
            QLineEdit {
                border: 2px solid #BBDEFB;
                border-radius: 6px;
                padding: 10px;
                background-color: rgba(255, 255, 255, 0.9);
                color: #0D47A1;
                font-size: 14px;
                selection-background-color: #2196F3;
                selection-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
                background-color: white;
            }
        """
        )
        self.project_name_input.setMinimumHeight(38)
        input_layout.addWidget(self.project_name_input, 1)  # 1 = stretch factor

        # Bouton de validation
        confirm_btn = QPushButton("Valider")
        confirm_btn.setStyleSheet(
            """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2196F3, stop:1 #1976D2);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 25px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #42A5F5, stop:1 #1E88E5);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1976D2, stop:1 #1565C0);
            }
        """
        )
        confirm_btn.setCursor(Qt.PointingHandCursor)  # Changer le curseur au survol
        confirm_btn.clicked.connect(self.on_project_name_submitted)
        input_layout.addWidget(confirm_btn)

        bubble_layout.addLayout(input_layout)
        container_layout.addWidget(bubble)

        # Ajouter la bulle au chat
        self.chat_layout.addWidget(bubble_container)

        # Faire défiler vers le bas après un court délai
        QTimer.singleShot(50, self.scroll_to_bottom)

        # Mettre le focus sur le champ de saisie
        self.project_name_input.setFocus()

        # Connecter la touche Entrée pour soumettre le nom du projet
        self.project_name_input.returnPressed.connect(self.on_project_name_submitted)

    def start_app_skeleton_wizard(self):
        """Démarre l'assistant de création de squelette d'application"""
        # Afficher un message explicatif
        self.add_chat_bubble(
            "Je vais vous aider à créer un squelette d'application. Commençons par définir le nom de votre projet :",
            is_user=False,
        )

        # Créer une bulle pour saisir le nom du projet
        self.input_chat_bubble = InputChatBubble(self)
        bubble_container = self.input_chat_bubble.add_project_name_input()
        self.chat_layout.addWidget(bubble_container)

        # Connecter le signal de soumission du nom du projet
        self.input_chat_bubble.projectNameSubmitted.connect(
            self.on_project_name_submitted
        )

        # Faire défiler vers le bas après un court délai
        QTimer.singleShot(50, self.scroll_to_bottom)

        # Mettre le focus sur le champ de saisie
        self.input_chat_bubble.project_name_input.setFocus()

    def on_project_name_submitted(self, project_name=None):
        """Gère la soumission du nom du projet

        Args:
            project_name (str, optional): Le nom du projet. Si None, le nom sera récupéré depuis self.project_name_input.
        """
        # Si project_name n'est pas fourni, le récupérer depuis le champ de saisie
        if project_name is None and hasattr(self, "project_name_input"):
            project_name = self.project_name_input.text().strip()

        # Vérifier que le nom n'est pas vide
        if not project_name:
            # Afficher un message d'erreur
            self.add_chat_bubble(
                "<span style='color:orange'>Veuillez entrer un nom pour votre projet.</span>",
                is_user=False,
                icon_name="triangle-alert",
                icon_color="#ff9000",
                icon_size=24,
            )
            return

        # Stocker le nom du projet
        self.project_name = project_name

        # Afficher un message de confirmation
        self.add_chat_bubble(
            f"<b>Nom du projet :</b> {project_name}",
            is_user=True,
            word_wrap=False,
            icon_name="check",
            icon_color="#4CAF50",
            icon_size=24,
        )

        # Vérifier si un chemin racine a été sélectionné
        if not self.path_root:
            # Aucun chemin sélectionné, demander à l'utilisateur d'en sélectionner un
            self.add_chat_bubble(
                "<span style='color:orange'>Veuillez d'abord sélectionner un dossier dans l'arborescence à gauche pour y créer votre projet.</span>",
                is_user=False,
                icon_name="triangle-alert",
                icon_color="#ff9000",
                icon_size=24,
            )
            # Faire clignoter le TreeView pour attirer l'attention
            QTimer.singleShot(500, lambda: self.file_tree.highlight_tree_view())

            # on met un flag pour attendre que l'utilisateur sélectionne un dossier
            self.wait_for_path = True
            return

        # Afficher le chemin complet et demander confirmation avec boutons intégrés
        chemin_complet = os.path.join(self.path_root, self.project_name)
        message_text = f"<b>Chemin complet du projet :</b><br><code>{chemin_complet}</code><br><br>Ce chemin vous convient-il ?"

        # Créer la bulle avec les boutons intégrés et une icône de dossier
        self.path_confirmation = PathConfirmationButtons(message_text, self)
        self.path_confirmation.add_confirmation_buttons()

        # Ajouter la bulle au chat
        self.chat_layout.addWidget(self.path_confirmation)

        # Connecter les signaux
        self.path_confirmation.pathConfirmed.connect(self.on_path_confirmed)
        self.path_confirmation.pathRejected.connect(self.on_path_rejected)

        # Faire défiler vers le bas
        QTimer.singleShot(50, self.scroll_to_bottom)

    def is_path_allowed(self, path):
        """Vérifie si un chemin est autorisé pour la création de répertoires
        
        Args:
            path (str): Le chemin à vérifier
            
        Returns:
            tuple: (bool, str) - Un booléen indiquant si le chemin est autorisé et un message explicatif
        """
        if not path:
            return (False, "Le chemin ne peut pas être vide")
        
        # Les constantes FORBIDDEN_PATHS et SYSTEM_DRIVES sont maintenant importées en haut du fichier
            
        # Normaliser le chemin pour faciliter la comparaison
        normalized_path = os.path.normpath(path).lower()
        
        # Extraire la lettre du lecteur si présente
        drive_letter = None
        if len(normalized_path) > 1 and normalized_path[1] == ':':
            drive_letter = normalized_path[0]
            
        # Vérifier si le chemin contient un des emplacements interdits
        path_parts = normalized_path.split(os.sep)
        
        # Si le chemin est sur un lecteur système, vérifier les emplacements interdits
        if drive_letter in SYSTEM_DRIVES:
            for forbidden in FORBIDDEN_PATHS:
                forbidden_lower = forbidden.lower()
                
                # Vérifier si un des composants du chemin est interdit
                for part in path_parts:
                    if part == forbidden_lower or \
                       part.startswith("programfiles") or \
                       part.startswith("program files"):
                        return (False, f"Création de dossier interdite dans l'emplacement système '{forbidden}'")
        
        # Vérifier si le chemin existe et est accessible en écriture
        parent_path = os.path.dirname(path)
        if os.path.exists(parent_path):
            if not os.access(parent_path, os.W_OK):
                return (False, f"Le dossier parent '{parent_path}' n'est pas accessible en écriture")
        
        return (True, "Chemin autorisé")
        
    def on_path_confirmed(self):
        """Gère la confirmation du chemin du projet et crée directement le répertoire"""
        self.add_chat_bubble(
            "Je confirme ce chemin pour mon projet.",
            is_user=True,
            icon_name="circle-check",
            icon_color="#FFFFFF",
            word_wrap=False,
        )
        
        # Vérifier si le chemin est autorisé avant de créer le répertoire
        project_path = os.path.join(self.path_root, self.project_name)
        is_allowed, message = self.is_path_allowed(project_path)
        if not is_allowed:
            self.add_chat_bubble(
                f"<b>Action non autorisée</b><br><br>"
                f"{message}<br><br>"
                f"Veuillez choisir un autre emplacement pour votre projet.",
                is_user=False,
                icon_name="triangle-alert",
                icon_color="#F44336",
                icon_size=24,
            )
            # Faire défiler vers le bas
            QTimer.singleShot(50, self.scroll_to_bottom)
            return

        # Créer directement le répertoire du projet sans demander de confirmation supplémentaire
        self.create_app_skeleton()

    def on_path_rejected(self):
        """Gère le rejet du chemin du projet et permet de saisir un nouveau nom de dossier"""
        self.add_chat_bubble(
            "Je souhaite modifier le chemin du projet.",
            is_user=True,
            icon_name="ban",
            icon_color="#2196F3",
            icon_size=24,
            word_wrap=False,
        )

        # Ajouter une nouvelle boîte de saisie pour le nom du dossier
        self.add_folder_name_input()

    def add_folder_name_input(self):
        """Ajoute une bulle interactive pour saisir un nouveau nom de dossier"""
        # Créer un conteneur pour la bulle
        bubble_container = QWidget()
        container_layout = QVBoxLayout(bubble_container)
        container_layout.setContentsMargins(0, 0, 0, 10)

        # Créer une bulle de chat pour contenir l'input
        bubble = QFrame()
        bubble.setObjectName("input_bubble")
        bubble.setStyleSheet(
            """
            QFrame#input_bubble {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(227, 242, 253, 0.8), stop:1 rgba(187, 222, 251, 0.8));
                border-radius: 10px;
                border: 3px solid #1976D2;
                padding: 15px;
            }
        """
        )

        # Layout pour la bulle
        bubble_layout = QVBoxLayout(bubble)
        bubble_layout.setContentsMargins(15, 15, 15, 15)

        # Champ de saisie pour le nom du dossier
        input_layout = QHBoxLayout()
        folder_name_label = QLabel("Nom du dossier :")
        folder_name_label.setStyleSheet(
            """
            color: #1976F2; 
            font-weight: bold;
            font-size: 14px;
            background: transparent;
        """
        )
        input_layout.addWidget(folder_name_label)

        self.folder_name_input = QLineEdit()
        self.folder_name_input.setText(
            self.project_name
        )  # Pré-remplir avec le nom du projet
        self.folder_name_input.setStyleSheet(
            """
            QLineEdit {
                border: 2px solid #BBDEFB;
                border-radius: 6px;
                padding: 10px;
                background-color: rgba(255, 255, 255, 0.9);
                color: #0D47A1;
                font-size: 14px;
                selection-background-color: #2196F3;
                selection-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
                background-color: white;
            }
        """
        )
        self.folder_name_input.setMinimumHeight(38)
        input_layout.addWidget(self.folder_name_input, 1)  # 1 = stretch factor

        # Bouton de validation
        confirm_btn = QPushButton("Valider")
        confirm_btn.setStyleSheet(
            """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2196F3, stop:1 #1976D2);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 25px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #42A5F5, stop:1 #1E88E5);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1976D2, stop:1 #1565C0);
            }
        """
        )
        confirm_btn.setCursor(Qt.PointingHandCursor)
        confirm_btn.clicked.connect(self.on_folder_name_submitted)
        input_layout.addWidget(confirm_btn)

        bubble_layout.addLayout(input_layout)
        container_layout.addWidget(bubble)

        # Ajouter la bulle au chat
        self.chat_layout.addWidget(bubble_container)

        # Faire défiler vers le bas après un court délai
        QTimer.singleShot(50, self.scroll_to_bottom)

        # Mettre le focus sur le champ de saisie
        self.folder_name_input.setFocus()

        # Connecter la touche Entrée pour soumettre le nom du dossier
        self.folder_name_input.returnPressed.connect(self.on_folder_name_submitted)

    def on_folder_name_submitted(self):
        """Gère la soumission du nouveau nom de dossier"""
        # Récupérer le nom du dossier
        folder_name = self.folder_name_input.text().strip()

        # Vérifier que le nom n'est pas vide
        if not folder_name:
            # Afficher un message d'erreur
            self.add_chat_bubble(
                "<span style='color:orange'>Veuillez entrer un nom pour le dossier.</span>",
                is_user=False,
                icon_name="triangle-alert",
                icon_color="#ff9000",
                icon_size=24,
            )
            return

        # Stocker le nouveau nom de dossier
        self.project_folder_name = folder_name
        
        # Vérifier si le chemin est autorisé
        project_path = os.path.join(self.path_root, folder_name)
        is_allowed, message = self.is_path_allowed(project_path)
        if not is_allowed:
            self.add_chat_bubble(
                f"<b>Action non autorisée</b><br><br>"
                f"{message}<br><br>"
                f"Veuillez choisir un autre emplacement pour votre projet.",
                is_user=False,
                icon_name="triangle-alert",
                icon_color="#F44336",
                icon_size=24,
            )
            # Proposer de nouveau la saisie du nom de dossier
            QTimer.singleShot(500, self.add_folder_name_input)
            return

        # Afficher un message de confirmation
        self.add_chat_bubble(
            f"<b>Nom du dossier :</b> {folder_name}",
            is_user=True,
            word_wrap=False,
            icon_name="check",
            icon_color="#4CAF50",
            icon_size=24,
        )

        # Afficher le nouveau chemin complet
        chemin_complet = os.path.join(self.path_root, folder_name)
        self.add_chat_bubble(
            f"<b>Nouveau chemin complet du projet :</b><br>"
            f"<code>{chemin_complet}</code>",
            is_user=False,
        )

        # Continuer avec la génération du squelette
        self.add_chat_bubble(
            "Je vais maintenant générer un squelette d'application basé sur vos choix. "
            "Veuillez patienter un instant...",
            is_user=False,
        )

        # Simuler un délai pour la génération
        QTimer.singleShot(1500, self.create_app_skeleton)

    def on_create_app_rejected(self):
        """Gère le rejet de la création du dossier du projet"""
        self.add_chat_bubble(
            "Je ne souhaite pas créer le dossier du projet pour le moment.",
            is_user=True,
            icon_name="ban",
            icon_color="#F44336",
        )

        # Afficher un message pour indiquer que l'action a été annulée
        self.add_chat_bubble(
            "D'accord, l'action a été annulée. Vous pouvez sélectionner un autre chemin ou revenir à cette étape plus tard.",
            is_user=False,
            icon_name="info-circle",
            icon_color="#2196F3",
        )

        # Faire défiler vers le bas
        QTimer.singleShot(50, self.scroll_to_bottom)

    def create_app_skeleton(self, project_type_id=None, technology_id=None):
        """Crée effectivement le squelette d'application en utilisant la commande mkdir"""
        # Déterminer le nom du dossier à utiliser
        folder_name = getattr(self, "project_folder_name", self.project_name)

        # Chemin complet du projet
        project_path = os.path.join(self.path_root, folder_name)
        
        # Vérifier si le chemin est autorisé
        is_allowed, message = self.is_path_allowed(project_path)
        if not is_allowed:
            self.add_chat_bubble(
                f"<b>Action non autorisée</b><br><br>"
                f"{message}<br><br>"
                f"Veuillez choisir un autre emplacement pour votre projet.",
                is_user=False,
                icon_name="triangle-alert",
                icon_color="#F44336",
                icon_size=24,
            )
            QTimer.singleShot(50, self.scroll_to_bottom)
            return

        # Créer le répertoire du projet avec la commande mkdir
        try:
            # Vérifier si le répertoire existe déjà
            if not os.path.exists(project_path):
                os.makedirs(project_path)
                creation_status = "créé"
            else:
                creation_status = "déjà existant"

            # Si nous avons des informations sur le type de projet et la technologie
            if project_type_id and technology_id:
                # Créer la structure de base en fonction du type de projet et de la technologie
                self.create_project_structure(
                    project_path, project_type_id, technology_id
                )

                # Trouver les noms du type de projet et de la technologie
                project_type_name = next(
                    (
                        pt["name"]
                        for pt in self.get_project_types()
                        if pt["id"] == project_type_id
                    ),
                    "",
                )
                technology_name = next(
                    (
                        tech["name"]
                        for tech in self.get_technologies_for_project_type(
                            project_type_id
                        )
                        if tech["id"] == technology_id
                    ),
                    "",
                )

                # Message spécifique avec les détails du projet
                self.add_chat_bubble(
                    f"<b>Votre projet '{self.project_name}' de type <span style='color:#2196F3'>{project_type_name}</span> "
                    f"utilisant <span style='color:#FF9800'>{technology_name}</span> est prêt !</b><br><br>"
                    f"Le dossier du projet a été {creation_status} :<br>"
                    f"<code>{project_path}</code><br><br>"
                    "Vous pouvez maintenant commencer à travailler sur votre application.",
                    is_user=False,
                    icon_name="circle-check",
                    icon_color="#4CAF50",
                    icon_size=24,
                )
            else:
                # Message générique si nous n'avons pas d'informations sur le type de projet
                self.add_chat_bubble(
                    f"<b>Votre squelette d'application '{self.project_name}' est prêt !</b><br><br>"
                    f"Le dossier du projet a été {creation_status} :<br>"
                    f"<code>{project_path}</code><br><br>"
                    "Vous pouvez maintenant commencer à travailler sur votre application.",
                    is_user=False,
                    icon_name="circle-check",
                    icon_color="#4CAF50",
                    icon_size=24,
                )

            # Mettre à jour le TreeView pour afficher le nouveau répertoire
            self.update_tree_view_and_select_folder(project_path)

        except Exception as e:
            # En cas d'erreur, afficher un message d'erreur
            self.add_chat_bubble(
                f"<b>Erreur lors de la création du dossier du projet</b><br><br>"
                f"Impossible de créer le dossier :<br>"
                f"<code>{project_path}</code><br><br>"
                f"Erreur : {str(e)}",
                is_user=False,
                icon_name="triangle-alert",
                icon_color="#F44336",
                icon_size=24,
            )

        # Faire défiler vers le bas
        QTimer.singleShot(50, self.scroll_to_bottom)

    def create_project_structure(self, project_path, project_type_id, technology_id):
        """Crée la structure de base d'un projet en fonction de son type et de sa technologie
        en utilisant la classe ProjectCreator"""
        # Utiliser la classe ProjectCreator pour créer la structure du projet
        ProjectCreator.create_project_structure(
            project_path, project_type_id, technology_id, self.project_name
        )

    def generate_app_skeleton(self):
        """Méthode de compatibilité pour l'ancien flux - redirige vers le nouveau flux"""
        # Vérifier si un chemin a été sélectionné
        if not self.path_root:
            # Aucun chemin sélectionné, demander à l'utilisateur d'en sélectionner un
            self.add_chat_bubble(
                "<span style='color:orange'>Veuillez d'abord sélectionner un dossier dans l'arborescence à gauche pour y créer votre projet.</span>",
                is_user=False,
                icon_name="triangle-alert",
                icon_color="#ff9000",
                icon_size=24,
            )
            # Faire clignoter le TreeView pour attirer l'attention
            QTimer.singleShot(500, lambda: self.file_tree.highlight_tree_view())

            return

        # Afficher le chemin complet et demander confirmation
        chemin_complet = os.path.join(self.path_root, self.project_name)
        self.add_chat_bubble(
            f"<b>Chemin complet du projet :</b><br>"
            f"<code>{chemin_complet}</code><br><br>"
            "Ce chemin vous convient-il ?",
            is_user=False,
        )

        # Ajouter des boutons de confirmation
        self.add_path_confirmation_buttons()

        # Faire défiler vers le bas après un court délai pour s'assurer que le widget est complètement rendu
        QTimer.singleShot(50, self.scroll_to_bottom)

    def scroll_to_bottom(self):
        """Fait défiler la zone de chat vers le bas pour voir le dernier message"""
        # Utiliser le maximum de la barre de défilement pour aller tout en bas
        self.scroll.verticalScrollBar().setValue(
            self.scroll.verticalScrollBar().maximum()
        )

    @Slot(str)
    def update_ia_bubble(self, text):
        self.current_ia_text += text
        # Vérifier si ia_bubble existe et est un ChatBubble
        if hasattr(self, "ia_bubble") and self.ia_bubble is not None:
            # Accéder directement au label stocké dans la bulle
            if hasattr(self.ia_bubble, "label"):
                self.ia_bubble.label.setText(self.current_ia_text)
        # Faire défiler automatiquement vers le bas pour voir les nouveaux messages
        self.scroll_to_bottom()

    @Slot()
    def handle_ia_finished(self):
        # À la fin, parser les actions et proposer la validation
        actions = self.extract_actions(self.current_ia_text)
        if actions:
            self.pending_actions = actions
            self.add_chat_bubble(
                f"<b>Action(s) proposée(s) par l'IA :</b> {json.dumps(actions, indent=2)}",
                is_user=False,
            )
            self.show_action_buttons()
        self.current_ia_text = ""

        # S'assurer que le dernier message est visible
        self.scroll_to_bottom()

        # Sauvegarder la conversation dans l'historique si elle contient des messages
        if len(self.current_conversation) > 0:
            self.save_current_conversation()

    def show_action_buttons(self):
        """Propose à l'utilisateur d'accepter/refuser les actions en utilisant une bulle de confirmation"""
        # Formater le texte des actions en attente
        action_text = "Action(s) proposée(s) par l'IA : [ "

        # Ajouter les détails des actions en attente
        for i, action in enumerate(self.pending_actions):
            if i > 0:
                action_text += ", "
            # Extraire le type et le chemin de l'action
            action_type = action.get("type", "action")
            action_path = action.get("path", "")
            action_text += f'{{ "type": "{action_type}", "path": "{action_path}" }}'

        action_text += " ]"

        # Créer la bulle de confirmation d'action
        action_bubble = self.add_action_confirmation_bubble(
            action_text, icon_name="code", icon_color="#FFFFFF"
        )

        # Définir les fonctions de callback
        def accept():
            self.add_chat_bubble(
                "Je valide les actions proposées.",
                is_user=True,
                icon_name="circle-check",
                icon_color="#FFFFFF",
            )
            self.apply_actions(self.pending_actions)
            self.pending_actions = []

        def refuse():
            self.add_chat_bubble(
                "Je refuse les actions proposées.",
                is_user=True,
                icon_name="ban",
                icon_color="#FFFFFF",
            )
            self.pending_actions = []

        # Connecter les signaux aux fonctions de callback
        action_bubble.actionAccepted.connect(accept)
        action_bubble.actionRejected.connect(refuse)

        # Faire défiler vers le bas
        self.scroll_to_bottom()

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

    def get_drive_info(self, drive_letter):
        # Obtenir des informations sur le lecteur (espace libre, capacité totale, etc.)
        try:
            total, used, free = shutil.disk_usage(drive_letter)
            total_gb = total / (1024**3)
            free_gb = free / (1024**3)
            return f"Espace total: {total_gb:.2f} GB, Espace libre: {free_gb:.2f} GB"
        except Exception as e:
            return f"Impossible d'obtenir les informations du lecteur: {str(e)}"

    def apply_actions(self, actions):
        for action in actions:
            typ = action.get("type")
            path = os.path.join(self.model.rootPath(), action.get("path", ""))
            if typ == "mkdir":
                os.makedirs(path, exist_ok=True)
                self.add_chat_bubble(f"📁 Dossier créé: {path}", is_user=True)
            elif typ == "touch":
                with open(path, "w", encoding="utf-8") as f:
                    f.write(action.get("content", ""))
                self.add_chat_bubble(f"📄 Fichier créé: {path}", is_user=True)
            elif typ == "remove":
                if os.path.isdir(path):
                    os.rmdir(path)
                elif os.path.isfile(path):
                    os.remove(path)
                self.add_chat_bubble(f"🗑️ Supprimé: {path}", is_user=True)
        self.model.refresh()

    @Slot()
    def on_tree_search_changed(self, text):
        """Gère le changement de texte dans le champ de recherche de l'arborescence"""
        # Cette méthode est connectée au signal search_text_changed du FileTreeWidget
        # Le filtrage est déjà géré dans le composant FileTreeWidget, donc nous n'avons pas besoin
        # d'implémenter la logique de filtrage ici.
        pass

    @Slot()
    def filter_files(self, text):
        """Méthode de compatibilité pour filtrer les fichiers (utilise file_tree.filter_tree_view).
           La logique de repli ci-dessous est conservée mais devrait utiliser le paramètre 'text'."""
        self.file_tree.filter_tree_view(text)
        # Vérifier si la recherche est vide
        if not text:
            # Si la recherche est vide, afficher tous les fichiers
            self.tree.setModel(self.model)
            return

        # Fonction récursive pour parcourir l'arborescence et afficher/masquer les éléments
        def filter_tree_items(parent_index):
            show_parent = False
            row_count = self.model.rowCount(parent_index)

            for row in range(row_count):
                child_index = self.model.index(row, 0, parent_index)
                file_name = self.model.fileName(child_index).lower()
                file_path = self.model.filePath(child_index).lower()

                # Vérifier si le nom ou le chemin contient le texte de recherche
                if text.lower() in file_name or text.lower() in file_path: # Utiliser text.lower() ici
                    self.tree.setRowHidden(row, parent_index, False)
                    show_parent = True
                else:
                    # Vérifier récursivement les enfants
                    has_visible_children = filter_tree_items(child_index)
                    self.tree.setRowHidden(row, parent_index, not has_visible_children)
                    show_parent = show_parent or has_visible_children

            return show_parent

        # Commencer le filtrage à partir de la racine
        filter_tree_items(QModelIndex())

    @Slot()
    def preview_selected_file(self):
        """Met à jour l'aperçu avec le fichier actuellement sélectionné dans l'arborescence"""
        # Récupérer l'indice sélectionné
        idx = self.file_tree.tree_view.currentIndex()
        if not idx.isValid():
            self.preview.clear()
            return

        # Récupérer le chemin
        path = self.file_tree.file_model.filePath(idx)

        # Traiter les fichiers
        if os.path.isfile(path):
            try:
                # Déterminer le type de fichier
                _, ext = os.path.splitext(path)

                # Extensions de fichiers texte courants
                text_extensions = [
                    ".txt",
                    ".py",
                    ".js",
                    ".html",
                    ".css",
                    ".json",
                    ".xml",
                    ".md",
                    ".log",
                    ".csv",
                    ".h",
                    ".c",
                    ".cpp",
                ]

                # Taille maximale pour l'aperçu
                max_size = 100 * 1024  # 100 Ko

                if os.path.getsize(path) > max_size:
                    self.preview.setPlainText(
                        f"Le fichier est trop volumineux pour un aperçu (> 100 Ko).\nChemin: {path}"
                    )
                    return

                if ext.lower() in text_extensions:
                    with open(path, "r", encoding="utf-8", errors="replace") as f:
                        content = f.read(2000)  # Limiter à 2000 caractères
                    self.preview.setPlainText(content)
                else:
                    self.preview.setPlainText(
                        f"Aperçu non disponible pour ce type de fichier ({ext}).\nChemin: {path}"
                    )
            except Exception as e:
                self.preview.setPlainText(
                    f"Erreur lors de la lecture du fichier: {str(e)}"
                )
        else:
            # Pour les dossiers, afficher des informations sur le dossier
            try:
                info = f"Dossier: {path}\n\n"
                items = os.listdir(path)
                files = [f for f in items if os.path.isfile(os.path.join(path, f))]
                dirs = [d for d in items if os.path.isdir(os.path.join(path, d))]

                info += (
                    f"Contient {len(files)} fichier(s) et {len(dirs)} sous-dossier(s)\n"
                )
                self.preview.setPlainText(info)
            except Exception as e:
                self.preview.setPlainText(
                    f"Erreur lors de la lecture du dossier: {str(e)}"
                )

    # Alias pour maintenir la compatibilité avec le code existant
    update_preview = preview_selected_file

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

    @Slot(str)
    def on_model_changed(self, model):
        """Gère le changement de modèle d'IA sélectionné dans le composant TopBarWidget

        Args:
            model (str): Le nom du modèle d'IA sélectionné
        """
        # Mise à jour du modèle sélectionné pour les futures requêtes IA
        self.add_chat_bubble(
            f"<span style='color:#4CAF50'><b>Modèle IA changé pour :</b> {model}</span>",
            is_user=False,
            icon_name="robot",
            icon_color="#4CAF50",
        )

        # Vérifier la connexion au serveur pour s'assurer que le modèle est disponible
        QTimer.singleShot(500, self.check_server_connection)

    @Slot()
    def show_project_info(self):
        """Affiche les informations sur le projet et l'application"""
        # Préparer le contenu HTML pour les informations du projet
        info_html = """
        <div style='background-color: rgba(25, 118, 210, 0.1); padding: 15px; border-radius: 10px; border-left: 5px solid #1976D2;'>
            <h3 style='color: #1976D2; margin-top: 0;'>AssistantPM - Assistant de Projet</h3>
            <p><b>Version:</b> 1.0.0</p>
            <p><b>Description:</b> Assistant IA pour la gestion et la création de projets de développement.</p>
            <p><b>Fonctionnalités:</b></p>
            <ul>
                <li>Création de squelettes d'applications</li>
                <li>Assistance IA pour le développement</li>
                <li>Gestion de projets avec différentes technologies</li>
                <li>Navigation dans l'arborescence de fichiers</li>
                <li>Interface de chat interactive</li>
            </ul>
            <p><b>Technologies:</b> Python, PySide6, Qt</p>
        </div>
        """

        # Ajouter la bulle d'information
        self.add_chat_bubble(
            info_html,
            is_user=False,
            icon_name="info-circle",
            icon_color="#1976D2",
            icon_size=24,
        )

        # Faire défiler vers le bas
        QTimer.singleShot(50, self.scroll_to_bottom)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Utiliser la racine des lecteurs par défaut
    widget = ChatArboWidget()
    widget.show()
    sys.exit(app.exec())