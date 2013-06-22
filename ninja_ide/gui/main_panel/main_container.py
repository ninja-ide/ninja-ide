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

import sys
import os
import re
import webbrowser

from PyQt4 import uic
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QSplitter
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QStyle
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QFileDialog
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QScrollBar
from PyQt4.QtGui import QShortcut
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QDir

from ninja_ide import resources
from ninja_ide.core.file_handling import file_manager
from ninja_ide.core import settings
from ninja_ide.core.pattern import singleton
from ninja_ide.core.file_handling.filesystem_notifications import (
    NinjaFileSystemWatcher)
from ninja_ide.gui.ide import IDE
from ninja_ide.gui.main_panel import tab_widget
from ninja_ide.gui.main_panel import tab_group
from ninja_ide.gui.editor import editor
#from ninja_ide.gui.editor import highlighter
from ninja_ide.gui.editor import helpers
from ninja_ide.gui.main_panel import browser_widget
from ninja_ide.gui.main_panel import start_page
from ninja_ide.gui.main_panel import image_viewer
from ninja_ide.gui.dialogs import from_import_dialog
from ninja_ide.tools import locator
from ninja_ide.tools import runner
from ninja_ide.tools import ui_tools

from ninja_ide.tools.logger import NinjaLogger

logger = NinjaLogger('ninja_ide.gui.main_panel.main_container')


@singleton
class _MainContainer(QWidget):

###############################################################################
# MainContainer SIGNALS
###############################################################################
    """
    beforeFileSaved(QString)
    fileSaved(QString)
    currentTabChanged(QString)
    locateFunction(QString, QString, bool) [functionName, filePath, isVariable]
    openProject(QString)
    openPreferences()
    dontOpenStartPage()
    navigateCode(bool, int)
    addBackItemNavigation()
    updateLocator(QString)
    updateFileMetadata()
    findOcurrences(QString)
    cursorPositionChange(int, int)    #row, col
    fileOpened(QString)
    newFileOpened(QString)
    enabledFollowMode(bool)
    recentTabsModified(QStringList)
    migrationAnalyzed()
    allTabClosed()
    """
