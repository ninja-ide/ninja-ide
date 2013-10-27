# -*- coding: utf-8 -*-
#
# This file is part of NINJA-IDE (http://ninja-ide.org).
#
# NINJA-IDE is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.
#
# NINJA-IDE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NINJA-IDE; If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import
from __future__ import unicode_literals

import os

from ninja_ide.tools.logger import NinjaLogger
logger = NinjaLogger('ninja_ide.gui.explorer.tree_projects_widget')
DEBUG = logger.debug

from PyQt4.QtGui import QTreeView
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QScrollArea
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QTreeWidgetItem
from PyQt4.QtGui import QAbstractItemView
from PyQt4.QtGui import QHeaderView
from PyQt4.QtGui import QFileDialog
from PyQt4.QtGui import QInputDialog
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QColor
from PyQt4.QtGui import QBrush
from PyQt4.QtGui import QLinearGradient
from PyQt4.QtGui import QMenu
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QStyle
from PyQt4.QtGui import QCursor
from PyQt4.QtGui import QFontMetrics
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QUrl
from PyQt4.QtGui import QDesktopServices

from ninja_ide import translations
from ninja_ide.core import settings
from ninja_ide.core.file_handling import file_manager
from ninja_ide.core.file_handling.filesystem_notifications import (
    NinjaFileSystemWatcher)
from ninja_ide.tools import ui_tools
from ninja_ide.gui.ide import IDE
from ninja_ide.gui.dialogs import project_properties_widget
from ninja_ide.gui.explorer import actions
from ninja_ide.gui.explorer.nproject import NProject
from ninja_ide.tools.completion import completion_daemon


def scrollable_wrapper(widget):
    scrollable = QScrollArea()
    scrollable.setWidget(widget)
    scrollable.setWidgetResizable(True)
    scrollable.setEnabled(True)
    return scrollable


class TreeHeader(QHeaderView):
    """
    SIGNALS:
    @headerClicked(QPoint)
    """

    def __init__(self):
        super(TreeHeader, self).__init__(Qt.Horizontal)
        self.title = ""
        self.is_current_project = False
        self._mouse_over = False
        self.setToolTip(translations.TR_PROJECT_OPTIONS)

    def paintSection(self, painter, rect, logicalIndex):
        gradient = QLinearGradient(0, 0, 0, rect.height())
        if self._mouse_over:
            gradient.setColorAt(0.0, QColor("#808080"))
            gradient.setColorAt(1.0, QColor("#474747"))
        else:
            gradient.setColorAt(0.0, QColor("#727272"))
            gradient.setColorAt(1.0, QColor("#363636"))
        painter.fillRect(rect, QBrush(gradient))

        if self.is_current_project:
            painter.setPen(QColor(0, 204, 82))
        else:
            painter.setPen(QColor(Qt.white))
        font = painter.font()
        font.setBold(True)
        painter.setFont(font)
        font_metrics = QFontMetrics(painter.font())
        ypos = (rect.height() / 2) + (font_metrics.height() / 3)
        painter.drawText(10, ypos, self.title)

    def enterEvent(self, event):
        super(TreeHeader, self).enterEvent(event)
        self._mouse_over = True

    def leaveEvent(self, event):
        super(TreeHeader, self).leaveEvent(event)
        self._mouse_over = False

    def mousePressEvent(self, event):
        super(TreeHeader, self).mousePressEvent(event)
        self.emit(SIGNAL("headerClicked(QPoint)"), QCursor.pos())


