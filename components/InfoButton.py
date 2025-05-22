
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QPen, QFont
from PySide6.QtCore import Qt, Signal, QRect, QSize


class InfoButton(QWidget):
    toggled = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(26, 26)
        self._hovered = False
        self._checked = False
        self.setMouseTracking(True)
        self.setFont(QFont("Segoe UI", 12, QFont.Bold))

    def enterEvent(self, event):
        self._hovered = True
        self.update()

    def leaveEvent(self, event):
        self._hovered = False
        self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._checked = not self._checked
            self.toggled.emit(self._checked)
            self.update()

    def isChecked(self):
        return self._checked

    def setChecked(self, checked: bool):
        self._checked = checked
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect().adjusted(1, 1, -1, -1)
        radius = rect.width() / 2

        bg_color = QColor("#dbeafe") if self._checked else QColor("#e0f2fe") if self._hovered else QColor("white")

        painter.setBrush(bg_color)
        painter.setPen(QPen(QColor("#3b82f6"), 1))
        painter.drawEllipse(rect)

        painter.setPen(QColor("#1d4ed8"))
        painter.setFont(self.font())
        painter.drawText(rect, Qt.AlignCenter, "❔")
