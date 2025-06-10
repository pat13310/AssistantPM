"""
Composant de carte d'aide pour l'Assistant IA
Ce module définit un widget Qt pour afficher une rubrique d'aide sous forme de carte
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QPixmap, QColor, QPainter, QPen, QLinearGradient
from PySide6.QtSvgWidgets import QSvgWidget

from project.structure.ui.ui_utils import load_colored_svg

class HelpCard(QFrame):
    """Widget de carte pour une rubrique d'aide"""
    
    # Signal émis quand la carte est cliquée
    clicked = Signal(str)  # Identifiant de la rubrique
    
    def __init__(self, topic_id, title, description, icon_name=None, parent=None):
        """
        Initialisation d'une carte de rubrique d'aide
        
        Args:
            topic_id (str): Identifiant unique de la rubrique
            title (str): Titre de la rubrique
            description (str): Description courte de la rubrique
            icon_name (str, optional): Nom de l'icône à utiliser
            parent (QWidget, optional): Widget parent
        """
        super().__init__(parent)
        
        self.topic_id = topic_id
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        
        # Enlever le style CSS car nous allons utiliser un paintEvent
        self.setStyleSheet("")
        
        # Variables d'état
        self._hovered = False
        self._selected = False
        
        # Couleur principale (vert par défaut)
        self.color = "#4CAF50"
        
        # Rendre la carte cliquable
        self.setCursor(Qt.PointingHandCursor)
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # En-tête avec icône et titre
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 5)  # Réduire l'espace en bas
        
        # Icône (si spécifiée)
        if icon_name:
            # Utilisation directe de QSvgWidget avec load_colored_svg
            svg_widget = QSvgWidget()
            svg_widget.load(load_colored_svg(icon_name, color_str="#4CAF50"))  # Couleur verte
            svg_widget.setFixedSize(30, 30)  # Icône plus grande
            
            # Créer un conteneur pour l'icône avec alignement central
            icon_container = QWidget()
            icon_layout = QVBoxLayout(icon_container)
            icon_layout.setContentsMargins(0, 0, 8, 0)  # Marge à droite pour séparer de l'icône du texte
            icon_layout.addWidget(svg_widget, 0, Qt.AlignCenter)
            
            header_layout.addWidget(icon_container)
        
        # Titre avec texte en blanc
        title_label = QLabel(title)
        title_label.setStyleSheet("""font-weight: bold; font-size: 12px; color: #ffffff; margin-top: 5px; 
                               background: transparent;""")
        title_label.setWordWrap(True)
        title_label.setAlignment(Qt.AlignVCenter)  # Aligner verticalement avec l'icône
        header_layout.addWidget(title_label, 1)  # 1 = stretch factor
        
        layout.addLayout(header_layout)
        
        # Description avec texte en blanc légèrement transparent
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""color: rgba(255,255,255,0.75); font-size: 10px; line-height: 100%; 
                               background: transparent;""")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Définir une taille fixe pour la carte, plus grande pour accommoder les contenus
        self.setFixedSize(280, 190)
        
    # La méthode _get_icon_pixmap a été supprimée car nous utilisons maintenant QSvgWidget directement
    
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

    def mousePressEvent(self, event):
        """Gère les événements de clic sur la carte"""
        self.clicked.emit(self.topic_id)
        super().mousePressEvent(event)
    
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
        
        # Rectangle principal (ajusté pour laisser de la place à la bordure)
        # Ajustement plus précis pour que le dégradé et la bordure aient le même arrondi
        rect = self.rect().adjusted(1, 1, -1, -1)
        
        # Couleur de fond avec dégradé
        gradient = QLinearGradient(0, 0, 0, rect.height())
        color = QColor(self.color)
        r, g, b = color.red(), color.green(), color.blue()
        
        if self._selected:
            # Dégradé spécial pour l'état sélectionné
            gradient.setColorAt(0, QColor(r, g, b, 60))      # Couleur du projet plus intense
            gradient.setColorAt(0.5, QColor(r, g, b, 50))    # Légèrement plus transparent au milieu
            gradient.setColorAt(1, QColor(r, g, b, 45))      # Plus transparent en bas
        elif self._hovered:
            # Dégradé légèrement plus clair que le normal mais toujours foncé
            gradient.setColorAt(0, QColor(35, 40, 45, 220))  # Gris-bleu foncé en haut avec une teinte légèrement différente
            gradient.setColorAt(0.5, QColor(30, 35, 40, 230)) # Transition 
            gradient.setColorAt(1, QColor(25, 30, 35, 240))  # Gris-bleu encore plus foncé en bas
        else:
            # Dégradé normal plus foncé
            gradient.setColorAt(0, QColor(30, 35, 40, 220))  # Gris-bleu très foncé en haut
            gradient.setColorAt(1, QColor(20, 25, 30, 240))  # Gris-bleu encore plus foncé en bas
        
        # Pinceau et stylo pour le rectangle principal
        painter.setBrush(gradient)
        
        if self._selected:
            # Bordure verte plus épaisse pour l'état sélectionné
            painter.setPen(QPen(QColor(self.color), 2))
        elif self._hovered:
            # Bordure verte pour l'état survolé
            painter.setPen(QPen(QColor(self.color), 1))
        else:
            # Bordure blanche pour l'état normal
            painter.setPen(QPen(QColor(255, 255, 255), 1))
            
        # Définir la même valeur d'arrondi pour tous les éléments
        radius = 8  # Valeur d'arrondi commune
        
        # Dessiner le rectangle principal avec coins arrondis
        painter.drawRoundedRect(rect, radius, radius)


class TopicCardGrid(QWidget):
    """Widget pour afficher une grille de cartes de rubriques d'aide"""
    
    # Signal émis quand une carte est sélectionnée
    topic_selected = Signal(str)  # Identifiant de la rubrique
    
    def __init__(self, parent=None):
        """Initialisation de la grille de cartes"""
        super().__init__(parent)
        
        # Layout principal: grille flexible
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(20)
        
        # Titre
        title_label = QLabel("Rubriques d'aide")
        title_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #333;")
        self.layout.addWidget(title_label)
        
        # Zone pour les rangées de cartes
        self.cards_layout = QVBoxLayout()
        self.layout.addLayout(self.cards_layout)
        
        # Ajouter un espace extensible à la fin
        self.layout.addStretch(1)
        
        # Liste des cartes ajoutées
        self.cards = []
        
    def add_card_row(self, cards_per_row=3):
        """Ajoute une nouvelle rangée de cartes"""
        row_layout = QHBoxLayout()
        self.cards_layout.addLayout(row_layout)
        
        # Ajouter un espace extensible à la fin de chaque rangée
        row_layout.addStretch(1)
        
        return row_layout
        
    def add_topic_card(self, row_layout, topic_id, title, description, icon_name=None):
        """Ajoute une carte de rubrique à une rangée spécifique"""
        card = HelpCard(topic_id, title, description, icon_name)
        card.clicked.connect(self._on_card_clicked)
        row_layout.insertWidget(row_layout.count() - 1, card)  # Insérer avant le stretch
        self.cards.append(card)
        return card
        
    def _on_card_clicked(self, topic_id):
        """Gère le clic sur une carte"""
        self.topic_selected.emit(topic_id)
        
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
                
                # Supprimer le layout lui-même
                self.cards_layout.removeItem(layout_item)
