# main.py
import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from Ui_AssistantPM  import Ui_AssistantPM  # type: ignore # ton fichier généré automatiquement

from components.CollapsibleLabel import CollapsibleLabel
from components.PhaseBar.HorizontalPhaseBar import HorizontalPhaseBar
#from components.PhaseMenu import PhaseMenu  # importe ton composant

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_AssistantPM()
        self.ui.setupUi(self)

        # Remplacement du placeholder par notre widget personnalisé
        sidebar = self.ui.sidebar.layout()
        self.header_menu=CollapsibleLabel()
        self.menu = HorizontalPhaseBar()

        sidebar.addWidget(self.header_menu)
        sidebar.addWidget(self.menu)

        self.setup_connections()

    def setup_connections(self):    
        self.header_menu.toggled.connect(self.toggle_sidebar_width)
        self.ui.label_5.mousePressEvent = self.handle_label_click  # Connect label click event
        
    def toggle_sidebar_width(self, expanded: bool):
        if expanded:            
            self.ui.splitter.setSizes([200, 0])  # largeur sidebar, reste
            self.menu.toggle_text_visibility(expanded)
        else:
            self.ui.splitter.setSizes([1, 0])
            self.menu.toggle_text_visibility(expanded)

        self.ui.sidebar.layout().activate()
        self.ui.sidebar.updateGeometry()
        self.ui.sidebar.adjustSize()

    
    # Exemple de slot
    def handle_label_click(self, event):
        print("Label cliqué")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
