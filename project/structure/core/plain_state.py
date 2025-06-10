# ───────────────────────────────────────────────────────────────────────────
# 2)  core/plain_state.py  – logique métier 100 % Python (sans Qt)
# ───────────────────────────────────────────────────────────────────────────

#  ─── core/plain_state.py ────────────────────────────────────────────────

"""État applicatif sans dépendance externe (testable en CLI / PyTest)."""

from __future__ import annotations

from typing import Callable, Optional

from .models import (
    ChatMessage,
    Conversation,
    ConversationState,
    ProjectConfig,
    ServerState,
    ServerStatus,
    UIMode,
)

__all__ = ["PlainAppState"]


class PlainAppState:
    """Gestionnaire d’état *sans* signal Qt.

    Tous les changements publient un *callback* optionnel afin de laisser la
    UI (ou les tests) réagir. Si aucun callback n’est fourni ⇒ silencieux.
    """

    # -------------------------------------------------------------------
    def __init__(
        self,
        on_project_config_changed: Optional[Callable[[ProjectConfig], None]] = None,
        on_message_added: Optional[Callable[[ChatMessage], None]] = None,
        on_conversation_started: Optional[Callable[[Conversation], None]] = None,
        on_server_status_changed: Optional[Callable[[ServerStatus, str], None]] = None,
    ) -> None:
        self._project_config = ProjectConfig()
        self._ui_mode: UIMode = UIMode.CHAT
        self._conversations = ConversationState()
        self._server_state = ServerState()

        # callbacks -------------------------------------------------------
        self._cb_project = on_project_config_changed or (lambda *_: None)
        self._cb_msg = on_message_added or (lambda *_: None)
        self._cb_conv = on_conversation_started or (lambda *_: None)
        self._cb_srv = on_server_status_changed or (lambda *_: None)

    # -------------------------------------------------------------------
    # « project » helpers
    # -------------------------------------------------------------------
    @property
    def project_config(self) -> ProjectConfig:
        return self._project_config

    def update_project_config(self, **kwargs):
        self._project_config.update(**kwargs)
        self._cb_project(self._project_config)

    def set_wait_for_path(self, waiting: bool):
        self.update_project_config(wait_for_path=waiting)

    # -------------------------------------------------------------------
    # « conversation » helpers
    # -------------------------------------------------------------------
    def start_new_conversation(self) -> Conversation:
        conv = self._conversations.start_new()
        self._cb_conv(conv)
        return conv

    def add_message(
        self,
        text: str,
        is_user: bool = False,
        **kwargs,
    ) -> ChatMessage:
        if self._conversations.current is None:
            self.start_new_conversation()
        msg = ChatMessage(text=text, is_user=is_user, **kwargs)
        self._conversations.current.add_message(msg)  # type: ignore
        self._cb_msg(msg)
        return msg

    # -------------------------------------------------------------------
    # « server » helpers
    # -------------------------------------------------------------------
    def set_server_connected(self, message: str = "Connexion établie"):
        self._server_state.set_connected(message)
        self._cb_srv(ServerStatus.CONNECTED, message)

    def set_server_disconnected(self, message: str = "Connexion fermée"):
        self._server_state.set_disconnected(message)
        self._cb_srv(ServerStatus.DISCONNECTED, message)

    @property
    def server_state(self) -> ServerState:
        return self._server_state

    # -------------------------------------------------------------------
    # Serialisation (ex. pour sauvegarde de sessions)
    # -------------------------------------------------------------------
    def to_dict(self):
        return {
            "project_config": self._project_config.to_dict(),
            "ui_mode": self._ui_mode.name,
            "conversation_state": self._conversations.to_dict(),
            "server_state": {
                "status": self._server_state.status.value,
                "message": self._server_state.message,
                "selected_model": self._server_state.selected_model,
            },
        }
