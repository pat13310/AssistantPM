"""
Module définissant les types d'actions possibles dans l'application AssistantPM.
Ce module contient des énumérations pour les différentes actions sur les répertoires, fichiers et projets.
"""

from enum import Enum, auto

class ActionCategory(Enum):
    """Catégorie principale d'action"""
    DIRECTORY = auto()  # Actions sur les répertoires
    FILE = auto()       # Actions sur les fichiers
    PROJECT = auto()    # Actions sur les projets
    SYSTEM = auto()     # Actions système
    UI = auto()         # Actions sur l'interface utilisateur
    DATABASE = auto()   # Actions sur la base de données
    NETWORK = auto()    # Actions réseau
    SECURITY = auto()   # Actions de sécurité


class DirectoryAction(Enum):
    """Actions possibles sur les répertoires"""
    CREATE = auto()         # Créer un répertoire
    DELETE = auto()         # Supprimer un répertoire
    RENAME = auto()         # Renommer un répertoire
    MOVE = auto()           # Déplacer un répertoire
    COPY = auto()           # Copier un répertoire
    LIST = auto()           # Lister le contenu d'un répertoire
    ARCHIVE = auto()        # Archiver un répertoire
    EXTRACT = auto()        # Extraire une archive
    CHANGE_PERMISSIONS = auto()  # Modifier les permissions d'un répertoire
    CHANGE_OWNER = auto()   # Modifier le propriétaire d'un répertoire
    SEARCH = auto()         # Rechercher dans un répertoire
    NAVIGATE = auto()       # Naviguer dans l'arborescence des répertoires
    REFRESH = auto()        # Rafraîchir la vue d'un répertoire
    SELECT = auto()         # Sélectionner un répertoire
    EXPAND = auto()         # Développer un répertoire dans l'arborescence
    COLLAPSE = auto()       # Réduire un répertoire dans l'arborescence
    SHOW_PROPERTIES = auto()  # Afficher les propriétés d'un répertoire


class FileAction(Enum):
    """Actions possibles sur les fichiers"""
    CREATE = auto()         # Créer un fichier
    DELETE = auto()         # Supprimer un fichier
    RENAME = auto()         # Renommer un fichier
    MOVE = auto()           # Déplacer un fichier
    COPY = auto()           # Copier un fichier
    OPEN = auto()           # Ouvrir un fichier
    EDIT = auto()           # Éditer un fichier
    SAVE = auto()           # Enregistrer un fichier
    SAVE_AS = auto()        # Enregistrer un fichier sous un nouveau nom
    CLOSE = auto()          # Fermer un fichier
    PRINT = auto()          # Imprimer un fichier
    EXPORT = auto()         # Exporter un fichier dans un autre format
    IMPORT = auto()         # Importer un fichier
    CHANGE_PERMISSIONS = auto()  # Modifier les permissions d'un fichier
    CHANGE_OWNER = auto()   # Modifier le propriétaire d'un fichier
    SEARCH = auto()         # Rechercher dans un fichier
    COMPARE = auto()        # Comparer deux fichiers
    SHOW_PROPERTIES = auto()  # Afficher les propriétés d'un fichier
    PREVIEW = auto()        # Prévisualiser un fichier
    DOWNLOAD = auto()       # Télécharger un fichier
    UPLOAD = auto()         # Téléverser un fichier
    ENCRYPT = auto()        # Chiffrer un fichier
    DECRYPT = auto()        # Déchiffrer un fichier


