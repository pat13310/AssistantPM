#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module pour le composant d'arborescence de fichiers - Version optimisée
Optimisations principales :
- Lazy loading intelligent
- Cache optimisé
- Réduction des rafraîchissements
- Gestion mémoire améliorée
- Performances des proxy models
"""

import os
from typing import Optional, List, Set
import locale
import weakref

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
    QFileSystemWatcher,
    QMutexLocker,
    QMutex,
    QSettings,
)
from PySide6.QtGui import (
    QColor,
    QPalette,
    QBrush,
    QFont,
    QIcon,
    QPixmap
)


# Configuration optimisée
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

SYSTEM_DRIVES = ['c']

# OPTIMISATION 1: Configuration de cache
CACHE_SIZE_LIMIT = 10000  # Limiter le cache à 10k entrées
REFRESH_DEBOUNCE_MS = 150  # Débouncer les refresh à 150ms


class ForbiddenPathProxyModel(QSortFilterProxyModel):
    """Modèle proxy optimisé avec cache intelligent"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.forbidden_paths = set(path.lower() for path in FORBIDDEN_PATHS)  # Set pour O(1) lookup
        self.system_drives = set(SYSTEM_DRIVES)
        self.show_forbidden = False
        self.setDynamicSortFilter(True)
        
        # OPTIMISATION 2: Cache des résultats de filtrage
        self._filter_cache = {}
        self._cache_mutex = QMutex()
        
        # OPTIMISATION 3: Timer de débouncing pour les invalidations
        self._invalidate_timer = QTimer()
        self._invalidate_timer.setSingleShot(True)
        self._invalidate_timer.timeout.connect(self._do_invalidate)
        
    def set_show_forbidden(self, show):
        """Active ou désactive l'affichage des répertoires interdits"""
        if self.show_forbidden != show:
            self.show_forbidden = show
            self._clear_filter_cache()
            self._debounced_invalidate()
    
    def _debounced_invalidate(self):
        """Débouncer les invalidations pour éviter les refresh trop fréquents"""
        self._invalidate_timer.start(REFRESH_DEBOUNCE_MS)
    
    def _do_invalidate(self):
        """Effectue l'invalidation réelle"""
        self.invalidateFilter()
        self.beginResetModel()
        self.endResetModel()
    
    def _clear_filter_cache(self):
        """Nettoie le cache de filtrage"""
        locker = QMutexLocker(self._cache_mutex)
        self._filter_cache.clear()
    
    def filterAcceptsRow(self, source_row, source_parent):
        """Version optimisée avec cache"""
        # TOUJOURS afficher la racine
        if not source_parent.isValid():
            return True
            
        if self.show_forbidden:
            return True
            
        # OPTIMISATION 4: Cache des résultats
        cache_key = (source_row, source_parent.internalId() if source_parent.isValid() else 0)
        
        locker = QMutexLocker(self._cache_mutex)
        if cache_key in self._filter_cache:
            return self._filter_cache[cache_key]
        
        # Calculer le résultat
        source_model = self.sourceModel()
        index = source_model.index(source_row, 0, source_parent)
        path = source_model.filePath(index)
        result = not self.is_forbidden_path(path)
        
        # Ajouter au cache (avec limite de taille)
        if len(self._filter_cache) < CACHE_SIZE_LIMIT:
            self._filter_cache[cache_key] = result
        
        return result
    
    def is_forbidden_path(self, path):
        """Version optimisée de is_forbidden_path"""
        if not path:
            return False
            
        path_lower = path.replace("\\", "/").lower()
        
        # OPTIMISATION 5: Extraction directe et comparaison optimisée
        for drive in self.system_drives:
            drive_path = f"{drive}:"
            if path_lower.startswith(drive_path):
                # Extraction plus efficace du premier dossier
                slash_pos = path_lower.find("/", len(drive_path))
                if slash_pos > len(drive_path):
                    folder_name = path_lower[len(drive_path)+1:slash_pos]
                elif len(path_lower) > len(drive_path) + 1:
                    folder_name = path_lower[len(drive_path)+1:]
                else:
                    continue
                    
                # Utilisation du set pour O(1) lookup
                if folder_name in self.forbidden_paths:
                    return True
        return False
    
    def data(self, index, role):
        """Version optimisée avec cache de couleurs"""
        if role == Qt.ForegroundRole and self.show_forbidden:
            source_index = self.mapToSource(index)
            source_model = self.sourceModel()
            
            if source_model and isinstance(source_model, QFileSystemModel):
                path = source_model.filePath(source_index)
                if self.is_forbidden_path(path):
                    return QBrush(QColor(255, 0, 0))
        
        return super().data(index, role)


