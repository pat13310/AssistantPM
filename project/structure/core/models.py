# ───────────────────────────────────────────────────────────────────────────────
# 1)  core/models.py  – UNE seule source de vérité pour toutes les dataclasses
# ───────────────────────────────────────────────────────────────────────────────

#  ─── core/models.py ─────────────────────────────────────────────────────────

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional

__all__ = [
    "ServerStatus",
    "UIMode",
    "ProjectConfig",
    "ChatMessage",
    "Conversation",
    "ServerState",
    "ConversationState",
]


# ╭──────────────────────────────────────────────────────────────────────────╮
# │  Enums globaux                                                         │
# ╰──────────────────────────────────────────────────────────────────────────╯

class ServerStatus(str, Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


class UIMode(Enum):
    CHAT = auto()
    PROJECT = auto()
    SETTINGS = auto()


# ╭──────────────────────────────────────────────────────────────────────────╮
# │  Dataclasses métier                                                    │
# ╰──────────────────────────────────────────────────────────────────────────╯

@dataclass
class ProjectConfig:
    """Configuration complète d’un projet (unique !)"""

    # ─── Champs principaux ────────────────────────────────────────────────
    name: str = ""
    path: str = ""  # dossier parent
    root_path: str = ""  # dossier racine complet (optionnel)

    # Sélections (IDs + libellés)
    project_type_id: Optional[str] = None
    project_type_name: str = ""
    technology_id: Optional[str] = None
    technology_name: str = ""
    language_id: Optional[str] = None
    language_name: str = ""
    app_type_id: Optional[str] = None
    app_type_name: str = ""
    subtype_id: Optional[str] = None

    # État du wizard de création
    wait_for_path: bool = False
    creation_step: str = "initial"

    # Métadonnées
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)

    # ─── Propriétés dérivées ──────────────────────────────────────────────
    @property
    def full_path(self) -> str:  # ex:  /home/toto/mon‑app
        if self.path and self.name:
            return str(Path(self.path) / self.name)
        return self.path or ""

    @property
    def is_valid(self) -> bool:
        return bool(self.name and self.path)

    @property
    def is_complete(self) -> bool:
        return all([
            self.name,
            self.path,
            self.project_type_id,
            self.technology_id,
        ])

    # ─── (S)erialisation helpers ─────────────────────────────────────────
    def to_dict(self) -> Dict[str, Any]:
        dct = self.__dict__.copy()
        dct["created_at"] = self.created_at.isoformat()
        dct["modified_at"] = self.modified_at.isoformat()
        return dct

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProjectConfig":
        if isinstance(data.get("created_at"), str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if isinstance(data.get("modified_at"), str):
            data["modified_at"] = datetime.fromisoformat(data["modified_at"])
        return cls(**data)

    # ─── Mutations utiles ────────────────────────────────────────────────
    def update(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)
        self.modified_at = datetime.now()


# ─── CHAT MESSAGE & CONVERSATION ───────────────────────────────────────────
@dataclass
class ChatMessage:
    text: str
    is_user: bool
    timestamp: datetime = field(default_factory=datetime.now)
    # UI metadata
    icon_name: Optional[str] = None
    icon_color: str = "#FFFFFF"
    icon_size: int = 20
    word_wrap: bool = True
    # functional metadata
    message_type: str = "text"  # text, action, system, error…
    metadata: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class Conversation:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    messages: List[ChatMessage] = field(default_factory=list)
    title: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    project_context: Optional[ProjectConfig] = None
    tags: List[str] = field(default_factory=list)

    def add_message(self, msg: ChatMessage):
        self.messages.append(msg)
        self.updated_at = datetime.now()
        if not self.title and msg.is_user:
            self.title = msg.text[:50] + ("…" if len(msg.text) > 50 else "")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "messages": [m.__dict__ for m in self.messages],
        }


# ─── SERVER & CONVERSATION STATES ────────────────────────────────────────
@dataclass
class ServerState:
    is_connected: bool = False
    url: str = ""
    status: ServerStatus = ServerStatus.DISCONNECTED
    last_error: Optional[str] = None
    message: str = ""
    selected_model: str = ""

    def set_connected(self, message: str = "Connexion établie"):
        self.is_connected = True
        self.status = ServerStatus.CONNECTED
        self.message = message
        self.last_error = None

    def set_disconnected(self, message: str = "Connexion fermée"):
        self.is_connected = False
        self.status = ServerStatus.DISCONNECTED
        self.message = message


class ConversationState:
    """Gestion interne d’un ensemble de conversations (aucune dépendance Qt)"""

    def __init__(self):
        self.current: Optional[Conversation] = None
        self.history: List[Conversation] = []

    # -------------------------------------------------------------------
    def start_new(self) -> Conversation:
        conv = Conversation()
        self.current = conv
        self.history.append(conv)
        return conv

    # -------------------------------------------------------------------
    def to_dict(self):
        return {
            "current": self.current.to_dict() if self.current else None,
            "history": [c.to_dict() for c in self.history],
        }