# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os

from PyQt4.QtGui import QTreeWidget
from PyQt4.QtGui import QTreeWidgetItem
from PyQt4.QtGui import QAbstractItemView
from PyQt4.QtGui import QHeaderView
from PyQt4.QtGui import QInputDialog
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QColor
from PyQt4.QtGui import QBrush
from PyQt4.QtGui import QMenu
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QStyle
from PyQt4.QtGui import QCursor
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QFileSystemWatcher

from ninja_ide import resources
from ninja_ide.core import settings
from ninja_ide.core import file_manager
from ninja_ide.tools import json_manager
from ninja_ide.tools import ui_tools
from ninja_ide.gui.main_panel import main_container
from ninja_ide.gui.dialogs import project_properties_widget


class TreeProjectsWidget(QTreeWidget):

###############################################################################
# TreeProjectsWidget SIGNALS
###############################################################################

    """
    runProject()
    closeProject(QString)
    addProjectToConsole(QString)
    removeProjectFromConsole(QString)
    """

###############################################################################

    #Extra context menu 'all' indicate a menu for ALL LANGUAGES!
    EXTRA_MENUS = {'all': []}
    images = {
        'py': resources.IMAGES['tree-python'],
        'java': resources.IMAGES['tree-java'],
        'fn': resources.IMAGES['tree-code'],
        'c': resources.IMAGES['tree-code'],
        'cs': resources.IMAGES['tree-code'],
        'jpg': resources.IMAGES['tree-image'],
        'png': resources.IMAGES['tree-image'],
        'html': resources.IMAGES['tree-html'],
        'css': resources.IMAGES['tree-css'],
        'ui': resources.IMAGES['designer']}

    def __init__(self):
        QTreeWidget.__init__(self)

        self.header().setHidden(True)
        self.setSelectionMode(QTreeWidget.SingleSelection)
        self.setAnimated(True)

        self._actualProject = None
        self._projects = {}
        self.__enableCloseNotification = True
        self._fileWatcher = QFileSystemWatcher()

        self.header().setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.header().setResizeMode(0, QHeaderView.ResizeToContents)
        self.header().setStretchLastSection(False)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.connect(self, SIGNAL(
            "customContextMenuRequested(const QPoint &)"),
            self._menu_context_tree)
        self.connect(self, SIGNAL("itemClicked(QTreeWidgetItem *, int)"),
            self._open_file)
        self.connect(self._fileWatcher, SIGNAL("directoryChanged(QString)"),
            self._refresh_project_by_path)

    def add_extra_menu(self, menu, lang='all'):
        '''
        Add an extra menu for the given language
        @lang: string with the form 'py', 'php', 'json', etc
        '''
        #remove blanks and replace dots Example(.py => py)
        lang = lang.strip().replace('.', '')
        self.EXTRA_MENUS.setdefault(lang, [])
        self.EXTRA_MENUS[lang].append(menu)

    def _menu_context_tree(self, point):
        index = self.indexAt(point)
        if not index.isValid():
            return

        item = self.itemAt(point)
        handler = None
        menu = QMenu(self)
        if item.isFolder or item.parent() is None:
            action_add_file = menu.addAction(QIcon(resources.IMAGES['new']),
                self.tr("Add New File"))
            self.connect(action_add_file, SIGNAL("triggered()"),
                self._add_new_file)
            action_add_folder = menu.addAction(QIcon(
                resources.IMAGES['openProj']), self.tr("Add New Folder"))
            self.connect(action_add_folder, SIGNAL("triggered()"),
                self._add_new_folder)
            action_create_init = menu.addAction(
                self.tr("Create '__init__' Complete"))
            self.connect(action_create_init, SIGNAL("triggered()"),
                self._create_init)
            if item.isFolder and (item.parent() != None):
                action_remove_folder = menu.addAction(self.tr("Remove Folder"))
                self.connect(action_remove_folder, SIGNAL("triggered()"),
                    self._delete_folder)
        elif not item.isFolder:
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
            #menu per file language!
            for m in self.EXTRA_MENUS.get(item.lang(), ()):
                menu.addSeparator()
                menu.addMenu(m)
        if item.parent() is None:
            menu.addSeparator()
            actionRunProject = menu.addAction(QIcon(
                resources.IMAGES['play']), self.tr("Run Project"))
            self.connect(actionRunProject, SIGNAL("triggered()"),
                SIGNAL("runProject()"))
            actionMainProject = menu.addAction(self.tr("Set as Main Project"))
            self.connect(actionMainProject, SIGNAL("triggered()"),
                lambda: self.set_default_project(item))
            if item.addedToConsole:
                actionRemoveFromConsole = menu.addAction(
                    self.tr("Remove this Project from the Python Console"))
                self.connect(actionRemoveFromConsole, SIGNAL("triggered()"),
                    self._remove_project_from_console)
            else:
                actionAdd2Console = menu.addAction(
                    self.tr("Add this Project to the Python Console"))
                self.connect(actionAdd2Console, SIGNAL("triggered()"),
                    self._add_project_to_console)
            actionProperties = menu.addAction(QIcon(resources.IMAGES['pref']),
                self.tr("Project Properties"))
            self.connect(actionProperties, SIGNAL("triggered()"),
                self.open_project_properties)
            #get the extra context menu for this projectType
            handler = settings.get_project_type_handler(item.projectType)
