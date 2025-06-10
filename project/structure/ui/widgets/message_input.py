# project/structure/ui/widgets/message_input_field.py
from PySide6.QtWidgets import QPlainTextEdit
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPalette

class MessageInputField(QPlainTextEdit):
    enterPressed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Votre message...")
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.setFixedHeight(40)
        # Utiliser setStyleSheet pour appliquer un style spécifique à cette instance
        # avec !important pour s'assurer qu'il ne sera pas écrasé par le style global
        # Forcer le style directement sur l'instance
        self.setStyleSheet("""
            * { /* S'applique à ce widget et tous ses enfants */
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                padding: 8px;
                color: black !important; /* Utiliser !important avec priorité maximale */
                background-color: white !important;
                font-weight: bold; 
                font-size: 12pt;
                selection-background-color: #4CAF50 !important;
                selection-color: white !important;
            }
        """)
        
        # S'assurer que le style est appliqué en modifiant directement la palette de couleurs
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Text, Qt.black)
        palette.setColor(QPalette.ColorRole.Base, Qt.white)
        self.setPalette(palette)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return and not event.modifiers() & Qt.ShiftModifier:
            self.enterPressed.emit()
            event.accept()  # Prevent the default newline insertion
        else:
            super().keyPressEvent(event)