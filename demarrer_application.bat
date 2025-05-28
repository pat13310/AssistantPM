@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
title Assistant PM - Lanceur d'Application
color 0B

:: Vérifier si Python est installé
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Python n'est pas installé ou n'est pas dans le PATH.
    echo Veuillez installer Python et réessayer.
    pause
    exit /b 1
)

:: Définir le répertoire courant au répertoire du script
cd /d %~dp0

:: Menu principal
:menu
cls
echo ╔══════════════════════════════════════════════════╗
echo ║          ASSISTANT PM - MENU DE DÉMARRAGE        ║
echo ╚══════════════════════════════════════════════════╝
echo.
echo  1. Démarrer l'application complète (serveur + interface)
echo  2. Démarrer uniquement le serveur IA
echo  3. Démarrer uniquement l'interface graphique
echo  4. Quitter
echo.
set /p choix=Votre choix (1-4): 

if "%choix%"=="1" goto demarrer_complet
if "%choix%"=="2" goto demarrer_serveur
if "%choix%"=="3" goto demarrer_interface
if "%choix%"=="4" goto fin

echo Choix invalide. Veuillez réessayer.
pause
goto menu

:demarrer_complet
cls
echo ╔══════════════════════════════════════════════════╗
echo ║        DÉMARRAGE DE L'APPLICATION COMPLÈTE       ║
echo ╚══════════════════════════════════════════════════╝
echo.
echo [INFO] Lancement du serveur IA en arrière-plan...
start cmd /c "title Serveur IA AssistantPM && color 0A && cd /d %~dp0 && python agent_ia_stream.py"

echo [INFO] Attente du démarrage du serveur (3 secondes)...
timeout /t 3 /nobreak > nul

echo [INFO] Lancement de l'interface graphique...
python project\structure\ui_agent_ia.py
goto fin

:demarrer_serveur
cls
echo ╔══════════════════════════════════════════════════╗
echo ║           DÉMARRAGE DU SERVEUR IA SEUL           ║
echo ╚══════════════════════════════════════════════════╝
echo.
echo [INFO] Lancement du serveur IA...
python agent_ia_stream.py
goto fin

:demarrer_interface
cls
echo ╔══════════════════════════════════════════════════╗
echo ║        DÉMARRAGE DE L'INTERFACE GRAPHIQUE        ║
echo ╚══════════════════════════════════════════════════╝
echo.
echo [INFO] Lancement de l'interface graphique...
echo [ATTENTION] Assurez-vous que le serveur IA est déjà en cours d'exécution.
python project\structure\ui_agent_ia.py
goto fin

:fin
exit /b 0
