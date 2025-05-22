from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime # Ajout pour les champs de date





@dataclass
class Question:
    id: str
    text: str
    suggestions: List[str]
    bestPractices: str
    response: Optional[str] = ""
    sousSuggestions: Optional[dict] = field(default_factory=dict)

@dataclass
class Phase:
    id: str
    title: str
    description: str
    icon: str
    color: str
    questions: Optional[List[Question]] = None
    order: Optional[int] = None
    nextPhase: Optional[str] = None
    prevPhase: Optional[str] = None

@dataclass
class ProjectData:
    name: str
    phases: List[Phase]

# Nouvelles classes basées sur le schéma de base de données

@dataclass
class User:
    id: int
    name: str
    email: str # Changé de E-mail à email pour suivre les conventions Python
    password: str # Note: Le stockage de mots de passe en clair est déconseillé. Envisagez le hachage.
    type_user: Optional[str] = None
    langue: Optional[str] = None

@dataclass
class Project:
    id: int
    nom: str
    id_user: int # Clé étrangère vers User.id
    description: Optional[str] = None
    date_creation: datetime = field(default_factory=datetime.now)
    date_modification: datetime = field(default_factory=datetime.now)

@dataclass
class Canevas:
    id: int
    id_project: int # Clé étrangère vers Project.id
    markdown: Optional[str] = None

@dataclass
class StepGroup: # Anciennement "Steps" dans le diagramme, renommé pour clarté
    id: int
    id_project: int # Clé étrangère vers Project.id
    date_creation: datetime = field(default_factory=datetime.now)
    date_modification: datetime = field(default_factory=datetime.now)
    # Potentiellement un nom ou une description pour ce groupe d'étapes
    # nom_groupe: Optional[str] = None 

@dataclass
class Step:
    id: int
    id_steps: int # Clé étrangère vers StepGroup.id (anciennement Steps.id)
    rubrique: Optional[str] = None
    sous_rubrique: Optional[str] = None # Changé de SousRubrique
    extra: Optional[str] = None # Pourrait être un dict si c'est du JSON

@dataclass
class Documentation:
    id: int
    id_project: int # Clé étrangère vers Project.id
    description: Optional[str] = None
    date_creation: datetime = field(default_factory=datetime.now)
    date_modification: datetime = field(default_factory=datetime.now)
    type_doc: Optional[str] = None

@dataclass
class Chapter:
    id: int
    id_doc: int # Clé étrangère vers Documentation.id
    titre: str
    description: Optional[str] = None