class OptimizedFileSystemModel(QFileSystemModel):
    """QFileSystemModel optimisé avec configuration de performance"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # OPTIMISATION 6: Configuration optimale du modèle
        self.setReadOnly(False)
        self.setNameFilterDisables(False)
        self.setFilter(QDir.AllDirs | QDir.Files | QDir.NoDotAndDotDot)
        self.setResolveSymlinks(False)  # Désactiver pour de meilleures performances
        
        # OPTIMISATION 7: Options de performance Qt6
        if hasattr(self, 'setOption'):
            try:
                # Désactiver la résolution des liens symboliques pour améliorer les performances
                self.setOption(QFileSystemModel.DontResolveSymlinks, True)
            except AttributeError:
                pass


class ForbiddenPathDelegate(QStyledItemDelegate):
    """Délégué optimisé avec rendu minimal"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.forbidden_paths = set(path.lower() for path in FORBIDDEN_PATHS)
        self.system_drives = set(SYSTEM_DRIVES)
        self.show_forbidden = False
        
        # OPTIMISATION 8: Cache des brushes pré-créés
        self._red_brush = QBrush(QColor(255, 0, 0))
    
    def set_show_forbidden(self, show):
        self.show_forbidden = show
    
    def paint(self, painter, option, index):
        """Version optimisée du rendu"""
        # OPTIMISATION 9: Rendu conditionnel plus efficace
        if not self.show_forbidden or index.column() != 0:
            super().paint(painter, option, index)
            return
            
        # Vérification rapide du chemin
        model = index.model()
        path = ""
        
        if isinstance(model, QSortFilterProxyModel):
            source_model = model.sourceModel()
            source_index = model.mapToSource(index)
            if isinstance(source_model, QFileSystemModel):
                path = source_model.filePath(source_index)
        elif isinstance(model, QFileSystemModel):
            path = model.filePath(index)
        
        # Rendu optimisé
        if path and self.is_forbidden_path(path):
            painter.save()
            text = index.data(Qt.DisplayRole)
            if text:
                painter.setPen(self._red_brush.color())
                painter.drawText(option.rect, Qt.AlignVCenter | Qt.AlignLeft, text)
            painter.restore()
        else:
            super().paint(painter, option, index)
    
    def is_forbidden_path(self, path):
        """Version ultra-rapide de la vérification"""
        if not path:
            return False
            
        path_lower = path.replace("\\", "/").lower()
        
        for drive in self.system_drives:
            drive_prefix = f"{drive}:/"
            if path_lower.startswith(drive_prefix):
                end_pos = path_lower.find("/", len(drive_prefix))
                if end_pos == -1:
                    folder_name = path_lower[len(drive_prefix):]
                else:
                    folder_name = path_lower[len(drive_prefix):end_pos]
                
                return folder_name in self.forbidden_paths
        return False


