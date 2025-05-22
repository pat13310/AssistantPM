import sys
import os
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QStackedWidget,
    QDialog,
)
from PySide6.QtCore import QSettings
from components.widgets.ToastNotification import ToastNotification
from Ui_AssistantPM import Ui_AssistantPM
import sqlite3
import jwt

from components.CollapsibleLabel import CollapsibleLabel
from menus.GeneralMenu import GeneralMenu

from project.dashboard.ProjectDashboard import ProjectDashboard
from project.forms.NewProjectForm import NewProjectForm
from project.forms.EditProjectForm import EditProjectForm
from PySide6.QtWidgets import QLabel
from components.infos.models import ProjectData, Phase
from components.wizard.PhaseWizardWidget import PhaseWizardWidget
from menus.CollapsibleSection import CollapsibleSection
from menus.MenuLabel import MenuLabel
from components.dialogues.ApiKeyDialog import ApiKeyDialog
from components.dialogues.LoginDialog import LoginDialog
from components.dialogues.SignupDialog import SignupDialog
from project.documents.DocumentationOverviewWidget import DocumentationOverviewWidget, DocType
from project.documents.DocumentationWidget import DocumentationWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_AssistantPM()
        self.ui.setupUi(self)

        # Widgets personnalisés
        from components.infos.data_phases import initial_phases
        self.menu = GeneralMenu()
        self.project_data = ProjectData(name="Moclearn Projet", phases=initial_phases)
        # Zone principale : stack des vues
        self.stack = QStackedWidget()
        self.stack.setMinimumSize(800, 500)
        self.project_dashboard = ProjectDashboard()
        self.new_project_form = NewProjectForm()
        self.edit_project_form = EditProjectForm(self.project_data)
        self.phase_wizard = PhaseWizardWidget(self.project_data)
        self.documentation_overview = DocumentationOverviewWidget()

        self.stack.addWidget(self.project_dashboard)
        self.stack.addWidget(self.new_project_form)
        self.stack.addWidget(self.edit_project_form)
        self.stack.addWidget(self.phase_wizard)
        self.stack.addWidget(self.documentation_overview)

        # Insertion dans main
        if self.ui.main.layout() is None:
            self.ui.main.setLayout(QVBoxLayout())
        self.ui.main.layout().addWidget(self.stack)

        # Menu latéral
        sidebar_layout = self.ui.sidebar.layout()
        sidebar_layout.addWidget(self.menu)
        self.setup_connections()
        self.display_view(self.project_dashboard)

    def setup_connections(self):
        self.menu.accueil_clicked.connect(
            lambda: self.display_view(self.project_dashboard)
        )
        self.menu.nouveau_clicked.connect(
            lambda: self.display_view(self.new_project_form)
        )
        self.menu.modifier_clicked.connect(
            lambda: self.display_view(self.edit_project_form)
        )
        self.menu.configuration_clicked.connect(self.open_api_key_dialog)
        self.menu.logout_clicked.connect(self.handle_logout)
        self.menu.phase_selected.connect(self.handle_phase_selection)
        self.new_project_form.projectSubmitted.connect(self.create_new_project)

        self.menu.documentation_clicked.connect(self.display_documentation_overview)
        self.documentation_overview.docTypeClicked.connect(self.print_doc_type)

    def display_documentation_overview(self):
        self.display_view(self.documentation_overview)

    def print_doc_type(self, doc_type: DocType):
        print(f"Clicked on document type: {doc_type.name}")
        documentation_widget = DocumentationWidget(doc_type)
        self.stack.addWidget(documentation_widget)
        self.display_view(documentation_widget)

    def display_view(self, widget):
        self.stack.setCurrentWidget(widget)

    def handle_phase_selection(self, phase_id: str):
        self.display_view(self.phase_wizard)

    def toggle_sidebar_width(self, expanded: bool):
        self.ui.splitter.setSizes([400 if expanded else 1, 0])
        self.menu.toggle_text_visibility(expanded)

    def open_api_key_dialog(self):
        dialog = ApiKeyDialog(self)
        dialog.exec()

    def handle_logout(self):
        print("Déconnexion demandée.")
        settings = QSettings("AssistantIA", "PhaseWizard")
        settings.remove("jwt_token")
        settings.remove("current_user_name")
        settings.remove("current_user_id")

        self.menu.update_logout_button_visibility(False)
        QApplication.instance().quit()

    def create_new_project(self, project_name: str, project_description: str):
        print(f"Tentative de création du projet: {project_name}")
        settings = QSettings("AssistantIA", "PhaseWizard")
        jwt_token = settings.value("jwt_token", None)

        if not jwt_token:
            ToastNotification.show_toast(
                "Erreur Utilisateur",
                "Aucun utilisateur connecté. Impossible de créer le projet.",
                ToastNotification.TYPE_WARNING,
                parent=self,
            )
            self.handle_logout()
            return

        try:
            secret_key = "votre-cle-secrete-super-difficile-a-deviner"
            payload = jwt.decode(jwt_token, secret_key, algorithms=["HS256"])
            user_id = payload.get("user_id")

            if not user_id:
                ToastNotification.show_toast(
                    "Erreur Token",
                    "Impossible de récupérer l'ID utilisateur depuis le token.",
                    ToastNotification.TYPE_ERROR,
                    parent=self
                )
                return

            conn = None
            try:
                conn = sqlite3.connect("projects.db")
                cursor = conn.cursor()

                cursor.execute(
                    "SELECT Id FROM Project WHERE Nom = ? AND Id_user = ?",
                    (project_name, user_id),
                )
                existing_project = cursor.fetchone()

                if existing_project:
                    ToastNotification.show_toast(
                        "Erreur de Création",
                        f"Un projet nommé '{project_name}' existe déjà pour cet utilisateur.",
                        ToastNotification.TYPE_WARNING,
                        parent=self,
                    )
                    return

                # La table Project a: Id, Nom, Description, Date_Creation, Date_Modification, Id_user
                cursor.execute(
                    "INSERT INTO Project (Nom, Description, Id_user) VALUES (?, ?, ?)",
                    (project_name, project_description, user_id),
                )
                conn.commit()
                project_id = cursor.lastrowid
                ToastNotification.show_toast(
                    "Projet Créé",
                    f"Le projet '{project_name}' (ID: {project_id}) a été créé avec succès pour l'utilisateur ID: {user_id}.",
                    ToastNotification.TYPE_SUCCESS,
                    parent=self
                )
            
                if hasattr(self.project_dashboard, "load_projects"):
                    self.project_dashboard.load_projects()
                self.display_view(self.project_dashboard)

            except sqlite3.Error as e:
                ToastNotification.show_toast(
                    "Erreur Base de Données",
                    f"Erreur lors de la création du projet : {e}",
                    ToastNotification.TYPE_ERROR,
                    parent=self
                )
                if conn:
                    conn.rollback()
            finally:
                if conn:
                    conn.close()

        except jwt.ExpiredSignatureError:
            ToastNotification.show_toast(
                "Session Expirée",
                "Votre session a expiré. Veuillez vous reconnecter.",
                ToastNotification.TYPE_WARNING,
                parent=self
            )
            self.handle_logout()
        except jwt.InvalidTokenError:
            ToastNotification.show_toast(
                "Erreur de Session",
                "Session invalide. Veuillez vous reconnecter.",
                ToastNotification.TYPE_ERROR,
                parent=self
            )
            self.handle_logout()
        except Exception as e:
            ToastNotification.show_toast(
                "Erreur Inattendue",
                f"Une erreur est survenue : {e}",
                parent=self
            )