#            if handler:
#                for m in handler.get_context_menus():
#                    menu.addSeparator()
#                    menu.addMenu(m)

            menu.addSeparator()
            action_refresh = menu.addAction(
                self.style().standardIcon(QStyle.SP_BrowserReload),
                self.tr("Refresh Project"))
            self.connect(action_refresh, SIGNAL("triggered()"),
                self._refresh_project)
            action_close = menu.addAction(
                self.style().standardIcon(QStyle.SP_DialogCloseButton),
                self.tr("Close Project"))
            self.connect(action_close, SIGNAL("triggered()"),
                self._close_project)

        #menu for all items!
        for m in self.EXTRA_MENUS.get('all', ()):
            menu.addSeparator()
            menu.addMenu(m)

        #menu for the Project Type(if present)
        if handler:
            for m in handler.get_context_menus():
                menu.addSeparator()
                menu.addMenu(m)
        #show the menu!
        menu.exec_(QCursor.pos())

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

    def _open_file(self, item, column):
        if item.childCount() == 0 and not item.isFolder:
            fileName = os.path.join(item.path, unicode(item.text(column)))
            main_container.MainContainer().open_file(fileName)

    def _get_project_root(self):
        item = self.currentItem()
        while item is not None and item.parent() is not None:
            item = item.parent()
        return item

    def set_default_project(self, item):
        item.setForeground(0, QBrush(QColor(0, 204, 82)))
        if self._actualProject:
            self._actualProject.setForeground(0, QBrush(Qt.darkGray))
        self._actualProject = item

    def open_project_properties(self):
        item = self._get_project_root()
        proj = project_properties_widget.ProjectProperties(item, self)
        proj.show()

    def _refresh_project_by_path(self, project_folder):
        item = self._projects[unicode(project_folder)]
        self._refresh_project(item)

    def _refresh_project(self, item=None):
        if item is None:
            item = self.currentItem()
        item.takeChildren()
        parentItem = self._get_project_root()
        if parentItem is None:
            return
        if item.parent() is None:
            path = item.path
        else:
            path = file_manager.create_path(item.path, unicode(item.text(0)))
        if parentItem.extensions != settings.SUPPORTED_EXTENSIONS:
            folderStructure = file_manager.open_project_with_extensions(
                path, parentItem.extensions)
        else:
            folderStructure = file_manager.open_project(path)
        if folderStructure[path][1] is not None:
            folderStructure[path][1].sort()
        else:
            return
        self._load_folder(folderStructure, path, item)
        item.setExpanded(True)

    def _close_project(self):
        item = self.currentItem()
        index = self.indexOfTopLevelItem(item)
        pathKey = item.path
        if self.__enableCloseNotification:
            self.emit(SIGNAL("closeProject(QString)"), pathKey)
        self._fileWatcher.removePath(pathKey)
        self.takeTopLevelItem(index)
        self._projects.pop(pathKey)
        item = self.currentItem()
        if item:
            self.set_default_project(item)

    def _create_init(self):
        item = self.currentItem()
        if item.parent() is None:
            pathFolder = item.path
        else:
            pathFolder = os.path.join(item.path, str(item.text(0)))
        try:
            file_manager.create_init_file_complete(pathFolder)
        except file_manager.NinjaFileExistsException, ex:
            QMessageBox.information(self, self.tr("Create INIT fail"),
                ex.message)
        self._refresh_project(item)

    def _add_new_file(self):
        item = self.currentItem()
        if item.parent() is None:
            pathForFile = item.path
        else:
            pathForFile = os.path.join(item.path, unicode(item.text(0)))
        result = QInputDialog.getText(self, self.tr("New File"),
            self.tr("Enter the File Name:"))
        fileName = unicode(result[0])

        if result[1] and fileName.strip() != '':
            try:
                fileName = os.path.join(pathForFile, fileName)
                fileName = file_manager.store_file_content(
                    fileName, '', newFile=True)
                name = file_manager.get_basename(fileName)
                subitem = ProjectItem(item, name, pathForFile)
                subitem.setToolTip(0, name)
                subitem.setIcon(0, self._get_file_icon(name))
                item.sortChildren(0, Qt.AscendingOrder)
                mainContainer = main_container.MainContainer()
                mainContainer.open_file(fileName)
                editorWidget = mainContainer.get_actual_editor()
                editorWidget.textCursor().insertText("# -*- coding: utf-8 *-*")
                main_container.MainContainer().save_file()
            except file_manager.NinjaFileExistsException, ex:
                QMessageBox.information(self, self.tr("File Already Exists"),
                    self.tr("Invalid Path: the file '%s' already exists." % \
                        ex.filename))

    def add_existing_file(self, path):
        relative = file_manager.convert_to_relative(
            self._actualProject.path, path)
        paths = relative.split(os.sep)[:-1]
        itemParent = self._actualProject
        for p in paths:
            for i in xrange(itemParent.childCount()):
                item = itemParent.child(i)
                if item.text(0) == p:
                    itemParent = item
                    break
        itemParent.setSelected(True)
        name = file_manager.get_basename(path)
        subitem = ProjectItem(itemParent, name, file_manager.get_folder(path))
        subitem.setToolTip(0, name)
        subitem.setIcon(0, self._get_file_icon(name))
        itemParent.sortChildren(0, Qt.AscendingOrder)
        itemParent.setExpanded(True)

    def _add_new_folder(self):
        item = self.currentItem()
        if item.parent() is None:
            pathForFolder = item.path
        else:
            pathForFolder = os.path.join(item.path, unicode(item.text(0)))
        result = QInputDialog.getText(self, self.tr("New Folder"),
            self.tr("Enter the Folder Name:"))
        folderName = unicode(result[0])

        if result[1] and folderName.strip() != '':
            folderName = os.path.join(pathForFolder, folderName)
            file_manager.create_folder(folderName)
            name = file_manager.get_basename(folderName)
            subitem = ProjectItem(item, name, pathForFolder)
            subitem.setToolTip(0, name)
            subitem.setIcon(0, QIcon(resources.IMAGES['tree-folder']))
            item.sortChildren(0, Qt.AscendingOrder)

    def _delete_file(self):
        item = self.currentItem()
        val = QMessageBox.question(self, self.tr("Delete File"),
                self.tr("Do you want to delete the following file: ") \
                + os.path.join(item.path, unicode(item.text(0))),
                QMessageBox.Yes, QMessageBox.No)
        if val == QMessageBox.Yes:
            path = file_manager.create_path(item.path, unicode(item.text(0)))
            file_manager.delete_file(item.path, unicode(item.text(0)))
            self.removeItemWidget(item, 0)
            mainContainer = main_container.MainContainer()
            if mainContainer.is_open(path):
                mainContainer.close_deleted_file(path)

    def _delete_folder(self):
        item = self.currentItem()
        val = QMessageBox.question(self, self.tr("Delete Folder"),
                self.tr("Do you want to delete the following folder: ") \
                + os.path.join(item.path, unicode(item.text(0))),
                QMessageBox.Yes, QMessageBox.No)
        if val == QMessageBox.Yes:
            file_manager.delete_folder(item.path, unicode(item.text(0)))
            self.removeItemWidget(item, 0)

    def _rename_file(self):
        item = self.currentItem()
        if item.parent() is None:
            pathForFile = item.path
        else:
            pathForFile = os.path.join(item.path, unicode(item.text(0)))
        result = QInputDialog.getText(self, self.tr("Rename File"),
            self.tr("Enter New File Name:"))
        fileName = unicode(result[0])

        if result[1] and fileName.strip() != '':
            fileName = os.path.join(
                file_manager.get_folder(unicode(pathForFile)), fileName)
            try:
                fileName = file_manager.rename_file(pathForFile, fileName)
                name = file_manager.get_basename(fileName)
                mainContainer = main_container.MainContainer()
                if mainContainer.is_open(pathForFile):
                    mainContainer.change_open_tab_name(pathForFile, fileName)
                subitem = ProjectItem(item.parent(), name,
                    file_manager.get_folder(unicode(fileName)))
                subitem.setToolTip(0, name)
                subitem.setIcon(0, self._get_file_icon(name))
                index = item.parent().indexOfChild(item)
                subitem.parent().takeChild(index)
                subitem.parent().sortChildren(0, Qt.AscendingOrder)
            except file_manager.NinjaFileExistsException, ex:
                QMessageBox.information(self, self.tr("File Already Exists"),
                    self.tr("Invalid Path: the file '%s' already exists." % \
                        ex.filename))

    def _copy_file(self):
        item = self.currentItem()
        if item.parent() is None:
            pathForFile = item.path
        else:
            pathForFile = os.path.join(item.path, unicode(item.text(0)))
        pathProject = self.get_selected_project_path()
        addToProject = ui_tools.AddToProject(pathProject, self)
        addToProject.setWindowTitle(self.tr("Copy File to"))
        addToProject.exec_()
        if not addToProject.pathSelected:
            return
        name = unicode(QInputDialog.getText(None,
            self.tr("Copy File"),
            self.tr("File Name:"))[0])
        if not name:
            QMessageBox.information(self, self.tr("Indalid Name"),
                self.tr("The file name is empty, please enter a name"))
            return
        path = file_manager.create_path(
            unicode(addToProject.pathSelected), name)
        try:
            content = file_manager.read_file_content(pathForFile)
            path = file_manager.store_file_content(path, content, newFile=True)
            self.add_existing_file(path)
        except file_manager.NinjaFileExistsException, ex:
                QMessageBox.information(self, self.tr("File Already Exists"),
                    self.tr("Invalid Path: the file '%s' already exists." % \
                        ex.filename))

    def _move_file(self):
        item = self.currentItem()
        if item.parent() is None:
            pathForFile = item.path
        else:
            pathForFile = os.path.join(item.path, unicode(item.text(0)))
        pathProject = self.get_selected_project_path()
        addToProject = ui_tools.AddToProject(pathProject, self)
        addToProject.setWindowTitle(self.tr("Copy File to"))
        addToProject.exec_()
        if not addToProject.pathSelected:
            return
        name = file_manager.get_basename(pathForFile)
        path = file_manager.create_path(
            unicode(addToProject.pathSelected), name)
        try:
            content = file_manager.read_file_content(pathForFile)
            path = file_manager.store_file_content(path, content, newFile=True)
            file_manager.delete_file(pathForFile)
            index = item.parent().indexOfChild(item)
            item.parent().takeChild(index)
            self.add_existing_file(path)
        except file_manager.NinjaFileExistsException, ex:
                QMessageBox.information(self, self.tr("File Already Exists"),
                    self.tr("Invalid Path: the file '%s' already exists." % \
                        ex.filename))

    def load_project(self, folderStructure, folder):
        if not folder:
            return

        name = file_manager.get_basename(folder)
        item = ProjectTree(self, name, folder)
        item.isFolder = True
        item.setToolTip(0, name)
        item.setIcon(0, QIcon(resources.IMAGES['tree-app']))
        self._projects[folder] = item
        if folderStructure[folder][1] is not None:
            folderStructure[folder][1].sort()
        if item.extensions != settings.SUPPORTED_EXTENSIONS:
            folderStructure = file_manager.open_project_with_extensions(
                item.path, item.extensions)
        self._load_folder(folderStructure, folder, item)
        item.setExpanded(True)
        if len(self._projects) == 1:
            self.set_default_project(item)
        if self.currentItem() is None:
            item.setSelected(True)
            self.setCurrentItem(item)

        self._fileWatcher.addPath(folder)

    def _load_folder(self, folderStructure, folder, parentItem):
        items = folderStructure[folder]

        if items[0] is not None:
            items[0].sort()
        for i in items[0]:
            subitem = ProjectItem(parentItem, i, folder)
            subitem.setToolTip(0, i)
            subitem.setIcon(0, self._get_file_icon(i))
        if items[1] is not None:
            items[1].sort()
        for _file in items[1]:
            if _file.startswith('.'):
                continue
            subfolder = ProjectItem(parentItem, _file, folder)
            subfolder.isFolder = True
            subfolder.setToolTip(0, _file)
            subfolder.setIcon(0, QIcon(resources.IMAGES['tree-folder']))
            self._load_folder(folderStructure,
                os.path.join(folder, _file), subfolder)

    def _get_file_icon(self, fileName):
        return QIcon(self.images.get(file_manager.get_file_extension(fileName),
            resources.IMAGES['tree-generic']))

    def get_selected_project_path(self):
        if self._actualProject:
            return self._actualProject.path
        return None

    def get_project_main_file(self):
        if self._actualProject:
            return self._actualProject.mainFile
        return ''

    def get_selected_project_type(self):
        rootItem = self._get_project_root()
        return rootItem.projectType

    def get_selected_project_lang(self):
        rootItem = self._get_project_root()
        return rootItem.lang()

    def get_open_projects(self):
        #return [p.path for p in self._projects.values()]
        return self._projects.values()

    def is_open(self, path):
        return len([True for item in self._projects.values() \
            if item.path == path]) != 0

    def _set_current_project(self, path):
        for item in self._projects.values():
            if item.path == path:
                self.set_default_project(item)
                break

    def _close_open_projects(self):
        self.__enableCloseNotification = False
        for i in xrange(self.topLevelItemCount()):
            self.setCurrentItem(self.topLevelItem(0))
            self._close_project()
        self.__enableCloseNotification = True
        self._projects = {}

    def keyPressEvent(self, event):
        item = self.currentItem()
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self._open_file(item, 0)
        elif event.key() == Qt.Key_Space and item.isFolder:
            expand = not item.isExpanded()
            item.setExpanded(expand)
        elif event.key() == Qt.Key_Left and not item.isExpanded():
            parent = item.parent()
            if parent:
                parent.setExpanded(False)
                self.setCurrentItem(parent)
                return
        super(TreeProjectsWidget, self).keyPressEvent(event)


