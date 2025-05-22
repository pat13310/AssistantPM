from typing import Callable, TypeVar, Generic, Optional, Any

T = TypeVar('T')

class LazyLoadedComponent(Generic[T]):
    """
    Classe générique pour le chargement paresseux des composants.
    Permet de retarder l'initialisation d'un composant jusqu'à ce qu'il soit réellement nécessaire.
    """
    
    def __init__(self, factory: Callable[[], T]):
        """
        Initialise un composant à chargement paresseux.
        
        Args:
            factory: Une fonction qui crée et retourne le composant lorsqu'il est nécessaire
        """
        self._factory = factory
        self._instance: Optional[T] = None
    
    def get(self) -> T:
        """
        Récupère l'instance du composant, en la créant si elle n'existe pas encore.
        
        Returns:
            L'instance du composant
        """
        if self._instance is None:
            self._instance = self._factory()
        return self._instance
    
    def is_initialized(self) -> bool:
        """
        Vérifie si le composant a déjà été initialisé.
        
        Returns:
            True si le composant a déjà été initialisé, False sinon
        """
        return self._instance is not None
    
    def reset(self) -> None:
        """
        Réinitialise le composant, forçant sa recréation lors du prochain accès.
        """
        self._instance = None
