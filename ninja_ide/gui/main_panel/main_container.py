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

from PyQt4 import uic
from PyQt4.QtGui import QSplitter
from PyQt4.QtGui import QStyle
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QFileDialog
from PyQt4.QtGui import QIcon
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QDir

from ninja_ide import resources
from ninja_ide.core import file_manager
from ninja_ide.core import settings
from ninja_ide.core.filesystem_notifications import NinjaFileSystemWatcher
from ninja_ide.gui.main_panel import tab_widget
from ninja_ide.gui.editor import editor
from ninja_ide.gui.editor import highlighter
from ninja_ide.gui.editor import helpers
from ninja_ide.gui.main_panel import browser_widget
from ninja_ide.gui.main_panel import start_page
from ninja_ide.gui.main_panel import image_viewer
from ninja_ide.tools import runner

from ninja_ide.tools.logger import NinjaLogger

logger = NinjaLogger('ninja_ide.gui.main_panel.main_container')

__mainContainerInstance = None


def MainContainer(*args, **kw):
    global __mainContainerInstance
    if __mainContainerInstance is None:
        __mainContainerInstance = __MainContainer(*args, **kw)
    return __mainContainerInstance


class __MainContainer(QSplitter):

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
        QSplitter.__init__(self, parent)
        self._parent = parent
        self._tabMain = tab_widget.TabWidget(self)
        self._tabSecondary = tab_widget.TabWidget(self)
        self.setAcceptDrops(True)
        self.addWidget(self._tabMain)
        self.addWidget(self._tabSecondary)
        self.setSizes([1, 1])
        self._tabSecondary.hide()
        self.actualTab = self._tabMain
        self._followMode = False
        self.splitted = False
        highlighter.restyle(resources.CUSTOM_SCHEME)
        #documentation browser
        self.docPage = None
        # File Watcher
        self._file_watcher = NinjaFileSystemWatcher
        self._watched_simple_files = []

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

    def _navigate_code(self, val, op):
        self.emit(SIGNAL("navigateCode(bool, int)"), val, op)

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
            self.splitted = False
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
            self.splitted = True
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
            lambda: self.emit(SIGNAL("addBackItemNavigation()")))
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

    def get_widget_for_path(self, filename):
        if self._tabMain.is_open(filename) != -1:
            index = self._tabMain.search_for_identifier_index(filename)
            return self._tabMain.widget(index)
        elif self._tabSecondary.is_open(filename) != -1:
            index = self._tabSecondary.search_for_identifier_index(filename)
            return self._tabSecondary.widget(index)
        return None

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
                self.splitted = True

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
