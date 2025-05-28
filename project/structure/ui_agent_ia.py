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
)
from PySide6.QtGui import QPixmap, QFont, QColor, QPalette, QIcon, QAction, QPainter
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

# Import de la classe TopicCard depuis le fichier séparé
from topic_card import TopicCard
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


class StreamThread(QThread):
    message = Signal(str)
    finished = Signal()

    def __init__(self, user_message, model):
        super().__init__()
        self.user_message = user_message
        self.model = model

    def run(self):
        try:
            url = "http://localhost:8000/chat_stream"
            headers = {
                "accept": "text/event-stream",
                "Content-Type": "application/json",
            }
            payload = json.dumps({"message": self.user_message, "model": self.model})

            # Utiliser un timeout plus long pour éviter les interruptions
            with httpx.stream(
                "POST", url, headers=headers, content=payload, timeout=120.0
            ) as r:
                text = ""
                for line in r.iter_lines():
                    # Vérifier si line est présent
                    if line:
                        # Vérifier le type de line et convertir si nécessaire
                        if isinstance(line, bytes):
                            line_str = line.decode("utf-8")
                        else:
                            line_str = line

                        if line_str.startswith("data: "):
                            try:
                                data = json.loads(line_str[6:])
                                part = data.get("text", "")
                                text += part
                                self.message.emit(part)
                            except json.JSONDecodeError:
                                # En cas d'erreur de décodage JSON, ignorer cette ligne
                                continue
        except Exception as e:
            # En cas d'erreur, émettre un message d'erreur
            self.message.emit(
                f"<span style='color:red'>Erreur de connexion: {str(e)}</span>"
            )
        finally:
            # Toujours émettre le signal de fin
            self.finished.emit()


class ChatBubble(QFrame):
    def __init__(self, text, is_user=False):
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
        main_layout = QVBoxLayout(
            self
        )  # Ajouter self pour définir le layout sur cette instance
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(2)  # Espacement réduit entre les éléments

        # Contenu du message
        self.label = QLabel(text)  # Stocker une référence au label
        self.label.setWordWrap(True)
        font = QFont()
        font.setPointSize(11)
        self.label.setFont(font)
        self.label.setStyleSheet("border: none; background: transparent;")

        self.label.setTextFormat(
            Qt.RichText
        )  # Pour supporter le HTML dans les messages
        main_layout.addWidget(self.label)


class InteractiveChatBubble(QFrame):
    # Signal émis lorsqu'un bouton est cliqué avec le choix sélectionné
    choiceSelected = Signal(str, str)  # type, choix

    def __init__(self, title, options, bubble_type="technology", parent=None):
        super().__init__(parent)
        self.bubble_type = bubble_type

        # Style de la bulle interactive (bleu pour l'IA)
        self.setStyleSheet(
            "background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, "
            "stop:0 #2196F3, stop:1 #1976D2); "
            "border-radius: 10px; "
            "margin: 2px; "
            "padding: 8px; "
            "border: 1px solid #42A5F5;"
            "font-family: 'Roboto';"
            "font-size: 11px;"
            "color: white;"
        )

        # Layout principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        # Titre du questionnaire
        title_label = QLabel(title)
        title_label.setWordWrap(True)
        title_label.setStyleSheet(
            "font-weight: bold; font-size: 12px; border: none; background: transparent;"
        )
        self.main_layout.addWidget(title_label)

        # Conteneur pour les boutons
        buttons_widget = QWidget()
        buttons_layout = QGridLayout()
        buttons_layout.setSpacing(8)
        buttons_widget.setLayout(buttons_layout)

        # Style commun pour les boutons
        button_style = """
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
                text-align: center;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.5);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.4);
            }
        """

        # Création des boutons pour chaque option
        row, col = 0, 0
        max_cols = 3  # Nombre maximum de colonnes

        for option in options:
            button = QPushButton(option)
            button.setStyleSheet(button_style)
            button.setCursor(Qt.PointingHandCursor)
            button.clicked.connect(
                lambda checked, opt=option: self.on_button_clicked(opt)
            )
            buttons_layout.addWidget(button, row, col)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        self.main_layout.addWidget(buttons_widget)

    def on_button_clicked(self, option):
        # Émettre le signal avec le type de bulle et l'option choisie
        self.choiceSelected.emit(self.bubble_type, option)

        # Horodatage avec style amélioré
        time_layout = QHBoxLayout()
        time_layout.setContentsMargins(10, 0, 180, 0)
        time_layout.setSpacing(0)  # Espacement réduit
        current_script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root_dir = os.path.dirname(current_script_dir)
        # Utiliser l'icône 'clock-9' qui existe dans le dossier assets/icons
        test_icon_path = os.path.join(
            project_root_dir, "assets", "icons", "clock-9.svg"
        )

        svg_widget_colored = QSvgWidget()
        svg_widget_colored.load(
            load_colored_svg("assets/icons/clock-9.svg", color_str="#F5F5F5")
        )
        svg_widget_colored.setFixedSize(16, 16)

        svg_widget_colored.setStyleSheet(
            "margin-left: 10px; background: transparent; border: none;"
        )
        time_layout.addWidget(svg_widget_colored)

        # Texte de l'horodatage avec style plus discret
        time_label = QLabel(
            QDateTime.currentDateTime().toString("HH:mm")
        )  # Format plus court sans secondes
        time_label.setAlignment(Qt.AlignLeft)
        time_font = QFont("Roboto", 9)
        time_font.setItalic(True)
        time_label.setFont(time_font)
        time_label.setStyleSheet(
            "color: #F5f5f5; border: none; background: transparent; margin-top: 2px;"
        )
        time_layout.addWidget(time_label)
        time_layout.addStretch(1)  # Pour aligner à gauche

        self.main_layout.addLayout(
            time_layout
        )  # Ajouter directement le layout au lieu d'un frame

        # Pas besoin de réappliquer le layout car il est déjà défini dans __init__
        self.setMaximumWidth(500)  # Légèrement plus étroit


