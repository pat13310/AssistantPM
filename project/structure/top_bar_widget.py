from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QSizePolicy,
    QWidget
)
from PySide6.QtCore import Signal, QSize, QThread, QObject, Qt, QTimer, QRectF
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
import os
import sys

# Ajouter le répertoire racine au chemin d'importation pour trouver le module ui
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from ui.ui_utils import load_colored_svg

class ConnectionWorker(QObject):
    """Travailleur pour gérer la connexion au serveur IA en arrière-plan"""
    
    # Signaux pour communiquer avec le thread principal
    connection_result = Signal(bool, str)  # connexion réussie, url_serveur
    finished = Signal()
    progress = Signal(int)  # Signal de progression (0-100)
    
    def __init__(self, server_url=None):
        super().__init__()
        self.server_url = server_url
        self.is_cancelled = False
    
    def check_connection(self):
        """Vérifie la connexion au serveur IA en arrière-plan avec yield pour éviter le blocage"""
        try:
            # Émettre le signal de début de progression
            self.progress.emit(10)
            
            # Utiliser QTimer.singleShot pour céder le contrôle à l'interface utilisateur
            # et éviter de bloquer le thread principal
            from PySide6.QtCore import QEventLoop
            loop = QEventLoop()
            QTimer.singleShot(10, loop.quit)  # Céder le contrôle pendant 10ms
            loop.exec()
            
            self.progress.emit(30)
            
            # Simuler une vérification de connexion en plusieurs étapes
            # pour permettre à l'interface de rester réactive
            import time
            
            # Utiliser des petites pauses au lieu d'une longue pause
            for i in range(5):
                if self.is_cancelled:
                    break
                    
                # Pause courte
                time.sleep(0.1)
                
                # Céder le contrôle à nouveau
                loop = QEventLoop()
                QTimer.singleShot(10, loop.quit)
                loop.exec()
                
                # Mettre à jour la progression
                self.progress.emit(40 + i*10)
            
            # Ici, ajoutez votre logique de vérification de connexion réelle
            # Par exemple, une requête HTTP vers le serveur IA
            
            self.progress.emit(95)
            
            # Si la connexion réussit
            self.connection_result.emit(True, self.server_url)
            self.progress.emit(100)
            
        except Exception as e:
            # En cas d'échec, émettre un signal avec False
            self.connection_result.emit(False, str(e))
        finally:
            # Toujours émettre le signal de fin pour nettoyer le thread
            self.finished.emit()
    
    def cancel(self):
        """Annule la vérification de connexion en cours"""
        self.is_cancelled = True


def get_svg_icon(name, size=24, color="#000000"):
    """
    Charger et colorer une icône SVG en utilisant load_colored_svg du module ui_utils
    Utilise une approche très simple et directe
    """
    # Chemin de l'icône dans le dossier assets/icons
    project_icon_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "../..", f"assets/icons/{name}.svg"))
    
    if not os.path.exists(project_icon_path):
        print(f"[Erreur] Icône SVG non trouvée: {name}.svg")
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        return pixmap
    
    # Créer un pixmap carré plus grand que nécessaire
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    
    # Charger l'image SVG avec la couleur demandée
    svg_data = load_colored_svg(project_icon_path, color)
    renderer = QSvgRenderer(svg_data)
    
    # Dessiner le SVG sur le pixmap
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    renderer.render(painter)
    painter.end()
    
    return pixmap


