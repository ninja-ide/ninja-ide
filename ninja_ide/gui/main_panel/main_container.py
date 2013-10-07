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
from PyQt4.QtGui import QStackedLayout
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QFileDialog
from PyQt4.QtGui import QIcon
from PyQt4.QtCore import SIGNAL
#from PyQt4.QtCore import Qt
from PyQt4.QtCore import QDir

from ninja_ide import resources
from ninja_ide import translations
from ninja_ide.core.file_handling import file_manager
from ninja_ide.core import settings
from ninja_ide.gui import dynamic_splitter
from ninja_ide.gui.ide import IDE
from ninja_ide.gui.main_panel import tab_group
from ninja_ide.gui.editor import editor
from ninja_ide.gui.editor import helpers
from ninja_ide.gui.main_panel import actions
from ninja_ide.gui.main_panel import browser_widget
from ninja_ide.gui.main_panel import start_page
from ninja_ide.gui.main_panel import image_viewer
from ninja_ide.gui.main_panel import combo_editor
from ninja_ide.gui.main_panel.helpers import split_orientation
from ninja_ide.gui.dialogs import from_import_dialog
from ninja_ide.tools import locator
from ninja_ide.tools import runner
from ninja_ide.tools import ui_tools

from ninja_ide.tools.logger import NinjaLogger

logger = NinjaLogger('ninja_ide.gui.main_panel.main_container')


class _MainContainer(QWidget):

###############################################################################
# MainContainer SIGNALS
###############################################################################
    """
    beforeFileSaved(QString)
    fileSaved(QString)
    currentEditorChanged(QString)
    locateFunction(QString, QString, bool) [functionName, filePath, isVariable]
    --------openProject(QString)
    openPreferences()
    ---------dontOpenStartPage()
    -------navigateCode(bool, int)
    ----------addBackItemNavigation()
    ----------updateLocator(QString)
    ---------updateFileMetadata()
    findOcurrences(QString)
    --------cursorPositionChange(int, int)    #row, col
    fileOpened(QString)
    newFileOpened(QString)
    --------recentTabsModified(QStringList)
    ---------migrationAnalyzed()
    allTabClosed()
    """