class ProjectTreeColumn(QScrollArea):

    def __init__(self, *args, **kwargs):
        super(ProjectTreeColumn, self).__init__(*args, **kwargs)
        self._widget = QWidget()
        self._widget.setLayout(QVBoxLayout())
        self.setWidget(self._widget)
        self.setWidgetResizable(True)
        self.setEnabled(True)
        self.projects = []
        self._active_project = None

        #connections = (
            #{'target': 'main_container',
            #'signal_name': 'openProject(QString)',
            #'slot': self.open_project_folder},
                #)
        #IDE.register_signals('tree_projects_widget', connections)

    def install(self):
        ide = IDE.get_service('ide')
        ui_tools.install_shortcuts(self, actions.PROJECTS_TREE_ACTIONS, ide)

    def open_project_folder(self):
        if settings.WORKSPACE:
            directory = settings.WORKSPACE
        else:
            directory = os.path.expanduser("~")

        folderName = QFileDialog.getExistingDirectory(self,
                self.tr("Open Project Directory"), directory)
        logger.debug("Choosing Foldername")
        if folderName:
            logger.debug("Opening %s" % folderName)
            ninjaide = IDE.get_service("ide")
            project = NProject(folderName)
            qfsm = ninjaide.filesystem.open_project(project)
            if qfsm:
                self.add_project(project)

    def add_project(self, project):
        if project not in self.projects:
            ptree = TreeProjectsWidget(project)
            self.connect(ptree, SIGNAL("setActiveProject(PyQt_PyObject)"),
                self._set_active_project)
            pmodel = project.model
            ptree.setModel(pmodel)
            ptree.header().title = project.name
            pindex = pmodel.index(pmodel.rootPath())
            ptree.setRootIndex(pindex)
            self._widget.layout().addWidget(scrollable_wrapper(ptree))
            if self._active_project is None:
                ptree.set_default_project()
            self.projects.append(ptree)

    def _set_active_project(self, tree_proj):
        self._active_project = tree_proj


class TreeProjectsWidget(QTreeView):

###############################################################################
# TreeProjectsWidget SIGNALS
###############################################################################

    """
    runProject()
    setActiveProject(PyQt_PyObject)
    closeProject(QString)
    closeFilesFromProjectClosed(QString)
    addProjectToConsole(QString)
    removeProjectFromConsole(QString)
    projectPropertiesUpdated(QTreeWidgetItem)
    """

