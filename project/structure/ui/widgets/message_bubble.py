#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module pour le composant MessageBubble - Bulle de message générique
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QSizePolicy
)
from PySide6.QtCore import Qt, QSize, QTimer, QPropertyAnimation, QEasingCurve, Property, QRect
from PySide6.QtSvgWidgets import QSvgWidget

class MessageBubble(QWidget):
    """
    Widget de bulle de message avec icône et texte formaté
    """
    
    def __init__(
        self,
        message,
        word_wrap=True,
        icon_name=None,
        icon_color=None,
        icon_size=20,
        user=False,
        animate_entry=True,
        temporary=False,
        timeout=2000,
        parent=None
    ):
        """
        Initialise une bulle de message
        
        Args:
            message (str): Message à afficher
            word_wrap (bool): Activer le retour à la ligne automatique
            icon_name (str, optional): Nom de l'icône SVG à utiliser. Si None, utilise 'user' pour les messages utilisateur et 'robot' pour les messages IA.
            icon_color (str): Couleur de l'icône (format CSS)
            icon_size (int): Taille de l'icône en pixels
            user (bool): True si c'est un message utilisateur, False si c'est un message IA
            animate_entry (bool): Activer l'animation d'entrée
            temporary (bool): Si True, le message disparaîtra automatiquement après un délai
            timeout (int): Délai en millisecondes avant la disparition du message temporaire (défaut: 2000ms)
            parent (QWidget): Widget parent
        """
        super().__init__(parent)
        
        # Stocker les paramètres
        self.temporary = temporary
        self.timeout = timeout
        
        # Layout principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 10)
        
        # Aligner la bulle à gauche ou à droite selon le type de message
        h_layout = QHBoxLayout()
        h_layout.setContentsMargins(0, 0, 0, 0)
        
        # Créer un widget pour contenir la bulle
        self.bubble = QFrame()
        self.bubble.setObjectName("message_bubble")
        
        # Style différent selon le type de message (utilisateur ou IA)
        if user:
            # Message utilisateur : bulle verte avec angle droit en bas à droite
            self.bubble.setStyleSheet(
                """
                QFrame#message_bubble {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #E8F5E9, stop:1 #C8E6C9);
                    border-radius: 15px;
                    border-bottom-right-radius: 0px;
                    padding: 10px;
                }
                """
            )
        else:
            # Message IA : bulle bleue avec angle droit en bas à gauche
            self.bubble.setStyleSheet(
                """
                QFrame#message_bubble {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #E3F2FD, stop:1 #BBDEFB);
                    border-radius: 15px;
                    border-bottom-left-radius: 0px;
                    padding: 10px;
                }
                """
            )
        
        # Layout pour la bulle
        bubble_layout = QHBoxLayout(self.bubble)
        bubble_layout.setContentsMargins(10, 8, 10, 8)
        
        # Déterminer l'icône à utiliser
        if icon_name is None:
            # Si aucune icône spécifiée, utiliser 'user' pour les messages utilisateur et 'robot' pour les messages IA
            icon_name = "user" if user else "bot"

        if icon_color is None:    
            # Couleur par défaut
            icon_color = "#1B5E20" if user else "#2196F3"
            
        # Icône SVG vectorielle
        svg_widget = self._get_svg_icon(icon_name, size=icon_size, color=icon_color)
        if svg_widget:
            bubble_layout.addWidget(svg_widget)
        else:
            # Fallback si l'icône n'est pas trouvée
            icon_label = QLabel()
            icon_label.setFixedSize(icon_size, icon_size)
            bubble_layout.addWidget(icon_label)
            
        # Texte
        self.label = QLabel(message)
        
        # Style différent selon le type de message
        if user:
            self.label.setStyleSheet(
                """
                color: #1B5E20; 
                font-size: 12px;
                background: transparent;
                margin-left: 10px;
                """
            )
        else:
            self.label.setStyleSheet(
                """
                color: #0D47A1; 
                font-size: 12px;
                background: transparent;
                margin-left: 10px;
                """
            )
        if not word_wrap:
            self.label.setStyleSheet(self.label.styleSheet() + "white-space: nowrap;")
        else:
            self.label.setWordWrap(True)
            self.label.setMinimumWidth(300)
            self.label.setMaximumWidth(400)  # Limiter la largeur pour éviter les lignes trop longues
        
        bubble_layout.addWidget(self.label)
        
        # Aligner la bulle à droite pour les messages utilisateur, à gauche pour les messages IA
        if user:
            h_layout.addStretch(1)  # Cela pousse la bulle vers la droite
            h_layout.addWidget(self.bubble)
        else:
            h_layout.addWidget(self.bubble)
            h_layout.addStretch(1)  # Cela pousse la bulle vers la gauche
        
        self.main_layout.addLayout(h_layout)
        
        # Animation d'entrée si activée
        if animate_entry:
            self._animate_entry(user)
        else:
            # Sinon, afficher directement à la taille normale
            self.setMaximumHeight(16777215)  # Valeur maximale pour Qt
            
        # Si c'est un message temporaire, configurer le timer pour le faire disparaître
        if self.temporary:
            self.fade_out_timer = QTimer(self)
            self.fade_out_timer.setSingleShot(True)
            self.fade_out_timer.timeout.connect(self.fade_out)
            self.fade_out_timer.start(self.timeout)
    
    def typing_animation(self, duration=1500):
        """Affiche une animation de 'typing' (trois points qui apparaissent)
        
        Args:
            duration (int, optional): Durée de l'animation en ms. Par défaut 1500ms.
        """
        # Sauvegarder le message original
        self.original_message = self.label.text()
        
        # Créer un timer pour l'animation
        self.typing_timer = QTimer(self)
        self.typing_dots = 0
        
        # Fonction de mise à jour des points
        def update_dots():
            self.typing_dots = (self.typing_dots + 1) % 4
            dots = "." * self.typing_dots
            self.label.setText(f"En train d'écrire{dots}")
        
        # Connecter le timer à la fonction de mise à jour
        self.typing_timer.timeout.connect(update_dots)
        self.typing_timer.start(300)  # Mise à jour toutes les 300ms
        
        # Arrêter l'animation après la durée spécifiée
        QTimer.singleShot(duration, self.stop_typing_animation)
    
    def stop_typing_animation(self):
        """Arrête l'animation de typing et restaure le message original"""
        if hasattr(self, 'typing_timer') and self.typing_timer.isActive():
            self.typing_timer.stop()
            # Restaurer le message original avec animation
            if hasattr(self, 'original_message'):
                self.update_message(self.original_message)
    
    def _get_svg_icon(self, icon_name, size=20, color="#2196F3"):
        """Charge une icône SVG avec la couleur spécifiée
        
        Args:
            icon_name (str): Nom de l'icône SVG (sans extension)
            size (int): Taille de l'icône en pixels
            color (str): Couleur de l'icône au format CSS
            
        Returns:
            QSvgWidget: Widget SVG ou None si l'icône n'est pas trouvée
        """
        import os
        from PySide6.QtSvgWidgets import QSvgWidget
        from PySide6.QtCore import QSize
        
        try:
            # Importer la fonction de chargement d'icône colorée
            try:
                from project.structure.ui.ui_utils import load_colored_svg
            except ImportError:
                # Fallback si le module n'est pas trouvable via l'importation relative
                import sys
                sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))
                from project.structure.ui.ui_utils import load_colored_svg
            
            # Chemin vers la racine du projet
            project_root = os.path.dirname(
                os.path.dirname(
                    os.path.dirname(
                        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    )
                )
            )
            icon_path = os.path.join(
                project_root,
                "assets",
                "icons",
                f"{icon_name}.svg",
            )
            
            if not os.path.exists(icon_path):
                print(f"[Erreur] Fichier SVG introuvable : {icon_path}")
                return None
                
            # Créer un widget SVG
            svg_widget = QSvgWidget()
            
            # Charger le SVG avec la couleur spécifiée si demandé
            svg_data = load_colored_svg(icon_path, color)
            if svg_data.isEmpty():
                print(f"[Erreur] SVG vide ou incorrect : {icon_path}")
                return None
                
            # Charger les données SVG dans le widget
            svg_widget.load(svg_data)
            
            # Définir la taille fixe
            svg_widget.setFixedSize(QSize(size, size))
            
            return svg_widget
        except Exception as e:
            print(f"[Erreur] Impossible de charger l'icône {icon_name}: {str(e)}")
            return None
    
    def update_message(self, new_message, animate=True):
        """Met à jour le texte du message avec une animation optionnelle
        
        Args:
            new_message (str): Nouveau texte du message
            animate (bool, optional): Activer l'animation. Par défaut True.
        """
        if not animate:
            # Mise à jour simple sans animation
            self.label.setText(new_message)
            return
        
        # Utiliser un timer pour simuler une animation simple
        # Cela évite les problèmes avec QPropertyAnimation
        self.old_text = self.label.text()
        self.new_text = new_message
        
        # Masquer temporairement le texte
        self.label.setStyleSheet(self.label.styleSheet() + "color: transparent;")
        
        # Attendre un court instant puis changer le texte
        QTimer.singleShot(150, self._change_text)
    
    def _change_text(self):
        """Change le texte et le fait réapparaître"""
        # Changer le texte pendant qu'il est invisible
        self.label.setText(self.new_text)
        
        # Restaurer le style original (avec la couleur)
        style = self.label.styleSheet().replace("color: transparent;", "")
        self.label.setStyleSheet(style)
        
    def _animate_entry(self, user):
        """Anime l'apparition de la bulle de message
        
        Args:
            user (bool): True si c'est un message utilisateur, False si c'est un message IA
        """
        # Cacher initialement la bulle
        self.bubble.setMaximumHeight(0)
        
        # Créer une animation pour agrandir progressivement la bulle
        self.entry_anim = QPropertyAnimation(self.bubble, b"maximumHeight")
        self.entry_anim.setDuration(300)  # 300ms
        self.entry_anim.setStartValue(0)
        
        # Récupérer la hauteur naturelle de la bulle
        QTimer.singleShot(10, self._start_entry_animation)
    
    def _start_entry_animation(self):
        """Démarre l'animation d'entrée après avoir calculé la hauteur naturelle"""
        # Obtenir la hauteur naturelle
        natural_height = self.bubble.sizeHint().height()
        
        # Configurer l'animation
        self.entry_anim.setEndValue(natural_height)
        self.entry_anim.setEasingCurve(QEasingCurve.OutBack)  # Effet de rebond
        
        # Démarrer l'animation
        self.entry_anim.start()
        
    def fade_out(self):
        """Fait disparaître progressivement le message"""
        # Créer une animation pour faire disparaître le widget
        self.fade_animation = QPropertyAnimation(self, b"maximumHeight")
        self.fade_animation.setDuration(500)  # Durée de l'animation en ms
        self.fade_animation.setStartValue(self.height())
        self.fade_animation.setEndValue(0)
        self.fade_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.fade_animation.finished.connect(self._remove_from_parent)
        self.fade_animation.start()
        
    def _remove_from_parent(self):
        """Supprime le widget du parent après l'animation"""
        if self.parent():
            # Supprimer du layout parent
            self.setParent(None)
            self.deleteLater()
    

    def hide(self):
        """Masque le widget"""
        super().hide()
        self.fade_out()