class ChatArboWidget(QWidget):
    def __init__(self, root_path=None):
        super().__init__()
        self.setWindowTitle("Assistant IA - Gestion de Projets")
        self.resize(1400, 800)
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

        # Arborescence avec barre de recherche
        tree_panel = QVBoxLayout()

        # Barre de recherche pour filtrer les fichiers
        search_layout = QHBoxLayout()
        search_icon = QLabel()
        pixmap = get_svg_icon("search", size=16, color="#555")
        if pixmap:
            search_icon.setPixmap(pixmap)
        search_layout.addWidget(search_icon)

        self.search_input = QLineEdit()
        self.search_input.setFixedHeight(28)
        self.search_input.setPlaceholderText("Rechercher des fichiers...")
        self.search_input.textChanged.connect(self.filter_files)
        search_layout.addWidget(self.search_input)

        tree_panel.addLayout(search_layout)

        # Arborescence
        self.model = QFileSystemModel()
        # Si aucun chemin racine n'est spécifié, utiliser la racine des lecteurs
        if root_path is None:
            root_path = ""  # Chemin vide pour afficher tous les lecteurs disponibles
        self.model.setRootPath(root_path)
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        # Si root_path est vide, ne pas définir de RootIndex spécifique pour afficher tous les lecteurs
        if root_path:
            self.tree.setRootIndex(self.model.index(root_path))
        self.tree.setColumnWidth(0, 300)
        self.tree.setStyleSheet(
            "background: #f8fafc; border-right: 1px solid #ccc;color:#333;"
        )

        # Connecter le signal de sélection du TreeView pour récupérer le chemin
        self.tree.clicked.connect(self.on_tree_item_clicked)

        # Variable pour stocker le chemin sélectionné pour la création de projet
        self.selected_project_path = None

        # Connecter le double-clic pour ouvrir les fichiers
        self.tree.doubleClicked.connect(self.on_tree_item_double_clicked)

        tree_panel.addWidget(self.tree)

        # Créer un widget pour contenir le layout de l'arborescence
        tree_widget = QWidget()
        tree_widget.setLayout(tree_panel)

        # Chat Area
        chat_panel = QVBoxLayout()

        # Barre supérieure avec statut et sélecteur de modèle sur la même ligne
        top_bar_frame = QFrame()
        top_bar_frame.setStyleSheet(
            "background-color: #2a2a2a; border-radius: 6px; padding: 4px; border: 1px solid #444444;"
        )
        top_bar_layout = QHBoxLayout(top_bar_frame)
        top_bar_layout.setContentsMargins(10, 5, 10, 5)

        # Partie gauche : statut de connexion
        status_layout = QHBoxLayout()

        # Icône de statut
        self.status_icon = QLabel()
        self.status_icon.setFixedSize(20, 20)
        self.status_icon.setStyleSheet("border: none; background: transparent;")
        # Utiliser notre fonction pour charger l'icône SVG
        disconnect_pixmap = get_svg_icon("wifi-off", size=16, color="#d32f2f")
        if disconnect_pixmap:
            self.status_icon.setPixmap(disconnect_pixmap)
        status_layout.addWidget(self.status_icon)

        self.status_indicator = QLabel("⛔ Non connecté")
        self.status_indicator.setStyleSheet(
            "color: #d32f2f; font-weight: bold;border: none;"
        )
        status_layout.addWidget(self.status_indicator)

        top_bar_layout.addLayout(status_layout)
        top_bar_layout.addStretch(1)

        # Partie centrale : sélecteur de modèle
        model_layout = QHBoxLayout()
        lb = QLabel("Modèle IA:")
        lb.setStyleSheet(
            "color: #e0e0e0; font-weight: bold; border: none; background: transparent;"
        )
        model_layout.addWidget(lb)
        self.model_choice = QComboBox()
        self.model_choice.addItems(["OpenAI", "DeepSeek"])
        self.model_choice.setFixedWidth(120)
        self.model_choice.setFixedHeight(30)
        # Utiliser le style global pour la ComboBox
        # Ajouter juste le style pour le texte en gras
        self.model_choice.setStyleSheet("font-weight: normal;")
        model_layout.addWidget(self.model_choice)

        top_bar_layout.addLayout(model_layout)

        # Ajouter un espace entre le sélecteur de modèle et les boutons d'action
        top_bar_layout.addSpacing(20)

        # Boutons d'action pour la conversation (déplacés dans la barre supérieure)
        # Style commun pour les boutons ronds
        round_button_style = """
            QPushButton {
                background-color: transparent;
                border: 1px solid #4CAF50;
                border-radius: 18px;
            }
            QPushButton:hover {
                background-color: rgba(76, 175, 80, 0.1);
                border: 2px solid #66BB6A;
            }
            QPushButton:pressed {
                background-color: rgba(76, 175, 80, 0.2);
                border: 2px solid #388E3C;
            }
        """

        # Bouton pour exporter la conversation
        self.export_btn = QPushButton()
        self.export_btn.setFixedSize(36, 36)  # Bouton rond
        export_pixmap = get_svg_icon("file-down", size=18, color="#4CAF50")
        if export_pixmap:
            self.export_btn.setIcon(QIcon(export_pixmap))
            self.export_btn.setIconSize(QSize(18, 18))
        self.export_btn.setStyleSheet(round_button_style)
        self.export_btn.setToolTip("Exporter la conversation")
        self.export_btn.clicked.connect(self.export_conversation)
        top_bar_layout.addWidget(self.export_btn)

        # Bouton pour effacer la conversation
        self.clear_btn = QPushButton()
        self.clear_btn.setFixedSize(36, 36)  # Bouton rond
        clear_pixmap = get_svg_icon("trash-2", size=18, color="#4CAF50")
        if clear_pixmap:
            self.clear_btn.setIcon(QIcon(clear_pixmap))
            self.clear_btn.setIconSize(QSize(18, 18))
        self.clear_btn.setStyleSheet(round_button_style)
        self.clear_btn.setToolTip("Effacer la conversation")
        self.clear_btn.clicked.connect(self.clear_conversation)
        top_bar_layout.addWidget(self.clear_btn)

        # Bouton pour créer un squelette d'application
        self.skeleton_btn = QPushButton()
        self.skeleton_btn.setFixedSize(36, 36)  # Bouton rond
        skeleton_pixmap = get_svg_icon("code", size=18, color="#4CAF50")
        if skeleton_pixmap:
            self.skeleton_btn.setIcon(QIcon(skeleton_pixmap))
            self.skeleton_btn.setIconSize(QSize(18, 18))
        self.skeleton_btn.setStyleSheet(round_button_style)
        self.skeleton_btn.setToolTip("Créer un squelette d'application")
        self.skeleton_btn.clicked.connect(self.start_app_skeleton_wizard)
        top_bar_layout.addWidget(self.skeleton_btn)

        # Bouton pour afficher l'historique
        self.history_btn = QPushButton()
        self.history_btn.setFixedSize(36, 36)  # Bouton rond
        history_pixmap = get_svg_icon("clock-9", size=18, color="#4CAF50")
        if history_pixmap:
            self.history_btn.setIcon(QIcon(history_pixmap))
            self.history_btn.setIconSize(QSize(18, 18))
        self.history_btn.setStyleSheet(round_button_style)
        self.history_btn.setToolTip("Historique des conversations")
        self.history_btn.clicked.connect(self.show_history)
        top_bar_layout.addWidget(self.history_btn)

        # Ajouter un espace entre les boutons d'action et le bouton de vérification
        top_bar_layout.addSpacing(10)

        # Partie droite : bouton de vérification avec icône uniquement
        self.check_connection_btn = QPushButton()
        self.check_connection_btn.setFixedSize(
            36, 36
        )  # Bouton rond pour l'icône uniquement
        # Utiliser notre fonction pour charger l'icône SVG en vert
        refresh_pixmap = get_svg_icon("rotate-cw", size=18, color="#4CAF50")
        if refresh_pixmap:
            self.check_connection_btn.setIcon(QIcon(refresh_pixmap))
            self.check_connection_btn.setIconSize(QSize(18, 18))

        # Utiliser le même style que les autres boutons ronds
        self.check_connection_btn.setStyleSheet(round_button_style)

        self.check_connection_btn.setToolTip("Vérifier la connexion au serveur IA")
        self.check_connection_btn.clicked.connect(self.check_server_connection)
        top_bar_layout.addWidget(self.check_connection_btn)

        chat_panel.addWidget(top_bar_frame)

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

        # Aperçu fichier sélectionné
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setMinimumHeight(120)
        self.preview.setStyleSheet(
            "background: #f6fafd; font-family: monospace; border: 1px solid #e0e0e0;"
        )
        chat_panel.addWidget(QLabel("Aperçu du fichier sélectionné:"))
        chat_panel.addWidget(self.preview, 1)

        self.send_btn.clicked.connect(self.send_message)
        self.tree.selectionModel().selectionChanged.connect(self.update_preview)
        self.tree.clicked.connect(self.on_tree_clicked)

        self.stream_thread = None

        # Variables pour gestion actions à valider
        self.pending_actions = []

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

    @Slot()
    def on_tree_item_clicked(self, index):
        # Récupérer le chemin complet de l'élément cliqué
        path = self.model.filePath(index)
        # Stocker le chemin sélectionné pour la création de projet
        self.selected_project_path = path
        # Afficher un message de confirmation discret dans la barre d'état
        self.status_indicator.setText(f"Chemin sélectionné: {os.path.basename(path)}")
        self.status_indicator.setStyleSheet(
            "color: #4CAF50; font-weight: bold; border: none; background: transparent;"
        )
        # Rétablir le message normal après 3 secondes
        QTimer.singleShot(3000, self.reset_status_message)

    @Slot()
    def on_tree_item_double_clicked(self, index):
        # Récupérer le chemin complet de l'élément double-cliqué
        path = self.model.filePath(index)
        # Si c'est un fichier, l'ouvrir dans l'aperçu
        if os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.preview.setText(content)
            except Exception as e:
                self.preview.setText(f"Erreur lors de l'ouverture du fichier: {str(e)}")

    def reset_status_message(self):
        # Rétablir le message de statut normal
        if self.server_connected:
            self.status_indicator.setText("Connecté")
            self.status_indicator.setStyleSheet(
                "color: #4CAF50; font-weight: bold; border: none; background: transparent;"
            )
        else:
            self.status_indicator.setText("Non connecté")
            self.status_indicator.setStyleSheet(
                "color: #d32f2f; font-weight: bold; border: none; background: transparent;"
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

    @Slot()
    def check_server_connection(self):
        """Vérifie si le serveur IA est en cours d'exécution et met à jour l'indicateur de statut"""
        try:
            # Tenter une connexion rapide pour vérifier si le serveur est actif
            response = httpx.get("http://localhost:8000/health", timeout=2.0)
            if response.status_code == 200:
                self.server_connected = True
                self.status_indicator.setText("Connecté au serveur IA")
                self.status_indicator.setStyleSheet(
                    "color: #2e7d32; font-weight: bold; border: none; background: transparent;"
                )

                # Changer l'icône pour indiquer la connexion avec une icône verte
                connect_pixmap = get_svg_icon("check", size=16, color="#4CAF50")
                if connect_pixmap:
                    self.status_icon.setPixmap(connect_pixmap)

                return True
            else:
                self.server_connected = False
                self.status_indicator.setText("Erreur de connexion")
                self.status_indicator.setStyleSheet(
                    "color: #d32f2f; font-weight: bold; border: none; background: transparent;"
                )

                # Changer l'icône pour indiquer l'erreur
                error_pixmap = get_svg_icon("alert-circle", size=16, color="#d32f2f")
                if error_pixmap:
                    self.status_icon.setPixmap(error_pixmap)

                return False
        except Exception:
            self.server_connected = False
            self.status_indicator.setText("Serveur IA non disponible")
            self.status_indicator.setStyleSheet(
                "color: #d32f2f; font-weight: bold; border: none; background: transparent;"
            )

            # Changer l'icône pour indiquer la déconnexion
            disconnect_pixmap = get_svg_icon("wifi-off", size=16, color="#d32f2f")
            if disconnect_pixmap:
                self.status_icon.setPixmap(disconnect_pixmap)

            return False

    @Slot()
    def send_message(self):
        user_text = self.user_input.toPlainText().strip()
        print("send_message")
        if not user_text:
            return
        self.user_input.clear()

        # Ajout bulle utilisateur
        self.add_chat_bubble(user_text, is_user=True)

        # Convertir le texte en minuscules pour la comparaison
        text_lower = user_text.lower()

        # Si l'utilisateur tape "aide", afficher directement les cartes d'aide
        if "aide" in text_lower or "help" in text_lower:
            # Afficher les cartes de rubriques sans message de salutation
            self.add_topic_cards_bubble()
            return

        # Vérifier si le message concerne la création d'un projet
        if ("créer" in text_lower or "générer" in text_lower) and (
            "projet" in text_lower
            or "structure" in text_lower
            or "dossier" in text_lower
        ):
            # Récupérer le chemin racine pour la création du projet
            project_path = self.get_project_root_path()
            if not project_path:
                self.add_chat_bubble(
                    "<span style='color:orange'>⚠️ Veuillez sélectionner un dossier pour la création du projet.</span>",
                    is_user=False,
                )
                return

            # Ajouter le chemin au message pour le serveur IA
            user_text += f"\nChemin du projet: {project_path}"

        # Vérifier si le serveur IA est en cours d'exécution
        if not self.check_server_connection():
            # Démarrer le serveur IA s'il n'est pas en cours d'exécution
            self.add_chat_bubble(
                "<span style='color:orange'>⚠️ Tentative de démarrage du serveur IA...</span>",
                is_user=False,
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
                    )
                    return
            except Exception as e:
                self.add_chat_bubble(
                    f"<span style='color:red'>⚠️ Erreur: {str(e)}</span>", is_user=False
                )
                return

        # Continuer avec le traitement normal
        self.add_chat_bubble("⏳ L'IA réfléchit...", is_user=False)
        model = self.model_choice.currentText().lower()
        self.stream_thread = StreamThread(user_text, model)
        self.stream_thread.message.connect(self.update_ia_bubble)
        self.stream_thread.finished.connect(self.handle_ia_finished)
        self.current_ia_text = ""
        self.stream_thread.start()

    def add_chat_bubble(self, text, is_user=False):
        bubble = ChatBubble(text, is_user)

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
        main_layout = QHBoxLayout(main_container)  # Layout vertical pour empiler les cartes
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(8)

        # Créer une bulle pour chaque topic
        for topic in topics:
            # Créer une carte pour le topic
            icon_name = topic.get("icon", "circle-help")
            
            # Chemin vers le fichier SVG original
            icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "assets", "icons", f"{icon_name}.svg")
            
            # Créer un fichier SVG temporaire coloré en vert
            #temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
            #svg_path = os.path.join(icon_path, f"{icon_name}.svg")
            
            # Créer la carte avec l'icône SVG verte
            card = TopicCard(
                title=topic["title"],
                description=topic["description"],
                icon_pixmap=icon_path
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

        return main_container

    def handle_topic_selection(self, topic):
        """Gère la sélection d'une rubrique"""
        # Ajouter le choix de l'utilisateur comme message
        self.add_chat_bubble(f"Je souhaite de l'aide sur : {topic}", is_user=True)

        # Traiter la sélection en fonction de la rubrique choisie
        if topic == "Création de projet":
            self.start_app_skeleton_wizard()
        elif topic == "Navigation fichiers":
            self.add_chat_bubble(
                "Pour naviguer dans vos fichiers, utilisez l'explorateur à gauche. "
                "Vous pouvez cliquer sur un fichier pour le sélectionner ou double-cliquer pour l'ouvrir. "
                "La barre de recherche en haut vous permet de filtrer les fichiers.",
                is_user=False,
            )
        elif topic == "Aide au codage":
            self.add_chat_bubble(
                "Je peux vous aider à résoudre des problèmes de code. "
                "Décrivez-moi le problème que vous rencontrez ou posez-moi une question spécifique sur votre code.",
                is_user=False,
            )
        elif topic == "Suggestions d'amélioration":
            self.add_chat_bubble(
                "Je peux analyser votre code et vous suggérer des améliorations. "
                "Sélectionnez un fichier dans l'explorateur et demandez-moi de l'analyser.",
                is_user=False,
            )
        elif topic == "Documentation":
            self.add_chat_bubble(
                "Je peux générer de la documentation pour votre code. "
                "Sélectionnez un fichier ou une fonction spécifique et demandez-moi de documenter.",
                is_user=False,
            )
        else:
            self.add_chat_bubble(
                f"Je vais vous aider concernant '{topic}'. Que souhaitez-vous savoir exactement ?",
                is_user=False,
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

        return bubble_container

    def on_interactive_choice(self, bubble_type, choice):
        """Gère la sélection d'une option dans une bulle interactive"""
        # Ajouter le choix de l'utilisateur comme message
        self.add_chat_bubble(f"J'ai choisi: {choice}", is_user=True)

        if bubble_type == "technology":
            # L'utilisateur a choisi une technologie, proposer les types d'applications
            app_types = self.get_app_types_for_technology(choice)
            self.add_interactive_bubble(
                f"Quel type d'application {choice} souhaitez-vous créer ?",
                app_types,
                bubble_type="app_type",
            )

        elif bubble_type == "app_type":
            # L'utilisateur a choisi un type d'application, proposer des fonctionnalités
            features = self.get_features_for_app_type(choice)
            self.add_interactive_bubble(
                f"Quelles fonctionnalités souhaitez-vous inclure dans votre {choice} ?",
                features,
                bubble_type="features",
            )

        elif bubble_type == "features":
            # L'utilisateur a choisi des fonctionnalités, générer un résumé
            self.add_chat_bubble(
                "Je vais maintenant générer un squelette d'application basé sur vos choix. "
                "Veuillez patienter un instant..."
            )
            # Simuler un délai pour la génération
            QTimer.singleShot(1500, self.generate_app_skeleton)

    def get_app_types_for_technology(self, technology):
        """Retourne les types d'applications disponibles pour une technologie donnée"""
        app_types = {
            "Python": [
                "Application Web",
                "API REST",
                "Application Desktop",
                "Script CLI",
                "Analyse de données",
            ],
            "JavaScript": [
                "Site Web",
                "Application SPA",
                "API REST",
                "Application Mobile",
            ],
            "React": [
                "Application Web",
                "Application Mobile",
                "Dashboard",
                "E-commerce",
            ],
            "C++": ["Application Desktop", "Jeu", "Système embarqué", "Bibliothèque"],
            "C#": [
                "Application Windows",
                "Application Web ASP.NET",
                "Jeu Unity",
                "API REST",
            ],
            "Vite": ["Application Vue.js", "Application React", "Site Statique", "PWA"],
            "Svelte": ["Application Web", "Application SPA", "Site Statique", "PWA"],
        }
        return app_types.get(technology, ["Application simple", "Projet de base"])

    def get_features_for_app_type(self, app_type):
        """Retourne les fonctionnalités disponibles pour un type d'application donné"""
        features = {
            "Application Web": [
                "Authentification",
                "Base de données",
                "API REST",
                "Upload de fichiers",
                "Thème sombre/clair",
            ],
            "API REST": [
                "Authentification JWT",
                "Documentation Swagger",
                "Validation des données",
                "Cache",
                "Tests unitaires",
            ],
            "Application Desktop": [
                "Interface graphique",
                "Persistance des données",
                "Mises à jour auto",
                "Thèmes",
            ],
            "Application Mobile": [
                "Navigation",
                "État global",
                "Mode hors ligne",
                "Notifications",
                "Caméra/Photos",
            ],
            "Jeu": [
                "Moteur physique",
                "Système de score",
                "Sauvegarde",
                "Audio",
                "Contrôles",
            ],
        }
        # Fonctionnalités par défaut pour les types non listés
        default_features = [
            "Structure de base",
            "README",
            "Tests",
            "Documentation",
            "CI/CD",
        ]
        return features.get(app_type, default_features)

    def generate_app_skeleton(self):
        """Génère un squelette d'application basé sur les choix de l'utilisateur"""
        # Cette méthode serait connectée à l'API pour générer le squelette
        # Pour l'instant, nous affichons simplement un message de confirmation
        self.add_chat_bubble(
            "<b>Votre squelette d'application est prêt !</b><br><br>"
            "J'ai créé une structure de projet basée sur vos choix. "
            "Vous pouvez maintenant télécharger le code ou continuer à personnaliser votre projet."
        )

    def start_app_skeleton_wizard(self):
        """Démarre l'assistant de création de squelette d'application"""
        technologies = ["Python", "JavaScript", "React", "C++", "C#", "Vite", "Svelte"]
        self.add_chat_bubble(
            "<b>Bienvenue dans l'assistant de création de squelette d'application !</b><br><br>"
            "Je vais vous guider à travers le processus de création d'un nouveau projet. "
            "Commençons par choisir la technologie que vous souhaitez utiliser."
        )
        self.add_interactive_bubble(
            "Choisissez une technologie :", technologies, "technology"
        )

    def on_interactive_choice(self, bubble_type, choice):
        """Gère la sélection d'une option dans une bulle interactive"""
        # Ajouter le choix de l'utilisateur comme message
        self.add_chat_bubble(f"J'ai choisi: {choice}", is_user=True)

        if bubble_type == "technology":
            # L'utilisateur a choisi une technologie, proposer les types d'applications
            app_types = self.get_app_types_for_technology(choice)
            self.add_chat_bubble(
                f"Pour la technologie <b>{choice}</b>, voici les types d'applications possibles :",
                is_user=False,
            )
            self.add_interactive_bubble(
                f"Quel type d'application {choice} souhaitez-vous créer ?",
                app_types,
                bubble_type="app_type",
            )

        elif bubble_type == "app_type":
            # L'utilisateur a choisi un type d'application, proposer des fonctionnalités
            features = self.get_features_for_app_type(choice)
            self.add_chat_bubble(
                f"Pour une application de type <b>{choice}</b>, voici les fonctionnalités que je peux inclure :",
                is_user=False,
            )
            self.add_interactive_bubble(
                f"Quelles fonctionnalités souhaitez-vous inclure dans votre {choice} ?",
                features,
                bubble_type="features",
            )

        elif bubble_type == "features":
            # L'utilisateur a choisi des fonctionnalités, générer un résumé
            self.add_chat_bubble(
                "Je vais maintenant générer un squelette d'application basé sur vos choix. "
                "Veuillez patienter un instant...",
                is_user=False,
            )
            # Simuler un délai pour la génération
            QTimer.singleShot(1500, self.generate_app_skeleton)

    def get_app_types_for_technology(self, technology):
        """Retourne les types d'applications disponibles pour une technologie donnée"""
        app_types = {
            "Python": [
                "Application Web",
                "API REST",
                "Application Desktop",
                "Script CLI",
                "Analyse de données",
            ],
            "JavaScript": [
                "Site Web",
                "Application SPA",
                "API REST",
                "Application Mobile",
            ],
            "React": [
                "Application Web",
                "Application Mobile",
                "Dashboard",
                "E-commerce",
            ],
            "C++": ["Application Desktop", "Jeu", "Système embarqué", "Bibliothèque"],
            "C#": [
                "Application Windows",
                "Application Web ASP.NET",
                "Jeu Unity",
                "API REST",
            ],
            "Vite": ["Application Vue.js", "Application React", "Site Statique", "PWA"],
            "Svelte": ["Application Web", "Application SPA", "Site Statique", "PWA"],
        }
        return app_types.get(technology, ["Application simple", "Projet de base"])

    def get_features_for_app_type(self, app_type):
        """Retourne les fonctionnalités disponibles pour un type d'application donné"""
        features = {
            "Application Web": [
                "Authentification",
                "Base de données",
                "API REST",
                "Upload de fichiers",
                "Thème sombre/clair",
            ],
            "API REST": [
                "Authentification JWT",
                "Documentation Swagger",
                "Validation des données",
                "Cache",
                "Tests unitaires",
            ],
            "Application Desktop": [
                "Interface graphique",
                "Persistance des données",
                "Mises à jour auto",
                "Thèmes",
            ],
            "Application Mobile": [
                "Navigation",
                "État global",
                "Mode hors ligne",
                "Notifications",
                "Caméra/Photos",
            ],
            "Jeu": [
                "Moteur physique",
                "Système de score",
                "Sauvegarde",
                "Audio",
                "Contrôles",
            ],
        }
        # Fonctionnalités par défaut pour les types non listés
        default_features = [
            "Structure de base",
            "README",
            "Tests",
            "Documentation",
            "CI/CD",
        ]
        return features.get(app_type, default_features)

    def generate_app_skeleton(self):
        """Génère un squelette d'application basé sur les choix de l'utilisateur"""
        # Cette méthode serait connectée à l'API pour générer le squelette
        # Pour l'instant, nous affichons simplement un message de confirmation
        self.add_chat_bubble(
            "<b>Votre squelette d'application est prêt !</b><br><br>"
            "J'ai créé une structure de projet basée sur vos choix. "
            "Vous pouvez maintenant télécharger le code ou continuer à personnaliser votre projet.",
            is_user=False,
        )

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

    @Slot()
    def on_tree_clicked(self, index):
        # Récupérer le chemin de l'élément cliqué
        path = self.model.filePath(index)
        # Vérifier si c'est un lecteur (comme C:, D:, etc.)
        if os.path.splitdrive(path)[1] == "":
            drive_letter = os.path.splitdrive(path)[0]
            # Afficher un message dans le chat
            self.add_chat_bubble(
                f"<b>Lecteur sélectionné :</b> {drive_letter}", is_user=False
            )
            drive_info = self.get_drive_info(drive_letter)
            self.add_chat_bubble(drive_info, is_user=False)

    def show_action_buttons(self):
        # Propose à l'utilisateur d'accepter/refuser les actions
        btns = QHBoxLayout()
        btn_yes = QPushButton("Valider les actions")
        btn_no = QPushButton("Refuser")
        btns.addWidget(btn_yes)
        btns.addWidget(btn_no)

        def accept():
            self.apply_actions(self.pending_actions)
            self.pending_actions = []
            btn_yes.setEnabled(False)
            btn_no.setEnabled(False)

        def refuse():
            self.add_chat_bubble(" Action(s) refusée(s).", is_user=True)
            btn_yes.setEnabled(False)
            btn_no.setEnabled(False)

        btn_yes.clicked.connect(accept)
        btn_no.clicked.connect(refuse)
        frame = QFrame()
        frame.setLayout(btns)
        self.chat_layout.addWidget(frame)
        self.scroll.verticalScrollBar().setValue(
            self.scroll.verticalScrollBar().maximum()
        )

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
    def filter_files(self):
        """Filtre les fichiers dans l'arborescence en fonction du texte de recherche"""
        search_text = self.search_input.toPlainText().strip().lower()
        if not search_text:
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
                if search_text in file_name or search_text in file_path:
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
    def update_preview(self):
        idx = self.tree.currentIndex()
        if not idx.isValid():
            self.preview.clear()
            return
        path = self.model.filePath(idx)
        if os.path.isfile(path):
            try:
                with open(path, encoding="utf-8") as f:
                    txt = f.read(800)
                self.preview.setPlainText(txt)
            except Exception:
                self.preview.setPlainText("Impossible d'afficher le contenu.")
        else:
            self.preview.setPlainText("")

    def export_conversation(self):
        """Exporter la conversation actuelle dans un fichier"""
        if not self.current_conversation:
            QMessageBox.information(
                self, "Information", "Aucune conversation à exporter."
            )
            return

        # Demander à l'utilisateur où sauvegarder le fichier
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter la conversation",
            os.path.join(os.path.expanduser("~"), "conversation.json"),
            "Fichiers JSON (*.json);;Fichiers texte (*.txt);;Tous les fichiers (*.*)",
        )

        if not file_path:
            return  # L'utilisateur a annulé

        try:
            # Préparer les données de la conversation
            conversation_data = {
                "id": self.current_conversation_id,
                "timestamp": datetime.datetime.now().isoformat(),
                "messages": self.current_conversation,
            }

            # Sauvegarder selon le format choisi
            if file_path.endswith(".json"):
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(conversation_data, f, ensure_ascii=False, indent=2)
            else:  # Format texte
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(
                        f"Conversation du {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n"
                    )
                    for msg in self.current_conversation:
                        sender = "Vous" if msg["is_user"] else "IA"
                        f.write(f"[{sender}] {msg['text']}\n\n")

            QMessageBox.information(
                self, "Succès", f"Conversation exportée avec succès vers {file_path}"
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Erreur", f"Erreur lors de l'exportation: {str(e)}"
            )

    def clear_conversation(self):
        """Effacer la conversation actuelle"""
        if not self.current_conversation:
            return

        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Voulez-vous vraiment effacer cette conversation ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            # Sauvegarder la conversation actuelle dans l'historique
            self.save_current_conversation()

            # Effacer les widgets de la conversation
            for i in reversed(range(self.chat_layout.count())):
                widget = self.chat_layout.itemAt(i).widget()
                if widget:
                    widget.setParent(None)

            # Créer une nouvelle conversation
            self.current_conversation_id = str(uuid.uuid4())
            self.current_conversation = []

            # Ajouter un message de bienvenue
            self.add_chat_bubble(
                "<b>Nouvelle conversation commencée.</b>", is_user=False
            )

    def save_current_conversation(self):
        """Sauvegarder la conversation actuelle dans l'historique"""
        if not self.current_conversation:
            return

        # Préparer les données de la conversation
        conversation_data = {
            "id": self.current_conversation_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "preview": self.get_conversation_preview(),
            "messages": self.current_conversation,
        }

        # Ajouter à l'historique (en limitant à 20 conversations)
        self.conversation_history.append(conversation_data)
        if len(self.conversation_history) > 20:
            self.conversation_history.pop(0)  # Supprimer la plus ancienne

    def get_conversation_preview(self):
        """Obtenir un aperçu de la conversation pour l'historique"""
        if not self.current_conversation:
            return "Conversation vide"

        # Trouver le premier message utilisateur
        for msg in self.current_conversation:
            if msg["is_user"]:
                # Tronquer si nécessaire
                preview = msg["text"]
                if len(preview) > 50:
                    preview = preview[:47] + "..."
                return preview

        return "Conversation sans message utilisateur"

    def show_history(self):
        """Afficher l'historique des conversations"""
        if not self.conversation_history:
            QMessageBox.information(
                self, "Historique", "Aucune conversation dans l'historique."
            )
            return

        # Créer une fenêtre pour afficher l'historique
        history_dialog = QMessageBox(self)
        history_dialog.setWindowTitle("Historique des conversations")

        # Préparer le texte de l'historique
        history_text = "<h3>Historique des conversations</h3><ul>"
        for i, conv in enumerate(reversed(self.conversation_history)):
            timestamp = datetime.datetime.fromisoformat(conv["timestamp"]).strftime(
                "%d/%m/%Y %H:%M"
            )
            preview = conv["preview"]
            history_text += f"<li><b>{timestamp}</b>: {preview}</li>"
        history_text += "</ul>"

        history_dialog.setText(history_text)
        history_dialog.setTextFormat(Qt.RichText)
        history_dialog.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Utiliser la racine des lecteurs par défaut
    widget = ChatArboWidget()
    widget.show()
    sys.exit(app.exec())