class FileTreeWidget(QWidget):
    """Widget d'arborescence optimisé"""
    
    # Signaux inchangés
    path_selected = Signal(str)
    item_clicked = Signal(str, bool)
    item_double_clicked = Signal(str, bool)
    search_text_changed = Signal(str)
    file_operation = Signal(str, str, bool, bool)
    
    def __init__(self, parent=None, root_path=None):
        super().__init__(parent)
        
        locale.setlocale(locale.LC_ALL, '')
        
        # OPTIMISATION 10: Utilisation des modèles optimisés
        self.file_system_model = QFileSystemModel(self)
        self.proxy_model = ForbiddenPathProxyModel(self)
        self.proxy_model.setSourceModel(self.file_system_model)
        
        # Configuration optimisée du modèle
        self.file_system_model.setReadOnly(False)
        self.file_system_model.setNameFilterDisables(False)
        self.file_system_model.setFilter(QDir.AllDirs | QDir.Files | QDir.NoDotAndDotDot)
        self.file_system_model.setResolveSymlinks(False)  # Désactiver pour de meilleures performances
        
        # Afficher tous les lecteurs
        self.file_system_model.setRootPath('')
        
        # OPTIMISATION 11: Désactiver le tri automatique initially
        self.proxy_model.setDynamicSortFilter(False)
        
        self.tree_view = None
        self.path_label = None
        self.show_all_checkbox = None
        self.root_path = None
        self.delegate = None
        
        # OPTIMISATION 12: Timer de refresh débounced
        self._refresh_timer = QTimer()
        self._refresh_timer.setSingleShot(True)
        self._refresh_timer.timeout.connect(self._do_refresh)
        
        # OPTIMISATION 13: Suivi des expansions pour optimiser le cache
        self._expanded_paths = set()
        
        self.init_ui()
        self.setup_connections()
        
        # Activation du tri après initialisation
        self.proxy_model.setDynamicSortFilter(True)
        
        if root_path and os.path.exists(root_path):
            self.set_root_path(root_path)
        else:
            self.refresh_tree_view()
    
    def init_ui(self):
        """Interface utilisateur optimisée"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Layout du chemin
        path_layout = QHBoxLayout()
        path_layout.setContentsMargins(5, 5, 5, 0)
        path_layout.setSpacing(5)
        
        self.path_label = QLabel("Chemin:")
        path_layout.addWidget(self.path_label)
        path_layout.addStretch()
        main_layout.addLayout(path_layout)
        
        # Layout checkbox
        checkbox_layout = QHBoxLayout()
        checkbox_layout.setContentsMargins(5, 0, 5, 5)
        checkbox_layout.setSpacing(5)
        
        self.show_all_checkbox = QCheckBox("Afficher tout")
        self.show_all_checkbox.setChecked(False)
        checkbox_layout.addWidget(self.show_all_checkbox)
        checkbox_layout.addStretch()
        main_layout.addLayout(checkbox_layout)
        
        # OPTIMISATION 14: TreeView avec configuration optimale
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.proxy_model)
        self.tree_view.setAnimated(False)  # Désactiver animations pour performance
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setIndentation(20)
        self.tree_view.setSortingEnabled(True)
        self.tree_view.sortByColumn(0, Qt.AscendingOrder)
        self.tree_view.setEditTriggers(QTreeView.NoEditTriggers)
        self.tree_view.setExpandsOnDoubleClick(True)
        self.tree_view.setSelectionMode(QTreeView.SingleSelection)
        self.tree_view.setUniformRowHeights(True)  # Important pour la performance
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.show_context_menu)
        
        # OPTIMISATION 15: Connexions pour le tracking des expansions
        self.tree_view.expanded.connect(self._on_item_expanded)
        self.tree_view.collapsed.connect(self._on_item_collapsed)
        
        # Masquer colonnes non utilisées
        for column in range(1, self.file_system_model.columnCount()):
            self.tree_view.setColumnHidden(column, True)
        
        self.tree_view.setColumnWidth(0, 250)
        
        # Délégué optimisé
        self.delegate = ForbiddenPathDelegate(self.tree_view)
        self.tree_view.setItemDelegate(self.delegate)
        
        main_layout.addWidget(self.tree_view)
    
    def _on_item_expanded(self, index):
        """Track des expansions pour optimisation du cache"""
        source_index = self.proxy_model.mapToSource(index)
        path = self.file_system_model.filePath(source_index)
        self._expanded_paths.add(path)
    
    def _on_item_collapsed(self, index):
        """Track des collapsions"""
        source_index = self.proxy_model.mapToSource(index)
        path = self.file_system_model.filePath(source_index)
        self._expanded_paths.discard(path)
    
    def setup_connections(self):
        """Connexions optimisées"""
        if self.tree_view:
            self.tree_view.clicked.connect(self.on_tree_item_clicked)
            self.tree_view.doubleClicked.connect(self.on_tree_item_double_clicked)
        
        if self.show_all_checkbox:
            self.show_all_checkbox.stateChanged.connect(self.on_show_all_changed)
    
    def refresh_tree_view(self, keep_selection=True):
        """Refresh optimisé avec débouncing"""
        self._refresh_timer.start(REFRESH_DEBOUNCE_MS)
    
    def _do_refresh(self):
        """Refresh effectif optimisé"""
        selected_path = self.get_selected_path() if hasattr(self, 'get_selected_path') else None
        
        # OPTIMISATION 16: Refresh minimal du modèle
        try:
            # Utiliser la méthode refresh si disponible (PySide6 >= 6.2)
            self.file_system_model.refresh()
        except AttributeError:
            # Fallback pour versions antérieures
            current_root = self.file_system_model.rootPath()
            self.file_system_model.setRootPath('')
            if current_root:
                self.file_system_model.setRootPath(current_root)
        
        # Forcer recalcul proxy avec cache clear
        self.proxy_model._clear_filter_cache()
        self.proxy_model.invalidateFilter()
        
        # Restaurer la vue
        if self.root_path:
            root_index = self.file_system_model.index(self.root_path)
            proxy_root_index = self.proxy_model.mapFromSource(root_index)
            self.tree_view.setRootIndex(proxy_root_index)
            # OPTIMISATION 17: Restorer seulement les expansions trackées
            self._restore_expansions()
        else:
            self.tree_view.setRootIndex(QModelIndex())
        
        # Restaurer sélection si possible
        if selected_path and os.path.exists(selected_path):
            index = self.file_system_model.index(selected_path)
            proxy_index = self.proxy_model.mapFromSource(index)
            if proxy_index.isValid():
                self.tree_view.setCurrentIndex(proxy_index)
                self.tree_view.scrollTo(proxy_index)
        
        self.tree_view.viewport().update()
    
    def _restore_expansions(self):
        """Restaure seulement les expansions trackées"""
        for path in self._expanded_paths.copy():
            if os.path.exists(path):
                index = self.file_system_model.index(path)
                proxy_index = self.proxy_model.mapFromSource(index)
                if proxy_index.isValid():
                    self.tree_view.expand(proxy_index)
            else:
                self._expanded_paths.discard(path)
    
    # Méthodes de base inchangées mais optimisées avec les nouveaux composants
    def set_root_path(self, path):
        if not path or not os.path.exists(path):
            return
        
        self.root_path = path
        
        if self.show_all_checkbox.isChecked():
            self.path_label.setText(f"Chemin: Tous les lecteurs (Projet: {path})")
            return
            
        root_index = self.file_system_model.setRootPath(path)
        proxy_index = self.proxy_model.mapFromSource(root_index)
        self.tree_view.setRootIndex(proxy_index)
        self.path_label.setText(f"Chemin: {path}")
        self.tree_view.expand(proxy_index)
    
    def get_selected_path(self):
        selected_indices = self.tree_view.selectedIndexes()
        if not selected_indices:
            return None
        
        selected_index = selected_indices[0]
        source_index = self.proxy_model.mapToSource(selected_index)
        return self.file_system_model.filePath(source_index)
    
    def on_tree_item_clicked(self, index):
        path = self.get_selected_path()
        if path:
            self.path_selected.emit(path)
            is_dir = os.path.isdir(path)
            self.item_clicked.emit(path, is_dir)
    
    def on_tree_item_double_clicked(self, index):
        path = self.get_selected_path()
        if path:
            is_dir = os.path.isdir(path)
            self.item_double_clicked.emit(path, is_dir)
    
    def on_show_all_changed(self, state):
        show_all = (state == Qt.Checked.value)
        self.proxy_model.set_show_forbidden(False)
        self.delegate.set_show_forbidden(False)
        
        if show_all:
            self.root_path = None
            self.refresh_tree_view()
        else:
            if self.root_path and os.path.exists(self.root_path):
                root_index = self.file_system_model.setRootPath(self.root_path)
                proxy_index = self.proxy_model.mapFromSource(root_index)
                self.tree_view.setRootIndex(proxy_index)
                self.path_label.setText(f"Chemin: {self.root_path}")
            else:
                self.file_system_model.setRootPath(QDir.rootPath())
                root_index = self.file_system_model.index(QDir.rootPath())
                proxy_root_index = self.proxy_model.mapFromSource(root_index)
                self.tree_view.setRootIndex(proxy_root_index)
                self.path_label.setText("Chemin: Tous les lecteurs")
        
        self.proxy_model.invalidateFilter()
        self.tree_view.expand(self.tree_view.rootIndex())
        self.tree_view.repaint()
        self.tree_view.viewport().update()
    
    # Autres méthodes inchangées...
    def show_context_menu(self, position):
        """Menu contextuel (inchangé)"""
        index = self.tree_view.indexAt(position)
        
        if not index.isValid():
            menu = QMenu(self)
            create_folder_action = menu.addAction("Créer un répertoire")
            create_folder_action.triggered.connect(lambda: self.create_folder(None))
            menu.exec_(self.tree_view.viewport().mapToGlobal(position))
            return
            
        source_index = self.proxy_model.mapToSource(index)
        path = self.file_system_model.filePath(source_index)
        is_dir = os.path.isdir(path)
        
        menu = QMenu(self)
        
        if is_dir:
            create_folder_action = menu.addAction("Créer un répertoire")
            create_folder_action.triggered.connect(lambda: self.create_folder(path))
            
            delete_folder_action = menu.addAction("Supprimer le répertoire")
            delete_folder_action.triggered.connect(lambda: self.delete_item(path))
        else:
            delete_file_action = menu.addAction("Supprimer le fichier")
            delete_file_action.triggered.connect(lambda: self.delete_item(path))
        
        menu.exec_(self.tree_view.viewport().mapToGlobal(position))
    
    def create_folder(self, parent_path):
        """Création dossier (inchangé)"""
        if not parent_path:
            if self.root_path:
                parent_path = self.root_path
            else:
                QMessageBox.warning(self, "Erreur", "Aucun répertoire sélectionné ou racine définie")
                return
        
        folder_name, ok = QInputDialog.getText(
            self, "Créer un répertoire", "Nom du répertoire:"
        )
        
        if ok and folder_name:
            new_folder_path = os.path.join(parent_path, folder_name)
            
            if os.path.exists(new_folder_path):
                QMessageBox.warning(self, "Erreur", f"Le répertoire '{folder_name}' existe déjà")
                return
            
            try:
                os.makedirs(new_folder_path, exist_ok=True)
                self.update_tree_view_and_select_folder(new_folder_path)
                self.file_operation.emit("create", new_folder_path, True, True)
                print(f"Répertoire créé : {new_folder_path}")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible de créer le répertoire: {str(e)}")
    
    def delete_item(self, path):
        """Suppression item (inchangé)"""
        if not path or not os.path.exists(path):
            QMessageBox.warning(self, "Erreur", "Élément inexistant")
            return
        
        is_dir = os.path.isdir(path)
        item_name = os.path.basename(path)
        item_type = "répertoire" if is_dir else "fichier"
        
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Confirmation de suppression")
        msg_box.setText(f"Êtes-vous sûr de vouloir supprimer {item_type} '{item_name}'?")
        
        oui_button = msg_box.addButton("Oui", QMessageBox.YesRole)
        non_button = msg_box.addButton("Non", QMessageBox.NoRole)
        msg_box.setDefaultButton(non_button)
        
        msg_box.exec_()
        
        if msg_box.clickedButton() == oui_button:
            try:
                if is_dir:
                    import shutil
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                
                self.root_path = None
                self.refresh_tree_view(keep_selection=False)
                self.file_operation.emit("delete", path, True, is_dir)
                print(f"{item_type.capitalize()} supprimé : {path}")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible de supprimer {item_type}: {str(e)}")
    
    def highlight_tree_view(self, flashes=2, duration_on=250, duration_off=250):
        """Clignotement (inchangé)"""
        if not self.tree_view:
            return

        original_stylesheet = self.tree_view.styleSheet()
        highlight_style = "QTreeView { background-color: #4a4a4a; border: 1px solid #35fc84; }"

        def _flash(count):
            if count <= 0:
                self.tree_view.setStyleSheet(original_stylesheet)
                return

            self.tree_view.setStyleSheet(highlight_style)
            QTimer.singleShot(duration_on, lambda: _turn_off(count))

        def _turn_off(count):
            self.tree_view.setStyleSheet(original_stylesheet)
            if count > 1:
                QTimer.singleShot(duration_off, lambda: _flash(count - 1))

        _flash(flashes)

    def update_tree_view_and_select_folder(self, folder_path):
        """Mise à jour et sélection (optimisé)"""
        if not os.path.exists(folder_path):
            print(f"Le dossier {folder_path} n'existe pas.")
            return
            
        if self.root_path is None or not folder_path.startswith(self.root_path):
            self.set_root_path(os.path.dirname(folder_path))
        
        # OPTIMISATION 18: Sélection et expansion optimisées
        index = self.file_system_model.index(folder_path)
        if index.isValid():
            proxy_index = self.proxy_model.mapFromSource(index)
            if proxy_index.isValid():
                self.tree_view.setCurrentIndex(proxy_index)
                parent = proxy_index.parent()
                if parent.isValid():
                    self.tree_view.expand(parent)
                self.tree_view.scrollTo(proxy_index)
                self.highlight_tree_view()