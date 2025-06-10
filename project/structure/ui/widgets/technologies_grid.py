"""
Composant pour afficher une grille de technologies
"""

import os
from PySide6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Signal, Qt, QTimer

from project.structure.project_type_card import ProjectTypeCard
from project.structure.back_button import BackButton

class TechnologiesGrid(QWidget):
    """
    Widget qui affiche une grille de cartes de technologies pour un type de projet
    """
    # Signaux
    technology_selected = Signal(str, str)   # Signal émis quand une technologie est sélectionnée (tech_id, project_type_id)
    back_requested = Signal()                # Signal émis quand l'utilisateur veut revenir aux types de projets
    
    def __init__(self, technologies_data, project_type_id, project_type_name, project_color, parent=None):
        super().__init__(parent)
        
        # Stocker les données
        self.technologies = technologies_data
        self.project_type_id = project_type_id
        self.project_type_name = project_type_name
        self.project_color = project_color
        self.cards = []
        
        # Configuration du layout principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        #self.main_layout.setSpacing(10)
        
        # Initialiser l'interface
        self._init_ui()
    
    def _init_ui(self):
        """Initialise l'interface utilisateur"""
        # Créer un bouton de retour
        back_button = BackButton("« Retour aux types de projets")
        back_button.clicked.connect(self.back_requested.emit)
        
        # Conteneur pour le bouton avec alignement à gauche
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        # Réduire les marges pour que le bouton soit mieux placé
        button_layout.setContentsMargins(10, 5, 0, 10)  # Un peu d'espace en bas
        button_layout.addWidget(back_button)
        button_layout.addStretch(1)  # Pousse le bouton vers la gauche
        
        # Créer un spacer pour ajouter de l'espace avant le titre
        spacer_widget = QWidget()
        spacer_widget.setFixedHeight(8)  # Hauteur fixe pour l'espace
        
        # Ajouter un titre (avec le même style et alignement que dans project_types_grid)
        title_label = QLabel(f"Sélectionnez une technologie pour {self.project_type_name} :")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 15px;
                font-weight: bold;
                color: #DDDDDD;
                padding: -1px 16px;
            }
        """)
        
        # Créer un widget pour afficher les cartes
        cards_widget = QWidget()
        self.cards_layout = QVBoxLayout(cards_widget)
        self.cards_layout.setContentsMargins(0, 5, 0, 0)
        self.cards_layout.setSpacing(15)
        
        # Ajouter les widgets dans l'ordre : bouton, spacer, titre, cartes
        self.main_layout.addWidget(spacer_widget) # Espace avant le titre
        self.main_layout.addWidget(title_label)
        self.main_layout.addWidget(cards_widget)
        self.main_layout.addWidget(button_container)
        
        # Créer la grille de cartes
        self._create_cards_grid()
    
    def _create_cards_grid(self):
        """Crée une grille de cartes pour les technologies"""
        # Nettoyer avant de créer
        self.clear_cards()
        
        # Créer le layout de grille
        grid_container = QWidget()
        grid_layout = QGridLayout(grid_container)
        grid_layout.setContentsMargins(8, 5, 8, 5)  # Harmonisation des marges
        grid_layout.setSpacing(10)
        grid_layout.setHorizontalSpacing(15)  # Plus d'espace horizontal entre les colonnes
        
        # Ajouter le conteneur au layout des cartes
        self.cards_layout.addWidget(grid_container)
        
        # Nombre de colonnes dans la grille
        num_columns = 4
        
        # Ajouter les cartes à la grille
        for i, tech in enumerate(self.technologies):
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
                    "color": self.project_color,  # Utiliser la couleur du type de projet parent
                }
                
                # Créer une carte pour la technologie
                card = ProjectTypeCard(tech_data_for_card)
                
                # Connecter le signal de clic
                card.clicked.connect(lambda checked=False, tech_id=tech["id"]: 
                    self.technology_selected.emit(tech_id, self.project_type_id))
                
                # Ajouter la carte à la grille
                grid_layout.addWidget(card, row, col)
                self.cards.append(card)
            except Exception as e:
                print(f"[ERREUR] Échec de création de la carte pour {tech['name']}: {str(e)}")
        
        # Ajouter des widgets vides pour compléter la dernière ligne si nécessaire
        total_items = len(self.technologies)
        if total_items % num_columns != 0:
            # Calculer combien de widgets vides il faut ajouter
            empty_slots = num_columns - (total_items % num_columns)
            last_row = total_items // num_columns
            # Ajouter les widgets vides
            for i in range(empty_slots):
                empty_widget = QWidget()
                empty_widget.setFixedSize(200, 70)  # Même taille qu'une ProjectTypeCard
                empty_widget.setStyleSheet("background-color: transparent;")
                grid_layout.addWidget(empty_widget, last_row, (total_items % num_columns) + i)
    
    def clear_cards(self):
        """Supprime toutes les cartes existantes"""
        self.cards = []
        
        # Supprimer tous les layouts existants
        for i in reversed(range(self.cards_layout.count())):
            layout_item = self.cards_layout.itemAt(i)
            if layout_item.widget():
                layout_item.widget().deleteLater()
