from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QApplication
)
from PySide6.QtSvgWidgets import QSvgWidget # Ajout de QSvgWidget
from PySide6.QtCore import Qt, QTimer, QRect, QSize, QRectF
from PySide6.QtGui import QFont, QColor, QPainterPath, QRegion, QPainter, QPen # QPixmap n'est plus nécessaire ici directement
import sys
import os

# Assurer l'accès à ui_utils
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from ui.ui_utils import load_colored_svg # Remplacer render_svg_icon par load_colored_svg

class ToastNotification(QDialog):
    TYPE_SUCCESS = "success"
    TYPE_WARNING = "warning"
    TYPE_ERROR = "error"

    def __init__(self, title, message, toast_type=TYPE_SUCCESS, duration=2000, parent=None):
        super().__init__(parent)

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.ToolTip |
            Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.border_color_qcolor = QColor("#22C55E") # QColor pour le painter
        self.icon_path = "assets/icons/check.svg"
        self.title_text_color = self.border_color_qcolor # Titre de la même couleur que la bordure

        if toast_type == self.TYPE_WARNING:
            self.border_color_qcolor = QColor("#F59E0B")
            self.icon_path = "assets/icons/triangle-alert.svg"
            self.title_text_color = self.border_color_qcolor
        elif toast_type == self.TYPE_ERROR:
            self.border_color_qcolor = QColor("#EF4444")
            self.icon_path = "assets/icons/triangle-alert.svg"
            self.title_text_color = self.border_color_qcolor
        
        self.radius = 10
        self.border_thickness = 2

        self._setup_ui(title, message)
        
        if parent:
            parent_rect = parent.geometry()
            self.move(parent_rect.center().x() - self.width() / 2, 
                      parent_rect.center().y() - self.height() / 2)
        else:
            screen_geometry = QApplication.primaryScreen().availableGeometry()
            self.move(screen_geometry.center().x() - self.width() / 2,
                      screen_geometry.center().y() - self.height() / 2)

        QTimer.singleShot(duration, self.close)

    def _setup_ui(self, title, message):
        min_width = 280
        
        # Le QDialog lui-même est le conteneur principal maintenant
        self.setStyleSheet("background-color: transparent;") # Nécessaire pour WA_TranslucentBackground

        main_layout = QHBoxLayout(self)
        # Les marges doivent tenir compte de l'épaisseur de la bordure pour que le contenu ne la chevauche pas
        margin = 15 + self.border_thickness // 2 
        main_layout.setContentsMargins(margin, margin, margin, margin)
        main_layout.setSpacing(12)

        icon_widget = QSvgWidget() # Remplacer QLabel par QSvgWidget
        icon_widget.setFixedSize(30, 30)
        
        svg_data = load_colored_svg(self.icon_path, color_str=self.border_color_qcolor.name())
        if svg_data.isEmpty():
            print(f"Warning: Icon {self.icon_path} could not be loaded or is empty for ToastNotification.")
        else:
            icon_widget.load(svg_data)
        
        main_layout.addWidget(icon_widget)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(3)

        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 11, QFont.Bold))
        title_label.setStyleSheet(f"color: {self.title_text_color.name()}; border: none;")
        text_layout.addWidget(title_label)

        message_label = QLabel(message)
        message_label.setFont(QFont("Arial", 10))
        message_label.setStyleSheet("color: #374151; border: none;") # Couleur de texte standard pour le message
        message_label.setMaximumWidth(200) # Limiter la largeur du message
        message_label.setMinimumWidth(300) # Largeur minimale pour le message
        message_label.setWordWrap(True) # Permettre le retour à la ligne
        text_layout.addWidget(message_label)
        
        main_layout.addLayout(text_layout)
        main_layout.addStretch()

        self.adjustSize()
        current_width = self.width()
        current_height = self.height()
        final_width = max(min_width, current_width)
        self.setFixedSize(final_width, current_height)

        # Le masque est toujours nécessaire pour les coins arrondis du QDialog transparent
        path = QPainterPath()
        path.addRoundedRect(QRect(-1, -1, self.width() + 2, self.height() + 2), self.radius, self.radius)
        self.setMask(QRegion(path.toFillPolygon().toPolygon()))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Rectangle pour le fond (taille complète du widget)
        bg_rect = self.rect()
        bg_path = QPainterPath()
        bg_path.addRoundedRect(bg_rect, self.radius, self.radius)
        painter.fillPath(bg_path, QColor("#FFFFFF"))

        # Rectangle pour la bordure, ajusté pour que la bordure soit dessinée à l'intérieur
        # L'ajustement doit être de la moitié de l'épaisseur du stylo pour centrer la ligne sur le bord désiré.
        # Si le stylo a une épaisseur de 2, un ajustement de 1px (2 // 2) est correct.
        # Le problème pourrait être que le masque coupe la bordure.
        # Assurons-nous que le masque est appliqué à la taille exacte du widget.
        # Le rect pour drawPath doit être tel que la bordure de `self.border_thickness` soit visible.
        
        # Pour une bordure de 2px, on dessine sur un rect ajusté de 1px pour que la ligne de 2px soit centrée sur ce bord.
        # Le masque doit correspondre à la géométrie extérieure de cette bordure.
        # Si le QDialog a la taille WxH, le masque est sur QRect(0,0,W,H).
        # La bordure doit être dessinée de sorte qu'elle ne dépasse pas ce masque.
        
        border_offset = self.border_thickness / 2.0
        # Crée un rectangle pour la bordure qui est légèrement plus petit pour que la bordure soit entièrement visible
        border_rect = QRectF(self.rect()).adjusted(border_offset, border_offset, -border_offset, -border_offset)
        
        border_path = QPainterPath()
        border_path.addRoundedRect(border_rect, self.radius - border_offset, self.radius - border_offset) # Ajuster aussi le radius

        pen = QPen(self.border_color_qcolor, self.border_thickness)
        painter.setPen(pen)
        painter.drawPath(border_path)
        
        # Appeler super().paintEvent(event) pour s'assurer que les widgets enfants sont dessinés.
        # Cela doit être fait après notre dessin personnalisé si nous voulons que les enfants soient par-dessus.
        super().paintEvent(event)

    @staticmethod
    def show_toast(title, message, toast_type=TYPE_SUCCESS, duration=2000, parent=None):
        if QApplication.instance() is None:
            _ = QApplication(sys.argv) 

        toast = ToastNotification(title, message, toast_type, duration, parent)
        toast.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Conserver les références aux toasts pour éviter qu'ils ne soient détruits prématurément
    active_toasts = []

    def show_and_store_toast(title, message, toast_type, duration=2000):
        toast = ToastNotification(title, message, toast_type, duration, parent=None)
        toast.show()
        active_toasts.append(toast)
        # Optionnel: se connecter au signal destroyed pour retirer de la liste
        toast.destroyed.connect(lambda obj=toast: active_toasts.remove(obj) if obj in active_toasts else None)

    show_and_store_toast("Succès !", "L'opération a été complétée avec succès.", ToastNotification.TYPE_SUCCESS)
    
    QTimer.singleShot(2500, lambda: show_and_store_toast("Attention", "Ceci est un avertissement important.", ToastNotification.TYPE_WARNING, duration=3000))
    QTimer.singleShot(6000, lambda: show_and_store_toast("Erreur Critique", "Une erreur fatale est survenue.Une erreur fatale est survenue.", ToastNotification.TYPE_ERROR, duration=4000))
    QTimer.singleShot(11000, lambda: app.quit()) # Quitter après 11 secondes pour voir tous les toasts
    # Pour s'assurer que l'application ne se ferme pas immédiatement si tous les toasts se ferment vite.
    # On peut ajouter un bouton pour quitter ou une autre logique.
    # Pour un test simple, on peut juste laisser la boucle d'événements tourner.
    # Si on veut quitter après le dernier toast, il faudrait une logique plus complexe.
    
    # Exemple simple pour garder l'application ouverte un peu plus longtemps pour voir tous les toasts
    # QTimer.singleShot(10000, app.quit) # Quitter après 10 secondes

    sys.exit(app.exec())
