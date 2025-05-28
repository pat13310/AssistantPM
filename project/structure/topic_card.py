from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal, QByteArray
from PySide6.QtGui import QPainter, QColor, QFont, QPixmap, QLinearGradient, QPen, QRadialGradient
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtSvg import QSvgRenderer
import os

# Ajouter le répertoire parent au chemin d'importation
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ui.ui_utils import load_colored_svg

class TopicCard(QWidget):
    """Carte représentant une rubrique d'aide avec titre, description et icône"""
    clicked = Signal(str)  # Signal émis avec le titre de la carte

    def __init__(self, title, description, icon_pixmap=None, parent=None):
        super().__init__(parent)
        self.title = title
        self._hovered = False
        self.setFixedSize(180, 140)
        self.setCursor(Qt.PointingHandCursor)

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 12, 16, 12)
        main_layout.setSpacing(8)

        # Header : icône + titre
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        # Icône - Utiliser uniquement QSvgWidget        
        if icon_pixmap is not None and isinstance(icon_pixmap, str) and os.path.exists(icon_pixmap) and icon_pixmap.endswith('.svg'):
            # Si c'est un chemin vers un fichier SVG valide
            svg_content = load_colored_svg(icon_pixmap, color_str="#2980b9")
            icon_widget = QSvgWidget()
            icon_widget.load(svg_content)
            icon_widget.setFixedSize(26, 26)
            icon_widget.setStyleSheet("background-color: transparent; border:none;")
            header_layout.addWidget(icon_widget)
        else:
            # Fallback: créer un label avec la première lettre du titre
            icon_label = QLabel(title[0].upper())
            icon_label.setAlignment(Qt.AlignCenter)
            icon_label.setFont(QFont("Arial", 13, QFont.Bold))
            icon_label.setStyleSheet("""
                background: rgba(255,255,255,0.18);
                color: #fff; border-radius: 13px;""")
            icon_label.setFixedSize(26, 26)
            header_layout.addWidget(icon_label)

        # Titre avec style amélioré
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-weight: bold; 
            font-size: 12px; 
            color: #ffffff; 
            background: transparent;
        """)
        title_label.setWordWrap(True)
        header_layout.addWidget(title_label, 1)
        main_layout.addLayout(header_layout)

        # Description avec style amélioré
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("""
            color: rgba(255,255,255,0.9); 
            font-size: 11px; 
            background: transparent;
            margin-top: 2px;
        """)
        main_layout.addWidget(desc_label, 1)

    def enterEvent(self, event):
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        # Fond arrondi avec dégradé de gris et effet hover
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(0, 0, -1, -1)
        
        # Créer un dégradé plus sophistiqué pour le fond
        gradient = QLinearGradient(0, 0, 0, rect.height())
        if self._hovered:
            # Dégradé plus vif en hover
            gradient.setColorAt(0, QColor(45, 50, 60, 95))     # Gris-bleu foncé en haut
            gradient.setColorAt(0.5, QColor(55, 60, 70, 90))   # Gris-bleu moyen au milieu
            gradient.setColorAt(1, QColor(40, 45, 55, 85))     # Gris-bleu foncé en bas
        else:
            # Dégradé normal plus subtil
            gradient.setColorAt(0, QColor(40, 45, 55, 85))     # Gris-bleu foncé en haut
            gradient.setColorAt(0.5, QColor(50, 55, 65, 80))   # Gris-bleu moyen au milieu
            gradient.setColorAt(1, QColor(35, 40, 50, 75))     # Gris-bleu foncé en bas
        
        # Ajouter un effet d'ombre portée
        shadowGradient = QRadialGradient(rect.center(), rect.width() * 0.8)
        shadowGradient.setColorAt(0, QColor(0, 0, 0, 0))        # Transparent au centre
        shadowGradient.setColorAt(1, QColor(0, 0, 0, 15))       # Légère ombre aux bords
        
        # Couleur de la bordure
        if self._hovered:
            color_border = QColor(52, 152, 219, 230)  # Bleu clair hover
        else:
            color_border = QColor(41, 128, 185, 150)  # Bleu par défaut
        
        # Dessiner d'abord l'ombre
        painter.setBrush(shadowGradient)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect.adjusted(2, 2, 2, 2), 13, 13)
        
        # Dessiner le rectangle arrondi avec le dégradé
        painter.setBrush(gradient)
        painter.setPen(QPen(color_border, 1.2))  # Bordure un peu plus épaisse
        painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), 13, 13)
        
        super().paintEvent(event)

    def mousePressEvent(self, event):
        self.clicked.emit(self.title)
        super().mousePressEvent(event)
