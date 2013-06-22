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

import re
import webbrowser

from PyQt4.QtCore import QObject
from PyQt4.QtCore import QSettings
from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QInputDialog
from PyQt4.QtGui import QMessageBox

from ninja_ide.core.file_handling import file_manager
from ninja_ide.core import settings
from ninja_ide.core.pattern import singleton
from ninja_ide.tools import ui_tools
from ninja_ide.gui import ide
from ninja_ide.gui.editor import editor
from ninja_ide.gui.main_panel import tab_group


@singleton
class Actions(QObject):

    """This class is like the Sauron's Ring:
    One ring to rule them all, One ring to find them,
    One ring to bring them all and in the darkness bind them.

    This Class knows all the containers, and its know by all the containers,
    but the containers don't need to know between each other, in this way we
    can keep a better api without the need to tie the behaviour between
    the widgets, and let them just consume the 'actions' they need."""

    def __init__(self):
        QObject.__init__(self)
        #Definition Locator
        #self._locator = locator.Locator()

        ide.IDE.register_service(self, 'actions')

        #Register signals connections
        connections = (
            {'target': 'main_container',
            'signal_name': 'currentTabChanged(QString)',
            'slot': 'update_migration_tips'},
            {'target': 'main_container',
            'signal_name': 'updateFileMetadata(QString)',
            'slot': 'update_migration_tips'},
            {'target': 'main_container',
            'signal_name': 'migrationAnalyzed()',
            'slot': 'update_migration_tips'}
            )
        ide.IDE.register_signals('actions', connections)

    def move_tab_to_next_split(self):
        self.ide.mainContainer.move_tab_to_next_split(
            self.ide.mainContainer.actualTab)

    def add_project_to_console(self, projectFolder):
        """Add the namespace of the project received into the ninja-console."""
        self.ide.misc._console.load_project_into_console(projectFolder)

    def remove_project_from_console(self, projectFolder):
        """Remove the namespace of the project received from the console."""
        self.ide.misc._console.unload_project_from_console(projectFolder)

    def open_project_properties(self):
        """Open a Project and load the symbols in the Code Locator."""
        self.ide.explorer.open_project_properties()

    def create_profile(self):
        """Create a profile binding files and projects to a key."""
        profileInfo = QInputDialog.getText(None,
            self.tr("Create Profile"), self.tr(
                "The Current Files and Projects will "
                "be associated to this profile.\n"
                "Profile Name:"))
        if profileInfo[1]:
            profileName = profileInfo[0]
            if not profileName or profileName in settings.PROFILES:
                QMessageBox.information(self, self.tr("Profile Name Invalid"),
                    self.tr("The Profile name is invalid or already exists."))
                return
            self.save_profile(profileName)
            return profileName

    def save_profile(self, profileName):
        """Save the updates from a profile."""
        projects_obj = self.ide.explorer.get_opened_projects()
        projects = [p.path for p in projects_obj]
        files = self.ide.mainContainer.get_opened_documents()
        files = files[0] + files[1]
        settings.PROFILES[profileName] = [files, projects]
        qsettings = QSettings()
        qsettings.setValue('ide/profiles', settings.PROFILES)

    def activate_profile(self):
        """Show the Profile Manager dialog."""
        profilesLoader = ui_tools.ProfilesLoader(self._load_profile_data,
            self.create_profile, self.save_profile,
            settings.PROFILES, self.ide)
        profilesLoader.show()

    def deactivate_profile(self):
        """Close the Profile Session."""
        self.ide.Profile = None

    def _load_profile_data(self, key):
        """Activate the selected profile, closing the current files/projects"""
        self.ide.explorer.close_opened_projects()
        self.ide.mainContainer.open_files(settings.PROFILES[key][0])
        self.ide.explorer.open_session_projects(settings.PROFILES[key][1])

    def close_files_from_project(self, project):
        """Close the files related to this project."""
        if project:
            tabMain = self.ide.mainContainer._tabMain
            for tabIndex in reversed(list(range(tabMain.count()))):
                if file_manager.belongs_to_folder(
                project, tabMain.widget(tabIndex).ID):
                    tabMain.removeTab(tabIndex)

            tabSecondary = self.ide.mainContainer._tabSecondary
            for tabIndex in reversed(list(range(tabSecondary.count()))):
                if file_manager.belongs_to_folder(
                project, tabSecondary.widget(tabIndex).ID):
                    tabSecondary.removeTab(tabIndex)
            self.ide.profile = None

    def count_file_code_lines(self):
        """Count the lines of code in the current file."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget:
            block_count = editorWidget.blockCount()
            blanks = re.findall('(^\n)|(^(\s+)?#)|(^( +)?($|\n))',
                editorWidget.get_text(), re.M)
            blanks_count = len(blanks)
            resume = self.tr("Lines code: %s\n") % (block_count - blanks_count)
            resume += (self.tr("Blanks and commented lines: %s\n\n") %
                blanks_count)
            resume += self.tr("Total lines: %s") % block_count
            msgBox = QMessageBox(QMessageBox.Information,
                self.tr("Summary of lines"), resume,
                QMessageBox.Ok, editorWidget)
            msgBox.exec_()

    def reset_editor_flags(self):
        """Reset the Flags for all the opened editors."""
        self.ide.mainContainer.reset_editor_flags()

    def call_editors_function(self, call_function, *args, **kwargs):
        self.ide.mainContainer.call_editors_function(
            call_function, args, kwargs)

    def preview_in_browser(self):
        """Load the current html file in the default browser."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget:
            if not editorWidget.ID:
                self.ide.mainContainer.save_file()
            ext = file_manager.get_file_extension(editorWidget.ID)
            if ext == 'html':
                webbrowser.open(editorWidget.ID)

    def save_all(self):
        """Save all the opened files."""
        self.ide.mainContainer.save_all()

    def locate_function(self, function, filePath, isVariable):
        """Move the cursor to the proper position in the navigate stack."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget:
            self.__codeBack.append((editorWidget.ID,
                editorWidget.textCursor().position()))
            self.__codeForward = []
        #self._locator.navigate_to(function,
            #filePath, isVariable)

    def update_explorer(self):
        """Update the symbols in the Symbol Explorer when a file is saved."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget:
            ext = file_manager.get_file_extension(editorWidget.ID)
            #obtain a symbols handler for this file extension
            symbols_handler = settings.get_symbols_handler(ext)
            if symbols_handler:
                source = editorWidget.toPlainText()
                if editorWidget.encoding is not None:
                    source = source.encode(editorWidget.encoding)
                if ext == 'py':
                    args = (source, True)
                else:
                    args = (source,)
                symbols = symbols_handler.obtain_symbols(*args)
                self.ide.explorer.update_symbols(symbols, editorWidget.ID)

            #TODO: Should we change the code below similar to the code above?
            exts = settings.SYNTAX.get('python')['extension']
            if ext in exts or editorWidget.newDocument:
                self.ide.explorer.update_errors(
                    editorWidget.errors, editorWidget.pep8)

    def update_migration_tips(self):
        """Update the migration tips in the Explorer."""
        # This should be refactored with the new definition of singals in
        # the MainContainer
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget:
            self.ide.explorer.update_migration(editorWidget.migration)

    def add_back_item_navigation(self):
        """Add an item to the back stack and reset the forward stack."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget:
            self.__codeBack.append((editorWidget.ID,
                editorWidget.textCursor().position()))
            self.__codeForward = []

    def group_tabs_together(self):
        """Group files that belongs to the same project together."""
        if self.ide.explorer._treeProjects is None:
            return
        projects_obj = self.ide.explorer.get_opened_projects()
        projects = [p.path for p in projects_obj]
        for project in projects:
            projectName = self.ide.explorer.get_project_name(project)
            if not projectName:
                projectName = file_manager.get_basename(project)
            tabGroup = tab_group.TabGroup(project, projectName, self)
            for index in reversed(list(range(
            self.ide.mainContainer._tabMain.count()))):
                widget = self.ide.mainContainer._tabMain.widget(index)
                if type(widget) is editor.Editor and \
                file_manager.belongs_to_folder(project, widget.ID):
                    tabGroup.add_widget(widget)
                    self.ide.mainContainer._tabMain.removeTab(index)
            if tabGroup.tabs:
                self.ide.mainContainer._tabMain.add_tab(tabGroup, projectName)

    def deactivate_tabs_groups(self):
        """Deactivate tab grouping based in the project they belong."""
        for index in reversed(list(range(
        self.ide.mainContainer._tabMain.count()))):
            widget = self.ide.mainContainer._tabMain.widget(index)
            if type(widget) is tab_group.TabGroup:
                widget.only_expand()

    def reload_toolbar(self):
        """Reload the Toolbar."""
        self.ide.load_toolbar()
