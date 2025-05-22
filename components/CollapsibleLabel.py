from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QPixmap, QCursor


class CollapsibleLabel(QWidget):
    toggled = Signal(bool)

    def __init__(self, text="Phase du Projet", parent=None):
        super().__init__(parent)
        self.expanded = True  # état initial

        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setFixedHeight(40)
        self.setObjectName("collapsible")

        self._init_widgets()
        self._init_layout()
        self._update_layout_state()

    def _init_widgets(self):
        self.label = QLabel("Phase du Projet")
        self.label.setStyleSheet("color: black; font-weight: bold; font-size: 14px;")
        self.label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        self.chevron = QLabel()
        self.chevron.setFixedSize(QSize(16, 16))
        self.chevron.setAlignment(Qt.AlignCenter)

    def _init_layout(self):
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(8, 4, 8, 4)
        self.layout.setSpacing(8)

    def _clear_layout(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)

    def _update_layout_state(self):
        # Met à jour l'icône
        icon = "chevron-left.svg" if self.expanded else "chevron-right.svg"
        self.chevron.setPixmap(QPixmap(f"assets/icons/{icon}"))

        self._clear_layout()

        if self.expanded:
            self.layout.addWidget(self.label)
            self.layout.addStretch()
            self.layout.addWidget(self.chevron)
        else:
            self.layout.addStretch()
            self.layout.addWidget(self.chevron)
            self.layout.addStretch()

        self.updateGeometry()

    def mousePressEvent(self, event):
        self.expanded = not self.expanded
        self._update_layout_state()
        self.toggled.emit(self.expanded)
        super().mousePressEvent(event)
