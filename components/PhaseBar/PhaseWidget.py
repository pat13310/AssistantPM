from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QSize, Signal,  QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import QColor, QPixmap, QRegion, QIcon, QEnterEvent, QMouseEvent


def render_svg_icon(path: str, size: QSize) -> QPixmap:
    icon = QIcon(path)
    return icon.pixmap(size)


class PhaseWidget(QWidget):
    phaseClicked = Signal(str)

    def __init__(self, phase: dict):
        super().__init__()
        self.phase = phase
        self.hover = False
        self.active = False
        self.validated = False
        self._bgColor = QColor(255, 255, 255)

        self.setCursor(Qt.PointingHandCursor)
        self.setMouseTracking(True)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # --- Cercle principal ---
        self.circle = QWidget()
        self.circle.setFixedSize(125, 125)

        self.circle_layout = QVBoxLayout(self.circle)
        self.circle_layout.setAlignment(Qt.AlignCenter)
        self.circle_layout.setContentsMargins(10, 10, 10, 10)
        self.circle_layout.setSpacing(5)

        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet("border: none; background: transparent;")
        self.circle_layout.addWidget(self.icon_label)

        self.title_label = QLabel(self.phase["name"])
        self.title_label.setAlignment(Qt.AlignCenter)
        self.circle_layout.addWidget(self.title_label)

        layout.addWidget(self.circle)

        self.desc_label = QLabel(self.phase["description"])
        self.desc_label.setWordWrap(True)
        self.desc_label.setAlignment(Qt.AlignCenter)
        self.desc_label.setStyleSheet("""
            color: #6B7280;
            font-size: 11px;
            background: transparent;
            border: none;
            margin-top: 10px;
        """)
        layout.addWidget(self.desc_label)

        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setOffset(1, 4)
        self.shadow.setColor(QColor(0, 0, 0, 65))
        self.circle.setGraphicsEffect(self.shadow)

    

        # Check
        self.check_label = QLabel("✔", self.circle)
        self.check_label.setFixedSize(22, 22)
        self.check_label.move(self.circle.width() - 24, 6)
        self.check_label.setStyleSheet("""
            background-color: #22C55E;
            color: white;
            border-radius: 11px;
            border: 1px solid #22A56F;
            font-size: 13px;
            font-weight: bold;
        """)
        self.check_label.setAlignment(Qt.AlignCenter)
        self.check_label.hide()

        # Animation
        self.anim = QPropertyAnimation(self, b"bgColor")
        self.anim.setDuration(150)
        self.anim.setEasingCurve(QEasingCurve.InOutQuad)

        self.update_styles()

    # Animation: propriété animable
    def get_bgColor(self):
        return self._bgColor

    def set_bgColor(self, color: QColor):
        self._bgColor = color
        self.apply_circle_style()

    bgColor = Property(QColor, get_bgColor, set_bgColor)

    def setValidated(self, validated: bool):
        self.validated = validated
        self.update_styles()

    def set_active(self, active: bool):
        self.active = active
        self.update_styles()

    def compute_bg_color(self):
        if self.validated:
            return QColor(34, 197, 94, 30)
        base = QColor(self.phase["color"])
        if self.active and self.hover:
            return QColor(base.red(), base.green(), base.blue(), 45)
        elif self.active:
            return QColor(base.red(), base.green(), base.blue(), 30)
        elif self.hover:
            return QColor(base.red(), base.green(), base.blue(), 15)
        else:
            return QColor(255, 255, 255)

    def get_border_color(self):
        return "#86EFAC" if self.validated else self.phase["border"]

    def apply_circle_style(self):
        bg = self._bgColor
        border = self.get_border_color()
        self.circle.setStyleSheet(f"""
            background-color: rgba({bg.red()}, {bg.green()}, {bg.blue()}, {bg.alpha()});
            border-radius: 61px;
            border: 2px solid {border};
        """)
        if not self.validated:
            #self.circle.setMask(QRegion(self.circle.rect().adjusted(-1,-1,0,0), QRegion.Ellipse))
            pass
        else:
            self.circle.clearMask()


    def update_styles(self):
        # Lance animation de transition du fond
        target = self.compute_bg_color()
        self.anim.stop()
        self.anim.setStartValue(self._bgColor)
        self.anim.setEndValue(target)
        self.anim.start()

        # Ombre selon hover
        self.shadow.setEnabled(self.hover)

        # Icône
        icon = render_svg_icon(self.phase["icon"], QSize(28, 28))
        self.icon_label.setPixmap(icon)

        # Check visible si validé
        self.check_label.setVisible(self.validated)

        # Titre : vert si validé
        if self.validated:
            self.title_label.setStyleSheet("""
                color: #22C55E;
                font-weight: 600;
                font-size: 11px;
                border: none;
                background: transparent;
            """)
        else:
            self.title_label.setStyleSheet(f"""
                color: {self.phase['color']};
                font-weight: 600;
                font-size: 11px;
                border: none;
                background: transparent;
            """)

    def enterEvent(self, event: QEnterEvent):
        self.hover = True
        self.update_styles()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.hover = False
        self.update_styles()
        super().leaveEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        if self.circle.underMouse() :
            self.active = True
            self.phaseClicked.emit(self.phase["name"])
            self.update_styles()
        super().mousePressEvent(event)
