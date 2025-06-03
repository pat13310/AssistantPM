from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QGridLayout, QPushButton
from PySide6.QtCore import Qt, Signal, QDateTime
from PySide6.QtGui import QFont
from PySide6.QtSvgWidgets import QSvgWidget
import os

# Import de la fonction utilitaire pour charger les SVG colorés
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ui.ui_utils import load_colored_svg

class InteractiveChatBubble(QFrame):
    # Signal émis lorsqu'un bouton est cliqué avec le choix sélectionné
    choiceSelected = Signal(str, str)  # type, choix

    def __init__(self, title, options, bubble_type="technology", parent=None):
        super().__init__(parent)
        self.bubble_type = bubble_type

        # Style de la bulle interactive (bleu pour l'IA)
        self.setStyleSheet(
            "background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, "
            "stop:0 #2196F3, stop:1 #1976D2); "
            "border-radius: 10px; "
            "margin: 2px; "
            "padding: 8px; "
            "border: 1px solid #42A5F5;"
            "font-family: 'Roboto';"
            "font-size: 11px;"
            "color: white;"
        )

        # Layout principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        # Titre du questionnaire
        title_label = QLabel(title)
        title_label.setWordWrap(True)
        title_label.setStyleSheet(
            "font-weight: bold; font-size: 12px; border: none; background: transparent;"
        )
        self.main_layout.addWidget(title_label)

        # Conteneur pour les boutons
        buttons_widget = QWidget()
        buttons_layout = QGridLayout()
        buttons_layout.setSpacing(8)
        buttons_widget.setLayout(buttons_layout)

        # Style commun pour les boutons
        button_style = """
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
                text-align: center;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.5);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.4);
            }
        """

        # Création des boutons pour chaque option
        row, col = 0, 0
        max_cols = 3  # Nombre maximum de colonnes

        for option in options:
            button = QPushButton(option)
            button.setStyleSheet(button_style)
            button.setCursor(Qt.PointingHandCursor)
            button.clicked.connect(
                lambda checked, opt=option: self.on_button_clicked(opt)
            )
            buttons_layout.addWidget(button, row, col)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        self.main_layout.addWidget(buttons_widget)

    def on_button_clicked(self, option):
        # Émettre le signal avec le type de bulle et l'option choisie
        self.choiceSelected.emit(self.bubble_type, option)

        # Horodatage avec style amélioré
        time_layout = QHBoxLayout()
        time_layout.setContentsMargins(10, 0, 180, 0)
        time_layout.setSpacing(0)  # Espacement réduit
        current_script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root_dir = os.path.dirname(current_script_dir)
        # Utiliser l'icône 'clock-9' qui existe dans le dossier assets/icons
        test_icon_path = os.path.join(
            project_root_dir, "assets", "icons", "clock-9.svg"
        )

        svg_widget_colored = QSvgWidget()
        svg_widget_colored.load(
            load_colored_svg("../../assets/icons/clock-9.svg", color_str="#F5F5F5")
        )
        svg_widget_colored.setFixedSize(16, 16)

        svg_widget_colored.setStyleSheet(
            "margin-left: 10px; background: transparent; border: none;"
        )
        time_layout.addWidget(svg_widget_colored)

        # Texte de l'horodatage avec style plus discret
        time_label = QLabel(
            QDateTime.currentDateTime().toString("HH:mm")
        )  # Format plus court sans secondes
        time_label.setAlignment(Qt.AlignLeft)
        time_font = QFont("Roboto", 9)
        time_font.setItalic(True)
        time_label.setFont(time_font)
        time_label.setStyleSheet(
            "color: #F5f5f5; border: none; background: transparent; margin-top: 2px;"
        )
        time_layout.addWidget(time_label)
        time_layout.addStretch(1)  # Pour aligner à gauche

        self.main_layout.addLayout(
            time_layout
        )  # Ajouter directement le layout au lieu d'un frame

        # Pas besoin de réappliquer le layout car il est déjà défini dans __init__
        self.setMaximumWidth(500)  # Légèrement plus étroit
