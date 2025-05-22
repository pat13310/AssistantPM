from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QLabel,
    QDialog,
    QDialogButtonBox,
)
class GitCredentialsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration Git")
        self.setMinimumSize(400, 200)
        
        layout = QVBoxLayout(self)
        
        # Champs pour le dépôt
        repo_layout = QHBoxLayout()
        repo_label = QLabel("URL du dépôt Git:")
        self.repo_input = QLineEdit()
        repo_layout.addWidget(repo_label)
        repo_layout.addWidget(self.repo_input)
        layout.addLayout(repo_layout)
        
        # Champs pour la branche
        branch_layout = QHBoxLayout()
        branch_label = QLabel("Branche:")
        self.branch_input = QLineEdit("main")
        branch_layout.addWidget(branch_label)
        branch_layout.addWidget(self.branch_input)
        layout.addLayout(branch_layout)
        
        # Champs pour le nom d'utilisateur
        username_layout = QHBoxLayout()
        username_label = QLabel("Nom d'utilisateur:")
        self.username_input = QLineEdit()
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        layout.addLayout(username_layout)
        
        # Champs pour le mot de passe/token
        password_layout = QHBoxLayout()
        password_label = QLabel("Token d'accès:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)
        
        # Message d'information
        info_label = QLabel("Note: Pour GitHub, utilisez un token d'accès personnel au lieu d'un mot de passe.")
        info_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(info_label)
        
        # Boutons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_credentials(self):
        return {
            "repo": self.repo_input.text(),
            "branch": self.branch_input.text(),
            "username": self.username_input.text(),
            "password": self.password_input.text()
        }

