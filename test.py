import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from components.wizard.PhaseWizardWidget import PhaseWizardWidget
from components.infos.models import ProjectData, Phase, Question

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test PhaseWizardWidget")
        self.setGeometry(100, 100, 800, 600)

        phases = []
        phases.append(Phase(id="analyse", title="Analyse des Besoins", description="", icon="assets/icons/search.svg", color="#FF0000", questions=[Question(id="q1", text="Question 1", suggestions=[], bestPractices="")]))
        phases.append(Phase(id="conception", title="Conception", description="", icon="assets/icons/pen-tool.svg", color="#00FF00", questions=[Question(id="q2", text="Question 2", suggestions=[], bestPractices="")]))
        project_data = ProjectData(name="Mon Projet", phases=phases)

        self.phase_wizard = PhaseWizardWidget(project_data)

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.phase_wizard)

        self.setCentralWidget(central_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
