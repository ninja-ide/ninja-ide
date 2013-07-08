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

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QTabWidget
from PyQt4.QtGui import QFileDialog
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QIcon

from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QSettings
from PyQt4.QtCore import QDateTime

from ninja_ide import resources
from ninja_ide.core import settings
from ninja_ide.core import file_manager
from ninja_ide.gui.explorer import tree_projects_widget
from ninja_ide.gui.explorer import tree_symbols_widget
from ninja_ide.gui.explorer import errors_lists
from ninja_ide.gui.explorer import migration_lists
from ninja_ide.gui.main_panel import main_container
from ninja_ide.gui.dialogs import wizard_new_project
from ninja_ide.tools import json_manager
from ninja_ide.tools import ui_tools

try:
    from PyQt4.QtWebKit import QWebInspector
except:
    settings.WEBINSPECTOR_SUPPORTED = False

from ninja_ide.tools.logger import NinjaLogger

logger = NinjaLogger('ninja_ide.gui.explorer.explorer_container')

__explorerContainerInstance = None


def ExplorerContainer(*args, **kw):
    global __explorerContainerInstance
    if __explorerContainerInstance is None:
        __explorerContainerInstance = __ExplorerContainer(*args, **kw)
    return __explorerContainerInstance


class __ExplorerContainer(QTabWidget):

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

    def __init__(self, parent=None):
        QTabWidget.__init__(self, parent)
        self.setTabPosition(QTabWidget.East)
        self.__ide = parent
        self._thread_execution = {}

        #Searching the Preferences
        self._treeProjects = None
        if settings.SHOW_PROJECT_EXPLORER:
            self.add_tab_projects()
        self._treeSymbols = None
        if settings.SHOW_SYMBOLS_LIST:
            self.add_tab_symbols()
        self._inspector = None
        if settings.SHOW_WEB_INSPECTOR and settings.WEBINSPECTOR_SUPPORTED:
            self.add_tab_inspector()
        self._listErrors = None
        if settings.SHOW_ERRORS_LIST:
            self.add_tab_errors()
        self._listMigration = None
        if settings.SHOW_MIGRATION_LIST:
            self.add_tab_migration()

    def update_symbols(self, symbols, fileName):
        if self._treeSymbols:
            self._treeSymbols.update_symbols_tree(symbols, filename=fileName)

    def update_errors(self, errors, pep8):
        if self._listErrors:
            self._listErrors.refresh_lists(errors, pep8)

    def update_migration(self, migration):
        if self._listMigration:
            self._listMigration.refresh_lists(migration)

    def addTab(self, tab, title):
        QTabWidget.addTab(self, tab, title)

    def add_tab_migration(self):
        if not self._listMigration:
            self._listMigration = migration_lists.MigrationWidget()
            self.addTab(self._listMigration, self.tr("Migration 2to3"))

    def add_tab_projects(self):
        if not self._treeProjects:
            self._treeProjects = tree_projects_widget.TreeProjectsWidget()
            self.addTab(self._treeProjects, self.tr('Projects'))
            self.connect(self._treeProjects, SIGNAL("runProject()"),
                         self.__ide.actions.execute_project)
            self.connect(self.__ide, SIGNAL("goingDown()"),
                         self._treeProjects.shutdown)
            self.connect(self._treeProjects,
                         SIGNAL("addProjectToConsole(QString)"),
                         self.__ide.actions.add_project_to_console)
            self.connect(self._treeProjects,
                         SIGNAL("removeProjectFromConsole(QString)"),
                         self.__ide.actions.remove_project_from_console)

            def close_project_signal():
                self.emit(SIGNAL("updateLocator()"))

            def close_files_related_to_closed_project(project):
                if project:
                    self.emit(SIGNAL("projectClosed(QString)"), project)
            self.connect(self._treeProjects, SIGNAL("closeProject(QString)"),
                         close_project_signal)
            self.connect(self._treeProjects, SIGNAL("refreshProject()"),
                         close_project_signal)
            self.connect(self._treeProjects,
                         SIGNAL("closeFilesFromProjectClosed(QString)"),
                         close_files_related_to_closed_project)

    def add_tab_symbols(self):
        if not self._treeSymbols:
            self._treeSymbols = tree_symbols_widget.TreeSymbolsWidget()
            self.addTab(self._treeSymbols, self.tr('Symbols'))

            def _go_to_definition(lineno):
                self.emit(SIGNAL("goToDefinition(int)"), lineno)
            self.connect(self._treeSymbols, SIGNAL("goToDefinition(int)"),
                         _go_to_definition)

    def update_current_symbol(self, line, col):
        """Select the proper item in the symbols list."""
        if self._treeSymbols is not None:
            self._treeSymbols.select_current_item(line, col)

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
                         self.__ide.mainContainer.reset_pep8_warnings)
            self.connect(self._listErrors, SIGNAL("lintActivated(bool)"),
                         self.__ide.mainContainer.reset_lint_warnings)

    def remove_tab_migration(self):
        if self._listMigration:
            self.removeTab(self.indexOf(self._listMigration))
            self._listMigration = None

    def remove_tab_errors(self):
        if self._listErrors:
            self.removeTab(self.indexOf(self._listErrors))
            self._listErrors = None

    def remove_tab_projects(self):
        if self._treeProjects:
            self.removeTab(self.indexOf(self._treeProjects))
            self._treeProjects = None

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

    def add_tab(self, widget, name, icon):
        self.addTab(widget, QIcon(icon), name)

    def rotate_tab_position(self):
        if self.tabPosition() == QTabWidget.East:
            self.setTabPosition(QTabWidget.West)
        else:
            self.setTabPosition(QTabWidget.East)

    def show_project_tree(self):
        if self._treeProjects:
            self.setCurrentWidget(self._treeProjects)

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
        if not self._treeProjects and notIDEStart:
            QMessageBox.information(self, self.tr("Projects Disabled"),
                self.tr("Project support has been disabled from Preferences"))
            return
        if not folderName:
            if settings.WORKSPACE:
                directory = settings.WORKSPACE
            else:
                directory = os.path.expanduser("~")
                current_project = self.get_actual_project()
                mainContainer = main_container.MainContainer()
                editorWidget = mainContainer.get_actual_editor()
                if current_project is not None:
                    directory = current_project
                elif editorWidget is not None and editorWidget.ID:
                    directory = file_manager.get_folder(editorWidget.ID)
            folderName = QFileDialog.getExistingDirectory(self,
                                  self.tr("Open Project Directory"), directory)
        try:
            if not folderName:
                return
            if not self._treeProjects.is_open(folderName):
                self._treeProjects.mute_signals = True
                self._treeProjects.loading_project(folderName)
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
                self._treeProjects._set_current_project(folderName)
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
            self._treeProjects.mute_signals = False

    def _callback_open_project(self, value):
        path, structure = value
        if structure is None:
            self._treeProjects.remove_loading_icon(path)
            return

        self._treeProjects.load_project(structure, path)
        self.save_recent_projects(path)
        self.emit(SIGNAL("projectOpened(QString)"), path)
        self.emit(SIGNAL("updateLocator()"))

    def create_new_project(self):
        if not self._treeProjects:
            QMessageBox.information(self, self.tr("Projects Disabled"),
                self.tr("Project support has been disabled from Preferences"))
            return
        wizard = wizard_new_project.WizardNewProject(self)
        wizard.show()

    def add_existing_file(self, path):
        if self._treeProjects:
            self._treeProjects.add_existing_file(path)

    def get_actual_project(self):
        if self._treeProjects:
            return self._treeProjects.get_selected_project_path()
        return None

    def get_project_main_file(self):
        if self._treeProjects:
            return self._treeProjects.get_project_main_file()
        return ''

    def get_project_given_filename(self, filename):
        projects = self.get_opened_projects()
        for project in projects:
            if filename.startswith(project.path):
                return project
        return None

    def get_opened_projects(self):
        if self._treeProjects:
            return self._treeProjects.get_open_projects()
        return []

    def open_session_projects(self, projects, notIDEStart=True):
        if not self._treeProjects:
            return
        for project in projects:
            if file_manager.folder_exists(project):
                self.open_project_folder(project, notIDEStart)

    def open_project_properties(self):
        if self._treeProjects:
            self._treeProjects.open_project_properties()

    def close_opened_projects(self):
        if self._treeProjects:
            self._treeProjects._close_open_projects()

    def save_recent_projects(self, folder):
        recent_project_list = QSettings(
            resources.SETTINGS_PATH,
            QSettings.IniFormat).value('recentProjects', {})
        #if already exist on the list update the date time
        projectProperties = json_manager.read_ninja_project(folder)
        name = projectProperties.get('name', '')
        description = projectProperties.get('description', '')

        if name == '':
            name = file_manager.get_basename(folder)

        if description == '':
            description = self.tr('no description available')

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
                del recent_project_list[self.find_most_old_open()]
        QSettings(resources.SETTINGS_PATH, QSettings.IniFormat).setValue(
            'recentProjects', recent_project_list)

    def find_most_old_open(self):
        recent_project_list = QSettings(
            resources.SETTINGS_PATH,
            QSettings.IniFormat).value('recentProjects', {})
        listFounder = []
        for recent_project_path, content in list(recent_project_list.items()):
            listFounder.append((recent_project_path, int(
                content["lastopen"].toString("yyyyMMddHHmmzzz"))))
        listFounder = sorted(listFounder, key=lambda date: listFounder[1],
                             reverse=True)   # sort by date last used
        return listFounder[0][0]

    def get_project_name(self, path):
        if self._treeProjects:
            item = self._treeProjects._projects.get(path, None)
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


class WebInspector(QWidget):

    def __init__(self, parent):
        QWidget.__init__(self, parent)
        vbox = QVBoxLayout(self)
        self._webInspector = QWebInspector(self)
        vbox.addWidget(self._webInspector)
        self.btnDock = QPushButton(self.tr("Undock"))
        vbox.addWidget(self.btnDock)
