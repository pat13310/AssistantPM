# project/structure/app.py
import sys
import os

# Ajout du chemin racine au PYTHONPATH pour les imports relatifs
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, root_path)

from PySide6.QtWidgets import QApplication

# Import local après avoir ajusté le chemin
from project.structure.ui_agent_ia import ChatArboWidget

def main():
    app = QApplication(sys.argv)
    widget = ChatArboWidget()
    widget.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()