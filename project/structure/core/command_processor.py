"""
Module de traitement des commandes utilisateur
Ce module contient la logique d'analyse et de traitement des commandes saisies par l'utilisateur

Ce module fait partie du package structure.core
"""

import re
from enum import Enum, auto

class ActionCategory(Enum):
    """Catégories d'actions pouvant être effectuées"""
    PROJECT = auto()
    DIRECTORY = auto()
    FILE = auto()
    UI = auto()
    OTHER = auto()

class ProjectAction(Enum):
    """Actions spécifiques aux projets"""
    CREATE = auto()
    DELETE = auto()
    OPEN = auto()
    RENAME = auto()
    LIST = auto()
    SHOW_ACTIONS = auto()  # Pour afficher le panel des actions projet

class DirectoryAction(Enum):
    """Actions spécifiques aux répertoires"""
    CREATE = auto()
    DELETE = auto()
    RENAME = auto()
    MOVE = auto()

class FileAction(Enum):
    """Actions spécifiques aux fichiers"""
    CREATE = auto()
    DELETE = auto()
    OPEN = auto()
    EDIT = auto()

class UIAction(Enum):
    """Actions liées à l'interface utilisateur"""
    SHOW = auto()
    HIDE = auto()
    CLEAR = auto()

class CommandResult:
    """
    Résultat de l'analyse d'une commande utilisateur
    """
    def __init__(self, 
                 category=None, 
                 action=None, 
                 params=None, 
                 is_command=False, 
                 original_text=""):
        self.category = category
        self.action = action
        self.params = params or {}
        self.is_command = is_command
        self.original_text = original_text
        
    @property
    def is_help_command(self):
        """Vérifie si la commande est une demande d'aide"""
        return (self.category == ActionCategory.UI and
                self.action == UIAction.SHOW and
                ("aide" in self.original_text.lower() or
                 "help" in self.original_text.lower()))

    @property
    def is_project_actions_command(self):
        """Vérifie si la commande est pour afficher les actions projet"""
        return (self.category == ActionCategory.PROJECT and
                self.action == ProjectAction.SHOW_ACTIONS)

class ActionType:
    """
    Classe utilitaire pour associer des icônes aux actions
    """
    @staticmethod
    def get_icon_for_action(category, action):
        """
        Retourne l'icône et la couleur correspondant à l'action
        
        Args:
            category: Catégorie de l'action (ActionCategory)
            action: Action spécifique
            
        Returns:
            tuple: (nom_icone, couleur_hexadecimale)
        """
        icon_mapping = {
            ActionCategory.PROJECT: {
                ProjectAction.CREATE: ("folder-plus", "#4CAF50"),
                ProjectAction.DELETE: ("folder-minus", "#F44336"),
                ProjectAction.OPEN: ("folder", "#2196F3"),
                ProjectAction.RENAME: ("edit", "#FF9800"),
                ProjectAction.LIST: ("list", "#9C27B0"),
                ProjectAction.SHOW_ACTIONS: ("folder-cog", "#607D8B"),
            },
            ActionCategory.DIRECTORY: {
                DirectoryAction.CREATE: ("folder-plus", "#4CAF50"),
                DirectoryAction.DELETE: ("folder-minus", "#F44336"),
                DirectoryAction.RENAME: ("edit", "#FF9800"),
                DirectoryAction.MOVE: ("move", "#2196F3"),
            },
            ActionCategory.FILE: {
                FileAction.CREATE: ("file-plus", "#4CAF50"),
                FileAction.DELETE: ("file-minus", "#F44336"),
                FileAction.OPEN: ("file", "#2196F3"),
                FileAction.EDIT: ("edit", "#FF9800"),
            },
            ActionCategory.UI: {
                UIAction.SHOW: ("eye", "#2196F3"),
                UIAction.HIDE: ("eye-off", "#F44336"),
                UIAction.CLEAR: ("trash-2", "#FF9800"),
            },
        }
        
        if category in icon_mapping and action in icon_mapping[category]:
            return icon_mapping[category][action]
        return ("help-circle", "#7F7F7F")  # Icône par défaut


