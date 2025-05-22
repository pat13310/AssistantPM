# project/views/EditProjectView.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QSizePolicy, QLabel
from PySide6.QtCore import Qt
from components.PhaseBar.HorizontalPhaseBar import HorizontalPhaseBar
from components.wizard.PhaseWizardWidget import PhaseWizardWidget
from components.infos.models import ProjectData  # doit être une instance complète
from components.Step.PhaseStepBar import PhaseStepBar  # Import PhaseStepBar
import sqlite3

class EditProjectForm(QWidget):
    def __init__(self, project_data: ProjectData, parent=None):
        super().__init__(parent)

        self.setStyleSheet("background-color: #f9fafb;")
        self.project_data = project_data
        self.current_project_id = None

        main_layout = QVBoxLayout(self)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(5)
        
        # Titre du projet
        self.project_title = QLabel("Édition du projet")
        self.project_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333; margin-bottom: 10px;")
        self.project_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.project_title)
        
        # Frise des phases
        self.phase_bar = HorizontalPhaseBar()
        layout.addWidget(self.phase_bar)

        # Assistant de réponse
        self.wizard = PhaseWizardWidget(project_data)
        layout.addWidget(self.wizard)

        scroll_content.setLayout(layout)
        self.scroll_area.setWidget(scroll_content)
        main_layout.addWidget(self.scroll_area)
        self.setLayout(main_layout)
        
    def load_project(self, project_id: int):
        """Charge les données d'un projet spécifique"""
        self.current_project_id = project_id
        
        # Récupérer les données du projet depuis la base de données
        conn = None
        try:
            conn = sqlite3.connect("projects.db")
            cursor = conn.cursor()
            
            # Récupérer les informations de base du projet
            cursor.execute(
                "SELECT Nom, Description, markdown_generated, docs_generated, tree_generated, "
                "source_code_generated, tests_generated, deployment_info_generated "
                "FROM Project WHERE Id = ?",
                (project_id,)
            )
            project_info = cursor.fetchone()
            
            if project_info:
                project_name, project_description, *project_states = project_info
                
                # Mettre à jour le titre du projet
                self.project_title.setText(f"Édition du projet: {project_name}")
                
                # Mettre à jour les données du projet
                self.project_data.name = project_name
                
                # Mettre à jour la frise des phases en fonction des états du projet
                # Si votre HorizontalPhaseBar a une méthode pour mettre à jour les états
                # Vous pouvez l'appeler ici
                # self.phase_bar.update_states(project_states)
                
                # Mettre à jour les données du projet dans le wizard
                # Comme il n'y a pas de méthode update_project_data, nous allons mettre à jour
                # directement l'attribut project du wizard
                self.wizard.project = self.project_data
                
                # Recharger la question actuelle pour mettre à jour l'interface
                self.wizard.load_question()
                
                print(f"Projet chargé: {project_name} (ID: {project_id})")
            else:
                print(f"Erreur: Projet avec ID {project_id} non trouvé")
                
        except sqlite3.Error as e:
            print(f"Erreur lors du chargement du projet: {e}")
        finally:
            if conn:
                conn.close()
