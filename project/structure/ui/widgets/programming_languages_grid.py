"""
Composant pour afficher une grille de langages de programmation
"""

import os
from PySide6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Signal, Qt, QTimer

from project.structure.project_type_card import ProjectTypeCard
from project.structure.back_button import BackButton


class ProgrammingLanguagesGrid(QWidget):
    """
    Widget qui affiche une grille de langages de programmation pour une technologie
    """
    # Signaux
    language_selected = Signal(str, str)   # Signal émis quand un langage est sélectionné (lang_id, tech_id)
    back_requested = Signal()              # Signal émis quand l'utilisateur veut revenir aux technologies
    
    def __init__(self, languages_data, technology_id, technology_name, technology_color, parent=None):
        super().__init__(parent)
        
        # Stocker les données
        self.languages = languages_data
        self.technology_id = technology_id
        self.technology_name = technology_name
        self.technology_color = technology_color
        self.cards = []
        
        # Configuration du layout principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Initialiser l'interface
        self._init_ui()
    
    def _init_ui(self):
        """Initialise l'interface utilisateur"""
        # Créer un bouton de retour
        back_button = BackButton("« Retour aux technologies")
        back_button.clicked.connect(self.back_requested.emit)
        
        # Conteneur pour le bouton avec alignement à gauche
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        # Réduire les marges pour que le bouton soit mieux placé
        button_layout.setContentsMargins(10, 5, 0, 10)
        button_layout.addWidget(back_button)
        button_layout.addStretch(1)  # Pousse le bouton vers la gauche
        
        # Créer un spacer pour ajouter de l'espace avant le titre
        spacer_widget = QWidget()
        spacer_widget.setFixedHeight(8)  # Hauteur fixe pour l'espace
        
        # Ajouter un titre
        title_label = QLabel(f"Sélectionnez un langage pour {self.technology_name} :")
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
        self.main_layout.addWidget(spacer_widget)  # Espace avant le titre
        self.main_layout.addWidget(title_label)
        self.main_layout.addWidget(cards_widget)
        self.main_layout.addWidget(button_container)
        
        # Créer la grille de cartes
        self._create_cards_grid()
    
    def _create_cards_grid(self):
        """Crée une grille de cartes pour les langages"""
        # Nettoyer avant de créer
        self.clear_cards()
        
        # Créer le layout de grille
        grid_container = QWidget()
        grid_layout = QGridLayout(grid_container)
        grid_layout.setContentsMargins(8, 5, 8, 5)
        grid_layout.setSpacing(10)
        grid_layout.setHorizontalSpacing(15)  # Plus d'espace horizontal entre les colonnes
        
        # Ajouter le conteneur au layout des cartes
        self.cards_layout.addWidget(grid_container)
        
        # Nombre de colonnes dans la grille
        num_columns = 4
        
        # Ajouter les cartes à la grille
        for i, language in enumerate(self.languages):
            # Calculer la position dans la grille (row, column)
            row = i // num_columns
            col = i % num_columns
            
            try:
                # Adapter le langage au format attendu par ProjectTypeCard
                language_data_for_card = {
                    "id": language["id"],
                    "name": language["name"],
                    "description": language.get("description", ""),
                    "icon": language.get("icon", "code"),
                    "color": self.technology_color,  # Utiliser la couleur de la technologie parente
                }
                
                # Créer une carte pour le langage
                card = ProjectTypeCard(language_data_for_card)
                
                # Connecter le signal de clic
                card.clicked.connect(lambda checked=False, lang_id=language["id"]: 
                    self.language_selected.emit(lang_id, self.technology_id))
                
                # Ajouter la carte à la grille
                grid_layout.addWidget(card, row, col)
                self.cards.append(card)
            except Exception as e:
                print(f"[ERREUR] Échec de création de la carte pour {language['name']}: {str(e)}")
        
        # Ajouter des widgets vides pour compléter la dernière ligne si nécessaire
        total_items = len(self.languages)
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
