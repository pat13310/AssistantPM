import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QGraphicsDropShadowEffect
from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QFont, QColor, QEnterEvent
from PySide6.QtSvgWidgets import QSvgWidget

from ui.ui_utils import load_colored_svg

class DocumentCard(QWidget):
    """
    Carte de document : icône, titre, description.
    Avec effets de survol et signal de clic.
    """
    # Signal émis lors du clic sur la carte
    clicked = Signal(str)
    
    def __init__(self, title: str, description: str, icon_name: str, is_completed=False, parent=None):
        super().__init__(parent)
        self.title = title
        self.description = description
        self.icon_name = icon_name
        self.is_completed = is_completed  # Indique si le document est déjà fait
        self.is_busy = False  # Indique si le document est en cours de traitement
        
        # Configuration de base du widget
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setMouseTracking(True)
        self.setMinimumSize(300, 100)
        self.setMaximumHeight(150)
        
        # Ombre douce
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(15)
        self.shadow.setOffset(0, 2)
        self.shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(self.shadow)
        
        # Initialiser le layout
        self._setup_layout()
        
        # Appliquer le style initial
        self.update_style(False)

    def _setup_layout(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(8)

        # En-tête : icône + titre
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        # Icône SVG colorée
        try:
            # Chemin vers le fichier SVG
            base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets", "icons"))
            icon_file_path = os.path.join(base_path, f"{self.icon_name}.svg")
            
            if os.path.exists(icon_file_path):
                svg_data = load_colored_svg(icon_file_path, "#03b541")  # Couleur verte
                icon_widget = QSvgWidget()
                icon_widget.load(svg_data)
                icon_widget.setStyleSheet("border: none;")

                icon_widget.setFixedSize(20, 20)
            else:
                print(f"Icône non trouvée: {icon_file_path}")
                icon_widget = QLabel("?")
                icon_widget.setStyleSheet("color: #03b541; font-weight: bold; border: none;")
        except Exception as e:
            print(f"Erreur lors du chargement de l'icône {self.icon_name}: {e}")
            icon_widget = QLabel("?")
            icon_widget.setStyleSheet("color: #03b541; font-weight: bold;")
            
        header_layout.addWidget(icon_widget)

        # Titre
        self.title_label = QLabel(self.title)
        self.title_label.setFont(QFont("Segoe UI", 13, QFont.Bold))
        self.title_label.setStyleSheet("color: #374151; border: none;")  # Titre en gris foncé
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Description
        self.desc_label = QLabel(self.description)
        self.desc_label.setFont(QFont("Segoe UI", 11))
        self.desc_label.setStyleSheet("color: #4b5563; border: none;")
        self.desc_label.setWordWrap(True)
        layout.addWidget(self.desc_label)
        
        # Indicateur de statut en bas
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(0, 5, 0, 0)
        status_layout.setSpacing(5)
        
        # Icône de statut (check ou clock)
        try:
            # Chemin vers le fichier SVG
            base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets", "icons"))
            
            # Choisir l'icône en fonction du statut
            if self.is_busy:
                status_icon = "loader.svg"  # Icône de chargement
                status_color = "#3b82f6"  # Bleu pour indiquer le traitement
            else:
                status_icon = "check.svg" if self.is_completed else "clock-9.svg"
                status_color = "#03b541" if self.is_completed else "#9ca3af"  # Vert si fait, gris sinon
            
            icon_file_path = os.path.join(base_path, status_icon)
            
            if os.path.exists(icon_file_path):
                svg_data = load_colored_svg(icon_file_path, status_color)
                status_icon_widget = QSvgWidget()
                status_icon_widget.load(svg_data)
                status_icon_widget.setFixedSize(16, 16)
                status_icon_widget.setStyleSheet("border: none;")
                status_layout.addWidget(status_icon_widget)
            else:
                print(f"Icône de statut non trouvée: {icon_file_path}")
        except Exception as e:
            print(f"Erreur lors du chargement de l'icône de statut: {e}")
        
        # Texte de statut
        if self.is_busy:
            status_text = "En cours de traitement..."
        else:
            status_text = "Document complété" if self.is_completed else "En attente"
        
        self.status_label = QLabel(status_text)
        self.status_label.setFont(QFont("Segoe UI", 10))
        self.status_label.setStyleSheet(f"color: {status_color}; border: none;")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        layout.addLayout(status_layout)
        
        # Stocker les références pour pouvoir les mettre à jour
        self.status_layout = status_layout
        self.status_color = status_color
        
        # Espace extensible en bas
        layout.addStretch()
        
    def update_style(self, hover: bool):
        """Met à jour le style de la carte en fonction de l'état de survol"""
        if hover:
            # Style au survol
            bg_color = "#f0fdf4"  # Vert très clair
            border_color = "#86efac"  # Vert clair
            self.shadow.setBlurRadius(24)
            self.shadow.setOffset(0, 4)
        else:
            # Style normal
            bg_color = "white"
            border_color = "#e5e7eb"  # Gris clair
            self.shadow.setBlurRadius(15)
            self.shadow.setOffset(0, 2)
            
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                border-radius: 12px;
                border: 2px solid {border_color};
            }}
        """)
        self.setCursor(Qt.PointingHandCursor)
    
    def enterEvent(self, event: QEnterEvent):
        """Géré lorsque la souris entre dans le widget"""
        self.update_style(True)
        return super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Géré lorsque la souris quitte le widget"""
        self.update_style(False)
        return super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        """Géré lorsque l'utilisateur clique sur le widget"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Style au clic
            self.setStyleSheet("""
                QWidget {
                    background-color: #dcfce7;
                    border-radius: 12px;
                    border: 2px solid #22c55e;
                }
            """)
            
            # Émettre le signal clicked avec le titre du document
            self.clicked.emit(self.title)
            
        return super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Géré lorsque l'utilisateur relâche le bouton de la souris"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Restaurer le style de survol
            self.update_style(True)
        return super().mouseReleaseEvent(event)
    
    def setBusy(self, busy: bool):
        """Définit si le document est en cours de traitement
        
        Args:
            busy (bool): True si le document est en cours de traitement, False sinon
        """
        if self.is_busy == busy:
            return  # Rien à faire si l'état n'a pas changé
            
        self.is_busy = busy
        
        try:
            # Mettre à jour l'icône de statut
            base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets", "icons"))
            
            # Choisir l'icône et la couleur en fonction du statut
            if busy:
                status_icon = "loader.svg"
                status_color = "#3b82f6"  # Bleu pour indiquer le traitement
                status_text = "En cours de traitement..."
            else:
                status_icon = "check.svg" if self.is_completed else "clock-9.svg"
                status_color = "#03b541" if self.is_completed else "#9ca3af"
                status_text = "Document complété" if self.is_completed else "En attente"
            
            # Mettre à jour le texte de statut
            self.status_label.setText(status_text)
            self.status_label.setStyleSheet(f"color: {status_color}; border: none;")
            
            # Mettre à jour l'icône si elle existe
            icon_file_path = os.path.join(base_path, status_icon)
            if os.path.exists(icon_file_path):
                # Supprimer l'ancienne icône
                for i in range(self.status_layout.count()):
                    item = self.status_layout.itemAt(i)
                    if item and item.widget() and isinstance(item.widget(), QSvgWidget):
                        item.widget().deleteLater()
                        break
                
                # Ajouter la nouvelle icône
                svg_data = load_colored_svg(icon_file_path, status_color)
                status_icon_widget = QSvgWidget()
                status_icon_widget.load(svg_data)
                status_icon_widget.setFixedSize(16, 16)
                status_icon_widget.setStyleSheet("border: none;")
                self.status_layout.insertWidget(0, status_icon_widget)
        except Exception as e:
            print(f"Erreur lors de la mise à jour de l'icône de statut: {e}")
