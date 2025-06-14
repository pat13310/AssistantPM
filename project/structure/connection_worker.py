#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module contenant la classe ConnectionWorker pour vérifier la connexion au serveur
dans un thread séparé sans bloquer l'interface utilisateur.
"""

import os
import sys
import httpx
from PySide6.QtCore import QObject, Signal, QTimer, QRunnable, Slot, QThreadPool


class ConnectionWorkerSignals(QObject):
    """Classe qui définit les signaux pour la classe ConnectionWorker"""
    connection_result = Signal(bool, str)
    finished = Signal()
    progress = Signal(int)  # Signal de progression (0-100)


class ConnectionWorker(QRunnable):
    """Classe qui gère la vérification de connexion au serveur dans un thread pool"""
    
    def __init__(self, url, timeout=5.0):
        super().__init__()
        self.url = url
        self.timeout = timeout
        self.is_cancelled = False
        # Créer une instance de la classe de signaux
        self.signals = ConnectionWorkerSignals()
    
    @Slot()
    def run(self):
        """Méthode principale exécutée par le thread pool"""
        try:
            # Émettre le signal de début de progression
            self.signals.progress.emit(10)
            
            # Vérifier si l'opération a été annulée
            if self.is_cancelled:
                self.signals.connection_result.emit(False, "Vérification annulée")
                self.signals.finished.emit()
                return
            
            # Émettre une progression
            self.signals.progress.emit(30)
            
            # Effectuer la requête HTTP pour vérifier la connexion
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    response = client.get(self.url)
                    # Vérifier si l'opération a été annulée pendant la requête
                    if self.is_cancelled:
                        self.signals.connection_result.emit(False, "Vérification annulée")
                        self.signals.finished.emit()
                        return
                    
                    # Émettre une progression
                    self.signals.progress.emit(70)
                    
                    # Vérifier le code de statut HTTP
                    if response.status_code == 200:
                        self.signals.progress.emit(100)
                        self.signals.connection_result.emit(True, "Connecté au serveur IA")
                    else:
                        self.signals.connection_result.emit(
                            False, f"Erreur HTTP: {response.status_code}"
                        )
            except httpx.TimeoutException:
                # Gérer spécifiquement les erreurs de timeout
                self.signals.connection_result.emit(False, "Délai d'attente dépassé")
            except httpx.ConnectError:
                # Gérer spécifiquement les erreurs de connexion
                self.signals.connection_result.emit(False, "Impossible de se connecter au serveur")
            except Exception as e:
                # Gérer les autres erreurs
                print(f"Erreur lors de la vérification de connexion: {e}")
                self.signals.connection_result.emit(False, "Erreur de connexion au serveur : connexion impossible")
        except Exception as e:
            # Exception générale lors de la tentative de connexion
            print(f"Erreur lors du démarrage de la vérification : {e}")
            self.signals.connection_result.emit(False, "Erreur interne")
        finally:
            # Toujours émettre le signal de fin
            self.signals.finished.emit()
    
    def cancel(self):
        """Annule la vérification de connexion en cours"""
        self.is_cancelled = True
    def _continue_check_connection(self):
        """Suite de la vérification de connexion après un court délai"""
        try:
            if self.is_cancelled:
                self.connection_result.emit(False, "Vérification annulée")
                self.finished.emit()
                return
                
            # Progression
            self.progress.emit(30)
            
            # Utiliser un bloc try/except spécifique pour les erreurs de timeout
            try:
                # Utiliser httpx avec un timeout approprié
                response = httpx.get(self.url, timeout=self.timeout)
                self.progress.emit(80)
                
                if response.status_code == 200:
                    # Connexion réussie
                    self.connection_result.emit(True, "Connecté au serveur IA")
                else:
                    # Erreur de connexion avec code d'état
                    self.connection_result.emit(False, f"Erreur de connexion: {response.status_code}")
            except httpx.TimeoutException:
                # Gérer spécifiquement les erreurs de timeout
                self.connection_result.emit(False, "Délai de connexion dépassé")
                print("Erreur de connexion au serveur : délai dépassé")
            except httpx.ConnectError:
                # Gérer les erreurs de connexion
                self.connection_result.emit(False, "Impossible de se connecter au serveur")
                print("Erreur de connexion au serveur : connexion impossible")
            except Exception as e:
                # Autres exceptions lors de la requête
                self.connection_result.emit(False, f"Erreur: {str(e)}")
                print(f"Erreur de connexion au serveur : {e}")
        except Exception as e:
            # Exception générale lors de la tentative de connexion
            self.connection_result.emit(False, "Serveur IA non disponible")
            print(f"Erreur de connexion au serveur : {e}")
        finally:
            # Signaler que la vérification est terminée
            self.progress.emit(100)
            self.finished.emit()
    
    def cancel(self):
        """Annule la vérification de connexion en cours"""
        self.is_cancelled = True
        # Émettre les signaux pour terminer proprement
        try:
            self.connection_result.emit(False, "Vérification annulée")
            self.finished.emit()
        except Exception:
            pass  # Ignorer les erreurs si les signaux ne peuvent pas être émis