class TopBarWidget(QFrame):
    """Composant pour la barre supérieure de l'interface ChatArboWidget
    Contient le statut de connexion, le sélecteur de modèle et les boutons d'action"""
    
    # Signaux
    exportClicked = Signal()
    clearClicked = Signal()
    skeletonClicked = Signal()
    historyClicked = Signal()
    infoClicked = Signal()
    checkConnectionClicked = Signal()
    modelChanged = Signal(str)
    connection_status_changed = Signal(bool, str)  # Nouveau signal pour notifier du changement de statut
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            "background-color: #2a2a2a; border-radius: 6px; padding: 4px; border: 1px solid #444444;"
        )
        
        # Initialiser le thread de connexion
        self.connection_thread = QThread()
        self.connection_worker = None
        
        # Configuration de l'interface
        self.setup_ui()

    def setup_ui(self):
        """Initialisation de l'interface utilisateur"""
        from PySide6.QtGui import QPainter

        # Layout principal
        top_bar_layout = QHBoxLayout(self)
        top_bar_layout.setContentsMargins(10, 5, 10, 5)

        # Partie gauche : statut de connexion
        status_layout = QHBoxLayout()


        self.status_indicator = QLabel("")
        self.status_indicator.setStyleSheet(
            "color: #fff;border: none;"
        )
        status_layout.addWidget(self.status_indicator)

        top_bar_layout.addLayout(status_layout)
        top_bar_layout.addStretch(1)

        # Partie centrale : sélecteur de modèle
        model_layout = QHBoxLayout()
        lb = QLabel("Modèle IA:")
        lb.setStyleSheet(
            "color: #e0e0e0;border: none; background: transparent;"
        )
        model_layout.addWidget(lb)
        self.model_choice = QComboBox()
        self.model_choice.addItems(["OpenAI", "DeepSeek"])
        self.model_choice.setFixedWidth(120)
        self.model_choice.setFixedHeight(30)
        self.model_choice.setStyleSheet("font-weight: normal;")
        self.model_choice.currentTextChanged.connect(self.on_model_changed)
        model_layout.addWidget(self.model_choice)

        top_bar_layout.addLayout(model_layout)

        # Ajouter un espace entre le sélecteur de modèle et les boutons d'action
        top_bar_layout.addSpacing(20)

        # Style commun pour les boutons ronds
        round_button_style = """
            QPushButton {
                background-color: rgba(76, 175, 80, 0.15);
                border: 2px solid #4CAF50;
                border-radius: 18px;
            }
            QPushButton:hover {
                background-color: rgba(76, 175, 80, 0.3);
                border: 2px solid #66BB6A;
            }
            QPushButton:pressed {
                background-color: rgba(76, 175, 80, 0.5);
                border: 2px solid #388E3C;
            }
        """

        # Bouton pour exporter la conversation
        self.export_btn = QPushButton()
        self.export_btn.setFixedSize(36, 36)  # Bouton rond
        export_pixmap = get_svg_icon("file-down", size=18, color="#4CAF50")
        if export_pixmap:
            self.export_btn.setIcon(QIcon(export_pixmap))
            self.export_btn.setIconSize(QSize(18, 18))
        self.export_btn.setStyleSheet(round_button_style)
        self.export_btn.setToolTip("Exporter la conversation")
        self.export_btn.clicked.connect(self.exportClicked.emit)
        top_bar_layout.addWidget(self.export_btn)

        # Bouton pour effacer la conversation
        self.clear_btn = QPushButton()
        self.clear_btn.setFixedSize(36, 36)  # Bouton rond
        clear_pixmap = get_svg_icon("trash-2", size=18, color="#4CAF50")
        if clear_pixmap:
            self.clear_btn.setIcon(QIcon(clear_pixmap))
            self.clear_btn.setIconSize(QSize(18, 18))
        self.clear_btn.setStyleSheet(round_button_style)
        self.clear_btn.setToolTip("Effacer la conversation")
        self.clear_btn.clicked.connect(self.clearClicked.emit)
        top_bar_layout.addWidget(self.clear_btn)

        # Bouton pour créer un squelette d'application
        self.skeleton_btn = QPushButton()
        self.skeleton_btn.setFixedSize(36, 36)  # Bouton rond
        skeleton_pixmap = get_svg_icon("code", size=18, color="#4CAF50")
        if skeleton_pixmap:
            self.skeleton_btn.setIcon(QIcon(skeleton_pixmap))
            self.skeleton_btn.setIconSize(QSize(18, 18))
        self.skeleton_btn.setStyleSheet(round_button_style)
        self.skeleton_btn.setToolTip("Créer un squelette d'application")
        self.skeleton_btn.clicked.connect(self.skeletonClicked.emit)
        top_bar_layout.addWidget(self.skeleton_btn)

        # Bouton pour afficher l'historique
        self.history_btn = QPushButton()
        self.history_btn.setFixedSize(36, 36)  # Bouton rond
        history_pixmap = get_svg_icon("clock-9", size=18, color="#4CAF50")
        if history_pixmap:
            self.history_btn.setIcon(QIcon(history_pixmap))
            self.history_btn.setIconSize(QSize(18, 18))
        self.history_btn.setStyleSheet(round_button_style)
        self.history_btn.setToolTip("Historique des conversations")
        self.history_btn.clicked.connect(self.historyClicked.emit)
        top_bar_layout.addWidget(self.history_btn)

        # Bouton pour afficher les infos du projet
        self.info_btn = QPushButton()
        self.info_btn.setFixedSize(36, 36)  # Bouton rond
        info_pixmap = get_svg_icon("circle-help", size=18, color="#4CAF50")
        if info_pixmap:
            self.info_btn.setIcon(QIcon(info_pixmap))
            self.info_btn.setIconSize(QSize(18, 18))
        self.info_btn.setStyleSheet(round_button_style)
        self.info_btn.setToolTip("Informations du projet")
        self.info_btn.clicked.connect(self.infoClicked.emit)
        top_bar_layout.addWidget(self.info_btn)

        # Ajouter un espace entre les boutons d'action et le bouton de vérification
        top_bar_layout.addSpacing(10)

        # Partie droite : bouton de vérification avec icône uniquement
        self.check_connection_btn = QPushButton()
        self.check_connection_btn.setFixedSize(36, 36)  # Bouton rond pour l'icône uniquement
        # Utiliser notre fonction pour charger l'icône SVG en vert
        refresh_pixmap = get_svg_icon("rotate-cw", size=18, color="#4CAF50")
        if refresh_pixmap:
            self.check_connection_btn.setIcon(QIcon(refresh_pixmap))
            self.check_connection_btn.setIconSize(QSize(18, 18))
        
        # Utiliser le même style que les autres boutons ronds
        self.check_connection_btn.setStyleSheet(round_button_style)
        self.check_connection_btn.setToolTip("Vérifier la connexion au serveur IA")
        self.check_connection_btn.clicked.connect(self.check_connection_async)
        top_bar_layout.addWidget(self.check_connection_btn)

    def check_connection_async(self):
        """Vérifie la connexion au serveur IA de manière asynchrone sans bloquer l'interface"""
        # Modifier l'icône pour indiquer que la vérification est en cours
        connecting_pixmap = get_svg_icon("loader", size=24, color="#FFA500")
        if connecting_pixmap:
            self.status_icon.setPixmap(connecting_pixmap)
        self.status_indicator.setText("Vérification de la connexion...")
        self.status_indicator.setStyleSheet("color: #FFA500; font-weight: bold; border: none;")
        
        # Nettoyer proprement avant de créer un nouveau thread
        self.cleanup_connection_thread()
        
        # Créer un nouveau thread avec priorité IDLE pour éviter d'interférer avec l'interface
        # IDLE est la priorité la plus basse possible, utilisée uniquement quand le CPU est inactif
        self.connection_thread = QThread()
        self.connection_thread.setPriority(QThread.IdlePriority)  # Priorité la plus basse
        
        # Créer un nouveau travailleur
        self.connection_worker = ConnectionWorker(server_url="http://localhost:5000")
        self.connection_worker.moveToThread(self.connection_thread)
        
        # Connecter le signal de progression pour mettre à jour l'interface
        self.connection_worker.progress.connect(self.on_connection_progress)
        
        # Connecter les autres signaux avec Qt.QueuedConnection pour éviter les blocages
        self.connection_thread.started.connect(
            self.connection_worker.check_connection, 
            type=Qt.QueuedConnection
        )
        self.connection_worker.finished.connect(
            self.connection_thread.quit, 
            type=Qt.QueuedConnection
        )
        self.connection_worker.connection_result.connect(
            self.on_connection_result, 
            type=Qt.QueuedConnection
        )
        
        # Démarrer le thread après un délai plus long pour s'assurer que l'interface a le temps de se mettre à jour
        QTimer.singleShot(200, self.connection_thread.start)
        
        # Émettre le signal pour informer les composants parents (sans attendre le résultat)
        QTimer.singleShot(50, self.checkConnectionClicked.emit)
    
    def cleanup_connection_thread(self):
        """Nettoie proprement le thread de connexion existant"""
        if hasattr(self, 'connection_thread') and self.connection_thread and self.connection_thread.isRunning():
            # Déconnecter tous les signaux
            try:
                self.connection_thread.started.disconnect()
                if self.connection_worker:
                    self.connection_worker.finished.disconnect()
                    self.connection_worker.connection_result.disconnect()
            except Exception:
                pass  # Ignorer les erreurs si les signaux ne sont pas connectés
            
            # Arrêter le thread proprement
            self.connection_thread.quit()
            self.connection_thread.wait(500)  # Attendre max 500ms
    
    def on_connection_progress(self, percentage):
        """Met à jour l'interface utilisateur avec la progression de la connexion"""
        # Mettre à jour le texte de statut avec le pourcentage
        self.status_indicator.setText(f"Connexion en cours... {percentage}%")
        
        # Optionnellement, on pourrait ajouter une barre de progression ici
        # mais pour l'instant on se contente de mettre à jour le texte
    
    def on_connection_result(self, is_connected, server_url):
        """Traite le résultat de la vérification de connexion"""
        # Mettre à jour l'interface utilisateur
        self.update_connection_status(is_connected, server_url)
        
        # Émettre le signal pour informer les composants parents
        self.connection_status_changed.emit(is_connected, server_url)
    
    def update_selected_path(self, path, is_dir=True):
        """
        Affiche le chemin sélectionné dans le TreeView
        
        Args:
            path (str): Chemin sélectionné
            is_dir (bool): True si c'est un dossier, False si c'est un fichier
        """
        # Normaliser le chemin pour l'affichage et le tooltip
        full_path = path.replace('\\', '/')
        emoji = '📁'
        if len(path) <= 3 and (path.endswith(':') or path.endswith(':/') or path.endswith(':\\')):
            display_path = full_path
            #emoji = '📁'  # Emoji disque dur pour les lecteurs
        else:
            display_path = os.path.basename(path)
            #emoji = '📁' if is_dir else '📄'  
            
        # Créer un message HTML avec l'emoji approprié
        html_message = f'<span style="font-size: 14px;">{emoji} <b>{display_path}</b></span>'
        
        # Afficher dans le label de statut de manière sécurisée
        try:
            if hasattr(self, 'status_indicator') and self.status_indicator:
                self.status_indicator.setText(html_message)
                self.status_indicator.setStyleSheet("border: none;")
                
                # Ajouter un tooltip avec le chemin complet
                self.status_indicator.setToolTip(full_path)
        except RuntimeError:
            # L'objet a déjà été supprimé, ignorer silencieusement
            print("Impossible de mettre à jour le chemin : le label a été supprimé")
        except Exception as e:
            print(f"Erreur lors de la mise à jour du chemin : {e}")
    
    def update_connection_status(self, is_connected, server_url=None):
        """
        Mettre à jour l'indicateur de statut de connexion au niveau de la combobox
        
        Args:
            is_connected (bool): True si connecté, False sinon
            server_url (str, optional): URL du serveur connecté
        """
        if is_connected:
            # Afficher un indicateur vert près de la combobox Modèle IA
            self.model_choice.setStyleSheet("font-weight: normal; border-left: 4px solid #4CAF50;")
        else:
            # Afficher un indicateur rouge près de la combobox Modèle IA
            self.model_choice.setStyleSheet("font-weight: normal; border-left: 4px solid #d32f2f;")
            
        # Émettre le signal de changement de statut
        self.connection_status_changed.emit(is_connected, server_url if server_url else "")

    def get_selected_model(self):
        """Retourne le modèle IA actuellement sélectionné"""
        return self.model_choice.currentText()

    def on_model_changed(self, model_text):
        """Émission du signal quand le modèle change"""
        self.modelChanged.emit(model_text)
