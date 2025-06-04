#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module pour le composant d'arborescence de fichiers - Version ultra-simplifiée
Ce module contient la classe FileTreeWidget qui encapsule la fonctionnalité
de base de l'arborescence de fichiers pour l'application.
"""

import os
from typing import Optional, List
import locale

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTreeView,
    QLabel,
    QCheckBox,
    QLineEdit,
    QStyledItemDelegate,
    QStyle,
    QFileDialog,
    QFileSystemModel,
)
from PySide6.QtCore import (
    Qt,
    QDir,
    QSortFilterProxyModel,
    Signal,
    QModelIndex,
    QTimer,
)
from PySide6.QtGui import (
    QColor,
    QPalette,
    QBrush,
    QFont,
    QIcon,
    QPixmap
)


# Liste des emplacements système interdits (insensible à la casse)
# Cette liste doit correspondre à celle utilisée dans ui_agent_ia.py
FORBIDDEN_PATHS = [
    "Program Files", 
    "Program Files (x86)",
    "Programs", 
    "Windows", 
    "Users", 
    "Documents and Settings", 
    "System Volume Information", 
    "$Recycle.Bin", 
    "MSOCache",
    "Recovery", 
    "PerfLogs", 
    "OneDriveTemp",
    "Config.Msi",
    "Boot"
]

# Liste des lecteurs système à protéger (généralement C:)
SYSTEM_DRIVES = ['c']


class ForbiddenPathProxyModel(QSortFilterProxyModel):
    """Modèle proxy pour filtrer les répertoires interdits"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.forbidden_paths = FORBIDDEN_PATHS
        self.system_drives = SYSTEM_DRIVES
        self.show_forbidden = False  # Par défaut, masquer les répertoires interdits
        self.setDynamicSortFilter(True)
    
    def set_show_forbidden(self, show):
        """Active ou désactive l'affichage des répertoires interdits
        
        Args:
            show (bool): True pour afficher, False pour masquer
        """
        if self.show_forbidden != show:
            self.show_forbidden = show
            # Force le modèle à réévaluer les filtres et les données
            self.invalidateFilter()
            # Force le modèle à réémettre les données pour tous les rôles
            self.beginResetModel()
            self.endResetModel()
    
    def filterAcceptsRow(self, source_row, source_parent):
        """Détermine si une ligne doit être affichée dans le modèle
        
        Args:
            source_row: Index de la ligne dans le modèle source
            source_parent: Index du parent dans le modèle source
            
        Returns:
            bool: True si la ligne doit être affichée, False sinon
        """
        # Si on montre les répertoires interdits, on accepte toutes les lignes
        if self.show_forbidden:
            return True
            
        # Récupérer l'index dans le modèle source
        source_model = self.sourceModel()
        index = source_model.index(source_row, 0, source_parent)
        
        # Récupérer le chemin de l'item
        path = source_model.filePath(index)
        
        # Vérifier si c'est un répertoire interdit
        return not self.is_forbidden_path(path)
    
    def data(self, index, role):
        """Surcharge de la méthode data pour colorier les dossiers interdits en rouge
        
        Args:
            index: Index de l'élément
            role: Rôle des données demandées
            
        Returns:
            object: Données demandées selon le rôle
        """
        # Pour le rôle de couleur du texte (ForegroundRole)
        if role == Qt.ForegroundRole:
            # Récupérer le chemin de l'élément
            source_index = self.mapToSource(index)
            source_model = self.sourceModel()
            
            if source_model and isinstance(source_model, QFileSystemModel):
                path = source_model.filePath(source_index)
                
                # Vérifier si c'est un dossier interdit et que l'option est activée
                if self.show_forbidden and self.is_forbidden_path(path):
                    # Retourner la couleur rouge
                    return QBrush(QColor(255, 0, 0))
        
        # Pour tous les autres cas, utiliser le comportement par défaut
        return super().data(index, role)
    
    def is_forbidden_path(self, path):
        """Vérifie si un chemin est dans la liste des dossiers interdits
        
        Args:
            path (str): Le chemin à vérifier
            
        Returns:
            bool: True si le chemin est interdit, False sinon
        """
        if not path:
            return False
            
        # Normaliser le chemin en utilisant des barres obliques (slash)
        path = path.replace("\\", "/").lower()
        
        # Vérifier d'abord si c'est un lecteur système
        for drive in self.system_drives:
            drive_path = f"{drive}:"
            if path.lower().startswith(drive_path):
                # Extraire le premier dossier après le lecteur
                path_parts = path.split("/")
                if len(path_parts) > 1:
                    folder_name = path_parts[1].lower()
                    # Vérifier si c'est un dossier interdit
                    for forbidden in self.forbidden_paths:
                        if folder_name == forbidden.lower():
                            return True
        return False