class ProjectAction(Enum):
    """Actions possibles sur les projets"""
    CREATE = auto()         # Créer un projet
    DELETE = auto()         # Supprimer un projet
    RENAME = auto()         # Renommer un projet
    OPEN = auto()           # Ouvrir un projet
    CLOSE = auto()          # Fermer un projet
    SAVE = auto()           # Enregistrer un projet
    SAVE_AS = auto()        # Enregistrer un projet sous un nouveau nom
    BUILD = auto()          # Compiler un projet
    RUN = auto()            # Exécuter un projet
    DEBUG = auto()          # Déboguer un projet
    TEST = auto()           # Tester un projet
    DEPLOY = auto()         # Déployer un projet
    ARCHIVE = auto()        # Archiver un projet
    EXPORT = auto()         # Exporter un projet
    IMPORT = auto()         # Importer un projet
    ADD_FILE = auto()       # Ajouter un fichier au projet
    REMOVE_FILE = auto()    # Retirer un fichier du projet
    ADD_DIRECTORY = auto()  # Ajouter un répertoire au projet
    REMOVE_DIRECTORY = auto()  # Retirer un répertoire du projet
    CONFIGURE = auto()      # Configurer un projet
    SHOW_PROPERTIES = auto()  # Afficher les propriétés d'un projet
    GENERATE_DOCUMENTATION = auto()  # Générer la documentation d'un projet
    ANALYZE_CODE = auto()   # Analyser le code d'un projet
    REFACTOR = auto()       # Refactoriser le code d'un projet
    MANAGE_DEPENDENCIES = auto()  # Gérer les dépendances d'un projet
    VERSION_CONTROL = auto()  # Gérer le contrôle de version d'un projet


class SystemAction(Enum):
    """Actions système possibles"""
    SHUTDOWN = auto()       # Éteindre le système
    RESTART = auto()        # Redémarrer le système
    SLEEP = auto()          # Mettre le système en veille
    HIBERNATE = auto()      # Mettre le système en hibernation
    LOCK = auto()           # Verrouiller le système
    LOG_OUT = auto()        # Se déconnecter du système
    UPDATE = auto()         # Mettre à jour le système
    BACKUP = auto()         # Sauvegarder le système
    RESTORE = auto()        # Restaurer le système
    INSTALL = auto()        # Installer un logiciel
    UNINSTALL = auto()      # Désinstaller un logiciel
    CONFIGURE = auto()      # Configurer le système
    MONITOR = auto()        # Surveiller les ressources système
    CLEAN = auto()          # Nettoyer le système


class UIAction(Enum):
    """Actions possibles sur l'interface utilisateur"""
    SHOW = auto()           # Afficher un élément d'interface
    HIDE = auto()           # Masquer un élément d'interface
    ENABLE = auto()         # Activer un élément d'interface
    DISABLE = auto()        # Désactiver un élément d'interface
    FOCUS = auto()          # Donner le focus à un élément d'interface
    BLUR = auto()           # Retirer le focus d'un élément d'interface
    RESIZE = auto()         # Redimensionner un élément d'interface
    MOVE = auto()           # Déplacer un élément d'interface
    REFRESH = auto()        # Rafraîchir un élément d'interface
    SCROLL = auto()         # Faire défiler un élément d'interface
    ZOOM_IN = auto()        # Zoomer sur un élément d'interface
    ZOOM_OUT = auto()       # Dézoomer sur un élément d'interface
    RESET_ZOOM = auto()     # Réinitialiser le zoom d'un élément d'interface
    TOGGLE = auto()         # Basculer l'état d'un élément d'interface
    SELECT = auto()         # Sélectionner un élément d'interface
    DESELECT = auto()       # Désélectionner un élément d'interface
    DRAG = auto()           # Faire glisser un élément d'interface
    DROP = auto()           # Déposer un élément d'interface
    CLICK = auto()          # Cliquer sur un élément d'interface
    DOUBLE_CLICK = auto()   # Double-cliquer sur un élément d'interface
    RIGHT_CLICK = auto()    # Cliquer avec le bouton droit sur un élément d'interface
    HOVER = auto()          # Survoler un élément d'interface
    CHANGE_THEME = auto()   # Changer le thème de l'interface
    CUSTOMIZE = auto()      # Personnaliser l'interface


class DatabaseAction(Enum):
    """Actions possibles sur la base de données"""
    CONNECT = auto()        # Se connecter à une base de données
    DISCONNECT = auto()     # Se déconnecter d'une base de données
    CREATE = auto()         # Créer une base de données
    DELETE = auto()         # Supprimer une base de données
    BACKUP = auto()         # Sauvegarder une base de données
    RESTORE = auto()        # Restaurer une base de données
    QUERY = auto()          # Exécuter une requête sur une base de données
    INSERT = auto()         # Insérer des données dans une base de données
    UPDATE = auto()         # Mettre à jour des données dans une base de données
    DELETE_DATA = auto()    # Supprimer des données d'une base de données
    EXPORT = auto()         # Exporter des données d'une base de données
    IMPORT = auto()         # Importer des données dans une base de données
    OPTIMIZE = auto()       # Optimiser une base de données
    REPAIR = auto()         # Réparer une base de données
    MIGRATE = auto()        # Migrer une base de données


