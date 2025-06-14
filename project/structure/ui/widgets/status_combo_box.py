from PySide6.QtWidgets import QWidget, QComboBox, QFrame, QHBoxLayout
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QColor

class StatusComboBox(QWidget):
    """
    Un widget personnalisé qui combine un QComboBox avec un indicateur de statut visuel.
    L'indicateur est une barre verticale colorée à gauche du combo box.
    """
    
    # Signal émis quand la sélection du combo box change
    currentTextChanged = Signal(str)
    currentIndexChanged = Signal(int)
    
    # Couleurs d'état
    STATUS_UNKNOWN = "#888888"  # Gris
    STATUS_OK = "#4CAF50"       # Vert
    STATUS_ERROR = "#F44336"    # Rouge
    
    def __init__(self, parent=None):
        """Initialisation du widget personnalisé"""
        super().__init__(parent)
        
        # Layout principal
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setContentsMargins(0, 0, 0, 0)
        
        # Indicateur de statut (barre verticale)
        self.status_indicator = QFrame(self)
        self.status_indicator.setFixedWidth(4)
        self.status_indicator.setStyleSheet(f"background-color: {self.STATUS_UNKNOWN};")
        self.layout.addWidget(self.status_indicator)
        
        # Combo box
        self.combo_box = QComboBox(self)
        self.combo_box.setStyleSheet("""
            QComboBox {
                font-weight: normal;
                padding-left: 5px;
                border: 1px solid #444444;
                border-left: none;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #444444;
                background-color: #2a2a2a;
                color: #e0e0e0;
                selection-background-color: #3a3a3a;
                outline: 0px; /* Supprimer le contour de focus */
            }
            QComboBox QAbstractItemView::item {
                border: none;
                padding-left: 5px;
            }
            QComboBox QAbstractItemView::item:selected {
                border: none;
                background-color: #3a3a3a;
            }
            QComboBox QAbstractItemView::item:hover {
                border: none;
                background-color: #333333;
            }
        """)
        
        # Connecter les signaux du combo box aux signaux du widget
        self.combo_box.currentTextChanged.connect(self.currentTextChanged)
        self.combo_box.currentIndexChanged.connect(self.currentIndexChanged)
        
        self.layout.addWidget(self.combo_box)
        
    def addItems(self, items):
        """Ajouter plusieurs éléments au combo box"""
        self.combo_box.addItems(items)
        
    def addItem(self, text, userData=None):
        """Ajouter un élément au combo box"""
        if userData is None:
            self.combo_box.addItem(text)
        else:
            self.combo_box.addItem(text, userData)
    
    def setCurrentIndex(self, index):
        """Définir l'index courant du combo box"""
        self.combo_box.setCurrentIndex(index)
        
    def currentIndex(self):
        """Obtenir l'index courant du combo box"""
        return self.combo_box.currentIndex()
        
    def currentText(self):
        """Obtenir le texte courant du combo box"""
        return self.combo_box.currentText()
    
    def setFixedWidth(self, width):
        """Définir la largeur fixe du combo box"""
        self.combo_box.setFixedWidth(width)
        
    def setFixedHeight(self, height):
        """Définir la hauteur fixe du combo box et de l'indicateur"""
        self.combo_box.setFixedHeight(height)
        self.status_indicator.setFixedHeight(height)
    
    def setStatusOk(self):
        """Définir l'état de l'indicateur à OK (vert)"""
        self.status_indicator.setStyleSheet(f"background-color: {self.STATUS_OK};")
        
    def setStatusError(self):
        """Définir l'état de l'indicateur à ERROR (rouge)"""
        self.status_indicator.setStyleSheet(f"background-color: {self.STATUS_ERROR};")
        
    def setStatusUnknown(self):
        """Définir l'état de l'indicateur à UNKNOWN (gris)"""
        self.status_indicator.setStyleSheet(f"background-color: {self.STATUS_UNKNOWN};")
        
    def setStatus(self, status):
        """
        Définir l'état de l'indicateur avec une valeur personnalisée
        
        Args:
            status: Peut être une chaîne prédéfinie ('ok', 'error', 'unknown') 
                   ou une couleur valide (nom, hex, rgb)
        """
        if status == 'ok':
            self.setStatusOk()
        elif status == 'error':
            self.setStatusError()
        elif status == 'unknown':
            self.setStatusUnknown()
        else:
            # Supposer que c'est une couleur valide
            try:
                self.status_indicator.setStyleSheet(f"background-color: {status};")
            except:
                # En cas d'erreur, revenir à l'état inconnu
                self.setStatusUnknown()
