"""
Composant pour afficher une grille d'actions liées aux projets
"""

import os
from PySide6.QtWidgets import (
    QWidget,
    QGridLayout,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
)
from PySide6.QtCore import Signal, Qt, QTimer

from project.structure.ui.widgets.help_card import HelpCard
from project.structure.back_button import BackButton


class ProjectActionsGrid(QWidget):
    """
    Widget qui affiche une grille d'actions pour les projets (créer, modifier, supprimer, archiver, versionner)
    """

    # Signaux
    action_selected = Signal(dict)  # Signal émis quand une action est sélectionnée
    back_requested = (
        Signal()
    )  # Signal émis quand l'utilisateur veut revenir à la conversation

    def __init__(self, parent=None):
        super().__init__(parent)

        # Configuration du layout principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(8, 8, 8, 8)
        self.main_layout.setSpacing(10)

        # Liste des actions de projet
        self.actions = [
            {
                "id": "create",
                "title": "Créer un projet",
                "description": "Créer un nouveau projet à partir de zéro",
                "icon": "plus",
                "color": "#4CAF50",  # Vert
            },
            {
                "id": "edit",
                "title": "Modifier un projet",
                "description": "Modifier la structure ou les paramètres d'un projet existant",
                "icon": "pencil",
                "color": "#2196F3",  # Bleu
            },
            {
                "id": "delete",
                "title": "Supprimer un projet",
                "description": "Supprimer définitivement un projet existant",
                "icon": "x",
                "color": "#F44336",  # Rouge
            },
            {
                "id": "archive",
                "title": "Archiver un projet",
                "description": "Archiver un projet pour le conserver sans l'afficher",
                "icon": "file-box",
                "color": "#FF9800",  # Orange
            },
            {
                "id": "version",
                "title": "Versionner un projet",
                "description": "Gérer les versions d'un projet avec Git ou autre",
                "icon": "git-fork",
                "color": "#9C27B0",  # Violet
            },
        ]

        # Initialiser l'interface
        self._init_ui()

    def _init_ui(self):

        # Ajouter un titre
        title_label = QLabel(f"Que souhaitez-vous faire avec votre projet ?")
        title_label.setStyleSheet(
            """
            QLabel {
                font-size: 15px;
                font-weight: bold;
                color: #CCCCCC;
                padding: 5px 10px;
            }
        """
        )

        self.main_layout.addWidget(title_label)

        # Créer un conteneur pour la grille d'actions
        grid_container = QWidget()
        grid_layout = QGridLayout(grid_container)
        grid_layout.setContentsMargins(8, 4, 8, 4)
        grid_layout.setSpacing(10)
        grid_layout.setHorizontalSpacing(15)
        grid_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # Définir le nombre de colonnes
        nb_colonnes = 3

        # Créer les cartes dans une disposition en grille
        for i, action in enumerate(self.actions):
            # Calculer la position dans la grille (ligne, colonne)
            row = i // nb_colonnes
            col = i % nb_colonnes

            # Récupérer le nom de l'icône et la couleur
            icon_name = action.get("icon", "circle-help")
            icon_color = action.get("color", "#2196F3")

            # Obtenir le chemin absolu vers le répertoire racine du projet
            root_dir = os.path.dirname(
                os.path.dirname(
                    os.path.dirname(
                        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    )
                )
            )

            # S'assurer que le nom de l'icône n'a pas de double extension
            if icon_name.endswith(".svg"):
                icon_name = icon_name[:-4]

            icon_path = os.path.join(root_dir, "assets", "icons", f"{icon_name}.svg")

            # Vérifier que le fichier existe
            if not os.path.exists(icon_path):
                print(f"[Attention] Icône non trouvée: {icon_path}")

            # Créer la carte avec l'icône SVG
            card = HelpCard(
                topic_id=action.get("id", ""),
                title=action.get("title", "Action"),
                description=action.get("description", ""),
                icon_name=icon_path,
            )

            # Améliorer l'apparence de la carte
            card.setFixedSize(220, 120)
            card.setStyleSheet(
                f"""
                HelpCard {{
                    background-color: #ffffff;
                    border-radius: 12px;
                    border: 1px solid #e0e0e0;
                    padding: 8px;
                }}
                HelpCard:hover {{
                    border: 2px solid {icon_color};
                    background-color: {self._lighten_color(icon_color)};
                }}
            """
            )

            # Connecter le signal de clic
            card.clicked.connect(
                lambda checked=False, a=action: self.action_selected.emit(a)
            )

            # Ajouter la carte au layout de grille à la position calculée
            grid_layout.addWidget(card, row, col)

        self.main_layout.addWidget(grid_container)

        # Ajouter un bouton pour revenir à la conversation
        back_button = BackButton("Retour à la conversation")

        back_button.clicked.connect(self.back_requested.emit)

        # Layout horizontal avec bouton aligné à gauche
        back_layout = QHBoxLayout()
        back_layout.setContentsMargins(10, 5, 0, 5)
        back_layout.addWidget(back_button)
        back_layout.addStretch(1)

        back_container = QWidget()
        back_container.setLayout(back_layout)
        self.main_layout.addWidget(back_container)

    def _lighten_color(self, color_hex):
        """
        Éclaircit une couleur hexadécimale pour l'effet de survol

        Args:
            color_hex (str): Couleur au format hexadécimal (#RRGGBB)

        Returns:
            str: Couleur éclaircie au format rgba()
        """
        # Extraction des composants RGB
        try:
            if color_hex.startswith("#"):
                color_hex = color_hex[1:]

            # Convertir en composantes r,g,b
            if len(color_hex) == 6:
                r = int(color_hex[0:2], 16)
                g = int(color_hex[2:4], 16)
                b = int(color_hex[4:6], 16)

                # Éclaircir en ajoutant de la transparence
                return f"rgba({r}, {g}, {b}, 0.15)"
            else:
                return "#f5f5f5"  # Fallback en cas d'erreur
        except Exception:
            return "#f5f5f5"  # Fallback en cas d'erreur