class NetworkAction(Enum):
    """Actions possibles sur le réseau"""
    CONNECT = auto()        # Se connecter à un réseau
    DISCONNECT = auto()     # Se déconnecter d'un réseau
    SCAN = auto()           # Scanner un réseau
    PING = auto()           # Envoyer un ping sur un réseau
    DOWNLOAD = auto()       # Télécharger depuis un réseau
    UPLOAD = auto()         # Téléverser vers un réseau
    SHARE = auto()          # Partager sur un réseau
    UNSHARE = auto()        # Arrêter de partager sur un réseau
    CONFIGURE = auto()      # Configurer un réseau
    MONITOR = auto()        # Surveiller un réseau
    DIAGNOSE = auto()       # Diagnostiquer un problème réseau
    FIREWALL = auto()       # Configurer le pare-feu réseau


class SecurityAction(Enum):
    """Actions possibles sur la sécurité"""
    LOGIN = auto()          # Se connecter
    LOGOUT = auto()         # Se déconnecter
    CHANGE_PASSWORD = auto()  # Changer de mot de passe
    RESET_PASSWORD = auto()  # Réinitialiser un mot de passe
    CREATE_USER = auto()    # Créer un utilisateur
    DELETE_USER = auto()    # Supprimer un utilisateur
    MODIFY_USER = auto()    # Modifier un utilisateur
    GRANT_PERMISSION = auto()  # Accorder une permission
    REVOKE_PERMISSION = auto()  # Révoquer une permission
    ENCRYPT = auto()        # Chiffrer des données
    DECRYPT = auto()        # Déchiffrer des données
    AUDIT = auto()          # Auditer la sécurité
    SCAN_VULNERABILITY = auto()  # Scanner les vulnérabilités
    BACKUP_CREDENTIALS = auto()  # Sauvegarder les identifiants
    RESTORE_CREDENTIALS = auto()  # Restaurer les identifiants


