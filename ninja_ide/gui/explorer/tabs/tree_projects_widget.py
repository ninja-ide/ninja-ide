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
from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QScrollArea
from PyQt4.QtGui import QVBoxLayout
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
from PyQt4.QtGui import QSizePolicy
from PyQt4.QtGui import QFontMetrics
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QDateTime

from ninja_ide import translations
from ninja_ide.core import settings
from ninja_ide.core.file_handling import file_manager
from ninja_ide.tools import ui_tools
from ninja_ide.tools import json_manager
from ninja_ide.gui.ide import IDE
from ninja_ide.gui.dialogs import add_to_project
from ninja_ide.gui.dialogs import project_properties_widget
from ninja_ide.gui.dialogs import new_project_manager
from ninja_ide.gui.explorer.explorer_container import ExplorerContainer
from ninja_ide.gui.explorer import actions
from ninja_ide.gui.explorer.nproject import NProject


def scrollable_wrapper(widget):
    scrollable = QScrollArea()
    scrollable.setWidget(widget)
    scrollable.setWidgetResizable(True)
    scrollable.setEnabled(True)
    return scrollable


class TreeHeader(QHeaderView):
    """
    SIGNALS:
    @headerClicked(QPoint, QString)
    """

    def __init__(self):
        super(TreeHeader, self).__init__(Qt.Horizontal)
        self.title = ""
        self.path = ""
        self._is_current_project = False
        self._mouse_over = False
        self.setToolTip(translations.TR_PROJECT_OPTIONS)

    def _get_is_current_project(self):
        return self._is_current_project

    def _set_is_current_project(self, val):
        self._is_current_project = val
        self.repaint()

    is_current_project = property(_get_is_current_project,
                                  _set_is_current_project)

    def paintSection(self, painter, rect, logicalIndex):
        gradient = QLinearGradient(0, 0, 0, rect.height())
        if self._mouse_over:
            gradient.setColorAt(0.0, QColor("#808080"))
            gradient.setColorAt(1.0, QColor("#474747"))
        else:
            gradient.setColorAt(0.0, QColor("#727272"))
            gradient.setColorAt(1.0, QColor("#363636"))
        painter.fillRect(rect, QBrush(gradient))

        if self._is_current_project:
            painter.setPen(QColor(0, 204, 82))
        else:
            painter.setPen(QColor(Qt.white))
        font = painter.font()
        font.setBold(True)
        painter.setFont(font)
        font_metrics = QFontMetrics(painter.font())
        ypos = int(rect.height() / 2.0) + int(font_metrics.height() / 3.0)
        painter.drawText(10, ypos, self.title)

    def enterEvent(self, event):
        super(TreeHeader, self).enterEvent(event)
        self._mouse_over = True

    def leaveEvent(self, event):
        super(TreeHeader, self).leaveEvent(event)
        self._mouse_over = False

    def mousePressEvent(self, event):
        super(TreeHeader, self).mousePressEvent(event)
        self.emit(SIGNAL("headerClicked(QPoint, QString)"),
                  QCursor.pos(), self.path)