# La fonction show_auth_dialogs doit être accessible ici.
# Déplaçons-la en dehors de if __name__ == "__main__" ou passons-la.
# Pour simplifier, nous la définissons au niveau global du script.
def show_auth_dialogs():
    current_dialog = "login"
    while True:
        if current_dialog == "login":
            result, login_dialog_instance = LoginDialog.launch(parent=None)
            if (
                hasattr(login_dialog_instance, "intended_action")
                and login_dialog_instance.intended_action == "switch_to_signup"
            ):
                current_dialog = "signup"
                continue
            elif result == QDialog.Accepted:
                return True
            else:
                return False
        elif current_dialog == "signup":
            signup_dialog_instance = SignupDialog(parent=None)
            result = signup_dialog_instance.exec()
            if hasattr(signup_dialog_instance, "intended_action"):
                if signup_dialog_instance.intended_action == "switch_to_login":
                    current_dialog = "login"
                    continue
                elif signup_dialog_instance.intended_action == "signup_success":
                    current_dialog = "login"
                    continue
            if result == QDialog.Rejected:
                return False
            current_dialog = "login"
            continue


if __name__ == "__main__":
    # Pour permettre un redémarrage après déconnexion, nous encapsulons la logique de l'application
    # dans une boucle.

    app = QApplication.instance()  # Récupère l'instance existante
    if app is None:  # Crée une nouvelle instance si aucune n'existe
        app = QApplication(sys.argv)

    while True:  # Boucle de vie de l'application
        print(
            "--- Débogage QSettings pour AssistantIA/PhaseWizard (Début de boucle) ---"
        )
        settings = QSettings("AssistantIA", "PhaseWizard")
        # ... (le reste du code de débogage QSettings peut rester ici si besoin) ...

        jwt_token = settings.value("jwt_token", None)  # Vérifier jwt_token
        auth_success = False

        if not jwt_token:  # Vérifier jwt_token
            # Ici, on pourrait ajouter une validation du token (signature, expiration)
            # Pour l'instant, on vérifie juste sa présence.
            # try:
            #     secret_key = "votre-cle-secrete-super-difficile-a-deviner" # Doit être la même que dans LoginDialog
            #     payload = jwt.decode(jwt_token, secret_key, algorithms=["HS256"])
            #     # Le token est valide, on pourrait vérifier l'expiration ici aussi si PyJWT ne le fait pas par défaut
            #     user_name = payload.get("username", "Utilisateur")
            #     user_id = payload.get("user_id", "N/A")
            #     print(f"Utilisateur '{user_name}' (ID: {user_id}) authentifié via JWT. Lancement de l'application.")
            #     auth_success = True
            # except jwt.ExpiredSignatureError:
            #     print("Token JWT expiré. Reconnexion nécessaire.")
            #     settings.remove("jwt_token") # Supprimer le token expiré
            #     settings.remove("current_user_name")
            #     # auth_success reste False
            # except jwt.InvalidTokenError:
            #     print("Token JWT invalide. Reconnexion nécessaire.")
            #     settings.remove("jwt_token")
            #     settings.remove("current_user_name")
            #     # auth_success reste False

            # Logique simplifiée pour l'instant : si pas de token, on affiche les dialogues.
            if show_auth_dialogs():
                auth_success = True
            else:
                # L'authentification a échoué ou a été annulée, quitter l'application
                # sys.exit(0) # Ne pas utiliser sys.exit dans une boucle, utiliser break
                break
        else:  # Un token JWT existe
            # Pour l'instant, on suppose que sa présence signifie une session valide.
            # La validation (comme commentée ci-dessus) serait à faire ici.
            user_name = settings.value(
                "current_user_name", "Utilisateur"
            )  # On garde current_user_name pour affichage rapide
            print(f"Session JWT active pour '{user_name}'. Lancement de l'application.")
            auth_success = True

        if auth_success:
            window = MainWindow()
            window.menu.update_logout_button_visibility(
                True
            )  # Afficher le bouton si connecté
            window.show()

            exit_code = app.exec()  # Exécute la boucle d'événements Qt

            # Si app.exec() se termine (par exemple, après self.close() dans handle_logout),
            # la boucle while reprendra. Vérifions si c'est une déconnexion.
            # Si jwt_token a été effacé, c'est une déconnexion, on recommence la boucle.
            # Sinon (fermeture normale de la fenêtre), on sort de la boucle.
            if not settings.value("jwt_token", None):  # Déconnexion via jwt_token
                print("Déconnexion détectée, redémarrage du cycle d'authentification.")
                # La fenêtre est déjà fermée, la boucle va naturellement recommencer.
                # Il faut s'assurer que `window` est détruite pour éviter les problèmes.
                del window
                continue
            else:  # Fermeture normale
                print("Fermeture normale de l'application.")
                break
        else:  # Si auth_success est False dès le départ (ne devrait pas arriver avec la logique actuelle)
            break

    sys.exit(0)  # Quitter proprement l'application


# La fonction show_auth_dialogs doit être accessible ici.
# Déplaçons-la en dehors de if __name__ == "__main__" ou passons-la.
# Pour simplifier, nous la définissons au niveau global du script.
def show_auth_dialogs():
    current_dialog = "login"
    while True:
        if current_dialog == "login":
            result, login_dialog_instance = LoginDialog.launch(parent=None)
            if (
                hasattr(login_dialog_instance, "intended_action")
                and login_dialog_instance.intended_action == "switch_to_signup"
            ):
                current_dialog = "signup"
                continue
            elif result == QDialog.Accepted:
                return True
            else:
                return False
        elif current_dialog == "signup":
            signup_dialog_instance = SignupDialog(parent=None)
            result = signup_dialog_instance.exec()
            if hasattr(signup_dialog_instance, "intended_action"):
                if signup_dialog_instance.intended_action == "switch_to_login":
                    current_dialog = "login"
                    continue
                elif signup_dialog_instance.intended_action == "signup_success":
                    current_dialog = "login"
                    continue
            if result == QDialog.Rejected:
                return False
            current_dialog = "login"
            continue
