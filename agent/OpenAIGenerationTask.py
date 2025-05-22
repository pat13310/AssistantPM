import openai
import os
from PySide6.QtCore import QRunnable, QObject, Signal

# --- Signaux pour génération IA ---
class GenerationSignals(QObject):
    finished = Signal(str, str)  # chemin complet, contenu HTML
    error = Signal(str)
    progress = Signal(int)  # pourcentage de progression (0-100)

openai.api_key = os.getenv("OPENAI_API_KEY")

# --- Tâche asynchrone ---
class OpenAIGenerationTask(QRunnable):
    def __init__(self, full_path, prompt):
        super().__init__()
        self.full_path = full_path
        self.prompt = prompt
        self.signals = GenerationSignals()

    def run(self):
        try:
            # Indiquer que la génération commence
            self.signals.progress.emit(10)
            
            # Initialiser le client OpenAI
            client = openai.OpenAI()
            self.signals.progress.emit(30)
            
            # Envoyer la requête à l'API
            self.signals.progress.emit(50)
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": self.prompt}],
                temperature=0.7
            )
            self.signals.progress.emit(80)
            
            # Traiter la réponse
            html = response.choices[0].message.content.strip()
            self.signals.progress.emit(95)
            
            # Émettre le signal de fin
            self.signals.finished.emit(self.full_path, html)
            self.signals.progress.emit(100)
        except Exception as e:
            self.signals.error.emit(str(e))
