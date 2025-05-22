import sys
import os
import time
from threading import Thread

# Ajouter le répertoire racine au chemin Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from PySide6.QtCore import QTimer, Signal, QObject
from project.documents.DocumentCard import DocumentCard

class WorkerSignals(QObject):
    """Signaux pour communiquer avec le thread principal"""
    finished = Signal()

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test État Occupé")
        self.setStyleSheet("background-color: #f3f6fb;")
        self.setMinimumSize(600, 400)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)
        
        # Créer une carte de document
        self.doc_card = DocumentCard(
            title="Cahier des Charges Fonctionnel",
            description="Définit les besoins et objectifs du projet",
            icon_name="list-checks",
            is_completed=False
        )
        
        # Ajouter la carte au layout
        main_layout.addWidget(self.doc_card)
        
        # Boutons de test
        buttons_layout = QHBoxLayout()
        
        # Bouton pour simuler un traitement
        self.start_button = QPushButton("Démarrer le traitement")
        self.start_button.clicked.connect(self.start_processing)
        buttons_layout.addWidget(self.start_button)
        
        # Bouton pour marquer comme complété
        self.complete_button = QPushButton("Marquer comme complété")
        self.complete_button.clicked.connect(self.mark_as_completed)
        buttons_layout.addWidget(self.complete_button)
        
        main_layout.addLayout(buttons_layout)
        
        # Signaux pour la communication avec le thread
        self.worker_signals = WorkerSignals()
        self.worker_signals.finished.connect(self.processing_finished)
    
    def start_processing(self):
        """Démarre un traitement simulé"""
        self.doc_card.setBusy(True)
        self.start_button.setEnabled(False)
        self.complete_button.setEnabled(False)
        
        # Simuler un traitement dans un thread séparé
        def process_task():
            # Simuler un traitement qui prend du temps
            time.sleep(3)
            # Émettre le signal de fin
            self.worker_signals.finished.emit()
        
        # Démarrer le thread
        thread = Thread(target=process_task)
        thread.daemon = True
        thread.start()
    
    def processing_finished(self):
        """Appelé lorsque le traitement est terminé"""
        self.doc_card.setBusy(False)
        self.start_button.setEnabled(True)
        self.complete_button.setEnabled(True)
    
    def mark_as_completed(self):
        """Marque le document comme complété"""
        # Simuler un traitement
        self.doc_card.setBusy(True)
        self.start_button.setEnabled(False)
        self.complete_button.setEnabled(False)
        
        # Utiliser un timer pour simuler un délai
        QTimer.singleShot(2000, self.complete_document)
    
    def complete_document(self):
        """Complète le document après le délai"""
        self.doc_card.setBusy(False)
        self.doc_card.is_completed = True
        
        # Mettre à jour l'affichage
        self.doc_card.setBusy(False)  # Appeler à nouveau pour mettre à jour l'icône
        
        # Désactiver le bouton de complétion
        self.complete_button.setEnabled(False)
        self.start_button.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())
