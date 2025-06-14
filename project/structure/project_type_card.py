"""
Carte représentant un type de projet avec icône, titre et description
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal, QByteArray
from PySide6.QtGui import QPainter, QColor, QFont, QPixmap, QLinearGradient, QPen, QRadialGradient
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtSvg import QSvgRenderer
import os

from ui.ui_utils import load_colored_svg

class ProjectTypeCard(QWidget):
    """Carte représentant un type de projet avec icône, titre et description"""
    clicked = Signal(str)  # Signal émis avec l'ID du type de projet

    def __init__(self, project_type, parent=None):
        super().__init__(parent)
        self.project_type = project_type
        self.project_id = project_type['id']
        self.title = project_type['name']
        self.description = project_type.get('description', '')
        self.color = project_type.get('color', '#4CAF50')  # Couleur par défaut verte
        self.icon_name = project_type.get('icon', 'code')
        self._hovered = False
        self._selected = False  # Nouvel attribut pour l'état sélectionné
        
        # Dimensions de la carte
        self.setFixedSize(230, 70)  # Largeur, hauteur
        self.setCursor(Qt.PointingHandCursor)

        # Layout principal
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 12, 8)  # Gauche, Haut, Droite, Bas
        main_layout.setSpacing(8)
        
        # Icône à gauche
        self.icon_widget = None
        self.setup_icon()
        if self.icon_widget:
            main_layout.addWidget(self.icon_widget, 0, Qt.AlignVCenter)
        
        # Conteneur pour le texte
        text_container = QWidget()
        text_container.setStyleSheet("background: transparent;") # Assurer la transparence
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)
        
        # Titre
        title_label = QLabel(self.title)
        title_label.setStyleSheet(f"""
            font-weight: bold; 
            font-size: 13px; 
            color: #ffffff; 
            background: transparent;
        """)
        title_label.setWordWrap(True)
        text_layout.addWidget(title_label)
        
        # Description
        if self.description:
            # Raccourcir la description si nécessaire
            desc = self.description
            if len(desc) > 60:
                desc = desc[:57] + "..."
                
            desc_label = QLabel(desc)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("""
                color: rgba(255,255,255,0.75); 
                font-size: 11px; 
                background: transparent;
            """)
            text_layout.addWidget(desc_label)
        
        # Ajouter le conteneur de texte au layout principal
        main_layout.addWidget(text_container, 1)  # Stretch factor 1
        
        # Connecter l'événement de clic
        self.mousePressEvent = self.on_click

    def setup_icon(self):
        """Configure l'icône du type de projet avec gestion avancée des cas d'erreur"""
        try:
            # Chemin vers l'icône
            icon_name = self.icon_name
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            icons_path = os.path.join(base_path, 'assets', 'icons')
            
            # Liste des chemins possibles à essayer dans l'ordre
            possible_paths = [
                os.path.join(icons_path, f"{icon_name}.svg"),                # Chemin exact
                os.path.join(icons_path, f"{icon_name.replace('-logo', '')}.svg"),  # Sans -logo
                os.path.join(icons_path, f"{icon_name.split('-')[0]}.svg"),  # Première partie avant -
            ]
            
            # Essayer chaque chemin possible
            icon_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    icon_path = path
                    break
            
            # Si aucune icône n'est trouvée, utiliser l'icône par défaut
            if icon_path is None:
                print(f"[INFO] Icône non trouvée pour {icon_name}, utilisation de l'icône par défaut")
                # Essayer avec code.svg ou une autre icône générique
                default_icons = ['code.svg', 'code-braces.svg', 'code-tags.svg']
                for default_icon in default_icons:
                    default_path = os.path.join(icons_path, default_icon)
                    if os.path.exists(default_path):
                        icon_path = default_path
                        break
            
            # Si une icône a été trouvée, l'afficher
            if icon_path:
                # Charger l'icône avec la couleur du projet
                svg_content = load_colored_svg(icon_path, color_str=self.color)
                
                # Créer et configurer le widget SVG
                self.icon_widget = QSvgWidget()
                self.icon_widget.load(svg_content)
                self.icon_widget.setFixedSize(24, 24)  # Taille fixe pour l'icône
                self.icon_widget.setStyleSheet("background: transparent; border: none;") # Assurer la transparence
            else:
                # Aucune icône trouvée, utiliser un cercle coloré avec la première lettre
                self.create_letter_icon()
                
        except Exception as e:
            print(f"Erreur lors du chargement de l'icône: {str(e)}")
            # Créer un cercle coloré avec la première lettre comme alternative
            self.create_letter_icon()
    
    def create_letter_icon(self):
        """Crée une icône avec la première lettre du nom dans un cercle coloré"""
        # Créer un label avec la première lettre comme alternative
        letter_label = QLabel(self.title[0].upper())
        letter_label.setAlignment(Qt.AlignCenter)
        letter_label.setFixedSize(24, 24)
        letter_label.setStyleSheet(f"""
            background-color: {self.color};
            color: white;
            border-radius: 12px;
            font-weight: bold;
            font-size: 14px;
        """)
        self.icon_widget = letter_label
        self.update()

    def enterEvent(self, event):
        """Gérer l'événement d'entrée de la souris (hover)"""
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Gérer l'événement de sortie de la souris"""
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def on_click(self, event):
        """Gérer l'événement de clic"""
        self.clicked.emit(self.project_id)

    def set_selected(self, selected):
        """Définit l'état de sélection de la carte"""
        if self._selected != selected:
            self._selected = selected
            self.update()  # Redessiner la carte
    
    def is_selected(self):
        """Renvoie True si la carte est sélectionnée"""
        return self._selected
        
    def paintEvent(self, event):
        """Dessiner la carte avec un style élégant et différentes bordures selon l'état"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Rectangle principal (sans ajustement pour éviter les bordures visibles)
        rect = self.rect()
        
        # Couleur de fond avec dégradé
        gradient = QLinearGradient(0, 0, 0, rect.height())
        color = QColor(self.color)
        r, g, b = color.red(), color.green(), color.blue()
        
        if self._selected:
            # Dégradé spécial pour l'état sélectionné
            gradient.setColorAt(0, QColor(r, g, b, 40))      # Couleur du projet plus intense
            gradient.setColorAt(0.5, QColor(r, g, b, 35))    # Légèrement plus transparent au milieu
            gradient.setColorAt(1, QColor(r, g, b, 30))      # Plus transparent en bas
        elif self._hovered:
            # Dégradé plus lumineux en hover
            gradient.setColorAt(0, QColor(r, g, b, 25))      # Couleur du projet avec opacité
            gradient.setColorAt(0.5, QColor(r, g, b, 20))    # Légèrement plus transparent au milieu
            gradient.setColorAt(1, QColor(r, g, b, 15))      # Plus transparent en bas
        else:
            # Dégradé normal plus subtil
            gradient.setColorAt(0, QColor(40, 45, 55, 85))   # Gris-bleu foncé en haut
            gradient.setColorAt(1, QColor(30, 35, 45, 95))   # Gris-bleu encore plus foncé en bas
        
        # Pinceau et stylo pour le rectangle principal
        painter.setBrush(gradient)
        
        if self._selected:
            # Bordure verte vive pour l'état sélectionné
            painter.setPen(QPen(QColor(self.color), 2))
        elif self._hovered:
            # Bordure légère pour l'état survolé
            painter.setPen(QPen(QColor(70, 75, 85, 100), 1))
        else:
            # Bordure invisible pour l'état normal
            painter.setPen(QPen(QColor(50, 55, 65, 0), 0))
            
        # Dessiner le rectangle principal avec coins arrondis
        painter.drawRoundedRect(rect, 6, 6)
        
        # Bordure colorée sur le côté gauche
        border_width = 6 if self._selected else 4
        left_border_rect = rect.adjusted(0, 0, -rect.width() + border_width, 0)
        
        # Dégradé vertical pour la bordure
        border_gradient = QLinearGradient(0, 0, 0, left_border_rect.height())
        
        if self._selected:
            # Bordure plus brillante et visible quand sélectionné
            border_gradient.setColorAt(0, color.lighter(150))
            border_gradient.setColorAt(1, color.lighter(110))
        elif self._hovered:
            # Bordure plus vive en hover
            border_gradient.setColorAt(0, color.lighter(120))
            border_gradient.setColorAt(1, color)
        else:
            border_gradient.setColorAt(0, color)
            border_gradient.setColorAt(1, color.darker(120))
        
        painter.setBrush(border_gradient)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(left_border_rect, 3, 3)
