from components.infos.models import Phase, Question



quick_access_phases = [
    Phase(
        id="accueil",   
        title="Accueil",
        description="Page d'accueil de l'application",
        icon="house",
        color="gray",

    ),
    Phase(
        id="documentation",
        title="Documentation",
        description="Documentation du projet",
        icon="book-open",
        color="blue",
        order=1,
    ),
    Phase(
        id="code",
        title="Code",
        description="Code source du projet",
        icon="code",
        color="green",
        order=2,
    ),
    Phase(
        id="architecture",
        title="Architecture",
        description="Architecture du projet",
        icon="folder-tree",
        color="orange",
        order=3,
    ),
    Phase(
        id="tests",
        title="Tests",
        description="Tests du projet",
        icon="test-tube",
        color="red",
        order=4,    
    ),
    Phase(
        id="deploiement",
        title="Déploiement",
        description="Déploiement du projet",
        icon="rocket",
        color="purple",
        order=5,
    ),
    Phase(
        id="monitoring",
        title="Monitoring",
        description="Surveillance du projet",
        icon="eye",
        color="yellow",
        order=6,
    ),
]

initial_phases = [
    Phase(
        id="analyse",
        title="Analyse des Besoins",
        description="Identification structurée des objectifs, utilisateurs, fonctionnalités et contraintes",
        icon="search",
        color="blue",
        order=1,
        prevPhase=None,
        nextPhase="conception",
        questions=[
            Question(
                id="analyse_objectifs",
                text="Quels sont les objectifs principaux du projet ?",
                suggestions=["Objectifs métier", "Objectifs techniques"],
                sousSuggestions={
                    "Objectifs métier": [
                        "Augmenter la satisfaction client",
                        "Améliorer les performances internes",
                        "Accroître les revenus",
                        "Optimiser les processus métiers",
                    ],
                    "Objectifs techniques": [
                        "Automatiser des tâches manuelles",
                        "Réduire les temps de traitement",
                        "Améliorer la sécurité",
                        "Faciliter la maintenance future",
                    ],
                },
                bestPractices="Formulez les objectifs selon la méthode SMART (Spécifique, Mesurable, Atteignable, Réaliste, Temporel).",
            ),
            Question(
                id="analyse_utilisateurs",
                text="Qui sont les utilisateurs cibles ?",
                suggestions=["Utilisateurs internes", "Utilisateurs externes"],
                sousSuggestions={
                    "Utilisateurs internes": [
                        "Employés de production",
                        "Cadres / managers",
                        "Support technique",
                    ],
                    "Utilisateurs externes": [
                        "Clients finaux",
                        "Partenaires commerciaux",
                        "Grand public",
                    ],
                },
                bestPractices="Créez des personas détaillés incluant les besoins, contextes d'utilisation et attentes pour chaque groupe d'utilisateurs.",
            ),
            Question(
                id="analyse_fonctionnalites",
                text="Quelles fonctionnalités sont indispensables ?",
                suggestions=["Fonctionnalités métier", "Fonctionnalités transverses"],
                sousSuggestions={
                    "Fonctionnalités métier": [
                        "Gestion des dossiers clients",
                        "Suivi des commandes",
                        "Facturation",
                    ],
                    "Fonctionnalités transverses": [
                        "Authentification / gestion utilisateurs",
                        "Notifications par email ou SMS",
                        "Export PDF ou Excel",
                        "Tableaux de bord",
                    ],
                },
                bestPractices="Utilisez la méthode MoSCoW pour prioriser : Must / Should / Could / Won’t have.",
            ),
            Question(
                id="analyse_contraintes",
                text="Quelles contraintes influencent le projet ?",
                suggestions=[
                    "Contraintes techniques",
                    "Contraintes organisationnelles",
                    "Contraintes réglementaires",
                ],
                sousSuggestions={
                    "Contraintes techniques": [
                        "Intégration avec systèmes existants",
                        "Choix imposé de langage ou base de données",
                        "Limites d’hébergement ou infrastructure",
                    ],
                    "Contraintes organisationnelles": [
                        "Budget limité",
                        "Délais serrés",
                        "Compétences internes restreintes",
                    ],
                    "Contraintes réglementaires": [
                        "Conformité RGPD",
                        "Traçabilité des actions",
                        "Archivage légal",
                    ],
                },
                bestPractices="Pour chaque contrainte, analysez son impact et les risques associés. Proposez des mesures d'atténuation ou d'adaptation.",
            ),
        ],
    ),
    Phase(
        id="conception",
        title="Conception",
        description="Décisions structurées sur l'architecture, la stack technique, l'interface, les données et les validations",
        icon="penTool",
        color="purple",
        order=2,
        prevPhase="analyse",
        nextPhase="developpement",
        questions=[
            Question(
                id="conception_architecture",
                text="Quelle architecture logicielle allez-vous adopter ?",
                suggestions=["Architecture applicative", "Distribution logicielle"],
                sousSuggestions={
                    "Architecture applicative": [
                        "Monolithique",
                        "Microservices",
                        "SOA (Services orientés)",
                        "Serverless",
                    ],
                    "Distribution logicielle": [
                        "1 tier (tout intégré)",
                        "2 tiers (frontend ↔ backend)",
                        "3 tiers (frontend ↔ API ↔ DB)",
                        "Événementielle (Kafka, MQ...)",
                    ],
                },
                bestPractices="Choisissez une architecture alignée avec le besoin de scalabilité, les compétences internes, et le budget de déploiement.",
            ),
            Question(
                id="conception_stack",
                text="Quelle stack technique sera utilisée ?",
                suggestions=["Fullstack", "Base de données", "Infrastructure"],
                sousSuggestions={
                    "Fullstack": {
                        "Frontend": [
                            "React (TypeScript)",
                            "Vue.js (Composition API)",
                            "Angular",
                            "Svelte",
                        ],
                        "Backend": [
                            "Node.js → Express, NestJS",
                            "Python → Django, FastAPI",
                            "Java → Spring Boot",
                            "Go → Gin",
                            "PHP → Laravel",
                        ],
                    },
                    "Base de données": [
                        "PostgreSQL",
                        "MySQL / MariaDB",
                        "SQLite (léger)",
                        "MongoDB (NoSQL)",
                        "Redis (cache)",
                    ],
                    "Infrastructure": [
                        "Docker",
                        "Kubernetes",
                        "AWS",
                        "Azure",
                        "GCP",
                        "Heroku (PaaS simplifié)",
                    ],
                },
                bestPractices="Assurez la cohérence entre les composants et la capacité de l’équipe à maintenir l’ensemble de la stack choisie.",
            ),
            Question(
                id="conception_uiux",
                text="Comment allez-vous concevoir l'interface utilisateur ?",
                suggestions=["Structure", "Design system", "Accessibilité"],
                sousSuggestions={
                    "Structure": [
                        "Navigation par onglets",
                        "Sidebar + breadcrumbs",
                        "Design responsive",
                    ],
                    "Design system": [
                        "Composants réutilisables",
                        "Thèmes personnalisables",
                        "Mode clair/sombre",
                    ],
                    "Accessibilité": [
                        "Normes WCAG 2.1 niveau AA",
                        "Navigation clavier complète",
                        "Contrastes suffisants",
                    ],
                },
                bestPractices="Débutez par des wireframes basse-fidélité, validez avec les utilisateurs, puis déclinez en maquettes UI réutilisables.",
            ),
            Question(
                id="conception_donnees",
                text="Quel modèle de données adoptez-vous ?",
                suggestions=["Type de stockage", "Organisation des entités"],
                sousSuggestions={
                    "Type de stockage": [
                        "Relationnel (PostgreSQL, MySQL)",
                        "NoSQL document (MongoDB)",
                        "Clé/valeur (Redis)",
                        "Time-series (InfluxDB)",
                    ],
                    "Organisation des entités": [
                        "Modèle entité-relation (MCD)",
                        "UML (classe, relation, héritage)",
                        "Modèle de collections pour MongoDB",
                        "Data vault pour historique",
                    ],
                },
                bestPractices="Adaptez la structure des données aux requêtes métier les plus fréquentes et à l’évolutivité attendue du projet.",
            ),
            Question(
                id="conception_validation",
                text="Comment validez-vous les choix de conception ?",
                suggestions=["Validation technique", "Validation métier"],
                sousSuggestions={
                    "Validation technique": [
                        "Revue entre pairs (architectes)",
                        "Prototype sur use case critique",
                        "Tests de performance préliminaires",
                    ],
                    "Validation métier": [
                        "Démonstration aux parties prenantes",
                        "Validation des wireframes",
                        "Documentation des choix dans un wiki projet",
                    ],
                },
                bestPractices="Formalisez chaque décision : alternatives étudiées, justification du choix, validation obtenue. Archivez dans un référentiel partagé.",
            ),
        ],
    ),
    Phase(
        id="developpement",
        title="Développement",
        description="Implémentation du code, gestion de la qualité, de la sécurité et des environnements",
        icon="code",
        color="teal",
        order=3,
        prevPhase="conception",
        nextPhase="tests",
        questions=[
            Question(
                id="developpement_methodologie",
                text="Quelle méthodologie de développement adopter ?",
                suggestions=[
                    "Méthodes agiles",
                    "Cycle en V",
                    "Méthodes pilotées par la qualité",
                ],
                sousSuggestions={
                    "Méthodes agiles": [
                        "Scrum avec sprints de 2 semaines",
                        "Kanban en flux continu",
                        "SAFe (pour grandes organisations)",
                    ],
                    "Cycle en V": [
                        "Spécifications strictes avant dev",
                        "Tests associés à chaque phase",
                        "Documentation exhaustive",
                    ],
                    "Méthodes pilotées par la qualité": [
                        "Test-Driven Development (TDD)",
                        "Behavior-Driven Development (BDD)",
                        "CI/CD avec tests automatisés",
                    ],
                },
                bestPractices="Adaptez la méthodologie à la taille de l’équipe et au rythme du projet. Priorisez la communication et les itérations courtes.",
            ),
            Question(
                id="developpement_qualite",
                text="Quelles pratiques de qualité code mettre en place ?",
                suggestions=[
                    "Revue de code",
                    "Tests automatisés",
                    "Outils d'analyse",
                    "Documentation",
                ],
                sousSuggestions={
                    "Revue de code": [
                        "Pull request avec approbation obligatoire",
                        "Pair programming",
                        "Checklist de validation",
                    ],
                    "Tests automatisés": [
                        "Tests unitaires (>80% couverture)",
                        "Tests d’intégration",
                        "Tests fonctionnels",
                        "Tests non régression",
                    ],
                    "Outils d'analyse": [
                        "Analyse statique avec SonarQube",
                        "Linting automatisé",
                        "Mesure de complexité cyclomatique",
                    ],
                    "Documentation": [
                        "Docstrings standard (PEP257, JSDoc...)",
                        "Génération automatique (Sphinx, TypeDoc)",
                        "Wikis internes pour les modules complexes",
                    ],
                },
                bestPractices="Définissez des règles de qualité communes, automatisez leur vérification, et suivez des indicateurs dans votre pipeline CI/CD.",
            ),
            Question(
                id="developpement_securite",
                text="Comment garantir la sécurité de l'application ?",
                suggestions=[
                    "Authentification",
                    "Protection des données",
                    "Sécurité applicative",
                    "Tests de sécurité",
                ],
                sousSuggestions={
                    "Authentification": [
                        "Authentification multi-facteurs (MFA)",
                        "OAuth2 / OpenID Connect",
                        "Gestion des sessions sécurisée",
                    ],
                    "Protection des données": [
                        "Chiffrement AES ou RSA",
                        "Hash des mots de passe (bcrypt)",
                        "Tokenisation des données sensibles",
                    ],
                    "Sécurité applicative": [
                        "Validation stricte des entrées",
                        "Protection contre XSS / CSRF / SQLi",
                        "Logging sécurisé",
                    ],
                    "Tests de sécurité": [
                        "Tests de pénétration",
                        "Scans de vulnérabilités (Snyk, OWASP ZAP)",
                        "Monitoring de dépendances",
                    ],
                },
                bestPractices="Appliquez les principes de « Security by Design ». Mettez en place des outils d’analyse continue des failles et suivez l’OWASP Top 10.",
            ),
            Question(
                id="developpement_environnements",
                text="Quels environnements de développement et déploiement prévoir ?",
                suggestions=["Développement", "Test", "Préproduction", "Production"],
                sousSuggestions={
                    "Développement": [
                        "Environnement local avec Docker",
                        "Mock des services externes",
                        "Outils de debug actifs",
                    ],
                    "Test": [
                        "CI avec jeux de tests automatiques",
                        "Environnement isolé pour QA",
                        "Base de données dédiée aux tests",
                    ],
                    "Préproduction": [
                        "Miroir fidèle de la production",
                        "Tests utilisateurs internes",
                        "Mesure de performances",
                    ],
                    "Production": [
                        "Infrastructure haute disponibilité",
                        "Monitoring actif (logs, métriques)",
                        "Processus de rollback défini",
                    ],
                },
                bestPractices="Automatisez la configuration des environnements avec Infrastructure as Code. Documentez les procédures de déploiement et de maintenance.",
            ),
        ],
    ),
    Phase(
        id="tests",
        title="Tests",
        description="Validation de la qualité logicielle par une stratégie structurée et des outils adaptés",
        icon="checkCircle",
        color="amber",
        order=4,
        prevPhase="developpement",
        nextPhase="deploiement",
        questions=[
            Question(
                id="tests_strategie",
                text="Quelle stratégie de test allez-vous adopter ?",
                suggestions=["Types de tests", "Approches organisationnelles"],
                sousSuggestions={
                    "Types de tests": [
                        "Tests unitaires (composants isolés)",
                        "Tests d’intégration (interactions modules)",
                        "Tests end-to-end (simulation réelle)",
                        "Tests de charge et performance",
                    ],
                    "Approches organisationnelles": [
                        "Pyramide de tests (unitaires en base)",
                        "Test-driven development (TDD)",
                        "Tests rédigés à partir des user stories",
                        "Tests manuels + automatisés combinés",
                    ],
                },
                bestPractices="Appliquez la pyramide des tests : beaucoup de tests unitaires, un nombre moyen de tests d'intégration, et peu d'E2E.",
            ),
            Question(
                id="tests_outils",
                text="Quels outils de test allez-vous utiliser ?",
                suggestions=["Unitaires", "E2E", "Performance", "Accessibilité"],
                sousSuggestions={
                    "Unitaires": [
                        "Jest (JavaScript/TypeScript)",
                        "Mocha + Chai",
                        "PyTest (Python)",
                        "JUnit (Java)",
                    ],
                    "E2E": ["Cypress", "Playwright", "Selenium"],
                    "Performance": ["JMeter", "k6", "Artillery"],
                    "Accessibilité": ["axe-core", "Pa11y", "Lighthouse"],
                },
                bestPractices="Choisissez les outils compatibles avec votre stack, et intégrez-les dans la CI/CD pour garantir des tests continus.",
            ),
            Question(
                id="tests_couverture",
                text="Quel niveau de couverture de test visez-vous ?",
                suggestions=[
                    "Par zone de criticité",
                    "Par type de composant",
                    "Par objectif de validation",
                ],
                sousSuggestions={
                    "Par zone de criticité": [
                        "≥ 90% sur code critique",
                        "≥ 70% sur reste du code",
                        "Focus sur modules métier sensibles",
                    ],
                    "Par type de composant": [
                        "API publiques entièrement testées",
                        "Interfaces utilisateur principales testées",
                        "Composants utilitaires testés en profondeur",
                    ],
                    "Par objectif de validation": [
                        "Test de chaque scénario d’usage principal",
                        "Couverture de chaque branche de décision",
                        "Tests sur erreurs et cas limites",
                    ],
                },
                bestPractices="Ne cherchez pas la couverture maximale, mais celle qui sécurise les parcours critiques. Mesurez régulièrement et ajustez.",
            ),
            Question(
                id="tests_acceptance",
                text="Comment allez-vous définir et valider les critères d'acceptation ?",
                suggestions=[
                    "Méthodologie",
                    "Collaboration métier",
                    "Outils de validation",
                ],
                sousSuggestions={
                    "Méthodologie": [
                        "Scénarios Given-When-Then (BDD)",
                        "Règles métiers + jeux d'exemples",
                        "Critères de Done clairs",
                    ],
                    "Collaboration métier": [
                        "Démonstrations utilisateurs",
                        "Relectures fonctionnelles",
                        "Retours clients sur maquettes",
                    ],
                    "Outils de validation": [
                        "Outils BDD : Cucumber, Behave",
                        "Matrice de couverture exigence",
                        "Tests A/B pour fonctionnalités sensibles",
                    ],
                },
                bestPractices="Travaillez avec les métiers dès le début. Formalisez les critères d'acceptation dans les specs et reliez-les aux tests.",
            ),
        ],
    ),
    Phase(
        id="deploiement",
        title="Déploiement",
        description="Mise en production, surveillance et amélioration continue",
        icon="upload",
        color="green",
        order=5,
        prevPhase="tests",
        nextPhase=None,
        questions=[
            Question(
                id="deploiement_strategie",
                text="Quelle stratégie de déploiement allez-vous adopter ?",
                suggestions=[
                    "Stratégies progressives",
                    "Stratégies planifiées",
                    "Rollback & résilience",
                ],
                sousSuggestions={
                    "Stratégies progressives": [
                        "Blue/Green deployment",
                        "Canary release",
                        "Rolling update",
                    ],
                    "Stratégies planifiées": [
                        "Déploiement à fenêtre fixe",
                        "Déploiement nocturne",
                        "Par lot de clients (segmentation)",
                    ],
                    "Rollback & résilience": [
                        "Déploiement avec image précédente disponible",
                        "Mécanisme de feature flags",
                        "Validation post-déploiement automatique",
                    ],
                },
                bestPractices="Choisissez une stratégie qui limite les risques, permet des tests contrôlés, et autorise un retour rapide en cas de souci.",
            ),
            Question(
                id="deploiement_monitoring",
                text="Quels systèmes de monitoring allez-vous mettre en place ?",
                suggestions=[
                    "Surveillance infrastructure",
                    "Surveillance applicative",
                    "Alerting",
                    "Observabilité",
                ],
                sousSuggestions={
                    "Surveillance infrastructure": [
                        "CPU, mémoire, disque",
                        "Réseau, processus, services",
                    ],
                    "Surveillance applicative": [
                        "Logs structurés (ELK, Loki)",
                        "Métriques (Prometheus, Datadog)",
                        "Traces distribuées (OpenTelemetry)",
                    ],
                    "Alerting": [
                        "Alertes seuils critiques",
                        "Escalade automatique",
                        "Notifications multicanaux",
                    ],
                    "Observabilité": [
                        "Tableaux de bord personnalisés",
                        "Exploration des logs",
                        "Corrélation des événements",
                    ],
                },
                bestPractices="Définissez SLI (indicateurs), SLO (objectifs), et SLA (engagements) pour chaque composant critique.",
            ),
            Question(
                id="deploiement_maintenance",
                text="Comment organiserez-vous la maintenance continue ?",
                suggestions=[
                    "Organisation d'équipe",
                    "Planification",
                    "Mises à jour",
                    "Suivi d'incidents",
                ],
                sousSuggestions={
                    "Organisation d'équipe": [
                        "Équipe dédiée support N1/N2",
                        "Astreintes avec rotation",
                        "Responsables de composants",
                    ],
                    "Planification": [
                        "Fenêtres de maintenance régulières",
                        "Suivi de dette technique",
                        "Budget temps dédié dans les sprints",
                    ],
                    "Mises à jour": [
                        "Mise à jour automatique des dépendances",
                        "Tests de compatibilité en CI",
                        "Changelog et communication interne",
                    ],
                    "Suivi d'incidents": [
                        "Outil de ticketing (Jira, ServiceNow)",
                        "Rapports post-mortem",
                        "Capitalisation (RCA, base de connaissance)",
                    ],
                },
                bestPractices="Formalisez chaque processus. Utilisez un référentiel partagé et mettez à jour les procédures après chaque incident.",
            ),
            Question(
                id="deploiement_amelioration",
                text="Comment allez-vous recueillir du feedback et améliorer en continu ?",
                suggestions=[
                    "Sources de feedback",
                    "Analyse",
                    "Implémentation",
                    "Mesure d’impact",
                ],
                sousSuggestions={
                    "Sources de feedback": [
                        "Enquêtes utilisateurs",
                        "Hotjar, FullStory, Session Replay",
                        "Retour support client",
                    ],
                    "Analyse": [
                        "Analyse de logs d’usage",
                        "Comparaison A/B",
                        "Cartes de chaleur",
                    ],
                    "Implémentation": [
                        "Roadmap de versioning",
                        "Méthodologie Kaizen",
                        "Ateliers d’amélioration continue",
                    ],
                    "Mesure d’impact": [
                        "KPIs métier (conversion, rétention)",
                        "Satisfaction utilisateur (NPS)",
                        "Taux de récurrence des bugs",
                    ],
                },
                bestPractices="Mettez en place une boucle de feedback fermée. Priorisez les améliorations à forte valeur ajoutée selon les retours et données mesurées.",
            ),
        ],
    ),
    # (les autres phases peuvent être ajoutées ici de manière similaire)
]
