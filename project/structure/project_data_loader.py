import os
import json

class ProjectDataLoader:
    """Classe utilitaire pour charger les données de projet depuis un fichier JSON"""
    
    _data = None
    
    @classmethod
    def load_data(cls):
        """Charge les données depuis le fichier JSON"""
        if cls._data is None:
            json_path = os.path.join(os.path.dirname(__file__), 'project_data.json')
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    cls._data = json.load(f)
            except Exception as e:
                print(f"Erreur lors du chargement des données de projet: {e}")
                # Fournir des données par défaut en cas d'erreur
                cls._data = {
                    "app_types_by_technology": {},
                    "features_by_app_type": {},
                    "default_features": [],
                    "default_app_types": []
                }
        return cls._data
    
    @classmethod
    def get_app_types_for_technology(cls, technology):
        """Retourne les types d'applications disponibles pour une technologie donnée"""
        data = cls.load_data()
        return data.get("app_types_by_technology", {}).get(
            technology, data.get("default_app_types", ["Application simple"])
        )
    
    @classmethod
    def get_features_for_app_type(cls, app_type):
        """Retourne les fonctionnalités disponibles pour un type d'application donné"""
        data = cls.load_data()
        return data.get("features_by_app_type", {}).get(
            app_type, data.get("default_features", ["Structure de base"])
        )
