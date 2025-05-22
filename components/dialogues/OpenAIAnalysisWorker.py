from PySide6.QtCore import QObject, Signal, Slot, QSettings

class OpenAIAnalysisWorker(QObject):
    analysis_complete = Signal(str)
    analysis_error = Signal(str)

    def __init__(self, markdown_content: str):
        super().__init__()
        self.markdown_content = markdown_content
        
        # Utilisation des mêmes noms que dans PhaseWizardWidget pour QSettings
        settings = QSettings("AssistantIA", "PhaseWizard") 
        api_key = settings.value("api_key_openai", None) 

        if not api_key:
            print("ERREUR: Clé API OpenAI ('api_key_openai') non trouvée dans QSettings pour AssistantIA/PhaseWizard.")
            self.openai_client = None
        else:
            try:
                from services.openai_client import OpenAIClient 
                self.openai_client = OpenAIClient(api_key=api_key)
            except ImportError:
                self.openai_client = None
                print("ERREUR: Impossible d'importer OpenAIClient depuis services.openai_client.")
                print("Veuillez vous assurer que le fichier existe et que la classe est correctement définie.")
            except Exception as e: 
                self.openai_client = None
                print(f"ERREUR lors de l'initialisation de OpenAIClient : {e}")

    @Slot()
    def run_analysis(self):
        try:
            prompt = (
                "Vous êtes un assistant expert en gestion de projet logiciel. "
                "Analysez le document Markdown suivant, qui décrit un projet. "
                "Évaluez sa cohérence globale, en identifiant les points forts, les faiblesses, "
                "les ambiguïtés, les contradictions potentielles, ou les manques d'informations critiques. "
                "Fournissez un rapport structuré et détaillé sous format Markdown.\n\n"
                "Document du projet:\n"
                f"{self.markdown_content}"
            )
            
            if not self.openai_client:
                self.analysis_error.emit("Client OpenAI non initialisé. Vérifiez l'import, la configuration de services.openai_client.py, et la présence de la clé API dans QSettings.")
                return

            try:
                # Utilisation de la méthode generer_code de OpenAIClient
                if hasattr(self.openai_client, 'generer_code'):
                    response = self.openai_client.generer_code(prompt)
                else:
                    self.analysis_error.emit("La méthode 'generer_code' n'est pas trouvée dans la classe OpenAIClient de services.openai_client.py.")
                    return

                if response:
                    self.analysis_complete.emit(response)
                else:
                    self.analysis_error.emit("Réponse vide reçue de l'API OpenAI.")
            except Exception as api_error:
                print(f"Erreur d'API OpenAI : {api_error}")
                self.analysis_error.emit(f"Erreur lors de la communication avec l'API OpenAI : {api_error}")

        except Exception as e:
            print(f"Erreur générale dans run_analysis : {e}")
            self.analysis_error.emit(f"Erreur inattendue lors de la préparation de l'analyse : {e}")
