from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QSize, QRect
from PySide6.QtGui import QPainter, QColor, QPixmap, QFont, QEnterEvent, QMouseEvent


class PhaseLabel(QWidget):
    def __init__(self, text: str, icon_path: str = None, on_click=None, parent=None):
        super().__init__(parent)
        self.on_click = on_click 
        self.text = text
        self.icon_path = icon_path
        self.icon_size = QSize(20, 20)

        self.hovered = False
        self.active = False
        self.only_icon = False  # par défaut, on montre le texte


        self.setMinimumHeight(40)
        self.setCursor(Qt.PointingHandCursor)
        self.setMouseTracking(True)

        self.font = QFont("Segoe UI", 10, QFont.Normal)
        self.text_color = QColor(0, 0, 0)
        self.bg_color = QColor(0, 0, 0, 0)

    def sizeHint(self):
        if self.only_icon:
            # Largeur = marge gauche + icône + marge droite
            return QSize(12 + self.icon_size.width() , 40)
        else:
            return QSize(200, 40)  # taille par défaut quand le texte est visible

    def enterEvent(self, event: QEnterEvent):
        self.hovered = True
        if not self.active:
            self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.hovered = False
        if not self.active:
            self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        self.active = True
        self.update()
        if self.on_click:
            self.on_click(self)  # notifier le parent
        print(f"Phase sélectionnée : {self.text}")
        super().mousePressEvent(event)

    def reset(self):
        self.active = False
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.TextAntialiasing)

        # Couleurs selon état
        if self.active:
            self.bg_color = QColor("#F1F1F1")
            self.text_color = QColor("black")
        elif self.hovered:
            self.bg_color = QColor("#F7F7F7")
            self.text_color = QColor("black")
        else:
            self.bg_color = QColor(0, 0, 0, 0)
            self.text_color = QColor("black")

        # Dessiner le fond
        rect = self.rect().adjusted(0, 0, -1, -1)
        painter.setBrush(self.bg_color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, 6, 6)

        if not self.only_icon:
            painter.setPen(self.text_color)
            painter.setFont(self.font)
            x_offset = 12 + self.icon_size.width() + 10
            text_rect = QRect(x_offset, 0, self.width() - x_offset - 12, self.height())
            painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft, self.text)

        # Dessiner l'icône
        if self.icon_path:
            icon = QPixmap(self.icon_path).scaled(self.icon_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)            
            icon = icon.scaled(self.icon_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            if self.only_icon:
                painter.drawPixmap((self.width() - self.icon_size.width()) // 2 , (self.height() - self.icon_size.height()) // 2, icon)
            else:
                painter.drawPixmap(12, (self.height() - self.icon_size.height()) // 2, icon)


        # Dessiner la bordure
        painter.end()

    def show_only_icon(self, value: bool):
        self.only_icon = not value    
        self.updateGeometry()  # demande au layout de recalculer la taille        
        self.update()
        
    def set_text_visible(self, visible: bool):
        self.text_visible = visible
        self.update()
