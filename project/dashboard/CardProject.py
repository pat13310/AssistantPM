import weakref
import os
import sys

# Ajouter le chemin racine du projet au sys.path pour les imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, os.pardir, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QGraphicsDropShadowEffect # QFrame retiré
)
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtCore import (
    Qt, QTimer, QRect, QObject, QSize, Signal, QByteArray
)
from PySide6.QtGui import QFont, QEnterEvent, QColor

# Importer le composant IconWithText
from components.ui.IconWithText import IconWithText

# Importer la fonction load_colored_svg une seule fois
try:
    from ui.ui_utils import load_colored_svg
except ImportError:
    # Fonction de secours si l'import échoue
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


# Classe pour stocker les données du projet
class ProjectData:
    def __init__(self, id=None, title="", description="", created_date="", states=None):
        self.id = id
        self.title = title
        self.description = description
        self.created_date = created_date
        self.states = states or []


class CardProject(QWidget, QObject):

    # Signal pour indiquer qu'une carte a été cliquée, avec le titre du projet
    clicked = Signal(str)
    
    # Nouveau signal pour émettre toutes les données du projet
    project_data_clicked = Signal(object)

    def __init__(self, title: str, description: str, created: str, project_states: list, project_id=None):
        super().__init__()
        
        # Stocker les données du projet dans un objet ProjectData
        self.project_data = ProjectData(
            id=project_id,
            title=title,
            description=description,
            created_date=created,
            states=project_states
        )

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setMouseTracking(True)
        self.setWindowOpacity(0)
        self.setMinimumSize(320, 200)
        self.setMaximumSize(320, 200)
        self.setFixedHeight(210)


        # Ombre douce
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(15)
        self.shadow.setOffset(0, 2)
        self.shadow.setColor(Qt.gray)
        self.setGraphicsEffect(self.shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20) # Marges externes de la carte
        layout.setSpacing(8) # Espacement vertical réduit entre les éléments
        
        # Utiliser le composant IconWithText pour le titre avec l'icône
        title_component = IconWithText(
            text=title,
            icon_name="presentation",
            color="#03b541",  # Couleur verte
            font_size=12,
            icon_size=20
        )
        
        # Stocker une référence au label du titre pour pouvoir le mettre à jour si nécessaire
        self.title_label = title_component.text_label
        
        # Ajouter le composant au layout principal
        layout.addWidget(title_component)

        self.desc_label = QLabel(description)
        self.desc_label.setStyleSheet("color: #555; border: none;")
        self.desc_label.setWordWrap(True)
        layout.addWidget(self.desc_label)

        self.date_label = QLabel(f"Créé le : {created}")
        self.date_label.setStyleSheet("color: #888; font-size: 9.5pt; border: none;")
        layout.addWidget(self.date_label)

        # Layout pour les états du projet
        self.states_layout = QHBoxLayout()
        self.states_layout.setContentsMargins(12, 0, 0, 0) # Conserver ces marges pour le layout des états
        self.states_layout.setSpacing(12) # Conserver cet espacement entre les conteneurs d'icônes
        self.states_layout.setAlignment(Qt.AlignLeft) # Aligner les icônes à gauche

        icon_svg_size = QSize(16, 16) # Taille souhaitée pour les icônes SVG

        # Déterminer le chemin de base pour les icônes
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets", "icons"))
        # check_icon_path n'est plus utilisé, la couleur indique la validation

        # Liste des icônes pour chaque phase (lorsqu'elle n'est pas validée)
        # Correspond aux états: markdown_generated, docs_generated, tree_generated, 
        # source_code_generated, tests_generated, deployment_info_generated
        phase_icons_default_names = [
            "book-open.svg",      # markdown_generated
            "book.svg",           # docs_generated
            "folder-tree.svg",    # tree_generated
            "code.svg",           # source_code_generated
            "test-tube.svg",      # tests_generated
            "rocket.svg"          # deployment_info_generated
        ]

        # La fonction load_colored_svg est déjà importée au début du fichier

        for i, state in enumerate(project_states):
            svg_widget = QSvgWidget()
            svg_widget.setFixedSize(icon_svg_size)
            
            # Déterminer l'icône de phase à utiliser (toujours l'icône de phase)
            if i < len(phase_icons_default_names):
                phase_icon_name = phase_icons_default_names[i]
            else:
                phase_icon_name = "info.svg" # Fallback
            
            icon_file_path = os.path.join(base_path, phase_icon_name)

            # Déterminer la couleur en fonction de l'état
            color_str = "#28a745" if state else "#AAAAAA" # Vert si validé, gris sinon

            if os.path.exists(icon_file_path):
                svg_data = load_colored_svg(icon_file_path, color_str)
                if not svg_data.isEmpty():
                    svg_widget.load(svg_data)
                else:
                    print(f"Warning: SVG data is empty for {icon_file_path} with color {color_str}")
            else:
                print(f"Warning: Icon file not found - {icon_file_path}")
                # Optionnel: charger une icône de secours directement si le fichier principal est introuvable
                fallback_icon_path = os.path.join(base_path, "info.svg")
                if os.path.exists(fallback_icon_path):
                     svg_data = load_colored_svg(fallback_icon_path, color_str) # Colorer aussi le fallback
                     if not svg_data.isEmpty():
                         svg_widget.load(svg_data)

            self.states_layout.addWidget(svg_widget)
        
        # Ajout du layout des états au layout principal
        layout.addLayout(self.states_layout)
        
        layout.addStretch(1) # Pousse tout le contenu vers le haut
    

        self.update_style(False)


    def update_style(self, hover: bool):
        bg_color = "#d4edda" if hover else "#e2f7e9"
        border_color = "#28a745" if hover else "#a3d1a8"
        cursor_style = "pointer"
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                border-radius: 15px;
                border: 2px solid {border_color};
            }}
        """)
        self.setCursor(Qt.PointingHandCursor)
        self.shadow.setBlurRadius(24 if hover else 15)
        self.shadow.setYOffset(6 if hover else 2)

    def enterEvent(self, event: QEnterEvent):
        self.update_style(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.update_style(False)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        # Gérer le clic sur la carte ici
        print(f"Card clicked: {self.title_label.text()}")
        
        # Émettre le signal avec le titre du projet pour la compatibilité avec le code existant
        self.clicked.emit(self.title_label.text().replace('<b>', '').replace('</b>', ''))
        
        # Émettre le signal avec toutes les données du projet
        self.project_data_clicked.emit(self.project_data)
        
        super().mousePressEvent(event)