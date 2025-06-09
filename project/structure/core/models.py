

@dataclass
class ProjectConfig:
    """Configuration complète d'un projet"""
    # Propriétés de base
    name: str = ""
    path: str = ""
    root_path: str = ""
    
    # Sélections de type et technologie
    project_type_id: Optional[str] = None
    project_type_name: str = ""
    technology_id: Optional[str] = None
    technology_name: str = ""
    language_id: Optional[str] = None
    language_name: str = ""
    
    # Types d'application spécifiques
    app_type_id: Optional[str] = None
    app_type_name: str = ""
    subtype_id: Optional[str] = None
    
    # État du processus de création
    wait_for_path: bool = False
    creation_step: str = "initial"
    
    # Métadonnées
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)

    @property
    def full_path(self) -> str:
        """Retourne le chemin complet du projet"""
        if self.path and self.name:
            return f"{self.path}/{self.name}".replace("//", "/")
        return self.path or ""

    @property
    def is_valid(self) -> bool:
        """Vérifie si la configuration est valide"""
        return bool(self.name and self.path)

    @property
    def is_complete(self) -> bool:
        """Vérifie si toutes les sélections sont faites"""
        return all([
            self.name,
            self.path,
            self.project_type_id,
            self.technology_id
        ])

    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire pour sérialisation"""
        return {
            'name': self.name,
            'path': self.path,
            'root_path': self.root_path,
            'project_type_id': self.project_type_id,
            # ... autres propriétés
            'created_at': self.created_at.isoformat(),
            'modified_at': self.modified_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectConfig':
        """Crée une instance depuis un dictionnaire"""
        # Convertir les dates ISO en objets datetime
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)



# Message
@dataclass
class ChatMessage:
    """Message individuel dans une conversation"""
    text: str
    is_user: bool
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Métadonnées visuelles
    icon_name: Optional[str] = None
    icon_color: str = "#FFFFFF"
    icon_size: int = 20
    word_wrap: bool = True
    
    # Métadonnées fonctionnelles
    message_type: str = "text"  # text, action, system, error
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # ID unique pour référencement
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

# Collection des messages
@dataclass
class Conversation:
    """Conversation complète avec métadonnées"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    messages: List[ChatMessage] = field(default_factory=list)
    title: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Métadonnées contextuelles
    project_context: Optional[ProjectConfig] = None
    tags: List[str] = field(default_factory=list)

    @property
    def preview_text(self) -> str:
        """Texte d'aperçu pour l'historique"""
        if not self.messages:
            return "Conversation vide"
        
        first_user_msg = next(
            (msg.text for msg in self.messages if msg.is_user), 
            "Aucun message utilisateur"
        )
        
        # Limiter à 100 caractères
        if len(first_user_msg) > 100:
            return first_user_msg[:97] + "..."
        return first_user_msg

    def add_message(self, message: ChatMessage) -> None:
        """Ajoute un message et met à jour l'heure"""
        self.messages.append(message)
        self.updated_at = datetime.now()
        
        # Générer un titre automatique si nécessaire
        if not self.title and len(self.messages) == 1 and message.is_user:
            self.title = message.text[:50] + ("..." if len(message.text) > 50 else "")