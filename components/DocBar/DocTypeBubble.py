from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QPainterPath, QMouseEvent, QCursor
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtCore import Qt, QSize, QRectF, Signal


class DocTypeBubble(QWidget):
    clicked = Signal(str)

    def __init__(self, title: str, subtitle: str, icon_path: str = None,
                 is_ready: bool = False, parent=None):
        super().__init__(parent)
        self.title = title
        self.subtitle = subtitle
        self.icon_path = icon_path
        self.is_ready = is_ready
        self.hover = False

        self.setFixedSize(QSize(140, 140))
        self.setAttribute(Qt.WidgetAttribute.WA_Hover)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        radius = 120
        center_x = (self.width() - radius) // 2
        center_y = (self.height() - radius) // 2

        bg_color = QColor("#D1FAE5") if self.is_ready else QColor("#F1F5F9")
        border_color = QColor("#4CAF50") if self.is_ready else QColor("#94A3B8")
        if self.hover:
            bg_color = bg_color.darker(110)

        # Ombre
        shadow_path = QPainterPath()
        shadow_path.addEllipse(center_x + 4, center_y + 4, radius, radius)
        painter.fillPath(shadow_path, QColor(0, 0, 0, 40))

        # Cercle principal
        circle_path = QPainterPath()
        circle_path.addEllipse(center_x, center_y, radius, radius)
        painter.setPen(QPen(border_color, 1.2))
        painter.setBrush(bg_color)
        painter.drawPath(circle_path)

        # Icône SVG (si présente)
        if self.icon_path:
            icon_size = 36
            icon_rect = QRectF(
                self.width() / 2 - icon_size / 2,
                center_y + 12,
                icon_size,
                icon_size
            )
            svg_renderer = QSvgRenderer(self.icon_path)
            svg_renderer.render(painter, icon_rect)
            text_y_offset = center_y + 60  # sous l’icône
        else:
            text_y_offset = center_y + 30  # recentré verticalement

        # Texte
        painter.setPen(Qt.black)
        font = QFont("Arial", 9, QFont.Bold)
        painter.setFont(font)

        text_rect = QRectF(center_x, text_y_offset, radius, 40)
        painter.drawText(text_rect, Qt.AlignCenter, f"{self.title}\n{self.subtitle}")

    def enterEvent(self, event):
        self.hover = True
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.update()

    def leaveEvent(self, event):
        self.hover = False
        self.setCursor(QCursor(Qt.ArrowCursor))
        self.update()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(f"{self.title} {self.subtitle}")
