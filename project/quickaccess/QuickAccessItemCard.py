import sys # Ajout pour le hack sys.path si ce fichier est exécuté directement
import os  # Ajout pour le hack sys.path

# Détermine le chemin racine du projet et l'ajoute à sys.path
# Utile si ce fichier est exécuté directement et importe depuis ui.ui_utils
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, os.pardir, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from PySide6.QtWidgets import QWidget, QApplication, QVBoxLayout # QApplication, QVBoxLayout pour le test
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QPaintEvent, QMouseEvent, QFontMetrics, QIcon # Ajout QFontMetrics, QIcon
from PySide6.QtCore import Qt, Signal, QSize, QRect, QRectF, QEvent, QPoint
from PySide6.QtSvg import QSvgRenderer
from ui.ui_utils import load_colored_svg


class QuickAccessItemCard(QWidget):
    clicked = Signal()

    # Styles généraux (version utilisateur)
    ICON_SIZE = QSize(32, 32)
    ICON_BLOCK_WIDTH = 60
    CARD_HEIGHT = 90  # Augmentation de la hauteur des cartes pour accommoder le texte explicatif
    CARD_FIXED_WIDTH = 370 # Largeur fixe pour les cards
    BORDER_RADIUS = 8
    SPACING = 5 # Espacement entre bloc icône et bloc texte
    TEXT_PADDING = 12 # Padding horizontal à l'intérieur du bloc texte

    # Couleurs (version utilisateur)
    COLOR_TEXT_DEFAULT = QColor("#555")
    COLOR_TEXT_HOVER = QColor("#22C55E")
    COLOR_TEXT_PRESSED = QColor("#15803D")

    BG_DEFAULT = QColor("#F0F0F0")
    BORDER_DEFAULT = QColor("#ACACAC")
    BG_HOVER = QColor("#F0FFF0")
    BORDER_HOVER = QColor("#22C55E")
    BG_PRESSED = QColor("#E0E0E0")
    BORDER_PRESSED = QColor("#15803D")

    COLOR_ICON_DEFAULT = QColor(Qt.black)
    COLOR_ICON_HOVER = QColor("#22C55E")
    COLOR_ICON_PRESSED = QColor("#15803D")

    def __init__(self, text: str, icon_path: str = None, description: str = None, parent=None):
        super().__init__(parent)
        self.text_content = text # Titre principal de la carte
        self.description = description or "" # Texte explicatif sous le titre
        self.icon_path_str = icon_path # Chemin de l'icône
        self._hovered = False
        self._pressed = False

        # Utiliser les noms de variables cohérents
        self.renderer_default = self._make_renderer(self.COLOR_ICON_DEFAULT) # Couleur d'icône, pas de texte
        self.renderer_hover = self._make_renderer(self.COLOR_ICON_HOVER)
        self.renderer_pressed = self._make_renderer(self.COLOR_ICON_PRESSED)

        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(self.CARD_HEIGHT)
        self.setMouseTracking(True)
        self.setFont(QFont("Segoe UI", 11)) # Définir la police une fois pour le widget

    def _make_renderer(self, color: QColor):
        if not self.icon_path_str:
            return None
        # Utiliser self.icon_path_str qui est défini dans __init__
        svg_data = load_colored_svg(self.icon_path_str, color.name())
        if svg_data.isEmpty():
            print(f"Avertissement: Impossible de charger les données SVG pour {self.icon_path_str} avec la couleur {color.name()}")
            # Fallback simple: essayer de charger l'icône sans coloration
            raw_icon = QIcon(self.icon_path_str)
            if not raw_icon.isNull():
                # Créer un renderer pour une icône non colorée si besoin, ou retourner None
                # Pour l'instant, on retourne None si la coloration spécifique échoue.
                # Ou on pourrait retourner un renderer pour l'icône brute.
                # Pour simplifier, si la coloration échoue, pas d'icône via cette voie.
                pass # On pourrait retourner un renderer de l'icône brute ici
            return None
        renderer = QSvgRenderer(svg_data)
        if not renderer.isValid():
            print(f"Avertissement: QSvgRenderer invalide pour {self.icon_path_str} avec la couleur {color.name()}")
            return None
        return renderer

    def _current_style(self):
        if self._pressed:
            return (
                self.BG_PRESSED, self.BORDER_PRESSED,
                self.COLOR_TEXT_PRESSED, self.renderer_pressed, 2.0 # Épaisseur en float
            )
        elif self._hovered:
            return (
                self.BG_HOVER, self.BORDER_HOVER,
                self.COLOR_TEXT_HOVER, self.renderer_hover, 2.0 # Épaisseur en float
            )
        else:
            return (
                self.BG_DEFAULT, self.BORDER_DEFAULT,
                self.COLOR_TEXT_DEFAULT, self.renderer_default, 1.0 # Épaisseur en float
            )

    def paintEvent(self, event: QPaintEvent):
        bg_color, border_color, text_color, renderer, border_thickness = self._current_style()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setPen(QPen(border_color, border_thickness))
        painter.setBrush(bg_color)
        # Le rect ajusté pour que la bordure soit bien visible
        paint_rect = QRectF(self.rect()).adjusted(
            border_thickness / 2, border_thickness / 2,
            -border_thickness / 2, -border_thickness / 2
        )
        painter.drawRoundedRect(paint_rect, self.BORDER_RADIUS, self.BORDER_RADIUS)

        # Icône
        if renderer:
            # Zone où l'icône doit être dessinée (partie gauche de la card, à l'intérieur du padding/bordure)
            # Le bloc icône est à gauche, hauteur de la card, largeur ICON_BLOCK_WIDTH
            # Le padding/bordure est déjà géré par paint_rect pour le fond/bordure globale.
            # L'icône est dessinée par-dessus ce fond.
            icon_display_x = (self.ICON_BLOCK_WIDTH - self.ICON_SIZE.width()) / 2.0
            # Ajuster pour l'épaisseur de la bordure si on veut l'aligner par rapport au contenu interne
            # icon_display_x += border_thickness / 2 
            icon_display_y = (self.height() - self.ICON_SIZE.height()) / 2.0
            
            target_rect = QRectF(icon_display_x, icon_display_y, self.ICON_SIZE.width(), self.ICON_SIZE.height())
            renderer.render(painter, target_rect)

        # Texte principal (titre)
        painter.setPen(text_color)
        painter.setFont(QFont("Segoe UI", 11, QFont.Bold)) # Police en gras pour le titre
        
        # Rectangle pour le texte, à droite du bloc icône
        text_rect_x = self.ICON_BLOCK_WIDTH + self.SPACING
        
        # Rectangle pour le titre (moitié supérieure)
        title_render_rect = QRect(
            int(text_rect_x), 0, # X commence après le bloc icône et l'espacement
            int(self.width() - text_rect_x), int(self.height() / 2) # Moitié supérieure de la carte
        ).adjusted(self.TEXT_PADDING, 5, -self.TEXT_PADDING, 0) # Padding horizontal et ajustement vertical
        
        painter.drawText(title_render_rect, Qt.AlignBottom | Qt.AlignLeft, self.text_content)
        
        # Texte secondaire (description)
        if self.description:
            painter.setPen(QColor("#777777")) # Couleur plus claire pour la description
            painter.setFont(QFont("Segoe UI", 9)) # Police plus petite pour la description
            
            # Rectangle pour la description (moitié inférieure)
            desc_render_rect = QRect(
                int(text_rect_x), int(self.height() / 2), # X comme le titre, Y à mi-hauteur
                int(self.width() - text_rect_x), int(self.height() / 2) # Moitié inférieure de la carte
            ).adjusted(self.TEXT_PADDING, 0, -self.TEXT_PADDING, -5) # Padding horizontal et ajustement vertical
            
            # Limiter le texte à deux lignes et ajouter des points de suspension si nécessaire
            fm = QFontMetrics(painter.font())
            elided_text = fm.elidedText(self.description, Qt.ElideRight, desc_render_rect.width())
            
            painter.drawText(desc_render_rect, Qt.AlignTop | Qt.AlignLeft, elided_text)

    def sizeHint(self) -> QSize:
        fm = QFontMetrics(self.font())
        # Calculer la largeur du texte. boundingRect donne un QRect, on prend sa largeur.
        # Utiliser horizontalAdvance pour une seule ligne.
        text_width = fm.horizontalAdvance(self.text_content)
        
        # Largeur totale = largeur bloc icône + espacement + largeur texte + (2 * padding horizontal du texte)
        # width = self.ICON_BLOCK_WIDTH + self.SPACING + text_width + (2 * self.TEXT_PADDING)
        # Retourner la largeur fixe définie
        return QSize(self.CARD_FIXED_WIDTH, self.CARD_HEIGHT)

    def minimumSizeHint(self) -> QSize:
        # Largeur minimale = largeur bloc icône + espacement + un peu pour le texte (ex: 3 caractères "...")
        # fm = QFontMetrics(self.font())
        # min_text_indicator_width = fm.horizontalAdvance("...") 
        # min_width = self.ICON_BLOCK_WIDTH + self.SPACING + min_text_indicator_width + (2 * self.TEXT_PADDING)
        # Retourner la largeur fixe définie
        return QSize(self.CARD_FIXED_WIDTH, self.CARD_HEIGHT)

    def enterEvent(self, event: QEvent):
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent):
        self._hovered = False
        self._pressed = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._pressed = True
            self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and self._pressed:
            self._pressed = False
            self.update()
            if self.rect().contains(event.position().toPoint()):
                self.clicked.emit()
        super().mouseReleaseEvent(event)

if __name__ == '__main__':
    # sys, os, QApplication, QVBoxLayout sont déjà importés en haut
    app = QApplication(sys.argv)

    main_window = QWidget()
    test_layout = QVBoxLayout(main_window)
    main_window.setStyleSheet("background-color: #FFFFFF;") 

    phases_data_test = [
        ("Documentation", "assets/icons/book-open.svg"),
        ("Code", "assets/icons/code.svg"),
        ("Architecture", "assets/icons/folder-tree.svg"),
        ("Tests", "assets/icons/test-tube.svg"),
        ("Déploiement", "assets/icons/rocket.svg"),
        ("Item Très Long Pour Tester Flow", "assets/icons/search.svg"),
        ("Vide", None) 
    ]

    for name, icon_path_test in phases_data_test:
        card = QuickAccessItemCard(name, icon_path_test)
        card.clicked.connect(lambda n=name: print(f"Card '{n}' cliquée!"))
        test_layout.addWidget(card)

    main_window.setWindowTitle("Test QuickAccessItemCard (PaintEvent)")
    main_window.resize(400, 300) 
    main_window.show()

    sys.exit(app.exec())
