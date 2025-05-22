from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QWidget,
    QHBoxLayout, QSizePolicy, QGraphicsDropShadowEffect
)
import os # Ajout de os
import sys # Ajout de sys

_current_dir_for_sys_path = os.path.dirname(os.path.abspath(__file__))
_project_root_for_sys_path = os.path.dirname(os.path.dirname(_current_dir_for_sys_path))
if _project_root_for_sys_path not in sys.path:
    sys.path.insert(0, _project_root_for_sys_path)

from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtCore import Qt, QRect,  QPoint, QSize
from PySide6.QtGui import QKeyEvent, QColor, QPainterPath, QRegion
from ui.ui_utils import load_colored_svg


class DocGenerationDlg(QDialog):
    def __init__(self, doc_name: str, parent=None):
        super().__init__(parent)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)

        radius = 20
        width, height = 440, 300

        self.resize(width, height)

        # === Conteneur principal ===
        self.container = QWidget(self)
        self.container.setGeometry(0, 0, width, height)
        self.container.setObjectName("container")
        self.container.setStyleSheet("""
            QWidget#container {
                background-color: #ECFDF5;
            }
        """)

        # === Masque arrondi (shape réelle) ===
        path = QPainterPath()
        path.addRoundedRect(QRect(0, 0, width, height), radius, radius)
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

        # === Ombre autour du conteneur ===
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(50)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 100))
        self.container.setGraphicsEffect(shadow)

        # === Layout interne ===
        layout = QVBoxLayout(self.container)
        layout.setSpacing(24)
        layout.setContentsMargins(40, 40, 40, 40)

        # === En-tête avec icône ===
        header = QHBoxLayout()
        icon_widget = QSvgWidget() # Remplacer QLabel par QSvgWidget
        icon_widget.setFixedSize(QSize(28, 28))
        
        svg_data = load_colored_svg("assets/icons/zap.svg") # Pas de couleur spécifiée
        if svg_data.isEmpty():
            print("Warning: Icon assets/icons/zap.svg could not be loaded for DocGenerationDlg.")
        else:
            icon_widget.load(svg_data)

        title = QLabel("Génération de documentation")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #111827;")

        header.addWidget(icon_widget) # Ajouter le QSvgWidget
        header.addSpacing(10)
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        # === Message principal ===
        msg = QLabel(
            f"La documentation pour <b>{doc_name}</b> n'est pas disponible.<br>"
            "Souhaitez-vous lancer la génération par l'IA ?"
        )
        msg.setWordWrap(True)
        msg.setStyleSheet("font-size: 14px; color: #1F2937;")
        layout.addWidget(msg)

        # === Bouton "Générer" ===
        self.generate_button = QPushButton("Générer la documentation")
        self.generate_button.setCursor(Qt.PointingHandCursor)
        self.generate_button.setStyleSheet("""
            QPushButton {
                background-color: #22C55E;
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 14px;
                border: none;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #16A34A;
            }
        """)
        layout.addWidget(self.generate_button)

        # === Bouton "Annuler" ===
        cancel_button = QPushButton("Annuler")
        cancel_button.setCursor(Qt.PointingHandCursor)
        cancel_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #6B7280;
                font-size: 13px;
                border: none;
                padding: 6px 12px;
            }
            QPushButton:hover {
                color: #111827;
                text-decoration: underline;
            }
        """)
        layout.addWidget(cancel_button, alignment=Qt.AlignHCenter)

        # === Connexions ===
        self.generate_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

        # === Centrage automatique
        self.adjustSize()
        screen = self.screen().availableGeometry()
        self.move(
            screen.center().x() - self.width() // 2,
            screen.center().y() - self.height() // 2
        )

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Escape:
            self.reject()
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.accept()

    def show_modal(self) -> bool:
        return self.exec() == QDialog.Accepted
