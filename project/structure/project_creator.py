#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module pour la création de structures de projets
Ce module contient les fonctions nécessaires pour créer des structures de projets
en fonction du type de projet et de la technologie choisie.
"""

import os
import json
from project.structure.project_creator_extensions import create_devops_project, create_microservices_project, create_cms_project
from project.structure.project_data_loader import ProjectDataLoader

class ProjectCreator:
    """Classe pour la création de structures de projets"""
    
    @staticmethod
    def get_app_types_for_technology(technology):
        """Retourne les types d'applications disponibles pour une technologie donnée"""
        return ProjectDataLoader.get_app_types_for_technology(technology)

    @staticmethod
    def get_features_for_app_type(app_type):
        """Retourne les fonctionnalités disponibles pour un type d'application donné"""
        return ProjectDataLoader.get_features_for_app_type(app_type)
    
    @staticmethod
    def create_project_structure(project_path, project_type_id, technology_id, project_name=None):
        """
        Crée la structure de base d'un projet en fonction de son type et de sa technologie
        
        Args:
            project_path (str): Chemin du répertoire du projet
            project_type_id (str): Identifiant du type de projet
            technology_id (str): Identifiant de la technologie
            project_name (str, optional): Nom du projet. Si None, le nom du dossier sera utilisé.
        """
        # Si le nom du projet n'est pas spécifié, utiliser le nom du dossier
        if project_name is None:
            project_name = os.path.basename(project_path)
            
        # Créer les répertoires de base communs à tous les projets
        ProjectCreator._create_common_directories(project_path)
        
        # Créer README.md
        ProjectCreator._create_readme(project_path, project_type_id, technology_id, project_name)
        
        # Créer la structure spécifique en fonction du type de projet
        if project_type_id == "web":
            ProjectCreator._create_web_project(project_path, technology_id, project_name)
        elif project_type_id == "desktop":
            ProjectCreator._create_desktop_project(project_path, technology_id, project_name)
        elif project_type_id == "mobile":
            ProjectCreator._create_mobile_project(project_path, technology_id, project_name)
        elif project_type_id == "api":
            ProjectCreator._create_api_project(project_path, technology_id, project_name)
        elif project_type_id == "library":
            ProjectCreator._create_library_project(project_path, technology_id, project_name)
        elif project_type_id == "game":
            ProjectCreator._create_game_project(project_path, technology_id, project_name)
        elif project_type_id == "data":
            ProjectCreator._create_data_project(project_path, technology_id, project_name)
        elif project_type_id == "iot":
            ProjectCreator._create_iot_project(project_path, technology_id, project_name)
        elif project_type_id == "blockchain":
            ProjectCreator._create_blockchain_project(project_path, technology_id, project_name)
        elif project_type_id == "ai":
            ProjectCreator._create_ai_project(project_path, technology_id, project_name)
        elif project_type_id == "devops":
            ProjectCreator._create_devops_project(project_path, technology_id, project_name)
        elif project_type_id == "microservices":
            ProjectCreator._create_microservices_project(project_path, technology_id, project_name)
        elif project_type_id == "cms":
            ProjectCreator._create_cms_project(project_path, technology_id, project_name)
    
    @staticmethod
    def _create_common_directories(project_path):
        """Crée les répertoires communs à tous les projets"""
        os.makedirs(os.path.join(project_path, "docs"), exist_ok=True)
        os.makedirs(os.path.join(project_path, "tests"), exist_ok=True)
    
    @staticmethod
    def _create_readme(project_path, project_type_id, technology_id, project_name):
        """Crée un fichier README.md pour le projet"""
        # Obtenir les noms du type de projet et de la technologie
        project_type_name = ProjectCreator._get_project_type_name(project_type_id)
        technology_name = ProjectCreator._get_technology_name(project_type_id, technology_id)
        
        with open(os.path.join(project_path, "README.md"), "w", encoding="utf-8") as f:
            f.write(f"# {project_name}\n\n")
            f.write(f"Un projet de type {project_type_name} utilisant {technology_name}.\n\n")
            f.write("## Installation\n\n")
            f.write("Instructions d'installation à venir...\n\n")
            f.write("## Utilisation\n\n")
            f.write("Instructions d'utilisation à venir...\n\n")
            f.write("## Licence\n\n")
            f.write("Ce projet est sous licence MIT.\n")
    
    @staticmethod
    def _get_project_type_name(project_type_id):
        """Retourne le nom d'un type de projet à partir de son identifiant"""
        project_types = {
            "web": "Application Web",
            "desktop": "Application Bureau",
            "mobile": "Application Mobile",
            "api": "API / Service Web",
            "library": "Bibliothèque / Package",
            "game": "Jeu Vidéo",
            "data": "Science des Données",
            "iot": "IoT / Embarqué",
            "blockchain": "Application Blockchain",
            "ai": "Intelligence Artificielle",
            "devops": "DevOps / CI/CD",
            "microservices": "Microservices",
            "cms": "Système de Gestion de Contenu"
        }
        return project_types.get(project_type_id, "Projet")
    
    @staticmethod
    def _get_technology_name(project_type_id, technology_id):
        """Retourne le nom d'une technologie à partir de son identifiant et du type de projet"""
        technologies = {
            "web": {
                "react": "React",
                "vue": "Vue.js",
                "angular": "Angular",
                "django": "Django",
                "flask": "Flask",
                "laravel": "Laravel",
                "express": "Express.js",
                "spring": "Spring Boot",
                "next": "Next.js",
                "nuxt": "Nuxt.js",
                "svelte": "Svelte",
                "rails": "Ruby on Rails",
                "php": "PHP",
                "symfony": "Symfony"
            },
            "desktop": {
                "electron": "Electron",
                "qt": "Qt",
                "wpf": "WPF",
                "javafx": "JavaFX",
                "gtk": "GTK",
                "wxwidgets": "wxWidgets",
                "winforms": "Windows Forms",
                "swing": "Java Swing",
                "tkinter": "Tkinter",
                "pyqt": "PyQt"
            },
            "mobile": {
                "react-native": "React Native",
                "flutter": "Flutter",
                "android": "Android Native",
                "ios": "iOS Native",
                "xamarin": "Xamarin",
                "ionic": "Ionic",
                "kotlin": "Kotlin Multiplatform",
                "swift": "Swift UI",
                "capacitor": "Capacitor",
                "nativescript": "NativeScript"
            },
            "api": {
                "fastapi": "FastAPI",
                "express-api": "Express.js API",
                "spring-boot": "Spring Boot",
                "aspnet-core": "ASP.NET Core",
                "graphql": "GraphQL",
                "django-rest": "Django REST Framework",
                "flask-restful": "Flask-RESTful",
                "nest": "NestJS",
                "go-gin": "Go Gin",
                "ruby-sinatra": "Ruby Sinatra"
            },
            "library": {
                "python-lib": "Python Package",
                "npm-package": "NPM Package",
                "java-lib": "Java Library",
                "dotnet-lib": ".NET Library",
                "rust-crate": "Rust Crate",
                "go-module": "Go Module",
                "ruby-gem": "Ruby Gem",
                "php-composer": "PHP Composer Package"
            },
            "game": {
                "unity": "Unity",
                "unreal": "Unreal Engine",
                "godot": "Godot",
                "pygame": "Pygame",
                "phaser": "Phaser.js",
                "monogame": "MonoGame",
                "libgdx": "LibGDX",
                "cocos2d": "Cocos2d"
            },
            "data": {
                "jupyter": "Jupyter Notebook",
                "pandas": "Pandas/NumPy",
                "r-project": "R Project",
                "tensorflow": "TensorFlow",
                "pytorch": "PyTorch",
                "scikit-learn": "Scikit-Learn",
                "spark": "Apache Spark",
                "hadoop": "Apache Hadoop",
                "tableau": "Tableau",
                "powerbi": "Power BI"
            },
            "iot": {
                "arduino": "Arduino",
                "raspberry-pi": "Raspberry Pi",
                "esp32": "ESP32",
                "micropython": "MicroPython",
                "particle": "Particle IoT",
                "zephyr": "Zephyr RTOS",
                "mbed": "ARM Mbed OS",
                "homeassistant": "Home Assistant"
            },
            "blockchain": {
                "ethereum": "Ethereum/Solidity",
                "web3js": "Web3.js",
                "hardhat": "Hardhat",
                "truffle": "Truffle",
                "hyperledger": "Hyperledger Fabric",
                "solana": "Solana",
                "rust-near": "NEAR Protocol (Rust)",
                "cosmos-sdk": "Cosmos SDK"
            },
            "ai": {
                "tensorflow": "TensorFlow",
                "pytorch": "PyTorch",
                "keras": "Keras",
                "scikit-learn": "Scikit-Learn",
                "huggingface": "Hugging Face Transformers",
                "opencv": "OpenCV",
                "nltk": "NLTK",
                "spacy": "spaCy"
            },
            "devops": {
                "docker": "Docker",
                "kubernetes": "Kubernetes",
                "terraform": "Terraform",
                "ansible": "Ansible",
                "jenkins": "Jenkins",
                "github-actions": "GitHub Actions",
                "gitlab-ci": "GitLab CI/CD",
                "aws-cloudformation": "AWS CloudFormation"
            },
            "microservices": {
                "spring-cloud": "Spring Cloud",
                "nestjs": "NestJS",
                "dotnet-microservices": ".NET Microservices",
                "go-micro": "Go Micro",
                "moleculer": "Moleculer.js",
                "dapr": "Dapr",
                "istio": "Istio",
                "kong": "Kong API Gateway"
            },
            "cms": {
                "wordpress": "WordPress",
                "drupal": "Drupal",
                "joomla": "Joomla",
                "ghost": "Ghost",
                "strapi": "Strapi",
                "contentful": "Contentful",
                "sanity": "Sanity.io",
                "keystonejs": "KeystoneJS"
            }
        }
        
        if project_type_id in technologies and technology_id in technologies[project_type_id]:
            return technologies[project_type_id][technology_id]
        return technology_id
    
    @staticmethod
    def _create_web_project(project_path, technology_id, project_name):
        """Crée la structure d'un projet web"""
        os.makedirs(os.path.join(project_path, "src"), exist_ok=True)
        os.makedirs(os.path.join(project_path, "public"), exist_ok=True)
        os.makedirs(os.path.join(project_path, "assets"), exist_ok=True)
        
        # Structure spécifique à la technologie
        if technology_id == "react":
            os.makedirs(os.path.join(project_path, "src", "components"), exist_ok=True)
            os.makedirs(os.path.join(project_path, "src", "pages"), exist_ok=True)
            os.makedirs(os.path.join(project_path, "src", "hooks"), exist_ok=True)
            
            # Créer package.json
            package_json = {
                "name": project_name.lower().replace(' ', '-'),
                "version": "0.1.0",
                "private": True,
                "dependencies": {
                    "react": "^18.2.0",
                    "react-dom": "^18.2.0",
                    "react-scripts": "5.0.1"
                },
                "scripts": {
                    "start": "react-scripts start",
                    "build": "react-scripts build",
                    "test": "react-scripts test",
                    "eject": "react-scripts eject"
                }
            }
            
            with open(os.path.join(project_path, "package.json"), "w", encoding="utf-8") as f:
                json.dump(package_json, f, indent=2)
        
        elif technology_id == "django":
            os.makedirs(os.path.join(project_path, project_name.lower().replace(' ', '_')), exist_ok=True)
            os.makedirs(os.path.join(project_path, "templates"), exist_ok=True)
            os.makedirs(os.path.join(project_path, "static"), exist_ok=True)
            
            # Créer requirements.txt
            with open(os.path.join(project_path, "requirements.txt"), "w", encoding="utf-8") as f:
                f.write("Django>=4.0,<5.0\n")
                f.write("psycopg2-binary>=2.9.3\n")
                f.write("djangorestframework>=3.13.0\n")
    
    @staticmethod
    def _create_desktop_project(project_path, technology_id, project_name):
        """Crée la structure d'un projet bureau"""
        os.makedirs(os.path.join(project_path, "src"), exist_ok=True)
        os.makedirs(os.path.join(project_path, "resources"), exist_ok=True)
        
        if technology_id == "qt":
            os.makedirs(os.path.join(project_path, "src", "ui"), exist_ok=True)
            os.makedirs(os.path.join(project_path, "src", "models"), exist_ok=True)
            
            # Créer un fichier .pro pour Qt
            with open(os.path.join(project_path, project_name.lower().replace(' ', '_') + ".pro"), "w", encoding="utf-8") as f:
                f.write("QT += core gui\n\n")
                f.write("greaterThan(QT_MAJOR_VERSION, 4): QT += widgets\n\n")
                f.write(f"TARGET = {project_name.lower().replace(' ', '_')}\n")
                f.write("TEMPLATE = app\n\n")
                f.write("SOURCES += \\\n")
                f.write("    src/main.cpp\n\n")
                f.write("HEADERS += \\\n")
                f.write("    src/mainwindow.h\n\n")
                f.write("FORMS += \\\n")
                f.write("    src/ui/mainwindow.ui\n")
    
    @staticmethod
    def _create_mobile_project(project_path, technology_id, project_name):
        """Crée la structure d'un projet mobile"""
        if technology_id == "flutter":
            os.makedirs(os.path.join(project_path, "lib"), exist_ok=True)
            os.makedirs(os.path.join(project_path, "assets"), exist_ok=True)
            os.makedirs(os.path.join(project_path, "android"), exist_ok=True)
            os.makedirs(os.path.join(project_path, "ios"), exist_ok=True)
            
            # Créer pubspec.yaml
            with open(os.path.join(project_path, "pubspec.yaml"), "w", encoding="utf-8") as f:
                f.write(f"name: {project_name.lower().replace(' ', '_')}\n")
                f.write("description: A new Flutter project.\n\n")
                f.write("version: 1.0.0+1\n\n")
                f.write("environment:\n")
                f.write("  sdk: '>=3.0.0 <4.0.0'\n\n")
                f.write("dependencies:\n")
                f.write("  flutter:\n")
                f.write("    sdk: flutter\n")
                f.write("  cupertino_icons: ^1.0.5\n\n")
                f.write("dev_dependencies:\n")
                f.write("  flutter_test:\n")
                f.write("    sdk: flutter\n\n")
                f.write("flutter:\n")
                f.write("  uses-material-design: true\n")
        
        elif technology_id == "react-native":
            os.makedirs(os.path.join(project_path, "src"), exist_ok=True)
            os.makedirs(os.path.join(project_path, "src", "components"), exist_ok=True)
            os.makedirs(os.path.join(project_path, "src", "screens"), exist_ok=True)
            os.makedirs(os.path.join(project_path, "src", "assets"), exist_ok=True)
            
            # Créer package.json
            package_json = {
                "name": project_name.lower().replace(' ', '-'),
                "version": "0.1.0",
                "private": True,
                "scripts": {
                    "android": "react-native run-android",
                    "ios": "react-native run-ios",
                    "start": "react-native start",
                    "test": "jest"
                },
                "dependencies": {
                    "react": "18.2.0",
                    "react-native": "0.72.0"
                },
                "devDependencies": {
                    "@babel/core": "^7.20.0",
                    "@babel/preset-env": "^7.20.0",
                    "jest": "^29.2.1"
                }
            }
            
            with open(os.path.join(project_path, "package.json"), "w", encoding="utf-8") as f:
                json.dump(package_json, f, indent=2)
    
    @staticmethod
    def _create_api_project(project_path, technology_id, project_name):
        """Crée la structure d'un projet API"""
        if technology_id == "fastapi":
            os.makedirs(os.path.join(project_path, "app"), exist_ok=True)
            os.makedirs(os.path.join(project_path, "app", "routers"), exist_ok=True)
            os.makedirs(os.path.join(project_path, "app", "models"), exist_ok=True)
            os.makedirs(os.path.join(project_path, "app", "schemas"), exist_ok=True)
            os.makedirs(os.path.join(project_path, "app", "db"), exist_ok=True)
            
            # Créer requirements.txt
            with open(os.path.join(project_path, "requirements.txt"), "w", encoding="utf-8") as f:
                f.write("fastapi>=0.95.0,<0.96.0\n")
                f.write("uvicorn>=0.22.0,<0.23.0\n")
                f.write("sqlalchemy>=2.0.0,<3.0.0\n")
                f.write("pydantic>=1.10.0,<2.0.0\n")
                f.write("python-dotenv>=1.0.0,<2.0.0\n")
            
            # Créer main.py
            with open(os.path.join(project_path, "main.py"), "w", encoding="utf-8") as f:
                f.write("from fastapi import FastAPI\n\n")
                f.write("app = FastAPI(\n")
                f.write(f"    title=\"{project_name}\",\n")
                f.write("    description=\"API FastAPI\",\n")
                f.write("    version=\"0.1.0\"\n")
                f.write(")\n\n")
                f.write("@app.get(\"/\")\n")
                f.write("async def root():\n")
                f.write("    return {\"message\": \"Hello World\"}\n")
        
        elif technology_id == "express-api":
            os.makedirs(os.path.join(project_path, "src"), exist_ok=True)
            os.makedirs(os.path.join(project_path, "src", "routes"), exist_ok=True)
            os.makedirs(os.path.join(project_path, "src", "controllers"), exist_ok=True)
            os.makedirs(os.path.join(project_path, "src", "models"), exist_ok=True)
            os.makedirs(os.path.join(project_path, "src", "middleware"), exist_ok=True)
            
            # Créer package.json
            package_json = {
                "name": project_name.lower().replace(' ', '-'),
                "version": "1.0.0",
                "description": "Express API",
                "main": "src/index.js",
                "scripts": {
                    "start": "node src/index.js",
                    "dev": "nodemon src/index.js",
                    "test": "jest"
                },
                "dependencies": {
                    "express": "^4.18.2",
                    "cors": "^2.8.5",
                    "dotenv": "^16.0.3",
                    "mongoose": "^7.0.3"
                },
                "devDependencies": {
                    "nodemon": "^2.0.22",
                    "jest": "^29.5.0"
                }
            }
            
            with open(os.path.join(project_path, "package.json"), "w", encoding="utf-8") as f:
                json.dump(package_json, f, indent=2)
    
    @staticmethod
    def _create_library_project(project_path, technology_id, project_name):
        """Crée la structure d'un projet de bibliothèque"""
        if technology_id == "python-lib":
            package_name = project_name.lower().replace(' ', '_')
            os.makedirs(os.path.join(project_path, package_name), exist_ok=True)
            os.makedirs(os.path.join(project_path, "examples"), exist_ok=True)
            
            # Créer setup.py
            with open(os.path.join(project_path, "setup.py"), "w", encoding="utf-8") as f:
                f.write("from setuptools import setup, find_packages\n\n")
                f.write("setup(\n")
                f.write(f"    name=\"{package_name}\",\n")
                f.write("    version=\"0.1.0\",\n")
                f.write("    packages=find_packages(),\n")
                f.write("    install_requires=[\n")
                f.write("        # Ajouter vos dépendances ici\n")
                f.write("    ],\n")
                f.write(f"    author=\"Auteur\",\n")
                f.write(f"    author_email=\"email@example.com\",\n")
                f.write(f"    description=\"Une bibliothèque Python\",\n")
                f.write(f"    keywords=\"python, library\",\n")
                f.write(f"    url=\"https://github.com/username/{package_name}\",\n")
                f.write("    classifiers=[\n")
                f.write("        \"Programming Language :: Python :: 3\",\n")
                f.write("        \"License :: OSI Approved :: MIT License\",\n")
                f.write("        \"Operating System :: OS Independent\",\n")
                f.write("    ],\n")
                f.write("    python_requires='>=3.6',\n")
                f.write(")\n")
            
            # Créer __init__.py
            init_path = os.path.join(project_path, package_name, "__init__.py")
            with open(init_path, "w", encoding="utf-8") as f:
                f.write(f"\"\"\"\n{project_name}\n\nUne bibliothèque Python.\n\"\"\"\n\n__version__ = '0.1.0'\n")
    
    @staticmethod
    def _create_game_project(project_path, technology_id, project_name):
        """Crée la structure d'un projet de jeu"""
        if technology_id == "pygame":
            os.makedirs(os.path.join(project_path, "src"), exist_ok=True)
            os.makedirs(os.path.join(project_path, "assets"), exist_ok=True)
            os.makedirs(os.path.join(project_path, "assets", "images"), exist_ok=True)
            os.makedirs(os.path.join(project_path, "assets", "sounds"), exist_ok=True)
            
            # Créer requirements.txt
            with open(os.path.join(project_path, "requirements.txt"), "w", encoding="utf-8") as f:
                f.write("pygame>=2.3.0\n")
            
            # Créer main.py
            with open(os.path.join(project_path, "main.py"), "w", encoding="utf-8") as f:
                f.write("import pygame\n")
                f.write("import sys\n\n")
                f.write("# Initialiser pygame\n")
                f.write("pygame.init()\n\n")
                f.write("# Configuration de l'écran\n")
                f.write("WIDTH, HEIGHT = 800, 600\n")
                f.write("screen = pygame.display.set_mode((WIDTH, HEIGHT))\n")
                f.write(f"pygame.display.set_caption(\"{project_name}\")\n\n")
                f.write("# Couleurs\n")
                f.write("WHITE = (255, 255, 255)\n")
                f.write("BLACK = (0, 0, 0)\n\n")
                f.write("# Boucle principale du jeu\n")
                f.write("clock = pygame.time.Clock()\n")
                f.write("running = True\n\n")
                f.write("while running:\n")
                f.write("    # Gérer les événements\n")
                f.write("    for event in pygame.event.get():\n")
                f.write("        if event.type == pygame.QUIT:\n")
                f.write("            running = False\n\n")
                f.write("    # Effacer l'écran\n")
                f.write("    screen.fill(WHITE)\n\n")
                f.write("    # Mettre à jour l'écran\n")
                f.write("    pygame.display.flip()\n")
                f.write("    clock.tick(60)  # 60 FPS\n\n")
                f.write("# Quitter pygame\n")
                f.write("pygame.quit()\n")
                f.write("sys.exit()\n")
    
    @staticmethod
    def _create_data_project(project_path, technology_id, project_name):
        """Crée la structure d'un projet de science des données"""
        if technology_id == "jupyter":
            os.makedirs(os.path.join(project_path, "notebooks"), exist_ok=True)
            os.makedirs(os.path.join(project_path, "data"), exist_ok=True)
            os.makedirs(os.path.join(project_path, "src"), exist_ok=True)
            
            # Créer requirements.txt
            with open(os.path.join(project_path, "requirements.txt"), "w", encoding="utf-8") as f:
                f.write("jupyter>=1.0.0\n")
                f.write("pandas>=2.0.0\n")
                f.write("numpy>=1.24.0\n")
                f.write("matplotlib>=3.7.0\n")
                f.write("seaborn>=0.12.0\n")
            
            # Créer un notebook exemple
            notebook = {
                "cells": [
                    {
                        "cell_type": "markdown",
                        "metadata": {},
                        "source": [
                            f"# {project_name} - Analyse de données\n",
                            "\n",
                            "Ce notebook contient une analyse de données pour le projet."
                        ]
                    },
                    {
                        "cell_type": "code",
                        "execution_count": None,
                        "metadata": {},
                        "outputs": [],
                        "source": [
                            "import pandas as pd\n",
                            "import numpy as np\n",
                            "import matplotlib.pyplot as plt\n",
                            "import seaborn as sns\n",
                            "\n",
                            "# Configuration du style des graphiques\n",
                            "plt.style.use('seaborn')\n",
                            "sns.set(font_scale=1.2)"
                        ]
                    }
                ],
                "metadata": {
                    "kernelspec": {
                        "display_name": "Python 3",
                        "language": "python",
                        "name": "python3"
                    },
                    "language_info": {
                        "codemirror_mode": {
                            "name": "ipython",
                            "version": 3
                        },
                        "file_extension": ".py",
                        "mimetype": "text/x-python",
                        "name": "python",
                        "nbconvert_exporter": "python",
                        "pygments_lexer": "ipython3",
                        "version": "3.10.0"
                    }
                },
                "nbformat": 4,
                "nbformat_minor": 5
            }
            
            with open(os.path.join(project_path, "notebooks", "exemple.ipynb"), "w", encoding="utf-8") as f:
                json.dump(notebook, f, indent=2)
    
    @staticmethod
    def _create_iot_project(project_path, technology_id, project_name):
        """Crée la structure d'un projet IoT"""
        if technology_id == "raspberry-pi":
            os.makedirs(os.path.join(project_path, "src"), exist_ok=True)
            os.makedirs(os.path.join(project_path, "config"), exist_ok=True)
            
            # Créer requirements.txt
            with open(os.path.join(project_path, "requirements.txt"), "w", encoding="utf-8") as f:
                f.write("RPi.GPIO>=0.7.0\n")
                f.write("gpiozero>=1.6.0\n")
            
            # Créer main.py
            with open(os.path.join(project_path, "main.py"), "w", encoding="utf-8") as f:
                f.write("#!/usr/bin/env python3\n")
                f.write("# -*- coding: utf-8 -*-\n\n")
                f.write("try:\n")
                f.write("    import RPi.GPIO as GPIO\n")
                f.write("    from gpiozero import LED, Button\n")
                f.write("    import time\n")
                f.write("    import signal\n")
                f.write("except ImportError:\n")
                f.write("    print(\"ATTENTION: Ce code est conçu pour fonctionner sur un Raspberry Pi.\")\n")
                f.write("    print(\"Les bibliothèques nécessaires ne sont pas disponibles sur cette plateforme.\")\n")
                f.write("    exit(1)\n\n")
                f.write("# Configuration\n")
                f.write("GPIO.setmode(GPIO.BCM)\n")
                f.write("GPIO.setwarnings(False)\n\n")
                f.write("# Définir les broches\n")
                f.write("LED_PIN = 17\n")
                f.write("BUTTON_PIN = 18\n\n")
                f.write("# Initialiser les composants\n")
                f.write("led = LED(LED_PIN)\n")
                f.write("button = Button(BUTTON_PIN)\n\n")
                f.write("# Fonctions\n")
                f.write("def on_button_pressed():\n")
                f.write("    print(\"Bouton pressé - LED allumée\")\n")
                f.write("    led.on()\n\n")
                f.write("def on_button_released():\n")
                f.write("    print(\"Bouton relâché - LED éteinte\")\n")
                f.write("    led.off()\n\n")
                f.write("# Configurer les événements\n")
                f.write("button.when_pressed = on_button_pressed\n")
                f.write("button.when_released = on_button_released\n\n")
                f.write("print(\"Programme démarré. Appuyez sur le bouton pour allumer la LED. Ctrl+C pour quitter.\")\n\n")
                f.write("# Maintenir le programme en cours d'exécution\n")
                f.write("try:\n")
                f.write("    signal.pause()\n")
                f.write("except KeyboardInterrupt:\n")
                f.write("    print(\"\\nProgramme arrêté\")\n")
                f.write("    GPIO.cleanup()\n")
                
    @staticmethod
    def _create_blockchain_project(project_path, technology_id, project_name):
        """Crée la structure d'un projet blockchain"""
        os.makedirs(os.path.join(project_path, "contracts"), exist_ok=True)
        os.makedirs(os.path.join(project_path, "scripts"), exist_ok=True)
        os.makedirs(os.path.join(project_path, "test"), exist_ok=True)
        
        if technology_id == "ethereum":
            # Créer la structure pour un projet Ethereum/Solidity
            os.makedirs(os.path.join(project_path, "migrations"), exist_ok=True)
            
            # Créer un contrat Solidity de base
            with open(os.path.join(project_path, "contracts", "SimpleStorage.sol"), "w", encoding="utf-8") as f:
                f.write("// SPDX-License-Identifier: MIT\n")
                f.write("pragma solidity ^0.8.0;\n\n")
                f.write(f"contract SimpleStorage {{\n")
                f.write("    uint256 private value;\n\n")
                f.write("    function set(uint256 _value) public {\n")
                f.write("        value = _value;\n")
                f.write("    }\n\n")
                f.write("    function get() public view returns (uint256) {\n")
                f.write("        return value;\n")
                f.write("    }\n")
                f.write("}\n")
            
            # Créer package.json pour Truffle
            package_json = {
                "name": project_name.lower().replace(' ', '-'),
                "version": "1.0.0",
                "description": "Ethereum Smart Contract Project",
                "main": "truffle-config.js",
                "scripts": {
                    "test": "truffle test",
                    "compile": "truffle compile",
                    "migrate": "truffle migrate",
                    "deploy": "truffle migrate --network development"
                },
                "dependencies": {
                    "@openzeppelin/contracts": "^4.8.0",
                    "@truffle/hdwallet-provider": "^2.1.0"
                },
                "devDependencies": {
                    "truffle": "^5.7.0",
                    "chai": "^4.3.7",
                    "dotenv": "^16.0.3"
                }
            }
            
            with open(os.path.join(project_path, "package.json"), "w", encoding="utf-8") as f:
                json.dump(package_json, f, indent=2)
            
            # Créer truffle-config.js
            with open(os.path.join(project_path, "truffle-config.js"), "w", encoding="utf-8") as f:
                f.write("/**\n * Truffle configuration file\n */\n\n")
                f.write("require('dotenv').config();\n\n")
                f.write("module.exports = {\n")
                f.write("  networks: {\n")
                f.write("    development: {\n")
                f.write("      host: \"127.0.0.1\",\n")
                f.write("      port: 8545,\n")
                f.write("      network_id: \"*\"\n")
                f.write("    }\n")
                f.write("  },\n\n")
                f.write("  compilers: {\n")
                f.write("    solc: {\n")
                f.write("      version: \"0.8.17\",\n")
                f.write("      settings: {\n")
                f.write("        optimizer: {\n")
                f.write("          enabled: true,\n")
                f.write("          runs: 200\n")
                f.write("        }\n")
                f.write("      }\n")
                f.write("    }\n")
                f.write("  }\n")
                f.write("};\n")
                
        elif technology_id == "hardhat":
            # Créer la structure pour un projet Hardhat
            os.makedirs(os.path.join(project_path, "contracts"), exist_ok=True)
            os.makedirs(os.path.join(project_path, "scripts"), exist_ok=True)
            os.makedirs(os.path.join(project_path, "test"), exist_ok=True)
            
            # Créer package.json pour Hardhat
            package_json = {
                "name": project_name.lower().replace(' ', '-'),
                "version": "1.0.0",
                "description": "Hardhat Ethereum Project",
                "scripts": {
                    "test": "hardhat test",
                    "compile": "hardhat compile",
                    "deploy": "hardhat run scripts/deploy.js --network localhost",
                    "node": "hardhat node"
                },
                "devDependencies": {
                    "@nomicfoundation/hardhat-toolbox": "^2.0.0",
                    "@nomiclabs/hardhat-ethers": "^2.2.1",
                    "@nomiclabs/hardhat-waffle": "^2.0.3",
                    "chai": "^4.3.7",
                    "dotenv": "^16.0.3",
                    "ethers": "^5.7.2",
                    "hardhat": "^2.12.4"
                },
                "dependencies": {
                    "@openzeppelin/contracts": "^4.8.0"
                }
            }
            
            with open(os.path.join(project_path, "package.json"), "w", encoding="utf-8") as f:
                json.dump(package_json, f, indent=2)
                
            # Créer hardhat.config.js
            with open(os.path.join(project_path, "hardhat.config.js"), "w", encoding="utf-8") as f:
                f.write("require('@nomicfoundation/hardhat-toolbox');\n")
                f.write("require('dotenv').config();\n\n")
                f.write("/** @type import('hardhat/config').HardhatUserConfig */\n")
                f.write("module.exports = {\n")
                f.write("  solidity: \"0.8.17\",\n")
                f.write("  networks: {\n")
                f.write("    localhost: {\n")
                f.write("      url: \"http://127.0.0.1:8545\"\n")
                f.write("    }\n")
                f.write("  }\n")
                f.write("};\n")
                
            # Créer un script de déploiement
            with open(os.path.join(project_path, "scripts", "deploy.js"), "w", encoding="utf-8") as f:
                f.write("// Script de déploiement\n\n")
                f.write("async function main() {\n")
                f.write("  const [deployer] = await ethers.getSigners();\n\n")
                f.write("  console.log(\"Déploiement des contrats avec le compte:\", deployer.address);\n\n")
                f.write("  const SimpleStorage = await ethers.getContractFactory(\"SimpleStorage\");\n")
                f.write("  const simpleStorage = await SimpleStorage.deploy();\n\n")
                f.write("  console.log(\"Contrat SimpleStorage déployé à l'adresse:\", simpleStorage.address);\n")
                f.write("}\n\n")
                f.write("main()\n")
                f.write("  .then(() => process.exit(0))\n")
                f.write("  .catch((error) => {\n")
                f.write("    console.error(error);\n")
                f.write("    process.exit(1);\n")
                f.write("  });\n")
                
    @staticmethod
    def _create_ai_project(project_path, technology_id, project_name):
        """Crée la structure d'un projet d'intelligence artificielle"""
        os.makedirs(os.path.join(project_path, "data"), exist_ok=True)
        os.makedirs(os.path.join(project_path, "data", "raw"), exist_ok=True)
        os.makedirs(os.path.join(project_path, "data", "processed"), exist_ok=True)
        os.makedirs(os.path.join(project_path, "models"), exist_ok=True)
        os.makedirs(os.path.join(project_path, "notebooks"), exist_ok=True)
        os.makedirs(os.path.join(project_path, "src"), exist_ok=True)
        os.makedirs(os.path.join(project_path, "tests"), exist_ok=True)
        
        # Créer un fichier .gitignore pour les projets d'IA
        with open(os.path.join(project_path, ".gitignore"), "w", encoding="utf-8") as f:
            f.write("# Fichiers Python\n")
            f.write("__pycache__/\n")
            f.write("*.py[cod]\n")
            f.write("*$py.class\n")
            f.write("*.so\n")
            f.write(".Python\n")
            f.write("env/\n")
            f.write("build/\n")
            f.write("develop-eggs/\n")
            f.write("dist/\n")
            f.write("downloads/\n")
            f.write("eggs/\n")
            f.write(".eggs/\n")
            f.write("lib/\n")
            f.write("lib64/\n")
            f.write("parts/\n")
            f.write("sdist/\n")
            f.write("var/\n")
            f.write("*.egg-info/\n")
            f.write(".installed.cfg\n")
            f.write("*.egg\n\n")
            f.write("# Environnements virtuels\n")
            f.write("venv/\n")
            f.write("ENV/\n")
            f.write("env.bak/\n")
            f.write("venv.bak/\n\n")
            f.write("# Fichiers de données volumineux\n")
            f.write("data/raw/*\n")
            f.write("!data/raw/.gitkeep\n")
            f.write("models/*.h5\n")
            f.write("models/*.pkl\n")
            f.write("models/*.joblib\n")
            f.write("models/*.onnx\n\n")
            f.write("# Notebooks Jupyter\n")
            f.write(".ipynb_checkpoints\n")
            
        # Créer des fichiers .gitkeep pour conserver la structure des dossiers
        open(os.path.join(project_path, "data", "raw", ".gitkeep"), "w").close()
        open(os.path.join(project_path, "data", "processed", ".gitkeep"), "w").close()
        open(os.path.join(project_path, "models", ".gitkeep"), "w").close()
        
        if technology_id == "tensorflow":
            # Créer requirements.txt pour TensorFlow
            with open(os.path.join(project_path, "requirements.txt"), "w", encoding="utf-8") as f:
                f.write("tensorflow>=2.10.0\n")
                f.write("numpy>=1.23.0\n")
                f.write("pandas>=1.5.0\n")
                f.write("matplotlib>=3.6.0\n")
                f.write("scikit-learn>=1.1.0\n")
                f.write("jupyter>=1.0.0\n")
                f.write("tensorboard>=2.10.0\n")
                f.write("tensorflow-datasets>=4.7.0\n")
            
            # Créer un exemple de script d'entraînement
            with open(os.path.join(project_path, "src", "train.py"), "w", encoding="utf-8") as f:
                f.write("#!/usr/bin/env python3\n")
                f.write("# -*- coding: utf-8 -*-\n\n")
                f.write("import os\n")
                f.write("import numpy as np\n")
                f.write("import tensorflow as tf\n")
                f.write("from tensorflow import keras\n")
                f.write("from tensorflow.keras import layers\n")
                f.write("import matplotlib.pyplot as plt\n\n")
                f.write("# Définir les chemins\n")
                f.write("MODEL_DIR = os.path.join('..', 'models')\n")
                f.write("DATA_DIR = os.path.join('..', 'data')\n\n")
                f.write("# Charger et préparer les données (exemple avec MNIST)\n")
                f.write("def load_data():\n")
                f.write("    print('Chargement des données...')\n")
                f.write("    (x_train, y_train), (x_test, y_test) = keras.datasets.mnist.load_data()\n")
                f.write("    # Normaliser les données\n")
                f.write("    x_train = x_train.astype('float32') / 255.0\n")
                f.write("    x_test = x_test.astype('float32') / 255.0\n")
                f.write("    # Ajouter une dimension pour le canal (nécessaire pour CNN)\n")
                f.write("    x_train = np.expand_dims(x_train, -1)\n")
                f.write("    x_test = np.expand_dims(x_test, -1)\n")
                f.write("    return (x_train, y_train), (x_test, y_test)\n\n")
                f.write("# Créer le modèle\n")
                f.write("def create_model():\n")
                f.write("    model = keras.Sequential([\n")
                f.write("        layers.Input(shape=(28, 28, 1)),\n")
                f.write("        layers.Conv2D(32, kernel_size=(3, 3), activation='relu'),\n")
                f.write("        layers.MaxPooling2D(pool_size=(2, 2)),\n")
                f.write("        layers.Conv2D(64, kernel_size=(3, 3), activation='relu'),\n")
                f.write("        layers.MaxPooling2D(pool_size=(2, 2)),\n")
                f.write("        layers.Flatten(),\n")
                f.write("        layers.Dropout(0.5),\n")
                f.write("        layers.Dense(10, activation='softmax')\n")
                f.write("    ])\n\n")
                f.write("    model.compile(\n")
                f.write("        loss='sparse_categorical_crossentropy',\n")
                f.write("        optimizer='adam',\n")
                f.write("        metrics=['accuracy']\n")
                f.write("    )\n")
                f.write("    return model\n\n")
                f.write("# Fonction principale\n")
                f.write("def main():\n")
                f.write("    # Charger les données\n")
                f.write("    (x_train, y_train), (x_test, y_test) = load_data()\n\n")
                f.write("    # Créer le modèle\n")
                f.write("    model = create_model()\n")
                f.write("    print(model.summary())\n\n")
                f.write("    # Callbacks\n")
                f.write("    callbacks = [\n")
                f.write("        keras.callbacks.ModelCheckpoint(\n")
                f.write("            filepath=os.path.join(MODEL_DIR, 'best_model.h5'),\n")
                f.write("            save_best_only=True,\n")
                f.write("            monitor='val_accuracy'\n")
                f.write("        ),\n")
                f.write("        keras.callbacks.TensorBoard(\n")
                f.write("            log_dir=os.path.join(MODEL_DIR, 'logs'),\n")
                f.write("            histogram_freq=1\n")
                f.write("        )\n")
                f.write("    ]\n\n")
                f.write("    # Entraîner le modèle\n")
                f.write("    print('Début de l\'entraînement...')\n")
                f.write("    history = model.fit(\n")
                f.write("        x_train, y_train,\n")
                f.write("        batch_size=128,\n")
                f.write("        epochs=10,\n")
                f.write("        validation_split=0.1,\n")
                f.write("        callbacks=callbacks\n")
                f.write("    )\n\n")
                f.write("    # Évaluer le modèle\n")
                f.write("    print('\nÉvaluation du modèle...')\n")
                f.write("    score = model.evaluate(x_test, y_test, verbose=0)\n")
                f.write("    print(f'Score de test: {score[0]:.4f}')\n")
                f.write("    print(f'Précision de test: {score[1]:.4f}')\n\n")
                f.write("    # Sauvegarder le modèle final\n")
                f.write("    model.save(os.path.join(MODEL_DIR, 'final_model.h5'))\n")
                f.write("    print(f'Modèle sauvegardé dans {os.path.join(MODEL_DIR, \"final_model.h5\")}')\n\n")
                f.write("if __name__ == '__main__':\n")
                f.write("    main()\n")
                
        elif technology_id == "pytorch":
            # Créer requirements.txt pour PyTorch
            with open(os.path.join(project_path, "requirements.txt"), "w", encoding="utf-8") as f:
                f.write("torch>=1.13.0\n")
                f.write("torchvision>=0.14.0\n")
                f.write("numpy>=1.23.0\n")
                f.write("pandas>=1.5.0\n")
                f.write("matplotlib>=3.6.0\n")
                f.write("scikit-learn>=1.1.0\n")
                f.write("jupyter>=1.0.0\n")
                f.write("tensorboard>=2.10.0\n")
                
            # Créer un exemple de script d'entraînement PyTorch
            with open(os.path.join(project_path, "src", "train.py"), "w", encoding="utf-8") as f:
                f.write("#!/usr/bin/env python3\n")
                f.write("# -*- coding: utf-8 -*-\n\n")
                f.write("import os\n")
                f.write("import torch\n")
                f.write("import torch.nn as nn\n")
                f.write("import torch.optim as optim\n")
                f.write("import torch.nn.functional as F\n")
                f.write("from torchvision import datasets, transforms\n")
                f.write("from torch.utils.data import DataLoader\n")
                f.write("from torch.utils.tensorboard import SummaryWriter\n\n")
                f.write("# Définir les chemins\n")
                f.write("MODEL_DIR = os.path.join('..', 'models')\n")
                f.write("DATA_DIR = os.path.join('..', 'data')\n\n")
                f.write("# Définir le dispositif d'exécution (GPU si disponible)\n")
                f.write("device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')\n")
                f.write("print(f'Utilisation du dispositif: {device}')\n\n")
                f.write("# Définir les transformations et charger les données\n")
                f.write("def load_data(batch_size=64):\n")
                f.write("    transform = transforms.Compose([\n")
                f.write("        transforms.ToTensor(),\n")
                f.write("        transforms.Normalize((0.1307,), (0.3081,))\n")
                f.write("    ])\n\n")
                f.write("    train_dataset = datasets.MNIST(\n")
                f.write("        os.path.join(DATA_DIR, 'raw'),\n")
                f.write("        train=True,\n")
                f.write("        download=True,\n")
                f.write("        transform=transform\n")
                f.write("    )\n\n")
                f.write("    test_dataset = datasets.MNIST(\n")
                f.write("        os.path.join(DATA_DIR, 'raw'),\n")
                f.write("        train=False,\n")
                f.write("        transform=transform\n")
                f.write("    )\n\n")
                f.write("    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)\n")
                f.write("    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)\n\n")
                f.write("    return train_loader, test_loader\n\n")
                f.write("# Définir le modèle\n")
                f.write("class ConvNet(nn.Module):\n")
                f.write("    def __init__(self):\n")
                f.write("        super(ConvNet, self).__init__()\n")
                f.write("        self.conv1 = nn.Conv2d(1, 32, 3, 1)\n")
                f.write("        self.conv2 = nn.Conv2d(32, 64, 3, 1)\n")
                f.write("        self.dropout1 = nn.Dropout2d(0.25)\n")
                f.write("        self.dropout2 = nn.Dropout2d(0.5)\n")
                f.write("        self.fc1 = nn.Linear(9216, 128)\n")
                f.write("        self.fc2 = nn.Linear(128, 10)\n\n")
                f.write("    def forward(self, x):\n")
                f.write("        x = self.conv1(x)\n")
                f.write("        x = F.relu(x)\n")
                f.write("        x = self.conv2(x)\n")
                f.write("        x = F.relu(x)\n")
                f.write("        x = F.max_pool2d(x, 2)\n")
                f.write("        x = self.dropout1(x)\n")
                f.write("        x = torch.flatten(x, 1)\n")
                f.write("        x = self.fc1(x)\n")
                f.write("        x = F.relu(x)\n")
                f.write("        x = self.dropout2(x)\n")
                f.write("        x = self.fc2(x)\n")
                f.write("        output = F.log_softmax(x, dim=1)\n")
                f.write("        return output\n\n")
                f.write("# Fonction d'entraînement\n")
                f.write("def train(model, train_loader, optimizer, epoch, writer):\n")
                f.write("    model.train()\n")
                f.write("    for batch_idx, (data, target) in enumerate(train_loader):\n")
                f.write("        data, target = data.to(device), target.to(device)\n")
                f.write("        optimizer.zero_grad()\n")
                f.write("        output = model(data)\n")
                f.write("        loss = F.nll_loss(output, target)\n")
                f.write("        loss.backward()\n")
                f.write("        optimizer.step()\n")
                f.write("        if batch_idx % 100 == 0:\n")
                f.write("            print(f'Epoch: {epoch} [{batch_idx * len(data)}/{len(train_loader.dataset)} "
                      f"({100. * batch_idx / len(train_loader):.0f}%)]\tLoss: {loss.item():.6f}')\n")
                f.write("            writer.add_scalar('training_loss', loss.item(), epoch * len(train_loader) + batch_idx)\n\n")
                f.write("# Fonction d'évaluation\n")
                f.write("def test(model, test_loader, writer, epoch):\n")
                f.write("    model.eval()\n")
                f.write("    test_loss = 0\n")
                f.write("    correct = 0\n")
                f.write("    with torch.no_grad():\n")
                f.write("        for data, target in test_loader:\n")
                f.write("            data, target = data.to(device), target.to(device)\n")
                f.write("            output = model(data)\n")
                f.write("            test_loss += F.nll_loss(output, target, reduction='sum').item()\n")
                f.write("            pred = output.argmax(dim=1, keepdim=True)\n")
                f.write("            correct += pred.eq(target.view_as(pred)).sum().item()\n\n")
                f.write("    test_loss /= len(test_loader.dataset)\n")
                f.write("    accuracy = 100. * correct / len(test_loader.dataset)\n\n")
                f.write("    print(f'Test set: Average loss: {test_loss:.4f}, "
                      f"Accuracy: {correct}/{len(test_loader.dataset)} ({accuracy:.2f}%)')\n\n")
                f.write("    writer.add_scalar('test_loss', test_loss, epoch)\n")
                f.write("    writer.add_scalar('test_accuracy', accuracy, epoch)\n")
                f.write("    return accuracy\n\n")
                f.write("# Fonction principale\n")
                f.write("def main():\n")
                f.write("    # Paramètres\n")
                f.write("    batch_size = 64\n")
                f.write("    epochs = 10\n")
                f.write("    lr = 0.01\n")
                f.write("    log_dir = os.path.join(MODEL_DIR, 'logs')\n")
                f.write("    os.makedirs(log_dir, exist_ok=True)\n\n")
                f.write("    # Initialiser le writer pour TensorBoard\n")
                f.write("    writer = SummaryWriter(log_dir)\n\n")
                f.write("    # Charger les données\n")
                f.write("    train_loader, test_loader = load_data(batch_size)\n\n")
                f.write("    # Créer le modèle\n")
                f.write("    model = ConvNet().to(device)\n")
                f.write("    optimizer = optim.SGD(model.parameters(), lr=lr, momentum=0.9)\n")
                f.write("    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=1, gamma=0.7)\n\n")
                f.write("    # Entraîner le modèle\n")
                f.write("    best_accuracy = 0\n")
                f.write("    for epoch in range(1, epochs + 1):\n")
                f.write("        print(f'\nEpoch {epoch}/{epochs}')\n")
                f.write("        train(model, train_loader, optimizer, epoch, writer)\n")
                f.write("        accuracy = test(model, test_loader, writer, epoch)\n")
                f.write("        scheduler.step()\n\n")
                f.write("        # Sauvegarder le meilleur modèle\n")
                f.write("        if accuracy > best_accuracy:\n")
                f.write("            best_accuracy = accuracy\n")
                f.write("            torch.save(model.state_dict(), os.path.join(MODEL_DIR, 'best_model.pt'))\n")
                f.write("            print(f'Nouveau meilleur modèle sauvegardé avec une précision de {best_accuracy:.2f}%')\n\n")
                f.write("    # Sauvegarder le modèle final\n")
                f.write("    torch.save(model.state_dict(), os.path.join(MODEL_DIR, 'final_model.pt'))\n")
                f.write("    print(f'Modèle final sauvegardé dans {os.path.join(MODEL_DIR, \"final_model.pt\")}')\n\n")
                f.write("    writer.close()\n\n")
                f.write("if __name__ == '__main__':\n")
                f.write("    main()\n")
