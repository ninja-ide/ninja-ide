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
import collections

from PyQt4.QtGui import QSplitter
from PyQt4.QtGui import QTabWidget
from PyQt4.QtGui import QFileDialog
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QInputDialog
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QSettings
from PyQt4.QtCore import QDateTime

from ninja_ide import resources
from ninja_ide.core import settings
from ninja_ide.core.file_handling import file_manager
from ninja_ide.gui.ide import IDE
from ninja_ide.gui.explorer import actions
from ninja_ide.gui.explorer import nproject
from ninja_ide.gui.dialogs import wizard_new_project
from ninja_ide.tools import ui_tools

from ninja_ide.tools.logger import NinjaLogger

logger = NinjaLogger('ninja_ide.gui.explorer.explorer_container')


class ExplorerContainer(QSplitter):

###############################################################################
# ExplorerContainer SIGNALS
###############################################################################

    """
    updateLocator()
    goToDefinition(int)
    projectOpened(QString)
    projectClosed(QString)
    """

###############################################################################

    __TABS = []
    __created = False

    def __init__(self, parent=None):
        super(ExplorerContainer, self).__init__(parent)
        self.create_tab_widget()

        IDE.register_service('explorer_container', self)

        connections = (
            {'target': 'central_container',
            'signal_name': "splitterBaseRotated()",
            'slot': self.rotate_tab_position},
            #{'target': 'main_container',
            #'signal_name': "updateFileMetadata()",
            #'slot': self.update_explorer},
            #{'target': 'main_container',
            #'signal_name': "updateLocator(QString)",
            #'slot': self.update_explorer},
            #{'target': 'main_container',
            #'signal_name': "currentEditorChanged(QString)",
            #'slot': self.update_explorer},

            #{'target': 'main_container',
            #'signal_name': 'currentEditorChanged(QString)',
            #'slot': self.update_migration},
            #{'target': 'main_container',
            #'signal_name': 'updateFileMetadata(QString)',
            #'slot': self.update_migration},
            #{'target': 'main_container',
            #'signal_name': 'migrationAnalyzed()',
            #'slot': self.update_migration},
            {'target': 'central_container',
            'signal_name': 'splitterBaseRotated()',
            'slot': self.rotate_tab_position},
        )

        IDE.register_signals('explorer_container', connections)
        self.__created = True

    @classmethod
    def register_tab(cls, tab_name, obj, icon=None):
        """Register a tab providing the service name and the instance."""
        cls.__TABS.append((tab_name, obj, icon))
        if cls.__created:
            explorer.add_tab(tab_name, obj, icon)

    def install(self):
        ide = IDE.get_service('ide')
        ide.place_me_on("explorer_container", self, "lateral")

        for tabname, obj, icon in self.__TABS:
            self.add_tab(tabname, obj, icon)

        if self.count() == 0:
            self.hide()
        ui_tools.install_shortcuts(self, actions.ACTIONS, ide)

    def create_tab_widget(self):
        tab_widget = QTabWidget()
        tab_widget.setTabPosition(QTabWidget.East)
        tab_widget.setMovable(True)
        self.addWidget(tab_widget)

    def add_tab(self, tabname, obj, icon=None):
        if icon is not None:
            self.widget(0).addTab(obj, QIcon(icon), tabname)
        else:
            self.widget(0).addTab(obj, tabname)
        func = getattr(obj, 'install_tab', None)
        if isinstance(func, collections.Callable):
            func()

    def change_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()

    def save_project(self):
        """Save all the opened files that belongs to the actual project."""
        path = self.get_actual_project()
        main_container = IDE.get_service('main_container')
        if path and main_container:
            main_container.save_project(path)

    #def update_errors(self, errors, pep8):
        #if self._listErrors:
            #self._listErrors.refresh_lists(errors, pep8)

    #def update_migration(self, migration):
        #if self._listMigration:
            #self._listMigration.refresh_lists(migration)

    #def add_tab_projects(self):
        #if not self.tree_projects:
            #self.tree_projects = tree_projects_widget.ProjectTreeColumn()
            #self.addTab(self.tree_projects, self.tr('Projects'))
            #self.connect(self.tree_projects, SIGNAL("runProject()"),
                #self._execute_project)

            #ide = IDE.get_service('ide')
            #self.connect(ide, SIGNAL("goingDown()"),
                #self.tree_projects.shutdown)
            #self.connect(self.tree_projects,
                #SIGNAL("addProjectToConsole(QString)"),
                #self._add_project_to_console)
            #self.connect(self.tree_projects,
                #SIGNAL("removeProjectFromConsole(QString)"),
                #self._remove_project_from_console)

            #def close_project_signal():
                #self.emit(SIGNAL("updateLocator()"))

            #def close_files_related_to_closed_project(project):
                #if project:
                    #self.emit(SIGNAL("projectClosed(QString)"), project)
            #self.connect(self.tree_projects, SIGNAL("closeProject(QString)"),
                #close_project_signal)
            #self.connect(self.tree_projects, SIGNAL("refreshProject()"),
                #close_project_signal)
            #self.connect(self.tree_projects,
                #SIGNAL("closeFilesFromProjectClosed(QString)"),
                #close_files_related_to_closed_project)

    def _execute_project(self):
        tools_dock = IDE.get_service('tools_dock')
        if tools_dock:
            tools_dock.execute_project()

    def add_tab_symbols(self):
        if not self._treeSymbols:
            self._treeSymbols = tree_symbols_widget.TreeSymbolsWidget()
            self.addTab(self._treeSymbols, self.tr('Symbols'))

            def _go_to_definition(lineno):
                self.emit(SIGNAL("goToDefinition(int)"), lineno)
            self.connect(self._treeSymbols, SIGNAL("goToDefinition(int)"),
                _go_to_definition)

    def add_tab_inspector(self):
        if not settings.WEBINSPECTOR_SUPPORTED:
            QMessageBox.information(self,
                self.tr("Web Inspector not Supported"),
                self.tr("Your Qt version doesn't support the Web Inspector"))
        if not self._inspector:
            self._inspector = WebInspector(self)
            self.addTab(self._inspector, self.tr("Web Inspector"))
            self.connect(self._inspector.btnDock, SIGNAL("clicked()"),
                self._dock_inspector)

    def add_tab_errors(self):
        if not self._listErrors:
            self._listErrors = errors_lists.ErrorsWidget()
            self.addTab(self._listErrors, self.tr("Errors"))
            self.connect(self._listErrors, SIGNAL("pep8Activated(bool)"),
                lambda b: self.emit(SIGNAL("pep8Activated(bool)"), b))
            self.connect(self._listErrors, SIGNAL("lintActivated(bool)"),
                lambda b: self.emit(SIGNAL("lintActivated(bool)"), b))

    def remove_tab_migration(self):
        if self._listMigration:
            self.removeTab(self.indexOf(self._listMigration))
            self._listMigration = None

    def remove_tab_errors(self):
        if self._listErrors:
            self.removeTab(self.indexOf(self._listErrors))
            self._listErrors = None

    def remove_tab_projects(self):
        if self.tree_projects:
            self.removeTab(self.indexOf(self.tree_projects))
            self.tree_projects = None

    def remove_tab_symbols(self):
        if self._treeSymbols:
            self.removeTab(self.indexOf(self._treeSymbols))
            self._treeSymbols = None

    def remove_tab_inspector(self):
        if self._inspector:
            self.removeTab(self.indexOf(self._inspector))
            self._inspector = None

    def _dock_inspector(self):
        if self._inspector.parent():
            self._inspector.btnDock.setText(self.tr("Dock"))
            self._inspector.setParent(None)
            self._inspector.resize(500, 500)
            self._inspector.show()
        else:
            self.addTab(self._inspector, self.tr("Web Inspector"))
            self._inspector.btnDock.setText(self.tr("Undock"))

    def rotate_tab_position(self):
        if self.tabPosition() == QTabWidget.East:
            self.setTabPosition(QTabWidget.West)
        else:
            self.setTabPosition(QTabWidget.East)

    def show_project_tree(self):
        if self.tree_projects:
            self.setCurrentWidget(self.tree_projects)

    def show_symbols_tree(self):
        if self._treeSymbols:
            self.setCurrentWidget(self._treeSymbols)

    def show_web_inspector(self):
        if self._inspector:
            self.setCurrentWidget(self._inspector)

    def refresh_inspector(self):
        if self._inspector:
            self._inspector._webInspector.hide()
            self._inspector._webInspector.show()

    def set_inspection_page(self, page):
        if self._inspector:
            self._inspector._webInspector.setPage(page)
            self._inspector._webInspector.setVisible(True)

    def open_project_folder(self, folderName='', notIDEStart=True):
        """Open a Project and load the symbols in the Code Locator."""
        #if not self.tree_projects and notIDEStart:
            #QMessageBox.information(self, self.tr("Projects Disabled"),
                #self.tr("Project support has been disabled from Preferences"))
            #return
        if not folderName:
            if settings.WORKSPACE:
                directory = settings.WORKSPACE
            else:
                directory = os.path.expanduser("~")
                #current_project = self.get_actual_project()
                #main_container = IDE.get_service('main_container')
                #if main_container:
                    #editorWidget = main_container.get_actual_editor()
                    #if current_project is not None:
                        #directory = current_project
                    #elif editorWidget is not None and editorWidget.ID:
                        #directory = file_manager.get_folder(editorWidget.ID)
            folderName = QFileDialog.getExistingDirectory(self,
                self.tr("Open Project Directory"), directory)
        try:
            if not folderName:
                return
            #FIXME: Here we open project with fs
            if not self.tree_projects.is_open(folderName):
                self.tree_projects.mute_signals = True
                self.tree_projects.loading_project(folderName)
                thread = ui_tools.ThreadProjectExplore()
                self._thread_execution[folderName] = thread
                self.connect(thread,
                    SIGNAL("folderDataAcquired(PyQt_PyObject)"),
                    self._callback_open_project)
                self.connect(thread,
                    SIGNAL("finished()"),
                    self._unmute_tree_signals_clean_threads)
                thread.open_folder(folderName)
            else:
                self.tree_projects._set_current_project(folderName)
        except Exception as reason:
            logger.error('open_project_folder: %s', reason)
            if not notIDEStart:
                QMessageBox.information(self, self.tr("Incorrect Project"),
                    self.tr("The project could not be loaded!"))

    def _unmute_tree_signals_clean_threads(self):
        paths_to_delete = []
        for path in self._thread_execution:
            thread = self._thread_execution.get(path, None)
            if thread and not thread.isRunning():
                paths_to_delete.append(path)
        for path in paths_to_delete:
            thread = self._thread_execution.pop(path, None)
            if thread:
                thread.wait()
        if len(self._thread_execution) == 0:
            self.tree_projects.mute_signals = False

    def _callback_open_project(self, value):
        path, structure = value
        if structure is None:
            self.tree_projects.remove_loading_icon(path)
            return

        self.tree_projects.load_project(structure, path)
        self.save_recent_projects(path)
        self.emit(SIGNAL("projectOpened(QString)"), path)
        self.emit(SIGNAL("updateLocator()"))

    def create_new_project(self):
        if not self.tree_projects:
            QMessageBox.information(self, self.tr("Projects Disabled"),
                self.tr("Project support has been disabled from Preferences"))
            return
        wizard = wizard_new_project.WizardNewProject(self)
        wizard.show()

    def add_existing_file(self, path):
        if self.tree_projects:
            self.tree_projects.add_existing_file(path)

    def get_project_given_filename(self, filename):
        projects = self.get_opened_projects()
        for project in projects:
            if filename.startswith(project.path):
                return project
        return None

    def get_opened_projects(self):
        if self.tree_projects:
            return self.tree_projects.get_open_projects()
        return []

    def open_session_projects(self, projects, notIDEStart=True):
        if not self.tree_projects:
            return
        for project in projects:
            if file_manager.folder_exists(project):
                self.open_project_folder(project, notIDEStart)

    def open_project_properties(self):
        if self.tree_projects:
            self.tree_projects.open_project_properties()

    def close_opened_projects(self):
        if self.tree_projects:
            self.tree_projects._close_open_projects()

    def save_recent_projects(self, folder):
        recent_project_list = QSettings(
            resources.SETTINGS_PATH, QSettings.IniFormat).value(
                'recentProjects', {})

        project = nproject.NProject(folder)
        #if already exist on the list update the date time
        if folder in recent_project_list:
            properties = recent_project_list[folder]
            properties["lastopen"] = QDateTime.currentDateTime()
            properties["name"] = project.name
            properties["description"] = project.description
            recent_project_list[folder] = properties
        else:
            recent_project_list[folder] = {
                "name": project.name,
                "description": project.description,
                "isFavorite": False, "lastopen": QDateTime.currentDateTime()}
            #if the length of the project list it's high that 10 then delete
            #the most old
            #TODO: add the length of available projects to setting
            if len(recent_project_list) > 10:
                del recent_project_list[self.find_most_old_open()]
        QSettings(resources.SETTINGS_PATH, QSettings.IniFormat).setValue(
            'recentProjects', recent_project_list)

    def find_most_old_open(self):
        recent_project_list = QSettings(
            resources.SETTINGS_PATH, QSettings.IniFormat).value(
                'recentProjects', {})
        listFounder = []
        for recent_project_path, content in list(recent_project_list.items()):
            listFounder.append((recent_project_path, int(
                content["lastopen"].toString("yyyyMMddHHmmzzz"))))
        listFounder = sorted(listFounder, key=lambda date: listFounder[1],
            reverse=True)   # sort by date last used
        return listFounder[0][0]

    def get_project_name(self, path):
        if self.tree_projects:
            item = self.tree_projects._projects.get(path, None)
            if item is not None:
                return item.name

    def cleanup_tabs(self):
        """
        Cleans depending on what objects are visible
        """
        # Clean up tabs
        if self._treeSymbols:
            self._treeSymbols.clean()
        if self._listErrors:
            self._listErrors.clear()
        if self._listMigration:
            self._listMigration.clear()

    def shortcut_index(self, index):
        self.setCurrentIndex(index)


explorer = ExplorerContainer()