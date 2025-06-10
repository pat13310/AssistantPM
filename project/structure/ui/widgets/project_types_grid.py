"""
Composant pour afficher une grille de types de projets
"""

import os
from PySide6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Signal, Qt, QTimer

from project.structure.project_type_card import ProjectTypeCard
from project.structure.back_button import BackButton


class ProjectTypesGrid(QWidget):
    """
    Widget qui affiche une grille de cartes de types de projets
    """
    # Signaux
    project_type_selected = Signal(str)   # Signal émis quand une carte de type de projet est sélectionnée
    back_requested = Signal()             # Signal émis quand l'utilisateur veut revenir à la conversation
    
    def __init__(self, project_types, parent=None):
        super().__init__(parent)
        
        # Stocker les types de projets
        self.project_types = project_types
        self.cards = []
        
        # Configuration du layout principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(8, 8, 8, 8)  # Harmonisation des marges
        self.main_layout.setSpacing(10)  # Harmonisation de l'espacement
        
        # Initialiser l'interface
        self._init_ui()
    
    def _init_ui(self):
        """Initialise l'interface utilisateur"""
        # Créer un widget pour afficher les cartes
        # Ajouter un titre
        title_label = QLabel(f"Sélectionnez un type de projet :")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 15px;
                font-weight: bold;
                color: #DDDDDD;
                padding: 5px 10px;
            }
        """)
        
        cards_widget = QWidget()
        self.cards_layout = QVBoxLayout(cards_widget)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(10)
        
        # Ajouter le widget des cartes au layout principal
        self.main_layout.addWidget(title_label)
        self.main_layout.addWidget(cards_widget)
        
        # Créer la grille de cartes
        self._create_cards_grid()
        
        # Ajouter un bouton "Retour à la conversation" aligné à gauche
        back_button = BackButton("« Retour à l'aide")
        
        back_button.clicked.connect(self.back_requested.emit)
        
        # Conteneur pour le bouton avec alignement à gauche
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 5, 10, 5)
        button_layout.addWidget(back_button)
        button_layout.addStretch(1)  # Pousse le bouton vers la gauche
        
        # Ajouter le conteneur au layout principal
        self.main_layout.addWidget(button_container)
        
    def _create_cards_grid(self):
        """Crée une grille de cartes pour les types de projets"""
        # Nettoyer avant de créer
        self.clear_cards()
        
        # Nombre de colonnes dans la grille
        num_columns = 4
        
        # Créer la première rangée
        current_row_layout = self._create_row()
        self.cards_layout.addLayout(current_row_layout)
        
        # Ajouter les cartes à la grille
        for i, project_type in enumerate(self.project_types):
            # Si nous avons rempli une rangée, créer une nouvelle rangée
            if i > 0 and i % num_columns == 0:
                current_row_layout = self._create_row()
                self.cards_layout.addLayout(current_row_layout)
            
            # Ajouter une carte à la rangée courante
            self.add_project_type_card(current_row_layout, project_type)
        
        # Ajouter des widgets vides pour compléter la dernière ligne si nécessaire
        total_items = len(self.project_types)
        if total_items % num_columns != 0:
            # Calculer combien de widgets vides il faut ajouter
            empty_slots = num_columns - (total_items % num_columns)
            for _ in range(empty_slots):
                empty_widget = QWidget()
                empty_widget.setFixedSize(200, 70)  # Même taille qu'une ProjectTypeCard
                empty_widget.setStyleSheet("background-color: transparent;")
                current_row_layout.insertWidget(current_row_layout.count() - 1, empty_widget)
    
    def _create_row(self):
        """Crée une nouvelle rangée pour les cartes"""
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(15)  # Espacement entre les cartes, identique à technologies_grid
        
        # Ajouter un espace extensible à la fin de chaque rangée
        row_layout.addStretch(1)
        
        return row_layout
    
    def add_project_type_card(self, row_layout, project_type):
        """Ajoute une carte de type de projet à une rangée spécifique"""
        card = ProjectTypeCard(project_type)
        card.clicked.connect(lambda: self._on_card_clicked(project_type["id"]))
        row_layout.insertWidget(row_layout.count() - 1, card)  # Insérer avant le stretch
        self.cards.append(card)
        return card
    
    def _on_card_clicked(self, project_type_id):
        """Gère le clic sur une carte"""
        self.project_type_selected.emit(project_type_id)
    
    def clear_cards(self):
        """Supprime toutes les cartes existantes"""
        self.cards = []
        
        # Supprimer tous les layouts existants
        for i in reversed(range(self.cards_layout.count())):
            layout_item = self.cards_layout.itemAt(i)
            if layout_item.layout():
                # Supprimer tous les widgets de cette rangée
                row_layout = layout_item.layout()
                for j in reversed(range(row_layout.count())):
                    widget_item = row_layout.itemAt(j)
                    if widget_item.widget():
                        widget_item.widget().deleteLater()
                    elif widget_item.spacerItem():
                        row_layout.removeItem(widget_item)
                # Supprimer la rangée
                self.cards_layout.removeItem(layout_item)
