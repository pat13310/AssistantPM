from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtCore import QByteArray, Qt, QSize
from PySide6.QtGui import QPixmap, QPainter
from PySide6.QtSvg import QSvgRenderer
import os


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


def get_svg_icon(name, size=24, color="#000000"):
    """
    Charger et colorer une icône SVG en utilisant load_colored_svg du module ui_utils
    Utilise une approche très simple et directe
    """
    # Chemin de l'icône dans le dossier assets/icons
    project_icon_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "../..", f"assets/icons/{name}.svg"))
    
    if not os.path.exists(project_icon_path):
        print(f"[Erreur] Icône SVG non trouvée: {name}.svg")
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        return pixmap
    
    # Créer un pixmap carré plus grand que nécessaire
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    
    # Charger l'image SVG avec la couleur demandée
    svg_data = load_colored_svg(project_icon_path, color)
    renderer = QSvgRenderer(svg_data)
    
    # Dessiner le SVG sur le pixmap
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    renderer.render(painter)
    painter.end()
    
    return pixmap


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)

    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root_dir = os.path.dirname(current_script_dir)
    test_icon_path = os.path.join(project_root_dir, "assets", "icons", "search.svg")

    window = QWidget()
    layout = QVBoxLayout(window)

    label_default = QLabel("Icône vectorielle :")
    svg_widget_default = QSvgWidget()
    svg_widget_default.load(load_colored_svg(test_icon_path))
    svg_widget_default.setFixedSize(64, 64)

    label_colored = QLabel("Icône colorée vectorielle :")
    svg_widget_colored = QSvgWidget()
    svg_widget_colored.load(load_colored_svg(test_icon_path, color_str="#22C55E"))
    svg_widget_colored.setFixedSize(64, 64)

    layout.addWidget(label_default)
    layout.addWidget(svg_widget_default)
    layout.addWidget(label_colored)
    layout.addWidget(svg_widget_colored)

    window.setWindowTitle("Test SVG Vectoriel avec Couleur")
    window.resize(240, 300)
    window.show()

    sys.exit(app.exec())
