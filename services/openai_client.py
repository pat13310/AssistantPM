
from openai import OpenAI # Importation modifiée

class OpenAIClient:
    def __init__(self, api_key: str):
        try:
            self.client = OpenAI(api_key=api_key)
        except Exception as e:
            print(f"Erreur lors de l'initialisation du client OpenAI avec la clé API : {e}")
            self.client = None # S'assurer que client est None si l'initialisation échoue

    def generer_code(self, prompt: str) -> str | None:
        if not self.client:
            print("Client OpenAI non initialisé correctement. Impossible de générer du code.")
            return None
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo", # Assurez-vous que ce modèle est toujours disponible et approprié
                messages=[
                    {"role": "system", "content": "Tu es un assistant expert en gestion de projet logiciel."}, # Message système adapté
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3 # Une température basse pour des réponses plus déterministes
            )
            # Accès à la réponse selon la nouvelle API
            if response.choices and response.choices[0].message:
                return response.choices[0].message.content
            else:
                print("Réponse inattendue de l'API OpenAI ou pas de contenu de message.")
                return None
        except Exception as e:
            print(f"Erreur lors de l'appel à l'API OpenAI (chat.completions.create) : {e}")
            return None

if __name__ == '__main__':
    # Exemple d'utilisation (nécessite une clé API valide dans vos variables d'environnement ou passée directement)
    # Pour tester, vous pouvez décommenter et remplacer "VOTRE_CLE_API"
    # import os
    # test_api_key = os.environ.get("OPENAI_API_KEY") # Ou directement "sk-..."
    # if not test_api_key:
    #     test_api_key = "VOTRE_CLE_API_POUR_TEST" 

    # if "VOTRE_CLE_API" in test_api_key:
    #     print("Veuillez remplacer 'VOTRE_CLE_API_POUR_TEST' par une vraie clé pour tester.")
    # else:
    #     client = OpenAIClient(api_key=test_api_key)
    #     if client.client: # Vérifier si l'initialisation a réussi
    #         test_prompt = "Donne un exemple simple de fonction Python pour additionner deux nombres."
    #         print(f"Prompt de test: {test_prompt}")
    #         generated_text = client.generer_code(test_prompt)
    #         if generated_text:
    #             print("\nRéponse générée:")
    #             print(generated_text)
    #         else:
    #             print("\nAucune réponse générée ou erreur.")
    pass # Garder le bloc if __name__ pour des tests futurs si besoin
