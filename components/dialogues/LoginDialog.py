from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
    QHBoxLayout,
    QGraphicsDropShadowEffect,
    # QMessageBox, # Remplacé par ToastNotification
    QApplication,
    QFrame,
    QSizePolicy, 
)
import os # Ajout de os
import sys

_current_dir_for_sys_path = os.path.dirname(os.path.abspath(__file__))
_project_root_for_sys_path = os.path.dirname(os.path.dirname(_current_dir_for_sys_path))
if _project_root_for_sys_path not in sys.path:
    sys.path.insert(0, _project_root_for_sys_path)

# Assurer l'accès à ToastNotification
from components.widgets.ToastNotification import ToastNotification
import sqlite3
import hashlib
import jwt # Importer jwt
from datetime import datetime, timedelta, timezone # Importer datetime pour l'expiration du token
from PySide6.QtCore import Qt, QSettings, QRect, QSize, Signal
from PySide6.QtGui import QFont, QColor, QPainterPath, QRegion, QKeyEvent


class LoginDialog(QDialog):
    switch_to_signup = Signal()

    @staticmethod
    def launch(parent=None):
        dialog = LoginDialog(parent)
        return dialog.exec(), dialog

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)

        self.border_color = "#22C55E"
        self.button_hover_color = "#16A34A"
        self.link_color = "#1D4ED8"
        self.link_hover_color = "#1E3A8A"

        radius = 16
        width, height = 500, 400
        self.resize(width, height)

        self.container = QWidget(self)
        self.container.setGeometry(0, 0, width, height)
        self.container.setObjectName("containerDialog")
        self.container.setStyleSheet(
            f"""
            QWidget#containerDialog {{
                background-color: #FFFFFF;
                border: 2px solid {self.border_color};
                border-radius: {radius}px;
                color: #374151;
            }}
        """
        )

        path = QPainterPath()
        path.addRoundedRect(QRect(0, 0, width, height), radius, radius)
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 5)
        shadow.setColor(QColor(0, 0, 0, 70))
        self.setGraphicsEffect(shadow)

        internal_layout = QVBoxLayout(self.container)
        internal_layout.setSpacing(18)
        internal_layout.setContentsMargins(25, 25, 25, 25) # Conserver les marges actuelles

        header_controls_layout = QHBoxLayout()
        # Pas de addStretch() ici pour l'instant, pour que le titre soit à gauche par défaut

        # Titre "Connexion"
        login_title_label_header = QLabel("Connexion")
        login_title_label_header.setStyleSheet(
            f"font-size: 20px; font-weight: bold; color: {self.border_color};margin-left: 160px; margin-bottom: 10px;"
        )
        login_title_label_header.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred) # Permet au titre de prendre de la place
        header_controls_layout.addWidget(login_title_label_header)

        # Espace flexible entre le titre et le bouton X
        header_controls_layout.addStretch(1)

        self.close_icon_button = QPushButton("✕")
        self.close_icon_button.setCursor(Qt.PointingHandCursor)
        self.close_icon_button.setFixedSize(28, 28)
        self.close_icon_button.setStyleSheet(
            f"""
            QPushButton {{ font-size: 15px; font-weight: bold; color: #9CA3AF; background-color: transparent; border: none; border-radius: 14px; }}
            QPushButton:hover {{ color: {self.button_hover_color}; background-color: #D1FAE5; }}
            QPushButton:pressed {{ color: #065F46; background-color: #A7F3D0; }}
        """
        )
        self.close_icon_button.clicked.connect(self.reject)
        header_controls_layout.addWidget(self.close_icon_button)
        internal_layout.addLayout(header_controls_layout)

        # L'ancien QLabel pour le titre (centré et séparé) est supprimé.
        # Le titre est maintenant géré dans header_controls_layout.
        # La marge inférieure qui était sur login_title_label peut être ajoutée au layout si nécessaire,
        # ou l'espacement du QVBoxLayout (internal_layout) peut être ajusté.
        # Pour l'instant, on compte sur l'espacement de internal_layout.setSpacing(18).

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("exemple@domaine.com")
        self.email_input.setStyleSheet(
            f"""
            QLineEdit {{
                border: 1px solid #D1D5DB; border-radius: 6px; padding: 8px 12px;
                font-size: 14px; background-color: #F9FAFB; color: #374151;
            }}
            QLineEdit:focus {{ border-color: {self.border_color}; }}
        """
        )

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("••••••••")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(
            f"""
            QLineEdit {{
                border: 1px solid #D1D5DB; border-radius: 6px; padding: 8px 12px;
                font-size: 14px; background-color: #F9FAFB; color: #374151;
            }}
            QLineEdit:focus {{ border-color: {self.border_color}; }}
        """
        )

        def form_field(label_text: str, widget: QWidget) -> QVBoxLayout:
            layout = QVBoxLayout()
            label = QLabel(label_text)
            label.setStyleSheet(
                "font-size: 13px; color: #374151; font-weight: 500; padding-bottom: 4px;"
            )
            layout.addWidget(label)
            layout.addWidget(widget)
            layout.setSpacing(4)
            return layout

        internal_layout.addLayout(form_field("Adresse e-mail :", self.email_input))
        internal_layout.addLayout(form_field("Mot de passe :", self.password_input))

        internal_layout.addStretch(1)

        self.login_button = QPushButton("Se connecter")
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.setStyleSheet(
            f"""
            QPushButton {{ background-color: {self.border_color}; color: white; font-weight: bold; font-size: 14px; padding: 10px; border: none; border-radius: 8px; }}
            QPushButton:hover {{ background-color: {self.button_hover_color}; }}
        """
        )
        internal_layout.addWidget(self.login_button)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet(
            "border-top: 1px solid #E5E7EB; margin-top: 20px; margin-bottom: 0px;"
        )
        internal_layout.addWidget(line)

        switch_to_signup_layout = QHBoxLayout()
        switch_to_signup_layout.setSpacing(5)
        switch_to_signup_layout.addStretch()

        no_account_label = QLabel("Pas encore de compte ?")
        no_account_label.setStyleSheet("font-size: 12px; color: #6B7280;")

        self.go_to_signup_button = QPushButton("S'inscrire")
        self.go_to_signup_button.setCursor(Qt.PointingHandCursor)
        self.go_to_signup_button.setStyleSheet(
            f"""
            QPushButton {{ 
                font-size: 12px; 
                font-weight: bold; 
                color: {self.border_color}; /* Couleur verte principale */
                background-color: transparent; 
                border: none; 
                text-decoration: underline; 
            }}
            QPushButton:hover {{ 
                color: {self.button_hover_color}; /* Vert plus foncé au survol */
            }}
        """
        )
        self.go_to_signup_button.clicked.connect(self.switch_to_signup_dialog)

        switch_to_signup_layout.addWidget(no_account_label)
        switch_to_signup_layout.addWidget(self.go_to_signup_button)
        switch_to_signup_layout.addStretch()
        internal_layout.addLayout(switch_to_signup_layout)

        self.adjustSize()
        if parent:
            self.move(parent.rect().center() - self.rect().center())
        else:
            screen = self.screen().availableGeometry()
            self.move(
                screen.center().x() - self.width() // 2,
                screen.center().y() - self.height() // 2,
            )

        self.email_input.setFocus()

    def handle_login(self):
        email = self.email_input.text().strip()
        password = self.password_input.text()

        if not email or not password:
            ToastNotification.show_toast(
                "Erreur de connexion",
                "Veuillez entrer votre e-mail et votre mot de passe.",
                ToastNotification.TYPE_WARNING,
                parent=self # Afficher le toast centré sur ce dialogue
            )
            return

        conn = None
        try:
            conn = sqlite3.connect("projects.db")
            cursor = conn.cursor()
            # Récupérer Id, Name, et Password
            cursor.execute("SELECT Id, Name, Password FROM User WHERE Email = ?", (email,))
            user_record = cursor.fetchone()

            if user_record:
                user_id, stored_name, stored_hashed_password = user_record
                input_hashed_password = hashlib.sha256(
                    password.encode("utf-8")
                ).hexdigest()
                if input_hashed_password == stored_hashed_password:
                    # Génération du JWT
                    secret_key = "votre-cle-secrete-super-difficile-a-deviner" # À gérer de manière sécurisée en production
                    payload = {
                        "user_id": user_id,
                        "username": stored_name,
                        "exp": datetime.now(timezone.utc) + timedelta(hours=1) # Expiration dans 1 heure
                    }
                    jwt_token = jwt.encode(payload, secret_key, algorithm="HS256")
                    
                    settings = QSettings("AssistantIA", "PhaseWizard")
                    settings.setValue("jwt_token", jwt_token)
                    # Plus besoin de stocker current_user_id et current_user_name séparément
                    # s'ils sont dans le token et que le token est la source de vérité.
                    # Cependant, pour un accès rapide au nom sans décoder le token à chaque fois,
                    # on peut toujours le stocker. L'ID est dans le token.
                    settings.setValue("current_user_name", stored_name) 
                                        
                    print(f"Connexion réussie pour {stored_name} (ID: {user_id}). JWT généré.")
                    self.intended_action = "login_success"
                    self.accept()
                else:
                    self.show_login_error()
            else:
                self.show_login_error()

        except sqlite3.Error as e:
            ToastNotification.show_toast(
                "Erreur de base de données", 
                f"Erreur lors de la connexion : {e}",
                ToastNotification.TYPE_ERROR,
                parent=self
            )
        except Exception as e:
            ToastNotification.show_toast(
                "Erreur inattendue", 
                f"Une erreur est survenue : {e}",
                ToastNotification.TYPE_ERROR,
                parent=self
            )
        finally:
            if conn:
                conn.close()

    def show_login_error(self):
        ToastNotification.show_toast(
            "Échec de la connexion",
            "E-mail ou mot de passe incorrect.",
            ToastNotification.TYPE_ERROR,
            parent=self
        )
        self.password_input.clear()
        self.password_input.setFocus()

    # La méthode show_message n'est plus nécessaire si toutes les QMessageBox sont remplacées
    # def show_message(self, title, text, icon=QMessageBox.Warning):
    #     # ... ancienne implémentation ...

    def switch_to_signup_dialog(self):
        self.intended_action = "switch_to_signup"
        self.switch_to_signup.emit()
        self.accept()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Escape:
            self.reject()
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if (
                self.email_input.hasFocus()
                or self.password_input.hasFocus()
                or self.login_button.hasFocus()
            ):
                self.handle_login()
            else:
                super().keyPressEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_dialog = LoginDialog()

    def open_signup_from_login():
        print("Signal switch_to_signup reçu. Ouverture de SignupDialog (simulation).")

    login_dialog.switch_to_signup.connect(open_signup_from_login)
    login_dialog.show()
    sys.exit(app.exec())
