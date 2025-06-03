#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide6.QtCore import QThread, Signal
import httpx
import json

class StreamThread(QThread):
    """
    Thread pour gérer la communication streaming avec le serveur IA
    Permet de recevoir les réponses de l'IA en temps réel
    """
    message = Signal(str)
    finished = Signal()

    def __init__(self, user_message, model):
        super().__init__()
        self.user_message = user_message
        self.model = model

    def run(self):
        try:
            url = "http://localhost:8000/chat_stream"
            headers = {
                "accept": "text/event-stream",
                "Content-Type": "application/json",
            }
            payload = json.dumps({"message": self.user_message, "model": self.model})

            # Utiliser un timeout plus long pour éviter les interruptions
            with httpx.stream(
                "POST", url, headers=headers, content=payload, timeout=120.0
            ) as r:
                text = ""
                for line in r.iter_lines():
                    # Vérifier si line est présent
                    if line:
                        # Vérifier le type de line et convertir si nécessaire
                        if isinstance(line, bytes):
                            line_str = line.decode("utf-8")
                        else:
                            line_str = line

                        if line_str.startswith("data: "):
                            try:
                                data = json.loads(line_str[6:])
                                part = data.get("text", "")
                                text += part
                                self.message.emit(part)
                            except json.JSONDecodeError:
                                # En cas d'erreur de décodage JSON, ignorer cette ligne
                                continue
        except Exception as e:
            # En cas d'erreur, émettre un message d'erreur
            self.message.emit(
                f"<span style='color:red'>Erreur de connexion: {str(e)}</span>"
            )
        finally:
            # Toujours émettre le signal de fin
            self.finished.emit()
