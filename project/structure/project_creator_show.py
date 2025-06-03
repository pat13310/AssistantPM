from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import Qt
from project.structure.project_data_loader import ProjectDataLoader


class ProjectCreatorShow(QObject):
    """Classe pour l'affichage des types d'applications et fonctionnalités disponibles"""
    
    # Signaux
    technology_selected = Signal(str)
    app_type_selected = Signal(str)
    feature_selected = Signal(str)
    project_creation_requested = Signal(str, str, list)  # technology, app_type, features
    
    def __init__(self):
        super().__init__()
        self.selected_technology = ""
        self.selected_app_type = ""
        self.selected_features = []
        self.selected_project_type = ""

    @staticmethod
    def get_app_types_for_technology(technology):
        """Retourne les types d'applications disponibles pour une technologie donnée"""
        return ProjectDataLoader.get_app_types_for_technology(technology)

    @staticmethod
    def get_features_for_app_type(app_type):
        """Retourne les fonctionnalités disponibles pour un type d'application donné"""
        return ProjectDataLoader.get_features_for_app_type(app_type)
    
    def select_technology(self, technology):
        """Sélectionne une technologie et émet un signal"""
        self.selected_technology = technology
        self.technology_selected.emit(technology)
        return self.get_app_types_for_technology(technology)
    
    def select_app_type(self, app_type):
        """Sélectionne un type d'application et émet un signal"""
        self.selected_app_type = app_type
        self.app_type_selected.emit(app_type)
        return self.get_features_for_app_type(app_type)
    
    def toggle_feature(self, feature):
        """Active ou désactive une fonctionnalité"""
        if feature in self.selected_features:
            self.selected_features.remove(feature)
        else:
            self.selected_features.append(feature)
        self.feature_selected.emit(feature)
        return self.selected_features
    
    def create_project(self, project_name, project_path):
        """Demande la création d'un projet avec les paramètres sélectionnés"""
        if not self.selected_technology or not self.selected_app_type:
            return False
        
        self.project_creation_requested.emit(
            self.selected_technology, 
            self.selected_app_type, 
            self.selected_features
        )
        
        # Réinitialiser les sélections après la création
        self.reset_selections()
        return True
    
    def reset_selections(self):
        """Réinitialise toutes les sélections"""
        self.selected_technology = ""
        self.selected_app_type = ""
        self.selected_features = []
        self.selected_project_type = ""
        
    @staticmethod
    def get_project_color_mapping():
        """Retourne le mapping des couleurs pour les types de projets"""
        return {
            "web": "#4CAF50",  # Vert
            "mobile": "#2196F3",  # Bleu
            "desktop": "#9C27B0",  # Violet
            "blockchain": "#FF9800",  # Orange
            "ai": "#F44336",  # Rouge
            "devops": "#00BCD4",  # Cyan
            "microservices": "#795548",  # Marron
            "cms": "#607D8B",  # Bleu-gris
        }
    
    @staticmethod
    def get_project_types():
        """Retourne la liste des types de projets disponibles"""
        return [
            {
                "id": "web",
                "name": "Développement Web",
                "icon": "globe",
                "color": "#4CAF50",
                "description": "Applications et sites web",
            },
            {
                "id": "mobile",
                "name": "Applications Mobiles",
                "icon": "smartphone",
                "color": "#2196F3",
                "description": "Applications pour iOS et Android",
            },
            {
                "id": "desktop",
                "name": "Applications Desktop",
                "icon": "monitor",
                "color": "#9C27B0",
                "description": "Applications pour Windows, macOS et Linux",
            },
            {
                "id": "blockchain",
                "name": "Blockchain",
                "icon": "link-2",
                "color": "#FF9800",
                "description": "Applications décentralisées et smart contracts",
            },
            {
                "id": "ai",
                "name": "Intelligence Artificielle",
                "icon": "brain",
                "color": "#F44336",
                "description": "Machine learning et traitement de données",
            },
            {
                "id": "devops",
                "name": "DevOps / CI/CD",
                "icon": "workflow",
                "color": "#00BCD4",
                "description": "Automatisation, déploiement et intégration continue",
            },
            {
                "id": "microservices",
                "name": "Microservices",
                "icon": "cloud",
                "color": "#795548",
                "description": "Architecture distribuée et services",
            },
            {
                "id": "cms",
                "name": "CMS",
                "icon": "server-cog",
                "color": "#607D8B",
                "description": "Systèmes de gestion de contenu",
            },
        ]
        
    def select_project_type(self, project_type_id):
        """Sélectionne un type de projet"""
        self.selected_project_type = project_type_id
        return self.get_technologies_for_project_type(project_type_id)
        
    @staticmethod
    def get_technologies_for_project_type(project_type_id):
        """Retourne les technologies disponibles pour un type de projet"""
        technologies = {
            "web": [
                {"id": "html_css", "name": "HTML/CSS", "icon": "globe", "description": "Langages de base pour le web"},
                {"id": "javascript", "name": "JavaScript", "icon": "globe", "description": "Langage de programmation dynamique pour le web"},
                {"id": "react", "name": "React", "icon": "globe", "description": "Bibliothèque JavaScript pour créer des interfaces utilisateur"},
                {"id": "vue", "name": "Vue.js", "icon": "globe", "description": "Framework progressif pour construire des UIs"},
                {"id": "angular", "name": "Angular", "icon": "globe", "description": "Plateforme pour construire des applications web"},
                {"id": "php", "name": "PHP", "icon": "globe", "description": "Langage de script côté serveur pour le web"},
                {"id": "python", "name": "Python", "icon": "globe", "description": "Langage polyvalent pour le développement web"},
                {"id": "ruby", "name": "Ruby on Rails", "icon": "globe", "description": "Framework web pour un développement rapide"},
            ],
            "mobile": [
                {"id": "react_native", "name": "React Native", "icon": "smartphone", "description": "Framework pour applications mobiles multi-plateformes"},
                {"id": "flutter", "name": "Flutter", "icon": "smartphone", "description": "SDK Google pour interfaces mobiles natives"},
                {"id": "swift", "name": "Swift (iOS)", "icon": "smartphone", "description": "Langage moderne pour iOS et iPadOS"},
                {"id": "kotlin", "name": "Kotlin (Android)", "icon": "smartphone", "description": "Langage moderne pour Android"},
            ],
            "desktop": [
                {"id": "electron", "name": "Electron", "icon": "monitor", "description": "Applications desktop avec technologies web"},
                {"id": "qt", "name": "Qt", "icon": "monitor", "description": "Framework C++ pour interfaces desktop multiplateforme"},
                {"id": "csharp", "name": "C#/.NET", "icon": "monitor", "description": "Écosystème Microsoft pour applications desktop"},
                {"id": "java", "name": "Java", "icon": "monitor", "description": "Applications multiplateformes avec Java"},
                {"id": "python_desktop", "name": "Python", "icon": "monitor", "description": "Applications desktop en Python"},
            ],
            "blockchain": [
                {"id": "ethereum", "name": "Ethereum", "icon": "link-2", "description": "Plateforme blockchain pour applications décentralisées"},
                {"id": "web3js", "name": "Web3.js", "icon": "link-2", "description": "Bibliothèque JavaScript pour interagir avec Ethereum"},
                {"id": "hardhat", "name": "Hardhat", "icon": "link-2    ", "description": "Environnement de développement pour Ethereum"},
                {"id": "truffle", "name": "Truffle", "icon": "link-2", "description": "Framework de développement pour Ethereum"},
                {"id": "hyperledger", "name": "Hyperledger", "icon": "link-2", "description": "Blockchain d'entreprise open-source"},
                {"id": "solana", "name": "Solana", "icon": "link-2", "description": "Blockchain haute performance"},
                {"id": "near", "name": "NEAR Protocol", "icon": "link-2", "description": "Plateforme décentralisée pour applications cloud"},
                {"id": "cosmos", "name": "Cosmos SDK", "icon": "link-2", "description": "Framework pour réseaux blockchain interconnectés"},
            ],
            "ai": [
                {"id": "tensorflow", "name": "TensorFlow", "icon": "brain", "description": "Bibliothèque pour l'apprentissage automatique"},
                {"id": "pytorch", "name": "PyTorch", "icon": "brain", "description": "Framework flexible pour le deep learning"},
                {"id": "keras", "name": "Keras", "icon": "brain", "description": "API haut niveau pour les réseaux de neurones"},
                {"id": "scikit", "name": "Scikit-Learn", "icon": "brain", "description": "Outils simples pour l'analyse de données"},
                {"id": "huggingface", "name": "Hugging Face Transformers", "icon": "brain", "description": "Bibliothèque pour les modèles de langage"},
                {"id": "opencv", "name": "OpenCV", "icon": "brain", "description": "Bibliothèque de vision par ordinateur"},
                {"id": "nltk", "name": "NLTK", "icon": "brain", "description": "Toolkit pour le traitement du langage naturel"},
                {"id": "spacy", "name": "spaCy", "icon": "brain", "description": "Bibliothèque avancée pour le NLP"},
            ],
            "devops": [
                {"id": "docker", "name": "Docker", "icon": "workflow", "description": "Plateforme de conteneurisation d'applications"},
                {"id": "kubernetes", "name": "Kubernetes", "icon": "workflow", "description": "Orchestration de conteneurs"},
                {"id": "terraform", "name": "Terraform", "icon": "workflow", "description": "Infrastructure as Code"},
                {"id": "ansible", "name": "Ansible", "icon": "workflow", "description": "Automatisation de la configuration"},
                {"id": "jenkins", "name": "Jenkins", "icon": "workflow", "description": "Serveur d'intégration continue"},
                {"id": "github_actions", "name": "GitHub Actions", "icon": "workflow", "description": "CI/CD intégré à GitHub"},
                {"id": "gitlab_ci", "name": "GitLab CI/CD", "icon": "workflow", "description": "Pipeline CI/CD intégré à GitLab"},
                {"id": "aws_cloudformation", "name": "AWS CloudFormation", "icon": "workflow", "description": "Infrastructure as Code pour AWS"},
            ],
            "microservices": [
                {"id": "spring_cloud", "name": "Spring Cloud", "icon": "cloud", "description": "Framework Java pour applications distribuées"},
                {"id": "nestjs", "name": "NestJS", "icon": "cloud", "description": "Framework Node.js progressif pour microservices"},
                {"id": "dotnet_micro", "name": ".NET Microservices", "icon": "cloud", "description": "Microservices avec la plateforme .NET"},
                {"id": "go_micro", "name": "Go Micro", "icon": "cloud", "description": "Framework Go pour le développement de microservices"},
                {"id": "moleculer", "name": "Moleculer.js", "icon": "cloud", "description": "Framework de microservices pour Node.js"},
                {"id": "dapr", "name": "Dapr", "icon": "cloud", "description": "Runtime portable pour applications cloud"},
                {"id": "istio", "name": "Istio", "icon": "cloud", "description": "Maillage de services pour Kubernetes"},
                {"id": "kong", "name": "Kong API Gateway", "icon": "cloud", "description": "Passerelle API et gestion d'API"},
            ],
            "cms": [
                {"id": "wordpress", "name": "WordPress", "icon": "server-cog", "description": "CMS le plus populaire au monde"},
                {"id": "drupal", "name": "Drupal", "icon": "server-cog", "description": "CMS puissant et flexible"},
                {"id": "joomla", "name": "Joomla", "icon": "server-cog", "description": "CMS polyvalent et extensible"},
                {"id": "ghost", "name": "Ghost", "icon": "server-cog", "description": "Plateforme de publication minimaliste"},
                {"id": "strapi", "name": "Strapi", "icon": "server-cog", "description": "CMS headless open-source"},
                {"id": "contentful", "name": "Contentful", "icon": "server-cog", "description": "Plateforme de contenu API-first"},
                {"id": "sanity", "name": "Sanity.io", "icon": "server-cog", "description": "CMS headless flexible et personnalisable"},
                {"id": "keystone", "name": "KeystoneJS", "icon": "server-cog", "description": "CMS headless basé sur Node.js"},
            ],
        }
        return technologies.get(project_type_id, [])
    
    def get_project_types_data(self):
        """Retourne les données des types de projets pour affichage"""
        return self.get_project_types()
        
    
    
    def get_technologies_data(self, project_type_id):
        """Retourne les données des technologies pour un type de projet"""
        technologies = self.get_technologies_for_project_type(project_type_id)
        
        # Trouver le nom du type de projet
        project_type_name = next(
            (pt["name"] for pt in self.get_project_types() if pt["id"] == project_type_id),
            ""
        )
        
        # Obtenir la couleur du type de projet
        project_color = self.get_project_color_mapping().get(project_type_id, "#4CAF50")
        
        # Retourner les données structurées
        return {
            "technologies": technologies,
            "project_type_name": project_type_name,
            "project_color": project_color
        }
        
    @staticmethod
    def get_programming_languages_for_technology(technology_id):
        """Retourne les langages de programmation disponibles pour une technologie"""
        languages = {
            # Web
            "html_css": [
                {"id": "html5", "name": "HTML5", "icon": "html", "description": "Langage de balisage standard pour les pages web"},
                {"id": "css3", "name": "CSS3", "icon": "css", "description": "Langage de style pour la mise en forme des pages web"},
                {"id": "sass", "name": "Sass/SCSS", "icon": "sass", "description": "Préprocesseur CSS avec variables et fonctions"},
            ],
            "javascript": [
                {"id": "js_es6", "name": "JavaScript (ES6+)", "icon": "javascript", "description": "Langage de programmation pour le web"},
                {"id": "typescript", "name": "TypeScript", "icon": "typescript", "description": "JavaScript typé pour les grandes applications"},
                {"id": "nodejs", "name": "Node.js", "icon": "nodejs", "description": "Environnement d'exécution JavaScript côté serveur"},
            ],
            "react": [
                {"id": "jsx", "name": "JSX", "icon": "react", "description": "Syntaxe de template pour React"},
                {"id": "tsx", "name": "TSX", "icon": "typescript", "description": "JSX avec TypeScript"},
            ],
            "vue": [
                {"id": "vue_js", "name": "Vue.js", "icon": "vue", "description": "Framework progressif pour les interfaces utilisateur"},
                {"id": "vue_ts", "name": "Vue avec TypeScript", "icon": "typescript", "description": "Vue.js avec TypeScript"},
            ],
            "angular": [
                {"id": "typescript", "name": "TypeScript", "icon": "typescript", "description": "Langage principal pour Angular"},
                {"id": "angular_js", "name": "JavaScript", "icon": "javascript", "description": "Version JS d'Angular (moins commun)"},
            ],
            "php": [
                {"id": "php7", "name": "PHP 7+", "icon": "php", "description": "Langage de script côté serveur"},
                {"id": "laravel", "name": "Laravel", "icon": "laravel", "description": "Framework PHP moderne"},
                {"id": "symfony", "name": "Symfony", "icon": "symfony", "description": "Framework PHP robuste"},
            ],
            "python": [
                {"id": "python3", "name": "Python 3", "icon": "python", "description": "Langage polyvalent et facile à apprendre"},
                {"id": "django", "name": "Django", "icon": "django", "description": "Framework web Python complet"},
                {"id": "flask", "name": "Flask", "icon": "flask", "description": "Micro-framework web Python"},
            ],
            "ruby": [
                {"id": "ruby_lang", "name": "Ruby", "icon": "ruby", "description": "Langage élégant et dynamique"},
                {"id": "rails", "name": "Ruby on Rails", "icon": "rails", "description": "Framework web Ruby productif"},
            ],
            
            # Mobile
            "react_native": [
                {"id": "js_rn", "name": "JavaScript", "icon": "javascript", "description": "JavaScript pour React Native"},
                {"id": "ts_rn", "name": "TypeScript", "icon": "typescript", "description": "TypeScript pour React Native"},
            ],
            "flutter": [
                {"id": "dart", "name": "Dart", "icon": "dart", "description": "Langage optimisé pour Flutter"},
            ],
            "swift": [
                {"id": "swift_lang", "name": "Swift", "icon": "swift", "description": "Langage moderne pour iOS et macOS"},
                {"id": "swiftui", "name": "SwiftUI", "icon": "swift", "description": "Framework déclaratif pour les UI"},
            ],
            "kotlin": [
                {"id": "kotlin_lang", "name": "Kotlin", "icon": "kotlin", "description": "Langage moderne pour Android"},
                {"id": "java_android", "name": "Java", "icon": "java", "description": "Langage traditionnel pour Android"},
            ],
            
            # Desktop
            "electron": [
                {"id": "js_electron", "name": "JavaScript", "icon": "javascript", "description": "JavaScript pour Electron"},
                {"id": "ts_electron", "name": "TypeScript", "icon": "typescript", "description": "TypeScript pour Electron"},
            ],
            "qt": [
                {"id": "cpp", "name": "C++", "icon": "cpp", "description": "C++ avec Qt pour applications desktop"},
                {"id": "qml", "name": "QML", "icon": "qt", "description": "Langage déclaratif pour les UI Qt"},
                {"id": "python_qt", "name": "Python (PyQt/PySide)", "icon": "python", "description": "Python avec Qt"},
            ],
            "csharp": [
                {"id": "cs_net", "name": "C#", "icon": "csharp", "description": "Langage principal pour .NET"},
                {"id": "xaml", "name": "XAML", "icon": "xaml", "description": "Langage de balisage pour UI .NET"},
            ],
            "java": [
                {"id": "java_desktop", "name": "Java", "icon": "java", "description": "Java pour applications desktop"},
                {"id": "kotlin_desktop", "name": "Kotlin", "icon": "kotlin", "description": "Kotlin pour applications desktop"},
            ],
            "python_desktop": [
                {"id": "tkinter", "name": "Tkinter", "icon": "python", "description": "Bibliothèque UI standard de Python"},
                {"id": "pyqt", "name": "PyQt/PySide", "icon": "qt", "description": "Liaison Python pour Qt"},
                {"id": "wxpython", "name": "wxPython", "icon": "python", "description": "Toolkit UI natif pour Python"},
            ],
        }
        
        return languages.get(technology_id, [])
    
    def get_programming_languages_data(self, technology_id):
        """Retourne les données des langages de programmation pour une technologie"""
        languages = self.get_programming_languages_for_technology(technology_id)
        
        # Trouver le nom de la technologie et son type de projet
        technology_name = ""
        project_color = "#4CAF50"  # Couleur par défaut
        
        # Parcourir tous les types de projets pour trouver la technologie
        for project_type_id, technologies in self._get_all_technologies_mapping().items():
            for tech in technologies:
                if tech["id"] == technology_id:
                    technology_name = tech["name"]
                    project_color = self.get_project_color_mapping().get(project_type_id, "#4CAF50")
                    break
            if technology_name:  # Si on a trouvé la technologie, on arrête
                break
        
        # Retourner les données structurées
        return {
            "languages": languages,
            "technology_name": technology_name,
            "color": project_color
        }
    
    def _get_all_technologies_mapping(self):
        """Méthode privée pour obtenir le mapping complet des technologies par type de projet"""
        return {
            "web": self.get_technologies_for_project_type("web"),
            "mobile": self.get_technologies_for_project_type("mobile"),
            "desktop": self.get_technologies_for_project_type("desktop"),
            "blockchain": self.get_technologies_for_project_type("blockchain"),
            "ai": self.get_technologies_for_project_type("ai"),
            "devops": self.get_technologies_for_project_type("devops"),
            "microservices": self.get_technologies_for_project_type("microservices"),
            "cms": self.get_technologies_for_project_type("cms"),
        }
