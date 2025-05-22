from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QWidget,
    QHBoxLayout, QGraphicsDropShadowEffect, QMessageBox, QApplication, QComboBox
)
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtCore import Qt, QSettings, QRect, QSize
from PySide6.QtGui import QIcon, QColor, QPainterPath, QRegion, QPixmap, QKeyEvent

import os
import sys

# Ajout au sys.path pour les imports
_current_dir_for_sys_path = os.path.dirname(os.path.abspath(__file__))
_project_root_for_sys_path = os.path.dirname(os.path.dirname(_current_dir_for_sys_path))
if _project_root_for_sys_path not in sys.path:
    sys.path.insert(0, _project_root_for_sys_path)

# Chargement SVG coloré (doit retourner QByteArray SVG)
from ui.ui_utils import load_colored_svg


class IconToggleButton(QPushButton):
    def __init__(self, icon_normal, icon_hover, icon_checked, icon_checked_hover, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(32, 32)
        self.setStyleSheet("QPushButton { border: none; background: transparent; }")

        self.icon_normal = icon_normal
        self.icon_hover = icon_hover
        self.icon_checked = icon_checked
        self.icon_checked_hover = icon_checked_hover

        self.setIcon(self.icon_normal)
        self.setIconSize(QSize(20, 20))

    def enterEvent(self, event):
        if self.isChecked():
            self.setIcon(self.icon_checked_hover)
        else:
            self.setIcon(self.icon_hover)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.isChecked():
            self.setIcon(self.icon_checked)
        else:
            self.setIcon(self.icon_normal)
        super().leaveEvent(event)

    def toggleIcon(self, checked):
        if checked:
            self.setIcon(self.icon_checked)
        else:
            self.setIcon(self.icon_normal)


class ApiKeyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)

        radius = 16
        width, height = 480, 340
        self.resize(width, height)

        # === Conteneur principal ===
        self.container = QWidget(self)
        self.container.setGeometry(0, 0, width, height)
        self.container.setObjectName("containerDialog")
        self.container.setStyleSheet(f"""
            QWidget#containerDialog {{
                background-color: #FFFFFF;
                border: 1px solid #D1D5DB;
                border-radius: {radius}px;
                color: #374151;
            }}
        """)

        # === Masque arrondi ===
        path = QPainterPath()
        path.addRoundedRect(QRect(0, 0, width, height), radius, radius)
        self.setMask(QRegion(path.toFillPolygon().toPolygon()))

        # === Ombre ===
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 5)
        shadow.setColor(QColor(0, 0, 0, 70))
        self.setGraphicsEffect(shadow)

        # === Layout principal ===
        layout = QVBoxLayout(self.container)
        layout.setSpacing(18)
        layout.setContentsMargins(25, 25, 25, 25)

        # === En-tête ===
        header = QHBoxLayout()
        icon_widget = QSvgWidget()
        icon_widget.setFixedSize(QSize(24, 24))

        svg_data = load_colored_svg("assets/icons/settings.svg", "#22C55E")
        if not svg_data.isEmpty():
            icon_widget.load(svg_data)

        title = QLabel("Configuration Clé API")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1F2937;")

        self.close_icon_button = QPushButton("✕")
        self.close_icon_button.setCursor(Qt.PointingHandCursor)
        self.close_icon_button.setFixedSize(28, 28)
        self.close_icon_button.setStyleSheet("""
            QPushButton {
                font-size: 15px;
                font-weight: bold;
                color: #9CA3AF;
                background-color: transparent;
                border: none;
                border-radius: 14px;
            }
            QPushButton:hover {
                color: #16A34A;
                background-color: #D1FAE5;
            }
        """)
        self.close_icon_button.clicked.connect(self.reject)

        header.addWidget(icon_widget)
        header.addSpacing(10)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.close_icon_button)
        layout.addLayout(header)

        # === Fournisseur IA ===
        layout.addWidget(self.label("Choisissez le fournisseur d'IA :"))

        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["OpenAI", "DeepSeek", "Gemini", "Mistral", "Claude"])
        self.provider_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                padding: 8px 10px;
                font-size: 13px;
                background-color: #F9FAFB;
                color: #374151;
            }
            QComboBox:focus {
                border: 1px solid #0da31e;
            }
        """)
        layout.addWidget(self.provider_combo)

        # === Champ Clé API + œil ===
        layout.addWidget(self.label("Clé API :"))

        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                padding: 8px 10px;
                font-size: 13px;
                background-color: #F9FAFB;
                color: #374151;
            }
            QLineEdit:focus {
                border-color: #0da31e;
            }
        """)

        # Bouton œil SVG
        #self.toggle_visibility_button = QPushButton()
        self.eye_icon = self.load_svg_icon("assets/icons/eye.svg", "#374151")
        self.eye_icon_hover = self.load_svg_icon("assets/icons/eye.svg", "#16A34A")
        self.eye_off_icon = self.load_svg_icon("assets/icons/eye-off.svg", "#374151")
        self.eye_off_icon_hover = self.load_svg_icon("assets/icons/eye-off.svg", "#16A34A")
        
        self.toggle_visibility_button = IconToggleButton(
            icon_normal=self.eye_icon,
        icon_hover=self.eye_icon_hover,
        icon_checked=self.eye_off_icon,
        icon_checked_hover=self.eye_off_icon_hover
        )
        #self.toggle_visibility_button.toggled.connect(self.toggle_api_key_visibility)

        
        
        self.toggle_visibility_button.setCheckable(True)
        self.toggle_visibility_button.setCursor(Qt.PointingHandCursor)
        self.toggle_visibility_button.setFixedSize(32, 32)
        self.toggle_visibility_button.setStyleSheet("QPushButton { border: none; background: transparent; }")

        # Charger et colorer les SVG en gris foncé
        self.eye_icon = self.load_svg_icon("assets/icons/eye.svg", "#374151")
        self.eye_off_icon = self.load_svg_icon("assets/icons/eye-off.svg", "#374151")
        self.toggle_visibility_button.setIcon(self.eye_icon)
        self.toggle_visibility_button.setIconSize(QSize(20, 20))
        self.toggle_visibility_button.toggled.connect(self.toggle_api_key_visibility)

        # Champ + bouton dans un layout
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(0)
        input_layout.addWidget(self.api_key_input)
        input_layout.addWidget(self.toggle_visibility_button)
        layout.addLayout(input_layout)

        # === Récupération des données
        self.settings = QSettings("AssistantIA", "PhaseWizard")
        current_provider = self.settings.value("ai_provider", "OpenAI")
        index = self.provider_combo.findText(current_provider)
        if index >= 0:
            self.provider_combo.setCurrentIndex(index)

        self.provider_combo.currentTextChanged.connect(self.load_api_key_for_provider)
        self.load_api_key_for_provider(current_provider)

        layout.addStretch(1)

        # === Bouton Enregistrer
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.save_button = QPushButton("Enregistrer")
        self.save_button.setCursor(Qt.PointingHandCursor)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #22C55E;
                color: white;
                font-weight: bold;
                font-size: 13px;
                padding: 10px 18px;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #16A34A;
            }
        """)
        self.save_button.clicked.connect(self.save_api_key)
        button_layout.addWidget(self.save_button)
        layout.addLayout(button_layout)

        self.adjustSize()
        if parent:
            self.move(parent.rect().center() - self.rect().center())
        else:
            screen = self.screen().availableGeometry()
            self.move(screen.center().x() - self.width() // 2, screen.center().y() - self.height() // 2)

        
    # === Méthodes utilitaires ===

    def label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet("font-size: 13px; color: #374151; border: none;")
        return lbl

    def load_svg_icon(self, path: str, color: str) -> QIcon:
        svg_data = load_colored_svg(path, color)
        pix = QPixmap()
        pix.loadFromData(svg_data)
        return QIcon(pix)

    def toggle_api_key_visibility(self, visible: bool):
        self.api_key_input.setEchoMode(QLineEdit.Normal if visible else QLineEdit.Password)
        self.toggle_visibility_button.toggleIcon(visible)

    def load_api_key_for_provider(self, provider: str):
        key = self.settings.value(f"api_key_{provider.lower()}", "")
        self.api_key_input.setText(key)

    def save_api_key(self):
        api_key = self.api_key_input.text().strip()
        if not api_key:
            QMessageBox.warning(self, "Clé API manquante", "Veuillez entrer une clé API.")
            return
        provider = self.provider_combo.currentText()
        self.settings.setValue("ai_provider", provider)
        self.settings.setValue(f"api_key_{provider.lower()}", api_key)
        self.accept()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Escape:
            self.reject()
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if self.api_key_input.hasFocus() and self.api_key_input.text().strip():
                self.save_api_key()
            else:
                super().keyPressEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = ApiKeyDialog()
    dialog.show()
    sys.exit(app.exec())
