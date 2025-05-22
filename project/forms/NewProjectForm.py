from PySide6.QtWidgets import (
    QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QHBoxLayout, QGraphicsDropShadowEffect, QFrame, QWidget, QTextEdit
)
from PySide6.QtGui import QFont, QColor,QMouseEvent
from PySide6.QtCore import Qt, Signal, QPoint, QSettings

class NewProjectForm(QWidget):
    projectSubmitted = Signal(str, str) # Ajout de la description au signal

    def __init__(self, parent=None):
        super().__init__(parent)
        # Augmenter la hauteur pour accommoder le nouveau champ
        self.setFixedSize(700, 500)
        self.project_name = ""
        self.project_description = ""
        self.old_pos = QPoint()
        self.settings = QSettings("AssistantPM", "ProjectNameDlg")
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet("""background-color: white;""")
    
        # --- Conteneur principal avec ombre et arrondi ---
        main_frame = QFrame(self)
        main_frame.setObjectName("mainBox")
        main_frame.setStyleSheet("""
            QFrame#mainBox {
                background-color: white;
                border-radius: 15px;
                border: 1px solid #d1d5db;
            }
        """)
        # Ajuster la géométrie pour correspondre à la taille de la fenêtre
        main_frame.setGeometry(0, 0, 700, 500)

        layout = QVBoxLayout(main_frame)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)

        # Barre de titre avec bouton fermer
        header_layout = QHBoxLayout()
        title = QLabel("Assistant IA pour la Gestion de Projet")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #1f2937;")
        title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        
        header_layout.addWidget(title)
        header_layout.addStretch()

        # Texte d'introduction
        description = QLabel(
            "Bienvenue dans votre assistant intelligent qui vous guidera à travers toutes les phases\n"
            "de votre projet informatique, de l'analyse des besoins au déploiement."
        )
        description.setAlignment(Qt.AlignCenter)
        description.setStyleSheet("color: #4b5563; font-size: 14px; background-color: white;")

        # Saisie nom du projet
        name_label = QLabel("Nom de votre projet")
        name_label.setFont(QFont("Arial", 11))
        name_label.setStyleSheet("color: #000000;") # Peut être harmonisé avec le style des autres labels

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ex: Plateforme E-commerce")
        self.name_input.textChanged.connect(self.toggle_button)
        self.name_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                font-size: 13px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                background-color: #f9fafb;
                color: #374151;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
                background-color: #ffffff;
            }
        """)

        # Bouton principal
        self.start_button = QPushButton("Commencer le projet  →")
        self.start_button.setEnabled(False)
        self.set_button_style(False)
        self.start_button.clicked.connect(self.on_submit)
        self.start_button.setMinimumHeight(40)
        # Retirer setSizePolicy et setFixedWidth pour laisser le bouton prendre sa taille naturelle
        # et être centré par le button_layout.
        # self.start_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed) 
        # self.start_button.setFixedWidth(200)
        
        self.start_button.adjustSize()  # ajuste au texte

        self.start_button.setMinimumHeight(40)
        self.start_button.adjustSize()

        # Centrage horizontal du bouton
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.start_button)
        button_layout.addStretch()




        # Ajout au layout
        layout.addLayout(header_layout)
        layout.addSpacing(10)
        layout.addWidget(description)
        layout.addSpacing(10)
        layout.addWidget(name_label)
        layout.addWidget(self.name_input)
        layout.addSpacing(15) # Espace avant le champ description

        # Saisie description du projet
        description_label = QLabel("Description de votre projet")
        description_label.setFont(QFont("Arial", 11))
        description_label.setStyleSheet("color: #000000;")

        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Décrivez brièvement votre projet ici...")
        self.description_input.setFixedHeight(80) # Hauteur pour plusieurs lignes
        self.description_input.setStyleSheet("""
            QTextEdit {
                padding: 8px 12px;
                font-size: 13px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                background-color: #f9fafb;
                color: #374151;
            }
            QTextEdit:focus {
                border: 2px solid #4CAF50;
                background-color: #ffffff;
            }
        """)
        layout.addWidget(description_label)
        layout.addWidget(self.description_input)

        layout.addLayout(button_layout)


        saved_name = self.settings.value("nom_projet", "")
        self.name_input.setText(saved_name)
        saved_description = self.settings.value("description_projet", "")
        self.description_input.setPlainText(saved_description)


    def toggle_button(self, text):
        enabled = bool(text.strip())
        self.start_button.setEnabled(enabled)
        self.set_button_style(enabled)

    def set_button_style(self, enabled):
        if enabled:
            self.start_button.setStyleSheet("""
                QPushButton {
                    color: white;
                    font-weight: bold;
                    font-size: 14px;
                    padding: 10px;
                    border-radius: 8px;
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:0,
                        stop:0 #4CAF50, stop:1 #81C784
                    );
                }
                QPushButton:hover {
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:0,
                        stop:0 #43A047, stop:1 #66BB6A
                    );
                    border: 1px solid #174f0f;
                }
            """)
        else:
            self.start_button.setStyleSheet("""
                QPushButton {
                    color: white;
                    font-size: 14px;
                    padding: 10px;
                    border-radius: 8px;
                    background-color: #d1d5db;
                }
            """)

    def on_submit(self):
        self.project_name = self.name_input.text().strip()
        self.project_description = self.description_input.toPlainText().strip()
        # 🔐 Sauvegarde dans QSettings
        self.settings.setValue("nom_projet", self.project_name)
        self.settings.setValue("description_projet", self.project_description)
        self.projectSubmitted.emit(self.project_name, self.project_description)

    # Pour déplacer la fenêtre frameless
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent):
        if not self.old_pos.isNull():
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPosition().toPoint()
