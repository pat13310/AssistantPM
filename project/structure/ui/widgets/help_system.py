"""
Système d'aide pour l'Assistant IA
Ce module définit les classes pour gérer l'affichage de rubriques d'aide dans l'interface
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QScrollArea, QStackedWidget
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont

class HelpTopic:
    """Classe représentant une rubrique d'aide"""
    
    def __init__(self, title, content, icon=None):
        """
        Initialisation d'une rubrique d'aide
        
        Args:
            title (str): Titre de la rubrique
            content (str): Contenu HTML de la rubrique
            icon (str, optional): Nom de l'icône associée
        """
        self.title = title
        self.content = content
        self.icon = icon
        self.subtopics = []  # Liste de sous-rubriques
        
    def add_subtopic(self, topic):
        """Ajoute une sous-rubrique"""
        self.subtopics.append(topic)
        return topic  # Pour permettre le chaînage
        
    def get_html(self, include_subtopics=True):
        """
        Génère le contenu HTML de la rubrique
        
        Args:
            include_subtopics (bool): Inclure les sous-rubriques
            
        Returns:
            str: Contenu HTML formaté
        """
        html = f"<h2>{self.title}</h2>{self.content}"
        
        if include_subtopics and self.subtopics:
            html += "<h3>Rubriques associées:</h3><ul>"
            for subtopic in self.subtopics:
                html += f"<li><a href='#topic:{subtopic.title}'>{subtopic.title}</a></li>"
            html += "</ul>"
            
        return html

class HelpSystem:
    """Système de gestion des rubriques d'aide"""
    
    def __init__(self):
        """Initialisation du système d'aide"""
        self.topics = {}
        self._initialize_topics()
        
    def _initialize_topics(self):
        """Initialise les rubriques d'aide par défaut"""
        # Rubrique principale: Assistant IA
        main_topic = HelpTopic(
            "Assistant IA",
            """
            <p>Bienvenue dans l'<b>Assistant IA</b> pour la gestion de projets de développement.</p>
            <p>Cette application vous permet de naviguer dans vos projets et d'interagir avec une 
            intelligence artificielle pour obtenir de l'aide sur votre code.</p>
            <p>Sélectionnez une des rubriques ci-dessous pour plus d'informations.</p>
            """
        )
        self.topics["main"] = main_topic
        
        # Rubrique: Interface utilisateur
        ui_topic = HelpTopic(
            "Interface utilisateur",
            """
            <p>L'interface se compose de deux parties principales:</p>
            <ul>
                <li><b>Explorateur de fichiers</b>: À gauche, permettant de naviguer dans vos projets</li>
                <li><b>Zone de chat</b>: À droite, pour interagir avec l'assistant IA</li>
            </ul>
            <p>La <b>barre supérieure</b> contient des boutons pour diverses actions comme effacer la conversation 
            ou générer un squelette d'application.</p>
            """
        )
        main_topic.add_subtopic(ui_topic)
        self.topics["ui"] = ui_topic
        
        # Rubrique: Commandes principales
        commands_topic = HelpTopic(
            "Commandes principales",
            """
            <p>Voici quelques commandes utiles que vous pouvez utiliser:</p>
            <ul>
                <li><b>Génère un squelette pour...</b>: Crée une structure de base pour un nouveau projet</li>
                <li><b>Explique ce code</b>: Demande une explication d'un fichier sélectionné</li>
                <li><b>Optimise cette fonction</b>: Demande des suggestions d'amélioration</li>
                <li><b>Corrige cette erreur</b>: Demande de l'aide pour résoudre un bug</li>
            </ul>
            """
        )
        main_topic.add_subtopic(commands_topic)
        self.topics["commands"] = commands_topic
        
        # Rubrique: Gestion de projet
        project_topic = HelpTopic(
            "Gestion de projet",
            """
            <p>L'assistant vous aide à gérer vos projets de développement:</p>
            <ul>
                <li>Naviguez dans l'arborescence pour explorer vos fichiers</li>
                <li>Sélectionnez un fichier pour l'analyser</li>
                <li>Demandez des conseils sur l'architecture ou l'implémentation</li>
                <li>Générez de nouveaux composants adaptés à votre projet</li>
            </ul>
            """
        )
        main_topic.add_subtopic(project_topic)
        self.topics["project"] = project_topic
        
        # Rubrique: Modèles IA
        models_topic = HelpTopic(
            "Modèles IA",
            """
            <p>L'application prend en charge différents modèles d'IA:</p>
            <ul>
                <li><b>OpenAI</b>: Modèle par défaut, polyvalent et performant</li>
                <li><b>DeepSeek</b>: Alternative optimisée pour certaines tâches</li>
            </ul>
            <p>Vous pouvez changer de modèle à tout moment via le menu déroulant dans la barre supérieure.</p>
            """
        )
        main_topic.add_subtopic(models_topic)
        self.topics["models"] = models_topic
        
        # Ajout de sous-rubriques
        coding_help = HelpTopic(
            "Aide au codage",
            """
            <p>L'assistant peut vous aider sur de nombreux aspects du développement:</p>
            <ul>
                <li>Suggestions d'algorithmes</li>
                <li>Correction de bugs</li>
                <li>Optimisation de performances</li>
                <li>Bonnes pratiques de programmation</li>
                <li>Documentation de code</li>
            </ul>
            """
        )
        commands_topic.add_subtopic(coding_help)
        self.topics["coding"] = coding_help
        
    def get_topic(self, topic_id):
        """Récupère une rubrique par son identifiant"""
        return self.topics.get(topic_id, self.topics["main"])
        
    def get_topic_html(self, topic_id):
        """Récupère le contenu HTML d'une rubrique"""
        topic = self.get_topic(topic_id)
        return topic.get_html()
        
    def get_all_topics(self):
        """Renvoie tous les sujets d'aide disponibles"""
        return self.topics.values()

