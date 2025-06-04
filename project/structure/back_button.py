from PySide6.QtWidgets import QPushButton


class BackButton(QPushButton):
    """Bouton de retour réutilisable avec un style cohérent"""
    
    def __init__(self, text="« Retour", parent=None):
        super().__init__(text, parent)
        self.apply_style()
    
    def apply_style(self):
        """Applique le style par défaut au bouton"""
        self.setStyleSheet(
            """
            QPushButton {
                background-color: #444444;
                color: white;
                border: 1px solid #CCCCCC;
                border-radius: 8px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #555555;
            }
            QPushButton:pressed {
                background-color: #333333;
            }
            """
        )
