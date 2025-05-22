import openai
import os
from PySide6.QtCore import QRunnable, QObject, Signal

# --- Signaux pour génération IA ---
class GenerationSignals(QObject):
    finished = Signal(str, str)  # chemin complet, contenu HTML
    error = Signal(str)


api_key = os.getenv("DEEPSEEK_API_KEY")

class DeepSeekGenerationTask(QRunnable):
    def __init__(self, full_path, prompt):
        super().__init__()
        self.full_path = full_path
        self.prompt = prompt
        self.signals = GenerationSignals()  # Supposant que cette classe existe déjà
        self.key = api_key
        self.model = "deepseek-chat"  # Le modèle principal de DeepSeek (DeepSeek-V3)
    
    def run(self):
        try:
            # Créer un client OpenAI configuré pour utiliser l'API DeepSeek
            client = openai.Client(
                api_key=self.key,
                base_url="https://api.deepseek.com"
            )
            
            # Appeler l'API DeepSeek avec les mêmes paramètres que pour OpenAI
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": self.prompt}],
                temperature=0.7
            )
            
            # Récupérer le contenu généré
            html = response.choices[0].message.content.strip()
            
            # Émettre le signal de fin avec le résultat
            self.signals.finished.emit(self.full_path, html)
            
        except Exception as e:
            # Émettre le signal d'erreur
            self.signals.error.emit(str(e))