class ForbiddenPathDelegate(QStyledItemDelegate):
    """Délégué pour afficher les dossiers interdits en rouge dans l'arborescence"""
    
    def __init__(self, parent=None):
        """Initialise le délégué avec la liste des chemins interdits
        
        Args:
            parent: Parent du délégué
        """
        super().__init__(parent)
        # Utiliser les constantes définies dans ce module
        self.forbidden_paths = FORBIDDEN_PATHS
        # Par défaut, considérer le lecteur C: comme système
        self.system_drives = SYSTEM_DRIVES
        # Option pour activer/désactiver la coloration des répertoires interdits
        self.show_forbidden = False  # Par défaut, masquer les répertoires interdits
    
    def set_show_forbidden(self, show):
        """Active ou désactive l'affichage des répertoires interdits
        
        Args:
            show (bool): True pour afficher en rouge, False pour un affichage normal
        """
        self.show_forbidden = show
    
    def paint(self, painter, option, index):
        """Personnalise l'affichage des éléments dans le TreeView
        
        Args:
            painter: Le peintre utilisé pour dessiner l'élément
            option: Les options de style pour l'élément
            index: L'index de l'élément dans le modèle
        """
        # D'abord, dessiner l'élément avec le style par défaut
        super().paint(painter, option, index)
        
        # Ensuite, vérifier si c'est un dossier interdit pour le colorier en rouge
        if not self.show_forbidden:
            return
            
        # Récupérer le chemin du fichier
        path = ""
        model = index.model()
        
        if isinstance(model, QSortFilterProxyModel):
            # Si c'est un proxy, récupérer le modèle source et l'index source
            source_model = model.sourceModel()
            source_index = model.mapToSource(index)
            if isinstance(source_model, QFileSystemModel):
                path = source_model.filePath(source_index)
        elif isinstance(model, QFileSystemModel):
            # Si c'est directement un QFileSystemModel
            path = model.filePath(index)
        
        # Vérifier si c'est un dossier interdit
        if self.is_forbidden_path(path):
            # Sauvegarder l'état du peintre
            painter.save()
            
            # Même si la colonne n'est pas celle du nom, on colore quand même
            if index.column() == 0:  # Colonne du nom
                # Récupérer le texte à afficher
                text = index.data(Qt.DisplayRole)
                if text:
                    rect = option.rect
                    # Dessiner le texte en rouge par-dessus
                    painter.setPen(QColor(255, 0, 0))
                    painter.drawText(rect, Qt.AlignVCenter | Qt.AlignLeft, text)
            
            # Restaurer l'état du peintre
            painter.restore()
    
    def is_forbidden_path(self, path):
        """Vérifie si un chemin est dans la liste des dossiers interdits
        
        Args:
            path (str): Le chemin à vérifier
            
        Returns:
            bool: True si le chemin est interdit, False sinon
        """
        if not path:
            return False
            
        # Normaliser le chemin en utilisant des barres obliques (slash)
        path = path.replace("\\", "/").lower()
        
        # Vérifier d'abord si c'est un lecteur système
        for drive in self.system_drives:
            drive_path = f"{drive}:"
            if path.lower().startswith(drive_path):
                # Extraire le premier dossier après le lecteur
                path_parts = path.split("/")
                if len(path_parts) > 1:
                    folder_name = path_parts[1].lower()
                    # Vérifier si c'est un dossier interdit
                    for forbidden in self.forbidden_paths:
                        if folder_name == forbidden.lower():
                            return True
        return False


