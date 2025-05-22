import openai
import os
from PySide6.QtCore import QRunnable, QObject, Signal

# --- Signaux pour génération IA en streaming ---
class StreamingSignals(QObject):
    finished = Signal(str, str)  # chemin complet, contenu HTML final
    error = Signal(str)
    progress = Signal(int)  # pourcentage de progression (0-100)
    chunk = Signal(str)  # nouveau morceau de texte généré

openai.api_key = os.getenv("OPENAI_API_KEY")

# --- Tâche asynchrone en mode streaming ---
class OpenAIStreamingTask(QRunnable):
    def __init__(self, full_path, prompt):
        super().__init__()
        self.full_path = full_path
        self.prompt = prompt
        self.signals = StreamingSignals()
        self.accumulated_text = ""

    def run(self):
        try:
            # Indiquer que la génération commence
            self.signals.progress.emit(10)
            
            # Initialiser le client OpenAI
            client = openai.OpenAI()
            self.signals.progress.emit(20)
            
            # Envoyer la requête à l'API en mode streaming
            self.signals.progress.emit(30)
            stream = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": self.prompt}],
                temperature=0.7,
                stream=True  # Activer le mode streaming
            )
            
            # Initialiser le compteur de progression
            self.signals.progress.emit(40)
            chunk_count = 0
            estimated_total_chunks = 100  # Estimation du nombre total de morceaux
            
            # Traiter le flux de réponses
            for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    # Extraire le texte du chunk
                    delta = chunk.choices[0].delta
                    if hasattr(delta, 'content') and delta.content:
                        # Émettre le nouveau morceau
                        self.signals.chunk.emit(delta.content)
                        # Accumuler le texte
                        self.accumulated_text += delta.content
                
                # Mettre à jour la progression
                chunk_count += 1
                progress = min(40 + int(50 * chunk_count / estimated_total_chunks), 90)
                self.signals.progress.emit(progress)
            
            # Finaliser la génération
            self.signals.progress.emit(95)
            
            # Émettre le signal de fin avec le texte complet
            self.signals.finished.emit(self.full_path, self.accumulated_text.strip())
            self.signals.progress.emit(100)
            
        except Exception as e:
            self.signals.error.emit(str(e))