class ProjectItem(QTreeWidgetItem):

    def __init__(self, parent, name, path):
        QTreeWidgetItem.__init__(self, parent)
        self.setText(0, name)
        self.path = path
        self.isFolder = False

    @property
    def isProject(self):
        #flag to check if the item is a project ALWAYS FALSE
        return False

    def lang(self):
        return file_manager.get_file_extension(unicode(self.text(0)))

    def get_full_path(self):
        '''
        Returns the full path of the file
        '''
        return os.path.join(self.path, unicode(self.text(0)))


class ProjectTree(QTreeWidgetItem):

    def __init__(self, parent, _name, path):
        QTreeWidgetItem.__init__(self, parent)
        self._parent = parent
        self.setText(0, _name)
        self.path = path
        self.isFolder = True
        self.setForeground(0, QBrush(Qt.darkGray))
        project = json_manager.read_ninja_project(path)
        self.name = project.get('name', '')
        if self.name != '':
            self.setText(0, self.name)
        self.projectType = project.get('project-type', '')
        self.description = project.get('description', '')
        self.url = project.get('url', '')
        self.license = project.get('license', '')
        self.mainFile = project.get('mainFile', '')
        self.extensions = project.get('supported-extensions',
            settings.SUPPORTED_EXTENSIONS)
        self.pythonPath = project.get('pythonPath', settings.PYTHON_PATH)
        self.programParams = project.get('programParams', '')
        self.venv = project.get('venv', '')
        self.addedToConsole = False

    @property
    def isProject(self):
        #flag to check if the item is a project ALWAYS TRUE
        return True

    def lang(self):
        if self.mainFile != '':
            return file_manager.get_file_extension(self.mainFile)
        return 'py'

    def get_full_path(self):
        '''
        Returns the full path of the project
        '''
        project_file = json_manager.get_ninja_project_file(self.path)
        return os.path.join(self.path, project_file)
