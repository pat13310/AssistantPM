from PySide6.QtWidgets import (
    QVBoxLayout,
    QTextEdit,
    QDialog,
    QDialogButtonBox,
)




class PromptEditorDialog(QDialog):
    def __init__(self, parent=None, current_prompt=""):
        super().__init__(parent)
        self.setWindowTitle("Éditeur de Prompt")
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(self)
        
        # Éditeur de texte
        self.editor = QTextEdit()
        self.editor.setPlainText(current_prompt)
        layout.addWidget(self.editor)
        
        # Boutons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_prompt(self):
        return self.editor.toPlainText()