class CommandProcessor:
    """
    Classe responsable de l'analyse et du traitement des commandes utilisateur
    """
    def __init__(self):
        # Définir les patterns pour les différentes actions
        # Format: (regex_pattern, category, action)
        self.action_patterns = [
            # Patterns pour les projets
            (r"créer\s+(le|un)\s+projet", ActionCategory.PROJECT, ProjectAction.CREATE),
            (r"générer\s+(un|le)\s+projet", ActionCategory.PROJECT, ProjectAction.CREATE),
            (r"nouveau\s+projet", ActionCategory.PROJECT, ProjectAction.CREATE),
            (r"supprimer\s+(le|un)\s+projet", ActionCategory.PROJECT, ProjectAction.DELETE),
            (r"ouvrir\s+(le|un)\s+projet", ActionCategory.PROJECT, ProjectAction.OPEN),
            (r"^projet$", ActionCategory.PROJECT, ProjectAction.SHOW_ACTIONS),  # Mot-clé simple "projet"
            # Patterns pour les répertoires
            (r"créer\s+(un|le)\s+(répertoire|dossier)", ActionCategory.DIRECTORY, DirectoryAction.CREATE),
            (r"nouveau\s+(répertoire|dossier)", ActionCategory.DIRECTORY, DirectoryAction.CREATE),
            (r"supprimer\s+(un|le)\s+(répertoire|dossier)", ActionCategory.DIRECTORY, DirectoryAction.DELETE),
            (r"renommer\s+(un|le)\s+(répertoire|dossier)", ActionCategory.DIRECTORY, DirectoryAction.RENAME),
            (r"déplacer\s+(un|le)\s+(répertoire|dossier)", ActionCategory.DIRECTORY, DirectoryAction.MOVE),
            # Patterns pour les fichiers
            (r"créer\s+(un|le)\s+fichier", ActionCategory.FILE, FileAction.CREATE),
            (r"nouveau\s+fichier", ActionCategory.FILE, FileAction.CREATE),
            (r"supprimer\s+(un|le)\s+fichier", ActionCategory.FILE, FileAction.DELETE),
            (r"ouvrir\s+(un|le)\s+fichier", ActionCategory.FILE, FileAction.OPEN),
            (r"éditer\s+(un|le)\s+fichier", ActionCategory.FILE, FileAction.EDIT),
            (r"modifier\s+(un|le)\s+fichier", ActionCategory.FILE, FileAction.EDIT),
            # Patterns pour l'aide
            (r"aide|help", ActionCategory.UI, UIAction.SHOW),
            # Patterns pour effacer le chat
            (r"^(clear|clean|effacer|nettoyer)$", ActionCategory.UI, UIAction.CLEAR),
        ]
        
    def extract_parameters(self, text, category, action):
        """
        Extrait les paramètres pertinents du texte en fonction de la catégorie et de l'action
        
        Args:
            text (str): Le texte de la commande
            category (ActionCategory): La catégorie d'action
            action: L'action spécifique
            
        Returns:
            dict: Les paramètres extraits
        """
        params = {}
        
        # Extraire le nom du projet pour les actions liées aux projets
        if category == ActionCategory.PROJECT:
            # Chercher un nom de projet après "projet"
            match = re.search(r"projet\s+([^,\.;]+)", text)
            if match:
                params["project_name"] = match.group(1).strip()
                
        # Extraire le nom du dossier pour les actions liées aux dossiers
        elif category == ActionCategory.DIRECTORY:
            match = re.search(r"(répertoire|dossier)\s+([^,\.;]+)", text)
            if match:
                params["directory_name"] = match.group(2).strip()
                
        # Extraire le nom du fichier pour les actions liées aux fichiers
        elif category == ActionCategory.FILE:
            match = re.search(r"fichier\s+([^,\.;]+)", text)
            if match:
                params["file_name"] = match.group(1).strip()
                
        return params
        
    def process_command(self, text):
        """
        Analyse le texte pour identifier les commandes et actions
        
        Args:
            text (str): Le texte saisi par l'utilisateur
            
        Returns:
            CommandResult: Le résultat de l'analyse
        """
        if not text:
            return CommandResult()
            
        text_lower = text.lower()
        category = None
        action = None
        
        # Vérifier chaque pattern
        for pattern, cat, act in self.action_patterns:
            if re.search(pattern, text_lower):
                category = cat
                action = act
                break
                
        # Si une action est identifiée, extraire les paramètres
        params = {}
        if category and action:
            params = self.extract_parameters(text, category, action)
            
        # Créer et retourner le résultat
        return CommandResult(
            category=category,
            action=action,
            params=params,
            is_command=(category is not None),
            original_text=text
        )
