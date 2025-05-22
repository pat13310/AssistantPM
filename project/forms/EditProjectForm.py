# project/views/EditProjectView.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QSizePolicy
from components.PhaseBar.HorizontalPhaseBar import HorizontalPhaseBar
from components.wizard.PhaseWizardWidget import PhaseWizardWidget
from components.infos.models import ProjectData  # doit être une instance complète
from components.Step.PhaseStepBar import PhaseStepBar  # Import PhaseStepBar

class EditProjectForm(QWidget):
    def __init__(self, project_data: ProjectData, parent=None):
        super().__init__(parent)

        self.setStyleSheet("background-color: #f9fafb;")

        main_layout = QVBoxLayout(self)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(5)
        
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
