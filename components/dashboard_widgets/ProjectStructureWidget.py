from PySide6.QtWidgets import QWidget, QVBoxLayout, QTreeView, QLabel
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt

class ProjectStructureWidget(QWidget):
    def __init__(self, project_name="Mon Projet", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Structure du Projet")

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title_label = QLabel(f"Arborescence du Projet: {project_name}")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(title_label)

        self.tree_view = QTreeView()
        self.tree_view.setHeaderHidden(True) # Cache l'en-tête des colonnes
        self.tree_view.setStyleSheet("""
            QTreeView {
                border: 1px solid #d1d5db;
                border-radius: 8px;
                padding: 5px;
            }
            QTreeView::item {
                padding: 4px;
            }
            QTreeView::item:hover {
                background-color: #e5f9c7; /* Vert clair au survol */
            }
            QTreeView::item:selected {
                background-color: #4CAF50; /* Vert pour la sélection */
                color: white;
            }
        """)
        
        self.model = QStandardItemModel()
        self.tree_view.setModel(self.model)

        self.populate_model(project_name)

        main_layout.addWidget(self.tree_view)
        self.setLayout(main_layout)

    def populate_model(self, project_name):
        self.model.clear() # Efface le modèle existant

        root_item = QStandardItem(project_name)
        root_item.setEditable(False)
        # Pourrait ajouter une icône de dossier ici
        # from PySide6.QtGui import QIcon
        # root_item.setIcon(QIcon("path/to/folder_icon.png"))
        self.model.appendRow(root_item)

        # Structure de base des dossiers par phase
        base_folders = [
            "01_Analyse_Besoins",
            "02_Conception",
            "03_Developpement",
            "04_Tests",
            "05_Deploiement",
            "Documentation_Generale" # Dossier supplémentaire pour la documentation
        ]

        for folder_name in base_folders:
            folder_item = QStandardItem(folder_name)
            folder_item.setEditable(False)
            # folder_item.setIcon(QIcon("path/to/folder_icon.png"))
            root_item.appendRow(folder_item)

            # Exemple d'ajout de sous-dossiers ou fichiers (à adapter)
            if folder_name == "03_Developpement":
                src_item = QStandardItem("src")
                # src_item.setIcon(QIcon("path/to/folder_icon.png"))
                folder_item.appendRow(src_item)
                main_py_item = QStandardItem("main.py")
                # main_py_item.setIcon(QIcon("path/to/file_icon.png"))
                src_item.appendRow(main_py_item)

        self.tree_view.expandAll() # Ouvre tous les nœuds par défaut

    def update_project_name(self, new_project_name):
        """ Met à jour le nom du projet et rafraîchit l'arborescence. """
        self.setWindowTitle(f"Structure du Projet: {new_project_name}")
        title_label = self.findChild(QLabel)
        if title_label:
            title_label.setText(f"Arborescence du Projet: {new_project_name}")
        self.populate_model(new_project_name)


if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = ProjectStructureWidget("Exemple de Projet")
    window.resize(400, 500)
    window.show()
    sys.exit(app.exec())