###############################################################################

    def __init__(self, parent=None):
        super(_MainContainer, self).__init__(parent)
        self._parent = parent
        self.stack = QStackedLayout(self)

        self.splitter = dynamic_splitter.DynamicSplitter()
        self.setAcceptDrops(True)

        #documentation browser
        self.docPage = None
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

        self.connect(self, SIGNAL("locateFunction(QString, QString, bool)"),
            self.locate_function)
        #self.connect(self.tabs, SIGNAL("reopenTab(QString)"),
            #self.open_file)
        #self.connect(self.tabs, SIGNAL("syntaxChanged(QWidget, QString)"),
            #self._specify_syntax)
        #self.connect(self.tabs, SIGNAL("allTabsClosed()"),
            #self._main_without_tabs)
        ##reload file
        #self.connect(self.tabs, SIGNAL("reloadFile(QWidget)"),
            #self.reload_file)
        ##for Save on Close operation
        #self.connect(self.tabs, SIGNAL("saveActualEditor()"),
            #self.save_file)
        ##Navigate Code
        #self.connect(self.tabs, SIGNAL("navigateCode(bool, int)"),
            #self.navigate_code_history)
        ## Refresh recent tabs
        #self.connect(self.tabs, SIGNAL("recentTabsModified(QStringList)"),
            #self._recent_files_changed)

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
            'signal_name': 'pep8Activated(bool)',
            'slot': self.reset_pep8_warnings},
            {'target': 'explorer_container',
            'signal_name': 'lintActivated(bool)',
            'slot': self.reset_lint_warnings},
            )

        IDE.register_signals('main_container', connections)

        if settings.SHOW_START_PAGE:
            self.show_start_page()

    def install(self):
        ide = IDE.get_service('ide')
        ide.place_me_on("main_container", self, "central", top=True)

        self.combo_area = combo_editor.ComboEditor(original=True)
        self.splitter.addWidget(self.combo_area)
        self.stack.addWidget(self.splitter)

        self.current_widget = self.combo_area

        ui_tools.install_shortcuts(self, actions.ACTIONS, ide)

    def change_visibility(self):
        """Show/Hide the Main Container area."""
        if self.isVisible():
            self.hide()
        else:
            self.show()

    def expand_file_combo(self):
        self.current_widget.show_combo_file()

    def locate_function(self, function, filePath, isVariable):
        """Move the cursor to the proper position in the navigate stack."""
        editorWidget = self.get_current_editor()
        if editorWidget:
            self.__codeBack.append((editorWidget.nfile.file_path,
                editorWidget.textCursor().position()))
            self.__codeForward = []
        self._locator.navigate_to(function, filePath, isVariable)

    def run_file(self, path):
        self.emit(SIGNAL("runFile(QString)"), path)

    def _add_to_project(self, path):
        self.emit(SIGNAL("addToProject(QString)"), path)

    def paste_history(self):
        """Paste the text from the copy/paste history."""
        editorWidget = self.get_current_editor()
        if editorWidget and editorWidget.hasFocus():
            cursor = editorWidget.textCursor()
            central = IDE.get_service('central_container')
            if central:
                cursor.insertText(central.get_paste())

    def copy_history(self):
        """Copy the selected text into the copy/paste history."""
        editorWidget = self.get_current_editor()
        if editorWidget and editorWidget.hasFocus():
            cursor = editorWidget.textCursor()
            copy = cursor.selectedText()
            central = IDE.get_service('central_container')
            if central:
                central.add_copy(copy)

    def import_from_everywhere(self):
        """Insert an import line from any place in the editor."""
        editorWidget = self.get_current_editor()
        if editorWidget:
            dialog = from_import_dialog.FromImportDialog(editorWidget, self)
            dialog.show()

    def add_back_item_navigation(self):
        """Add an item to the back stack and reset the forward stack."""
        editorWidget = self.get_current_editor()
        if editorWidget:
            self.__codeBack.append((editorWidget.nfile.file_path,
                editorWidget.textCursor().position()))
            self.__codeForward = []

    def preview_in_browser(self):
        """Load the current html file in the default browser."""
        editorWidget = self.get_current_editor()
        if editorWidget:
            if not editorWidget.nfile.file_path:
                self.save_file()
            ext = file_manager.get_file_extension(editorWidget.nfile.file_path)
            if ext == 'html':
                webbrowser.open(editorWidget.ID)

    def add_bookmark_breakpoint(self):
        """Add a bookmark or breakpoint to the current file in the editor."""
        editorWidget = self.get_current_editor()
        if editorWidget and editorWidget.hasFocus():
            if self.current_widget.bar.code_navigator.operation == 1:
                editorWidget._sidebarWidget.set_bookmark(
                    editorWidget.textCursor().blockNumber())
            elif self.current_widget.bar.code_navigator.operation == 2:
                editorWidget._sidebarWidget.set_breakpoint(
                    editorWidget.textCursor().blockNumber())

    def __navigate_with_keyboard(self, val):
        """Navigate between the positions in the jump history stack."""
        op = self.actualTab._tabs.operation
        self.navigate_code_history(val, op)

    def navigate_code_history(self, val, op):
        """Navigate the code history."""
        self.__operations[op](val)

    def _navigate_code_jumps(self, val):
        """Navigate between the jump points."""
        node = None
        if not val and self.__codeBack:
            node = self.__codeBack.pop()
            editorWidget = self.get_current_editor()
            if editorWidget:
                self.__codeForward.append((editorWidget.ID,
                    editorWidget.textCursor().position()))
        elif val and self.__codeForward:
            node = self.__codeForward.pop()
            editorWidget = self.get_current_editor()
            if editorWidget:
                self.__codeBack.append((editorWidget.ID,
                    editorWidget.textCursor().position()))
        if node:
            self.open_file(node[0], node[1])

    def _navigate_breakpoints(self, val):
        """Navigate between the breakpoints."""
        #FIXME: put navigate breakpoints and bookmarks as one method.
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
                lineNumber = settings.BREAKPOINTS[self.__breakpointsFile][0]
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
            self.open_file(self.__breakpointsFile, lineNumber, None, True)
        else:
            settings.BREAKPOINTS.pop(self.__breakpointsFile)
            if settings.BREAKPOINTS:
                self._navigate_breakpoints(val)

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
                lineNumber = settings.BOOKMARKS[self.__bookmarksFile][0]
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
            if settings.BOOKMARKS:
                self._navigate_bookmarks(val)

    def count_file_code_lines(self):
        """Count the lines of code in the current file."""
        editorWidget = self.get_current_editor()
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

    def editor_cut(self):
        editorWidget = self.get_current_editor()
        if editorWidget:
            editorWidget.cut()

    def editor_copy(self):
        editorWidget = self.get_current_editor()
        if editorWidget:
            editorWidget.copy()

    def editor_paste(self):
        editorWidget = self.get_current_editor()
        if editorWidget:
            editorWidget.paste()

    def editor_upper(self):
        editorWidget = self.get_current_editor()
        if editorWidget:
            editorWidget.to_upper()

    def editor_lower(self):
        editorWidget = self.get_current_editor()
        if editorWidget:
            editorWidget.to_lower()

    def editor_title(self):
        editorWidget = self.get_current_editor()
        if editorWidget:
            editorWidget.to_title()

    def editor_go_to_definition(self):
        """Search the definition of the method or variable under the cursor.

        If more than one method or variable is found with the same name,
        shows a table with the results and let the user decide where to go."""
        editorWidget = self.get_current_editor()
        if editorWidget and editorWidget.hasFocus():
            editorWidget.go_to_definition()

    def editor_redo(self):
        """Execute the redo action in the current editor."""
        editorWidget = self.get_current_editor()
        if editorWidget and editorWidget.hasFocus():
            editorWidget.redo()

    def editor_undo(self):
        editorWidget = self.get_current_editor()
        if editorWidget and editorWidget.hasFocus():
            editorWidget.undo()

    def editor_indent_less(self):
        """Indent 1 position to the left for the current line or selection."""
        editorWidget = self.get_current_editor()
        if editorWidget and editorWidget.hasFocus():
            editorWidget.indent_less()

    def editor_indent_more(self):
        """Indent 1 position to the right for the current line or selection."""
        editorWidget = self.get_current_editor()
        if editorWidget and editorWidget.hasFocus():
            editorWidget.indent_more()

    def editor_insert_debugging_prints(self):
        """Insert a print statement in each selected line."""
        editorWidget = self.get_current_editor()
        if editorWidget:
            helpers.insert_debugging_prints(editorWidget)

    def editor_insert_pdb(self):
        """Insert a pdb.set_trace() statement in tjhe current line."""
        editorWidget = self.get_current_editor()
        if editorWidget:
            helpers.insert_pdb(editorWidget)

    def editor_comment(self):
        """Mark the current line or selection as a comment."""
        editorWidget = self.get_current_editor()
        if editorWidget and editorWidget.hasFocus():
            helpers.comment(editorWidget)

    def editor_uncomment(self):
        """Uncomment the current line or selection."""
        editorWidget = self.get_current_editor()
        if editorWidget and editorWidget.hasFocus():
            helpers.uncomment(editorWidget)

    def editor_insert_horizontal_line(self):
        """Insert an horizontal lines of comment symbols."""
        editorWidget = self.get_current_editor()
        if editorWidget and editorWidget.hasFocus():
            helpers.insert_horizontal_line(editorWidget)

    def editor_insert_title_comment(self):
        """Insert a Title surrounded by comment symbols."""
        editorWidget = self.get_current_editor()
        if editorWidget and editorWidget.hasFocus():
            helpers.insert_title_comment(editorWidget)

    def editor_remove_trailing_spaces(self):
        """Remove the trailing spaces in the current editor."""
        editorWidget = self.get_current_editor()
        if editorWidget:
            helpers.remove_trailing_spaces(editorWidget)

    def editor_replace_tabs_with_spaces(self):
        """Replace the Tabs with Spaces in the current editor."""
        editorWidget = self.get_current_editor()
        if editorWidget:
            helpers.replace_tabs_with_spaces(editorWidget)

    def editor_move_up(self):
        """Move the current line or selection one position up."""
        editorWidget = self.get_current_editor()
        if editorWidget and editorWidget.hasFocus():
            helpers.move_up(editorWidget)

    def editor_move_down(self):
        """Move the current line or selection one position down."""
        editorWidget = self.get_current_editor()
        if editorWidget and editorWidget.hasFocus():
            helpers.move_down(editorWidget)

    def editor_remove_line(self):
        """Remove the current line or selection."""
        editorWidget = self.get_current_editor()
        if editorWidget and editorWidget.hasFocus():
            helpers.remove_line(editorWidget)

    def editor_duplicate(self):
        """Duplicate the current line or selection."""
        editorWidget = self.get_current_editor()
        if editorWidget and editorWidget.hasFocus():
            helpers.duplicate(editorWidget)

    def editor_highlight_word(self):
        """Highlight the occurrences of the current word in the editor."""
        editorWidget = self.get_current_editor()
        if editorWidget and editorWidget.hasFocus():
            editorWidget.highlight_selected_word()

    def editor_complete_declaration(self):
        """Do the opposite action that Complete Declaration expect."""
        editorWidget = self.get_current_editor()
        if editorWidget and editorWidget.hasFocus():
            editorWidget.complete_declaration()

    def editor_go_to_line(self, line):
        """Jump to the specified line in the current editor."""
        editorWidget = self.get_current_editor()
        if editorWidget:
            editorWidget.jump_to_line(line)

    def zoom_in_editor(self):
        """Increase the font size in the current editor."""
        editorWidget = self.get_current_editor()
        if editorWidget:
            editorWidget.zoom_in()

    def zoom_out_editor(self):
        """Decrease the font size in the current editor."""
        editorWidget = self.get_current_editor()
        if editorWidget:
            editorWidget.zoom_out()

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

    def _main_without_tabs(self):
        """Notify that there are no more tabs opened."""
        self.emit(SIGNAL("allTabsClosed()"))

    def current_editor_changed(self, filename):
        """Notify the new ID of the current tab."""
        if filename is None:
            filename = translations.TR_NEW_DOCUMENT
        self.emit(SIGNAL("currentEditorChanged(QString)"), filename)

    def change_tabs_visibility(self):
        if self._tabMain.tabBar().isVisible():
            self._tabMain.tabBar().hide()
        else:
            self._tabMain.tabBar().show()

    def show_split(self, orientation):
        pass
        #FIXME: check how we handle this
        #closingFollowMode = self._followMode
        #if self._followMode:
            #self._exit_follow_mode()
        #if self.tabsecondary.isVisible() and \
        #orientation == self.orientation():
            #self.tabsecondary.hide()
            #self.split_visible = False
            #for i in range(self.tabsecondary.count()):
                #widget = self.tabsecondary.widget(0)
                #name = self.tabsecondary.tabText(0)
                #self._tabMain.add_tab(widget, name)
                #if name in self.tabsecondary.titles:
                    #self.tabsecondary.titles.remove(name)
                #if type(widget) is editor.Editor and widget.textModified:
                    #self._tabMain.tab_was_modified(True)
            #self.actualTab = self._tabMain
        #elif not self.tabsecondary.isVisible() and not closingFollowMode:
            #widget = self.get_actual_widget()
            #name = self._tabMain.tabText(self._tabMain.currentIndex())
            #self.tabsecondary.add_tab(widget, name)
            #if name in self._tabMain.titles:
                #self._tabMain.titles.remove(name)
            #if type(widget) is editor.Editor and widget.textModified:
                #self.tabsecondary.tab_was_modified(True)
            #self.tabsecondary.show()
            #self.split_visible = True
            #self.splitter.setSizes([1, 1])
            #self.actualTab = self.tabsecondary
            #self.emit(SIGNAL("currentEditorChanged(QString)"), widget.ID)
        #self.splitter.setOrientation(orientation)

    def add_editor(self, fileName=None, tabIndex=None):
        ninjaide = IDE.get_service('ide')
        editable = ninjaide.get_or_create_editable(fileName)
        editorWidget = editor.create_editor(editable)

        #add the tab
        self.combo_area.add_editor(editable)
        #index = self.add_tab(editorWidget, tab_name, tabIndex=tabIndex)
        #self.tabs.setTabToolTip(index, QDir.toNativeSeparators(fileName))
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
        self.connect(editorWidget,
            SIGNAL("checksFound(QPlainTextEdit, PyQt_PyObject)"),
            self._show_tab_indicator)
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
        pass
        #FIXME: check how we handle this
        #for i in range(self._tabMain.count()):
            #widget = self._tabMain.widget(i)
            #if type(widget) is editor.Editor:
                #project = self._parent.explorer.get_project_given_filename(
                    #widget.ID)
                #widget.set_project(project)

    def reset_pep8_warnings(self, value):
        pass
        #FIXME: check how we handle this
        #for i in range(self._tabMain.count()):
            #widget = self._tabMain.widget(i)
            #if type(widget) is editor.Editor:
                #if value:
                    #widget.syncDocErrorsSignal = True
                    #widget.pep8.check_style()
                #else:
                    #widget.hide_pep8_errors()
        #for i in range(self.tabsecondary.count()):
            #widget = self.tabsecondary.widget(i)
            #if type(widget) is editor.Editor:
                #if value:
                    #widget.syncDocErrorsSignal = True
                    #widget.pep8.check_style()
                #else:
                    #widget.hide_pep8_errors()

    def reset_lint_warnings(self, value):
        pass
        #FIXME: check how we handle this
        #for i in range(self._tabMain.count()):
            #widget = self._tabMain.widget(i)
            #if type(widget) is editor.Editor:
                #if value:
                    #widget.syncDocErrorsSignal = True
                    #widget.errors.check_errors()
                #else:
                    #widget.hide_lint_errors()
        #for i in range(self.tabsecondary.count()):
            #widget = self.tabsecondary.widget(i)
            #if type(widget) is editor.Editor:
                #if value:
                    #widget.syncDocErrorsSignal = True
                    #widget.errors.check_errors()
                #else:
                    #widget.hide_lint_errors()

    def _cursor_position_changed(self, row, col):
        self.emit(SIGNAL("cursorPositionChange(int, int)"), row, col)

    def _find_occurrences(self, word):
        self.emit(SIGNAL("findOcurrences(QString)"), word)

    def _show_tab_indicator(self, editorWidget, icon):
        pass
        #index = self.tabs.indexOf(editorWidget)
        #self.emit(SIGNAL("updateFileMetadata()"))
        #if index >= 0 and icon:
            #if isinstance(icon, int):
                #icon = QIcon(self.style().standardIcon(icon))
            #self.tabs.setTabIcon(index, icon)

    def _hide_icon_tab_indicator(self, editorWidget):
        pass
        #index = self.tabs.indexOf(editorWidget)
        #self.emit(SIGNAL("updateFileMetadata()"))
        #if index >= 0:
            #self.tabs.setTabIcon(index, QIcon())

    def _editor_keyPressEvent(self, event):
        self.emit(SIGNAL("editorKeyPressEvent(QEvent)"), event)

    def _editor_locate_function(self, function, filePath, isVariable):
        self.emit(SIGNAL("locateFunction(QString, QString, bool)"),
            function, filePath, isVariable)

    def _editor_tab_was_modified(self, val=True):
        pass
        #self.tabs.tab_was_modified(val)

    def _editor_tab_was_saved(self, editorWidget=None):
        pass
        #self.tabs.tab_was_saved(editorWidget)
        #self.emit(SIGNAL("updateLocator(QString)"), editorWidget.ID)

    def get_current_widget(self):
        return self.current_widget.currentWidget()

    def get_current_editor(self):
        """Return the Actual Editor or None

        Return an instance of Editor if the Current Tab contains
        an Editor or None if it is not an instance of Editor"""
        widget = self.current_widget.currentWidget()
        if isinstance(widget, editor.Editor):
            return widget
        return None

    def reload_file(self, editorWidget=None):
        if editorWidget is None:
            editorWidget = self.get_current_editor()
        #if editorWidget is not None and editorWidget.ID:
            #fileName = editorWidget.ID
            #old_cursor_position = editorWidget.textCursor().position()
            #old_widget_index = self.tabs.indexOf(editorWidget)
            #self.tabs.removeTab(old_widget_index)
            ##open the file in the same tab as before
            #self.open_file(fileName, tabIndex=old_widget_index)
            ##get the new editor and set the old cursor position
            #editorWidget = self.get_current_editor()
            #cursor = editorWidget.textCursor()
            #cursor.setPosition(old_cursor_position)
            #editorWidget.setTextCursor(cursor)

    def add_tab(self, widget, tabName, tabIndex=None):
        pass
        #return self.tabs.add_tab(widget, tabName, index=tabIndex)

    def open_image(self, fileName):
        try:
            if not self.is_open(fileName):
                viewer = image_viewer.ImageViewer(fileName)
                self.add_tab(viewer, file_manager.get_basename(fileName))
                viewer.ID = fileName
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
                editorWidget = self.get_current_editor()
                ninjaide = IDE.get_service('ide')
                if ninjaide:
                    current_project = ninjaide.get_current_project()
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
                    tabIndex, positionIsLineNumber)

    def __open_file(self, fileName='', cursorPosition=-1,
                    tabIndex=None, positionIsLineNumber=False):
        try:
            if not self.is_open(fileName):
                editorWidget = self.add_editor(fileName, tabIndex=tabIndex)
                if cursorPosition == -1:
                    cursorPosition = 0
                if positionIsLineNumber:
                    editorWidget.go_to_line(cursorPosition)
                else:
                    editorWidget.set_cursor_position(cursorPosition)
            else:
                self.move_to_open(fileName)
                editorWidget = self.get_current_editor()
                if editorWidget and cursorPosition != -1:
                    if positionIsLineNumber:
                        editorWidget.go_to_line(cursorPosition)
                    else:
                        editorWidget.set_cursor_position(cursorPosition)
            self.emit(SIGNAL("currentEditorChanged(QString)"), fileName)
        except file_manager.NinjaIOException as reason:
            QMessageBox.information(self,
                self.tr("The file couldn't be open"), str(reason))
        except Exception as reason:
            logger.error('open_file: %s', reason)

    def is_open(self, filename):
        pass
        #return self.tabs.is_open(filename) != -1

    def move_to_open(self, filename):
        pass
        #FIXME: add in the current split?
        #if self.tabs.is_open(filename) != -1:
            #self.tabs.move_to_open(filename)
        #self.tabs.currentWidget().setFocus()
        #self.emit(SIGNAL("currentEditorChanged(QString)"), filename)

    def move_tab_right(self):
        self._move_tab()

    def move_tab_left(self):
        self._move_tab(forward=False)

    def _move_tab(self, forward=True, widget=None):
        pass
        #if widget is None:
            #widget = self.tabs.currentWidget()
        #if widget is not None:
            #old_widget_index = self.tabs.indexOf(widget)
            #if forward and old_widget_index < self.tabs.count() - 1:
                #new_widget_index = old_widget_index + 1
            #elif old_widget_index > 0 and not forward:
                #new_widget_index = old_widget_index - 1
            #else:
                #return
            #tabName = self.tabs.tabText(old_widget_index)
            #self.tabs.insertTab(new_widget_index, widget, tabName)
            #self.tabs.setCurrentIndex(new_widget_index)

    def get_widget_for_id(self, filename):
        pass
        #widget = None
        #index = self.tabs.is_open(filename)
        #if index != -1:
            #widget = self.tabs.widget(index)
        #return widget

    def change_open_tab_id(self, idname, newId):
        """Search for the Tab with idname, and set the newId to that Tab."""
        pass
        #index = self.tabs.is_open(idname)
        #if index != -1:
            #widget = self.tabs.widget(index)
            #tabName = file_manager.get_basename(newId)
            #self.tabs.change_open_tab_name(index, tabName)
            #widget.ID = newId

    def close_deleted_file(self, idname):
        """Search for the Tab with id, and ask the user if should be closed."""
        pass
        #index = self.tabs.is_open(idname)
        #if index != -1:
            #result = QMessageBox.question(self, self.tr("Close Deleted File"),
                #self.tr("Are you sure you want to close the deleted file?\n"
                        #"The content will be completely deleted."),
                #buttons=QMessageBox.Yes | QMessageBox.No)
            #if result == QMessageBox.Yes:
                #self.tabs.removeTab(index)

    def save_file(self, editorWidget=None):
        #FIXME: check how we handle this
        if not editorWidget:
            editorWidget = self.get_current_editor()
        if not editorWidget:
            return False
        try:
            #editorWidget.just_saved = True
            nfile = editorWidget.nfile
            if nfile.is_new_file or not nfile.has_write_permission():
                return self.save_file_as()

            self.emit(SIGNAL("beforeFileSaved(QString)"), nfile.file_path)
            if settings.REMOVE_TRAILING_SPACES:
                helpers.remove_trailing_spaces(editorWidget)
            content = editorWidget.get_text()
            nfile.save(content)
            #file_manager.store_file_content(
                #fileName, content, addExtension=False)
            encoding = file_manager.get_file_encoding(content)
            editorWidget.encoding = encoding
            self.emit(SIGNAL("fileSaved(QString)"),
                (self.tr("File Saved: %s") % nfile.file_path))
            editorWidget._file_saved()
            return True
        except Exception as reason:
            #editorWidget.just_saved = False
            logger.error('save_file: %s', reason)
            QMessageBox.information(self, self.tr("Save Error"),
                self.tr("The file couldn't be saved!"))
        return False

    def save_file_as(self):
        editorWidget = self.get_current_editor()
        if not editorWidget:
            return False
        nfile = editorWidget.nfile
        try:
            #editorWidget.just_saved = True
            filters = '(*.py);;(*.*)'
            if nfile.file_path:
                ext = file_manager.get_file_extension(nfile.file_path)
                if ext != 'py':
                    filters = '(*.%s);;(*.py);;(*.*)' % ext
            save_folder = self._get_save_folder(nfile.file_path)
            fileName = QFileDialog.getSaveFileName(
                self._parent, self.tr("Save File"), save_folder, filters)
            if not fileName:
                return False

            if settings.REMOVE_TRAILING_SPACES:
                helpers.remove_trailing_spaces(editorWidget)
            #newFile = file_manager.get_file_extension(fileName) == ''
            nfile.save(editorWidget.get_text(), path=fileName)
            print editorWidget.nfile._file_path
            #fileName = file_manager.store_file_content(
                #fileName, editorWidget.get_text(),
                #addExtension=True, newFile=newFile)
            #self.actualTab.setTabText(self.actualTab.currentIndex(),
                #file_manager.get_basename(fileName))
            editorWidget.register_syntax(
                file_manager.get_file_extension(fileName))
            #self._file_watcher.allow_kill = False
            #if editorWidget.ID != fileName:
                #self.remove_standalone_watcher(editorWidget.ID)
            #editorWidget.ID = fileName
            self.emit(SIGNAL("fileSaved(QString)"),
                (self.tr("File Saved: %s") % fileName))
            self.emit(SIGNAL("currentEditorChanged(QString)"), fileName)
            editorWidget._file_saved()
            #self.add_standalone_watcher(fileName)
            #self._file_watcher.allow_kill = True
            return True
        except file_manager.NinjaFileExistsException as ex:
            #editorWidget.just_saved = False
            QMessageBox.information(self, self.tr("File Already Exists"),
                (self.tr("Invalid Path: the file '%s' already exists.") %
                    ex.filename))
        except Exception as reason:
            #editorWidget.just_saved = False
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
        ninjaide = IDE.get_service('ide')
        current_project = ninjaide.get_current_project()
        if current_project:
            return current_project.path
        return os.path.expanduser("~")

    def save_project(self, projectFolder):
        pass
        #FIXME: check how we handle this
        #for i in range(self._tabMain.count()):
            #editorWidget = self._tabMain.widget(i)
            #if type(editorWidget) is editor.Editor and \
            #file_manager.belongs_to_folder(projectFolder, editorWidget.ID):
                #reloaded = self._tabMain.check_for_external_modifications(
                    #editorWidget)
                #if not reloaded:
                    #self.save_file(editorWidget)
        #for i in range(self.tabsecondary.count()):
            #editorWidget = self.tabsecondary.widget(i)
            #if type(editorWidget) is editor.Editor and \
            #file_manager.belongs_to_folder(projectFolder, editorWidget.ID):
                #reloaded = self.tabsecondary.check_for_external_modifications(
                    #editorWidget)
                #if not reloaded:
                    #self.save_file(editorWidget)

    def save_all(self):
        pass
        #FIXME: check how we handle this
        #for i in range(self._tabMain.count()):
            #editorWidget = self._tabMain.widget(i)
            #if type(editorWidget) is editor.Editor:
                #reloaded = self._tabMain.check_for_external_modifications(
                    #editorWidget)
                #if not reloaded:
                    #self.save_file(editorWidget)
        #for i in range(self.tabsecondary.count()):
            #editorWidget = self.tabsecondary.widget(i)
            #self.tabsecondary.check_for_external_modifications(editorWidget)
            #if type(editorWidget) is editor.Editor:
                #reloaded = self.tabsecondary.check_for_external_modifications(
                    #editorWidget)
                #if not reloaded:
                    #self.save_file(editorWidget)

    def call_editors_function(self, call_function, *arguments):
        pass
        #args = arguments[0]
        #kwargs = arguments[1]
        #for i in range(self.tabs.count()):
            #editorWidget = self.tabs.widget(i)
            #if isinstance(editorWidget, editor.Editor):
                #function = getattr(editorWidget, call_function)
                #function(*args, **kwargs)
        #TODO: add other splits

    def show_start_page(self):
        pass
        #if not self.is_open("Start Page"):
            #startPage = start_page.StartPage(parent=self)
            #self.connect(startPage, SIGNAL("openProject(QString)"),
                #self.open_project)
            #self.connect(startPage, SIGNAL("openPreferences()"),
                #lambda: self.emit(SIGNAL("openPreferences()")))
            #self.add_tab(startPage, 'Start Page')
        #else:
            #self.move_to_open("Start Page")

    def show_python_doc(self):
        if sys.platform == 'win32':
            self.docPage = browser_widget.BrowserWidget(
                'http://docs.python.org/')
        else:
            process = runner.start_pydoc()
            self.docPage = browser_widget.BrowserWidget(process[1], process[0])
        self.add_tab(self.docPage, translations.TR_PYTHON_DOC)

    def show_report_bugs(self):
        webbrowser.open(resources.BUGS_PAGE)

    def show_plugins_doc(self):
        bugsPage = browser_widget.BrowserWidget(resources.PLUGINS_DOC, self)
        self.add_tab(bugsPage, translations.TR_HOW_TO_WRITE_PLUGINS)

    def editor_jump_to_line(self, lineno=None):
        """Jump to line *lineno* if it is not None
        otherwise ask to the user the line number to jump
        """
        editorWidget = self.get_current_editor()
        if editorWidget:
            editorWidget.jump_to_line(lineno=lineno)

    def get_opened_documents(self):
        pass
        #return self.tabs.get_documents_data()

    def open_files(self, files):
        for fileData in files:
            if file_manager.file_exists(fileData[0]):
                self.open_file(fileData[0], fileData[1])

    def check_for_unsaved_tabs(self):
        pass
        #return self.tabs._check_unsaved_tabs()

    def get_unsaved_files(self):
        pass
        #return self.tabs.get_unsaved_files()

    def reset_editor_flags(self):
        pass
        #for i in range(self.tabs.count()):
            #widget = self.tabs.widget(i)
            #if isinstance(widget, editor.Editor):
                #widget.set_flags()

    def _specify_syntax(self, widget, syntaxLang):
        if isinstance(widget, editor.Editor):
            widget.restyle(syntaxLang)

    def apply_editor_theme(self, family, size):
        pass
        #for i in range(self.tabs.count()):
            #widget = self.tabs.widget(i)
            #if isinstance(widget, editor.Editor):
                #widget.restyle()
                #widget.set_font(family, size)

    def update_editor_margin_line(self):
        pass
        #for i in range(self.tabs.count()):
            #widget = self.tabs.widget(i)
            #if isinstance(widget, editor.Editor):
                #widget._update_margin_line()

    def open_project(self, path):
        self.emit(SIGNAL("openProject(QString)"), path)

    def close_python_doc(self):
        pass
        #close the python document server (if running)
        #if self.docPage:
            #index = self.tabs.indexOf(self.docPage)
            #self.tabs.removeTab(index)
            ##assign None to the browser
            #self.docPage = None

    def close_tab(self):
        """Close the current tab in the current TabWidget."""
        pass
        #self.tabs.close_tab()

    def change_tab(self):
        """Change the tab in the current TabWidget."""
        pass
        #self.tabs.change_tab()

    def change_tab_reverse(self):
        """Change the tab in the current TabWidget backwards."""
        pass
        #self.tabs.change_tab_reverse()

    def show_navigation_buttons(self):
        pass
        #self.tabs.navigator.show_menu_navigation()

    def change_split_focus(self):
        pass
        #FIXME: check how we handle this
        #if self.actualTab == self._tabMain and self.tabsecondary.isVisible():
            #self.actualTab = self.tabsecondary
        #else:
            #self.actualTab = self._tabMain
        #widget = self.actualTab.currentWidget()
        #if widget is not None:
            #widget.setFocus()

    def shortcut_index(self, index):
        pass
        #self.tabs.setCurrentIndex(index)

    def print_file(self):
        """Call the print of ui_tool

        Call print of ui_tool depending on the focus of the application"""
        #TODO: Add funtionality for proyect tab and methods tab
        editorWidget = self.get_current_editor()
        if editorWidget is not None:
            fileName = "newDocument.pdf"
            if editorWidget.ID:
                fileName = file_manager.get_basename(
                    editorWidget.ID)
                fileName = fileName[:fileName.rfind('.')] + '.pdf'
            ui_tools.print_file(fileName, editorWidget.print_)

    def split_assistance(self):
        dialog = split_orientation.SplitOrientation(self)
        dialog.show()

    def close_split(self):
        pass

    def navigate_back(self):
        self.__navigate_with_keyboard(False)

    def navigate_forward(self):
        self.__navigate_with_keyboard(True)


#Register MainContainer
main = _MainContainer()
