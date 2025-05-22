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
from PySide6.QtCore import Qt, QSettings, QRect, QSize, Signal
from PySide6.QtGui import QFont, QColor, QPainterPath, QRegion, QKeyEvent # QPixmap n'est plus utilisé

# La manipulation de sys.path est maintenant faite au début du fichier.
# from ui.ui_utils import render_svg_icon # Pas utilisé directement ici


class SignupDialog(QDialog):
    # Signal émis lorsqu'on clique sur "Se connecter"
    switch_to_login = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)

        # Couleurs
        self.border_color = "#22C55E"  # Vert
        self.button_hover_color = "#16A34A"
        self.link_color = "#1D4ED8"  # Bleu pour les liens
        self.link_hover_color = "#1E3A8A"

        # Dimensions et rayon
        radius = 16
        width, height = 420, 480  # Un peu plus haut pour plus de champs
        self.resize(width, height)

        # === Conteneur principal ===
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

        # === Masque arrondi et Ombre ===
        path = QPainterPath()
        path.addRoundedRect(QRect(0, 0, width, height), radius, radius)
        self.setMask(QRegion(path.toFillPolygon().toPolygon()))
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 5)
        shadow.setColor(QColor(0, 0, 0, 70))
        self.setGraphicsEffect(shadow)

        # === Layout interne ===
        internal_layout = QVBoxLayout(self.container)
        internal_layout.setSpacing(15)  # Espacement un peu réduit
        internal_layout.setContentsMargins(
            25, 20, 25, 25
        )  # Conserver les marges actuelles

        # === En-tête avec Titre et Bouton de fermeture ===
        header_controls_layout = QHBoxLayout()

        signup_title_label_header = QLabel("Créer un compte")
        signup_title_label_header.setStyleSheet(
            f"font-size: 18px; font-weight: bold; color: {self.border_color};margin-bottom: 10px; margin-left:130px;"
        )
        signup_title_label_header.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Preferred
        )
        header_controls_layout.addWidget(signup_title_label_header)

        header_controls_layout.addStretch(1)

        self.close_icon_button = QPushButton("✕")
        self.close_icon_button.setCursor(Qt.PointingHandCursor)
        self.close_icon_button.setFixedSize(28, 28)
        self.close_icon_button.setStyleSheet(
            f"""
            QPushButton {{ font-family: 'Arial'; font-size: 15px; font-weight: bold; color: #9CA3AF; background-color: transparent; border: none; border-radius: 14px; }}
            QPushButton:hover {{ color: {self.button_hover_color}; background-color: #D1FAE5; }}
            QPushButton:pressed {{ color: #065F46; background-color: #A7F3D0; }}
        """
        )
        self.close_icon_button.clicked.connect(self.reject)
        header_controls_layout.addWidget(self.close_icon_button)
        internal_layout.addLayout(header_controls_layout)

        # L'ancien titre QLabel séparé est supprimé.
        # Le titre est maintenant dans header_controls_layout.

        # Fonction d'aide pour créer les champs de formulaire (copiée de LoginDialog)
        def form_field(label_text: str, widget: QWidget) -> QVBoxLayout:
            layout = QVBoxLayout()
            label = QLabel(label_text)
            label.setStyleSheet(
                "font-size: 13px; color: #374151; font-weight: 500; padding-bottom: 4px;"
            )
            layout.addWidget(label)
            layout.addWidget(widget)
            layout.setSpacing(4)  # Espacement entre label et QLineEdit
            return layout

        # === Champs de saisie ===
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("John Doe")
        self.name_input.setStyleSheet(
            f"""
            QLineEdit {{ border: 1px solid #D1D5DB; border-radius: 6px; padding: 8px 10px; font-size: 13px; background-color: #F9FAFB; color: #374151; min-height: 20px; }}
            QLineEdit:focus {{ border-color: {self.border_color}; }}
        """
        )
        self.name_input.setFixedHeight(38)
        internal_layout.addLayout(form_field("Nom complet :", self.name_input))

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("exemple@domaine.com")
        self.email_input.setStyleSheet(
            f"""
            QLineEdit {{ border: 1px solid #D1D5DB; border-radius: 6px; padding: 8px 10px; font-size: 13px; background-color: #F9FAFB; color: #374151; min-height: 20px; }}
            QLineEdit:focus {{ border-color: {self.border_color}; }}
        """
        )
        self.email_input.setFixedHeight(38)
        internal_layout.addLayout(form_field("Adresse e-mail :", self.email_input))

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("••••••••")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(
            f"""
            QLineEdit {{ border: 1px solid #D1D5DB; border-radius: 6px; padding: 8px 10px; font-size: 13px; background-color: #F9FAFB; color: #374151; min-height: 20px; }}
            QLineEdit:focus {{ border-color: {self.border_color}; }}
        """
        )
        self.password_input.setFixedHeight(38)
        internal_layout.addLayout(form_field("Mot de passe :", self.password_input))

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("••••••••")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setStyleSheet(
            f"""
            QLineEdit {{ border: 1px solid #D1D5DB; border-radius: 6px; padding: 8px 10px; font-size: 13px; background-color: #F9FAFB; color: #374151; min-height: 20px; }}
            QLineEdit:focus {{ border-color: {self.border_color}; }}
        """
        )
        self.confirm_password_input.setFixedHeight(38)
        internal_layout.addLayout(
            form_field("Confirmer le mot de passe :", self.confirm_password_input)
        )

        internal_layout.addStretch(1)  # Pousse les boutons vers le bas

        # === Bouton d'inscription ===
        self.signup_button = QPushButton("S'inscrire")
        self.signup_button.setCursor(Qt.PointingHandCursor)
        self.signup_button.setFixedHeight(40)
        self.signup_button.setStyleSheet(
            f"""
            QPushButton {{ background-color: {self.border_color}; color: white; font-weight: bold; font-size: 14px; padding: 10px 18px; border: none; border-radius: 6px; }}
            QPushButton:hover {{ background-color: {self.button_hover_color}; }}
        """
        )
        self.signup_button.clicked.connect(self.handle_signup)
        internal_layout.addWidget(self.signup_button)

        # === Ligne de séparation et lien vers Connexion ===
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet(
            "border-top: 1px solid #E5E7EB; margin-top: 10px; margin-bottom: 0px;"
        )  # Ajustement des marges
        internal_layout.addWidget(line)

        switch_to_login_layout = QHBoxLayout()
        switch_to_login_layout.setSpacing(5)
        switch_to_login_layout.addStretch()

        already_account_label = QLabel("Déjà un compte ?")
        already_account_label.setStyleSheet(
            "font-size: 12px; color: #6B7280; border: none;"
        )

        self.go_to_login_button = QPushButton("Se connecter")
        self.go_to_login_button.setCursor(Qt.PointingHandCursor)
        self.go_to_login_button.setStyleSheet(
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
        self.go_to_login_button.clicked.connect(self.switch_to_login_dialog)

        switch_to_login_layout.addWidget(already_account_label)
        switch_to_login_layout.addWidget(self.go_to_login_button)
        switch_to_login_layout.addStretch()
        internal_layout.addLayout(switch_to_login_layout)

        # Centrage et focus
        self.adjustSize()
        if parent:
            self.move(parent.rect().center() - self.rect().center())
        else:
            screen = self.screen().availableGeometry()
            self.move(
                screen.center().x() - self.width() // 2,
                screen.center().y() - self.height() // 2,
            )
        self.name_input.setFocus()

    def handle_signup(self):
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()

        if not all([name, email, password, confirm_password]):
            ToastNotification.show_toast(
                "Erreur d'inscription", 
                "Tous les champs sont requis.",
                ToastNotification.TYPE_WARNING,
                parent=self
            )
            return

        if password != confirm_password:
            ToastNotification.show_toast(
                "Erreur d'inscription", 
                "Les mots de passe ne correspondent pas.",
                ToastNotification.TYPE_WARNING,
                parent=self
            )
            self.confirm_password_input.clear()
            self.confirm_password_input.setFocus()
            return
        
        # Logique d'inscription avec la base de données SQLite
        conn = None
        try:
            conn = sqlite3.connect("projects.db")
            cursor = conn.cursor()

            # Vérifier si l'email existe déjà
            cursor.execute("SELECT Email FROM User WHERE Email = ?", (email,))
            if cursor.fetchone():
                ToastNotification.show_toast(
                    "Erreur d'inscription", 
                    "Cette adresse e-mail est déjà utilisée.",
                    ToastNotification.TYPE_WARNING,
                    parent=self
                )
                return

            # Hacher le mot de passe
            hashed_password = hashlib.sha256(password.encode("utf-8")).hexdigest()

            # Insérer le nouvel utilisateur
            # La table User a les colonnes: Id, Name, Email, Password, Type_user, Langue
            # Type_user et Langue peuvent être NULL ou avoir des valeurs par défaut si définies dans le schéma
            cursor.execute(
                "INSERT INTO User (Name, Email, Password) VALUES (?, ?, ?)",
                (name, email, hashed_password),
            )
            conn.commit()

            print(f"Inscription réussie pour: {name}, Email: {email}")
            ToastNotification.show_toast(
                "Inscription réussie",
                "Votre compte a été créé avec succès. Vous pouvez maintenant vous connecter.",
                ToastNotification.TYPE_SUCCESS,
                parent=self
            )
            self.intended_action = "signup_success"
            self.accept()

        except sqlite3.Error as e:
            ToastNotification.show_toast(
                "Erreur de base de données", 
                f"Erreur lors de l'inscription : {e}",
                ToastNotification.TYPE_ERROR,
                parent=self
            )
            if conn:
                conn.rollback()
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

    # La méthode show_message n'est plus nécessaire
    # def show_message(self, title, text, icon=QMessageBox.Warning):
    #    # ... ancienne implémentation ...

    def switch_to_login_dialog(self):
        self.intended_action = "switch_to_login"  # Pour informer mainprojets.py
        self.switch_to_login.emit()
        self.accept()  # Ferme la dialogue actuelle pour permettre à l'autre de s'ouvrir

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Escape:
            self.reject()
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            focused_widget = QApplication.focusWidget()
            if focused_widget in [
                self.name_input,
                self.email_input,
                self.password_input,
                self.confirm_password_input,
                self.signup_button,
            ]:
                self.handle_signup()
            else:
                super().keyPressEvent(event)


if __name__ == "__main__":
    import os

    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    app = QApplication(sys.argv)
    dialog = SignupDialog()

    def open_login_from_signup():
        print("Signal switch_to_login reçu. Ouverture de LoginDialog (simulation).")
        # Ici, vous instancieriez et afficheriez LoginDialog
        # from components.dialogues.LoginDialog import LoginDialog
        # login_d = LoginDialog()
        # login_d.exec()

    dialog.switch_to_login.connect(open_login_from_signup)
    dialog.show()
    sys.exit(app.exec())
