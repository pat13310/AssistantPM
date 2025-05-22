import os
import sqlite3

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, QDateTime, QLocale, Signal, QSize
from PySide6.QtSvgWidgets import QSvgWidget

from project.dashboard.CardProject import CardProject
from components.layout.FlowLayout import FlowLayout  # ton layout fluide
from ui.ui_utils import load_colored_svg
from components.ui.IconWithText import IconWithText


class ProjectDashboard(QWidget):
    # Signal émis lorsqu'un projet est sélectionné, avec l'ID du projet
    project_selected = Signal(int)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ProjectDashboard")
        self.setStyleSheet("""
            #ProjectDashboard {
                background-color: #f0f0f0;
                color: #333;
                padding: 0px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(0)

        # Utiliser le composant IconWithText pour le titre
        title_component = IconWithText(
            text="<h4>Projets récents</h4>",
            icon_name="boxes",
            color="#03b541",  # Couleur verte
            font_size=14,
            icon_size=24
        )
        
        # Ajouter le composant au layout principal
        layout.addWidget(title_component)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet("""
            QScrollBar:vertical {
                background: #f0f0f0;
                width: 10px;
                margin: 0px 0px 0px 0px;
                border-radius: 2px;
                padding: 0px ;
            }
            QScrollBar:vertical:hover {
                background: #e0e0e0;
            }
            QScrollBar::handle:vertical {
                background: #f0f0f0;
                min-height: 20px;
                border-radius: 4px;
                border: 1px solid #888;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
                min-height: 20px;
                border-radius: 4px;
                border: 1px solid #333;
            }
                        
            QScrollBar::add-line:vertical {
                border: none;
                background: none;
            }

            QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)

        self.content = QWidget()
        self.content.setStyleSheet("margin: 8px;")
        self.content_layout = FlowLayout(self.content, spacing=20)
        self.scroll.setWidget(self.content)

        layout.addWidget(self.scroll)

        # DB
        self.db_connection = sqlite3.connect("projects.db")
        self.cursor = self.db_connection.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                title TEXT,
                description TEXT,
                created TEXT
            )
        """)
        self.db_connection.commit()

        self.projects = []
        self.load_projects()

    def load_projects(self):
        self.cursor.execute("SELECT ID, Nom, Description, Date_Creation, markdown_generated, docs_generated, tree_generated, source_code_generated, tests_generated, deployment_info_generated FROM Project")
        self.projects = self.cursor.fetchall()
        self.display_projects()

    def display_projects(self):
        # Nettoyage du layout Flow
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if not self.projects:
            empty = QLabel("Aucun projet trouvé.")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet("color: #888; font-style: italic;")
            self.content_layout.addWidget(empty)
            return

        locale_fr = QLocale(QLocale.French)
        for i, (
            project_id,
            title, 
            desc, 
            created_raw, 
            markdown_generated,
            docs_generated,
            tree_generated,
            source_code_generated,
            tests_generated,
            deployment_infos_generated
                ) in enumerate(self.projects):
            dt = QDateTime.fromString(created_raw, "yyyy-MM-dd HH:mm:ss")

            created_str = locale_fr.toString(dt, "d MMMM yyyy 'à' HH:mm")

            # Données factices pour les états du projet (à remplacer par les vraies données)
            # Par exemple, 5 phases, avec des états True (complété) ou False (non complété)
            # Pour varier l'affichage, on peut utiliser l'index i
            project_states_dummy = [markdown_generated, docs_generated, tree_generated, source_code_generated, tests_generated, deployment_infos_generated]
            card = CardProject(title, desc, created_str, project_states_dummy, project_id)
            # Connecter le signal project_data_clicked de la carte à notre méthode de navigation
            card.project_data_clicked.connect(self.navigate_to_project_data)
            # Garder aussi l'ancien signal pour la compatibilité
            card.clicked.connect(self.navigate_to_project)
            self.content_layout.addWidget(card)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.display_projects()
        
    def navigate_to_project(self, project_title):
        """Méthode appelée lorsqu'une carte projet est cliquée (ancienne méthode)"""
        print(f"Navigation vers le projet: {project_title}")
        
        # Récupérer l'ID du projet à partir de son titre
        self.cursor.execute("SELECT ID FROM Project WHERE Nom = ?", (project_title,))
        result = self.cursor.fetchone()
        if result:
            project_id = result[0]
            print(f"ID du projet: {project_id}")
            
            # Émettre un signal pour indiquer qu'un projet a été sélectionné
            # Ce signal sera capturé par la fenêtre principale pour changer de vue
            self.project_selected.emit(project_id)
            
    def navigate_to_project_data(self, project_data):
        """Nouvelle méthode appelée lorsqu'une carte projet est cliquée avec toutes les données"""
        print(f"Navigation vers le projet: {project_data.title} (ID: {project_data.id})")
        
        # Émettre un signal pour indiquer qu'un projet a été sélectionné
        # Ce signal sera capturé par la fenêtre principale pour changer de vue
        if project_data.id:
            self.project_selected.emit(project_data.id)
            
            # Pour l'instant, nous allons simplement afficher un message
            # Vous devrez implémenter la navigation réelle en fonction de votre architecture d'application
