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

from PyQt5 import uic
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QStackedLayout,
    QMessageBox,
    QFileDialog
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import (
    Qt,
    QDir,
    pyqtSignal
)

from ninja_ide import resources
from ninja_ide import translations
from ninja_ide.core.file_handling import file_manager
from ninja_ide.core import settings
from ninja_ide.gui import dynamic_splitter
from ninja_ide.gui.ide import IDE
from ninja_ide.gui.editor import editor
from ninja_ide.gui.editor import helpers
from ninja_ide.gui.main_panel import actions
from ninja_ide.gui.main_panel import main_selector
# from ninja_ide.gui.main_panel import browser_widget
from ninja_ide.gui.main_panel import start_page
from ninja_ide.gui.main_panel import files_handler
from ninja_ide.gui.main_panel import add_file_folder
from ninja_ide.gui.main_panel import image_viewer
from ninja_ide.gui.main_panel import combo_editor
from ninja_ide.gui.main_panel.helpers import split_orientation
# from ninja_ide.gui.dialogs import from_import_dialog
from ninja_ide.tools.locator import (
    # locator,
    locator_widget
)
# from ninja_ide.tools import runner
from ninja_ide.tools import ui_tools

from ninja_ide.tools.logger import NinjaLogger

logger = NinjaLogger('ninja_ide.gui.main_panel.main_container')


class _MainContainer(QWidget):

###############################################################################
# MainContainer SIGNALS
###############################################################################
    """
    newFileOpened(QString)
    allTabClosed()
    runFile(QString)
    addToProject(QString)
    showFileInExplorer(QString)
    recentTabsModified()
    currentEditorChanged(QString)
    fileOpened(QString)
    ---------migrationAnalyzed()
    findOcurrences(QString)
    ---------updateFileMetadata()
    editorKeyPressEvent(QEvent)
    locateFunction(QString, QString, bool) [functionName, filePath, isVariable]
    updateLocator(QString)
    beforeFileSaved(QString)
    fileSaved(QString)
    openPreferences()
    --------openProject(QString)
    ---------dontOpenStartPage()
    """