class ActionType:
    """Classe utilitaire pour accéder facilement aux différents types d'actions"""
    
    @staticmethod
    def get_action_by_name(category_name, action_name):
        """Obtient une action par son nom et sa catégorie
        
        Args:
            category_name (str): Nom de la catégorie d'action
            action_name (str): Nom de l'action
            
        Returns:
            Enum: L'action correspondante ou None si non trouvée
        """
        category_map = {
            "directory": DirectoryAction,
            "file": FileAction,
            "project": ProjectAction,
            "system": SystemAction,
            "ui": UIAction,
            "database": DatabaseAction,
            "network": NetworkAction,
            "security": SecurityAction
        }
        
        category = category_map.get(category_name.lower())
        if not category:
            return None
            
        try:
            return category[action_name.upper()]
        except KeyError:
            return None
    
    @staticmethod
    def get_icon_for_action(category, action):
        """Obtient l'icône correspondant à une action
        
        Args:
            category (ActionCategory): Catégorie de l'action
            action (Enum): Action spécifique
            
        Returns:
            tuple: (nom_icone, couleur_icone) ou (None, None) si non trouvée
        """
        # Mapping des icônes par catégorie et action
        icon_map = {
            # Répertoires
            (ActionCategory.DIRECTORY, DirectoryAction.CREATE): ("folder-plus", "#4CAF50"),
            (ActionCategory.DIRECTORY, DirectoryAction.DELETE): ("folder-minus", "#F44336"),
            (ActionCategory.DIRECTORY, DirectoryAction.RENAME): ("folder-edit", "#2196F3"),
            (ActionCategory.DIRECTORY, DirectoryAction.MOVE): ("folder-move", "#FF9800"),
            (ActionCategory.DIRECTORY, DirectoryAction.COPY): ("folder-copy", "#9C27B0"),
            (ActionCategory.DIRECTORY, DirectoryAction.LIST): ("folder-open", "#607D8B"),
            (ActionCategory.DIRECTORY, DirectoryAction.ARCHIVE): ("folder-zip", "#795548"),
            (ActionCategory.DIRECTORY, DirectoryAction.EXTRACT): ("folder-unzip", "#8BC34A"),
            
            # Fichiers
            (ActionCategory.FILE, FileAction.CREATE): ("file-plus", "#4CAF50"),
            (ActionCategory.FILE, FileAction.DELETE): ("file-minus", "#F44336"),
            (ActionCategory.FILE, FileAction.RENAME): ("file-edit", "#2196F3"),
            (ActionCategory.FILE, FileAction.MOVE): ("file-move", "#FF9800"),
            (ActionCategory.FILE, FileAction.COPY): ("file-copy", "#9C27B0"),
            (ActionCategory.FILE, FileAction.OPEN): ("file-open", "#607D8B"),
            (ActionCategory.FILE, FileAction.EDIT): ("file-edit", "#2196F3"),
            (ActionCategory.FILE, FileAction.SAVE): ("file-save", "#4CAF50"),
            
            # Projets
            (ActionCategory.PROJECT, ProjectAction.CREATE): ("project-plus", "#4CAF50"),
            (ActionCategory.PROJECT, ProjectAction.DELETE): ("project-minus", "#F44336"),
            (ActionCategory.PROJECT, ProjectAction.RENAME): ("project-edit", "#2196F3"),
            (ActionCategory.PROJECT, ProjectAction.OPEN): ("project-open", "#607D8B"),
            (ActionCategory.PROJECT, ProjectAction.BUILD): ("project-build", "#FF9800"),
            (ActionCategory.PROJECT, ProjectAction.RUN): ("project-run", "#4CAF50"),
            (ActionCategory.PROJECT, ProjectAction.DEBUG): ("project-debug", "#2196F3"),
            (ActionCategory.PROJECT, ProjectAction.TEST): ("project-test", "#9C27B0"),
            
            # Système
            (ActionCategory.SYSTEM, SystemAction.SHUTDOWN): ("power", "#F44336"),
            (ActionCategory.SYSTEM, SystemAction.RESTART): ("refresh", "#FF9800"),
            (ActionCategory.SYSTEM, SystemAction.UPDATE): ("update", "#4CAF50"),
            (ActionCategory.SYSTEM, SystemAction.BACKUP): ("backup", "#2196F3"),
            
            # Interface utilisateur
            (ActionCategory.UI, UIAction.SHOW): ("eye", "#4CAF50"),
            (ActionCategory.UI, UIAction.HIDE): ("eye-off", "#F44336"),
            (ActionCategory.UI, UIAction.ENABLE): ("check-circle", "#4CAF50"),
            (ActionCategory.UI, UIAction.DISABLE): ("ban", "#F44336"),
            
            # Base de données
            (ActionCategory.DATABASE, DatabaseAction.CONNECT): ("database-connect", "#4CAF50"),
            (ActionCategory.DATABASE, DatabaseAction.DISCONNECT): ("database-disconnect", "#F44336"),
            (ActionCategory.DATABASE, DatabaseAction.QUERY): ("database-search", "#2196F3"),
            
            # Réseau
            (ActionCategory.NETWORK, NetworkAction.CONNECT): ("wifi", "#4CAF50"),
            (ActionCategory.NETWORK, NetworkAction.DISCONNECT): ("wifi-off", "#F44336"),
            (ActionCategory.NETWORK, NetworkAction.DOWNLOAD): ("download", "#2196F3"),
            (ActionCategory.NETWORK, NetworkAction.UPLOAD): ("upload", "#FF9800"),
            
            # Sécurité
            (ActionCategory.SECURITY, SecurityAction.LOGIN): ("login", "#4CAF50"),
            (ActionCategory.SECURITY, SecurityAction.LOGOUT): ("logout", "#F44336"),
            (ActionCategory.SECURITY, SecurityAction.ENCRYPT): ("lock", "#2196F3"),
            (ActionCategory.SECURITY, SecurityAction.DECRYPT): ("unlock", "#FF9800"),
        }
        
        return icon_map.get((category, action), (None, None))


# Exemple d'utilisation
if __name__ == "__main__":
    # Obtenir une action par son nom
    create_dir_action = ActionType.get_action_by_name("directory", "create")
    print(f"Action: {create_dir_action}")
    
    # Obtenir l'icône pour une action
    icon_name, icon_color = ActionType.get_icon_for_action(ActionCategory.DIRECTORY, DirectoryAction.CREATE)
    print(f"Icône: {icon_name}, Couleur: {icon_color}")
