from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Signal, QSize

from menus.MenuLabel import MenuLabel
from menus.CollapsibleSection import CollapsibleSection
from components.infos.data_phases import quick_access_phases # Import des phases


class GeneralMenu(QWidget):
    accueil_clicked = Signal()
    nouveau_clicked = Signal()
    modifier_clicked = Signal()
    # phase_clicked = Signal() # Ancien signal global pour les phases
    phase_selected = Signal(str) # Nouveau signal pour une phase spécifique
    configuration_clicked = Signal()
    logout_clicked = Signal()
    documentation_clicked = Signal()

    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(4, 10, 2, 10)
        self.layout.setSpacing(4)
        self.setStyleSheet("background-color: white;color: black;")

        self.labels = []
        icon_size = QSize(18, 18) # Définir icon_size une fois ici

        # Section: Gestion projet
        gestion_section = CollapsibleSection("Gestion Projet")

        accueil = MenuLabel(
            "Accueil", "assets/icons/house.svg", icon_size, self.label_clicked
        )
        accueil.clicked.connect(self.accueil_clicked.emit)
        gestion_section.add_widget(accueil)
        self.labels.append(accueil)

        nouveau = MenuLabel(
            "Nouveau Projet", "assets/icons/plus.svg", icon_size, self.label_clicked
        )
        nouveau.clicked.connect(self.nouveau_clicked.emit)
        gestion_section.add_widget(nouveau)
        self.labels.append(nouveau)

        modifier = MenuLabel(
            "Modifier Projet", "assets/icons/pencil.svg", icon_size, self.label_clicked
        )
        modifier.clicked.connect(self.modifier_clicked.emit)
        gestion_section.add_widget(modifier)
        self.labels.append(modifier)

        # Section: Autres (Supprimée)
        # autres_section = CollapsibleSection("Phases")
        # phases = MenuLabel("Phases du Projet", None, icon_size, self.label_clicked)
        # phases.signal = self.phase_clicked
        # autres_section.add_widget(phases)
        # self.labels.append(phases)

        # Ajouter les sections au layout principal
        self.layout.addWidget(gestion_section)
        # self.layout.addWidget(autres_section) # Ligne supprimée

        # Section: Étapes du Projet
        etapes_projet_section = CollapsibleSection("Étapes du Projet")
        for phase_data in quick_access_phases:
            icon_path = f"assets/icons/{phase_data.icon}.svg"
            phase_label = MenuLabel(
                phase_data.title, icon_path, icon_size, self.label_clicked
            )
            # Connecter le clic à l'émission du signal phase_selected avec l'ID de la phase
            # Pour cela, nous utilisons une lambda pour capturer l'ID de la phase actuelle
            if phase_data.title == "Documentation":
                phase_label.clicked.connect(self.documentation_clicked.emit)
            else:
                phase_label.clicked.connect(lambda phase_id=phase_data.id: self.phase_selected.emit(phase_id))
            etapes_projet_section.add_widget(phase_label)
            self.labels.append(phase_label)
        self.layout.addWidget(etapes_projet_section)

        # Section: Paramètres
        parametres_section = CollapsibleSection("Paramètres")
        config_api = MenuLabel(
            "Configuration API",
            "assets/icons/settings.svg",
            icon_size,
            self.label_clicked,
        )
        config_api.clicked.connect(self.configuration_clicked.emit)
        parametres_section.add_widget(config_api)
        self.labels.append(config_api)
        self.layout.addWidget(parametres_section)  # Ajout de la section au layout

        self.layout.addStretch()  # Met un espace flexible avant le bouton de déconnexion

        # Bouton de Déconnexion (initialement masqué)
        # Utiliser une icône appropriée si disponible, par exemple 'log-out.svg'
        # from PySide6.QtCore import QSize # Déjà importé plus haut
        # icon_size = QSize(18, 18) # Déjà défini
        self.logout_button = MenuLabel(
            "Déconnexion", "assets/icons/zap.svg", icon_size, self.label_clicked
        )  # Placeholder icon
        self.logout_button.clicked.connect(self.logout_clicked.emit)
        self.logout_button.setVisible(False)  # Masqué par défaut
        self.layout.addWidget(self.logout_button)
        self.labels.append(
            self.logout_button
        )  # Important pour la gestion du clic actif

    def update_logout_button_visibility(self, is_logged_in: bool):
        self.logout_button.setVisible(is_logged_in)

    def label_clicked(self, clicked_label):
        # Ne pas désactiver les autres labels si on clique sur Déconnexion
        # car cela va fermer/redémarrer l'application.
        if clicked_label == self.logout_button:
            clicked_label.clicked.emit()
            return  # Ne pas changer l'état actif des autres labels

        for label in self.labels:
            label.reset()
        clicked_label.active = True
        clicked_label.clicked.emit()

    def toggle_text_visibility(self, show_text: bool):
        for label in self.labels:
            label.show_only_icon(show_text)