###############################################################################

    fileOpened = pyqtSignal('QString')
    updateLocator = pyqtSignal('QString')
    currentEditorChanged = pyqtSignal('QString')
    beforeFileSaved = pyqtSignal('QString')
    fileSaved = pyqtSignal('QString')

    def __init__(self, parent=None):
        super(_MainContainer, self).__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        self._parent = parent
        self._vbox = QVBoxLayout(self)
        self._vbox.setContentsMargins(0, 0, 0, 0)
        self._vbox.setSpacing(0)
        self.stack = QStackedLayout()
        self.stack.setStackingMode(QStackedLayout.StackAll)
        self._vbox.addLayout(self.stack)
        self.splitter = dynamic_splitter.DynamicSplitter()
        self.setAcceptDrops(True)
        self._files_handler = files_handler.FilesHandler(self)
        self._add_file_folder = add_file_folder.AddFileFolderWidget(self)

        # documentation browser
        self.docPage = None
        # Code Navigation
        # self._locator = locator.GoToDefinition()
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

        # self.locateFunction['QString',
        #                    'QString',
        #                    bool].connect(self.locate_function)

        IDE.register_service('main_container', self)

        # Register signals connections
        connections = (
            {
                'target': 'main_container',
                'signal_name': 'updateLocator',
                'slot': self._explore_file_code
            },
            {
                'target': 'filesystem',
                'signal_name': 'projectOpened',
                'slot': self._explore_code
            },
            {
                'target': 'projects_explorer',
                'signal_name': 'updateLocator',
                'slot': self._explore_code
            }
        )
        """
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
        {'target': 'filesystem',
            'signal_name': 'projectOpened',
            'slot': self._explore_code},
        {'target': 'main_container',
            'signal_name': 'updateLocator(QString)',
            'slot': self._explore_file_code},
        )
        """

        IDE.register_signals('main_container', connections)

        self.selector = main_selector.MainSelector(self)
        self._opening_dialog = False
        self.add_widget(self.selector)

        if settings.SHOW_START_PAGE:
            self.show_start_page()

        self.selector.changeCurrent[int].connect(self._change_current_stack)
        # self.selector.removeWidget[int].connect(self._remove_item_from_stack)
        # self.selector.ready.connect(self._selector_ready)
        self.selector.animationCompleted.connect(
            self._selector_animation_completed)
        # self.closeDialog['PyQt_PyObject'].connect(self.remove_widget)

    def install(self):
        ide = IDE.get_service('ide')
        ide.place_me_on("main_container", self, "central", top=True)

        self.combo_area = combo_editor.ComboEditor(original=True)
        self.combo_area.allFilesClosed.connect(self._files_closed)
        # self.combo_area.allFilesClosed.connect(self._files_closed)
        self.splitter.add_widget(self.combo_area)
        self.add_widget(self.splitter)

        self.current_widget = self.combo_area
        # Code Locator
        self._code_locator = locator_widget.LocatorWidget(ide)

        ui_tools.install_shortcuts(self, actions.ACTIONS, ide)

    def show_locator(self):
        """Show the locator widget"""

        if not self._code_locator.isVisible():
            self._code_locator.show()

    def _explore_code(self):
        """ Update locator metadata for the current projects """

        self._code_locator.explore_code()

    def _explore_file_code(self, path):
        """ Update locator metadata for the file in path """

        self._code_locator.explore_file_code(path)

    def add_status_bar(self, status):
        self._vbox.addWidget(status)

    @property
    def combo_header_size(self):
        return self.combo_area.bar.height()

    def add_widget(self, widget):
        self.stack.addWidget(widget)

    def remove_widget(self, widget):
        self.stack.removeWidget(widget)

    def _close_dialog(self, widget):
        self.emit(SIGNAL("closeDialog(PyQt_PyObject)"), widget)
        self.disconnect(widget, SIGNAL("finished(int)"),
                        lambda: self._close_dialog(widget))

    def show_dialog(self, widget):
        self._opening_dialog = True
        # self.connect(widget, SIGNAL("finished(int)"),
        #             lambda: self._close_dialog(widget))
        self.setVisible(True)
        self.stack.addWidget(widget)
        self.show_selector()

    def show_selector(self):
        if self.selector != self.stack.currentWidget():
            temp_dir = os.path.join(QDir.tempPath(), "ninja-ide")
            if not os.path.exists(temp_dir):
                os.mkdir(temp_dir)
            collected_data = []
            current = self.stack.currentIndex()
            for index in range(self.stack.count()):
                widget = self.stack.widget(index)
                if widget == self.selector:
                    continue
                pixmap = QWidget.grab(widget, widget.rect())
                path = os.path.join(temp_dir, "screen%s.png" % index)
                pixmap.save(path)
                collected_data.append((index, path))
            self.selector.set_model(collected_data)
            self._selector_ready()
        """
        if self.selector != self.stack.currentWidget():
            temp_dir = os.path.join(QDir.tempPath(), "ninja-ide")
            if not os.path.exists(temp_dir):
                os.mkdir(temp_dir)
            collected_data = []
            current = self.stack.currentIndex()
            for index in range(self.stack.count()):
                widget = self.stack.widget(index)
                if widget == self.selector:
                    continue
                closable = True
                if widget == self.splitter:
                    closable = False
                pixmap = QWidget.grab(widget, widget.rect())
                path = os.path.join(temp_dir, "screen%s.png" % index)
                pixmap.save(path)
                if index == current:
                    self.selector.set_preview(index, path)
                    collected_data.insert(0, (index, path, closable))
                else:
                    collected_data.append((index, path, closable))
            self.selector.set_model(collected_data)
        else:
            self.selector.close_selector()
        """

    def _selector_ready(self):
        print(self.stack.currentWidget())
        self.stack.setCurrentWidget(self.selector)
        print(self.stack.currentWidget())
        self.selector.start_animation()

    def _selector_animation_completed(self):
        if self._opening_dialog:
            # We choose the last one with -2, -1 (for last one) +
            # -1 for the hidden selector widget which is in the stacked too.
            self.selector.open_item(self.stack.count() - 2)
        self._opening_dialog = False

    def _change_current_stack(self, index):
        self.stack.setCurrentIndex(index)

    def _remove_item_from_stack(self, index):
        widget = self.stack.takeAt(index)
        del widget

    def show_editor_area(self):
        self.stack.setCurrentWidget(self.splitter)

    def _files_closed(self):
        if settings.SHOW_START_PAGE:
            self.show_start_page()

    def change_visibility(self):
        """Show/Hide the Main Container area."""
        if self.isVisible():
            self.hide()
        else:
            self.show()

    def expand_symbol_combo(self):
        self.stack.setCurrentWidget(self.splitter)
        self.current_widget.show_combo_symbol()

    def expand_file_combo(self):
        self.stack.setCurrentWidget(self.splitter)
        self.current_widget.show_combo_file()

    def locate_function(self, function, filePath, isVariable):
        """Move the cursor to the proper position in the navigate stack."""
        editorWidget = self.get_current_editor()
        if editorWidget:
            self.__codeBack.append((editorWidget.file_path,
                                   editorWidget.getCursorPosition()))
            self.__codeForward = []
        self._locator.navigate_to(function, filePath, isVariable)

    def run_file(self, path):
        self.emit(SIGNAL("runFile(QString)"), path)

    def _add_to_project(self, path):
        self.emit(SIGNAL("addToProject(QString)"), path)

    def _show_file_in_explorer(self, path):
        self.emit(SIGNAL("showFileInExplorer(QString)"), path)

    def paste_history(self):
        """Paste the text from the copy/paste history."""
        editorWidget = self.get_current_editor()
        if editorWidget and editorWidget.hasFocus():
            line, index = editorWidget.getCursorPosition()
            central = IDE.get_service('central_container')
            if central:
                editorWidget.insertAt(central.get_paste(), line, index)

    def copy_history(self):
        """Copy the selected text into the copy/paste history."""
        editorWidget = self.get_current_editor()
        if editorWidget and editorWidget.hasFocus():
            copy = editorWidget.selectedText()
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
            self.__codeBack.append((editorWidget.file_path,
                                   editorWidget.cursor_position))
            self.__codeForward = []

    def preview_in_browser(self):
        """Load the current html file in the default browser."""
        editorWidget = self.get_current_editor()
        if editorWidget:
            if not editorWidget.file_path:
                self.save_file()
            ext = file_manager.get_file_extension(editorWidget.file_path)
            if ext in ('html', 'shpaml', 'handlebars', 'tpl'):
                webbrowser.open_new_tab(editorWidget.file_path)

    def add_bookmark_breakpoint(self):
        """Add a bookmark or breakpoint to the current file in the editor."""
        editorWidget = self.get_current_editor()
        if editorWidget and editorWidget.hasFocus():
            if self.current_widget.bar.code_navigator.operation == 1:
                editorWidget.handle_bookmarks_breakpoints(
                    editorWidget.getCursorPosition()[0], Qt.ControlModifier)
            elif self.current_widget.bar.code_navigator.operation == 2:
                editorWidget.handle_bookmarks_breakpoints(
                    editorWidget.getCursorPosition()[0], Qt.NoModifier)

    def __navigate_with_keyboard(self, val):
        """Navigate between the positions in the jump history stack."""
        op = self.current_widget.bar.code_navigator.operation
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
                self.__codeForward.append((editorWidget.file_path,
                                          editorWidget.getCursorPosition()))
        elif val and self.__codeForward:
            node = self.__codeForward.pop()
            editorWidget = self.get_current_editor()
            if editorWidget:
                self.__codeBack.append((editorWidget.file_path,
                                                   editorWidget.getCursorPosition()))
        if node:
            filename = node[0]
            line, col = node[1]
            self.open_file(filename, line, col)

    def _navigate_breakpoints(self, val):
        """Navigate between the breakpoints."""
        # FIXME: put navigate breakpoints and bookmarks as one method.
        breakList = list(settings.BREAKPOINTS.keys())
        breakList.sort()
        if not breakList:
            return
        if self.__breakpointsFile not in breakList:
            self.__breakpointsFile = breakList[0]
        index = breakList.index(self.__breakpointsFile)
        breaks = settings.BREAKPOINTS.get(self.__breakpointsFile, [])
        lineNumber = 0
        # val == True: forward
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
        # val == True: forward
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
            # settings.BOOKMARKS.pop(self.__bookmarksFile)
            if settings.BOOKMARKS:
                self._navigate_bookmarks(val)

    def count_file_code_lines(self):
        """Count the lines of code in the current file."""
        editorWidget = self.get_current_editor()
        if editorWidget:
            block_count = editorWidget.lines()
            blanks = re.findall('(^\n)|(^(\s+)?#)|(^( +)?($|\n))',
                                editorWidget.text(), re.M)
            blanks_count = len(blanks)
            resume = self.tr("Lines code: %s\n") % (block_count - blanks_count)
            resume += (self.tr("Blanks and commented lines: %s\n\n") %
                       blanks_count)
            resume += self.tr("Total lines: %s") % blockdget
            msgBox.exec_()

            msgBox = QMessageBox(QMessageBox.Information,
                                 self.tr("Summary of lines"), resume,
                                 QMessageBox.Ok, editorWidget)

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
            helpers.comment_or_uncomment(editorWidget)

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
        """ Jump to the specified line in the current editor. """

        editorWidget = self.get_current_editor()
        if editorWidget:
            editorWidget.go_to_line(line)
            editorWidget.setFocus()

    def zoom_in_editor(self):
        """Increase the font size in the current editor."""

        editorWidget = self.get_current_editor()
        if editorWidget:
            editorWidget.zoom(1.0)

    def zoom_out_editor(self):
        """Decrease the font size in the current editor."""
        editorWidget = self.get_current_editor()
        if editorWidget:
            editorWidget.zoom(-1.0)

    def reset_zoom(self):
        editor_widget = self.get_current_editor()
        if editor_widget is not None:
            editor_widget.reset_zoom()

    def recent_files_changed(self):
        self.emit(SIGNAL("recentTabsModified()"))

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        file_path = event.mimeData().urls()[0].toLocalFile()
        self.open_file(file_path)

    def setFocus(self):
        widget = self.get_current_widget()
        if widget:
            widget.setFocus()

    def current_editor_changed(self, filename):
        """Notify the new filename of the current editor."""
        if filename is None:
            filename = translations.TR_NEW_DOCUMENT
        self.currentEditorChanged.emit(filename)

    def show_split(self, orientation_vertical=False):
        # IDE.select_current(self.current_widget.currentWidget())
        self.current_widget.split_editor(orientation_vertical)

    def add_editor(self, fileName=None, ignore_checkers=False):
        ninjaide = IDE.get_service('ide')
        editable = ninjaide.get_or_create_editable(fileName)
        if editable.editor:
            self.current_widget.set_current(editable)
            return self.current_widget.currentWidget()
        else:
            editable.ignore_checkers = ignore_checkers

        editorWidget = self.create_editor_from_editable(editable)

        # add the tab
        keep_index = (self.splitter.count() > 1 and
                      self.combo_area.stacked.count() > 0)
        self.combo_area.add_editor(editable, keep_index)

        # emit a signal about the file open
        self.fileOpened.emit(fileName)

        if not keep_index:
            self.current_widget.set_current(editable)

        self.stack.setCurrentWidget(self.splitter)

        editorWidget.setFocus()

        return editorWidget

    def create_editor_from_editable(self, editable):
        neditor = editor.create_editor(editable)

        # Connect signals
        neditor.zoomChanged[int].connect(self._show_zoom_indicator)
        neditor.destroyed.connect(self._editor_destroyed)
        editable.fileSaved.connect(self._editor_tab_was_saved)
        neditor.addBackItemNavigation.connect(self.add_back_item_navigation)
        # self.connect(editable, SIGNAL("fileSaved(PyQt_PyObject)"),
        #             self._editor_tab_was_saved)
        # editorWidget.font_changed.connect(self.show_zoom_indicator)
        # self.connect(editorWidget, SIGNAL("openDropFile(QString)"),
        #             self.open_file)
        # self.connect(editorWidget, SIGNAL("addBackItemNavigation()"),
        #             self.add_back_item_navigation)
        # self.connect(editorWidget,
        #             SIGNAL("locateFunction(QString, QString, bool)"),
        #             self._editor_locate_function)
        # self.connect(editorWidget, SIGNAL("findOcurrences(QString)"),
        #             self._find_occurrences)
        # keyPressEventSignal for plugins
        # self.connect(editorWidget, SIGNAL("keyPressEvent(QEvent)"),
        #             self._editor_keyPressEvent)

        return neditor

    def _editor_destroyed(self):
        ui_tools.FadingIndicator.editor_destroyed()

    def _show_zoom_indicator(self, text):
        neditor = self.get_current_editor()
        ui_tools.FadingIndicator.show_text(
            neditor, "Zoom: {}%".format(str(text)))

    def reset_pep8_warnings(self, value):
        pass
        # FIXME: check how we handle this
        # for i in range(self._tabMain.count()):
            # widget = self._tabMain.widget(i)
            # if type(widget) is editor.Editor:
                # if value:
                    # widget.syncDocErrorsSignal = True
                    # widget.pep8.check_style()
                # else:
                    # widget.hide_pep8_errors()

    def reset_lint_warnings(self, value):
        pass
        #FIXME: check how we handle this
        # for i in range(self._tabMain.count()):
            #widget = self._tabMain.widget(i)
            #if type(widget) is editor.Editor:
                #if value:
                    #widget.syncDocErrorsSignal = True
                    #widget.errors.check_errors()
                #else:
                    #widget.hide_lint_errors()

    def show_zoom_indicator(self, text):
        ui_tools.FadingIndicator.show_text(self,
                                           "Zoom: {0}%".format(text))

    def _find_occurrences(self, word):
        self.emit(SIGNAL("findOcurrences(QString)"), word)

    def _editor_keyPressEvent(self, event):
        self.emit(SIGNAL("editorKeyPressEvent(QEvent)"), event)

    def _editor_locate_function(self, function, filePath, isVariable):
        self.emit(SIGNAL("locateFunction(QString, QString, bool)"),
                  function, filePath, isVariable)

    def _editor_tab_was_saved(self, editable=None):
        self.updateLocator.emit(editable.file_path)
        # self.emit(SIGNAL("updateLocator(QString)"), editable.file_path)

    def get_current_widget(self):
        return self.current_widget.currentWidget()

    def get_current_editor(self):
        """Return the Actual Editor or None

        Return an instance of Editor if the Current Tab contains
        an Editor or None if it is not an instance of Editor"""
        widget = self.current_widget.currentWidget()
        if isinstance(widget, editor.NEditor):
            return widget
        return None

    def reload_file(self, editorWidget=None):
        if editorWidget is None:
            editorWidget = self.get_current_editor()
            editorWidget.neditable.reload_file()

    def open_image(self, fileName):
        try:
            if not self.is_open(fileName):
                viewer = image_viewer.ImageViewer(fileName)
                # self.add_tab(viewer, file_manager.get_basename(fileName))
                # viewer.ID = fileName
            else:
                self.move_to_open(fileName)
        except Exception as reason:
            logger.error('open_image: %s', reason)
            QMessageBox.information(self, self.tr("Incorrect File"),
                                    self.tr("The image couldn\'t be open"))

    def open_file(self, filename='', line=-1, col=0, ignore_checkers=False):
        logger.debug("will try to open %s" % filename)
        if not filename:
            logger.debug("has nofilename")
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
                    elif editorWidget is not None and editorWidget.file_path:
                        directory = file_manager.get_folder(
                            editorWidget.file_path)
            extensions = ';;'.join(
                ['{}(*{})'.format(e.upper()[1:], e)
                 for e in settings.SUPPORTED_EXTENSIONS + ['.*', '']])
            fileNames = QFileDialog.getOpenFileNames(self,
                                                     self.tr("Open File"),
                                                     directory,
                                                     extensions)[0]
        else:
            logger.debug("has filename")
            fileNames = [filename]
        if not fileNames:
            return

        for filename in fileNames:
            image_extensions = ('bmp', 'gif', 'jpeg', 'jpg', 'png')
            if file_manager.get_file_extension(filename) in image_extensions:
                logger.debug("will open as image")
                self.open_image(filename)
            elif file_manager.get_file_extension(filename).endswith('ui'):
                logger.debug("will load in ui editor")
                self.w = uic.loadUi(filename)
                self.w.show()
            else:
                logger.debug("will try to open: " + filename)
                self.__open_file(filename, line, col,
                                 ignore_checkers)

    def __open_file(self, fileName='', line=-1, col=0, ignore_checkers=False):
        try:
            editorWidget = self.add_editor(fileName,
                                           ignore_checkers=ignore_checkers)
            if line != -1:
                editorWidget.go_to_line(line, col)
            self.currentEditorChanged.emit(fileName)
        except file_manager.NinjaIOException as reason:
            QMessageBox.information(self,
                                    self.tr("The file couldn't be open"),
                                    str(reason))

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
        # FIXME: check how we handle this
        if not editorWidget:
            editorWidget = self.get_current_editor()
        if editorWidget is None:
            return False
        # Ok, we have an editor instance
        # Save to file only if editor really was modified
        if editorWidget.is_modified:
            try:
                if (editorWidget.nfile.is_new_file or
                        not editorWidget.nfile.has_write_permission()):
                    return self.save_file_as()

                self.beforeFileSaved.emit(editorWidget.file_path)

                if settings.REMOVE_TRAILING_SPACES:
                    helpers.remove_trailing_spaces(editorWidget)
                # New line at end
                # FIXME: from settings
                helpers.insert_block_at_end(editorWidget)
                # Save convent
                editorWidget.neditable.save_content()
                encoding = file_manager.get_file_encoding(editorWidget.text)
                editorWidget.encoding = encoding

                self.fileSaved.emit(
                    self.tr("File Saved: {}".format(editorWidget.file_path)))

                return True
            except Exception as reason:
                logger.error('save_file: %s', reason)
                QMessageBox.information(self, self.tr("Save Error"),
                                        self.tr("The file couldn't be saved!"))
            return False

    def save_file_as(self):
        editorWidget = self.get_current_editor()
        if not editorWidget:
            return False
        try:
            filters = '(*.py);;(*.*)'
            if editorWidget.file_path:  # existing file
                ext = file_manager.get_file_extension(editorWidget.file_path)
                if ext != 'py':
                    filters = '(*.%s);;(*.py);;(*.*)' % ext
            save_folder = self._get_save_folder(editorWidget.file_path)
            fileName = QFileDialog.getSaveFileName(
                self._parent, self.tr("Save File"), save_folder, filters)[0]
            if not fileName:
                return False

            if settings.REMOVE_TRAILING_SPACES:
                helpers.remove_trailing_spaces(editorWidget)

            ext = file_manager.get_file_extension(fileName)
            if not ext:
                fileName = '%s.%s' % (fileName, 'py',)

            editorWidget.neditable.save_content(path=fileName)
            # editorWidget.register_syntax(
            #     file_manager.get_file_extension(fileName))

            self.fileSaved.emit(self.tr("File Saved: {}".format(fileName)))

            self.currentEditorChanged.emit(fileName)

            return True
        except file_manager.NinjaFileExistsException as ex:
            QMessageBox.information(self, self.tr("File Already Exists"),
                                    (self.tr("Invalid Path: the file '%s' "
                                             " already exists.") %
                                    ex.filename))
        except Exception as reason:
            logger.error('save_file_as: %s', reason)
            QMessageBox.information(self, self.tr("Save Error"),
                                    self.tr("The file couldn't be saved!"))
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
            #file_manager.belongs_to_folder(projectFolder,
                    #editorWidget.file_path):
                #reloaded = self._tabMain.check_for_external_modifications(
                    #editorWidget)
                #if not reloaded:
                    #self.save_file(editorWidget)
        #for i in range(self.tabsecondary.count()):
            #editorWidget = self.tabsecondary.widget(i)
            #if type(editorWidget) is editor.Editor and \
            #file_manager.belongs_to_folder(projectFolder,
                    #editorWidget.file_path):
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
        start = self.stack.widget(0)
        if isinstance(start, start_page.StartPage):
            self.stack.setCurrentIndex(0)
        else:
            startPage = start_page.StartPage(parent=self)
            # self.connect(startPage, SIGNAL("openProject(QString)"),
            #             self.open_project)
            # self.connect(startPage, SIGNAL("openPreferences()"),
            #             lambda: self.emit(SIGNAL("openPreferences()")))
            # Connections
            startPage.newFile.connect(self.add_editor)
            self.stack.insertWidget(0, startPage)
            self.stack.setCurrentIndex(0)

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
        #return self.tabs.get_documents_data()
        return []

    def check_for_unsaved_files(self):
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
        # close the python document server (if running)
        # if self.docPage:
        #    index = self.tabs.indexOf(self.docPage)
        #    self.tabs.removeTab(index)
        #    assign None to the browser
        #    self.docPage = None

    def close_file(self):
        self.current_widget.close_current_file()

    def create_file(self, base_path, project_path):
        self._add_file_folder.create_file(base_path, project_path)

    def create_folder(self, base_path, project_path):
        self._add_file_folder.create_folder(base_path, project_path)

    def change_tab(self):
        """Change the tab in the current TabWidget."""
        self.stack.setCurrentWidget(self.splitter)
        # self._files_handler.next_item()

    def change_tab_reverse(self):
        """Change the tab in the current TabWidget backwards."""
        self.stack.setCurrentWidget(self.splitter)
        # self._files_handler.previous_item()

    def toggle_tabs_and_spaces(self):
        """Toggle Show/Hide Tabs and Spaces"""

        settings.SHOW_TABS_AND_SPACES = not settings.SHOW_TABS_AND_SPACES
        qsettings = IDE.ninja_settings()
        qsettings.setValue('preferences/editor/show_tabs_and_spaces',
                           settings.SHOW_TABS_AND_SPACES)
        neditor = self.get_current_editor()
        if neditor is not None:
            neditor.show_whitespaces = settings.SHOW_TABS_AND_SPACES

    def show_navigation_buttons(self):
        """Show Navigation menu."""
        self.stack.setCurrentWidget(self.splitter)
        self.combo_area.show_menu_navigation()

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
            if editorWidget.file_path:
                fileName = file_manager.get_basename(
                    editorWidget.file_path)
                fileName = fileName[:fileName.rfind('.')] + '.pdf'
            ui_tools.print_file(fileName, editorWidget.print_)

    def split_assistance(self):
        dialog = split_orientation.SplitOrientation(self)
        dialog.show()

    # def close_split(self):
    #    if self.current_widget != self.combo_area:
    #        self.current_widget.bar.close_split()

    # def split_vertically(self):
    #    self.show_split(False)

    # def split_horizontally(self):
    #    self.show_split(True)

    def navigate_back(self):
        self.__navigate_with_keyboard(False)

    def navigate_forward(self):
        self.__navigate_with_keyboard(True)


# Register MainContainer
main = _MainContainer()
