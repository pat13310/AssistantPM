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
    QMenu,
    QInputDialog,
    QMessageBox,
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
    
    # Signal pour les opérations sur les fichiers/dossiers (action, path, success, is_dir)
    # action: string ("create", "delete", etc.), path: string, success: bool, is_dir: bool
    file_operation = Signal(str, str, bool, bool)
    
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
        self.file_system_model.setReadOnly(False)  # Permettre la modification (création/suppression)
        
        # Afficher tous les lecteurs
        self.file_system_model.setRootPath('')
        
        self.proxy_model = ForbiddenPathProxyModel()
        self.tree_view = None
        self.path_label = None
        self.forbidden_checkbox = None
        self.root_path = None
        self.delegate = None
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

        # Option : positionner une racine spécifique si besoin
        if root_path and os.path.exists(root_path):
            self.set_root_path(root_path)
        else:
            # Appel du refresh traditionnel pour afficher l'état réel du disque dès le début
            self.refresh_tree_view()
    

    def refresh_tree_view(self, keep_selection=True):
        """
        Rafraîchit complètement l'affichage de l'arborescence de fichiers (QTreeView).
        À appeler après toute modification du système de fichiers ou à l'initialisation.

        Args:
            keep_selection (bool): Si True, tente de resélectionner l'élément sélectionné avant le refresh.
        """
        # 1. Sauvegarder l'élément sélectionné (pour UX)
        selected_path = self.get_selected_path() if keep_selection else None

        # 2. Rafraîchir le modèle système de fichiers
        try:
            self.file_system_model.refresh()  # PySide6 >= 6.2
        except AttributeError:
            # Pour compatibilité, reset racine puis reviens si besoin
            self.file_system_model.setRootPath('')
            if self.root_path:
                self.file_system_model.setRootPath(self.root_path)

        # 3. Forcer le recalcul du proxy
        self.proxy_model.invalidateFilter()
        self.proxy_model.invalidate()

        # 4. Redéfinir la racine de la vue
        if self.root_path:
            root_index = self.file_system_model.index(self.root_path)
            proxy_root_index = self.proxy_model.mapFromSource(root_index)
            self.tree_view.setRootIndex(proxy_root_index)
            self.tree_view.expand(proxy_root_index)
        else:
            root_index = self.file_system_model.index('')
            proxy_root_index = self.proxy_model.mapFromSource(root_index)
            self.tree_view.setRootIndex(proxy_root_index)
            self.tree_view.expand(proxy_root_index)

        # 5. Récupérer la sélection si possible
        if selected_path and os.path.exists(selected_path):
            index = self.file_system_model.index(selected_path)
            proxy_index = self.proxy_model.mapFromSource(index)
            if proxy_index.isValid():
                self.tree_view.setCurrentIndex(proxy_index)
                self.tree_view.scrollTo(proxy_index)

        # 6. Rafraîchir visuellement la vue
        self.tree_view.viewport().update()
        self.tree_view.repaint()

    
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
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.show_context_menu)

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
    
    def show_context_menu(self, position):
        """Affiche le menu contextuel pour l'arborescence
        
        Args:
            position (QPoint): Position du clic droit
        """
        # Récupérer l'index sous le curseur
        index = self.tree_view.indexAt(position)
        
        # Vérifier si le clic est sur un élément valide
        if not index.isValid():
            # Créer un menu vide pour les clics dans le vide
            menu = QMenu(self)
            create_folder_action = menu.addAction("Créer un répertoire")
            create_folder_action.triggered.connect(lambda: self.create_folder(None))
            menu.exec_(self.tree_view.viewport().mapToGlobal(position))
            return
            
        # Obtenir le chemin de l'élément sélectionné
        source_index = self.proxy_model.mapToSource(index)
        path = self.file_system_model.filePath(source_index)
        
        # Vérifier si c'est un dossier ou un fichier
        is_dir = os.path.isdir(path)
        
        # Créer le menu contextuel
        menu = QMenu(self)
        
        # Ajouter les actions au menu contextuel en fonction du type d'élément
        if is_dir:
            # Actions pour les répertoires
            create_folder_action = menu.addAction("Créer un répertoire")
            create_folder_action.triggered.connect(lambda: self.create_folder(path))
            
            delete_folder_action = menu.addAction("Supprimer le répertoire")
            delete_folder_action.triggered.connect(lambda: self.delete_item(path))
        else:
            # Actions pour les fichiers
            delete_file_action = menu.addAction("Supprimer le fichier")
            delete_file_action.triggered.connect(lambda: self.delete_item(path))
        
        # Afficher le menu à la position du clic droit
        menu.exec_(self.tree_view.viewport().mapToGlobal(position))
    
    def create_folder(self, parent_path):
        """Crée un nouveau répertoire
        
        Args:
            parent_path (str): Chemin du répertoire parent, ou None si aucun élément sélectionné
        """
        # Si pas de chemin parent spécifié, utiliser la racine
        if not parent_path:
            if self.root_path:
                parent_path = self.root_path
            else:
                QMessageBox.warning(self, "Erreur", "Aucun répertoire sélectionné ou racine définie")
                return
        
        # Demander le nom du nouveau répertoire
        folder_name, ok = QInputDialog.getText(
            self, "Créer un répertoire", "Nom du répertoire:"
        )
        
        if ok and folder_name:
            # Créer le chemin complet du nouveau répertoire
            new_folder_path = os.path.join(parent_path, folder_name)
            
            # Vérifier si le répertoire existe déjà
            if os.path.exists(new_folder_path):
                QMessageBox.warning(self, "Erreur", f"Le répertoire '{folder_name}' existe déjà")
                return
            
            try:
                # Créer le répertoire
                os.makedirs(new_folder_path, exist_ok=True)
                
                # Rafraîchir la vue et sélectionner le nouveau répertoire
                self.update_tree_view_and_select_folder(new_folder_path)
                
                # Émettre le signal pour indiquer qu'une création de dossier a été effectuée
                self.file_operation.emit("create", new_folder_path, True, True)  # True pour is_dir car c'est un dossier
                
                print(f"Répertoire créé : {new_folder_path}")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible de créer le répertoire: {str(e)}")
    
    def delete_item(self, path):
        """Supprime un répertoire ou un fichier
        
        Args:
            path (str): Chemin de l'élément à supprimer
        """
        if not path or not os.path.exists(path):
            QMessageBox.warning(self, "Erreur", "Élément inexistant")
            return
        
        is_dir = os.path.isdir(path)
        item_name = os.path.basename(path)
        item_type = "répertoire" if is_dir else "fichier"
        
        # Créer une boîte de dialogue de confirmation personnalisée avec boutons en français
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Confirmation de suppression")
        msg_box.setText(f"Êtes-vous sûr de vouloir supprimer {item_type} '{item_name}'?")
        
        # Créer les boutons Oui et Non en français
        oui_button = msg_box.addButton("Oui", QMessageBox.YesRole)
        non_button = msg_box.addButton("Non", QMessageBox.NoRole)
        msg_box.setDefaultButton(non_button)
        
        # Afficher la boîte de dialogue et attendre la réponse
        msg_box.exec_()
        
        # Vérifier quel bouton a été cliqué
        if msg_box.clickedButton() == oui_button:
            try:
                # Sauvegarder le répertoire parent
                parent_path = os.path.dirname(path)
                parent_exists = os.path.exists(parent_path)
                
                # Supprimer le répertoire ou fichier
                if is_dir:
                    import shutil
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                
                # Après suppression, réinitialiser complètement l'arborescence
                
                # Réinitialiser la variable root_path pour revenir à l'état initial
                self.root_path = None
                
                # Utiliser la méthode refresh_tree_view pour actualiser l'arborescence
                self.refresh_tree_view(keep_selection=False)
                
                # Émettre le signal pour indiquer qu'une suppression a été effectuée
                self.file_operation.emit("delete", path, True, is_dir)
                
                print(f"{item_type.capitalize()} supprimé : {path}")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible de supprimer {item_type}: {str(e)}")
    
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

    def update_tree_view_and_select_folder(self, folder_path):
        """Met à jour l'arborescence et sélectionne un dossier spécifique.

        Cette méthode rafraîchit l'arborescence et sélectionne le dossier spécifié
        pour mettre en évidence le nouveau dossier créé ou modifié.

        Args:
            folder_path (str): Chemin complet du dossier à sélectionner
        """
        # Vérifier si le chemin existe
        if not os.path.exists(folder_path):
            print(f"Le dossier {folder_path} n'existe pas.")
            return
            
        # Définir la racine si nécessaire
        if self.root_path is None or not folder_path.startswith(self.root_path):
            # Si le dossier n'est pas dans l'arborescence actuelle, changer la racine
            self.set_root_path(os.path.dirname(folder_path))
        
        # Obtenir l'index du modèle pour le chemin spécifié
        index = self.file_system_model.index(folder_path)
        if index.isValid():
            # Mapper l'index à travers le proxy model
            proxy_index = self.proxy_model.mapFromSource(index)
            if proxy_index.isValid():
                # Sélectionner l'élément dans la vue
                self.tree_view.setCurrentIndex(proxy_index)
                # Développer le parent pour montrer l'élément
                parent = proxy_index.parent()
                if parent.isValid():
                    self.tree_view.expand(parent)
                # Faire défiler pour que l'élément soit visible
                self.tree_view.scrollTo(proxy_index)
                # Faire clignoter pour attirer l'attention
                self.highlight_tree_view()
