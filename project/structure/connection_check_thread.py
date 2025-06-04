#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide6.QtCore import QThread, Signal
import httpx

class ConnectionCheckThread(QThread):
    """
    Thread pour vérifier la connexion au serveur IA
    Permet d'éviter de bloquer l'interface utilisateur pendant la vérification
    """
    connection_status = Signal(bool, str)
    finished = Signal()

    def __init__(self, url="http://localhost:8000/health"):
        super().__init__()
        self.url = url
        self.timeout = 2.0

    def run(self):
        try:
            # Tenter une connexion rapide pour vérifier si le serveur est actif
            response = httpx.get(self.url, timeout=self.timeout)
            if response.status_code == 200:
                self.connection_status.emit(True, "Connecté au serveur IA")
            else:
                self.connection_status.emit(False, "Erreur de connexion")
        except Exception as e:
            self.connection_status.emit(False, f"Serveur IA non disponible: {str(e)}")
        finally:
            # Toujours émettre le signal de fin
            self.finished.emit()
