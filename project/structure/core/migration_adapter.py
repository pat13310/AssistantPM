from typing import Optional, Dict, Any
import warnings
from PySide6.QtCore import QObject, Signal
from project.structure.core.state_manager import AppState

class LegacyStateAdapter(QObject):
    """Adaptateur pour rediriger les accès aux anciennes variables d'état"""
    
    # Signal pour tracer les accès legacy
    legacy_access_detected = Signal(str, str)  # property_name, access_type
    
    def __init__(self, state_manager: AppState, enable_warnings: bool = True):
        super().__init__()
        self.state_manager = state_manager
        self.enable_warnings = enable_warnings
        self._migration_log = []
        
        # Cache pour éviter les boucles infinies
        self._updating_from_state = False
    
    # 🔧 Propriétés Legacy Redirectées
    @property
    def selected_project_path(self) -> Optional[str]:
        """Legacy: Chemin du projet sélectionné"""
        self._emit_legacy_access('selected_project_path', 'getter')
        config = self.state_manager.project_config
        return config.path if config else None

    @selected_project_path.setter
    def selected_project_path(self, value: Optional[str]):
        """Legacy: Définit le chemin du projet"""
        self._emit_legacy_access('selected_project_path', 'setter')
        if not self._updating_from_state:
            self.state_manager.update_project_config(path=value or "")

    @property
    def project_name(self) -> Optional[str]:
        """Legacy: Nom du projet"""
        self._emit_legacy_access('project_name', 'getter')
        config = self.state_manager.project_config
        return config.name if config else None

    @project_name.setter
    def project_name(self, value: Optional[str]):
        """Legacy: Définit le nom du projet"""
        self._emit_legacy_access('project_name', 'setter')
        if not self._updating_from_state:
            self.state_manager.update_project_config(name=value or "")
            
    @property
    def server_connected(self) -> bool:
        """Legacy: État de connexion au serveur"""
        self._emit_legacy_access('server_connected', 'getter')
        return self.state_manager.server_state.is_connected
        
    @server_connected.setter
    def server_connected(self, value: bool):
        """Legacy: Définit l'état de connexion au serveur"""
        self._emit_legacy_access('server_connected', 'setter')
        if not self._updating_from_state:
            self.state_manager.server_state.is_connected = value

    
    def _emit_legacy_access(self, property_name: str, access_type: str):
        """Émet un signal et log pour tracer les accès legacy"""
        self.legacy_access_detected.emit(property_name, access_type)
        self._migration_log.append(f"{access_type}: {property_name}")
        
        if self.enable_warnings:
            warnings.warn(
                f"Accès legacy détecté: {property_name} ({access_type}). "
                f"Migrer vers state_manager.{self._get_new_property_path(property_name)}",
                DeprecationWarning,
                stacklevel=3
            )
            
    def _get_new_property_path(self, property_name: str) -> str:
        """Retourne le chemin vers la nouvelle propriété dans le state_manager"""
        mapping = {
            'selected_project_path': 'project_config.path',
            'project_name': 'project_config.name',
            'server_connected': 'server_state.is_connected',
            # Ajouter d'autres mappings au besoin
        }
        return mapping.get(property_name, f"<unknown property: {property_name}>")


    def validate_migration(self) -> Dict[str, Any]:
        """Valide que l'état legacy correspond à l'état du StateManager"""
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Vérifier la configuration de projet
            config = self.state_manager.project_config
            if config:
                if self.selected_project_path != config.path:
                    validation_results['errors'].append(
                        f"Mismatch selected_project_path: {self.selected_project_path} != {config.path}"
                    )
                    validation_results['valid'] = False
            
            # Vérifier l'état du serveur
            if self.server_connected != self.state_manager.server_state.is_connected:
                validation_results['errors'].append(
                    f"Mismatch server_connected: {self.server_connected} != {self.state_manager.server_state.is_connected}"
                )
                validation_results['valid'] = False
                
        except Exception as e:
            validation_results['errors'].append(f"Exception during validation: {str(e)}")
            validation_results['valid'] = False
        
        return validation_results


class ChatArboWidgetMigrationMixin:
    """Mixin à ajouter à ChatArboWidget pour faciliter la migration"""
    
    def _initialize_migration(self):
        """Initialise l'adaptateur de migration"""
        # Créer le StateManager
        self.state_manager = AppState()
        
        # Créer l'adaptateur legacy
        self.legacy_adapter = LegacyStateAdapter(
            self.state_manager, 
            enable_warnings=True  # Mettre False en production
        )
        
        # Connecter aux signaux pour debugging
        self.legacy_adapter.legacy_access_detected.connect(
            self._on_legacy_access_detected
        )
        
        # Migrer l'état existant si nécessaire
        self._migrate_existing_state()

    def _migrate_existing_state(self):
        """Migre l'état existant vers le StateManager"""
        existing_values = {}
        
        # Capturer les valeurs existantes (si elles existent)
        for attr in ['selected_project_path', 'project_name', 'server_connected']:
            if hasattr(self, attr):
                existing_values[attr] = getattr(self, attr)
        
        # Migrer vers le StateManager
        if existing_values:
            print("Migration de l'état existant vers StateManager...")
            
            project_config = {}
            if 'selected_project_path' in existing_values:
                project_config['path'] = existing_values['selected_project_path']
            if 'project_name' in existing_values:
                project_config['name'] = existing_values['project_name']
            
            if project_config:
                self.state_manager.update_project_config(**project_config)
    
    # Redirection automatique des propriétés legacy
    @property
    def selected_project_path(self):
        return self.legacy_adapter.selected_project_path

    @selected_project_path.setter
    def selected_project_path(self, value):
        self.legacy_adapter.selected_project_path = value

    @property
    def project_name(self):
        return self.legacy_adapter.project_name

    @project_name.setter
    def project_name(self, value):
        self.legacy_adapter.project_name = value

    def _on_legacy_access_detected(self, property_name: str, access_type: str):
        """Méthode appelée quand un accès legacy est détecté"""
        print(f"Accès legacy détecté: {property_name} ({access_type})")
        
    # ... autres propriétés