class ProjectTreeColumn(QDialog):

    def __init__(self, parent=None):
        super(ProjectTreeColumn, self).__init__(parent,
                                                Qt.WindowStaysOnTopHint)
        self._layout = QVBoxLayout()
        self._layout.setSizeConstraint(QVBoxLayout.SetDefaultConstraint)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self.setLayout(self._layout)
        self._vbox = QVBoxLayout()
        self._vbox.setContentsMargins(0, 0, 0, 0)
        self._vbox.setSpacing(0)
        self._vbox.setSizeConstraint(QVBoxLayout.SetDefaultConstraint)
        self._buttons = []

        self._projects_area = QWidget()
        logger.debug("This is the projects area")
        logger.debug(self._projects_area)
        self._projects_area.setLayout(self._vbox)

        self._scroll_area = QScrollArea()
        self.layout().addWidget(self._scroll_area)
        self._scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setEnabled(True)
        self._scroll_area.setWidget(self._projects_area)
        self._scroll_area.setGeometry(self.geometry())
        self._vbox.setGeometry(self.geometry())
        self.projects = []
        self._active_project = None

        connections = (
            {'target': 'main_container',
             'signal_name': 'addToProject(QString)',
             'slot': self._add_file_to_project},
            {'target': 'main_container',
             'signal_name': 'showFileInExplorer(QString)',
             'slot': self._show_file_in_explorer},
        )
        IDE.register_service('projects_explorer', self)
        IDE.register_signals('projects_explorer', connections)
        ExplorerContainer.register_tab(translations.TR_TAB_PROJECTS, self)

        #FIXME: Should have a ninja settings object that stores tree state
        #FIXME: Or bettter, application data object
        #TODO: check this:
        #self.connect(ide, SIGNAL("goingDown()"),
            #self.tree_projects.shutdown)

        #def close_project_signal():
            #self.emit(SIGNAL("updateLocator()"))

    def install_tab(self):
        ide = IDE.get_service('ide')
        ui_tools.install_shortcuts(self, actions.PROJECTS_TREE_ACTIONS, ide)

        self.connect(ide, SIGNAL("goingDown()"), self.close)

    def load_session_projects(self, projects):
        for project in projects:
            self._open_project_folder(project)

    def open_project_folder(self, folderName=None):
        if settings.WORKSPACE:
            directory = settings.WORKSPACE
        else:
            directory = os.path.expanduser("~")

        if folderName is None:
            folderName = QFileDialog.getExistingDirectory(
                self, translations.TR_OPEN_PROJECT_DIRECTORY, directory)
            logger.debug("Choosing Foldername")
        if folderName:
            logger.debug("Opening %s" % folderName)
            self._open_project_folder(folderName)

    def _open_project_folder(self, folderName):
        ninjaide = IDE.get_service("ide")
        project = NProject(folderName)
        qfsm = ninjaide.filesystem.open_project(project)
        if qfsm:
            self.add_project(project)
            self.emit(SIGNAL("updateLocator()"))
            self.save_recent_projects(folderName)
            main_container = IDE.get_service('main_container')
            if main_container:
                main_container.show_editor_area()

    def _add_file_to_project(self, path):
        """Add the file for 'path' in the project the user choose here."""
        if self._active_project:
            pathProject = [self._active_project.project]
            addToProject = add_to_project.AddToProject(pathProject, self)
            addToProject.exec_()
            if not addToProject.pathSelected:
                return
            main_container = IDE.get_service('main_container')
            if not main_container:
                return
            editorWidget = main_container.get_current_editor()
            if not editorWidget.file_path:
                name = QInputDialog.getText(None,
                                            translations.TR_ADD_FILE_TO_PROJECT,
                                            translations.TR_FILENAME + ": ")[0]
                if not name:
                    QMessageBox.information(
                        self,
                        translations.TR_INVALID_FILENAME,
                        translations.TR_INVALID_FILENAME_ENTER_A_FILENAME)
                    return
            else:
                name = file_manager.get_basename(editorWidget.file_path)
            new_path = file_manager.create_path(addToProject.pathSelected, name)
            ide_srv = IDE.get_service("ide")
            old_file = ide_srv.get_or_create_nfile(path)
            new_file = old_file.save(editorWidget.get_text(), new_path)
            #FIXME: Make this file replace the original in the open tab
        else:
            pass
            # Message about no project

    def _show_file_in_explorer(self, path):
        '''Iterate through the list of available projects and show
        the current file in the explorer view for the first
        project that contains it (i.e. if the same file is
        included in multiple open projects, the path will be
        expanded for the first project only).
        Note: This slot is connected to the main container's
        "showFileInExplorer(QString)" signal.'''
        for project in self.projects:
            index = project.model().index(path)
            if index.isValid():
                # Show the explorer if it is currently hidden
                central = IDE.get_service('central_container')
                if central and not central.is_lateral_panel_visible():
                    central.change_lateral_visibility()
                # This highlights the index in the tree for us
                project.setCurrentIndex(index)
                # Loop through the parents to expand the tree
                # all the way up to the selected index.
                while index.isValid():
                    project.expand(index)
                    index = index.parent()
                break

    @property
    def children(self):
        return self._projects_area.layout().count()

    def add_project(self, project):
        if project not in self.projects:
            ptree = TreeProjectsWidget(project)
            ptree.setParent(self)
            self.connect(ptree, SIGNAL("setActiveProject(PyQt_PyObject)"),
                         self._set_active_project)
            self.connect(ptree, SIGNAL("closeProject(PyQt_PyObject)"),
                         self._close_project)
            pmodel = project.model
            ptree.setModel(pmodel)
            ptree.header().title = project.name
            ptree.header().path = project.path
            pindex = pmodel.index(pmodel.rootPath())
            ptree.setRootIndex(pindex)
            #self._widget.layout().addWidget(scrollable_wrapper(ptree))
            self._projects_area.layout().addWidget(ptree)
            if self._active_project is None:
                ptree.set_default_project()
            self.projects.append(ptree)
            ptree.setGeometry(self.geometry())

    def _close_project(self, widget):
        """Close the project related to the tree widget."""
        self.projects.remove(widget)
        if self._active_project == widget and len(self.projects) > 0:
            self.projects[0].set_default_project()
        self._layout.removeWidget(widget)
        ninjaide = IDE.get_service('ide')
        ninjaide.filesystem.close_project(widget.project.path)
        widget.deleteLater()

    def _set_active_project(self, tree_proj):
        if self._active_project is not None:
            self._active_project.set_default_project(False)
        self._active_project = tree_proj

    def close_opened_projects(self):
        for project in reversed(self.projects):
            self._close_project(project)

    def save_project(self):
        """Save all the opened files that belongs to the actual project."""
        if self._active_project:
            path = self._active_project.project.path
            main_container = IDE.get_service('main_container')
            if path and main_container:
                main_container.save_project(path)

    def create_new_project(self):
        wizard = new_project_manager.NewProjectManager(self)
        wizard.show()

    @property
    def current_project(self):
        if self._active_project:
            return self._active_project.project

    @property
    def current_tree(self):
        return self._active_project

    def save_recent_projects(self, folder):
        settings = IDE.data_settings()
        recent_project_list = settings.value('recentProjects', {})
        #if already exist on the list update the date time
        projectProperties = json_manager.read_ninja_project(folder)
        name = projectProperties.get('name', '')
        description = projectProperties.get('description', '')

        if name == '':
            name = file_manager.get_basename(folder)

        if description == '':
            description = translations.TR_NO_DESCRIPTION

        if folder in recent_project_list:
            properties = recent_project_list[folder]
            properties["lastopen"] = QDateTime.currentDateTime()
            properties["name"] = name
            properties["description"] = description
            recent_project_list[folder] = properties
        else:
            recent_project_list[folder] = {
                "name": name,
                "description": description,
                "isFavorite": False, "lastopen": QDateTime.currentDateTime()}
            #if the length of the project list it's high that 10 then delete
            #the most old
            #TODO: add the length of available projects to setting
            if len(recent_project_list) > 10:
                del recent_project_list[self.find_most_old_open(
                    recent_project_list)]
        settings.setValue('recentProjects', recent_project_list)

    def find_most_old_open(self, recent_project_list):
        listFounder = []
        for recent_project_path, content in list(recent_project_list.items()):
            listFounder.append((recent_project_path, int(
                content["lastopen"].toString("yyyyMMddHHmmzzz"))))
        listFounder = sorted(listFounder, key=lambda date: listFounder[1],
                             reverse=True)   # sort by date last used
        return listFounder[0][0]

    def reject(self):
        if self.parent() is None:
            self.emit(SIGNAL("dockWidget(PyQt_PyObject)"), self)

    def closeEvent(self, event):
        self.emit(SIGNAL("dockWidget(PyQt_PyObject)"), self)
        event.ignore()


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
    #TODO: We need to implement a new mechanism for scope aware menus

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
        self.connect(t_header, SIGNAL("headerClicked(QPoint, QString)"),
                     lambda point, path: self._menu_context_tree(
                         point, True, path))
        self.setHeader(t_header)
        t_header.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        t_header.setResizeMode(0, QHeaderView.Stretch)
        t_header.setStretchLastSection(False)
        t_header.setClickable(True)

        self.hideColumn(1)  # Size
        self.hideColumn(2)  # Type
        self.hideColumn(3)  # Modification date
        self.setUniformRowHeights(True)

        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.auto_resize_grow(self.verticalScrollBar().minimum(),
                              self.verticalScrollBar().maximum())

        #TODO: We need to expand the widget to be as big as the real area
        #that contains all the visible tree items, the code below
        #tries to detect when that area grows to adjust the size of the
        #widget, but i'm not sure this is the proper approach
        self.connect(self.verticalScrollBar(),
                     SIGNAL("rangeChanged(int, int)"), self.auto_resize_grow)

    def setParent(self, parent):
        self.__parent = parent

    def auto_resize_grow(self, minimum, maximum):
        logger.debug("This is the maximum")
        logger.debug(maximum)

        if maximum:
            height = self.height()
            #I am very reluctant to do this with a for an linear search
            #even for an alpha, so lets just try guessing
            #FIXME: We need to know the value in pixels of qslider's single
            #value to know how to add it to height
            #FIXME: I dont know how to know when or how much to srink this.
            new_height = height + (maximum * 8)
            self.setFixedHeight(new_height)

    def auto_resize_shrink(self):
        count = 0
        if self.__parent:
            count = self.__parent.children
        if count != 1:
            self.setFixedHeight(1)
        #self.auto_resize_grow(self.verticalScrollBar().minimum(),
                #self.verticalScrollBar().maximum())

    def setModel(self, model):
        super(TreeProjectsWidget, self).setModel(model)
        self.__format_tree()
        #Activated is said to do the right thing on every system
        self.connect(self, SIGNAL("activated(const QModelIndex &)"),
                     self._open_file)

    def __init__(self, project, state_index=list()):
        super(TreeProjectsWidget, self).__init__()
        self.project = project
        self._added_to_console = False
        self.__format_tree()
        self.__parent = None
        self.setMinimumHeight(self.height())

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.connect(self, SIGNAL(
            "customContextMenuRequested(const QPoint &)"),
            self._menu_context_tree)

        self.connect(project, SIGNAL("projectNameUpdated(QString)"),
                     self._update_header_title)
        self.expanded.connect(self._item_expanded)
        self.collapsed.connect(self._item_collapsed)
        #FIXME: Should I store this somehow for each project path?
        #Perhaps store after each change
        self.state_index = list()
        self._folding_menu = FoldingContextMenu(self)

    def _update_header_title(self, title):
        self.header().title = title

    #FIXME: Check using the amount of items under this tree
    #add it to the items of pindex item children
    def _item_collapsed(self, tree_item):
        """Store status of item when collapsed"""
        path = self.model().filePath(tree_item)
        if path in self.state_index:
            path_index = self.state_index.index(path)
            self.state_index.pop(path_index)
        self.auto_resize_shrink()

    def _item_expanded(self, tree_item):
        """Store status of item when expanded"""
        path = self.model().filePath(tree_item)
        if path not in self.state_index:
            self.state_index.append(path)

    def _menu_context_tree(self, point, isRoot=False, root_path=None):
        index = self.indexAt(point)
        if not index.isValid() and not isRoot:
            return

        handler = None
        menu = QMenu(self)
        if isRoot or self.model().isDir(index):
            self._add_context_menu_for_folders(menu, isRoot, root_path)
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
            ":img/play"), translations.TR_RUN_PROJECT)
        self.connect(actionRunProject, SIGNAL("triggered()"),
                     self._execute_project)
        actionMainProject = menu.addAction(translations.TR_SET_AS_MAIN_PROJECT)
        self.connect(actionMainProject, SIGNAL("triggered()"),
                     self.set_default_project)
        if self._added_to_console:
            actionRemoveFromConsole = menu.addAction(
                translations.TR_REMOVE_PROJECT_FROM_PYTHON_CONSOLE)
            self.connect(actionRemoveFromConsole, SIGNAL("triggered()"),
                         self._remove_project_from_console)
        else:
            actionAdd2Console = menu.addAction(
                translations.TR_ADD_PROJECT_TO_PYTHON_CONSOLE)
            self.connect(actionAdd2Console, SIGNAL("triggered()"),
                         self._add_project_to_console)
        actionShowFileSizeInfo = menu.addAction(translations.TR_SHOW_FILESIZE)
        self.connect(actionShowFileSizeInfo, SIGNAL("triggered()"),
                     self.show_filesize_info)
        actionProperties = menu.addAction(QIcon(":img/pref"),
                                          translations.TR_PROJECT_PROPERTIES)
        self.connect(actionProperties, SIGNAL("triggered()"),
                     self.open_project_properties)

        menu.addSeparator()
        action_close = menu.addAction(
            self.style().standardIcon(QStyle.SP_DialogCloseButton),
            translations.TR_CLOSE_PROJECT)
        self.connect(action_close, SIGNAL("triggered()"),
                     self._close_project)
        #menu for the project
        for m in self.extra_menus_by_scope['project']:
            if isinstance(m, QMenu):
                menu.addSeparator()
                menu.addMenu(m)

    def _add_context_menu_for_folders(self, menu, isRoot=False, path=None):
        #Create Actions
        action_add_file = menu.addAction(QIcon(":img/new"),
                                         translations.TR_ADD_NEW_FILE)
        action_add_folder = menu.addAction(QIcon(
            ":img/openProj"), translations.TR_ADD_NEW_FOLDER)
        action_create_init = menu.addAction(translations.TR_CREATE_INIT)
        action_remove_folder = menu.addAction(translations.TR_REMOVE_FOLDER)

        #Connect actions
        if isRoot:
            self.connect(action_add_file, SIGNAL("triggered()"),
                         lambda: self._add_new_file(path))
            self.connect(action_add_folder, SIGNAL("triggered()"),
                         lambda: self._add_new_folder(path))
            self.connect(action_create_init, SIGNAL("triggered()"),
                         lambda: self._create_init(path))
        else:
            self.connect(action_add_file, SIGNAL("triggered()"),
                         self._add_new_file)
            self.connect(action_add_folder, SIGNAL("triggered()"),
                         self._add_new_folder)
            self.connect(action_create_init, SIGNAL("triggered()"),
                         self._create_init)
            self.connect(action_remove_folder, SIGNAL("triggered()"),
                         self._delete_folder)

    def _add_context_menu_for_files(self, menu, lang):
        #Create actions
        action_rename_file = menu.addAction(translations.TR_RENAME_FILE)
        action_move_file = menu.addAction(translations.TR_MOVE_FILE)
        action_copy_file = menu.addAction(translations.TR_COPY_FILE)
        action_remove_file = menu.addAction(
            self.style().standardIcon(QStyle.SP_DialogCloseButton),
            translations.TR_DELETE_FILE)

        #Connect actions
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
            action_edit_ui_file = menu.addAction(translations.TR_EDIT_UI_FILE)
            self.connect(action_edit_ui_file, SIGNAL("triggered()"),
                         self._edit_ui_file)

        #menu for files
        for m in self.extra_menus_by_scope['file']:
            if isinstance(m, QMenu):
                menu.addSeparator()
                menu.addMenu(m)

    def _add_project_to_console(self):
        tools_dock = IDE.get_service('tools_dock')
        if tools_dock:
            tools_dock.add_project_to_console(self.project.path)
            self._added_to_console = True

    def _remove_project_from_console(self):
        tools_dock = IDE.get_service('tools_dock')
        if tools_dock:
            tools_dock.remove_project_from_console(self.project.path)
            self._added_to_console = False

    def _open_file(self, model_index):
        if self.model().isDir(model_index):
            return
        path = self.model().filePath(model_index)
        main_container = IDE.get_service('main_container')
        logger.debug("tried to get main container")
        if main_container:
            logger.debug("will call open file")
            main_container.open_file(path)

    def set_default_project(self, value=True):
        self.header().is_current_project = value
        if value:
            self.emit(SIGNAL("setActiveProject(PyQt_PyObject)"), self)

    def open_project_properties(self):
        proj = project_properties_widget.ProjectProperties(self.project, self)
        proj.show()

    def _close_project(self):
        self.emit(SIGNAL("closeProject(PyQt_PyObject)"), self)

    def _create_init(self):
        path = self.model().filePath(self.currentIndex())
        try:
            file_manager.create_init_file_complete(path)
        except file_manager.NinjaFileExistsException as ex:
            QMessageBox.information(self, translations.TR_CREATE_INIT_FAIL,
                                    ex.message)

    def _add_new_file(self, path=''):
        if not path:
            path = self.model().filePath(self.currentIndex())
        result = QInputDialog.getText(self, translations.TR_NEW_FILE,
                                      translations.TR_ENTER_NEW_FILENAME + ": ")
        fileName = result[0]

        if result[1] and fileName.strip() != '':
            fileName = os.path.join(path, fileName)
            ide_srv = IDE.get_service('ide')
            current_nfile = ide_srv.get_or_create_nfile(fileName)
            current_nfile.create()
            main_container = IDE.get_service('main_container')
            if main_container:
                main_container.open_file(fileName)

    def _add_new_folder(self, path=''):
        #FIXME: We need nfilesystem support for this
        if not path:
            path = self.model().filePath(self.currentIndex())
        result = QInputDialog.getText(self, translations.TR_ADD_NEW_FOLDER,
                                      translations.TR_ENTER_NEW_FOLDER_NAME +
                                      ": ")
        folderName = result[0]

        if result[1] and folderName.strip() != '':
            folderName = os.path.join(path, folderName)
            file_manager.create_folder(folderName)

    def _delete_file(self, path=''):
        if not path:
            path = self.model().filePath(self.currentIndex())
        val = QMessageBox.question(self, translations.TR_DELETE_FILE,
                                   translations.TR_DELETE_FOLLOWING_FILE + path,
                                   QMessageBox.Yes, QMessageBox.No)
        if val == QMessageBox.Yes:
            path = file_manager.create_path(path)
            main_container = ide_srv = IDE.get_service('main_container')
            if main_container and main_container.is_open(path):
                main_container.close_deleted_file(path)
            #FIXME: Manage the deletion signal instead of main container
            #fiddling here
            ide_srv = IDE.get_service('ide')
            current_nfile = ide_srv.get_or_create_nfile(path)
            current_nfile.delete()

    def _delete_folder(self):
        #FIXME: We need nfilesystem support for this
        path = self.model().filePath(self.currentIndex())
        val = QMessageBox.question(self, translations.TR_REMOVE_FOLDER,
                                   translations.TR_DELETE_FOLLOWING_FOLDER +
                                   path, QMessageBox.Yes, QMessageBox.No)
        if val == QMessageBox.Yes:
            file_manager.delete_folder(path)

    def _rename_file(self):
        path = self.model().filePath(self.currentIndex())
        name = file_manager.get_basename(path)
        result = QInputDialog.getText(self, translations.TR_RENAME_FILE,
                                      translations.TR_ENTER_NEW_FILENAME,
                                      text=name)
        fileName = result[0]

        if result[1] and fileName.strip() != '':
            fileName = os.path.join(
                file_manager.get_folder(path), fileName)
            if path == fileName:
                return
            ide_srv = IDE.get_service("ide")
            current_nfile = ide_srv.get_or_create_nfile(path)
            #FIXME: Catch willOverWrite and willMove signals
            current_nfile.move(fileName)

    def _copy_file(self):
        path = self.model().filePath(self.currentIndex())
        name = file_manager.get_basename(path)
        global projectsColumn
        pathProjects = [p.project for p in projectsColumn.projects]
        addToProject = add_to_project.AddToProject(pathProjects, self)
        addToProject.setWindowTitle(translations.TR_COPY_FILE_TO)
        addToProject.exec_()
        if not addToProject.pathSelected:
            return
        name = QInputDialog.getText(self, translations.TR_COPY_FILE,
                                    translations.TR_FILENAME, text=name)[0]
        if not name:
            QMessageBox.information(
                self, translations.TR_INVALID_FILENAME,
                translations.TR_INVALID_FILENAME_ENTER_A_FILENAME)
            return
        new_path = file_manager.create_path(addToProject.pathSelected, name)
        ide_srv = IDE.get_service("ide")
        current_nfile = ide_srv.get_or_create_nfile(path)
        #FIXME: Catch willOverWrite and willCopyTo signals
        current_nfile.copy(new_path)

    def _move_file(self):
        path = self.model().filePath(self.currentIndex())
        global projectsColumn
        pathProjects = [p.project for p in projectsColumn.projects]
        addToProject = add_to_project.AddToProject(pathProjects, self)
        addToProject.setWindowTitle(translations.TR_COPY_FILE_TO)
        addToProject.exec_()
        if not addToProject.pathSelected:
            return
        name = file_manager.get_basename(path)
        new_path = file_manager.create_path(addToProject.pathSelected, name)
        ide_srv = IDE.get_service("ide")
        current_nfile = ide_srv.get_or_create_nfile(path)
        #FIXME: Catch willOverWrite and willMove signals
        current_nfile.move(new_path)

    def show_filesize_info(self):
        """Show or Hide the filesize information on TreeProjectWidget"""
        self.showColumn(1) if self.isColumnHidden(1) else self.hideColumn(1)

    #def _edit_ui_file(self):
        #path = self.model().filePath(self.currentIndex())
        #pathForFile = "file://%s" % path
        ##open the correct program to edit Qt UI files!
        #QDesktopServices.openUrl(QUrl(pathForFile, QUrl.TolerantMode))

    def _execute_project(self):
        tools_dock = IDE.get_service('tools_dock')
        if tools_dock:
            tools_dock.execute_project(self.project.path)


class FoldingContextMenu(QMenu):
    """
    This class represents a menu for Folding/Unfolding task
    """

    def __init__(self, tree):
        super(FoldingContextMenu, self).__init__()
        self._tree = tree
        self._collapsed = True

        self.setTitle(translations.TR_FOLD + " / " + translations.TR_UNFOLD)

        fold_project = self.addAction(translations.TR_FOLD_PROJECT)
        unfold_project = self.addAction(translations.TR_UNFOLD_PROJECT)

        self.connect(fold_project, SIGNAL("triggered()"),
                     lambda: self._fold_unfold_project(False))
        self.connect(unfold_project, SIGNAL("triggered()"),
                     lambda: self._fold_unfold_project(True))

    def _fold_unfold_project(self, expand):
        """
        Fold the current project
        """
        if self._collapsed:
            self._tree.expandAll()
        else:
            self._tree.collapseAll()

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


if settings.SHOW_PROJECT_EXPLORER:
    projectsColumn = ProjectTreeColumn()
else:
    projectsColumn = None
