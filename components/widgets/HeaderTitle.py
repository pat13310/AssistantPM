from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtCore import Qt, QSize, QByteArray
from PySide6.QtGui import QPixmap
import os

TITLE_LABEL_STYLE = """
    font-size: 20px;
    font-weight: bold;
    color: #374151;
    margin-left: 10px;
    background-color: transparent;
"""

def load_colored_svg(path: str, color_str: str = None) -> QByteArray:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            svg_text = f.read()
    except FileNotFoundError:
        print(f"[Erreur] Fichier SVG non trouvé: {path}")
        return QByteArray()

    if color_str:
        svg_text = svg_text.replace('fill="black"', 'fill="currentColor"')
        svg_text = svg_text.replace('fill="#000000"', 'fill="currentColor"')
        svg_text = svg_text.replace('stroke="black"', 'stroke="currentColor"')
        svg_text = svg_text.replace('stroke="#000000"', 'stroke="currentColor"')
        svg_text = svg_text.replace("currentColor", color_str)

    return QByteArray(svg_text.encode("utf-8"))

class HeaderTitle(QWidget):
    def __init__(self, title: str, icon_path: str = None, icon_size: QSize = QSize(24, 24), icon_color: str = None, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        layout.setContentsMargins(0, 0, 0, 0)

        if icon_path:
            if icon_path.lower().endswith(".svg"):
                svg_data = load_colored_svg(icon_path, icon_color)
                if not svg_data.isEmpty():
                    svg_icon = QSvgWidget()
                    svg_icon.load(svg_data)
                    svg_icon.setFixedSize(icon_size)
                    svg_icon.setStyleSheet("background-color: transparent; margin-top: 4px;")
                    layout.addWidget(svg_icon)
                else:
                    print(f"[Erreur] SVG vide ou incorrect : {icon_path}")
            else:
                pixmap = QPixmap(icon_path)
                if not pixmap.isNull():
                    pix_icon = QLabel()
                    pix_icon.setPixmap(pixmap.scaled(icon_size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    pix_icon.setStyleSheet("background-color: transparent; margin-top: 4px;")
                    layout.addWidget(pix_icon)
                else:
                    print(f"[Erreur] Image non trouvée : {icon_path}")

        title_label = QLabel(title)
        title_label.setStyleSheet(TITLE_LABEL_STYLE)
        layout.addWidget(title_label)
        layout.addStretch()
