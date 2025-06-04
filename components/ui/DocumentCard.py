from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPalette
from components.ui.IconWithText import IconWithText

class DocumentCard(QWidget):
    """
    Carte représentant un type de document.
    Contient un titre, une description et une icône.
    """
    
    clicked = Signal()  # Signal émis lors du clic
    
    def __init__(self, title="", description="", icon_name="file-text", parent=None):
        super().__init__(parent)
        
        self.setObjectName("documentCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(8)
        
        # Layout horizontal pour l'icône et le contenu
        content_layout = QHBoxLayout()
        content_layout.setSpacing(12)
        
        # Icône
        self.icon_widget = IconWithText(icon_name=icon_name, text="")
        self.icon_widget.setFixedSize(40, 40)
        content_layout.addWidget(self.icon_widget, 0, Qt.AlignmentFlag.AlignTop)
        
        # Layout vertical pour le texte
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)
        
        # Titre
        self.title_label = QLabel(title)
        self.title_label.setObjectName("documentCardTitle")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setWordWrap(True)
        text_layout.addWidget(self.title_label)
        
        # Description
        self.description_label = QLabel(description)
        self.description_label.setObjectName("documentCardDescription")
        desc_font = QFont()
        desc_font.setPointSize(10)
        self.description_label.setFont(desc_font)
        self.description_label.setWordWrap(True)
        self.description_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        text_layout.addWidget(self.description_label)
        
        content_layout.addLayout(text_layout, 1)
        main_layout.addLayout(content_layout)
        
        # Style CSS
        self.setStyleSheet("""
            #documentCard {
                background: transparent;
            }
            #documentCardTitle {
                color: #1f2937;
            }
            #documentCardDescription {
                color: #6b7280;
            }
        """)
    
    def mousePressEvent(self, event):
        """Gère le clic sur la carte"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)
    
    def setTitle(self, title):
        """Définit le titre de la carte"""
        self.title_label.setText(title)
    
    def setDescription(self, description):
        """Définit la description de la carte"""
        self.description_label.setText(description)
    
    def setIcon(self, icon_name):
        """Définit l'icône de la carte"""
        self.icon_widget.setIcon(icon_name)
