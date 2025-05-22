from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QSize, QRect
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QMouseEvent, QImage, QPixmap
from PySide6.QtSvg import QSvgRenderer

class StepItem(QWidget):
    def __init__(self, title: str, subtitle: str, icon_path: str, color: QColor, parent=None):
        super().__init__(parent)
        self.title = title
        self.subtitle = subtitle
        self.icon_path = icon_path
        self.color = color

        self.hovered = False
        self.active = False
        self.circle_diameter = 80
        self.icon_renderer = QSvgRenderer(icon_path)

        self.setFixedSize(180, 140)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_Hover, True)
        self.setCursor(Qt.PointingHandCursor)

    def sizeHint(self):
        return QSize(180, 140)

    def enterEvent(self, event):
        self.hovered = True
        self.update()

    def leaveEvent(self, event):
        self.hovered = False
        self.update()

    def mousePressEvent(self, event: QMouseEvent):
        self.active = True
        self.update()
        print(f"Étape sélectionnée : {self.title}")

    def reset(self):
        self.active = False
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        #painter.setRenderHint(QPainter.HighQualityAntialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        # Couleurs
        border_color = QColor(self.color)
        text_color = QColor(self.color)
        if self.hovered:
            border_color.setAlpha(180)
        elif not self.active:
            border_color.setAlpha(80)
            text_color = QColor("#888")

        subtitle_color = QColor("#666")

        # Cercle
        cx = self.width() // 2
        rect = QRect(cx - self.circle_diameter // 2, 0, self.circle_diameter, self.circle_diameter)
        painter.setPen(QPen(border_color, 1.5, Qt.SolidLine))
        painter.setBrush(Qt.transparent)
        painter.drawEllipse(rect)

        if self.icon_renderer:
            icon_size = QSize(28, 28)
            icon_pixmap = self.render_colored_svg(text_color, icon_size)
            icon_x = cx - icon_size.width() // 2
            icon_y = rect.center().y() - icon_size.height() // 2
            painter.drawPixmap(icon_x, icon_y, icon_pixmap)

        # Titre
        painter.setFont(QFont("Segoe UI", 10, QFont.Bold))
        painter.setPen(text_color)
        painter.drawText(QRect(0, self.circle_diameter + 4, self.width(), 20), Qt.AlignHCenter, self.title)

        # Description
        painter.setFont(QFont("Segoe UI", 9))
        painter.setPen(subtitle_color)
        painter.drawText(QRect(10, self.circle_diameter + 28, self.width() - 20, 40),
                        Qt.AlignHCenter | Qt.TextWordWrap, self.subtitle)

        painter.end()
    
    def render_colored_svg(self, color: QColor, size: QSize) -> QPixmap:
        image = QImage(size, QImage.Format_ARGB32)
        image.fill(Qt.transparent)
        painter = QPainter(image)
        painter.setRenderHint(QPainter.Antialiasing)
        if self.icon_renderer:
            self.icon_renderer.render(painter, QRect(0, 0, size.width(), size.height()))
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(image.rect(), color)
        painter.end()
        return QPixmap.fromImage(image)

