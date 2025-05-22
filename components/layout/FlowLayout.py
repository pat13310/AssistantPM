from PySide6.QtWidgets import QLayout, QSizePolicy
from PySide6.QtCore import QSize, QRect, Qt, QPoint


class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=10, spacing=20):
        super().__init__(parent)
        self.setContentsMargins(margin, margin, margin, margin)
        self._spacing = spacing
        self._items = []

    def addItem(self, item):
        self._items.append(item)
    

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        return self._items[index] if 0 <= index < len(self._items) else None

    def takeAt(self, index):
        return self._items.pop(index) if 0 <= index < len(self._items) else None

    def expandingDirections(self):
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self._do_layout(QRect(0, 0, width, 0), test_only=True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._do_layout(rect, test_only=False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        margins = self.contentsMargins()
        size += QSize(2 * margins.top(), 2 * margins.top())
        return size

    def _do_layout(self, rect, test_only):
        x = rect.x()
        y = rect.y()
        line_items = []
        line_height = 0
        spacing = self._spacing
        max_width = rect.width()

        for item in self._items:
            widget_size = item.sizeHint()
            w, h = widget_size.width(), widget_size.height()

            # Vérifie s'il faut aller à la ligne
            if line_items and x + w > rect.right():
                if not test_only:
                    self._place_line(line_items, x_start=rect.x(), y=y, line_height=line_height)
                x = rect.x()
                y += line_height + spacing
                line_items = []
                line_height = 0

            line_items.append((item, w, h))
            if len(line_items) > 1:
                x += spacing
            x += w
            line_height = max(line_height, h)

        # Dernière ligne
        if line_items and not test_only:
            self._place_line(line_items, x_start=rect.x(), y=y, line_height=line_height)

        return y + line_height - rect.y()

    def _place_line(self, line_items, x_start, y, line_height):
        x = x_start
        for idx, (item, w, h) in enumerate(line_items):
            if idx > 0:
                x += self._spacing
            y_offset = 0
            item.setGeometry(QRect(QPoint(x, y + y_offset), QSize(w, h)))
            x += w
