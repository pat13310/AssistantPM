from agent.BaseModule import BaseModule
from agent.ChatModule import ChatModule


class CodeRefactorModule(BaseModule):
    name = "refactor"

    def __init__(self, api_key, model="gpt-4", stream=True):
        self.chat = ChatModule(api_key, model, stream)

    def can_handle(self, task: str) -> bool:
        return task.strip().lower().startswith("refactor:")

    def handle_async(self, task: str, callback, error_callback, partial_callback=None):
        raw_input = task[len("refactor:"):].strip()

        # Séparation consigne / code
        if "::" in raw_input:
            instruction, code = raw_input.split("::", 1)
        else:
            instruction = "Refactorise le code suivant de manière propre."
            code = raw_input

        prompt = (
            "Tu es un assistant expert Python. Voici une consigne de refactorisation :\n"
            f"- 🧾 Instruction : {instruction.strip()}\n\n"
            f"Voici le code source à améliorer/refactoriser :\n```python\n{code.strip()}\n```\n\n"
            "Renvoie uniquement le code refactorisé dans un bloc Markdown Python."
        )

        self.chat.handle_async(prompt, callback, error_callback, partial_callback)
