# -*- coding: utf-8 -*-
from __future__ import absolute_import

import sys
import os
import logging

from PyQt4 import uic
from PyQt4.QtGui import QSplitter
from PyQt4.QtGui import QStyle
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QFileDialog
from PyQt4.QtGui import QIcon
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import Qt

from ninja_ide import resources
from ninja_ide.core import file_manager
from ninja_ide.core import settings
from ninja_ide.gui.main_panel import tab_widget
from ninja_ide.gui.editor import editor
from ninja_ide.gui.editor import highlighter
from ninja_ide.gui.editor import helpers
from ninja_ide.gui.main_panel import browser_widget
from ninja_ide.gui.main_panel import image_viewer
from ninja_ide.tools import runner


logger = logging.getLogger('ninja_ide.gui.main_panel.main_container')

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
    """
###############################################################################

    def __init__(self, parent=None):
        QSplitter.__init__(self, parent)
        self._parent = parent
        self._tabMain = tab_widget.TabWidget(self)
        self._tabSecondary = tab_widget.TabWidget(self)
        self.addWidget(self._tabMain)
        self.addWidget(self._tabSecondary)
        self.setSizes([1, 1])
        self._tabSecondary.hide()
        self.actualTab = self._tabMain
        self._followMode = False
        self.splitted = False
        self._workingDirectory = ''
        highlighter.restyle(resources.CUSTOM_SCHEME)
        #documentation browser
        self.docPage = None

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
        self.connect(self._tabMain, SIGNAL("reloadFile()"), self.reload_file)
        self.connect(self._tabSecondary, SIGNAL("reloadFile()"),
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

    def _navigate_code(self, val, op):
        self.emit(SIGNAL("navigateCode(bool, int)"), val, op)

    def _main_without_tabs(self):
        if self._tabSecondary.isVisible():
            self.show_split(self.orientation())

    def _secondary_without_tabs(self):
        self.show_split(self.orientation())

    def _reopen_last_tab(self, tab, path):
        self.actualTab = tab
        self.open_file(unicode(path))

    def _change_actual(self, tabWidget):
        if not self._followMode:
            self.actualTab = tabWidget

    def _current_tab_changed(self, index):
        if self.actualTab.widget(index):
            self.emit(SIGNAL("currentTabChanged(QString)"),
                self.actualTab.widget(index)._id)

    def split_tab(self, orientationHorizontal):
        if orientationHorizontal:
            self.show_split(Qt.Horizontal)
        else:
            self.show_split(Qt.Vertical)

    def _split_this_tab(self, tab, index, orientationHorizontal):
        tab.setCurrentIndex(index)
        if orientationHorizontal:
            self.show_split(Qt.Horizontal)
        else:
            self.show_split(Qt.Vertical)

    def show_split(self, orientation):
        closingFollowMode = self._followMode
        if self._followMode:
            self.show_follow_mode()
        if self._tabSecondary.isVisible() and \
        orientation == self.orientation():
            self._tabSecondary.hide()
            self.splitted = False
            for i in xrange(self._tabSecondary.count()):
                widget = self._tabSecondary.widget(0)
                name = unicode(self._tabSecondary.tabText(0))
                self._tabMain.add_tab(widget, name)
                if name in self._tabSecondary.titles:
                    self._tabSecondary.titles.remove(name)
                if type(widget) is editor.Editor and widget.textModified:
                    self._tabMain.tab_was_modified(True)
            self.actualTab = self._tabMain
        elif not self._tabSecondary.isVisible() and not closingFollowMode:
            widget = self.get_actual_widget()
            name = unicode(self._tabMain.tabText(self._tabMain.currentIndex()))
            self._tabSecondary.add_tab(widget, name)
            if name in self._tabMain.titles:
                self._tabMain.titles.remove(name)
            if type(widget) is editor.Editor and widget.textModified:
                self._tabSecondary.tab_was_modified(True)
            self._tabSecondary.show()
            self.splitted = True
            self.setSizes([1, 1])
            self.actualTab = self._tabSecondary
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
        content=None, syntax=None):
        editorWidget = editor.create_editor(fileName=fileName, project=project,
            syntax=syntax)

        if not fileName:
            tabName = "New Document"
        else:
            tabName = file_manager.get_basename(fileName)

        #add the tab
        inserted_index = self.add_tab(editorWidget, tabName, tabIndex=tabIndex)
        self.actualTab.setTabToolTip(inserted_index, fileName)
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
        #Cursor position changed
        self.connect(editorWidget, SIGNAL("cursorPositionChange(int, int)"),
            self._cursor_position_changed)
        #keyPressEventSignal for plugins
        self.connect(editorWidget, SIGNAL("keyPressEvent(QEvent)"),
            self._editor_keyPressEvent)

        #insert the content if present
        if content:
            editorWidget.setPlainText(content)
        #emit a signal about the file open
        self.emit(SIGNAL("fileOpened(QString)"), fileName)

        return editorWidget

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

    def reload_file(self):
        editorWidget = self.get_actual_editor()
        if type(editorWidget) is editor.Editor and editorWidget.ID:
            fileName = editorWidget.ID
            old_cursor_position = editorWidget.textCursor().position()
            old_widget_index = self.actualTab.currentIndex()
            self.actualTab.close_tab()
            #open the file in the same tab as before
            self.open_file(fileName, tabIndex=old_widget_index)
            #get the new editor and set the old cursor position
            editorWidget = self.get_actual_editor()
            cursor = editorWidget.textCursor()
            cursor.setPosition(old_cursor_position)
            editorWidget.setTextCursor(cursor)

    def open_image(self, fileName):
        try:
            if not self.is_open(fileName):
                viewer = image_viewer.ImageViewer(fileName)
                self.add_tab(viewer, file_manager.get_basename(fileName))
                viewer.id = fileName
            else:
                self.move_to_open(fileName)
        except Exception, reason:
            logger.error('open_image: %s', reason)
            QMessageBox.information(self, self.tr("Incorrect File"),
                self.tr("The image couldn\'t be open"))

    def open_file(self, fileName='', cursorPosition=0,\
                    tabIndex=None, positionIsLineNumber=False, notStart=True):
        fileName = unicode(fileName)
        if not fileName:
            if settings.WORKSPACE:
                directory = settings.WORKSPACE
            else:
                directory = self._workingDirectory
            extensions = ';;'.join(
                ['(*%s)' % e for e in \
                    settings.SUPPORTED_EXTENSIONS + ['.*', '']])
            fileName = unicode(QFileDialog.getOpenFileName(self,
                self.tr("Open File"), directory, extensions))
        if not fileName:
            return
        self._workingDirectory = os.path.dirname(fileName)

        if file_manager.get_file_extension(fileName) in ('jpg', 'png'):
            self.open_image(fileName)
        elif file_manager.get_file_extension(fileName).endswith('ui'):
            self.w = uic.loadUi(fileName)
            self.w.show()
        else:
            self.__open_file(fileName, cursorPosition,
                tabIndex, positionIsLineNumber, notStart)

    def __open_file(self, fileName='', cursorPosition=0,\
                    tabIndex=None, positionIsLineNumber=False, notStart=True):
        try:
            if not self.is_open(fileName):
                self.actualTab.notOpening = False
                content = file_manager.read_file_content(fileName)
                editorWidget = self.add_editor(fileName, tabIndex=tabIndex,
                    content=content)
                editorWidget.ID = fileName
                encoding = file_manager._search_coding_line(content)
                editorWidget.encoding = encoding
                if not positionIsLineNumber:
                    editorWidget.set_cursor_position(cursorPosition)
                else:
                    editorWidget.go_to_line(cursorPosition)

                if not editorWidget.has_write_permission():
                    fileName += unicode(self.tr(" (Read-Only)"))
                    index = self.actualTab.currentIndex()
                    self.actualTab.setTabText(index, fileName)
            else:
                self.move_to_open(fileName)
                editorWidget = self.get_actual_editor()
                if editorWidget:
                    if positionIsLineNumber:
                        editorWidget.go_to_line(cursorPosition)
                    else:
                        editorWidget.set_cursor_position(cursorPosition)
            self.emit(SIGNAL("currentTabChanged(QString)"), fileName)
        except file_manager.NinjaIOException, reason:
            if not notStart:
                QMessageBox.information(self,
                    self.tr("The file couldn't be open"),
                    unicode(reason))
        except Exception, reason:
            logger.error('open_file: %s', reason)
        self.actualTab.notOpening = True

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
            editorWidget.ID = fileName
            encoding = file_manager._search_coding_line(content)
            editorWidget.encoding = encoding
            self.emit(SIGNAL("fileSaved(QString)"),
                self.tr("File Saved: %1").arg(fileName))
            editorWidget._file_saved()
            return True
        except Exception, reason:
            logger.error('save_file: %s', reason)
            QMessageBox.information(self, self.tr("Save Error"),
                self.tr("The file couldn't be saved!"))
        return False

    def save_file_as(self):
        editorWidget = self.get_actual_editor()
        if not editorWidget:
            return False
        try:
            filter = '(*.py);;(*.*)'
            if editorWidget.ID:
                ext = file_manager.get_file_extension(editorWidget.ID)
                if ext != 'py':
                    filter = '(*.%s);;(*.py);;(*.*)' % ext
            fileName = unicode(QFileDialog.getSaveFileName(
                self._parent, self.tr("Save File"), editorWidget.ID, filter))
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
            editorWidget.ID = fileName
            self.emit(SIGNAL("fileSaved(QString)"),
                self.tr("File Saved: %1").arg(fileName))
            editorWidget._file_saved()
            return True
        except file_manager.NinjaFileExistsException, ex:
            QMessageBox.information(self, self.tr("File Already Exists"),
                self.tr("Invalid Path: the file '%s' already exists." % \
                    ex.filename))
        except Exception, reason:
            logger.error('save_file_as: %s', reason)
            QMessageBox.information(self, self.tr("Save Error"),
                self.tr("The file couldn't be saved!"))
            self.actualTab.setTabText(self.actualTab.currentIndex(),
                self.tr("New Document"))
        return False

    def save_project(self, projectFolder):
        for i in xrange(self._tabMain.count()):
            editorWidget = self._tabMain.widget(i)
            if type(editorWidget) is editor.Editor and \
            file_manager.belongs_to_folder(projectFolder, editorWidget.ID):
                self.save_file(editorWidget)
        for i in xrange(self._tabSecondary.count()):
            editorWidget = self._tabSecondary.widget(i)
            if type(editorWidget) is editor.Editor and \
            file_manager.belongs_to_folder(projectFolder, editorWidget.ID):
                self.save_file(editorWidget)

    def save_all(self):
        for i in xrange(self._tabMain.count()):
            editorWidget = self._tabMain.widget(i)
            if type(editorWidget) is editor.Editor:
                self.save_file(editorWidget)
        for i in xrange(self._tabSecondary.count()):
            editorWidget = self._tabSecondary.widget(i)
            if type(editorWidget) is editor.Editor:
                self.save_file(editorWidget)

    def show_start_page(self):
        startPage = browser_widget.BrowserWidget(
            resources.START_PAGE_URL, parent=self)
        self.connect(startPage, SIGNAL("openProject(QString)"),
            self.open_project)

        #Signals Wrapper
        def emit_start_page_signals(opt):
            if opt:
                self.emit(SIGNAL("openPreferences()"))
            else:
                self.emit(SIGNAL("dontOpenStartPage()"))
        self.connect(startPage, SIGNAL("openPreferences()"),
            lambda: emit_start_page_signals(True))
        self.connect(startPage, SIGNAL("dontOpenStartPage()"),
            lambda: emit_start_page_signals(False))
        self.add_tab(startPage, 'Start Page')

    def show_python_doc(self):
        if sys.platform == 'win32':
            self.docPage = browser_widget.BrowserWidget('http://pydoc.org/')
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
            self._followMode = False
            self._tabSecondary.close_tab()
            self._tabSecondary.hide()
            self._tabSecondary.setTabsClosable(True)
            self._tabMain._follow_mode = False
            self._tabSecondary._follow_mode = False
        else:
            #check if is instance of Editor
            self._followMode = True
            self.setOrientation(Qt.Horizontal)
            name = unicode(self._tabMain.tabText(self._tabMain.currentIndex()))
            editor2 = editor.create_editor(fileName=name)
            editor2.setPlainText(editorWidget.get_text())
            editor2.setReadOnly(True)
            self._tabSecondary.add_tab(editor2, name)
            if editorWidget.textModified:
                self._tabSecondary.tab_was_modified(True)
            self._tabMain._follow_mode = True
            self._tabSecondary._follow_mode = True
            self._tabSecondary.show()
            editor2.verticalScrollBar().setRange(
                editorWidget._sidebarWidget.highest_line - 2, 0)
            self._tabSecondary.setTabsClosable(False)
            self.setSizes([1, 1])
        self.actualTab = tempTab
        self.emit(SIGNAL("enabledFollowMode(bool)"), self._followMode)

    def _exit_follow_mode(self):
        if self._followMode:
            self.show_follow_mode()

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

        for fileData in files:
            if file_manager.file_exists(unicode(fileData[0])):
                self.open_file(unicode(fileData[0]),
                    fileData[1], notIDEStart)
        self.actualTab = self._tabMain

    def check_for_unsaved_tabs(self):
        return self._tabMain._check_unsaved_tabs() or \
            self._tabSecondary._check_unsaved_tabs()

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
        for i in xrange(self._tabMain.count()):
            widget = self._tabMain.widget(i)
            if type(widget) is editor.Editor:
                widget.restyle()
                widget.set_font(family, size)
        for i in xrange(self._tabSecondary.count()):
            widget = self._tabSecondary.widget(i)
            if type(widget) is editor.Editor:
                widget.restyle()
                widget.set_font(family, size)

    def open_project(self, path):
        self.emit(SIGNAL("openProject(QString)"), path)

    def close_python_doc(self):
        #close the python document server (if running)
        if self.docPage:
            index = self.actualTab.indexOf(self.docPage)
            self.actualTab.removeTab(index)
            #assign None to the browser
            self.docPage = None