###############################################################################

    def __init__(self, parent=None):
        super(MainContainer, self).__init__(parent)
        self._parent = parent
        hbox = QHBoxLayout(self)

        #Create scrollbar for follow mode
        self.scrollBar = QScrollBar(Qt.Vertical, self)
        self.scrollBar.setFixedWidth(20)
        self.scrollBar.setToolTip(
            self.tr('Follow Mode: Scroll the Editors together'))
        self.scrollBar.hide()
        hbox.addWidget(self.scrollBar)

        self.splitter = QSplitter()
        self._tabMain = tab_widget.TabWidget(self)
        self._tabSecondary = tab_widget.TabWidget(self)
        self.setAcceptDrops(True)
        self.splitter.addWidget(self._tabMain)
        self.splitter.addWidget(self._tabSecondary)
        self.splitter.setSizes([1, 1])
        hbox.addWidget(self.splitter)

        self._tabSecondary.hide()
        self.actualTab = self._tabMain
        self._followMode = False
        self.split_visible = False
        #TODO: WHY IS THIS????????
        #highlighter.restyle(resources.CUSTOM_SCHEME)
        #documentation browser
        self.docPage = None
        # File Watcher
        self._file_watcher = NinjaFileSystemWatcher
        self._watched_simple_files = []
        #Code Navigation
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

        self.connect(self.mainContainer,
            SIGNAL("locateFunction(QString, QString, bool)"),
            self.locate_function)
        self.connect(self.scrollBar, SIGNAL("valueChanged(int)"),
            self.move_follow_scrolls)
        self.connect(self._tabMain, SIGNAL("currentChanged(int)"),
            self._current_tab_changed)
        self.connect(self._tabSecondary, SIGNAL("currentChanged(int)"),
            self._current_tab_changed)
        self.connect(self._tabMain, SIGNAL("currentChanged(int)"),
            self._exit_follow_mode)
        self.connect(self._tabMain, SIGNAL("changeActualTab(QTabWidget)"),
            self._change_actual)
        self.connect(self._tabSecondary, SIGNAL("changeActualTab(QTabWidget)"),
            self._change_actual)
        self.connect(self._tabMain, SIGNAL("splitTab(QTabWidget, int, bool)"),
            self._split_this_tab)
        self.connect(self._tabSecondary,
            SIGNAL("splitTab(QTabWidget, int, bool)"),
            self._split_this_tab)
        self.connect(self._tabMain, SIGNAL("reopenTab(QTabWidget, QString)"),
            self._reopen_last_tab)
        self.connect(self._tabSecondary,
            SIGNAL("reopenTab(QTabWidget, QString)"),
            self._reopen_last_tab)
        self.connect(self._tabMain, SIGNAL("syntaxChanged(QWidget, QString)"),
            self._specify_syntax)
        self.connect(self._tabSecondary,
            SIGNAL("syntaxChanged(QWidget, QString)"),
            self._specify_syntax)
        self.connect(self._tabMain, SIGNAL("allTabsClosed()"),
            self._main_without_tabs)
        self.connect(self._tabSecondary, SIGNAL("allTabsClosed()"),
            self._secondary_without_tabs)
        #reload file
        self.connect(self._tabMain, SIGNAL("reloadFile(QWidget)"),
            self.reload_file)
        self.connect(self._tabSecondary, SIGNAL("reloadFile(QWidget)"),
            self.reload_file)
        #for Save on Close operation
        self.connect(self._tabMain, SIGNAL("saveActualEditor()"),
            self.save_file)
        self.connect(self._tabSecondary, SIGNAL("saveActualEditor()"),
            self.save_file)
        #Navigate Code
        self.connect(self._tabMain, SIGNAL("navigateCode(bool, int)"),
            self._navigate_code)
        self.connect(self._tabSecondary, SIGNAL("navigateCode(bool, int)"),
            self._navigate_code)
        # Refresh recent tabs
        self.connect(self._tabMain, SIGNAL("recentTabsModified(QStringList)"),
            self._recent_files_changed)

        IDE.register_service('main_container', self)

        #Register signals connections
        connections = (
            {'target': 'menu_file',
            'signal_name': 'openFile(QString)',
            'slot': self.open_file},
            {'target': 'explorer_container',
            'signal_name': 'goToDefinition(int)',
            'slot': self.editor_go_to_line},
            {'target': 'explorer_container',
            'signal_name': 'projectClosed(QString)',
            'slot': self.close_files_from_project},
            {"target": 'main_container',
            "signal_name": "avigateCode(bool, int)",
            "slot": self.navigate_code_history}
            )
        IDE.register_signals('main_container', connections)

    def install(self, ide):
        self.install_shortcuts(ide)

    def install_shortcuts(self, ide):
        short = resources.get_shortcut
        shortChangeTab = QShortcut(short("Change-Tab"), ide)
        IDE.register_shortcut('Change-Tab', shortChangeTab)
        shortChangeTabReverse = QShortcut(short("Change-Tab-Reverse"), ide)
        IDE.register_shortcut('Change-Tab-Reverse', shortChangeTabReverse)
        shortDuplicate = QShortcut(short("Duplicate"), ide)
        IDE.register_shortcut('Duplicate', shortDuplicate)
        shortRemove = QShortcut(short("Remove-line"), ide)
        IDE.register_shortcut('Remove-line', shortRemove)
        shortRemove = QShortcut(short("Remove-line"), ide)
        IDE.register_shortcut('Remove-line', shortRemove)
        shortMoveUp = QShortcut(short("Move-up"), ide)
        IDE.register_shortcut('Move-up', shortMoveUp)
        shortMoveDown = QShortcut(short("Move-down"), ide)
        IDE.register_shortcut('Move-down', shortMoveDown)
        shortCloseTab = QShortcut(short("Close-tab"), ide)
        IDE.register_shortcut('Close-tab', shortCloseTab)
        shortNew = QShortcut(short("New-file"), ide)
        IDE.register_shortcut('New-file', shortNew)
        shortOpen = QShortcut(short("Open-file"), ide)
        IDE.register_shortcut('Open-file', shortOpen)
        shortSave = QShortcut(short("Save-file"), ide)
        IDE.register_shortcut('Save-file', shortSave)
        shortRedo = QShortcut(short("Redo"), ide)
        IDE.register_shortcut('Redo', shortRedo)
        shortAddBookmark = QShortcut(short("Add-Bookmark-or-Breakpoint"), ide)
        IDE.register_shortcut('Add-Bookmark-or-Breakpoint',
            shortAddBookmark)
        shortComment = QShortcut(short("Comment"), ide)
        IDE.register_shortcut('Comment', shortComment)
        shortUncomment = QShortcut(short("Uncomment"), ide)
        IDE.register_shortcut('Uncomment', shortUncomment)
        shortHorizontalLine = QShortcut(short("Horizontal-line"), ide)
        IDE.register_shortcut('Horizontal-line', shortHorizontalLine)
        shortTitleComment = QShortcut(short("Title-comment"), ide)
        IDE.register_shortcut('Title-comment', shortTitleComment)
        shortIndentLess = QShortcut(short("Indent-less"), ide)
        IDE.register_shortcut('Indent-less', shortIndentLess)
        shortSplitHorizontal = QShortcut(short("Split-horizontal"), ide)
        IDE.register_shortcut('Split-horizontal', shortSplitHorizontal)
        shortSplitVertical = QShortcut(short("Split-vertical"), ide)
        IDE.register_shortcut('Split-vertical', shortSplitVertical)
        shortFollowMode = QShortcut(short("Follow-mode"), ide)
        IDE.register_shortcut('Follow-mode', shortFollowMode)
        shortReloadFile = QShortcut(short("Reload-file"), ide)
        IDE.register_shortcut('Reload-file', shortReloadFile)
        shortImport = QShortcut(short("Import"), ide)
        IDE.register_shortcut('Import', shortImport)
        shortGoToDefinition = QShortcut(short("Go-to-definition"), ide)
        IDE.register_shortcut('Go-to-definition', shortGoToDefinition)
        shortCompleteDeclarations = QShortcut(
            short("Complete-Declarations"), ide)
        IDE.register_shortcut('Complete-Declarations',
            shortCompleteDeclarations)
        shortNavigateBack = QShortcut(short("Navigate-back"), ide)
        IDE.register_shortcut('Navigate-back', shortNavigateBack)
        shortNavigateForward = QShortcut(short("Navigate-forward"), ide)
        IDE.register_shortcut('Navigate-forward', shortNavigateForward)
        shortOpenLastTabOpened = QShortcut(short("Open-recent-closed"), ide)
        IDE.register_shortcut('Open-recent-closed', shortOpenLastTabOpened)
        shortShowCodeNav = QShortcut(short("Show-Code-Nav"), ide)
        IDE.register_shortcut('Show-Code-Nav', shortShowCodeNav)
        shortChangeSplitFocus = QShortcut(short("change-split-focus"), ide)
        IDE.register_shortcut('change-split-focus', shortChangeSplitFocus)
        shortMoveTabSplit = QShortcut(short("move-tab-to-next-split"), ide)
        IDE.register_shortcut('move-tab-to-next-split', shortMoveTabSplit)
        shortChangeTabVisibility = QShortcut(
            short("change-tab-visibility"), ide)
        IDE.register_shortcut('change-tab-visibility',
            shortChangeTabVisibility)
        shortHelp = QShortcut(short("Help"), ide)
        IDE.register_shortcut('Help', shortHelp)
        shortHighlightWord = QShortcut(short("Highlight-Word"), ide)
        IDE.register_shortcut('Highlight-Word', shortHighlightWord)
        shortPrint = QShortcut(short("Print-file"), ide)
        IDE.register_shortcut('Print-file', shortPrint)
        shortCopyHistory = QShortcut(short("History-Copy"), ide)
        IDE.register_shortcut('History-Copy', shortCopyHistory)
        shortPasteHistory = QShortcut(short("History-Paste"), ide)
        IDE.register_shortcut('History-Paste', shortPasteHistory)

        #Connect
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
            self.show_follow_mode)
        self.connect(self.shortReloadFile, SIGNAL("activated()"),
            self.reload_file)
        self.connect(self.shortSplitHorizontal, SIGNAL("activated()"),
            lambda: self.split_tab(True))
        self.connect(self.shortSplitVertical, SIGNAL("activated()"),
            lambda: self.split_tab(False))
        self.connect(self.shortNew, SIGNAL("activated()"),
            self.add_editor)
        self.connect(self.shortOpen, SIGNAL("activated()"),
            self.open_file)
        self.connect(self.shortCloseTab, SIGNAL("activated()"),
            self.close_tab)
        self.connect(self.shortSave, SIGNAL("activated()"),
            self.save_file)
        self.connect(self.shortIndentLess, SIGNAL("activated()"),
            self.editor_indent_less)
        self.connect(self.shortComment, SIGNAL("activated()"),
            self.editor_comment)
        self.connect(self.shortUncomment, SIGNAL("activated()"),
            self.editor_uncomment)
        self.connect(self.shortHelp, SIGNAL("activated()"),
            self.show_python_doc)
        self.connect(self.shortMoveUp, SIGNAL("activated()"),
            self.editor_move_up)
        self.connect(self.shortMoveDown, SIGNAL("activated()"),
            self.editor_move_down)
        self.connect(self.shortRemove, SIGNAL("activated()"),
            self.editor_remove_line)
        self.connect(self.shortDuplicate, SIGNAL("activated()"),
            self.editor_duplicate)
        self.connect(self.shortChangeTab, SIGNAL("activated()"),
            self.change_tab)
        self.connect(self.shortChangeTabReverse, SIGNAL("activated()"),
            self.change_tab_reverse)
        self.connect(self.shortShowCodeNav, SIGNAL("activated()"),
            self.show_navigation_buttons)
        self.connect(self.shortHighlightWord, SIGNAL("activated()"),
            self.editor_highlight_word)
        self.connect(self.shortChangeSplitFocus, SIGNAL("activated()"),
            self.change_split_focus)
        self.connect(self.shortMoveTabSplit, SIGNAL("activated()"),
            self.move_tab_to_next_split)
        self.connect(self.shortChangeTabVisibility, SIGNAL("activated()"),
            self.change_tabs_visibility)
        self.connect(shortPrint, SIGNAL("activated()"),
            self.print_file)
        self.connect(shortAddBookmark, SIGNAL("activated()"),
            self._add_bookmark_breakpoint)
        self.connect(shortImport, SIGNAL("activated()"),
            self.import_from_everywhere)
        self.connect(shortNavigateBack, SIGNAL("activated()"),
            lambda: self.__navigate_with_keyboard(False))
        self.connect(shortNavigateForward, SIGNAL("activated()"),
            lambda: self.__navigate_with_keyboard(True))
        self.connect(shortOpenLastTabOpened, SIGNAL("activated()"),
            self._reopen_last_tab)
        self.connect(shortCopyHistory, SIGNAL("activated()"),
            self._copy_history)
        self.connect(shortPasteHistory, SIGNAL("activated()"),
            self._paste_history)

    def locate_function(self, function, filePath, isVariable):
        """Move the cursor to the proper position in the navigate stack."""
        editorWidget = self.get_actual_editor()
        if editorWidget:
            self.__codeBack.append((editorWidget.ID,
                editorWidget.textCursor().position()))
            self.__codeForward = []
        self._locator.navigate_to(function, filePath, isVariable)

    def close_files_from_project(self, project):
        """Close the files related to this project."""
        if project:
            for tabIndex in reversed(list(range(self._tabMain.count()))):
                if file_manager.belongs_to_folder(
                project, self._tabMain.widget(tabIndex).ID):
                    self._tabMain.removeTab(tabIndex)

            for tabIndex in reversed(list(range(self._tabSecondary.count()))):
                if file_manager.belongs_to_folder(
                project, self._tabSecondary.widget(tabIndex).ID):
                    self._tabSecondary.removeTab(tabIndex)
            self.ide.profile = None

    def _paste_history(self):
        """Paste the text from the copy/paste history."""
        editorWidget = self.get_actual_editor()
        if editorWidget and editorWidget.hasFocus():
            cursor = editorWidget.textCursor()
            central = IDE.get_service('central_container')
            if central:
                paste = central.lateralPanel.get_paste()
                cursor.insertText(paste)

    def _copy_history(self):
        """Copy the selected text into the copy/paste history."""
        editorWidget = self.get_actual_editor()
        if editorWidget and editorWidget.hasFocus():
            cursor = editorWidget.textCursor()
            copy = cursor.selectedText()
            central = IDE.get_service('central_container')
            if central:
                central.lateralPanel.add_new_copy(copy)

    def import_from_everywhere(self):
        """Add an item to the back stack and reset the forward stack."""
        editorWidget = self.get_actual_editor()
        if editorWidget:
            text = editorWidget.get_text()
            froms = re.findall('^from (.*)', text, re.MULTILINE)
            fromSection = list(set([f.split(' import')[0] for f in froms]))
            dialog = from_import_dialog.FromImportDialog(fromSection,
                editorWidget, self.ide)
            dialog.show()

    def add_back_item_navigation(self):
        """Add an item to the back stack and reset the forward stack."""
        editorWidget = self.get_actual_editor()
        if editorWidget:
            self.__codeBack.append((editorWidget.ID,
                editorWidget.textCursor().position()))
            self.__codeForward = []

    def preview_in_browser(self):
        """Load the current html file in the default browser."""
        editorWidget = self.get_actual_editor()
        if editorWidget:
            if not editorWidget.ID:
                self.ide.mainContainer.save_file()
            ext = file_manager.get_file_extension(editorWidget.ID)
            if ext == 'html':
                webbrowser.open(editorWidget.ID)

    def _add_bookmark_breakpoint(self):
        """Add a bookmark or breakpoint to the current file in the editor."""
        editorWidget = self.get_actual_editor()
        if editorWidget and editorWidget.hasFocus():
            if self.actualTab.navigator.operation == 1:
                editorWidget._sidebarWidget.set_bookmark(
                    editorWidget.textCursor().blockNumber())
            elif self.actualTab.navigator.operation == 2:
                editorWidget._sidebarWidget.set_breakpoint(
                    editorWidget.textCursor().blockNumber())

    def __navigate_with_keyboard(self, val):
        """Navigate between the positions in the jump history stack."""
        op = self.actualTab.navigator.operation
        self.navigate_code_history(val, op)

    def navigate_code_history(self, val, op):
        """Navigate the code history."""
        self.__operations[op](val)

    def _navigate_code_jumps(self, val):
        """Navigate between the jump points."""
        node = None
        if not val and self.__codeBack:
            node = self.__codeBack.pop()
            editorWidget = self.get_actual_editor()
            if editorWidget:
                self.__codeForward.append((editorWidget.ID,
                    editorWidget.textCursor().position()))
        elif val and self.__codeForward:
            node = self.__codeForward.pop()
            editorWidget = self.get_actual_editor()
            if editorWidget:
                self.__codeBack.append((editorWidget.ID,
                    editorWidget.textCursor().position()))
        if node:
            self.open_file(node[0], node[1])

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
            self.open_file(self.__breakpointsFile,
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
            self.open_file(self.__bookmarksFile,
                lineNumber, None, True)
        else:
            settings.BOOKMARKS.pop(self.__bookmarksFile)

    def count_file_code_lines(self):
        """Count the lines of code in the current file."""
        editorWidget = self.get_actual_editor()
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

    def editor_go_to_definition(self):
        """Search the definition of the method or variable under the cursor.

        If more than one method or variable is found with the same name,
        shows a table with the results and let the user decide where to go."""
        editorWidget = self.get_actual_editor()
        if editorWidget and editorWidget.hasFocus():
            editorWidget.go_to_definition()

    def editor_redo(self):
        """Execute the redo action in the current editor."""
        editorWidget = self.get_actual_editor()
        if editorWidget and editorWidget.hasFocus():
            editorWidget.redo()

    def editor_indent_less(self):
        """Indent 1 position to the left for the current line or selection."""
        editorWidget = self.get_actual_editor()
        if editorWidget and editorWidget.hasFocus():
            editorWidget.indent_less()

    def editor_indent_more(self):
        """Indent 1 position to the right for the current line or selection."""
        editorWidget = self.get_actual_editor()
        if editorWidget and editorWidget.hasFocus():
            editorWidget.indent_more()

    def editor_insert_debugging_prints(self):
        """Insert a print statement in each selected line."""
        editorWidget = self.get_actual_editor()
        if editorWidget:
            helpers.insert_debugging_prints(editorWidget)

    def editor_insert_pdb(self):
        """Insert a pdb.set_trace() statement in tjhe current line."""
        editorWidget = self.get_actual_editor()
        if editorWidget:
            helpers.insert_pdb(editorWidget)

    def editor_comment(self):
        """Mark the current line or selection as a comment."""
        editorWidget = self.get_actual_editor()
        if editorWidget and editorWidget.hasFocus():
            helpers.comment(editorWidget)

    def editor_uncomment(self):
        """Uncomment the current line or selection."""
        editorWidget = self.get_actual_editor()
        if editorWidget and editorWidget.hasFocus():
            helpers.uncomment(editorWidget)

    def editor_insert_horizontal_line(self):
        """Insert an horizontal lines of comment symbols."""
        editorWidget = self.get_actual_editor()
        if editorWidget and editorWidget.hasFocus():
            helpers.insert_horizontal_line(editorWidget)

    def editor_insert_title_comment(self):
        """Insert a Title surrounded by comment symbols."""
        editorWidget = self.get_actual_editor()
        if editorWidget and editorWidget.hasFocus():
            helpers.insert_title_comment(editorWidget)

    def editor_remove_trailing_spaces(self):
        """Remove the trailing spaces in the current editor."""
        editorWidget = self.get_actual_editor()
        if editorWidget:
            helpers.remove_trailing_spaces(editorWidget)

    def editor_replace_tabs_with_spaces(self):
        """Replace the Tabs with Spaces in the current editor."""
        editorWidget = self.get_actual_editor()
        if editorWidget:
            helpers.replace_tabs_with_spaces(editorWidget)

    def editor_move_up(self):
        """Move the current line or selection one position up."""
        editorWidget = self.get_actual_editor()
        if editorWidget and editorWidget.hasFocus():
            helpers.move_up(editorWidget)

    def editor_move_down(self):
        """Move the current line or selection one position down."""
        editorWidget = self.get_actual_editor()
        if editorWidget and editorWidget.hasFocus():
            helpers.move_down(editorWidget)

    def editor_remove_line(self):
        """Remove the current line or selection."""
        editorWidget = self.get_actual_editor()
        if editorWidget and editorWidget.hasFocus():
            helpers.remove_line(editorWidget)

    def editor_duplicate(self):
        """Duplicate the current line or selection."""
        editorWidget = self.get_actual_editor()
        if editorWidget and editorWidget.hasFocus():
            helpers.duplicate(editorWidget)

    def editor_highlight_word(self):
        """Highlight the occurrences of the current word in the editor."""
        editorWidget = self.get_actual_editor()
        if editorWidget and editorWidget.hasFocus():
            editorWidget.highlight_selected_word()

    def editor_complete_declaration(self):
        """Do the opposite action that Complete Declaration expect."""
        editorWidget = self.get_actual_editor()
        if editorWidget and editorWidget.hasFocus():
            editorWidget.complete_declaration()

    def editor_go_to_line(self, line):
        """Jump to the specified line in the current editor."""
        editorWidget = self.get_actual_editor()
        if editorWidget:
            editorWidget.jump_to_line(line)

    def _recent_files_changed(self, files):
        self.emit(SIGNAL("recentTabsModified(QStringList)"), files)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        file_path = event.mimeData().urls()[0].toLocalFile()
        self.open_file(file_path)

    def setFocus(self):
        widget = self.get_actual_widget()
        if widget:
            widget.setFocus()

    def enable_follow_mode_scrollbar(self, val):
        if val:
            editorWidget = self.get_actual_editor()
            maxScroll = editorWidget.verticalScrollBar().maximum()
            position = editorWidget.verticalScrollBar().value()
            self.scrollBar.setMaximum(maxScroll)
            self.scrollBar.setValue(position)
        self.scrollBar.setVisible(val)

    def move_follow_scrolls(self, val):
        widget = self._tabMain.currentWidget()
        diff = widget._sidebarWidget.highest_line - val
        s1 = self._tabMain.currentWidget().verticalScrollBar()
        s2 = self._tabSecondary.currentWidget().verticalScrollBar()
        s1.setValue(val)
        s2.setValue(val + diff)

    def _navigate_code(self, val, op):
        self.emit(SIGNAL("navigateCode(bool, int)"), val, op)

    def group_tabs_together(self):
        """Group files that belongs to the same project together."""
        explorer = IDE.get_service('explorer_container')
        if not explorer or explorer._treeProjects is None:
            return
        projects_obj = explorer.get_opened_projects()
        projects = [p.path for p in projects_obj]
        for project in projects:
            projectName = explorer.get_project_name(project)
            if not projectName:
                projectName = file_manager.get_basename(project)
            tabGroup = tab_group.TabGroup(project, projectName, self)
            for index in reversed(list(range(
            self._tabMain.count()))):
                widget = self._tabMain.widget(index)
                if type(widget) is editor.Editor and \
                file_manager.belongs_to_folder(project, widget.ID):
                    tabGroup.add_widget(widget)
                    self._tabMain.removeTab(index)
            if tabGroup.tabs:
                self._tabMain.add_tab(tabGroup, projectName)

    def deactivate_tabs_groups(self):
        """Deactivate tab grouping based in the project they belong."""
        for index in reversed(list(range(
        self._tabMain.count()))):
            widget = self._tabMain.widget(index)
            if type(widget) is tab_group.TabGroup:
                widget.only_expand()

    def _main_without_tabs(self):
        if self._followMode:
            # if we were in follow mode, close the duplicated editor.
            self._exit_follow_mode()
        elif self._tabSecondary.isVisible():
            self.show_split(self.orientation())
        self.emit(SIGNAL("allTabsClosed()"))

    def _secondary_without_tabs(self):
        self.show_split(self.orientation())

    def _reopen_last_tab(self, tab, path):
        self.actualTab = tab
        self.open_file(path)

    def _change_actual(self, tabWidget):
        if not self._followMode:
            self.actualTab = tabWidget

    def _current_tab_changed(self, index):
        if self.actualTab.widget(index):
            self.emit(SIGNAL("currentTabChanged(QString)"),
                self.actualTab.widget(index)._id)

    def split_tab(self, orientationHorizontal):
        """Split the main container in 2 areas.

        We are inverting the horizontal and vertical property here,
        because Qt see it Horizontal as side by side, but is confusing
        for the user."""
        if orientationHorizontal:
            self.show_split(Qt.Vertical)
        else:
            self.show_split(Qt.Horizontal)

    def _split_this_tab(self, tab, index, orientationHorizontal):
        tab.setCurrentIndex(index)
        if orientationHorizontal:
            self.show_split(Qt.Horizontal)
        else:
            self.show_split(Qt.Vertical)

    def change_tabs_visibility(self):
        if self._tabMain.tabBar().isVisible():
            self._tabMain.tabBar().hide()
            self._tabSecondary.tabBar().hide()
        else:
            self._tabMain.tabBar().show()
            self._tabSecondary.tabBar().show()

    def show_split(self, orientation):
        closingFollowMode = self._followMode
        if self._followMode:
            self._exit_follow_mode()
        if self._tabSecondary.isVisible() and \
        orientation == self.orientation():
            self._tabSecondary.hide()
            self.split_visible = False
            for i in range(self._tabSecondary.count()):
                widget = self._tabSecondary.widget(0)
                name = self._tabSecondary.tabText(0)
                self._tabMain.add_tab(widget, name)
                if name in self._tabSecondary.titles:
                    self._tabSecondary.titles.remove(name)
                if type(widget) is editor.Editor and widget.textModified:
                    self._tabMain.tab_was_modified(True)
            self.actualTab = self._tabMain
        elif not self._tabSecondary.isVisible() and not closingFollowMode:
            widget = self.get_actual_widget()
            name = self._tabMain.tabText(self._tabMain.currentIndex())
            self._tabSecondary.add_tab(widget, name)
            if name in self._tabMain.titles:
                self._tabMain.titles.remove(name)
            if type(widget) is editor.Editor and widget.textModified:
                self._tabSecondary.tab_was_modified(True)
            self._tabSecondary.show()
            self.split_visible = True
            self.setSizes([1, 1])
            self.actualTab = self._tabSecondary
            self.emit(SIGNAL("currentTabChanged(QString)"), widget.ID)
        self.setOrientation(orientation)

    def move_tab_to_next_split(self, tab_from):
        if self._followMode:
            return

        if tab_from == self._tabSecondary:
            tab_to = self._tabMain
        else:
            tab_to = self._tabSecondary

        widget = tab_from.currentWidget()
        name = tab_from.tabText(tab_from.currentIndex())
        tab_from.remove_title(tab_from.currentIndex())
        tab_to.add_tab(widget, name)
        if widget is editor.Editor and widget.textModified:
            tab_to.tab_was_saved(widget)
        tab_from.update_current_widget()

    def add_editor(self, fileName="", project=None, tabIndex=None,
        syntax=None, use_open_highlight=False):

        project_obj = self._parent.explorer.get_project_given_filename(
            fileName)
        editorWidget = editor.create_editor(fileName=fileName, project=project,
            syntax=syntax, use_open_highlight=use_open_highlight,
            project_obj=project_obj)

        if not fileName:
            tabName = "New Document"
        else:
            tabName = file_manager.get_basename(fileName)

        #add the tab
        inserted_index = self.add_tab(editorWidget, tabName, tabIndex=tabIndex)
        self.actualTab.setTabToolTip(inserted_index,
            QDir.toNativeSeparators(fileName))
        #Connect signals
        self.connect(editorWidget, SIGNAL("modificationChanged(bool)"),
            self._editor_tab_was_modified)
        self.connect(editorWidget, SIGNAL("fileSaved(QPlainTextEdit)"),
            self._editor_tab_was_saved)
        self.connect(editorWidget, SIGNAL("openDropFile(QString)"),
            self.open_file)
        self.connect(editorWidget, SIGNAL("addBackItemNavigation()"),
            self.add_back_item_navigation)
        self.connect(editorWidget,
            SIGNAL("locateFunction(QString, QString, bool)"),
            self._editor_locate_function)
        self.connect(editorWidget, SIGNAL("warningsFound(QPlainTextEdit)"),
            self._show_warning_tab_indicator)
        self.connect(editorWidget, SIGNAL("errorsFound(QPlainTextEdit)"),
            self._show_error_tab_indicator)
        self.connect(editorWidget, SIGNAL("cleanDocument(QPlainTextEdit)"),
            self._hide_icon_tab_indicator)
        self.connect(editorWidget, SIGNAL("findOcurrences(QString)"),
            self._find_occurrences)
        self.connect(editorWidget, SIGNAL("migrationAnalyzed()"),
            lambda: self.emit(SIGNAL("migrationAnalyzed()")))
        #Cursor position changed
        self.connect(editorWidget, SIGNAL("cursorPositionChange(int, int)"),
            self._cursor_position_changed)
        #keyPressEventSignal for plugins
        self.connect(editorWidget, SIGNAL("keyPressEvent(QEvent)"),
            self._editor_keyPressEvent)

        #emit a signal about the file open
        self.emit(SIGNAL("fileOpened(QString)"), fileName)

        return editorWidget

    def update_editor_project(self):
        for i in range(self._tabMain.count()):
            widget = self._tabMain.widget(i)
            if type(widget) is editor.Editor:
                project = self._parent.explorer.get_project_given_filename(
                    widget.ID)
                widget.set_project(project)
        for i in range(self._tabSecondary.count()):
            widget = self._tabSecondary.widget(i)
            if type(widget) is editor.Editor:
                project = self._parent.explorer.get_project_given_filename(
                    widget.ID)
                widget.set_project(project)

    def reset_pep8_warnings(self, value):
        for i in range(self._tabMain.count()):
            widget = self._tabMain.widget(i)
            if type(widget) is editor.Editor:
                if value:
                    widget.syncDocErrorsSignal = True
                    widget.pep8.check_style()
                else:
                    widget.hide_pep8_errors()
        for i in range(self._tabSecondary.count()):
            widget = self._tabSecondary.widget(i)
            if type(widget) is editor.Editor:
                if value:
                    widget.syncDocErrorsSignal = True
                    widget.pep8.check_style()
                else:
                    widget.hide_pep8_errors()

    def reset_lint_warnings(self, value):
        for i in range(self._tabMain.count()):
            widget = self._tabMain.widget(i)
            if type(widget) is editor.Editor:
                if value:
                    widget.syncDocErrorsSignal = True
                    widget.errors.check_errors()
                else:
                    widget.hide_lint_errors()
        for i in range(self._tabSecondary.count()):
            widget = self._tabSecondary.widget(i)
            if type(widget) is editor.Editor:
                if value:
                    widget.syncDocErrorsSignal = True
                    widget.errors.check_errors()
                else:
                    widget.hide_lint_errors()

    def _cursor_position_changed(self, row, col):
        self.emit(SIGNAL("cursorPositionChange(int, int)"), row, col)

    def _find_occurrences(self, word):
        self.emit(SIGNAL("findOcurrences(QString)"), word)

    def _show_warning_tab_indicator(self, editorWidget):
        index = self.actualTab.indexOf(editorWidget)
        self.emit(SIGNAL("updateFileMetadata()"))
        if index >= 0:
            self.actualTab.setTabIcon(index,
                QIcon(self.style().standardIcon(QStyle.SP_MessageBoxWarning)))

    def _show_error_tab_indicator(self, editorWidget):
        index = self.actualTab.indexOf(editorWidget)
        self.emit(SIGNAL("updateFileMetadata()"))
        if index >= 0:
            self.actualTab.setTabIcon(index,
                QIcon(resources.IMAGES['bug']))

    def _hide_icon_tab_indicator(self, editorWidget):
        index = self.actualTab.indexOf(editorWidget)
        self.emit(SIGNAL("updateFileMetadata()"))
        if index >= 0:
            self.actualTab.setTabIcon(index, QIcon())

    def _editor_keyPressEvent(self, event):
        self.emit(SIGNAL("editorKeyPressEvent(QEvent)"), event)

    def _editor_locate_function(self, function, filePath, isVariable):
        self.emit(SIGNAL("locateFunction(QString, QString, bool)"),
            function, filePath, isVariable)

    def _editor_tab_was_modified(self, val=True):
        self.actualTab.tab_was_modified(val)

    def _editor_tab_was_saved(self, editorWidget=None):
        self.actualTab.tab_was_saved(editorWidget)
        self.emit(SIGNAL("updateLocator(QString)"), editorWidget.ID)

    def add_tab(self, widget, tabName, tabIndex=None):
        return self.actualTab.add_tab(widget, tabName, index=tabIndex)

    def get_actual_widget(self):
        return self.actualTab.currentWidget()

    def get_actual_editor(self):
        """Return the Actual Editor or None

        Return an instance of Editor if the Current Tab contains
        an Editor or None if it is not an instance of Editor"""
        widget = self.actualTab.currentWidget()
        if type(widget) is editor.Editor:
            return widget
        return None

    def reload_file(self, editorWidget=None):
        if editorWidget is None:
            editorWidget = self.get_actual_editor()
        if editorWidget is not None and editorWidget.ID:
            fileName = editorWidget.ID
            self._file_watcher.allow_kill = False
            old_cursor_position = editorWidget.textCursor().position()
            old_widget_index = self.actualTab.indexOf(editorWidget)
            self.actualTab.removeTab(old_widget_index)
            #open the file in the same tab as before
            self.open_file(fileName, tabIndex=old_widget_index)
            #get the new editor and set the old cursor position
            editorWidget = self.get_actual_editor()
            cursor = editorWidget.textCursor()
            cursor.setPosition(old_cursor_position)
            editorWidget.setTextCursor(cursor)
            self._file_watcher.allow_kill = True

    def open_image(self, fileName):
        try:
            if not self.is_open(fileName):
                viewer = image_viewer.ImageViewer(fileName)
                self.add_tab(viewer, file_manager.get_basename(fileName))
                viewer.id = fileName
            else:
                self.move_to_open(fileName)
        except Exception as reason:
            logger.error('open_image: %s', reason)
            QMessageBox.information(self, self.tr("Incorrect File"),
                self.tr("The image couldn\'t be open"))

    def open_file(self, filename='', cursorPosition=-1,
                    tabIndex=None, positionIsLineNumber=False, notStart=True):
        if not filename:
            if settings.WORKSPACE:
                directory = settings.WORKSPACE
            else:
                directory = os.path.expanduser("~")
                editorWidget = self.get_actual_editor()
                pexplorer = self._parent.explorer
                current_project = pexplorer and pexplorer.get_actual_project()
                if current_project is not None:
                    directory = current_project
                elif editorWidget is not None and editorWidget.ID:
                    directory = file_manager.get_folder(editorWidget.ID)
            extensions = ';;'.join(
                ['(*%s)' % e for e in
                    settings.SUPPORTED_EXTENSIONS + ['.*', '']])
            fileNames = list(QFileDialog.getOpenFileNames(self,
                self.tr("Open File"), directory, extensions))
        else:
            fileNames = [filename]
        if not fileNames:
            return

        for filename in fileNames:
            if file_manager.get_file_extension(filename) in ('jpg', 'png'):
                self.open_image(filename)
            elif file_manager.get_file_extension(filename).endswith('ui'):
                self.w = uic.loadUi(filename)
                self.w.show()
            else:
                self.__open_file(filename, cursorPosition,
                    tabIndex, positionIsLineNumber, notStart)

    def __open_file(self, fileName='', cursorPosition=-1,
                    tabIndex=None, positionIsLineNumber=False, notStart=True):
        try:
            if not self.is_open(fileName):
                self.actualTab.notOpening = False
                content = file_manager.read_file_content(fileName)
                editorWidget = self.add_editor(fileName, tabIndex=tabIndex,
                    use_open_highlight=True)

                #Add content
                #we HAVE to add the editor's content before set the ID
                #because of the minimap logic
                editorWidget.setPlainText(content)
                editorWidget.ID = fileName
                editorWidget.async_highlight()
                encoding = file_manager.get_file_encoding(content)
                editorWidget.encoding = encoding
                if cursorPosition == -1:
                    cursorPosition = 0
                if not positionIsLineNumber:
                    editorWidget.set_cursor_position(cursorPosition)
                else:
                    editorWidget.go_to_line(cursorPosition)
                self.add_standalone_watcher(editorWidget.ID, notStart)

                #New file then try to add a coding line
                if not content:
                    helpers.insert_coding_line(editorWidget)
                    self.save_file(editorWidget=editorWidget)

                if not editorWidget.has_write_permission():
                    fileName += self.tr(" (Read-Only)")
                    index = self.actualTab.currentIndex()
                    self.actualTab.setTabText(index, fileName)

            else:
                self.move_to_open(fileName)
                editorWidget = self.get_actual_editor()
                if editorWidget and notStart and cursorPosition != -1:
                    if positionIsLineNumber:
                        editorWidget.go_to_line(cursorPosition)
                    else:
                        editorWidget.set_cursor_position(cursorPosition)
            self.emit(SIGNAL("currentTabChanged(QString)"), fileName)
        except file_manager.NinjaIOException as reason:
            if notStart:
                QMessageBox.information(self,
                    self.tr("The file couldn't be open"), str(reason))
        except Exception as reason:
            logger.error('open_file: %s', reason)
        self.actualTab.notOpening = True

    def add_standalone_watcher(self, filename, not_start=True):
        # Add File Watcher if needed
        opened_projects = self._parent.explorer.get_opened_projects()
        opened_projects = [p.path for p in opened_projects]
        #alone = not_start
        #for folder in opened_projects:
            #if file_manager.belongs_to_folder(folder, filename):
                #alone = False
        #if alone or sys.platform == 'darwin':
            #self._file_watcher.add_file_watch(filename)
            #self._watched_simple_files.append(filename)

    def remove_standalone_watcher(self, filename):
        if filename in self._watched_simple_files:
            self._file_watcher.remove_file_watch(filename)
            self._watched_simple_files.remove(filename)

    def is_open(self, filename):
        return self._tabMain.is_open(filename) != -1 or \
            self._tabSecondary.is_open(filename) != -1

    def move_to_open(self, filename):
        if self._tabMain.is_open(filename) != -1:
            self._tabMain.move_to_open(filename)
            self.actualTab = self._tabMain
        elif self._tabSecondary.is_open(filename) != -1:
            self._tabSecondary.move_to_open(filename)
            self.actualTab = self._tabSecondary
        self.actualTab.currentWidget().setFocus()
        self.emit(SIGNAL("currentTabChanged(QString)"), filename)

    def change_open_tab_name(self, id, newId):
        """Search for the Tab with id, and set the newId to that Tab."""
        index = self._tabMain.is_open(id)
        if index != -1:
            widget = self._tabMain.widget(index)
            tabContainer = self._tabMain
        elif self._tabSecondary.is_open(id):
            # tabSecondaryIndex is recalculated because there is a really
            # small chance that the tab is there, so there is no need to
            # calculate this value by default
            index = self._tabSecondary.is_open(id)
            widget = self._tabSecondary.widget(index)
            tabContainer = self._tabSecondary
        tabName = file_manager.get_basename(newId)
        tabContainer.change_open_tab_name(index, tabName)
        widget.ID = newId

    def close_deleted_file(self, id):
        """Search for the Tab with id, and ask the user if should be closed."""
        index = self._tabMain.is_open(id)
        if index != -1:
            tabContainer = self._tabMain
        elif self._tabSecondary.is_open(id):
            # tabSecondaryIndex is recalculated because there is a really
            # small chance that the tab is there, so there is no need to
            # calculate this value by default
            index = self._tabSecondary.is_open(id)
            tabContainer = self._tabSecondary
        result = QMessageBox.question(self, self.tr("Close Deleted File"),
            self.tr("Are you sure you want to close the deleted file?\n"
                    "The content will be completely deleted."),
            buttons=QMessageBox.Yes | QMessageBox.No)
        if result == QMessageBox.Yes:
            tabContainer.removeTab(index)

    def save_file(self, editorWidget=None):
        if not editorWidget:
            editorWidget = self.get_actual_editor()
        if not editorWidget:
            return False
        try:
            editorWidget.just_saved = True
            if editorWidget.newDocument or \
            not file_manager.has_write_permission(editorWidget.ID):
                return self.save_file_as()

            fileName = editorWidget.ID
            self.emit(SIGNAL("beforeFileSaved(QString)"), fileName)
            if settings.REMOVE_TRAILING_SPACES:
                helpers.remove_trailing_spaces(editorWidget)
            content = editorWidget.get_text()
            file_manager.store_file_content(
                fileName, content, addExtension=False)
            self._file_watcher.allow_kill = False
            if editorWidget.ID != fileName:
                self.remove_standalone_watcher(editorWidget.ID)
            self.add_standalone_watcher(fileName)
            self._file_watcher.allow_kill = True
            editorWidget.ID = fileName
            encoding = file_manager.get_file_encoding(content)
            editorWidget.encoding = encoding
            self.emit(SIGNAL("fileSaved(QString)"),
                (self.tr("File Saved: %s") % fileName))
            editorWidget._file_saved()
            return True
        except Exception as reason:
            editorWidget.just_saved = False
            logger.error('save_file: %s', reason)
            QMessageBox.information(self, self.tr("Save Error"),
                self.tr("The file couldn't be saved!"))
        return False

    def save_file_as(self):
        editorWidget = self.get_actual_editor()
        if not editorWidget:
            return False
        try:
            editorWidget.just_saved = True
            filters = '(*.py);;(*.*)'
            if editorWidget.ID:
                ext = file_manager.get_file_extension(editorWidget.ID)
                if ext != 'py':
                    filters = '(*.%s);;(*.py);;(*.*)' % ext
            save_folder = self._get_save_folder(editorWidget.ID)
            fileName = QFileDialog.getSaveFileName(
                self._parent, self.tr("Save File"), save_folder, filters)
            if not fileName:
                return False

            if settings.REMOVE_TRAILING_SPACES:
                helpers.remove_trailing_spaces(editorWidget)
            newFile = file_manager.get_file_extension(fileName) == ''
            fileName = file_manager.store_file_content(
                fileName, editorWidget.get_text(),
                addExtension=True, newFile=newFile)
            self.actualTab.setTabText(self.actualTab.currentIndex(),
                file_manager.get_basename(fileName))
            editorWidget.register_syntax(
                file_manager.get_file_extension(fileName))
            self._file_watcher.allow_kill = False
            if editorWidget.ID != fileName:
                self.remove_standalone_watcher(editorWidget.ID)
            editorWidget.ID = fileName
            self.emit(SIGNAL("fileSaved(QString)"),
                (self.tr("File Saved: %s") % fileName))
            self.emit(SIGNAL("currentTabChanged(QString)"), fileName)
            editorWidget._file_saved()
            self.add_standalone_watcher(fileName)
            self._file_watcher.allow_kill = True
            return True
        except file_manager.NinjaFileExistsException as ex:
            editorWidget.just_saved = False
            QMessageBox.information(self, self.tr("File Already Exists"),
                (self.tr("Invalid Path: the file '%s' already exists.") %
                    ex.filename))
        except Exception as reason:
            editorWidget.just_saved = False
            logger.error('save_file_as: %s', reason)
            QMessageBox.information(self, self.tr("Save Error"),
                self.tr("The file couldn't be saved!"))
            self.actualTab.setTabText(self.actualTab.currentIndex(),
                self.tr("New Document"))
        return False

    def _get_save_folder(self, fileName):
        """
        Returns the root directory of the 'Main Project' or the home folder
        """
        actual_project = self._parent.explorer.get_actual_project()
        if actual_project:
            return actual_project
        return os.path.expanduser("~")

    def save_project(self, projectFolder):
        for i in range(self._tabMain.count()):
            editorWidget = self._tabMain.widget(i)
            if type(editorWidget) is editor.Editor and \
            file_manager.belongs_to_folder(projectFolder, editorWidget.ID):
                reloaded = self._tabMain.check_for_external_modifications(
                    editorWidget)
                if not reloaded:
                    self.save_file(editorWidget)
        for i in range(self._tabSecondary.count()):
            editorWidget = self._tabSecondary.widget(i)
            if type(editorWidget) is editor.Editor and \
            file_manager.belongs_to_folder(projectFolder, editorWidget.ID):
                reloaded = self._tabSecondary.check_for_external_modifications(
                    editorWidget)
                if not reloaded:
                    self.save_file(editorWidget)

    def save_all(self):
        for i in range(self._tabMain.count()):
            editorWidget = self._tabMain.widget(i)
            if type(editorWidget) is editor.Editor:
                reloaded = self._tabMain.check_for_external_modifications(
                    editorWidget)
                if not reloaded:
                    self.save_file(editorWidget)
        for i in range(self._tabSecondary.count()):
            editorWidget = self._tabSecondary.widget(i)
            self._tabSecondary.check_for_external_modifications(editorWidget)
            if type(editorWidget) is editor.Editor:
                reloaded = self._tabSecondary.check_for_external_modifications(
                    editorWidget)
                if not reloaded:
                    self.save_file(editorWidget)

    def call_editors_function(self, call_function, *arguments):
        args = arguments[0]
        kwargs = arguments[1]
        for i in range(self._tabMain.count()):
            editorWidget = self._tabMain.widget(i)
            if type(editorWidget) is editor.Editor:
                function = getattr(editorWidget, call_function)
                function(*args, **kwargs)
        for i in range(self._tabSecondary.count()):
            editorWidget = self._tabSecondary.widget(i)
            self._tabSecondary.check_for_external_modifications(editorWidget)
            if type(editorWidget) is editor.Editor:
                function = getattr(editorWidget, call_function)
                function(*args, **kwargs)

    def show_start_page(self):
        if not self.is_open("Start Page"):
            startPage = start_page.StartPage(parent=self)
            self.connect(startPage, SIGNAL("openProject(QString)"),
                self.open_project)
            self.connect(startPage, SIGNAL("openPreferences()"),
                lambda: self.emit(SIGNAL("openPreferences()")))
            self.add_tab(startPage, 'Start Page')
        else:
            self.move_to_open("Start Page")

    def show_python_doc(self):
        if sys.platform == 'win32':
            self.docPage = browser_widget.BrowserWidget(
                'http://docs.python.org/')
            self.add_tab(self.docPage, self.tr("Python Documentation"))
        else:
            process = runner.start_pydoc()
            self.docPage = browser_widget.BrowserWidget(process[1], process[0])
            self.add_tab(self.docPage, self.tr("Python Documentation"))

    def editor_jump_to_line(self, lineno=None):
        """Jump to line *lineno* if it is not None
        otherwise ask to the user the line number to jump
        """
        editorWidget = self.get_actual_editor()
        if editorWidget:
            editorWidget.jump_to_line(lineno=lineno)

    def show_follow_mode(self):
        tempTab = self.actualTab
        self.actualTab = self._tabMain
        editorWidget = self.get_actual_editor()
        if not editorWidget:
            return
        if self._tabSecondary.isVisible() and not self._followMode:
            self.show_split(self.orientation())
        if self._followMode:
            self._exit_follow_mode()
        else:
            self._followMode = True
            self.setOrientation(Qt.Horizontal)
            name = self._tabMain.tabText(self._tabMain.currentIndex())
            editor2 = editor.create_editor()
            editor2.setDocument(editorWidget.document())
            self._tabSecondary.add_tab(editor2, name)
            if editorWidget.textModified:
                self._tabSecondary.tab_was_modified(True)
            self._tabSecondary.show()
            editor2.verticalScrollBar().setRange(
                editorWidget._sidebarWidget.highest_line - 2, 0)
            self._tabSecondary.setTabsClosable(False)
            self._tabSecondary.follow_mode = True
            self.setSizes([1, 1])
            self.emit(SIGNAL("enabledFollowMode(bool)"), self._followMode)
        self.actualTab = tempTab

    def _exit_follow_mode(self):
        if self._followMode:
            self._followMode = False
            self._tabSecondary.close_tab()
            self._tabSecondary.hide()
            self._tabSecondary.follow_mode = False
            self._tabSecondary.setTabsClosable(True)
            self.emit(SIGNAL("enabledFollowMode(bool)"), self._followMode)

    def get_opened_documents(self):
        if self._followMode:
            return [self._tabMain.get_documents_data(), []]
        return [self._tabMain.get_documents_data(),
            self._tabSecondary.get_documents_data()]

    def open_files(self, files, mainTab=True, notIDEStart=True):
        if mainTab:
            self.actualTab = self._tabMain
        else:
            self.actualTab = self._tabSecondary
            if files:
                self._tabSecondary.show()
                self.split_visible = True

        for fileData in files:
            if file_manager.file_exists(fileData[0]):
                self.open_file(fileData[0], fileData[1], notStart=notIDEStart)
        self.actualTab = self._tabMain

    def check_for_unsaved_tabs(self):
        return self._tabMain._check_unsaved_tabs() or \
            self._tabSecondary._check_unsaved_tabs()

    def get_unsaved_files(self):
        return self._tabMain.get_unsaved_files() or \
            self._tabSecondary.get_unsaved_files()

    def reset_editor_flags(self):
        for i in range(self._tabMain.count()):
            widget = self._tabMain.widget(i)
            if type(widget) is editor.Editor:
                widget.set_flags()
        for i in range(self._tabSecondary.count()):
            widget = self._tabSecondary.widget(i)
            if type(widget) is editor.Editor:
                widget.set_flags()

    def _specify_syntax(self, widget, syntaxLang):
        if type(widget) is editor.Editor:
            widget.restyle(syntaxLang)

    def apply_editor_theme(self, family, size):
        for i in range(self._tabMain.count()):
            widget = self._tabMain.widget(i)
            if type(widget) is editor.Editor:
                widget.restyle()
                widget.set_font(family, size)
        for i in range(self._tabSecondary.count()):
            widget = self._tabSecondary.widget(i)
            if type(widget) is editor.Editor:
                widget.restyle()
                widget.set_font(family, size)

    def update_editor_margin_line(self):
        for i in range(self._tabMain.count()):
            widget = self._tabMain.widget(i)
            if type(widget) is editor.Editor:
                widget._update_margin_line()
        for i in range(self._tabSecondary.count()):
            widget = self._tabSecondary.widget(i)
            if type(widget) is editor.Editor:
                widget._update_margin_line()

    def open_project(self, path):
        self.emit(SIGNAL("openProject(QString)"), path)

    def close_python_doc(self):
        #close the python document server (if running)
        if self.docPage:
            index = self.actualTab.indexOf(self.docPage)
            self.actualTab.removeTab(index)
            #assign None to the browser
            self.docPage = None

    def close_tab(self):
        """Close the current tab in the current TabWidget."""
        self.actualTab.close_tab()

    def change_tab(self):
        """Change the tab in the current TabWidget."""
        self.actualTab.change_tab()

    def change_tab_reverse(self):
        """Change the tab in the current TabWidget backwards."""
        self.actualTab.change_tab_reverse()

    def show_navigation_buttons(self):
        self.actualTab.navigator.show_menu_navigation()

    def change_split_focus(self):
        if self.actualTab == self._tabMain and self._tabSecondary.isVisible():
            self.actualTab = self._tabSecondary
        else:
            self.actualTab = self._tabMain
        widget = self.actualTab.currentWidget()
        if widget is not None:
            widget.setFocus()

    def shortcut_index(self, index):
        self.actualTab.setCurrentIndex(index)

    def print_file(self):
        """Call the print of ui_tool

        Call print of ui_tool depending on the focus of the application"""
        #TODO: Add funtionality for proyect tab and methods tab
        editorWidget = self.get_actual_editor()
        if editorWidget is not None:
            fileName = "newDocument.pdf"
            if editorWidget.ID:
                fileName = file_manager.get_basename(
                    editorWidget.ID)
                fileName = fileName[:fileName.rfind('.')] + '.pdf'
            ui_tools.print_file(fileName, editorWidget.print_)


#Register MainContainer
MainContainer = _MainContainer()