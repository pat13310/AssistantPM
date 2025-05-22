import os
import sys

_current_dir_for_sys_path = os.path.dirname(os.path.abspath(__file__))
_project_root_for_sys_path = os.path.dirname(os.path.dirname(_current_dir_for_sys_path))
if _project_root_for_sys_path not in sys.path:
    sys.path.insert(0, _project_root_for_sys_path)

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTextEdit, QPushButton, QWidget,
    QHBoxLayout, QGraphicsDropShadowEffect
)
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtCore import Qt, Signal, QThread, QRect, QSize
from PySide6.QtGui import QFont, QColor, QPainterPath, QRegion, QKeyEvent

# Importer le worker
from .OpenAIAnalysisWorker import OpenAIAnalysisWorker
from ui.ui_utils import load_colored_svg # Assurez-vous que render_svg_icon n'est pas importé

# Pour la conversion Markdown -> HTML
try:
    import markdown
except ImportError:
    markdown = None
    print("Avertissement: La bibliothèque 'markdown' n'est pas installée. Le rendu Markdown sera basique.")
    print("Pour un meilleur rendu, veuillez installer la bibliothèque : pip install markdown")


# Supposons que vous ayez un client OpenAI configuré quelque part, par exemple :
# from services.openai_client import OpenAIClient # À adapter pour l'appel réel