###############################################################################

    #Extra context menu 'all' indicate a menu for ALL LANGUAGES!
    extra_menus = {'all': []}
    #Extra context menu by scope all is for ALL the TREE ITEMS!
    extra_menus_by_scope = {'project': [], 'folder': [], 'file': []}

    images = {
        'py': ":img/tree-python",
        'jpg': ":img/tree-image",
        'png': ":img/tree-image",
        'html': ":img/tree-html",
        'css': ":img/tree-css",
        'ui': ":img/designer"}

    def __format_tree(self):
        """If not called after setting model, all the column format
        options are reset to default when the model is set"""
        self.setSelectionMode(QTreeView.SingleSelection)
        self.setAnimated(True)

        t_header = TreeHeader()
        self.connect(t_header, SIGNAL("headerClicked(QPoint)"),
            lambda point: self._menu_context_tree(point, True))
        self.setHeader(t_header)
        t_header.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        t_header.setResizeMode(0, QHeaderView.Stretch)
        t_header.setStretchLastSection(False)
        t_header.setClickable(True)

        self.hideColumn(1)  # Size
        self.hideColumn(2)  # Type
        self.hideColumn(3)  # Modification date

    def setModel(self, model):
        super(TreeProjectsWidget, self).setModel(model)
        self.__format_tree()
        #Activated is said to do the right thing on every system
        self.connect(self, SIGNAL("activated(const QModelIndex &)"),
                    self._open_file)

    def __init__(self, project, state_index=list()):
        super(TreeProjectsWidget, self).__init__()
        self.project = project

        self._actualProject = None
        #self._projects -> key: [Item, folderStructure]
        self._projects = {}
        self._loading_items = {}
        self._thread_execution = {}
        self.__enableCloseNotification = True
        self._fileWatcher = NinjaFileSystemWatcher
        self._timer_running = False

        self.__format_tree()

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.connect(self, SIGNAL(
            "customContextMenuRequested(const QPoint &)"),
            self._menu_context_tree)

        self.expanded.connect(self._item_expanded)
        self.collapsed.connect(self._item_collapsed)
        self.mute_signals = False
        self.state_index = list()
        self._folding_menu = FoldingContextMenu(self)

    def _item_collapsed(self, tree_item):
        """Store status of item when collapsed"""
        if not self.mute_signals:
            path = self.model().filePath(tree_item)
            if path in self.state_index:
                path_index = self.state_index.index(path)
                self.state_index.pop(path_index)

    def _item_expanded(self, tree_item):
        """Store status of item when expanded"""
        if not self.mute_signals:
            path = self.model().filePath(tree_item)
            if path not in self.state_index:
                self.state_index.append(path)

    def add_extra_menu(self, menu, lang='all'):
        '''
        Add an extra menu for the given language
        @lang: string with the form 'py', 'php', 'json', etc
        '''
        #remove blanks and replace dots Example(.py => py)
        lang = lang.strip().replace('.', '')
        self.extra_menus.setdefault(lang, [])
        self.extra_menus[lang].append(menu)

    def add_extra_menu_by_scope(self, menu, scope):
        '''
        Add an extra menu for the given language
        @scope: string with the menu scope (all, project, folder, item)
        '''
        if scope.project:
            self.extra_menus_by_scope['project'].append(menu)
        if scope.folder:
            self.extra_menus_by_scope['folder'].append(menu)
        if scope.file:
            self.extra_menus_by_scope['file'].append(menu)

    def _menu_context_tree(self, point, isRoot=False):
        index = self.indexAt(point)
        if not index.isValid() and not isRoot:
            return

        handler = None
        menu = QMenu(self)
        if isRoot or self.model().isDir(index):
            self._add_context_menu_for_folders(menu, isRoot)
        else:
            filename = self.model().fileName(index)
            lang = file_manager.get_file_extension(filename)
            self._add_context_menu_for_files(menu, lang)
        if isRoot:
            #get the extra context menu for this projectType
            handler = settings.get_project_type_handler(
                self.project.project_type)
            self._add_context_menu_for_root(menu)

        menu.addMenu(self._folding_menu)

        #menu for all items (legacy API)!
        extra_menus = self.extra_menus.get('all', ())
        #menu for all items!
        for m in extra_menus:
            if isinstance(m, QMenu):
                menu.addSeparator()
                menu.addMenu(m)
        #menu for the Project Type(if present)
        if handler:
            for m in handler.get_context_menus():
                if isinstance(m, QMenu):
                    menu.addSeparator()
                    menu.addMenu(m)
        #show the menu!
        menu.exec_(QCursor.pos())

    def _add_context_menu_for_root(self, menu):
        menu.addSeparator()
        actionRunProject = menu.addAction(QIcon(
            ":img/play"), self.tr("Run Project"))
        self.connect(actionRunProject, SIGNAL("triggered()"),
            SIGNAL("runProject()"))
        actionMainProject = menu.addAction(self.tr("Set as Main Project"))
        self.connect(actionMainProject, SIGNAL("triggered()"),
            self.set_default_project)
        #if item.addedToConsole:
            #actionRemoveFromConsole = menu.addAction(
                #self.tr("Remove this Project from the Python Console"))
            #self.connect(actionRemoveFromConsole, SIGNAL("triggered()"),
                #self._remove_project_from_console)
        #else:
            #actionAdd2Console = menu.addAction(
                #self.tr("Add this Project to the Python Console"))
            #self.connect(actionAdd2Console, SIGNAL("triggered()"),
                #self._add_project_to_console)
        actionProperties = menu.addAction(QIcon(":img/pref"),
            self.tr("Project Properties"))
        self.connect(actionProperties, SIGNAL("triggered()"),
            self.open_project_properties)

        menu.addSeparator()
        action_close = menu.addAction(
            self.style().standardIcon(QStyle.SP_DialogCloseButton),
            self.tr("Close Project"))
        self.connect(action_close, SIGNAL("triggered()"),
            self._close_project)
        #menu for the project
        for m in self.extra_menus_by_scope['project']:
            if isinstance(m, QMenu):
                menu.addSeparator()
                menu.addMenu(m)

    def _add_context_menu_for_folders(self, menu, isRoot):
        action_add_file = menu.addAction(QIcon(":img/new"),
                    self.tr("Add New File"))
        self.connect(action_add_file, SIGNAL("triggered()"),
            self._add_new_file)
        action_add_folder = menu.addAction(QIcon(
            ":img/openProj"), self.tr("Add New Folder"))
        self.connect(action_add_folder, SIGNAL("triggered()"),
            self._add_new_folder)
        action_create_init = menu.addAction(
            self.tr("Create '__init__' Complete"))
        self.connect(action_create_init, SIGNAL("triggered()"),
            self._create_init)
        if not isRoot:
            #Folders but not the root
            action_remove_folder = menu.addAction(self.tr("Remove Folder"))
            self.connect(action_remove_folder, SIGNAL("triggered()"),
                self._delete_folder)
            for m in self.extra_menus_by_scope['folder']:
                if isinstance(m, QMenu):
                    menu.addSeparator()
                    menu.addMenu(m)

    def _add_context_menu_for_files(self, menu, lang):
        action_rename_file = menu.addAction(self.tr("Rename File"))
        action_move_file = menu.addAction(self.tr("Move File"))
        action_copy_file = menu.addAction(self.tr("Copy File"))
        action_remove_file = menu.addAction(
            self.style().standardIcon(QStyle.SP_DialogCloseButton),
            self.tr("Delete File"))
        self.connect(action_remove_file, SIGNAL("triggered()"),
            self._delete_file)
        self.connect(action_rename_file, SIGNAL("triggered()"),
            self._rename_file)
        self.connect(action_copy_file, SIGNAL("triggered()"),
            self._copy_file)
        self.connect(action_move_file, SIGNAL("triggered()"),
            self._move_file)
        #Allow to edit Qt UI files with the appropiate program
        if lang == 'ui':
            action_edit_ui_file = menu.addAction(self.tr("Edit UI File"))
            self.connect(action_edit_ui_file, SIGNAL("triggered()"),
                self._edit_ui_file)
        #menu per file language (legacy plugin API)!
        for m in self.extra_menus.get(lang, ()):
            if isinstance(m, QMenu):
                menu.addSeparator()
                menu.addMenu(m)
        #menu for files
        for m in self.extra_menus_by_scope['file']:
            if isinstance(m, QMenu):
                menu.addSeparator()
                menu.addMenu(m)

    def _add_project_to_console(self):
        item = self.currentItem()
        if isinstance(item, ProjectTree):
            self.emit(SIGNAL("addProjectToConsole(QString)"), item.path)
            item.addedToConsole = True

    def _remove_project_from_console(self):
        item = self.currentItem()
        if isinstance(item, ProjectTree):
            self.emit(SIGNAL("removeProjectFromConsole(QString)"), item.path)
            item.addedToConsole = False

    def _open_file(self, model_index):
        path = self.model().filePath(model_index)
        main_container = IDE.get_service('main_container')
        logger.debug("tried to get main container")
        if main_container:
            logger.debug("will call open file")
            main_container.open_file(path)

    def _get_project_root(self, item=None):
        if item is None:
            item = self.currentItem()
        while item is not None and item.parent() is not None:
            item = item.parent()
        return item

    def set_default_project(self):
        self.header().is_current_project = True
        self.emit(SIGNAL("setActiveProject(PyQt_PyObject)"), self)

    def open_project_properties(self):
        item = self._get_project_root()
        proj = project_properties_widget.ProjectProperties(item, self)
        proj.show()

    def _clean_threads(self):
        paths_to_delete = []
        for path in self._thread_execution:
            thread = self._thread_execution.get(path, None)
            if thread and not thread.isRunning():
                paths_to_delete.append(path)
        for path in paths_to_delete:
            thread = self._thread_execution.pop(path, None)
            if thread:
                thread.wait()

    def _close_project(self):
        item = self.currentItem()
        index = self.indexOfTopLevelItem(item)
        pathKey = item.path
        self._fileWatcher.remove_watch(pathKey)
        self.takeTopLevelItem(index)
        self._projects.pop(pathKey, None)
        if self.__enableCloseNotification:
            self.emit(SIGNAL("closeProject(QString)"), pathKey)
        self.emit(SIGNAL("closeFilesFromProjectClosed(QString)"), pathKey)
        item = self.currentItem()
        if item:
            self.set_default_project(item)
            self._actualProject = item
        else:
            self._actualProject = None

    def _create_init(self):
        item = self.currentItem()
        if item.parent() is None:
            pathFolder = item.path
        else:
            pathFolder = os.path.join(item.path, str(item.text(0)))
        try:
            file_manager.create_init_file_complete(pathFolder)
        except file_manager.NinjaFileExistsException as ex:
            QMessageBox.information(self, self.tr("Create INIT fail"),
                ex.message)

    def _add_new_file(self):
        item = self.currentItem()
        if item.parent() is None:
            pathForFile = item.path
        else:
            pathForFile = os.path.join(item.path, item.text(0))
        result = QInputDialog.getText(self, self.tr("New File"),
            self.tr("Enter the File Name:"))
        fileName = result[0]

        if result[1] and fileName.strip() != '':
            try:
                fileName = os.path.join(pathForFile, fileName)
                fileName = file_manager.store_file_content(
                    fileName, '', newFile=True)
                name = file_manager.get_basename(fileName)
                subitem = ProjectItem(item, name, pathForFile)
                subitem.setToolTip(0, name)
                subitem.setIcon(0, self._get_file_icon(name))
                main_container = IDE.get_service('main_container')
                if main_container:
                    main_container.open_file(fileName)
            except file_manager.NinjaFileExistsException as ex:
                QMessageBox.information(self, self.tr("File Already Exists"),
                    (self.tr("Invalid Path: the file '%s' already exists.") %
                        ex.filename))

    def add_existing_file(self, path):
        relative = file_manager.convert_to_relative(
            self._actualProject.path, path)
        paths = relative.split(os.sep)[:-1]
        itemParent = self._actualProject
        for p in paths:
            for i in range(itemParent.childCount()):
                item = itemParent.child(i)
                if item.text(0) == p:
                    itemParent = item
                    break
        itemParent.setSelected(True)
        name = file_manager.get_basename(path)
        subitem = ProjectItem(itemParent, name, file_manager.get_folder(path))
        subitem.setToolTip(0, name)
        subitem.setIcon(0, self._get_file_icon(name))
        itemParent.setExpanded(True)

    def _add_new_folder(self):
        item = self.currentItem()
        if item.parent() is None:
            pathForFolder = item.path
        else:
            pathForFolder = os.path.join(item.path, item.text(0))
        result = QInputDialog.getText(self, self.tr("New Folder"),
            self.tr("Enter the Folder Name:"))
        folderName = result[0]

        if result[1] and folderName.strip() != '':
            folderName = os.path.join(pathForFolder, folderName)
            file_manager.create_folder(folderName)
            name = file_manager.get_basename(folderName)
            subitem = ProjectItem(item, name, pathForFolder)
            subitem.setToolTip(0, name)
            subitem.setIcon(0, QIcon(":img/tree-folder"))

    def _delete_file(self):
        item = self.currentItem()
        val = QMessageBox.question(self, self.tr("Delete File"),
                self.tr("Do you want to delete the following file: ")
                + os.path.join(item.path, item.text(0)),
                QMessageBox.Yes, QMessageBox.No)
        if val == QMessageBox.Yes:
            path = file_manager.create_path(item.path, item.text(0))
            file_manager.delete_file(item.path, item.text(0))
            index = item.parent().indexOfChild(item)
            item.parent().takeChild(index)
            main_container = IDE.get_service('main_container')
            if main_container and main_container.is_open(path):
                main_container.close_deleted_file(path)

    def _delete_folder(self):
        item = self.currentItem()
        val = QMessageBox.question(self, self.tr("Delete Folder"),
                self.tr("Do you want to delete the following folder: ")
                + os.path.join(item.path, item.text(0)),
                QMessageBox.Yes, QMessageBox.No)
        if val == QMessageBox.Yes:
            file_manager.delete_folder(item.path, item.text(0))
            index = item.parent().indexOfChild(item)
            item.parent().takeChild(index)

    def _rename_file(self):
        item = self.currentItem()
        if item.parent() is None:
            pathForFile = item.path
        else:
            pathForFile = os.path.join(item.path, item.text(0))
        result = QInputDialog.getText(self, self.tr("Rename File"),
            self.tr("Enter New File Name:"), text=item.text(0))
        fileName = result[0]

        if result[1] and fileName.strip() != '':
            fileName = os.path.join(
                file_manager.get_folder(pathForFile), fileName)
            if pathForFile == fileName:
                return
            try:
                fileName = file_manager.rename_file(pathForFile, fileName)
                name = file_manager.get_basename(fileName)
                main_container = IDE.get_service('main_container')
                if main_container and main_container.is_open(pathForFile):
                    main_container.change_open_tab_name(pathForFile, fileName)
                subitem = ProjectItem(item.parent(), name,
                    file_manager.get_folder(fileName))
                subitem.setToolTip(0, name)
                subitem.setIcon(0, self._get_file_icon(name))
                index = item.parent().indexOfChild(item)
                subitem.parent().takeChild(index)
            except file_manager.NinjaFileExistsException as ex:
                QMessageBox.information(self, self.tr("File Already Exists"),
                    (self.tr("Invalid Path: the file '%s' already exists.") %
                        ex.filename))

    def _copy_file(self):
        #get the selected QTreeWidgetItem
        item = self.currentItem()
        if item.parent() is None:
            pathForFile = item.path
        else:
            pathForFile = os.path.join(item.path, item.text(0))
        pathProjects = [p.path for p in self.get_open_projects()]
        addToProject = ui_tools.AddToProject(pathProjects, self)
        addToProject.setWindowTitle(self.tr("Copy File to"))
        addToProject.exec_()
        if not addToProject.pathSelected:
            return
        name = QInputDialog.getText(self, self.tr("Copy File"),
            self.tr("File Name:"), text=item.text(0))[0]
        if not name:
            QMessageBox.information(self, self.tr("Invalid Name"),
                self.tr("The file name is empty, please enter a name"))
            return
        path = file_manager.create_path(addToProject.pathSelected, name)
        try:
            content = file_manager.read_file_content(pathForFile)
            path = file_manager.store_file_content(path, content, newFile=True)
            self.add_existing_file(path)
        except file_manager.NinjaFileExistsException as ex:
                QMessageBox.information(self, self.tr("File Already Exists"),
                    (self.tr("Invalid Path: the file '%s' already exists.") %
                        ex.filename))

    def _move_file(self):
        item = self.currentItem()
        if item.parent() is None:
            pathForFile = item.path
        else:
            pathForFile = os.path.join(item.path, item.text(0))
        pathProjects = [p.path for p in self.get_open_projects()]
        addToProject = ui_tools.AddToProject(pathProjects, self)
        addToProject.setWindowTitle(self.tr("Copy File to"))
        addToProject.exec_()
        if not addToProject.pathSelected:
            return
        name = file_manager.get_basename(pathForFile)
        path = file_manager.create_path(addToProject.pathSelected, name)
        try:
            content = file_manager.read_file_content(pathForFile)
            path = file_manager.store_file_content(path, content, newFile=True)
            file_manager.delete_file(pathForFile)
            index = item.parent().indexOfChild(item)
            item.parent().takeChild(index)
            self.add_existing_file(path)
            # Update path of opened file
            main = IDE.get_service('main_container')
            if main and main.is_open(pathForFile):
                widget = main.get_widget_for_path(pathForFile)
                if widget:
                    widget.ID = path
        except file_manager.NinjaFileExistsException as ex:
                QMessageBox.information(self, self.tr("File Already Exists"),
                    (self.tr("Invalid Path: the file '%s' already exists.") %
                        ex.filename))

    def _edit_ui_file(self):
        item = self.currentItem()
        if item.parent() is None:
            pathForFile = item.path
        else:
            pathForFile = os.path.join(item.path, item.text(0))
        pathForFile = "file://%s" % pathForFile
        #open the correct program to edit Qt UI files!
        QDesktopServices.openUrl(QUrl(pathForFile, QUrl.TolerantMode))

    def loading_project(self, folder, reload_item=None):
        loadingItem = ui_tools.LoadingItem()
        if reload_item is None:
            parent = self
        else:
            parent = reload_item.parent()
        item = loadingItem.add_item_to_tree(folder, self, ProjectItem, parent)
        self._loading_items[folder] = item

    def remove_loading_icon(self, folder):
        item = self._loading_items.pop(folder, None)
        if item is not None:
            index = self.indexOfTopLevelItem(item)
            self.takeTopLevelItem(index)

    def load_project(self, folderStructure, folder):
        if not folder:
            return

        self.remove_loading_icon(folder)

        ninjaide = IDE.get_service('ide')
        project = ninjaide.get_project(folder)
        item = ProjectTree(self, project)
        item.isFolder = True
        item.setToolTip(0, folder)
        item.setIcon(0, QIcon(":img/tree-app"))
        self._projects[folder] = item
        if folderStructure[folder][1] is not None:
            folderStructure[folder][1].sort()
        self._load_folder(folderStructure, folder, item)
        item.setExpanded(True)
        if len(self._projects) == 1:
            self.set_default_project(item)
        if self.currentItem() is None:
            item.setSelected(True)
            self.setCurrentItem(item)
        self._fileWatcher.add_watch(folder)
        completion_daemon.add_project_folder(folder)
        self.sortItems(0, Qt.AscendingOrder)

    def _load_folder(self, folderStructure, folder, parentItem):
        """Load the Tree Project structure recursively."""
        # Avoid failing if for some reason folder is not found
        # Might be the case of special files, as links or versioning files
        files, folders = folderStructure.get(folder, [None, None])

        if files is not None:
            files.sort()
            for i in files:
                subitem = ProjectItem(parentItem, i, folder)
                subitem.setToolTip(0, i)
                subitem.setIcon(0, self._get_file_icon(i))
        if folders is not None:
            folders.sort()
            for _folder in folders:
                if _folder.startswith('.'):
                    continue
                subfolder = ProjectItem(parentItem, _folder, folder, True)
                subfolder.setToolTip(0, _folder)
                subfolder.setIcon(0, QIcon(":img/tree-folder"))
                subFolderPath = os.path.join(folder, _folder)
                if subFolderPath in self.state_index:
                    subfolder.setExpanded(True)
                self._load_folder(folderStructure,
                    subFolderPath, subfolder)

    def _get_file_icon(self, fileName):
        return QIcon(self.images.get(file_manager.get_file_extension(fileName),
            ":img/tree-generic"))

    def get_item_for_path(self, path):
        items = self.findItems(file_manager.get_basename(path),
            Qt.MatchRecursive, 0)
        folder = file_manager.get_folder(path)
        for item in items:
            if file_manager.belongs_to_folder(folder, item.path):
                return item

    def get_project_by_name(self, projectName):
        """Return the name of the project item based on the project name."""
        # Return the item or None if it's not found
        for item in list(self._projects.values()):
            if item.name == projectName:
                return item

    def get_selected_project_path(self):
        if self._actualProject:
            return self._actualProject.path
        return None

    def get_selected_project_type(self):
        rootItem = self._get_project_root()
        return rootItem.projectType

    def get_selected_project_lang(self):
        rootItem = self._get_project_root()
        return rootItem.lang()

    def get_open_projects(self):
        return list(self._projects.values())

    def is_open(self, path):
        return len([True for item in list(self._projects.values())
            if item.path == path]) != 0

    def _set_current_project(self, path):
        for item in list(self._projects.values()):
            if item.path == path:
                self.set_default_project(item)
                break

    def _close_open_projects(self):
        self.__enableCloseNotification = False
        for i in range(self.topLevelItemCount()):
            self.setCurrentItem(self.topLevelItem(0))
            self._close_project()
        self.__enableCloseNotification = True
        self._projects = {}


