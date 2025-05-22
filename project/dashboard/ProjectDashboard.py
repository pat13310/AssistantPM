from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, QDateTime, QLocale
import sqlite3

from project.dashboard.CardProject import CardProject
from components.layout.FlowLayout import FlowLayout  # ton layout fluide


class ProjectDashboard(QWidget):
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

        title = QLabel("<h4>📁 Projets récents</h4>")
        title.setStyleSheet("color: #777; font-size: 12pt;margin-bottom: 8px;")
        layout.addWidget(title)

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
        self.cursor.execute("SELECT Nom, Description, Date_Creation, markdown_generated, docs_generated, tree_generated, source_code_generated, tests_generated,deployment_info_generated FROM Project")
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
            card = CardProject(title, desc, created_str, project_states_dummy)
            self.content_layout.addWidget(card)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.display_projects()
