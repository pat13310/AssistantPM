"""
Composant pour afficher une grille de cartes d'aide
"""

import os
from PySide6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Signal, Qt, QTimer

from project.structure.ui.widgets.help_card import HelpCard
from project.structure.chat_bubble import ChatBubble
from project.structure.ui.ui_utils import load_colored_svg
from project.structure.back_button import BackButton


class HelpCardsGrid(QWidget):
    """
    Widget qui affiche une grille de cartes d'aide avec titre, description et icônes
    """
    # Signaux
    topic_selected = Signal(dict)  # Signal émis quand une carte d'aide est sélectionnée
    back_requested = Signal()      # Signal émis quand l'utilisateur veut revenir à la conversation
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Configuration du layout principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(8, 8, 8, 8)  # Harmonisation des marges
        self.main_layout.setSpacing(10)  # Harmonisation de l'espacement
        
        # Liste des rubriques d'aide
        self.topics = [
            {
                "title": "Création de projet",
                "description": "Créer un nouveau squelette de projet avec différentes technologies",
                "icon": "code",
                "content": "<b>Création de projet</b><br><br>Créez un nouveau projet en spécifiant les technologies souhaitées. L'assistant vous guidera dans le processus et générera un squelette de projet adapté."
            },
            {
                "title": "Navigation fichiers",
                "description": "Explorer et interagir avec les fichiers de votre projet",
                "icon": "folder-code",
                "content": "<b>Navigation dans les fichiers</b><br><br>Utilisez l'arborescence pour explorer vos fichiers ou demandez à l'IA de vous aider à retrouver et modifier des fichiers spécifiques."
            },
            {
                "title": "Aide au codage",
                "description": "Obtenir de l'aide pour résoudre des problèmes de code",
                "icon": "circle-help",
                "content": "<b>Aide au codage</b><br><br>Soumettez vos questions ou problèmes de code à l'IA pour obtenir des explications claires et des solutions adaptées."
            },
            {
                "title": "Suggestions d'amélioration",
                "description": "Recevoir des suggestions pour améliorer votre code",
                "icon": "brain",
                "content": "<b>Amélioration de code</b><br><br>Demandez à l'IA d'analyser votre code pour obtenir des suggestions d'amélioration en termes de performance, lisibilité ou bonnes pratiques."
            },
            {
                "title": "Documentation",
                "description": "Générer de la documentation pour votre code",
                "icon": "file-text",
                "content": "<b>Génération de documentation</b><br><br>Faites générer automatiquement de la documentation pour vos fonctions, classes ou modules afin de maintenir votre code bien documenté."
            }
        ]
        
        # Initialiser l'interface
        self._init_ui()
    
    def _init_ui(self):
        
        # Ajouter un titre
        title_label = QLabel(f"Sélectionnez l'aide :")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 15px;
                font-weight: bold;
                color: #DDDDDD;
                padding: 5px 10px;
            }
        """)
        
        self.main_layout.addWidget(title_label)
        
        # Créer un conteneur pour la grille de cartes
        grid_container = QWidget()
        grid_layout = QGridLayout(grid_container)
        grid_layout.setContentsMargins(8, 4, 8, 4)  # Harmonisation des marges
        grid_layout.setSpacing(10)  # Harmonisation de l'espacement
        grid_layout.setHorizontalSpacing(15)  # Plus d'espace horizontal entre les colonnes
        grid_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        # Définir le nombre de colonnes
        nb_colonnes = 4
        
        # Créer les cartes dans une disposition en grille
        for i, topic in enumerate(self.topics):
            # Calculer la position dans la grille (ligne, colonne)
            row = i // nb_colonnes
            col = i % nb_colonnes
            
            # Créer une carte pour le topic
            icon_name = topic.get("icon", "circle-help")
            
            # Chemin vers le fichier SVG original
            # Obtenir le chemin absolu vers le répertoire racine du projet
            # Le dossier racine est E:\Projets QT\AssistanPM et non pas E:\Projets QT\AssistanPM\project
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
            
            # S'assurer que le nom de l'icône n'a pas de double extension
            if icon_name.endswith(".svg"):
                icon_name = icon_name[:-4]
                
            icon_path = os.path.join(root_dir, "assets", "icons", f"{icon_name}.svg")
            
            # Les icônes sont maintenant correctement chargées
            
            # Vérifier que le fichier existe
            if not os.path.exists(icon_path):
                print(f"[Attention] Icône non trouvée: {icon_path}")
            
            # Créer la carte avec l'icône SVG
            # Nous n'avons pas besoin de charger le SVG ici, nous envoyons juste le chemin
            # La classe HelpCard utilisera load_colored_svg en interne
            card = HelpCard(
                topic_id=i,
                title=topic.get("title", "Rubrique"),
                description=topic.get("description", ""),
                icon_name=icon_path
            )
            
            # Améliorer l'apparence de la carte
            card.setFixedSize(220, 120)  # Taille fixe pour une grille uniforme
            card.setStyleSheet("""
                HelpCard {
                    background-color: #ffffff;
                    border-radius: 12px;
                    border: 1px solid #e0e0e0;
                    padding: 8px;
                }
                HelpCard:hover {
                    border: 2px solid #4CAF50;
                    background-color: #f5fff5;
                }
            """)
            
            # Connecter le signal de clic
            card.clicked.connect(
                lambda checked=False, t=topic: self.topic_selected.emit(t)
            )
            
            # Ajouter la carte au layout de grille à la position calculée
            grid_layout.addWidget(card, row, col)
        
        self.main_layout.addWidget(grid_container)
        
        # Ajouter un bouton pour revenir à la conversation
        back_button = BackButton("Retour à la conversation")
        
        back_button.clicked.connect(self.back_requested.emit)
        
        # Layout horizontal avec bouton aligné à gauche
        back_layout = QHBoxLayout()
        back_layout.setContentsMargins(10, 5, 0, 5) # Marge à gauche pour alignement avec les cartes
        back_layout.addWidget(back_button)
        back_layout.addStretch(1)  # Espace extensible à droite pour aligner à gauche
        
        back_container = QWidget()
        back_container.setLayout(back_layout)
        self.main_layout.addWidget(back_container)
        
    def set_topics(self, topics):
        """
        Mise à jour des rubriques d'aide
        
        Args:
            topics (list): Liste de dictionnaires contenant les informations des rubriques
        """
        self.topics = topics
        # Reconstruire l'interface avec les nouvelles rubriques
        # Pour une implémentation complète, il faudrait nettoyer le layout existant
        # et reconstruire la grille