class ProjectItem(QTreeWidgetItem):

    def __init__(self, parent, name, path, isFolder=False):
        QTreeWidgetItem.__init__(self, parent)
        self.setText(0, name)
        self.path = path
        self.isFolder = isFolder

    @property
    def isProject(self):
        #flag to check if the item is a project ALWAYS FALSE
        return False

    def lang(self):
        return file_manager.get_file_extension(self.text(0))

    def get_full_path(self):
        '''
        Returns the full path of the file
        '''
        return os.path.join(self.path, self.text(0))

    def set_item_icon(self, icon):
        self.setIcon(0, icon)

    def __lt__(self, otherItem):
        column = self.treeWidget().sortColumn()
        my_text = ('1%s' % self.text(column).lower() if
            self.isFolder else '0%s' % self.text(column).lower())
        other_text = ('1%s' % otherItem.text(column).lower() if
            otherItem.isFolder else '0%s' % otherItem.text(column).lower())
        return my_text < other_text


class ProjectTree(QTreeWidgetItem):

    def __init__(self, parent, project):
        QTreeWidgetItem.__init__(self, parent)
        self._parent = parent
        self._project = project
        self.setText(0, self._project.name)
        self.path = self._project.path
        self.isFolder = True
        self.setForeground(0, QBrush(QColor(255, 165, 0)))

        self.update_paths()

    def update_paths(self):
        for path in self._project.related_projects:
            completion_daemon.add_project_folder(path)

    @property
    def isProject(self):
        #flag to check if the item is a project ALWAYS TRUE
        return True

    def lang(self):
        if self._project.main_file != '':
            return file_manager.get_file_extension(self._project.main_file)
        return 'py'

    def get_full_path(self):
        '''
        Returns the full path of the project
        '''
        return self._project.full_path


