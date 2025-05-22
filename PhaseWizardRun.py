
import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from components.wizard.PhaseWizardWidget import PhaseWizardWidget
from components.infos.data_phases import initial_phases
from components.infos.models import ProjectData


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #fff;")
        self.setWindowTitle("Assistant IA - Gestion de Projet")
        self.setMinimumSize(900, 600)

        project = ProjectData(name="MonProjet", phases=initial_phases)
        self.wizard = PhaseWizardWidget(project)
        self.wizard.completed.connect(self.on_completed)

        self.setCentralWidget(self.wizard)

    def on_completed(self, project):
        print("✔ Projet complété :", project.name)
        for phase in project.phases:
            print(f"Phase : {phase.title}")
            for q in phase.questions:
                print(f"  - {q.id} : {q.response or '[vide]'}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
