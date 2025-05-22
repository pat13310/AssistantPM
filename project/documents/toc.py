# toc.py

TOC_STRUCTURE = {
    "Cahier des Charges Fonctionnel": {
        "Introduction": {
            "Contexte": {
                "Historique de l’organisation": {},
                "Motivation du projet": {},
                "Situation actuelle": {}
            },
            "Présentation générale du projet": {
                "Description succincte": {},
                "Objectifs stratégiques": {},
                "Sponsors du projet": {}
            },
            "Enjeux métiers": {
                "Opportunités": {},
                "Risques métier": {},
                "Impacts prévus": {}
            },
            "Historique du besoin": {},
            "Parties prenantes": {
                "Clients": {},
                "Équipe projet": {},
                "Autres intervenants": {}
            }
        },
        "Objectifs du projet": {
            "Objectifs fonctionnels": {
                "Amélioration des processus": {},
                "Automatisation": {},
                "Expérience utilisateur": {},
                "Interfaçage avec systèmes existants": {}
            },
            "Objectifs non fonctionnels": {
                "Performance": {},
                "Sécurité": {},
                "Fiabilité": {},
                "Conformité réglementaire": {},
                "Maintenabilité": {}
            },
            "Indicateurs de succès": {
                "KPI métiers": {},
                "Mesures de satisfaction": {},
                "Délais de réalisation": {}
            }
        },
        "Périmètre": {
            "Fonctionnalités incluses": {
                "Liste des modules": {},
                "Comportements attendus": {}
            },
            "Fonctionnalités exclues": {},
            "Interfaces concernées": {
                "Systèmes amont": {},
                "Systèmes aval": {}
            },
            "Frontières du système": {}
        },
        "Acteurs et utilisateurs": {
            "Description des utilisateurs": {
                "Utilisateurs internes": {},
                "Utilisateurs externes": {}
            },
            "Rôles et responsabilités": {},
            "Interactions entre les acteurs": {},
            "Cas particuliers": {}
        },
        "Contraintes": {
            "Contraintes techniques": {
                "Technologies imposées": {},
                "Standards d'intégration": {}
            },
            "Contraintes organisationnelles": {},
            "Contraintes budgétaires": {},
            "Contraintes temporelles": {},
            "Contraintes légales": {}
        },
        "Glossaire": {
            "Termes métier": {},
            "Acronymes": {},
            "Références externes": {}
        }
    },

    "Spécifications Fonctionnelles Détaillées": {
        "Vue d'ensemble": {
            "Fonctionnalités principales": {},
            "Flux généraux d'utilisation": {},
            "Cartographie des fonctionnalités": {}
        },
        "Cas d'utilisation": {
            "Diagrammes de cas d'utilisation": {},
            "Descriptions textuelles": {
                "Acteurs impliqués": {},
                "Déroulement principal": {},
                "Scénarios alternatifs": {}
            },
            "Pré/post-conditions": {},
            "Exceptions et erreurs": {}
        },
        "Maquettes / Wireframes": {
            "Écrans principaux": {},
            "Parcours utilisateur": {},
            "Navigation entre les vues": {},
            "Accessibilité visuelle": {}
        },
        "Règles métier": {
            "Règles de gestion": {},
            "Contraintes métier": {},
            "Exceptions": {},
            "Dépendances externes": {}
        },
        "Gestion des erreurs": {
            "Types d’erreurs": {},
            "Comportement du système": {},
            "Messages utilisateur": {},
            "Codes de retour": {}
        },
        "Exigences spécifiques": {
            "Accessibilité": {},
            "Compatibilité navigateur": {},
            "Responsive design": {},
            "Internationalisation": {},
            "Temps de chargement": {},
            "Séparation présentation/logique": {}
        }
    },

    "Spécifications Techniques Détaillées": {
        "Architecture générale": {
            "Architecture logicielle": {
                "MVC / microservices / autres": {},
                "Composants logiciels": {}
            },
            "Architecture matérielle": {},
            "Services externes": {},
            "Modèle de déploiement": {}
        },
        "Choix technologiques": {
            "Langages de programmation": {},
            "Frameworks et bibliothèques": {},
            "Base de données": {
                "Type": {},
                "Modèle de données": {}
            },
            "Protocoles d’échange": {},
            "Outils tiers": {},
            "Critères de sélection": {}
        },
        "Sécurité": {
            "Authentification et autorisation": {},
            "Protection des données": {},
            "Audit et journalisation": {},
            "Gestion des sessions": {},
            "Gestion des vulnérabilités": {},
            "Mise à jour sécurité": {}
        },
        "Performance et scalabilité": {
            "Temps de réponse": {},
            "Montée en charge": {},
            "Tests de performance": {},
            "Caching": {},
            "Tolérance aux pannes": {},
            "Load balancing": {}
        }
    },

    "Stratégie de Tests et Recette": {
        "Types de tests": {
            "Tests unitaires": {},
            "Tests d’intégration": {},
            "Tests de validation": {},
            "Tests de performance": {},
            "Tests de non-régression": {},
            "Tests de sécurité": {},
            "Tests d’accessibilité": {}
        },
        "Plan de test": {
            "Stratégie globale": {},
            "Périmètre des tests": {},
            "Enchaînements de tests": {},
            "Matrice de couverture": {},
            "Critères de sortie": {}
        },
        "Critères d’acceptation": {
            "Exemples concrets": {},
            "Tests bloquants": {},
            "Résultats attendus": {},
            "Conditions de succès": {}
        },
        "Environnement de test": {
            "Configuration matérielle": {},
            "Jeux de données": {},
            "Outils utilisés": {},
            "Virtualisation": {},
            "Accès aux environnements": {}
        },
        "Suivi et gestion des anomalies": {
            "Processus de remontée": {},
            "Outils de suivi": {},
            "Priorisation des bugs": {},
            "Cycle de vie des anomalies": {},
            "Taux de correction": {}
        }
    },

    "Dossier d'Architecture Technique": {
        "Schémas d’architecture": {
            "Vue logique": {},
            "Vue physique": {},
            "Diagrammes UML": {},
            "Architecture réseau": {},
            "Architecture applicative": {}
        },
        "Composants principaux": {
            "Description des modules": {},
            "Interfaces internes": {},
            "Gestion des dépendances": {},
            "Cycle de vie des composants": {}
        },
        "Flux de données": {
            "Entrées / sorties": {},
            "Traitements métier": {},
            "Synchronisation": {},
            "Orchestration des services": {},
            "Traçabilité": {}
        },
        "Déploiement et hébergement": {
            "Infrastructure cible": {},
            "Automatisation CI/CD": {},
            "Conteneurisation": {},
            "Séparation environnements": {},
            "Matrice de déploiement": {}
        },
        "Surveillance et maintenance": {
            "Monitoring": {},
            "Logs et alertes": {},
            "Maintenance préventive": {},
            "Métriques système": {},
            "Plan de reprise": {},
            "Escalade et support": {}
        }
    }
}
