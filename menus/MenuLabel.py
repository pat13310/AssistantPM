import os
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtSvg import QSvgRenderer # Remplacer QSvgWidget par QSvgRenderer
from PySide6.QtCore import Qt, QSize, QRect, QRectF, Signal # Ajout de QRectF et Signal
from PySide6.QtGui import QPainter, QColor, QFont, QEnterEvent, QMouseEvent
import sys

# Assurer l'accès à ui_utils
current_dir = os.path.dirname(os.path.abspath(__file__))
# Aller deux niveaux plus haut pour atteindre la racine du projet (e.g., menus -> components -> project_root)
# Si MenuLabel.py est dans e:/projets QT/AssistanPM/menus/
# current_dir = e:/projets QT/AssistanPM/menus
# project_root devrait être e:/projets QT/AssistanPM
project_root = os.path.dirname(current_dir) # Ceci mène à e:/projets QT/AssistanPM
# Si la structure est /menus/MenuLabel.py, alors project_root = os.path.dirname(current_dir) est correct
# Si la structure est /components/menus/MenuLabel.py, alors project_root = os.path.dirname(os.path.dirname(current_dir))

# Vérifions la structure attendue par l'import de ui.ui_utils
# ui_utils.py est dans e:/projets QT/AssistanPM/ui/ui_utils.py
# Donc, project_root doit être e:/projets QT/AssistanPM
# Si MenuLabel.py est dans e:/projets QT/AssistanPM/menus/MenuLabel.py
# current_dir = e:/projets QT/AssistanPM/menus
# os.path.dirname(current_dir) = e:/projets QT/AssistanPM
# Donc, la ligne suivante est correcte si MenuLabel.py est directement dans un dossier 'menus' à la racine.
# Si 'menus' est dans 'components', il faut ajuster.
# D'après l'arborescence fournie, 'menus' est à la racine.
if project_root not in sys.path:
    # sys a déjà été importé en haut du fichier
    sys.path.insert(0, project_root)

from ui.ui_utils import load_colored_svg