class FileTreeWidget(QWidget):
    """Widget d'arborescence de fichiers simplifié avec signal de sélection de chemin"""
    
    # Signal émis lorsqu'un nouveau chemin est sélectionné dans l'arborescence
    path_selected = Signal(str)
    
    # Signaux requis par ui_agent_ia.py
    item_clicked = Signal(str, bool)  # path, is_dir
    item_double_clicked = Signal(str, bool)  # path, is_dir
    search_text_changed = Signal(str)  # search text
    
    def __init__(self, parent=None, root_path=None):
        """Initialise le widget d'arborescence
        
        Args:
            parent: Widget parent
            root_path: Chemin racine initial pour l'arborescence
        """
        super().__init__(parent)
        
        # Configuration de la locale pour l'affichage des dates et des nombres
        locale.setlocale(locale.LC_ALL, '')
        
        # Initialisation des attributs de classe
        self.file_system_model = QFileSystemModel()
        
        # Configuration du modèle de système de fichiers
        self.file_system_model.setReadOnly(False)
        self.file_system_model.setNameFilterDisables(False)
        # Afficher les 4 colonnes standard: Nom, Taille, Type, Date de modification
        self.file_system_model.setRootPath('')
        
        self.proxy_model = ForbiddenPathProxyModel()
        self.tree_view = None
        self.path_label = None
        self.forbidden_checkbox = None
        self.root_path = None
        self.delegate = None
        
        # Configuration du modèle de fichiers
        self.file_system_model.setReadOnly(True)
        self.file_system_model.setNameFilterDisables(False)
        self.file_system_model.setFilter(QDir.AllDirs | QDir.Files | QDir.NoDotAndDotDot)
        
        # Création du proxy model
        self.proxy_model.setSourceModel(self.file_system_model)
        
        # Configuration pour afficher les colonnes standard
        self.proxy_model.setDynamicSortFilter(True)
        
        # Initialisation de l'interface utilisateur
        self.init_ui()
        
        # Configuration des connexions entre signaux et slots
        self.setup_connections()
        
        # Si un chemin racine a été fourni, l'utiliser
        if root_path and os.path.exists(root_path):
            self.set_root_path(root_path)
    
    def init_ui(self):
        """Initialise l'interface utilisateur du widget"""
        # Création du layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Création du layout pour les contrôles en haut
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(5, 5, 5, 5)
        top_layout.setSpacing(5)
        
        # Ajout du label pour le chemin
        self.path_label = QLabel("Chemin:")
        top_layout.addWidget(self.path_label)
        
        # Ajout de la checkbox pour afficher/masquer les dossiers interdits
        self.forbidden_checkbox = QCheckBox("Afficher répertoires interdits")
        self.forbidden_checkbox.setChecked(False)  # Décoché par défaut pour masquer les répertoires interdits
        top_layout.addWidget(self.forbidden_checkbox)
        
        # Ajouter un espace extensible
        top_layout.addStretch()
        
        # Ajouter le layout des contrôles au layout principal
        main_layout.addLayout(top_layout)
        
        # Création du TreeView pour l'arborescence de fichiers
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.proxy_model)
        self.tree_view.setAnimated(True) # Conserver l'animation
        self.tree_view.setHeaderHidden(True)  # S'assurer que l'en-tête est masqué
        self.tree_view.setIndentation(20)
        self.tree_view.setSortingEnabled(True)
        self.tree_view.sortByColumn(0, Qt.AscendingOrder)
        self.tree_view.setEditTriggers(QTreeView.NoEditTriggers)
        self.tree_view.setExpandsOnDoubleClick(True)
        self.tree_view.setSelectionMode(QTreeView.SingleSelection)
        self.tree_view.setUniformRowHeights(True)

        # Masquer toutes les colonnes sauf la première (Nom)
        for column in range(1, self.file_system_model.columnCount()):
            self.tree_view.setColumnHidden(column, True)

        # Ajuster la taille de la colonne Nom (la seule visible)
        self.tree_view.setColumnWidth(0, 250)
        
        # Créer et configurer le délégué pour la coloration des dossiers interdits
        self.delegate = ForbiddenPathDelegate(self.tree_view)
        self.tree_view.setItemDelegate(self.delegate)
        
        # Ajouter le TreeView au layout principal
        main_layout.addWidget(self.tree_view)
    
    def setup_connections(self):
        """Configure les connexions entre signaux et slots"""
        # Connexion pour la sélection d'un élément dans l'arborescence
        if hasattr(self, 'tree_view') and self.tree_view is not None:
            self.tree_view.clicked.connect(self.on_tree_item_clicked)
            # Connexion pour double-cliquer sur un élément
            self.tree_view.doubleClicked.connect(self.on_tree_item_double_clicked)
        
        # Connexion des signaux et slots pour la recherche
        if hasattr(self, 'search_field') and self.search_field is not None:
            self.search_field.textChanged.connect(self.filter_tree_view)
            self.search_field.textChanged.connect(self.search_text_changed)
        
        # Connexion pour la checkbox des dossiers interdits
        if hasattr(self, 'forbidden_checkbox') and self.forbidden_checkbox is not None:
            self.forbidden_checkbox.stateChanged.connect(self.on_show_forbidden_changed)
    
    def set_root_path(self, path):
        """Définit le chemin racine pour l'arborescence
        
        Args:
            path (str): Chemin à utiliser comme racine
        """
        if not path or not os.path.exists(path):
            return
        
        self.root_path = path
        
        # Définir le chemin racine dans le modèle de fichiers
        root_index = self.file_system_model.setRootPath(path)
        
        # Définir l'index racine dans la vue en utilisant le proxy
        proxy_index = self.proxy_model.mapFromSource(root_index)
        self.tree_view.setRootIndex(proxy_index)
        
        # Mettre à jour le label du chemin
        self.path_label.setText(f"Chemin: {path}")
        
        # Développer le premier niveau
        self.tree_view.expand(proxy_index)
    
    def get_selected_path(self):
        """Récupère le chemin sélectionné dans l'arborescence
        
        Returns:
            str: Chemin sélectionné ou None si aucune sélection
        """
        # Récupérer les indices sélectionnés
        selected_indices = self.tree_view.selectedIndexes()
        
        if not selected_indices:
            return None
        
        # Prendre le premier indice sélectionné
        selected_index = selected_indices[0]
        
        # Convertir l'indice du proxy en indice source
        source_index = self.proxy_model.mapToSource(selected_index)
        
        # Récupérer le chemin à partir du modèle source
        return self.file_system_model.filePath(source_index)
    
    def on_tree_item_clicked(self, index):
        """Slot appelé quand un élément de l'arborescence est cliqué
        
        Args:
            index (QModelIndex): Index de l'élément cliqué
        """
        # Récupérer le chemin de l'élément cliqué
        path = self.get_selected_path()
        
        if path:
            # Émettre le signal avec le chemin sélectionné
            self.path_selected.emit(path)
            
            # Vérifier si c'est un dossier ou un fichier
            is_dir = os.path.isdir(path)
            
            # Émettre le signal item_clicked requis par ui_agent_ia.py
            self.item_clicked.emit(path, is_dir)
    
    def on_tree_item_double_clicked(self, index):
        """Slot appelé quand un élément de l'arborescence est double-cliqué
        
        Args:
            index (QModelIndex): Index de l'élément double-cliqué
        """
        path = self.get_selected_path()
        if path:
            # Vérifier si c'est un dossier ou un fichier
            is_dir = os.path.isdir(path)
            
            # Émettre le signal item_double_clicked requis par ui_agent_ia.py
            self.item_double_clicked.emit(path, is_dir)
            
            print(f"Double-clic sur: {path}")
    
    def on_show_forbidden_changed(self, state):
        """Slot appelé quand l'état de la checkbox des dossiers interdits change
        
        Args:
            state (int): État de la checkbox (Qt.Checked ou Qt.Unchecked)
        """
        show_forbidden = (state == Qt.Checked)
        
        # Mettre à jour le modèle proxy
        self.proxy_model.set_show_forbidden(show_forbidden)
        
        # Mettre à jour le délégué
        self.delegate.set_show_forbidden(show_forbidden)
        
        # Forcer le rafraîchissement complet de la vue
        self.tree_view.viewport().update()
        self.tree_view.repaint()
        
        # Message pour l'utilisateur sur le changement d'affichage
        status = "affichés en rouge" if show_forbidden else "masqués"
        print(f"Répertoires système {status}.")

    def highlight_tree_view(self, flashes=2, duration_on=250, duration_off=250):
        """Change temporairement le style du TreeView pour attirer l'attention en le faisant clignoter.

        Args:
            flashes (int): Nombre de fois que l'élément doit clignoter.
            duration_on (int): Durée en millisecondes de l'état surligné.
            duration_off (int): Durée en millisecondes de l'état normal entre les surlignages.
        """
        if not self.tree_view:
            return

        original_stylesheet = self.tree_view.styleSheet()
        highlight_style = "QTreeView { background-color: #4a4a4a; border: 1px solid #35fc84; }" # Gris foncé avec bordure verte

        def _flash(count):
            if count <= 0:
                self.tree_view.setStyleSheet(original_stylesheet)
                return

            # Allumer
            self.tree_view.setStyleSheet(highlight_style)
            
            # Éteindre après duration_on
            QTimer.singleShot(duration_on, lambda: _turn_off(count))

        def _turn_off(count):
            self.tree_view.setStyleSheet(original_stylesheet)
            # Prochain flash après duration_off, si ce n'est pas le dernier "off"
            if count > 1: # Ne pas relancer de timer si c'est le dernier "off"
                QTimer.singleShot(duration_off, lambda: _flash(count - 1))
            # Si count == 1, on vient de faire le dernier "off", donc on s'arrête.

        _flash(flashes)
