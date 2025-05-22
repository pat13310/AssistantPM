import os
from agent.ChatModule import BaseModule, ChatModule

class DocModule(BaseModule):
    name = "doc"

    # Utiliser un modèle avec une plus grande fenêtre de contexte par défaut
    def __init__(self, api_key, model="gpt-4-turbo-preview", stream=True): 
        self.chat_module = ChatModule(api_key, model, stream)

    def can_handle(self, task: str) -> bool:
        return task.strip().lower().startswith("doc:")

    def handle_async(self, task: str, callback, error_callback, partial_callback=None):
        task = task.strip()

        if task.startswith("doc:auto:"):
            project_path = task.replace("doc:auto:", "").strip()
            context = self._build_context_from_project(project_path)
        else:
            context = task.replace("doc:", "", 1).strip()

        prompt = self._build_prompt(context)
        self.chat_module.handle_async(prompt, callback, error_callback, partial_callback)

    def _build_prompt(self, context: str) -> str:
        return (
            "Tu es un assistant technique expert en HTML et en documentation logicielle. Génère une documentation structurée, professionnelle et esthétique en HTML "
            "pour le projet/code suivant :\n\n"
            f"'''\n{context}\n'''\n\n"
            "Instructions pour la documentation HTML :\n"
            "1.  **Document HTML Complet :** Inclure `<!DOCTYPE html>`, `<html>`, `<head>`, `<body>`.\n"
            "2.  **Titre :** Mettre un titre pertinent dans `<title>` et dans un `<h1>`.\n"
            "3.  **Style CSS Intégré :** Inclure une section `<style>` dans le `<head>` avec du CSS pour rendre la page agréable à lire (choix de police, marges, espacements, couleurs sobres, style pour les titres, paragraphes, listes). NE PAS inclure de CSS pour la coloration syntaxique ici.\n"
            "4.  **Coloration Syntaxique JS (Prism.js) :**\n"
            "    a. Dans le `<head>`, inclure le CSS d'un thème Prism.js depuis un CDN, par exemple : `<link href=\"https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-okaidia.min.css\" rel=\"stylesheet\" />`\n"
            "    b. Pour chaque bloc de code `<pre><code>`, ajouter la classe de langage appropriée, par exemple : `<pre><code class=\"language-python\">...</code></pre>`.\n"
            "    c. Juste avant la balise `</body>`, inclure le script principal de Prism.js et le composant pour Python depuis un CDN : \n"
            "       `<script src=\"https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-core.min.js\"></script>`\n"
            "       `<script src=\"https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/autoloader/prism-autoloader.min.js\"></script>` (L'autoloader simplifie l'ajout de langages)\n"
            "5.  **Structure :** Utiliser des balises sémantiques HTML5 (`<header>`, `<nav>`, `<main>`, `<section>`, `<footer>` si pertinent).\n"
            "6.  **Sections Requises :** Inclure au minimum les sections suivantes avec des titres `<h2>` ou `<h3>` appropriés : Introduction, Architecture/Fonctionnement, Modules/Composants (si pertinent), Dépendances (si pertinent), Blocs de code importants (utiliser `<pre><code class=\"language-...\">`), Conclusion.\n"
            "7.  **Diagrammes Mermaid (Syntaxe Valide!) :** Si pertinent pour illustrer l'architecture, les dépendances ou un flux, inclure un diagramme Mermaid. Utiliser une syntaxe Mermaid **simple et strictement valide** (ex: `graph TD; A-->B; C---D;`) directement à l'intérieur d'un `<pre class=\"mermaid\">`. NE PAS inclure les délimiteurs ```mermaid.\n"
            "8.  **Inclusion de Mermaid.js (TRÈS IMPORTANT) :** IMPÉRATIVEMENT, juste avant la balise de fermeture `</body>` (mais APRÈS les scripts Prism.js), inclure les deux lignes suivantes pour que les diagrammes Mermaid s'affichent :\n"
            "    `<script src=\"https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js\"></script>`\n"
            "    `<script>mermaid.initialize({startOnLoad:true});</script>`\n"
            "9.  **Profondeur de l'Analyse :** Ne te contente pas de décrire le code. Explique la *logique métier*, les *interactions* entre les composants principaux, les *choix de conception* apparents, et les *objectifs* de chaque module ou section de code importante. Sois aussi détaillé que possible.\n"
            "10. **Clarté et Professionnalisme :** Le contenu doit être clair, bien organisé et techniquement précis.\n\n"
            "Génère uniquement le code HTML complet, en étant détaillé et en n'oubliant PAS les étapes 4, 7 (syntaxe Mermaid valide!), et 8."
        )

    def _build_context_from_project(self, path: str) -> str:
        context_parts = []

        # Nom du dossier
        context_parts.append(f"📁 Projet : {os.path.basename(path)}")

        # README
        readme_path = os.path.join(path, "README.md")
        if os.path.exists(readme_path):
            with open(readme_path, encoding="utf-8") as f:
                context_parts.append(f"📄 README.md:\n{f.read()[:2000]}")

        # Arborescence
        context_parts.append("📂 Structure du projet :")
        for root, dirs, files in os.walk(path):
            level = root.replace(path, "").count(os.sep)
            indent = "  " * level
            folder = os.path.basename(root)
            context_parts.append(f"{indent}- {folder}/")
            subindent = "  " * (level + 1)
            for f in files:
                context_parts.append(f"{subindent}- {f}")

        # Fichiers Python (premiers 5, extraits plus longs)
        count = 0
        max_files_to_scan = 5
        max_chars_per_file = 3000
        context_parts.append("\n🧠 Extraits de code :")
        for root, _, files in os.walk(path):
            if count >= max_files_to_scan:
                break
            for f in files:
                if f.endswith(".py") and count < max_files_to_scan:
                    file_path = os.path.join(root, f)
                    try:
                        with open(file_path, encoding="utf-8") as fp:
                            snippet = fp.read()[:max_chars_per_file] 
                            context_parts.append(f"\n### {f} :\n```python\n{snippet}\n```")
                            count += 1
                            if count >= max_files_to_scan:
                                break
                    except Exception as e:
                        continue

        return "\n".join(context_parts)