class AnalyseProjectDlg(QDialog):
    def __init__(self, project_markdown_content: str, parent=None):
        super().__init__(parent)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)

        self.project_markdown_content = project_markdown_content
        self.analysis_thread = None
        self.analysis_worker = None

        # Dimensions et rayon pour les coins arrondis
        radius = 16 # Un peu moins que DocGenerationDlg pour varier
        width, height = 650, 550 # Adapté pour plus de contenu
        self.resize(width, height)

        # === Conteneur principal ===
        self.container = QWidget(self)
        self.container.setGeometry(0, 0, width, height)
        self.container.setObjectName("containerDialog") # Nom d'objet pour le style
        self.container.setStyleSheet("""
            QWidget#containerDialog {
                background-color: #F0FDF4; /* Vert très clair */
                border: 1px solid #86EFAC; /* Bordure verte claire */
                border-radius: %spx;
            }
        """ % radius)

        # === Masque arrondi (shape réelle) ===
        # Le masque est toujours nécessaire pour les coins arrondis parfaits si la bordure est > 0
        # et pour que la transparence de la QDialog fonctionne correctement.
        path = QPainterPath()
        path.addRoundedRect(QRect(0, 0, width, height), radius, radius)
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region) # Applique le masque à la QDialog elle-même

        # === Ombre autour du conteneur ===
        shadow = QGraphicsDropShadowEffect(self) # Appliquer à self, pas self.container directement
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow) # L'ombre est sur la QDialog, le container est juste le fond visible

        # === Layout interne ===
        internal_layout = QVBoxLayout(self.container) # Le layout est dans le container
        internal_layout.setSpacing(20)
        internal_layout.setContentsMargins(30, 30, 30, 30) # Marges ajustées

        # === En-tête avec icône ===
        header_layout = QHBoxLayout()
        icon_widget = QSvgWidget() # Remplacer QLabel par QSvgWidget
        icon_widget.setFixedSize(QSize(26, 26))
        icon_widget.setStyleSheet("background-color: transparent; border: none;")

        svg_data = load_colored_svg("assets/icons/search.svg") # Pas de couleur spécifiée, utilise la couleur du SVG ou noir par défaut
        if svg_data.isEmpty():
            print("Warning: Icon assets/icons/search.svg could not be loaded for AnalyseProjectDlg.")
        else:
            icon_widget.load(svg_data)
        
        self.title_label = QLabel("Analyse de Cohérence du Projet")
        self.title_label.setStyleSheet(" font-size: 17px; font-weight: bold; color: #1F2937;background-color: transparent;border: none;")

        header_layout.addWidget(icon_widget) # Ajouter le QSvgWidget
        header_layout.addSpacing(12)
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()

        # === Bouton de fermeture (croix) ===
        self.close_icon_button = QPushButton("✕") # Utilisation du caractère de multiplication
        self.close_icon_button.setCursor(Qt.PointingHandCursor)
        self.close_icon_button.setFixedSize(30, 30) # Taille fixe pour un aspect carré
        self.close_icon_button.setStyleSheet("""
            QPushButton {
                font-family: 'Arial', sans-serif; /* Police qui rend bien la croix */
                font-size: 16px;
                font-weight: bold;
                color: #9CA3AF; /* Gris moyen */
                background-color: transparent;
                border: none;
                border-radius: 15px; /* Pour un cercle parfait si la taille est fixe */
            }
            QPushButton:hover { 
                color: #16A34A; /* Vert foncé pour le texte au survol */
                background-color: #D1FAE5; /* Vert très clair pour le fond au survol */
            }
            QPushButton:pressed { 
                color: #065F46; /* Vert encore plus foncé pour le texte au clic */
                background-color: #A7F3D0; /* Vert clair pour le fond au clic */
            }
        """)
        self.close_icon_button.clicked.connect(self.reject) # Ferme la dialogue
        header_layout.addWidget(self.close_icon_button)

        internal_layout.addLayout(header_layout)
        
        # === Zone de texte pour les résultats ===
        self.result_text_edit = QTextEdit()
        self.result_text_edit.setReadOnly(True)
        self.result_text_edit.setPlaceholderText("Cliquez sur 'Lancer l'analyse' pour obtenir le rapport de cohérence du projet généré par l'IA.")
        self.result_text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #FFFFFF;
                border: 1px solid #D1D5DB;
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
                color: #374151;
            }
        """)
        internal_layout.addWidget(self.result_text_edit, 1) # Le '1' donne de l'expansion

        # === Boutons d'action ===
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)

        self.analyse_button = QPushButton("Lancer l'analyse")
        self.analyse_button.setCursor(Qt.PointingHandCursor)
        self.analyse_button.setStyleSheet("""
            QPushButton {
                background-color: #22C55E; /* Vert principal */
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 12px 20px;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #16A34A; /* Vert plus foncé au survol */
            }
            QPushButton:disabled {
                background-color: #A3E6B8; /* Vert plus clair et désaturé pour désactivé */
                color: #F0FDF4;
            }
        """)
        self.analyse_button.clicked.connect(self.start_analysis)
        
        
        buttons_layout.addStretch() # Pousse les boutons vers la droite
        buttons_layout.addWidget(self.analyse_button) # Bouton principal à droite
        internal_layout.addLayout(buttons_layout)
        
        # Centrage
        self.adjustSize() # Ajuste la taille au contenu si nécessaire
        if parent:
            self.move(parent.rect().center() - self.rect().center())
        else:
            screen = self.screen().availableGeometry()
            self.move(
                screen.center().x() - self.width() // 2,
                screen.center().y() - self.height() // 2
            )


    def start_analysis(self):
        if self.analysis_thread and self.analysis_thread.isRunning():
            # Ne pas démarrer une nouvelle analyse si une est déjà en cours
            return

        self.analyse_button.setEnabled(False)
        self.result_text_edit.setMarkdown("Analyse en cours, veuillez patienter...") # Utiliser setMarkdown pour un meilleur rendu

        self.analysis_thread = QThread() # Pas de parent pour le QThread
        self.analysis_worker = OpenAIAnalysisWorker(self.project_markdown_content)
        self.analysis_worker.moveToThread(self.analysis_thread)

        # Connecter les signaux du worker aux slots
        self.analysis_worker.analysis_complete.connect(self.on_analysis_complete)
        self.analysis_worker.analysis_error.connect(self.on_analysis_error)
        
        # Connecter le démarrage du thread à la méthode run_analysis du worker
        self.analysis_thread.started.connect(self.analysis_worker.run_analysis)
        
        # Signaux pour quitter le thread lorsque le worker a terminé ou a une erreur
        self.analysis_worker.analysis_complete.connect(self.analysis_thread.quit)
        self.analysis_worker.analysis_error.connect(self.analysis_thread.quit)

        # Nettoyage après la fin du thread
        # Il est crucial que deleteLater soit appelé pour que Qt nettoie les objets C++.
        self.analysis_thread.finished.connect(self.analysis_worker.deleteLater)
        # NE PAS connecter self.analysis_thread.deleteLater() ici directement.
        # Géré par _on_thread_finished ou closeEvent.
        self.analysis_thread.finished.connect(self._on_thread_finished)

        self.analysis_thread.start()

    def _on_thread_finished(self):
        """Appelé lorsque le thread (sender) se termine normalement."""
        finishing_thread = self.sender()
        if not isinstance(finishing_thread, QThread):
            # Cela ne devrait pas arriver si connecté correctement
            return

        if self.analyse_button and not self.analyse_button.isEnabled():
            self.analyse_button.setEnabled(True)

        # Si le thread qui a terminé est celui que nous suivons activement
        if hasattr(self, 'analysis_thread') and self.analysis_thread == finishing_thread:
            # Le worker associé (self.analysis_worker) est déjà connecté à deleteLater
            # via finishing_thread.finished. Nous devons juste effacer notre référence Python.
            if hasattr(self, 'analysis_worker'):
                self.analysis_worker = None
            
            # Effacer notre référence Python au thread.
            self.analysis_thread = None
        
        # L'objet QThread (finishing_thread) lui-même doit être marqué pour suppression.
        # C'est sûr car sa méthode run() est terminée.
        finishing_thread.deleteLater()

    def on_analysis_complete(self, report: str):
        if markdown:
            # Convertir Markdown en HTML
            # Utilisation d'extensions pour un meilleur rendu (par exemple, tables, fenced_code)
            try:
                html_report = markdown.markdown(report, extensions=['extra', 'sane_lists', 'codehilite', 'toc'])
                
                # Ajouter une feuille de style CSS de base pour l'HTML
                # Note: QTextEdit/QTextBrowser a un support CSS limité.
                # Les styles pour 'codehilite' (coloration syntaxique) sont généralement gérés par l'extension elle-même
                # en ajoutant des classes CSS. Il faudrait une feuille de style CSS plus complète pour les voir.
                styled_html = f"""
                <style>
                    body {{ font-family: 'Segoe UI', sans-serif; font-size: 13px; color: #374151; line-height: 1.6; }}
                    h1, h2, h3, h4, h5, h6 {{ color: #111827; margin-top: 1.2em; margin-bottom: 0.6em; line-height: 1.3; font-weight: 600;}}
                    h1 {{ font-size: 1.8em; }}
                    h2 {{ font-size: 1.5em; border-bottom: 1px solid #E5E7EB; padding-bottom: 0.3em; }}
                    h3 {{ font-size: 1.25em; }}
                    p {{ margin-bottom: 0.8em; }}
                    ul, ol {{ margin-left: 20px; margin-bottom: 0.8em; }}
                    li {{ margin-bottom: 0.3em; }}
                    code {{ 
                        background-color: #F3F4F6; 
                        padding: 0.2em 0.4em; 
                        margin: 0; 
                        font-size: 85%; 
                        border-radius: 3px; 
                        font-family: 'Consolas', 'Courier New', monospace;
                    }}
                    pre code {{
                        display: block;
                        padding: 0.8em;
                        overflow-x: auto;
                    }}
                    blockquote {{
                        border-left: 3px solid #D1D5DB;
                        padding-left: 1em;
                        color: #6B7280;
                        margin-left: 0;
                        margin-right: 0;
                        font-style: italic;
                    }}
                    table {{ border-collapse: collapse; width: 100%; margin-bottom: 1em; }}
                    th, td {{ border: 1px solid #D1D5DB; padding: 0.5em; text-align: left; }}
                    th {{ background-color: #F9FAFB; font-weight: bold; }}
                </style>
                {html_report}
                """
                self.result_text_edit.setHtml(styled_html)
            except Exception as e:
                print(f"Erreur lors de la conversion Markdown en HTML : {e}")
                self.result_text_edit.setMarkdown(report) # Fallback au rendu Markdown de base
        else:
            # Si la bibliothèque markdown n'est pas disponible, utiliser le rendu de base
            self.result_text_edit.setMarkdown(report)
        
        # self.analyse_button.setEnabled(True) # Déplacé vers _cleanup_thread_references
        # self.analysis_complete.emit(report) # Si la dialogue elle-même doit émettre un signal

    def on_analysis_error(self, error_message: str):
        self.result_text_edit.setPlainText(f"Erreur lors de l'analyse :\n{error_message}")
        # self.analyse_button.setEnabled(True) # Déplacé vers _cleanup_thread_references

    def closeEvent(self, event):
        if hasattr(self, 'analysis_thread') and self.analysis_thread and self.analysis_thread.isRunning():
            self.analysis_thread.quit() # Demander l'arrêt du thread
            if not self.analysis_thread.wait(5000): # Attendre jusqu'à 5 secondes
                # Le thread n'a pas pu s'arrêter à temps.
                print("Avertissement: Le thread d'analyse n'a pas pu être arrêté proprement lors de la fermeture. "
                      "Il pourrait y avoir une fuite de ressources ou un comportement inattendu si le thread continue en arrière-plan.")
                # IMPORTANT: Ne PAS appeler deleteLater sur le thread ici, et ne PAS effacer
                # self.analysis_thread. Cela "fuira" l'objet QThread et son worker,
                # mais empêchera l'avertissement "Destroyed while thread is still running".
                # La solution propre est de rendre la tâche du worker interruptible.
            # else:
                # wait() a réussi. Le thread s'est terminé.
                # Le signal 'finished' a été émis, et _on_thread_finished
                # s'occupera de deleteLater et de nettoyer les références Python.
                pass
        
        # Si self.analysis_thread existe mais n'est pas isRunning (c.-à-d. qu'il a déjà terminé
        # avant que closeEvent ne soit appelé), _on_thread_finished devrait déjà
        # avoir géré son nettoyage. Il n'y a généralement rien à faire ici dans ce cas.
        # Si _on_thread_finished n'a pas encore été traité par la boucle d'événements,
        # il le sera. Forcer deleteLater ici pourrait être prématuré ou redondant.

        super().closeEvent(event)


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    # Simuler un contenu markdown pour le test
    sample_markdown = """
# Projet Alpha

## 1. Objectifs
- Développer une application mobile.
- Atteindre 10,000 utilisateurs en 6 mois.

## 2. Fonctionnalités
- Authentification utilisateur
- Dashboard principal
- Messagerie instantanée (sera développée dans la phase 2)

## 3. Risques
- Dépassement de budget.
- Manque de ressources pour la phase 2.
    """
    dialog = AnalyseProjectDlg(sample_markdown)
    dialog.show()
    sys.exit(app.exec())
