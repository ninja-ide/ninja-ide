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

from PyQt4.QtCore import Qt
from PyQt4.QtCore import QObject
from PyQt4.QtCore import QSettings
from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QApplication
from PyQt4.QtGui import QKeySequence
from PyQt4.QtGui import QInputDialog
from PyQt4.QtGui import QMessageBox

from ninja_ide.core.file_handling import file_manager
from ninja_ide.core import settings
from ninja_ide.core.pattern import singleton
from ninja_ide import resources
from ninja_ide.tools import ui_tools
from ninja_ide.tools import locator
from ninja_ide.gui import ide
from ninja_ide.gui.editor import editor
from ninja_ide.gui.dialogs import from_import_dialog
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
        self._locator = locator.Locator()
        self.__codeBack = []
        self.__codeForward = []
        self.__bookmarksFile = ''
        self.__bookmarksPos = -1
        self.__breakpointsFile = ''
        self.__breakpointsPos = -1
        self.__operations = {
            0: self._navigate_code_jumps,
            1: self._navigate_bookmarks,
            2: self._navigate_breakpoints}

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

    def install_shortcuts(self, ide):
        """Install the shortcuts to the IDE."""
        self.shortSwitchFocus = QShortcut(short("Switch-Focus"), self.ide)
        self.shortFullscreen = QShortcut(short("Full-screen"), self.ide)

        #Connect Shortcuts Signals
        self.connect(self.shortNavigateBack, SIGNAL("activated()"),
            lambda: self.__navigate_with_keyboard(False))
        self.connect(self.shortNavigateForward, SIGNAL("activated()"),
            lambda: self.__navigate_with_keyboard(True))
        self.connect(self.shortFullscreen, SIGNAL("activated()"),
            self.fullscreen_mode)
        self.connect(self.shortSwitchFocus, SIGNAL("activated()"),
            self.switch_focus)
        self.connect(self.shortImport, SIGNAL("activated()"),
            self.import_from_everywhere)
        self.connect(self.shortOpenLastTabOpened, SIGNAL("activated()"),
            self.reopen_last_tab)
        self.connect(self.shortAddBookmark, SIGNAL("activated()"),
            self._add_bookmark_breakpoint)
        self.connect(self.shortShowPasteHistory, SIGNAL("activated()"),
            self.ide.central.lateralPanel.combo.showPopup)
        self.connect(self.shortCopyHistory, SIGNAL("activated()"),
            self._copy_history)
        self.connect(self.shortPasteHistory, SIGNAL("activated()"),
            self._paste_history)

        #Connect SIGNALs from other objects
        self.connect(self.ide.mainContainer._tabMain,
            SIGNAL("runFile()"), self.execute_file)
        self.connect(self.ide.mainContainer._tabSecondary,
            SIGNAL("runFile()"), self.execute_file)
        self.connect(self.ide.mainContainer._tabMain,
            SIGNAL("addToProject(QString)"), self._add_file_to_project)
        self.connect(self.ide.mainContainer._tabSecondary,
            SIGNAL("addToProject(QString)"), self._add_file_to_project)
        self.connect(self.ide.mainContainer,
            SIGNAL("openProject(QString)"), self.open_project)

        # Not Configurable Shortcuts
        self._shortEscStatus = QShortcut(QKeySequence(Qt.Key_Escape),
            status)
        self._shortEscMisc = QShortcut(QKeySequence(Qt.Key_Escape),
            self.ide.misc)
        self.connect(self._shortEscStatus, SIGNAL("activated()"),
            status.hide_status)
        self.connect(self._shortEscMisc, SIGNAL("activated()"),
            self.ide.misc.hide)

    def move_tab_to_next_split(self):
        self.ide.mainContainer.move_tab_to_next_split(
            self.ide.mainContainer.actualTab)

    def switch_focus(self):
        widget = QApplication.focusWidget()
        if widget:
            if widget in (self.ide.mainContainer.actualTab,
               self.ide.mainContainer.actualTab.currentWidget()):
                self.ide.explorer.currentWidget().setFocus()
            elif widget in (self.ide.explorer,
                 self.ide.explorer.currentWidget()):
                if self.ide.misc.isVisible():
                    self.ide.misc.stack.currentWidget().setFocus()
                else:
                    self.ide.mainContainer.actualTab.currentWidget().setFocus()
            elif widget.parent() is self.ide.misc.stack:
                self.ide.mainContainer.actualTab.currentWidget().setFocus()

    def _copy_history(self):
        """Copy the selected text into the copy/paste history."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget and editorWidget.hasFocus():
            cursor = editorWidget.textCursor()
            copy = cursor.selectedText()
            self.ide.central.lateralPanel.add_new_copy(copy)

    def _paste_history(self):
        """Paste the text from the copy/paste history."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget and editorWidget.hasFocus():
            cursor = editorWidget.textCursor()
            paste = self.ide.central.lateralPanel.get_paste()
            cursor.insertText(paste)

    def _add_bookmark_breakpoint(self):
        """Add a bookmark or breakpoint to the current file in the editor."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget and editorWidget.hasFocus():
            if self.ide.mainContainer.actualTab.navigator.operation == 1:
                editorWidget._sidebarWidget.set_bookmark(
                    editorWidget.textCursor().blockNumber())
            elif self.ide.mainContainer.actualTab.navigator.operation == 2:
                editorWidget._sidebarWidget.set_breakpoint(
                    editorWidget.textCursor().blockNumber())

    def __navigate_with_keyboard(self, val):
        """Navigate between the positions in the jump history stack."""
        op = self.ide.mainContainer._tabMain.navigator.operation
        self.navigate_code_history(val, op)

    def _add_file_to_project(self, path):
        """Add the file for 'path' in the project the user choose here."""
        pathProject = [self.ide.explorer.get_actual_project()]
        addToProject = ui_tools.AddToProject(pathProject, self.ide)
        addToProject.exec_()
        if not addToProject.pathSelected:
            return
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if not editorWidget.ID:
            name = QInputDialog.getText(None,
                self.tr("Add File To Project"), self.tr("File Name:"))[0]
            if not name:
                QMessageBox.information(self, self.tr("Invalid Name"),
                    self.tr("The file name is empty, please enter a name"))
                return
        else:
            name = file_manager.get_basename(editorWidget.ID)
        path = file_manager.create_path(addToProject.pathSelected, name)
        try:
            path = file_manager.store_file_content(
                path, editorWidget.get_text(), newFile=True)
            self.ide.mainContainer._file_watcher.allow_kill = False
            if path != editorWidget.ID:
                self.ide.mainContainer.remove_standalone_watcher(
                    editorWidget.ID)
            editorWidget.ID = path
            self.ide.mainContainer.add_standalone_watcher(path)
            self.ide.mainContainer._file_watcher.allow_kill = True
            self.ide.explorer.add_existing_file(path)
            self.ide.change_window_title(path)
            name = file_manager.get_basename(path)
            self.ide.mainContainer.actualTab.setTabText(
                self.ide.mainContainer.actualTab.currentIndex(), name)
            editorWidget._file_saved()
        except file_manager.NinjaFileExistsException as ex:
            QMessageBox.information(self, self.tr("File Already Exists"),
                (self.tr("Invalid Path: the file '%s' already exists.") %
                    ex.filename))

    def add_project_to_console(self, projectFolder):
        """Add the namespace of the project received into the ninja-console."""
        self.ide.misc._console.load_project_into_console(projectFolder)

    def remove_project_from_console(self, projectFolder):
        """Remove the namespace of the project received from the console."""
        self.ide.misc._console.unload_project_from_console(projectFolder)

    def import_from_everywhere(self):
        """Show the dialog to insert an import from any place in the editor."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget:
            text = editorWidget.get_text()
            froms = re.findall('^from (.*)', text, re.MULTILINE)
            fromSection = list(set([f.split(' import')[0] for f in froms]))
            dialog = from_import_dialog.FromImportDialog(fromSection,
                editorWidget, self.ide)
            dialog.show()

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

    def fullscreen_mode(self):
        """Change to fullscreen mode."""
        if self.ide.isFullScreen():
            self.ide.showMaximized()
        else:
            self.ide.showFullScreen()

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
        self._locator.navigate_to(function,
            filePath, isVariable)

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

    def navigate_code_history(self, val, op):
        """Navigate the code history."""
        self.__operations[op](val)

    def _navigate_code_jumps(self, val):
        """Navigate between the jump points."""
        node = None
        if not val and self.__codeBack:
            node = self.__codeBack.pop()
            editorWidget = self.ide.mainContainer.get_actual_editor()
            if editorWidget:
                self.__codeForward.append((editorWidget.ID,
                    editorWidget.textCursor().position()))
        elif val and self.__codeForward:
            node = self.__codeForward.pop()
            editorWidget = self.ide.mainContainer.get_actual_editor()
            if editorWidget:
                self.__codeBack.append((editorWidget.ID,
                    editorWidget.textCursor().position()))
        if node:
            self.ide.mainContainer.open_file(node[0], node[1])

    def _navigate_breakpoints(self, val):
        """Navigate between the breakpoints."""
        breakList = list(settings.BREAKPOINTS.keys())
        breakList.sort()
        if not breakList:
            return
        if self.__breakpointsFile not in breakList:
            self.__breakpointsFile = breakList[0]
        index = breakList.index(self.__breakpointsFile)
        breaks = settings.BREAKPOINTS.get(self.__breakpointsFile, [])
        lineNumber = 0
        #val == True: forward
        if val:
            if (len(breaks) - 1) > self.__breakpointsPos:
                self.__breakpointsPos += 1
                lineNumber = breaks[self.__breakpointsPos]
            elif len(breaks) > 0:
                if index < (len(breakList) - 1):
                    self.__breakpointsFile = breakList[index + 1]
                else:
                    self.__breakpointsFile = breakList[0]
                self.__breakpointsPos = 0
                breaks = settings.BREAKPOINTS[self.__breakpointsFile]
                lineNumber = breaks[0]
        else:
            if self.__breakpointsPos > 0:
                self.__breakpointsPos -= 1
                lineNumber = breaks[self.__breakpointsPos]
            elif len(breaks) > 0:
                self.__breakpointsFile = breakList[index - 1]
                breaks = settings.BREAKPOINTS[self.__breakpointsFile]
                self.__breakpointsPos = len(breaks) - 1
                lineNumber = breaks[self.__breakpointsPos]
        if file_manager.file_exists(self.__breakpointsFile):
            self.ide.mainContainer.open_file(self.__breakpointsFile,
                lineNumber, None, True)
        else:
            settings.BREAKPOINTS.pop(self.__breakpointsFile)

    def _navigate_bookmarks(self, val):
        """Navigate between the bookmarks."""
        bookList = list(settings.BOOKMARKS.keys())
        bookList.sort()
        if not bookList:
            return
        if self.__bookmarksFile not in bookList:
            self.__bookmarksFile = bookList[0]
        index = bookList.index(self.__bookmarksFile)
        bookms = settings.BOOKMARKS.get(self.__bookmarksFile, [])
        lineNumber = 0
        #val == True: forward
        if val:
            if (len(bookms) - 1) > self.__bookmarksPos:
                self.__bookmarksPos += 1
                lineNumber = bookms[self.__bookmarksPos]
            elif len(bookms) > 0:
                if index < (len(bookList) - 1):
                    self.__bookmarksFile = bookList[index + 1]
                else:
                    self.__bookmarksFile = bookList[0]
                self.__bookmarksPos = 0
                bookms = settings.BOOKMARKS[self.__bookmarksFile]
                lineNumber = bookms[0]
        else:
            if self.__bookmarksPos > 0:
                self.__bookmarksPos -= 1
                lineNumber = bookms[self.__bookmarksPos]
            elif len(bookms) > 0:
                self.__bookmarksFile = bookList[index - 1]
                bookms = settings.BOOKMARKS[self.__bookmarksFile]
                self.__bookmarksPos = len(bookms) - 1
                lineNumber = bookms[self.__bookmarksPos]
        if file_manager.file_exists(self.__bookmarksFile):
            self.ide.mainContainer.open_file(self.__bookmarksFile,
                lineNumber, None, True)
        else:
            settings.BOOKMARKS.pop(self.__bookmarksFile)

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

    def reopen_last_tab(self):
        """Reopen the last closed tab."""
        self.ide.mainContainer.actualTab._reopen_last_tab()

    def reload_toolbar(self):
        """Reload the Toolbar."""
        self.ide.load_toolbar()