class MenuLabel(QWidget):
    clicked = Signal()

    def __init__(self, text: str, icon_path: str = None, icon_size: QSize = QSize(18, 18), on_click=None, parent=None):
        super().__init__(parent)
        self.text_content = text # Renommé pour éviter conflit avec QWidget.text()
        self.icon_path = icon_path
        self.on_click = on_click
        self.icon_size = icon_size
        self.only_icon_mode = False # Renommé pour clarté
        self.hovered = False
        self.active = False

        self.setMinimumHeight(40)
        self.setCursor(Qt.PointingHandCursor)
        self.setMouseTracking(True)

        self.font = QFont("Segoe UI", 10, QFont.Normal)
        # Les couleurs de texte et de fond seront gérées par paintEvent pour le fond
        # et par stylesheet pour le QLabel du texte.

        self._setup_ui()

    def _setup_ui(self):
        self.icon_renderer = None
        if self.icon_path:
            svg_data = load_colored_svg(self.icon_path, color_str="#333333") # Gris foncé pour icônes
            if not svg_data.isEmpty():
                self.icon_renderer = QSvgRenderer(svg_data)
            else:
                print(f"Warning: Icon {self.icon_path} could not be loaded for MenuLabel.")

        self.main_layout = QHBoxLayout(self)
        # Les marges devront tenir compte de l'icône dessinée manuellement
        # Marge gauche pour l'icône + espacement + texte
        self.icon_margin_left = 12
        self.text_margin_left_with_icon = self.icon_margin_left + self.icon_size.width() + 10
        self.text_margin_left_no_icon = 12

        current_text_margin = self.text_margin_left_with_icon if self.icon_renderer else self.text_margin_left_no_icon
        
        self.main_layout.setContentsMargins(current_text_margin, 0, 12, 0) 
        self.main_layout.setSpacing(0) # Le texte est le seul enfant direct du layout maintenant

        self.text_label = QLabel(self.text_content, self)
        self.text_label.setFont(self.font)
        self.text_label.setAttribute(Qt.WA_TranslucentBackground) # Important
        self.text_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        
        # self.main_layout.addWidget(self.icon_widget) # Supprimé
        self.main_layout.addWidget(self.text_label, 1)

        self._update_text_color()

    def _update_text_color(self):
        current_text_color = QColor(0, 0, 0) # Noir par défaut
        if self.active:
            current_text_color = QColor(0, 0, 0) # Peut être différent si besoin
        elif self.hovered:
            current_text_color = QColor(0, 0, 0) # Peut être différent si besoin
        
        self.text_label.setStyleSheet(f"background-color: transparent; color: {current_text_color.name()};")

    def sizeHint(self):
        if self.only_icon_mode:
            # Consider icon size + margins
            return QSize(self.icon_size.width() + 24, 40) # 12px margin each side
        # Consider icon + text + spacing + margins
        # This is a bit more complex, QWidget usually handles this with layout.
        # Let the layout determine the size, or provide a reasonable default.
        return super().sizeHint() # Laisser le layout gérer ou QSize(200,40) comme avant

    def enterEvent(self, event: QEnterEvent):
        self.hovered = True
        self._update_text_color()
        self.update() # Redessiner le fond
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.hovered = False
        self._update_text_color()
        self.update() # Redessiner le fond
        super().leaveEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        self.active = True
        self._update_text_color()
        self.update() # Redessiner le fond
        self.clicked.emit()  # Émettre le signal clicked
        if self.on_click:
            self.on_click(self)
        # Ne pas appeler super().mousePressEvent(event) si on gère complètement le clic
        # ou l'appeler si on veut la propagation standard.
        # Pour un simple bouton, on peut l'omettre ou le mettre à la fin.
        # super().mousePressEvent(event) # Dépend du comportement désiré

    def mouseReleaseEvent(self, event: QMouseEvent):
        # Optionnel: gérer le mouseRelease pour remettre active à False si on veut un effet "pressé"
        # self.active = False
        # self._update_text_color()
        # self.update()
        super().mouseReleaseEvent(event)


    def reset(self):
        self.active = False
        self._update_text_color()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        current_bg_color = QColor(0, 0, 0, 0) # Transparent par défaut
        if self.active:
            current_bg_color = QColor("#cdf7db")
        elif self.hovered:
            current_bg_color = QColor("#e2f7e9")

        rect = self.rect().adjusted(0, 0, -1, -1) # Ajustement pour la bordure si elle était dessinée
        painter.setBrush(current_bg_color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, 6, 6)

        # Dessiner l'icône manuellement
        if self.icon_renderer:
            icon_y = (self.height() - self.icon_size.height()) // 2
            icon_x = 0
            if self.only_icon_mode:
                icon_x = (self.width() - self.icon_size.width()) // 2
            else:
                icon_x = self.icon_margin_left
            
            target_rect = QRectF(icon_x, icon_y, self.icon_size.width(), self.icon_size.height())
            self.icon_renderer.render(painter, target_rect)
        
        # Le text_label est un widget enfant et sera dessiné par Qt après ce paintEvent.
        # Il est important que son WA_TranslucentBackground soit True.

    def show_only_icon(self, show_icon_only: bool):
        self.only_icon_mode = show_icon_only
        self.text_label.setVisible(not show_icon_only)
        
        if self.only_icon_mode:
            # Si seulement l'icône, le layout n'a pas besoin de marges pour le texte
            self.main_layout.setContentsMargins(0,0,0,0) 
        else:
            # Rétablir les marges pour le texte
            current_text_margin = self.text_margin_left_with_icon if self.icon_renderer else self.text_margin_left_no_icon
            self.main_layout.setContentsMargins(current_text_margin, 0, 12, 0)
            
        self.updateGeometry() # Important pour que le layout se recalcule
        self.update() # Redessiner
