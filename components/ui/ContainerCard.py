from PySide6.QtWidgets import QWidget, QVBoxLayout, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, Signal, QEvent
from PySide6.QtGui import QColor, QEnterEvent

class ContainerCard(QWidget):
    """
    Cadre visuel qui englobe une carte entière.
    - Fond léger, contour arrondi, ombre douce.
    - Émet un signal clicked lorsqu'il est cliqué.
    """
    
    clicked = Signal()  # Signal émis lors du clic
    
    def __init__(self, child=None, parent=None):
        super().__init__(parent)
        
        self.hovered = False
        self.setObjectName("containerCard")
        
        # Configuration du widget
        self.setMinimumHeight(120)
        self.setMinimumWidth(200)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Créer le layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(18, 18, 18, 18)  # Marge interne confortable
        self.layout.setSpacing(10)
        
        # Ajouter l'enfant s'il est fourni
        if child:
            self.layout.addWidget(child)
        
        # Style du cadre (personnalisable)
        self.setStyleSheet("""
            #containerCard {
                background: #f3f6fb;
                border-radius: 16px;
                border: 2px solid #bae6fd;
            }
        """)
        
        # Ombre externe douce
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(16)
        shadow.setColor(QColor(0, 0, 0, 32))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
    
    # Surcharger les événements directement plutôt que d'utiliser un filtre
    def enterEvent(self, event):
        """Géré lorsque la souris entre dans le widget"""
        self._handle_hover(True)
        return super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Géré lorsque la souris quitte le widget"""
        self._handle_hover(False)
        return super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        """Géré lorsque l'utilisateur clique sur le widget"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._handle_press()
        return super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Géré lorsque l'utilisateur relâche le bouton de la souris"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._handle_release()
            # Émettre le signal clicked
            self.clicked.emit()
        return super().mouseReleaseEvent(event)
    
    def _handle_hover(self, hovered):
        """Gère l'effet de survol"""
        self.hovered = hovered
        if hovered:
            self.setStyleSheet("""
                #containerCard {
                    background: #e9f5ff;
                    border-radius: 16px;
                    border: 2px solid #7dd3fc;
                }
            """)
        else:
            self.setStyleSheet("""
                #containerCard {
                    background: #f3f6fb;
                    border-radius: 16px;
                    border: 2px solid #bae6fd;
                }
            """)
    
    def _handle_press(self):
        """Gère l'effet d'appui"""
        self.setStyleSheet("""
            #containerCard {
                background: #dbeafe;
                border-radius: 16px;
                border: 2px solid #38bdf8;
            }
        """)
    
    def _handle_release(self):
        """Gère l'effet de relâchement"""
        if self.hovered:
            self._handle_hover(True)
        else:
            self._handle_hover(False)
    
    def addWidget(self, widget):
        """Ajoute un widget au conteneur"""
        self.layout.addWidget(widget)
