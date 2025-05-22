import os
import re
from agent.BaseModule import BaseModule

class MarkdownCoherenceAgent(BaseModule):
    """
    Agent chargé d'analyser un fichier Markdown (généralement context.md)
    pour vérifier la cohérence des informations qu'il contient.
    """

    name = "markdown_coherence_analyzer"

    def can_handle(self, task: str) -> bool:
        """
        Détermine si ce module peut prendre en charge la tâche donnée.
        Pour l'instant, on suppose qu'il est appelé directement pour la bonne tâche.
        """
        keywords = ["analyser markdown", "cohérence contexte", "verifier markdown", "cohérence md"]
        return any(keyword in task.lower() for keyword in keywords)

    async def handle_async(
        self,
        task: str, # La tâche pourrait inclure le chemin du fichier ou des paramètres spécifiques
        callback: callable,
        error_callback: callable,
        partial_callback: callable = None
    ) -> None:
        """
        Exécute l'analyse de cohérence du fichier Markdown.
        """
        # Pour l'instant, nous supposons que le fichier à analyser est toujours 'context/context.md'
        # On pourrait rendre cela configurable via le paramètre 'task'
        markdown_file_path = os.path.join("context", "context.md")

        if not os.path.exists(markdown_file_path):
            error_callback(f"Le fichier Markdown '{markdown_file_path}' n'a pas été trouvé.")
            return

        try:
            with open(markdown_file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            error_callback(f"Erreur lors de la lecture du fichier '{markdown_file_path}': {e}")
            return

        analysis_results = [] # Liste pour stocker les messages/objets d'analyse

        # --- 1. Parsing du Markdown ---
        parsed_data = self._parse_markdown(content)
        if not parsed_data:
            error_callback("Erreur lors du parsing du fichier Markdown. Le contenu est peut-être mal formaté.")
            return
        
        # --- 2. Application des règles de cohérence ---
        # Chaque méthode _check_... retournera une liste d'objets ou de chaînes
        tech_stack_issues = self._check_tech_stack_coherence(parsed_data)
        analysis_results.extend(tech_stack_issues)
        
        testing_tools_issues = self._check_testing_tools_coherence(parsed_data)
        analysis_results.extend(testing_tools_issues)
        
        constraints_complexity_issues = self._check_constraints_vs_complexity(parsed_data)
        analysis_results.extend(constraints_complexity_issues)
        
        security_completeness_issues = self._check_security_completeness(parsed_data)
        analysis_results.extend(security_completeness_issues)

        # Si analysis_results ne contient que des chaînes (pas d'objets structurés pour les problèmes)
        # et qu'elle est vide, alors on ajoute le message par défaut.
        # Si elle contient des objets, on suppose que les problèmes sont déjà listés.
        is_only_strings = all(isinstance(item, str) for item in analysis_results)
        if not analysis_results or (is_only_strings and not any(analysis_results)):
             analysis_results.append({
                "type": "info",
                "message": "Aucune incohérence majeure détectée. Le document semble globalement cohérent."
            })
        elif is_only_strings and len(analysis_results) == 1 and analysis_results[0] == "Aucune incohérence majeure détectée. Le document semble globalement cohérent.":
            # Cas où une règle n'a rien trouvé et a ajouté le message par défaut, mais d'autres ont trouvé des problèmes.
            # On le transforme en objet pour la cohérence.
            analysis_results = [res for res in analysis_results if isinstance(res, dict)] # Garder que les dicts
            if not any(isinstance(item, dict) for item in analysis_results): # S'il ne reste plus rien
                 analysis_results.append({
                    "type": "info",
                    "message": "Aucune incohérence majeure détectée. Le document semble globalement cohérent."
                })


        callback(analysis_results)

    def _parse_markdown(self, content: str) -> dict:
        """
        Parse le contenu Markdown et extrait les informations structurées.
        Retourne un dictionnaire ou None en cas d'erreur.
        """
        data = {"project_name": None, "phases": []}
        current_phase = None
        current_question = None

        lines = content.splitlines()

        for line in lines:
            line = line.strip()
            if not line:
                continue

            project_match = re.match(r"^# Projet : (.+)", line)
            if project_match:
                data["project_name"] = project_match.group(1).strip()
                continue

            phase_match = re.match(r"^## Phase : (.+)", line)
            if phase_match:
                current_phase = {"title": phase_match.group(1).strip(), "questions": []}
                data["phases"].append(current_phase)
                current_question = None # Réinitialiser la question actuelle
                continue
            
            question_match = re.match(r"^### (.+)", line)
            if question_match and current_phase is not None:
                current_question = {"text": question_match.group(1).strip(), "response": ""}
                current_phase["questions"].append(current_question)
                continue

            # Si ce n'est ni un projet, ni une phase, ni une question, c'est une réponse (ou une ligne vide)
            if current_question is not None:
                # Gérer les réponses sur plusieurs lignes
                if current_question["response"]:
                    current_question["response"] += "\n" + line
                else:
                    current_question["response"] = line
        
        if not data["project_name"] and not data["phases"]: # Vérification basique si quelque chose a été parsé
             return None
        return data

    def _find_response_for_question(self, parsed_data: dict, phase_title_keyword: str, question_keyword: str) -> str | None:
        """Utilitaire pour trouver une réponse spécifique."""
        for phase in parsed_data.get("phases", []):
            if phase_title_keyword.lower() in phase.get("title", "").lower():
                for q_a in phase.get("questions", []):
                    if question_keyword.lower() in q_a.get("text", "").lower():
                        return q_a.get("response", "")
        return None

    def _check_tech_stack_coherence(self, parsed_data: dict) -> list:
        """Vérifie la cohérence de la stack technologique."""
        results = []
        tech_response = self._find_response_for_question(parsed_data, "conception", "technologies et frameworks")
        
        if tech_response:
            backends = []
            databases = []

            # Simplistic check for multiple backends/databases
            # This could be improved with more sophisticated keyword matching
            if "node.js" in tech_response.lower(): backends.append("Node.js")
            if "java" in tech_response.lower() or "spring" in tech_response.lower(): backends.append("Java/Spring")
            if "python" in tech_response.lower() or "django" in tech_response.lower(): backends.append("Python/Django")
            
            if "postgresql" in tech_response.lower(): databases.append("PostgreSQL")
            if "mongodb" in tech_response.lower(): databases.append("MongoDB")
            if "mysql" in tech_response.lower(): databases.append("MySQL")

            if len(backends) > 1:
                results.append({
                    "type": "decision_needed",
                    "category": "tech_stack_backend",
                    "message": f"Multiples technologies backend listées : {', '.join(backends)}.",
                    "options": backends,
                    "details": "Veuillez sélectionner la technologie backend principale ou confirmer si toutes sont nécessaires (ex: microservices distincts).",
                    "phase": "Conception",
                    "question": "Quelles technologies et frameworks utiliser?"
                })
            if len(databases) > 1:
                results.append({
                    "type": "decision_needed",
                    "category": "tech_stack_database",
                    "message": f"Multiples SGBD listés : {', '.join(databases)}.",
                    "options": databases,
                    "details": "Veuillez sélectionner le SGBD principal ou confirmer si tous sont nécessaires (ex: besoins de données différents).",
                    "phase": "Conception",
                    "question": "Quelles technologies et frameworks utiliser?"
                })
        return results

    def _check_testing_tools_coherence(self, parsed_data: dict) -> list:
        """Vérifie la cohérence entre les outils de test et la stack."""
        results = []
        test_tools_response = self._find_response_for_question(parsed_data, "tests", "outils de test")
        tech_response = self._find_response_for_question(parsed_data, "conception", "technologies et frameworks")

        if test_tools_response and tech_response:
            js_test_tools_present = "jest" in test_tools_response.lower() or "mocha" in test_tools_response.lower()
            
            is_nodejs_backend = "node.js" in tech_response.lower()
            # On pourrait aussi vérifier la présence d'un frontend JS si cette info était disponible

            if js_test_tools_present and not is_nodejs_backend:
                # Check if other backends are primary
                is_java_primary = "java" in tech_response.lower() or "spring" in tech_response.lower()
                is_python_primary = "python" in tech_response.lower() or "django" in tech_response.lower()
                
                if (is_java_primary and not is_nodejs_backend) or (is_python_primary and not is_nodejs_backend) :
                     results.append({
                         "type": "warning",
                         "category": "testing_tools_mismatch",
                         "message": "Des outils de test JavaScript (Jest/Mocha) sont listés, mais la stack technologique principale ne semble pas être Node.js.",
                         "details": "Vérifiez l'adéquation de ces outils ou si un frontend JavaScript est concerné et non mentionné explicitement dans la stack backend.",
                         "phase": "Tests",
                         "question": "Quels outils de test utiliser?",
                         "suggested_actions": ["Confirmer la pertinence des outils", "Mettre à jour la stack technologique", "Ignorer"]
                     })
        return results

    def _check_constraints_vs_complexity(self, parsed_data: dict) -> list:
        """Vérifie l'impact des contraintes sur les choix complexes."""
        results = []
        constraints_response = self._find_response_for_question(parsed_data, "analyse des besoins", "contraintes techniques ou organisationnelles")
        architecture_response = self._find_response_for_question(parsed_data, "conception", "architecture logicielle")
        tech_response = self._find_response_for_question(parsed_data, "conception", "technologies et frameworks")

        is_tight_deadline = False
        if constraints_response and "délai serré" in constraints_response.lower():
            is_tight_deadline = True

        is_microservices = False
        if architecture_response and "microservices" in architecture_response.lower():
            is_microservices = True
        
        multiple_techs = False
        if tech_response:
            backends_count = sum(1 for be in ["node.js", "java", "python"] if be in tech_response.lower())
            db_count = sum(1 for db in ["postgresql", "mongodb", "mysql"] if db in tech_response.lower())
            if backends_count > 1 or db_count > 1:
                multiple_techs = True

        if is_tight_deadline and (is_microservices or multiple_techs):
            warning = "Suggestion : La contrainte 'Délai serré' est mentionnée. "
            if is_microservices:
                warning += "L'architecture microservices peut ajouter de la complexité. "
            if multiple_techs:
                warning += "L'utilisation de multiples technologies backend/DB peut également impacter les délais. "
            warning += "Évaluez les risques et envisagez une approche par étapes (MVP) si nécessaire."
            results.append({
                "type": "suggestion",
                "category": "constraints_complexity_impact",
                "message": warning,
                "phase_constraints": "Analyse des Besoins", # Approximatif, pourrait être plus précis
                "phase_complexity_drivers": "Conception",
                "suggested_actions": ["Réévaluer les choix techniques", "Planifier un MVP", "Accepter le risque"]
            })
        return results

    def _check_security_completeness(self, parsed_data: dict) -> list:
        """Vérifie si la section sécurité est suffisamment détaillée."""
        results = []
        security_response = self._find_response_for_question(parsed_data, "développement", "sécurité de l'application")

        if security_response:
            # Exemple de vérification très simple. Pourrait être amélioré.
            superficial_keywords = ["validation des entrées", "validation entrées"]
            is_superficial = any(keyword in security_response.lower() for keyword in superficial_keywords)
            
            more_robust_keywords = ["owasp", "chiffrement", "authentification forte", "tests de pénétration", "pare-feu"]
            has_robust_terms = any(keyword in security_response.lower() for keyword in more_robust_keywords)

            if is_superficial and not has_robust_terms and len(security_response.split()) < 15 : # Si réponse courte et superficielle
                results.append({
                    "type": "suggestion",
                    "category": "security_superficial",
                    "message": "La section sur la sécurité semble se limiter à des aspects basiques (ex: validation des entrées).",
                    "details": "Envisagez de détailler davantage la stratégie de sécurité (ex: OWASP Top 10, gestion des secrets, tests de sécurité, chiffrement des données sensibles, etc.).",
                    "phase": "Développement",
                    "question": "Comment garantir la sécurité de l'application?",
                    "suggested_actions": ["Détailler la section sécurité", "Planifier des tests de sécurité", "Ignorer pour l'instant"]
                })
        return results

# Exemple d'utilisation (pourrait être dans un fichier de test comme test_agent.py)
if __name__ == '__main__':
    import asyncio

    # Créer un faux fichier context.md pour le test
    mock_context_content = """# Projet : Moclearn Projet Test
## Phase : Analyse des Besoins
### Quelles sont les contraintes techniques ou organisationnelles?
Délai serré
## Phase : Conception
### Quelle architecture logicielle adopter pour le projet?
Architecture microservices
### Quelles technologies et frameworks utiliser?
Backend: Node.js, Java Spring
Base de données: PostgreSQL, MongoDB
## Phase : Développement
### Comment garantir la sécurité de l'application?
Validation des entrées utilisateur.
## Phase : Tests
### Quels outils de test utiliser?
Jest, Mocha pour tests unitaires
"""
    os.makedirs("context", exist_ok=True)
    with open("context/context.md", "w", encoding="utf-8") as f:
        f.write(mock_context_content)

    agent = MarkdownCoherenceAgent()

    async def run_test():
        def my_callback(result):
            print("Résultat de l'analyse :")
            if isinstance(result, list):
                for item in result:
                    print(f"- {item}")
            else:
                print(result)

        def my_error_callback(error):
            print(f"Erreur de l'agent : {error}")

        if agent.can_handle("analyser markdown de contexte"):
            await agent.handle_async("analyser markdown de contexte", my_callback, my_error_callback)
        else:
            print("L'agent ne peut pas gérer cette tâche.")

    asyncio.run(run_test())
