import json
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Optional, List, Dict, Any
from PySide6.QtCore import QObject, Signal

# Enums pour les états
class ServerStatus(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"

class UIMode(Enum):
    CHAT = auto()
    PROJECT = auto()
    SETTINGS = auto()


@dataclass
class ProjectConfig:
    """Configuration d'un projet"""

    name: str = ""
    path: str = ""
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_modified: float = field(default_factory=lambda: time.time())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit la configuration en dictionnaire"""
        return {
            "name": self.name,
            "path": self.path,
            "description": self.description,
            "metadata": self.metadata,
            "last_modified": self.last_modified
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectConfig':
        """Crée une instance à partir d'un dictionnaire"""
        return cls(
            name=data.get("name", ""),
            path=data.get("path", ""),
            description=data.get("description", ""),
            metadata=data.get("metadata", {}),
            last_modified=data.get("last_modified", time.time())
        )
    
    def update_modification_time(self):
        """Met à jour l'horodatage de modification"""
        self.last_modified = time.time()


@dataclass
class Conversation:
    """Structure d'une conversation"""

    id: str
    title: str
    messages: List[Any] = field(default_factory=list)


@dataclass
class ChatMessage:
    """Structure d'un message chat"""

    id: str
    content: str
    role: str  # 'user' ou 'assistant'
    timestamp: float


@dataclass
class ServerState:
    """État du serveur"""

    is_connected: bool = False
    url: str = ""
    status: str = "disconnected"
    last_error: Optional[str] = None
    message: str = ""
    selected_model: str = ""
    
    def set_connected(self, message: str = "Connexion établie"):
        """Définit l'état comme connecté"""
        self.is_connected = True
        self.status = ServerStatus.CONNECTED.value
        self.message = message
        self.last_error = None
    
    def set_disconnected(self, message: str = "Connexion fermée"):
        """Définit l'état comme déconnecté"""
        self.is_connected = False
        self.status = ServerStatus.DISCONNECTED.value
        self.message = message

class ConversationState:
    """Gestion de l'état des conversations"""
    
    def __init__(self):
        self.current_conversation = None
        self.conversation_history = []
        self.total_conversations = 0
    
    @property
    def has_current_conversation(self) -> bool:
        """Vérifie si une conversation est active"""
        return self.current_conversation is not None
    
    def start_new_conversation(self) -> Conversation:
        """Démarre une nouvelle conversation"""
        self.total_conversations += 1
        conversation_id = f"conv_{self.total_conversations}"
        title = f"Conversation {self.total_conversations}"
        
        # Créer et stocker la nouvelle conversation
        conversation = Conversation(id=conversation_id, title=title)
        self.current_conversation = conversation
        self.conversation_history.append(conversation)
        
        return conversation


class AppState(QObject):
    """Gestionnaire d'état centralisé de l'application avec signaux Qt"""

    # ========================================================================
    # SIGNAUX D'ÉTAT
    # ========================================================================

    # Signaux de projet
    project_config_changed = Signal(ProjectConfig)
    project_creation_step_changed = Signal(str)
    project_path_selection_required = Signal(bool)
    # Signaux de conversation
    conversation_started = Signal(Conversation)
    conversation_cleared = Signal()
    message_added = Signal(ChatMessage)

    # Signaux de serveur
    server_status_changed = Signal(ServerStatus, str)  # status, message
    model_changed = Signal(str)  # model_name

    def __init__(self, parent=None):
        super().__init__(parent)

        # État interne
        self._project_config = ProjectConfig()  # Initialiser avec un objet vide plutôt que None
        self._ui_mode: UIMode = UIMode.CHAT
        self._conversation_state: ConversationState = ConversationState()
        self._server_state: ServerState = ServerState()
        
    @property
    def project_config(self):
        """Accès à la configuration du projet"""
        return self._project_config
        
    @property
    def server_state(self):
        """Accès à l'état du serveur"""
        return self._server_state

    def update_project_config(self, **kwargs) -> None:
        """Met à jour la configuration du projet de manière immutable"""
        # Mettre à jour la configuration existante
        for key, value in kwargs.items():
            if hasattr(self._project_config, key):
                setattr(self._project_config, key, value)
            
        self._project_config.update_modification_time()
        self.project_config_changed.emit(self._project_config)  # Signal automatique!

    def set_wait_for_path(self, waiting: bool) -> None:
        """Indique si l'application attend la sélection d'un chemin"""
        self.update_project_config(wait_for_path=waiting)
        self.project_path_selection_required.emit(waiting)

    ## 💬 Gestion des Conversations
    def add_message(self, text: str, is_user: bool = False, **kwargs) -> ChatMessage:
        """Ajoute un message à la conversation courante"""
        # S'assurer qu'il y a une conversation courante
        if not self._conversation_state.has_current_conversation:
            self.start_new_conversation()

        # Créer et ajouter le message
        message = ChatMessage(text=text, is_user=is_user, **kwargs)
        self._conversation_state.current_conversation.add_message(message)

        self.message_added.emit(message)  # Signal automatique!
        return message

    ## 🌐 Gestion du Serveur
    def start_new_conversation(self) -> Conversation:
        """Démarre une nouvelle conversation"""
        conversation = self._conversation_state.start_new_conversation()
        self.conversation_started.emit(conversation)  # Signal automatique!
        return conversation

    def set_server_connected(self, message: str = "Connexion établie") -> None:
        """Marque le serveur comme connecté"""
        self._server_state.set_connected(message)
        self.server_status_changed.emit(ServerStatus.CONNECTED, message)

    def set_server_disconnected(self, message: str = "Connexion fermée") -> None:
        """Marque le serveur comme déconnecté"""
        self._server_state.set_disconnected(message)
        self.server_status_changed.emit(ServerStatus.DISCONNECTED, message)

    ## 💾 Persistance et Sérialisation
    def save_state_to_file(self, file_path: str) -> bool:
        """Sauvegarde l'état complet dans un fichier JSON"""
        try:
            state_data = self.to_dict()

            # Créer le répertoire parent si nécessaire
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(state_data, f, indent=2, ensure_ascii=False)

            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de l'état: {e}")
            return False

    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'état complet en dictionnaire"""
        return {
            "project_config": (
                self._project_config.to_dict() if self._project_config else None
            ),
            "ui_mode": self._ui_mode.value,
            "conversation_state": {
                "current_conversation": (
                    self._conversation_state.current_conversation.to_dict()
                    if self._conversation_state.current_conversation
                    else None
                ),
                "conversation_history": [
                    conv.to_dict()
                    for conv in self._conversation_state.conversation_history
                ],
            },
            "server_state": {
                "status": self._server_state.status.value,
                "message": self._server_state.message,
                "selected_model": self._server_state.selected_model,
            },
        }
