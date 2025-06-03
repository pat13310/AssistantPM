"""
Composant pour gérer l'affichage et l'interaction avec les types de projets
"""
import os
from PySide6.QtWidgets import (
    QWidget, 
    QVBoxLayout, 
    QLabel, 
    QHBoxLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtSvgWidgets import QSvgWidget
from project.structure.project_creator_show import ProjectCreatorShow
from ui.ui_utils import load_colored_svg

class ProjectTypesWidget(QWidget):
    """Widget pour afficher et gérer les types de projets"""
    
    # Signaux
    project_type_selected = Signal(str)
    technology_selected = Signal(str)
    app_type_selected = Signal(str)
    feature_selected = Signal(str)
    project_creation_requested = Signal(str, str, list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialiser les variables
        self.project_show = ProjectCreatorShow()
        self.bubbles = []
        
        # Connecter les signaux de ProjectCreatorShow
        self.project_show.technology_selected.connect(self.technology_selected)
        self.project_show.app_type_selected.connect(self.app_type_selected)
        self.project_show.feature_selected.connect(self.feature_selected)
        self.project_show.project_creation_requested.connect(self.project_creation_requested)
        
        # Configurer le layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(5)
        
    def add_bubble(self, text, is_user=False, extra_properties=None):
        """
        Crée une bulle de chat générique
        
        Args:
            text (str): Texte à afficher dans la bulle
            is_user (bool): True si c'est une bulle utilisateur, False sinon
            extra_properties (dict): Propriétés supplémentaires à stocker dans la bulle
            
        Returns:
            QWidget: Le widget de la bulle créée
        """
        print(f"Création d'une bulle: {text[:30]}...")
        
        # Créer le widget de bulle
        bubble = QWidget()
        bubble_layout = QVBoxLayout(bubble)
        bubble_layout.setContentsMargins(10, 10, 10, 10)
        
        # Créer le label pour le texte
        label = QLabel(text)
        label.setTextFormat(Qt.RichText)
        label.setWordWrap(True)
        bubble_layout.addWidget(label)
        
        # Appliquer un style de base
        bubble.setStyleSheet(
            "background-color: rgba(42, 42, 42, 0.7); "
            "border-radius: 4px; padding: 8px;"
        )
        
        # Stocker les propriétés supplémentaires dans le widget
        if extra_properties:
            for key, value in extra_properties.items():
                print(f"Ajout de la propriété {key} = {value}")
                bubble.setProperty(key, value)
        
        # Ajouter la bulle au layout
        self.main_layout.addWidget(bubble)
        self.bubbles.append(bubble)
        print(f"Bulle ajoutée au layout. Total bulles: {len(self.bubbles)}")
        
        # S'assurer que le widget est visible
        bubble.setVisible(True)
        bubble.show()
        
        return bubble
        
    def clear_bubbles(self, property_name=None, property_value=None):
        """
        Efface les bulles en fonction d'une propriété spécifique
        
        Args:
            property_name (str): Nom de la propriété à vérifier
            property_value: Valeur de la propriété à vérifier
        """
        bubbles_to_remove = []
        
        for bubble in self.bubbles:
            if property_name is None or (hasattr(bubble, property_name) and getattr(bubble, property_name) == property_value):
                bubble.setVisible(False)
                bubble.deleteLater()
                bubbles_to_remove.append(bubble)
                
        # Retirer les bulles supprimées de la liste
        for bubble in bubbles_to_remove:
            if bubble in self.bubbles:
                self.bubbles.remove(bubble)
    
    def display_project_types(self):
        """Affiche les types de projets disponibles"""
        print("Début de l'affichage des types de projets")
        
        # Vérification que le layout est prêt
        if not self.main_layout:
            print("ERREUR: main_layout n'est pas initialisé")
            self.main_layout = QVBoxLayout(self)
            self.main_layout.setContentsMargins(0, 0, 0, 0)
            self.main_layout.setSpacing(5)
        
        # Effacer les bulles précédentes
        self.clear_bubbles("project_type_bubble", True)
        
        # Obtenir les données des types de projets
        project_types = self.project_show.get_project_types_data()
        print(f"Nombre de types de projets trouvés: {len(project_types)}")
        
        # Vérifier que les données sont bien reçues
        if not project_types:
            print("ERREUR: Aucun type de projet trouvé!")
            return
        
        # Débogage - afficher les types de projets trouvés
        for i, pt in enumerate(project_types):
            print(f"  Type {i+1}: {pt.get('name', 'Nom inconnu')} (id: {pt.get('id', 'ID inconnu')})")
        
        # Forcer la visibilité du widget
        self.setVisible(True)
        
        # Créer un message pour introduire les types de projets
        intro_bubble = self.add_bubble("Sélectionnez un type de projet :", extra_properties={"project_type_bubble": True})
        
        # Créer une bulle pour chaque type de projet
        for i, project_type in enumerate(project_types):
            # Afficher des informations de débogage
            print(f"Traitement du type de projet {i+1}/{len(project_types)}: {project_type['name']}")
            
            # Préparer le chemin de l'icône
            icon_name = project_type.get('icon', 'code')
            icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets', 'icons', f"{icon_name}.svg")
            
            # Vérifier si l'icône existe
            if not os.path.exists(icon_path):
                print(f"[ATTENTION] Icône non trouvée: {icon_path}, utilisation de l'icône par défaut")
                # Utiliser une icône par défaut si l'icône spécifiée n'existe pas
                icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets', 'icons', "code.svg")
                # Vérifier si l'icône par défaut existe
                if not os.path.exists(icon_path):
                    print(f"[ERREUR] Icône par défaut non trouvée: {icon_path}")
            
            try:
                # Charger l'icône avec la couleur du type de projet
                svg_content = load_colored_svg(icon_path, color_str=project_type['color'])
                
                # Créer le texte pour la bulle avec l'icône
                text = f"<b>{project_type['name']}</b>"
                if 'description' in project_type:
                    text += f"<br><span style='color: #aaaaaa; font-size: 12px;'>{project_type['description']}</span>"
                
                # Ajouter la bulle
                bubble = self.add_bubble(text, extra_properties={
                    "project_type_id": project_type['id'],
                    "project_type_bubble": True
                })
                
                try:
                    # Appliquer un style spécifique à la bulle en fonction de la couleur du type de projet
                    for child in bubble.findChildren(QLabel):
                        try:
                            print(f"Configuration du style pour {project_type['name']}")
                            
                            # Remplacer le layout existant par un layout horizontal
                            old_layout = child.layout()
                            if old_layout:
                                while old_layout.count():
                                    item = old_layout.takeAt(0)
                                    if item.widget():
                                        item.widget().deleteLater()
                                old_layout.deleteLater()
                            
                            # Créer un nouveau layout horizontal
                            h_layout = QHBoxLayout(child)
                            h_layout.setContentsMargins(5, 5, 5, 5)
                            h_layout.setSpacing(10)
                            
                            # Ajouter l'icône SVG seulement si on a pu la charger
                            if svg_content:
                                svg_widget = QSvgWidget()
                                svg_widget.load(svg_content)
                                svg_widget.setFixedSize(24, 24)  # Taille de l'icône
                                h_layout.addWidget(svg_widget, 0, Qt.AlignVCenter)
                            else:
                                print(f"[ATTENTION] Contenu SVG vide pour {project_type['name']}")
                            
                            # Ajouter le texte
                            text_label = QLabel(text)
                            text_label.setTextFormat(Qt.RichText)
                            text_label.setWordWrap(True)
                            h_layout.addWidget(text_label, 1, Qt.AlignVCenter)
                            
                            # Appliquer un style avec une bordure de couleur mais sans fond bleu
                            child.setStyleSheet(f"border-left: 4px solid {project_type['color']}; padding-left: 10px; background-color: rgba(42, 42, 42, 0.7); border-radius: 4px;")
                            
                            # Rendre la bulle cliquable
                            child.setTextInteractionFlags(Qt.TextBrowserInteraction)
                            child.mousePressEvent = lambda event, pt_id=project_type['id']: self.on_project_type_selected(pt_id)
                            
                            print(f"Style appliqué avec succès pour {project_type['name']}")
                        except Exception as e:
                            print(f"[ERREUR] Échec de l'application du style pour {project_type['name']}: {str(e)}")
                except Exception as e:
                    print(f"[ERREUR] Échec global pour {project_type['name']}: {str(e)}")
                
                print(f"Bulle créée avec succès pour: {project_type['name']}")
            except Exception as e:
                print(f"[ERREUR] Échec de création de la bulle pour {project_type['name']}: {str(e)}")
                # Continuer avec le prochain type de projet en cas d'erreur
                continue
    
    def on_project_type_selected(self, project_type_id):
        """Gère la sélection d'un type de projet"""
        print(f"Type de projet sélectionné: {project_type_id}")
        
        # Émettre le signal pour informer le parent
        self.project_type_selected.emit(project_type_id)
        
        # Obtenir les technologies pour ce type de projet
        technologies = self.project_show.select_project_type(project_type_id)
        
        # Afficher les technologies
        self.display_technologies(technologies, project_type_id)
    
    def display_technologies(self, technologies, project_type_id):
        """Affiche les technologies disponibles pour un type de projet"""
        # Effacer les bulles précédentes
        self.clear_bubbles("tech_bubble", True)
        
        # Obtenir les données supplémentaires
        tech_data = self.project_show.get_technologies_data(project_type_id)
        project_type_name = tech_data.get("project_type_name", "")
        project_color = tech_data.get("project_color", "#4CAF50")
        
        # Créer un message pour introduire les technologies
        intro_text = f"Choisissez une technologie pour votre projet <b>{project_type_name}</b> :"
        intro_bubble = self.add_bubble(intro_text, extra_properties={"tech_bubble": True})
        
        # Créer une bulle pour chaque technologie
        for tech in technologies:
            # Préparer le chemin de l'icône
            icon_name = tech.get('icon', 'code')
            icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets', 'icons', f"{icon_name}.svg")
            
            # Vérifier si l'icône existe
            if not os.path.exists(icon_path):
                # Utiliser une icône par défaut si l'icône spécifiée n'existe pas
                icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets', 'icons', "code.svg")
            
            try:
                # Charger l'icône avec la couleur du type de projet
                svg_content = load_colored_svg(icon_path, color_str=project_color)
                
                # Créer le texte pour la bulle avec l'icône
                text = f"<b>{tech['name']}</b>"
                
                # Ajouter la bulle
                bubble = self.add_bubble(text, extra_properties={
                    "tech_id": tech['id'],
                    "tech_bubble": True
                })
                
                # Appliquer un style spécifique à la bulle
                for child in bubble.findChildren(QLabel):
                    # Créer un layout horizontal
                    h_layout = QHBoxLayout(child)
                    h_layout.setContentsMargins(5, 5, 5, 5)
                    h_layout.setSpacing(10)
                    
                    # Ajouter l'icône SVG
                    if svg_content:
                        svg_widget = QSvgWidget()
                        svg_widget.load(svg_content)
                        svg_widget.setFixedSize(24, 24)  # Taille de l'icône
                        h_layout.addWidget(svg_widget, 0, Qt.AlignVCenter)
                    
                    # Ajouter le texte
                    text_label = QLabel(text)
                    text_label.setTextFormat(Qt.RichText)
                    text_label.setWordWrap(True)
                    h_layout.addWidget(text_label, 1, Qt.AlignVCenter)
                    
                    # Appliquer un style avec une bordure de couleur mais sans fond bleu
                    child.setStyleSheet(f"border-left: 4px solid {project_color}; padding-left: 10px; background-color: rgba(42, 42, 42, 0.7); border-radius: 4px;")
                    
                    # Rendre la bulle cliquable
                    child.setTextInteractionFlags(Qt.TextBrowserInteraction)
                    child.mousePressEvent = lambda event, tech_id=tech['id']: self.on_technology_selected(tech_id)
            except Exception as e:
                print(f"[ERREUR] Échec de création de la bulle pour la technologie {tech['name']}: {str(e)}")
                continue
    
    def on_technology_selected(self, technology_id):
        """Gère la sélection d'une technologie"""
        # Informer le ProjectCreatorShow de la sélection
        self.project_show.select_technology(technology_id)