from project.structure.ui.widgets.help_card import TopicCardGrid, HelpCard

class HelpDialog(QWidget):
    """Dialogue d'aide avec navigation par rubriques sous forme de cartes"""
    
    topic_selected = Signal(str)  # Signal émis quand une rubrique est sélectionnée
    back_requested = Signal()     # Signal émis quand l'utilisateur veut revenir à la vue des cartes
    
    def __init__(self, parent=None):
        """Initialisation du dialogue d'aide"""
        super().__init__(parent)
        self.help_system = HelpSystem()
        self.current_topic_id = "main"
        self.showing_cards = True  # Si True, affiche les cartes; si False, affiche une rubrique
        self._setup_ui()
        
    def _setup_ui(self):
        """Configuration de l'interface utilisateur"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(main_layout)
        
        # Titre avec bouton retour
        header_layout = QHBoxLayout()
        
        # Bouton retour (invisible au départ)
        self.back_button = QPushButton("← Retour aux rubriques")
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #4CAF50;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #2E7D32;
                text-decoration: underline;
            }
        """)
        self.back_button.clicked.connect(self._on_back_clicked)
        self.back_button.setVisible(False)  # Caché au départ
        header_layout.addWidget(self.back_button)
        
        # Titre
        title_label = QLabel("Aide - Choisissez une rubrique")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label, 1)  # 1 = stretch factor
        
        main_layout.addLayout(header_layout)
        
        # Pile de widgets pour alterner entre la vue des cartes et la vue détaillée
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)
        
        # 1. Widget de cartes de rubriques
        self.topic_cards = TopicCardGrid()
        self.topic_cards.topic_selected.connect(self._on_topic_selected)
        self.stack.addWidget(self.topic_cards)
        
        # 2. Widget de contenu détaillé
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        self.content_scroll = QScrollArea()
        self.content_scroll.setWidgetResizable(True)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        
        # Contenu de la rubrique
        self.content_label = QLabel()
        self.content_label.setWordWrap(True)
        self.content_label.setTextFormat(Qt.RichText)
        self.content_label.setOpenExternalLinks(False)
        self.content_label.linkActivated.connect(self._on_link_activated)
        self.content_label.setStyleSheet("color: #333; line-height: 1.5;")
        
        self.content_layout.addWidget(self.content_label)
        self.content_layout.addStretch()
        
        self.content_scroll.setWidget(self.content_widget)
        content_layout.addWidget(self.content_scroll)
        
        self.stack.addWidget(content_widget)
        
        # Initialiser les cartes de rubriques
        self._init_topic_cards()
        
    def _init_topic_cards(self):
        """Initialise les cartes de rubriques d'aide"""
        # Première rangée
        row1 = self.topic_cards.add_card_row()
        
        # Ajouter les cartes principales
        self.topic_cards.add_topic_card(
            row1, 
            "ui", 
            "Interface utilisateur", 
            "Découvrez les composants de l'interface et comment les utiliser efficacement.",
            "layout"
        )
        
        self.topic_cards.add_topic_card(
            row1,
            "commands",
            "Commandes principales",
            "Les commandes les plus utiles pour interagir avec l'assistant IA.",
            "command"
        )
        
        self.topic_cards.add_topic_card(
            row1,
            "project",
            "Gestion de projet",
            "Comment naviguer et gérer vos projets de développement.",
            "folder"
        )
        
        # Deuxième rangée
        row2 = self.topic_cards.add_card_row()
        
        self.topic_cards.add_topic_card(
            row2,
            "models",
            "Modèles IA",
            "Les différents modèles d'IA disponibles et leurs spécificités.",
            "cpu"
        )
        
        self.topic_cards.add_topic_card(
            row2,
            "coding",
            "Aide au codage",
            "Comment obtenir de l'aide pour vos tâches de programmation.",
            "code"
        )
        
    def _on_topic_selected(self, topic_id):
        """Gère la sélection d'une rubrique"""
        self._show_topic(topic_id)
        self.topic_selected.emit(topic_id)
        
    def _on_back_clicked(self):
        """Gère le clic sur le bouton retour"""
        self.showing_cards = True
        self.stack.setCurrentIndex(0)  # Afficher la grille de cartes
        self.back_button.setVisible(False)
        self.back_requested.emit()
        
    def _on_link_activated(self, link):
        """Gère l'activation d'un lien dans le contenu d'aide"""
        if link.startswith("#topic:"):
            topic_title = link[7:]  # Enlever "#topic:"
            # Trouver l'ID du sujet par son titre
            for topic_id, topic in self.help_system.topics.items():
                if topic.title == topic_title:
                    self._show_topic(topic_id)
                    return
        
    def _on_topic_selected(self, topic_id):
        """Gère la sélection d'une rubrique"""
        self._show_topic(topic_id)
        self.topic_selected.emit(topic_id)
        
    def _on_link_activated(self, link):
        """Gère l'activation d'un lien dans le contenu d'aide"""
        if link.startswith("#topic:"):
            topic_title = link[7:]  # Enlever "#topic:"
            # Trouver l'ID du sujet par son titre
            for topic_id, topic in self.help_system.topics.items():
                if topic.title == topic_title:
                    self._show_topic(topic_id)
                    return
                    
            # Si on ne trouve pas exactement, chercher une correspondance partielle
            for topic_id, topic in self.help_system.topics.items():
                if topic_title.lower() in topic.title.lower():
                    self._show_topic(topic_id)
                    return
        
    def _show_topic(self, topic_id):
        """Affiche le contenu d'une rubrique"""
        self.current_topic_id = topic_id
        html_content = self.help_system.get_topic_html(topic_id)
        self.content_label.setText(html_content)
        
        # Passer à la vue détaillée
        self.showing_cards = False
        self.stack.setCurrentIndex(1)  # Afficher le contenu détaillé
        self.back_button.setVisible(True)
        
    def get_current_topic_id(self):
        """Renvoie l'ID de la rubrique actuellement affichée"""
        return self.current_topic_id
