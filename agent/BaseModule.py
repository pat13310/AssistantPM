from abc import ABC, abstractmethod


class BaseModule(ABC):
    """
    Classe de base pour tous les modules de l'agent.
    """

    name = "base"  # Nom du module (à redéfinir)

    @abstractmethod
    def can_handle(self, task: str) -> bool:
        """
        Détermine si ce module peut prendre en charge la tâche donnée.
        """
        pass

    @abstractmethod
    def handle_async(
        self,
        task: str,
        callback: callable,
        error_callback: callable,
        partial_callback: callable = None
    ) -> None:
        """
        Exécute une tâche de manière asynchrone. Peut émettre des fragments via `partial_callback`.
        """
        pass
