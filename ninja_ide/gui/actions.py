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
import sys
import webbrowser

from PyQt4.QtCore import Qt
from PyQt4.QtCore import QObject
from PyQt4.QtCore import QSettings
from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QApplication
from PyQt4.QtGui import QKeySequence
from PyQt4.QtGui import QInputDialog
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QShortcut

from ninja_ide.core import file_manager
from ninja_ide.core import settings
from ninja_ide import resources
from ninja_ide.tools import ui_tools
from ninja_ide.tools import locator
from ninja_ide.tools import json_manager
from ninja_ide.gui.editor import editor
from ninja_ide.gui.editor import helpers
from ninja_ide.gui.dialogs import from_import_dialog
from ninja_ide.gui.main_panel import class_diagram
from ninja_ide.gui.main_panel import tab_group


__actionsInstance = None


# Actions Singleton
def Actions(*args, **kw):
    global __actionsInstance
    if __actionsInstance is None:
        __actionsInstance = __Actions(*args, **kw)
    return __actionsInstance


class __Actions(QObject):

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

    def install_shortcuts(self, ide):
        """Install the shortcuts to the IDE."""
        self.ide = ide
        short = resources.get_shortcut
        self.shortChangeTab = QShortcut(short("Change-Tab"), self.ide)
        self.shortChangeTabReverse = QShortcut(
            short("Change-Tab-Reverse"), self.ide)
        self.shortMoveTabToRight = QShortcut(
            short("Move-Tab-to-right"), self.ide)
        self.shortMoveTabToLeft = QShortcut(
            short("Move-Tab-to-left"), self.ide)
        self.shortDuplicate = QShortcut(short("Duplicate"), self.ide)
        self.shortRemove = QShortcut(short("Remove-line"), self.ide)
        self.shortMoveUp = QShortcut(short("Move-up"), self.ide)
        self.shortMoveDown = QShortcut(short("Move-down"), self.ide)
        self.shortCloseTab = QShortcut(short("Close-tab"), self.ide)
        self.shortNew = QShortcut(short("New-file"), self.ide)
        self.shortNewProject = QShortcut(short("New-project"), self.ide)
        self.shortOpen = QShortcut(short("Open-file"), self.ide)
        self.shortOpenProject = QShortcut(short("Open-project"), self.ide)
        self.shortSave = QShortcut(short("Save-file"), self.ide)
        self.shortSaveProject = QShortcut(short("Save-project"), self.ide)
        self.shortPrint = QShortcut(short("Print-file"), self.ide)
        self.shortRedo = QShortcut(short("Redo"), self.ide)
        self.shortAddBookmark = QShortcut(short("Add-Bookmark-or-Breakpoint"),
            self.ide)
        self.shortComment = QShortcut(short("Comment"), self.ide)
        self.shortUncomment = QShortcut(short("Uncomment"), self.ide)
        self.shortHorizontalLine = QShortcut(short("Horizontal-line"),
            self.ide)
        self.shortTitleComment = QShortcut(short("Title-comment"), self.ide)
        self.shortIndentLess = QShortcut(short("Indent-less"), self.ide)
        self.shortHideMisc = QShortcut(short("Hide-misc"), self.ide)
        self.shortHideEditor = QShortcut(short("Hide-editor"), self.ide)
        self.shortHideExplorer = QShortcut(short("Hide-explorer"), self.ide)
        self.shortRunFile = QShortcut(short("Run-file"), self.ide)
        self.shortRunProject = QShortcut(short("Run-project"), self.ide)
        self.shortSwitchFocus = QShortcut(short("Switch-Focus"), self.ide)
        self.shortStopExecution = QShortcut(short("Stop-execution"), self.ide)
        self.shortHideAll = QShortcut(short("Hide-all"), self.ide)
        self.shortFullscreen = QShortcut(short("Full-screen"), self.ide)
        self.shortFind = QShortcut(short("Find"), self.ide)
        self.shortFindNext = QShortcut(short("Find-next"), self.ide)
        self.shortFindPrevious = QShortcut(short("Find-previous"), self.ide)
        self.shortFindReplace = QShortcut(short("Find-replace"), self.ide)
        self.shortFindWithWord = QShortcut(short("Find-with-word"), self.ide)
        self.shortHelp = QShortcut(short("Help"), self.ide)
        self.shortSplitHorizontal = QShortcut(short("Split-horizontal"),
            self.ide)
        self.shortSplitVertical = QShortcut(short("Split-vertical"), self.ide)
        self.shortFollowMode = QShortcut(short("Follow-mode"), self.ide)
        self.shortReloadFile = QShortcut(short("Reload-file"), self.ide)
        self.shortFindInFiles = QShortcut(short("Find-in-files"), self.ide)
        self.shortImport = QShortcut(short("Import"), self.ide)
        self.shortGoToDefinition = QShortcut(short("Go-to-definition"),
            self.ide)
        self.shortCompleteDeclarations = QShortcut(
            short("Complete-Declarations"), self.ide)
        self.shortCodeLocator = QShortcut(short("Code-locator"), self.ide)
        self.shortFileOpener = QShortcut(short("File-Opener"), self.ide)
        self.shortNavigateBack = QShortcut(short("Navigate-back"), self.ide)
        self.shortNavigateForward = QShortcut(short("Navigate-forward"),
            self.ide)
        self.shortOpenLastTabOpened = QShortcut(short("Open-recent-closed"),
            self.ide)
        self.shortShowCodeNav = QShortcut(short("Show-Code-Nav"), self.ide)
        self.shortShowPasteHistory = QShortcut(short("Show-Paste-History"),
            self.ide)
        self.shortPasteHistory = QShortcut(short("History-Paste"), self.ide)
        self.shortCopyHistory = QShortcut(short("History-Copy"), self.ide)
        self.shortHighlightWord = QShortcut(short("Highlight-Word"), self.ide)
        self.shortChangeSplitFocus = QShortcut(short("change-split-focus"),
            self.ide)
        self.shortMoveTabSplit = QShortcut(short("move-tab-to-next-split"),
            self.ide)
        self.shortChangeTabVisibility = QShortcut(
            short("change-tab-visibility"), self.ide)

        #Connect Shortcuts Signals
        self.connect(self.shortNavigateBack, SIGNAL("activated()"),
            lambda: self.__navigate_with_keyboard(False))
        self.connect(self.shortNavigateForward, SIGNAL("activated()"),
            lambda: self.__navigate_with_keyboard(True))
        self.connect(self.shortCodeLocator, SIGNAL("activated()"),
            self.ide.status.show_locator)
        self.connect(self.shortFileOpener, SIGNAL("activated()"),
            self.ide.status.show_file_opener)
        self.connect(self.shortGoToDefinition, SIGNAL("activated()"),
            self.editor_go_to_definition)
        self.connect(self.shortCompleteDeclarations, SIGNAL("activated()"),
            self.editor_complete_declaration)
        self.connect(self.shortRedo, SIGNAL("activated()"),
            self.editor_redo)
        self.connect(self.shortHorizontalLine, SIGNAL("activated()"),
            self.editor_insert_horizontal_line)
        self.connect(self.shortTitleComment, SIGNAL("activated()"),
            self.editor_insert_title_comment)
        self.connect(self.shortFollowMode, SIGNAL("activated()"),
            self.ide.mainContainer.show_follow_mode)
        self.connect(self.shortReloadFile, SIGNAL("activated()"),
            self.ide.mainContainer.reload_file)
        self.connect(self.shortSplitHorizontal, SIGNAL("activated()"),
            lambda: self.ide.mainContainer.split_tab(True))
        self.connect(self.shortSplitVertical, SIGNAL("activated()"),
            lambda: self.ide.mainContainer.split_tab(False))
        self.connect(self.shortNew, SIGNAL("activated()"),
            self.ide.mainContainer.add_editor)
        self.connect(self.shortNewProject, SIGNAL("activated()"),
            self.ide.explorer.create_new_project)
        self.connect(self.shortHideMisc, SIGNAL("activated()"),
            self.view_misc_visibility)
        self.connect(self.shortHideEditor, SIGNAL("activated()"),
            self.view_main_visibility)
        self.connect(self.shortHideExplorer, SIGNAL("activated()"),
            self.view_explorer_visibility)
        self.connect(self.shortHideAll, SIGNAL("activated()"),
            self.hide_all)
        self.connect(self.shortFullscreen, SIGNAL("activated()"),
            self.fullscreen_mode)
        self.connect(self.shortOpen, SIGNAL("activated()"),
            self.ide.mainContainer.open_file)
        self.connect(self.shortOpenProject, SIGNAL("activated()"),
            self.open_project)
        self.connect(self.shortCloseTab, SIGNAL("activated()"),
            self.ide.mainContainer.close_tab)
        self.connect(self.shortSave, SIGNAL("activated()"),
            self.ide.mainContainer.save_file)
        self.connect(self.shortSaveProject, SIGNAL("activated()"),
            self.save_project)
        self.connect(self.shortPrint, SIGNAL("activated()"),
            self.print_file)
        self.connect(self.shortFind, SIGNAL("activated()"),
            self.ide.status.show)
        self.connect(self.shortFindPrevious, SIGNAL("activated()"),
            self.ide.status._searchWidget.find_previous)
        self.connect(self.shortFindNext, SIGNAL("activated()"),
            self.ide.status._searchWidget.find_next)
        self.connect(self.shortFindWithWord, SIGNAL("activated()"),
            self.ide.status.show_with_word)
        self.connect(self.shortFindReplace, SIGNAL("activated()"),
            self.ide.status.show_replace)
        self.connect(self.shortRunFile, SIGNAL("activated()"),
            self.execute_file)
        self.connect(self.shortRunProject, SIGNAL("activated()"),
            self.execute_project)
        self.connect(self.shortSwitchFocus, SIGNAL("activated()"),
            self.switch_focus)
        self.connect(self.shortStopExecution, SIGNAL("activated()"),
            self.kill_execution)
        self.connect(self.shortIndentLess, SIGNAL("activated()"),
            self.editor_indent_less)
        self.connect(self.shortComment, SIGNAL("activated()"),
            self.editor_comment)
        self.connect(self.shortUncomment, SIGNAL("activated()"),
            self.editor_uncomment)
        self.connect(self.shortHelp, SIGNAL("activated()"),
            self.ide.mainContainer.show_python_doc)
        self.connect(self.shortImport, SIGNAL("activated()"),
            self.import_from_everywhere)
        self.connect(self.shortFindInFiles, SIGNAL("activated()"),
            self.ide.misc.show_find_in_files_widget)
        self.connect(self.shortMoveUp, SIGNAL("activated()"),
            self.editor_move_up)
        self.connect(self.shortMoveDown, SIGNAL("activated()"),
            self.editor_move_down)
        self.connect(self.shortRemove, SIGNAL("activated()"),
            self.editor_remove_line)
        self.connect(self.shortDuplicate, SIGNAL("activated()"),
            self.editor_duplicate)
        self.connect(self.shortOpenLastTabOpened, SIGNAL("activated()"),
            self.reopen_last_tab)
        self.connect(self.shortChangeTab, SIGNAL("activated()"),
            self.ide.mainContainer.change_tab)
        self.connect(self.shortChangeTabReverse, SIGNAL("activated()"),
            self.ide.mainContainer.change_tab_reverse)
        self.connect(self.shortMoveTabToRight, SIGNAL("activated()"),
            self.move_tab)
        self.connect(self.shortMoveTabToLeft, SIGNAL("activated()"),
            lambda: self.move_tab(next=False))
        self.connect(self.shortShowCodeNav, SIGNAL("activated()"),
            self.ide.mainContainer.show_navigation_buttons)
        self.connect(self.shortAddBookmark, SIGNAL("activated()"),
            self._add_bookmark_breakpoint)
        self.connect(self.shortShowPasteHistory, SIGNAL("activated()"),
            self.ide.central.lateralPanel.combo.showPopup)
        self.connect(self.shortCopyHistory, SIGNAL("activated()"),
            self._copy_history)
        self.connect(self.shortPasteHistory, SIGNAL("activated()"),
            self._paste_history)
        self.connect(self.shortHighlightWord, SIGNAL("activated()"),
            self.editor_highlight_word)
        self.connect(self.shortChangeSplitFocus, SIGNAL("activated()"),
            self.ide.mainContainer.change_split_focus)
        self.connect(self.shortMoveTabSplit, SIGNAL("activated()"),
            self.move_tab_to_next_split)
        self.connect(self.shortChangeTabVisibility, SIGNAL("activated()"),
            self.ide.mainContainer.change_tabs_visibility)

        key = Qt.Key_1
        for i in range(10):
            if sys.platform == "darwin":
                short = TabShortcuts(
                    QKeySequence(Qt.CTRL + Qt.ALT + key), self.ide, i)
            else:
                short = TabShortcuts(QKeySequence(Qt.ALT + key), self.ide, i)
            key += 1
            self.connect(short, SIGNAL("activated()"), self._change_tab_index)
        short = TabShortcuts(QKeySequence(Qt.ALT + Qt.Key_0), self.ide, 10)
        self.connect(short, SIGNAL("activated()"), self._change_tab_index)

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
            self.ide.status)
        self._shortEscMisc = QShortcut(QKeySequence(Qt.Key_Escape),
            self.ide.misc)
        self.connect(self._shortEscStatus, SIGNAL("activated()"),
            self.ide.status.hide_status)
        self.connect(self._shortEscMisc, SIGNAL("activated()"),
            self.ide.misc.hide)

    def update_shortcuts(self):
        """If the user update the key binded to any shortcut, update them."""
        resources.load_shortcuts()
        short = resources.get_shortcut
        self.shortDuplicate.setKey(short("Duplicate"))
        self.shortRemove.setKey(short("Remove-line"))
        self.shortMoveUp.setKey(short("Move-up"))
        self.shortMoveDown.setKey(short("Move-down"))
        self.shortCloseTab.setKey(short("Close-tab"))
        self.shortNew.setKey(short("New-file"))
        self.shortNewProject.setKey(short("New-project"))
        self.shortOpen.setKey(short("Open-file"))
        self.shortOpenProject.setKey(short("Open-project"))
        self.shortSave.setKey(short("Save-file"))
        self.shortSaveProject.setKey(short("Save-project"))
        self.shortPrint.setKey(short("Print-file"))
        self.shortRedo.setKey(short("Redo"))
        self.shortComment.setKey(short("Comment"))
        self.shortUncomment.setKey(short("Uncomment"))
        self.shortHorizontalLine.setKey(short("Horizontal-line"))
        self.shortTitleComment.setKey(short("Title-comment"))
        self.shortIndentLess.setKey(short("Indent-less"))
        self.shortHideMisc.setKey(short("Hide-misc"))
        self.shortHideEditor.setKey(short("Hide-editor"))
        self.shortHideExplorer.setKey(short("Hide-explorer"))
        self.shortRunFile.setKey(short("Run-file"))
        self.shortRunProject.setKey(short("Run-project"))
        self.shortSwitchFocus.setKey(short("Switch-Focus"))
        self.shortStopExecution.setKey(short("Stop-execution"))
        self.shortHideAll.setKey(short("Hide-all"))
        self.shortFullscreen.setKey(short("Full-screen"))
        self.shortFind.setKey(short("Find"))
        self.shortFindNext.setKey(short("Find-next"))
        self.shortFindPrevious.setKey(short("Find-previous"))
        self.shortFindReplace.setKey(short("Find-replace"))
        self.shortFindWithWord.setKey(short("Find-with-word"))
        self.shortHelp.setKey(short("Help"))
        self.shortSplitHorizontal.setKey(short("Split-horizontal"))
        self.shortSplitVertical.setKey(short("Split-vertical"))
        self.shortFollowMode.setKey(short("Follow-mode"))
        self.shortReloadFile.setKey(short("Reload-file"))
        self.shortFindInFiles.setKey(short("Find-in-files"))
        self.shortImport.setKey(short("Import"))
        self.shortGoToDefinition.setKey(short("Go-to-definition"))
        self.shortCompleteDeclarations.setKey(short("Complete-Declarations"))
        self.shortCodeLocator.setKey(short("Code-locator"))
        self.shortFileOpener.setKey(short("File-Opener"))
        self.shortNavigateBack.setKey(short("Navigate-back"))
        self.shortNavigateForward.setKey(short("Navigate-forward"))
        self.shortOpenLastTabOpened.setKey(short("Open-recent-closed"))
        self.shortChangeTab.setKey(short("Change-Tab"))
        self.shortChangeTabReverse.setKey(short("Change-Tab-Reverse"))
        self.shortMoveTabToRight.setKey(short("Move-Tab-to-right"))
        self.shortMoveTabToLeft.setKey(short("Move-Tab-to-left"))
        self.shortAddBookmark.setKey(short("Add-Bookmark-or-Breakpoint"))
        self.shortShowCodeNav.setKey(short("Show-Code-Nav"))
        self.shortShowPasteHistory.setKey(short("Show-Paste-History"))
        self.shortPasteHistory.setKey(short("History-Paste"))
        self.shortCopyHistory.setKey(short("History-Copy"))
        self.shortHighlightWord.setKey(short("Highlight-Word"))
        self.shortChangeSplitFocus.setKey(short("change-split-focus"))
        self.shortMoveTabSplit.setKey(short("move-tab-to-next-split"))
        self.shortChangeTabVisibility.setKey(short("change-tab-visibility"))

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

    def _change_tab_index(self):
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget and editorWidget.hasFocus():
            container = self.ide.mainContainer.actualTab
        else:
            container = self.ide.explorer
        obj = self.sender()
        if obj.index < container.count():
            container.setCurrentIndex(obj.index)

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
                QMessageBox.information(None, self.tr("Invalid Name"),
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
            QMessageBox.information(None, self.tr("File Already Exists"),
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

    def open_project(self, path=''):
        """Open a Project and load the symbols in the Code Locator."""
        self.ide.explorer.open_project_folder(path)

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
                QMessageBox.information(None, self.tr("Profile Name Invalid"),
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
        qsettings = QSettings(resources.SETTINGS_PATH, QSettings.IniFormat)
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

    def execute_file(self):
        """Execute the current file."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        #emit a signal for plugin!
        self.emit(SIGNAL("fileExecuted(QString)"), editorWidget.ID)
        if editorWidget:
            self.ide.mainContainer.save_file(editorWidget)
            ext = file_manager.get_file_extension(editorWidget.ID)
            #TODO: Remove the IF statment with polymorphism using Handler
            if ext == 'py':
                self.ide.misc.run_application(editorWidget.ID)
            elif ext == 'html':
                self.ide.misc.render_web_page(editorWidget.ID)

    def execute_project(self):
        """Execute the project marked as Main Project."""
        mainFile = self.ide.explorer.get_project_main_file()
        if not mainFile and self.ide.explorer._treeProjects and \
          self.ide.explorer._treeProjects._actualProject:
            self.ide.explorer._treeProjects.open_project_properties()
        elif mainFile:
            self.save_project()
            path = self.ide.explorer.get_actual_project()
            #emit a signal for plugin!
            self.emit(SIGNAL("projectExecuted(QString)"), path)

            # load our jutsus!
            project = json_manager.read_ninja_project(path)
            python_exec = project.get('venv', False)
            if not python_exec:
                python_exec = project.get('pythonPath', 'python')
            PYTHONPATH = project.get('PYTHONPATH', None)
            params = project.get('programParams', '')
            preExec = project.get('preExecScript', '')
            postExec = project.get('postExecScript', '')
            mainFile = file_manager.create_path(path, mainFile)
            self.ide.misc.run_application(mainFile, pythonPath=python_exec,
                PYTHONPATH=PYTHONPATH,
                programParams=params, preExec=preExec, postExec=postExec)

    def kill_execution(self):
        """Kill the execution of the current file or project."""
        self.ide.misc.kill_application()

    def fullscreen_mode(self):
        """Change to fullscreen mode."""
        if self.ide.isFullScreen():
            self.ide.showMaximized()
        else:
            self.ide.showFullScreen()

    def editor_redo(self):
        """Execute the redo action in the current editor."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget and editorWidget.hasFocus():
            editorWidget.redo()

    def editor_indent_less(self):
        """Indent 1 position to the left for the current line or selection."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget and editorWidget.hasFocus():
            editorWidget.indent_less()

    def editor_indent_more(self):
        """Indent 1 position to the right for the current line or selection."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget and editorWidget.hasFocus():
            editorWidget.indent_more()

    def editor_insert_debugging_prints(self):
        """Insert a print statement in each selected line."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget:
            helpers.insert_debugging_prints(editorWidget)

    def editor_insert_pdb(self):
        """Insert a pdb.set_trace() statement in tjhe current line."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget:
            helpers.insert_pdb(editorWidget)

    def editor_comment(self):
        """Mark the current line or selection as a comment."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget and editorWidget.hasFocus():
            helpers.comment(editorWidget)

    def editor_uncomment(self):
        """Uncomment the current line or selection."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget and editorWidget.hasFocus():
            helpers.uncomment(editorWidget)

    def editor_insert_horizontal_line(self):
        """Insert an horizontal lines of comment symbols."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget and editorWidget.hasFocus():
            helpers.insert_horizontal_line(editorWidget)

    def editor_insert_title_comment(self):
        """Insert a Title surrounded by comment symbols."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget and editorWidget.hasFocus():
            helpers.insert_title_comment(editorWidget)

    def editor_remove_trailing_spaces(self):
        """Remove the trailing spaces in the current editor."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget:
            helpers.remove_trailing_spaces(editorWidget)

    def editor_replace_tabs_with_spaces(self):
        """Replace the Tabs with Spaces in the current editor."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget:
            helpers.replace_tabs_with_spaces(editorWidget)

    def editor_move_up(self):
        """Move the current line or selection one position up."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget and editorWidget.hasFocus():
            helpers.move_up(editorWidget)

    def editor_move_down(self):
        """Move the current line or selection one position down."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget and editorWidget.hasFocus():
            helpers.move_down(editorWidget)

    def editor_remove_line(self):
        """Remove the current line or selection."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget and editorWidget.hasFocus():
            helpers.remove_line(editorWidget)

    def editor_duplicate(self):
        """Duplicate the current line or selection."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget and editorWidget.hasFocus():
            helpers.duplicate(editorWidget)

    def editor_go_to_definition(self):
        """Search the definition of the method or variable under the cursor.

        If more than one method or variable is found with the same name,
        shows a table with the results and let the user decide where to go."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget and editorWidget.hasFocus():
            editorWidget.go_to_definition()

    def editor_highlight_word(self):
        """Highlight the occurrences of the current word in the editor."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget and editorWidget.hasFocus():
            editorWidget.highlight_selected_word()

    def editor_complete_declaration(self):
        """Do the opposite action that Complete Declaration expect."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget and editorWidget.hasFocus():
            editorWidget.complete_declaration()

    def editor_go_to_line(self, line):
        """Jump to the specified line in the current editor."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget:
            editorWidget.jump_to_line(line)

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

    def hide_all(self):
        """Hide/Show all the containers except the editor."""
        if self.ide.menuBar().isVisible():
            self.ide.central.lateralPanel.hide()
            self.ide.misc.hide()
            self.ide.toolbar.hide()
            self.ide.menuBar().hide()
        else:
            self.ide.central.lateralPanel.show()
            self.ide.toolbar.show()
            self.ide.menuBar().show()
        self.ide._menuView.hideAllAction.setChecked(
            self.ide.menuBar().isVisible())
        self.ide._menuView.hideConsoleAction.setChecked(
            self.ide.central.misc.isVisible())
        self.ide._menuView.hideEditorAction.setChecked(
            self.ide.central.mainContainer.isVisible())
        self.ide._menuView.hideExplorerAction.setChecked(
            self.ide.central.lateralPanel.isVisible())
        self.ide._menuView.hideToolbarAction.setChecked(
            self.ide.toolbar.isVisible())

    def view_misc_visibility(self):
        self.ide.central.change_misc_visibility()
        self.ide._menuView.hideConsoleAction.setChecked(
            self.ide.central.misc.isVisible())

    def view_main_visibility(self):
        self.ide.central.change_main_visibility()
        self.ide._menuView.hideEditorAction.setChecked(
            self.ide.central.mainContainer.isVisible())

    def view_explorer_visibility(self):
        self.ide.central.change_explorer_visibility()
        self.ide._menuView.hideExplorerAction.setChecked(
            self.ide.central.lateralPanel.isVisible())

    def save_project(self):
        """Save all the opened files that belongs to the actual project."""
        path = self.ide.explorer.get_actual_project()
        if path:
            self.ide.mainContainer.save_project(path)

    def save_all(self):
        """Save all the opened files."""
        self.ide.mainContainer.save_all()

    def print_file(self):
        """Call the print of ui_tool

        Call print of ui_tool depending on the focus of the application"""
        #TODO: Add funtionality for proyect tab and methods tab
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget is not None:
            fileName = "newDocument.pdf"
            if editorWidget.ID:
                fileName = file_manager.get_basename(
                    editorWidget.ID)
                fileName = fileName[:fileName.rfind('.')] + '.pdf'
            ui_tools.print_file(fileName, editorWidget.print_)

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

    def open_class_diagram(self):
        """Open the Class Diagram Generator."""
        diagram = class_diagram.ClassDiagram(self)
        self.ide.mainContainer.add_tab(diagram, self.tr("Class Diagram v.0.1"))

    def reload_toolbar(self):
        """Reload the Toolbar."""
        self.ide.load_toolbar()

    def move_tab(self, next=True, widget=None):
        actualTab = self.ide.mainContainer.actualTab
        if widget is None:
            widget = actualTab.currentWidget()
        if widget is not None:
            old_widget_index = actualTab.indexOf(widget)
            if next and old_widget_index < actualTab.count() - 1:
                new_widget_index = old_widget_index + 1
            elif old_widget_index > 0 and not next:
                new_widget_index = old_widget_index - 1
            else:
                return
            tabName = actualTab.tabText(old_widget_index)
            actualTab.insertTab(new_widget_index, widget, tabName)
            actualTab.setCurrentIndex(new_widget_index)


class TabShortcuts(QShortcut):

    def __init__(self, key, parent, index):
        super(TabShortcuts, self).__init__(key, parent)
        self.index = index