class FoldingContextMenu(QMenu):
    """
    This class represents a menu for Folding/Unfolding task
    """

    def __init__(self, tree):
        super(FoldingContextMenu, self).__init__()
        self.setTitle(self.tr("Fold/Unfold"))
        self._tree = tree
        fold_project = self.addAction(self.tr("Fold the project"))
        unfold_project = self.addAction(self.tr("Unfold the project"))
        self.addSeparator()
        fold_all_projects = self.addAction(self.tr("Fold all projects"))
        unfold_all_projects = self.addAction(self.tr("Unfold all projects"))

        self.connect(fold_project, SIGNAL("triggered()"),
            lambda: self._fold_unfold_project(False))
        self.connect(unfold_project, SIGNAL("triggered()"),
            lambda: self._fold_unfold_project(True))
        self.connect(fold_all_projects, SIGNAL("triggered()"),
            self._fold_all_projects)
        self.connect(unfold_all_projects, SIGNAL("triggered()"),
            self._unfold_all_projects)

    def _recursive_fold_unfold(self, item, expand):
        if item.isFolder:
            item.setExpanded(expand)
        for index in range(item.childCount()):
            child = item.child(index)
            self._recursive_fold_unfold(child, expand)

    def _fold_unfold_project(self, expand):
        """
        Fold the current project
        """
        root = self._tree._get_project_root(item=self._tree.currentItem())
        childs = root.childCount()
        if childs:
            root.setExpanded(expand)

        for index in range(childs):
            item = root.child(index)
            self._recursive_fold_unfold(item, expand)

    def _fold_all_projects(self):
        """
        Fold all projects
        """
        self._tree.collapseAll()

    def _unfold_all_projects(self):
        """
        Unfold all project
        """
        self._tree.expandAll()


PTColumn = ProjectTreeColumn()
ec = IDE.get_service("explorer_container")
ec.addTab(PTColumn, PTColumn.tr('Projects'))