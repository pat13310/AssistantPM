# ───────────────────────────────────────────────────────────────────────────
# 3)  core/qt_state.py  – wrapper Qt qui convertit les callbacks en Signaux
# ───────────────────────────────────────────────────────────────────────────

#  ─── core/qt_state.py ───────────────────────────────────────────────────

from __future__ import annotations

from PySide6.QtCore import QObject, Signal

from .models import ChatMessage, Conversation, ProjectConfig, ServerStatus
from .plain_state import PlainAppState

__all__ = ["QtAppState"]


class QtAppState(QObject, PlainAppState):
    """Ajoute les signaux Qt *sans* dupliquer la logique métier."""

    # Signaux grand public -------------------------------------------------
    project_config_changed = Signal(ProjectConfig)
    message_added = Signal(ChatMessage)
    conversation_started = Signal(Conversation)
    server_status_changed = Signal(ServerStatus, str)  # status, message

    # -------------------------------------------------------------------
    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        PlainAppState.__init__(
            self,
            on_project_config_changed=self.project_config_changed.emit,
            on_message_added=self.message_added.emit,
            on_conversation_started=self.conversation_started.emit,
            on_server_status_changed=self.server_status_changed.emit,
        )
