from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QWidget
)
from project.structure.ui.widgets.status_combo_box import StatusComboBox
from PySide6.QtCore import Signal, QSize, QThread, QObject, Qt, QTimer, QRectF, QThreadPool
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
import json
import os
import sys

# Ajouter le répertoire racine au chemin d'importation pour trouver le module ui
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from ui.ui_utils import load_colored_svg

# Importer ConnectionWorker depuis le module dédié
from project.structure.connection_worker import ConnectionWorker

# Constantes pour les couleurs de statut
STATUS_ERROR = "#FF0000"  # Rouge
STATUS_OK = "#4CAF50"     # Vert
STATUS_RESET = "#808080"  # Gris
STATUS_PENDING = "#FFA500"  # Orange (pour les vérifications en cours)

def get_svg_icon(name, size=24, color="#000000"):
    """
    Charger et colorer une icône SVG en utilisant load_colored_svg du module ui_utils
    Utilise une approche très simple et directe
    """
    # Chemin de l'icône dans le dossier assets/icons
    project_icon_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "../..", f"assets/icons/{name}.svg"))
    
    if not os.path.exists(project_icon_path):
        print(f"[Erreur] Icône SVG non trouvée: {name}.svg")
        # Utiliser une icône de secours en fonction du nom demandé
        fallback_icons = {
            "alert-circle": "warning",
            "check-circle": "check",
            "circle-help": "help"
        }
        
        # Essayer d'utiliser une icône de secours
        if name in fallback_icons:
            fallback_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "../..", 
                                                        f"assets/icons/{fallback_icons[name]}.svg"))
            if os.path.exists(fallback_path):
                print(f"[Info] Utilisation de l'icône de secours: {fallback_icons[name]}.svg")
                project_icon_path = fallback_path
            else:
                # Créer un pixmap vide si l'icône de secours n'existe pas non plus
                pixmap = QPixmap(size, size)
                pixmap.fill(Qt.transparent)
                return pixmap
        else:
            # Créer un pixmap vide si aucune icône de secours n'est définie
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
        status_layout.setSpacing(5)
        
        # Icône de statut
        self.status_icon = QLabel()
        self.status_icon.setFixedSize(24, 24)
        self.status_icon.setStyleSheet("border: none;")
        status_layout.addWidget(self.status_icon)
        
        # Texte de statut
        self.status_indicator = QLabel("Non connecté")
        self.status_indicator.setStyleSheet(f"color: {STATUS_RESET}; font-weight: normal; border: none;")
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
        
        # Utiliser StatusComboBox au lieu de QComboBox
        self.model_choice = StatusComboBox()
        
        # Charger les types d'IA depuis le fichier JSON
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "ia_types.json")
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                ia_types = json.load(f)
                
            # Ajouter les types d'IA au combo box avec tooltips
            for i, ia_type in enumerate(ia_types):
                self.model_choice.addItem(ia_type["name"])
                # Ajouter la description comme tooltip
                self.model_choice.combo_box.setItemData(i, ia_type["description"], Qt.ToolTipRole)
        except Exception as e:
            print(f"Erreur lors du chargement des types d'IA: {e}")
            # Valeurs par défaut en cas d'erreur
            self.model_choice.addItems(["OpenAI", "Anthropic", "Google", "Deepseek", "Local"])
        
        self.model_choice.setFixedWidth(120)
        self.model_choice.setFixedHeight(30)
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
        """Vérifie la connexion au serveur de manière asynchrone avec QThreadPool"""
        try:
            # Nettoyer les ressources précédentes si nécessaire
            self.cleanup_connection_thread()
            
            
            # Mettre à jour l'indicateur de statut en attente
            self.status_indicator.setText("Vérification de la connexion...")
            self.status_indicator.setStyleSheet(f"color: {STATUS_PENDING}; font-weight: bold; border: none;")
            
            # Créer un nouveau worker
            self.connection_worker = ConnectionWorker("http://localhost:8000/health", timeout=3.0)
            
            # Connecter les signaux
            self.connection_worker.signals.connection_result.connect(self.on_connection_result)
            self.connection_worker.signals.progress.connect(self.on_connection_progress)
            self.connection_worker.signals.finished.connect(self.on_connection_finished)
            
            # Démarrer le worker dans le thread pool
            print("Démarrage de la vérification de connexion au serveur...")
            QThreadPool.globalInstance().start(self.connection_worker)
            
            # Émettre le signal pour informer les composants parents
            self.checkConnectionClicked.emit()
        except Exception as e:
            print(f"Erreur lors de la vérification de connexion: {e}")
            self.update_connection_status(False, f"Erreur: {str(e)}")
            # Émettre le signal pour informer les composants parents
            self.connection_status_changed.emit(False, f"Erreur interne: {str(e)}")
    
    def cleanup_connection_thread(self):
        """Nettoie proprement les ressources de connexion"""
        # Réinitialiser le style de l'indicateur de statut
        self.status_indicator.setStyleSheet(f"color: {STATUS_RESET}; font-weight: normal; border: none;")
        
        # Avec QThreadPool, nous n'avons plus besoin de nettoyer manuellement les threads
        # Nous devons juste annuler le worker en cours si nécessaire
        if hasattr(self, 'connection_worker') and self.connection_worker:
            self.connection_worker.cancel()
    
    def on_connection_finished(self):
        """Gère la fin de la vérification de connexion"""
        print("Vérification de connexion terminée")
        # Rien de spécial à faire ici car QThreadPool gère automatiquement le nettoyage
    
    def on_connection_progress(self, percentage):
        """Met à jour l'interface utilisateur avec la progression de la connexion"""
        # Mettre à jour le texte de statut avec le pourcentage
        self.status_indicator.setText(f"Connexion en cours... {percentage}%")
        
        # Optionnellement, on pourrait ajouter une barre de progression ici
        # mais pour l'instant on se contente de mettre à jour le texte
    
    def on_connection_result(self, is_connected, message):
        """Traite le résultat de la vérification de connexion"""
        # Mettre à jour l'interface utilisateur avec le résultat
        self.update_connection_status(is_connected, message)
        
        # Émettre le signal pour informer les composants parents
        self.connection_status_changed.emit(is_connected, message)
        
        # Configurer un timer pour effacer le message après 3 secondes
        QTimer.singleShot(3000, self.reset_status_message)
    
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
    
    def update_connection_status(self, is_connected, message=""):
        """Met à jour l'indicateur de statut en fonction de l'état de connexion"""
        if is_connected:
            # Connexion réussie - afficher une icône verte
            status_pixmap = get_svg_icon("check-circle", size=24, color=STATUS_OK)
            if status_pixmap:
                self.status_icon.setPixmap(status_pixmap)
            self.status_indicator.setText("Connecté au serveur IA")
            self.status_indicator.setStyleSheet(f"color: {STATUS_OK}; font-weight: bold; border: none;")
            
            # Mettre à jour le statut de la StatusComboBox pour indiquer une connexion réussie
            self.model_choice.setStatusOk()
        else:
            # Connexion échouée - afficher une icône rouge
            status_pixmap = get_svg_icon("alert-circle", size=24, color=STATUS_ERROR)
            if status_pixmap:
                self.status_icon.setPixmap(status_pixmap)
            
            # Afficher le message d'erreur s'il est fourni, sinon un message générique
            if message:
                self.status_indicator.setText(f"{message}")
            else:
                self.status_indicator.setText("Non connecté au serveur IA")
            
            self.status_indicator.setStyleSheet(f"color: {STATUS_ERROR}; font-weight: bold; border: none;")
            
            # Mettre à jour le statut de la StatusComboBox pour indiquer une connexion échouée
            self.model_choice.setStatusError()

    def reset_status_message(self):
        """Efface le message de statut et remet l'interface à l'état normal"""
        # Effacer le texte du statut
        self.status_indicator.setText("")

        self.status_indicator.setStyleSheet(f"color: {STATUS_RESET}; font-weight: normal; border: none;")
        
        
    def get_selected_model(self):
        """Retourne le modèle IA actuellement sélectionné"""
        return self.model_choice.currentText()

    def on_model_changed(self, model_name):
        """Gère le changement de modèle"""
        print(f"Modèle changé pour: {model_name}")
        
    def update_model(self, model_id):
        """Met à jour le modèle sélectionné dans la barre supérieure"""
        # Trouver le texte correspondant à l'ID du modèle
        model_text = model_id
        
        # Vérifier si le modèle existe déjà dans la liste
        found = False
        for i in range(self.model_choice.combo_box.count()):
            if self.model_choice.combo_box.itemText(i) == model_text:
                self.model_choice.setCurrentIndex(i)
                found = True
                break
        
        # Si le modèle n'est pas dans la liste, l'ajouter
        if not found:
            self.model_choice.addItem(model_text)
            # Sélectionner le dernier élément ajouté
            self.model_choice.setCurrentIndex(self.model_choice.combo_box.count() - 1)