import os
import openai

# Configuration initiale du client OpenAI (la clé sera définie plus tard)
# openai.api_key est généralement défini globalement ou passé à chaque requête avec la nouvelle API.
# Pour la nouvelle version de la librairie openai (>=1.0.0), on instancie un client.

def analyze_markdown_with_openai(api_key: str, markdown_content: str) -> str:
    """
    Analyse le contenu Markdown en utilisant l'API OpenAI.

    Args:
        api_key: La clé API OpenAI.
        markdown_content: Le contenu du fichier Markdown à analyser.

    Returns:
        La réponse textuelle de l'analyse d'OpenAI.
    """
    try:
        # Initialisation du client OpenAI (pour les versions >= 1.0.0 de la librairie)
        client = openai.OpenAI(api_key=api_key)

        prompt = f"""
Tu es un expert en architecture logicielle et en gestion de projet. Analyse le contenu Markdown suivant, qui décrit les informations collectées pour un projet logiciel. Identifie les points suivants :

1.  **Cohérence de la Stack Technologique** :
    *   Y a-t-il des choix multiples pour le backend (ex: Node.js, Java, Python en même temps) ou les bases de données (ex: PostgreSQL, MongoDB, MySQL en même temps) ? Si oui, cela est-il justifié (par exemple, pour des microservices distincts) ou cela nécessite-t-il une clarification ou une décision ?
    *   Les technologies listées sont-elles adaptées aux objectifs du projet ?

2.  **Adéquation des Outils de Test** :
    *   Les outils de test mentionnés (ex: Jest, Mocha) sont-ils cohérents avec la stack technologique principale envisagée (backend, frontend) ?

3.  **Impact des Contraintes sur la Complexité** :
    *   Si des contraintes fortes comme un "Délai serré" sont mentionnées, les choix architecturaux (ex: microservices) ou technologiques (ex: stack polyglotte) sont-ils réalistes ? Y a-t-il des risques potentiels ?

4.  **Complétude et Clarté des Sections Clés** :
    *   La section sur la sécurité de l'application est-elle suffisamment détaillée ou reste-t-elle superficielle (ex: se limitant à la validation des entrées) ? Quels aspects importants pourraient manquer ?
    *   Les objectifs du projet sont-ils clairs et mesurables ?
    *   Les fonctionnalités essentielles sont-elles bien définies ?

5.  **Suggestions Générales d'Amélioration** :
    *   Y a-t-il d'autres incohérences, ambiguïtés, ou points faibles dans le document ?
    *   Quelles suggestions ferais-tu pour améliorer la clarté, la complétude ou la cohérence de ce document ?

Voici le contenu Markdown à analyser :
---
{markdown_content}
---

Fournis ton analyse de manière structurée, en abordant chacun des points ci-dessus.
Sois précis et donne des exemples tirés du texte si possible.
        """

        response = client.chat.completions.create(
            model="gpt-4-turbo", # ou "gpt-3.5-turbo" si gpt-4 n'est pas accessible ou pour réduire les coûts
            messages=[
                {"role": "system", "content": "Tu es un assistant expert en analyse de documents techniques et en architecture logicielle."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5, # Un peu de créativité mais pas trop pour une analyse
            max_tokens=2000  # Augmenter si l'analyse est très détaillée
        )
        
        if response.choices and response.choices[0].message:
            return response.choices[0].message.content.strip()
        else:
            return "Aucune réponse reçue d'OpenAI ou format de réponse inattendu."

    except openai.APIError as e:
        return f"Erreur de l'API OpenAI: {e}"
    except Exception as e:
        return f"Une erreur inattendue est survenue: {e}"

if __name__ == "__main__":
    api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        print("Erreur : La variable d'environnement OPENAI_API_KEY n'est pas définie.")
        print("Veuillez la définir avant de lancer le script.")
        print("Exemple (Linux/macOS): export OPENAI_API_KEY='votre_cle_api'")
        print("Exemple (Windows CMD): set OPENAI_API_KEY=votre_cle_api")
        print("Exemple (Windows PowerShell): $env:OPENAI_API_KEY='votre_cle_api'")
    else:
        markdown_file_path = os.path.join("context", "context.md")

        if not os.path.exists(markdown_file_path):
            print(f"Erreur : Le fichier Markdown '{markdown_file_path}' n'a pas été trouvé.")
        else:
            try:
                with open(markdown_file_path, "r", encoding="utf-8") as f:
                    markdown_content_to_analyze = f.read()
                
                print(f"Analyse du fichier '{markdown_file_path}' avec OpenAI en cours...")
                analysis_result = analyze_markdown_with_openai(api_key, markdown_content_to_analyze)
                
                print("\n===== Analyse de Cohérence par OpenAI =====")
                print(analysis_result)
                print("==========================================")

            except Exception as e:
                print(f"Erreur lors de la lecture du fichier ou de l'exécution de l'analyse : {e}")
