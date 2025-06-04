#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module contenant la classe ConnectionWorker pour vérifier la connexion au serveur
dans un thread séparé sans bloquer l'interface utilisateur.
"""

from PySide6.QtCore import QObject, Signal
import httpx


class ConnectionWorker(QObject):
    """Classe qui gère la vérification de connexion au serveur dans un thread séparé"""
    connection_result = Signal(bool, str)
    finished = Signal()
    
    def __init__(self, url):
        super().__init__()
        self.url = url
    
    def check_connection(self):
        """Vérifie la connexion au serveur et émet un signal avec le résultat"""
        try:
            # Tenter une connexion rapide pour vérifier si le serveur est actif
            response = httpx.get(self.url, timeout=2.0)
            if response.status_code == 200:
                # Connexion réussie
                self.connection_result.emit(True, "Connecté au serveur IA")
            else:
                # Erreur de connexion
                self.connection_result.emit(False, "Erreur de connexion")
        except Exception as e:
            # Exception lors de la tentative de connexion
            self.connection_result.emit(False, "Serveur IA non disponible")
            print(f"Erreur de connexion au serveur : {e}")
        
        # Signaler que la vérification est terminée
        self.finished.emit()
