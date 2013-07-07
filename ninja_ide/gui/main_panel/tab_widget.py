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

from PyQt4.QtGui import QTabWidget
from PyQt4.QtGui import QCursor
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QMenu
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QApplication
from PyQt4.QtGui import QClipboard
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QDir

from ninja_ide import resources
from ninja_ide.core import settings
from ninja_ide.core import file_manager
from ninja_ide.core.filesystem_notifications.base_watcher import MODIFIED, \
                                                                DELETED
from ninja_ide.core.filesystem_notifications import NinjaFileSystemWatcher
from ninja_ide.gui.editor import editor
from ninja_ide.gui.main_panel import browser_widget

from ninja_ide.tools.logger import NinjaLogger

logger = NinjaLogger('ninja_ide.gui.main_panel.tab_widget')
DEBUG = logger.debug


class TabWidget(QTabWidget):

###############################################################################
# TabWidget SIGNALS
###############################################################################
    """
    tabCloseRequested(int)
    dropTab(QTabWidget)
    saveActualEditor()
    allTabsClosed()
    changeActualTab(QTabWidget)
    splitTab(QTabWidget, int, bool)
    reopenTab(QTabWidget, QString)
    runFile()
    addToProject(QString)
    syntaxChanged(QWidget, QString)
    reloadFile(QWidget)
    navigateCode(bool, int)
    recentTabsModified(QStringList)
    """
###############################################################################

    def __init__(self, parent):
        QTabWidget.__init__(self, parent)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setAcceptDrops(True)
        self.notOpening = True
        self.__lastOpened = []
        self._resyntax = []
        self.navigator = TabNavigator()
        self.setCornerWidget(self.navigator, Qt.TopRightCorner)
        self._parent = parent
        self.follow_mode = False
        self._change_map = {}
        #On some platforms there are problem with focusInEvent
        self.question_already_open = False
        #Keep track of the tab titles
        self.titles = []
        self.dontLoopInExpandTitle = False
        self.connect(NinjaFileSystemWatcher,
            SIGNAL("fileChanged(int, QString)"), self._file_changed)
        self.connect(self, SIGNAL("tabCloseRequested(int)"), self.removeTab)
        self.connect(self.navigator.btnPrevious, SIGNAL("clicked()"),
            lambda: self._navigate_code(False))
        self.connect(self.navigator.btnNext, SIGNAL("clicked()"),
            lambda: self._navigate_code(True))

    def get_recent_files_list(self):
        return self.__lastOpened

    def _navigate_code(self, val):
        op = self.navigator.operation
        self.emit(SIGNAL("navigateCode(bool, int)"), val, op)

    def _add_to_last_opened(self, path):
        if path not in self.__lastOpened:
            self.__lastOpened.append(path)
            if len(self.__lastOpened) > settings.MAX_REMEMBER_TABS:
                self.__lastOpened = self.__lastOpened[1:]
            self.emit(SIGNAL("recentTabsModified(QStringList)"),
                self.__lastOpened)

    def add_tab(self, widget, title, index=None):
        try:
            if index is not None:
                inserted_index = self.insertTab(index, widget, title)
            else:
                inserted_index = self.addTab(widget, title)
            self.setCurrentIndex(inserted_index)
            self.expand_tab_name(title)
            widget.setFocus()
            return inserted_index
        except AttributeError as reason:
            msg = "Widget couldn't be added, doesn't inherit from ITabWidget"
            logger.error('add_tab: %s', reason)
            logger.error(msg)

    def expand_tab_name(self, title):
        """Expand the tab title to differentiate files with the same name.

        The way it is currently implemented, it will only change the first
        conflicting title passed in, because it only searches until the new
        title isn't in the tab titles.
        """
        if title == 'New Document':
            return
        elif title not in self.titles:
            self.titles.append(title)
            return
        indexes = [i for i in range(self.count())
            if type(self.widget(i)) is editor.Editor and
            self.tabText(i) == title and
            self.widget(i).ID]  # self.widget.ID returns the basename
        self.dontLoopInExpandTitle = True
        for i in indexes:
            newName = file_manager.create_path(
                file_manager.get_basename(
                    file_manager.get_folder(self.widget(i).ID)), title)
            while newName in self.titles:
                # Keep prepending the folder name onto the title until it
                # does not conflict.
                path = self.widget(i).ID
                tempDir = path[:path.rfind(newName)]
                newName = file_manager.create_path(
                    file_manager.get_basename(
                        file_manager.get_folder(tempDir)),
                    '..',
                    title)
            self.titles.append(newName)
            self.setTabText(i, newName)
        self.dontLoopInExpandTitle = False

    def tab_was_modified(self, val):
        ed = self.currentWidget()
        text = self.tabBar().tabText(self.currentIndex())
        if type(ed) is editor.Editor and self.notOpening and val and \
           not text.startswith('(*) '):
            ed.textModified = True
            text = '(*) %s' % self.tabBar().tabText(self.currentIndex())
            self.tabBar().setTabText(self.currentIndex(), text)

    def focusInEvent(self, event):
        QTabWidget.focusInEvent(self, event)
        self.emit(SIGNAL("changeActualTab(QTabWidget)"), self)

        #custom behavior after the default
        editorWidget = self.currentWidget()
        if not editorWidget:
            return
        #Check never saved
        if editorWidget.newDocument:
            return
        #Check external modifications!
        self.check_for_external_modifications(editorWidget)
        #we can ask again
        self.question_already_open = False

    def _prompt_reload(self, editorWidget, change):
        self.question_already_open = True
        if change == MODIFIED:
            if editorWidget.just_saved:
                editorWidget.just_saved = False
                return
            val = QMessageBox.question(self, 'The file has changed on disk!',
                (self.tr("%s\nDo you want to reload it?") % editorWidget.ID),
                QMessageBox.Yes, QMessageBox.No)
            if val == QMessageBox.Yes:
                self.emit(SIGNAL("reloadFile(QWidget)"), editorWidget)
            else:
                #dont ask again while the current file is open
                editorWidget.ask_if_externally_modified = False
        elif change == DELETED:
                val = QMessageBox.information(self,
                            'The file has been deleted from disk!',
                (self.tr("%s\n") % editorWidget.ID),
                QMessageBox.Yes)
        self.question_already_open = False

    def _file_changed(self, change_type, file_path):
        file_path = QDir.toNativeSeparators(file_path)
        editorWidget = self.currentWidget()
        current_open = QDir.toNativeSeparators(editorWidget and
                                                    editorWidget.ID or "")
        opened = [path for path, _ in self.get_documents_data()]

        if (file_path in opened) and \
            ((not editorWidget) or (current_open != file_path)) and \
            (change_type in (MODIFIED, DELETED)):

            self._change_map.setdefault(file_path,
                                        []).append(change_type)
        elif not editorWidget:
            return
        elif (current_open == file_path) and \
            (not self.question_already_open):
            #dont ask again if you are already asking!
            self._prompt_reload(editorWidget, change_type)

    def check_for_external_modifications(self, editorWidget):
        e_path = editorWidget.ID
        if e_path in self._change_map:
            if DELETED in self._change_map[e_path]:
                self._prompt_reload(editorWidget, DELETED)
            else:
                self._prompt_reload(editorWidget, MODIFIED)
            self._change_map.pop(e_path)

    def tab_was_saved(self, ed):
        index = self.indexOf(ed)
        text = self.tabBar().tabText(index)
        if text.startswith('(*) '):
            text = text[4:]
        self.tabBar().setTabText(index, text)

    def is_open(self, identifier):
        """Check if a Tab with id = identifier is open"""
        for i in range(self.count()):
            if self.widget(i) == identifier:
                return i
        return -1

    def move_to_open(self, identifier):
        """Set the selected Tab for the widget with id = identifier"""
        for i in range(self.count()):
            if self.widget(i) == identifier:
                self.setCurrentIndex(i)
                return

    def search_for_identifier_index(self, identifier):
        for i in range(self.count()):
            if self.widget(i) == identifier:
                return i

    def remove_title(self, index):
        """Looks for the title of the tab at index and removes it from
        self.titles, if it's there.'"""
        if self.tabText(index) in self.titles:
            self.titles.remove(self.tabText(index))

    def update_current_widget(self):
        """Sets the focus to the current widget. If this is the last tab in the
        current split, the allTabsClosed() signal is emitted.'"""
        if self.currentWidget() is not None:
            self.currentWidget().setFocus()
        else:
            self.emit(SIGNAL("allTabsClosed()"))

    def removeTab(self, index):
        """Remove the Tab at the selected index and check if the
        widget was modified and need to execute any saving"""
        if index != -1:
            self.setCurrentIndex(index)
            widget = self.currentWidget()
            if type(widget) is editor.Editor:
                val = QMessageBox.No
                if widget.textModified and not self.follow_mode:
                    fileName = self.tabBar().tabText(self.currentIndex())
                    val = QMessageBox.question(
                        self, (self.tr('The file %s was not saved') %
                            fileName),
                            self.tr("Do you want to save before closing?"),
                            QMessageBox.Yes | QMessageBox.No |
                            QMessageBox.Cancel)
                if val == QMessageBox.Cancel:
                    return
                elif val == QMessageBox.Yes:
                    self.emit(SIGNAL("saveActualEditor()"))
                    if widget.textModified:
                        return
            if type(widget) == browser_widget.BrowserWidget:
                widget.shutdown_pydoc()
            elif type(widget) is editor.Editor and widget.ID:
                self._add_to_last_opened(widget.ID)
                self._parent.remove_standalone_watcher(widget.ID)
                widget.completer.cc.unload_module()

            self.remove_title(index)
            super(TabWidget, self).removeTab(index)
            del widget
            self.update_current_widget()

    def setTabText(self, index, text):
        QTabWidget.setTabText(self, index, text)
        if text in self.titles and not self.dontLoopInExpandTitle:
            self.expand_tab_name(text)

    def close_tab(self):
        self.removeTab(self.currentIndex())

    def get_documents_data(self):
        """Return Editors: path, project, cursor position"""
        files = []
        for i in range(self.count()):
            if (type(self.widget(i)) is editor.Editor) \
            and self.widget(i).ID != '':
                files.append([self.widget(i).ID,
                    self.widget(i).get_cursor_position()])
                self.widget(i)._sidebarWidget._save_breakpoints_bookmarks()
        return files

    def mousePressEvent(self, event):
        QTabWidget.mousePressEvent(self, event)
        if self.follow_mode:
            return
        if event.button() == Qt.RightButton:
            index = self.tabBar().tabAt(event.pos())
            self.setCurrentIndex(index)
            widget = self.widget(index)
            if type(widget) is editor.Editor:
                #show menu
                menu = QMenu()
                actionAdd = menu.addAction(self.tr("Add to Project..."))
                actionRun = menu.addAction(self.tr("Run this File!"))
                menuSyntax = menu.addMenu(self.tr("Change Syntax"))
                self._create_menu_syntax(menuSyntax)
                menu.addSeparator()
                actionClose = menu.addAction(self.tr("Close This Tab"))
                actionCloseAll = menu.addAction(self.tr("Close All Tabs"))
                actionCloseAllNotThis = menu.addAction(
                    self.tr("Close Other Tabs"))
                menu.addSeparator()
                if self._parent.splitted:
                    actionMoveSplit = menu.addAction(
                        self.tr("Move this Tab to the other Split"))
                    actionCloseSplit = menu.addAction(
                        self.tr("Close Split"))
                    #Connect split actions
                    self.connect(actionMoveSplit, SIGNAL("triggered()"),
                        lambda: self._parent.move_tab_to_next_split(self))
                    self.connect(actionCloseSplit, SIGNAL("triggered()"),
                        lambda: self._parent.split_tab(
                            self._parent.orientation() == Qt.Horizontal))
                else:
                    actionSplitH = menu.addAction(
                        self.tr("Split this Tab (Vertically)"))
                    actionSplitV = menu.addAction(
                        self.tr("Split this Tab (Horizontally)"))
                    #Connect split actions
                    self.connect(actionSplitH, SIGNAL("triggered()"),
                        lambda: self._split_this_tab(True))
                    self.connect(actionSplitV, SIGNAL("triggered()"),
                        lambda: self._split_this_tab(False))
                menu.addSeparator()
                actionCopyPath = menu.addAction(
                    self.tr("Copy file location to Clipboard"))
                actionReopen = menu.addAction(
                    self.tr("Reopen last closed File"))
                if len(self.__lastOpened) == 0:
                    actionReopen.setEnabled(False)
                #Connect actions
                self.connect(actionRun, SIGNAL("triggered()"),
                    self._run_this_file)
                self.connect(actionAdd, SIGNAL("triggered()"),
                    self._add_to_project)
                self.connect(actionClose, SIGNAL("triggered()"),
                    lambda: self.removeTab(index))
                self.connect(actionCloseAllNotThis, SIGNAL("triggered()"),
                    self._close_all_tabs_except_this)
                self.connect(actionCloseAll, SIGNAL("triggered()"),
                    self._close_all_tabs)
                self.connect(actionCopyPath, SIGNAL("triggered()"),
                    self._copy_file_location)
                self.connect(actionReopen, SIGNAL("triggered()"),
                    self._reopen_last_tab)
                menu.exec_(event.globalPos())
        if event.button() == Qt.MidButton:
            index = self.tabBar().tabAt(event.pos())
            self.removeTab(index)

    def _create_menu_syntax(self, menuSyntax):
        syntax = list(settings.SYNTAX.keys())
        syntax.sort()
        for syn in syntax:
            menuSyntax.addAction(syn)
            self.connect(menuSyntax, SIGNAL("triggered(QAction*)"),
                self._reapply_syntax)

    def _reapply_syntax(self, syntaxAction):
        if [self.currentIndex(), syntaxAction] != self._resyntax:
            self._resyntax = [self.currentIndex(), syntaxAction]
            self.emit(SIGNAL("syntaxChanged(QWidget, QString)"),
                self.currentWidget(), syntaxAction.text())

    def _run_this_file(self):
        self.emit(SIGNAL("runFile()"))

    def _add_to_project(self):
        self.emit(SIGNAL("changeActualTab(QTabWidget)"), self)
        widget = self.currentWidget()
        if type(widget) is editor.Editor:
            self.emit(SIGNAL("addToProject(QString)"), widget.ID)

    def _reopen_last_tab(self):
        self.emit(SIGNAL("reopenTab(QTabWidget, QString)"),
            self, self.__lastOpened.pop())
        self.emit(SIGNAL("recentTabsModified(QStringList)"), self.__lastOpened)

    def _split_this_tab(self, orientation):
        self.emit(SIGNAL("splitTab(QTabWidget, int, bool)"),
            self, self.currentIndex(), orientation)

    def _copy_file_location(self):
        widget = self.currentWidget()
        QApplication.clipboard().setText(widget.ID, QClipboard.Clipboard)

    def _close_all_tabs(self):
        for i in range(self.count()):
            self.removeTab(0)

    def _close_all_tabs_except_this(self):
        self.tabBar().moveTab(self.currentIndex(), 0)
        for i in range(self.count()):
            if self.count() > 1:
                self.removeTab(1)

    def _check_unsaved_tabs(self):
        """
        Check if are there any unsaved tab
        Returns True or False
        """
        val = False
        for i in range(self.count()):
            if type(self.widget(i)) is editor.Editor:
                val = val or self.widget(i).textModified
        return val

    def get_unsaved_files(self):
        """
        Returns a list with the tabText of the unsaved files
        """
        files = []
        for i in range(self.count()):
            widget = self.widget(i)
            if type(widget) is editor.Editor and widget.textModified:
                files.append(self.tabText(i))
        return files

    def change_tab(self):
        if self.currentIndex() < (self.count() - 1):
            self.setCurrentIndex(self.currentIndex() + 1)
        else:
            self.setCurrentIndex(0)

    def change_tab_reverse(self):
        if self.currentIndex() > 0:
            self.setCurrentIndex(self.currentIndex() - 1)
        else:
            self.setCurrentIndex(self.count() - 1)

    def change_open_tab_name(self, index, newName):
        """Change the name of the tab at index, for the newName."""
        self.remove_title(index)
        self.setTabText(index, newName)
        self.titles.append(newName)


class TabNavigator(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.setContextMenuPolicy(Qt.DefaultContextMenu)
        self.setMinimumHeight(38)
        hbox = QHBoxLayout(self)
        self.btnPrevious = QPushButton(
            QIcon(resources.IMAGES['nav-code-left']), '')
        self.btnPrevious.setObjectName('navigation_button')
        self.btnPrevious.setToolTip(
            self.tr("Right click to change navigation options"))
        self.btnNext = QPushButton(
            QIcon(resources.IMAGES['nav-code-right']), '')
        self.btnNext.setObjectName('navigation_button')
        self.btnNext.setToolTip(
            self.tr("Right click to change navigation options"))
        hbox.addWidget(self.btnPrevious)
        hbox.addWidget(self.btnNext)
        self.setContentsMargins(0, 0, 0, 0)

        self.menuNavigate = QMenu(self.tr("Navigate"))
        self.codeAction = self.menuNavigate.addAction(
            self.tr("Code Jumps"))
        self.codeAction.setCheckable(True)
        self.codeAction.setChecked(True)
        self.bookmarksAction = self.menuNavigate.addAction(
            self.tr("Bookmarks"))
        self.bookmarksAction.setCheckable(True)
        self.breakpointsAction = self.menuNavigate.addAction(
            self.tr("Breakpoints"))
        self.breakpointsAction.setCheckable(True)

        # 0 = Code Jumps
        # 1 = Bookmarks
        # 2 = Breakpoints
        self.operation = 0

        self.connect(self.codeAction, SIGNAL("triggered()"),
            self._show_code_nav)
        self.connect(self.breakpointsAction, SIGNAL("triggered()"),
            self._show_breakpoints)
        self.connect(self.bookmarksAction, SIGNAL("triggered()"),
            self._show_bookmarks)

    def contextMenuEvent(self, event):
        self.show_menu_navigation()

    def show_menu_navigation(self):
        self.menuNavigate.exec_(QCursor.pos())

    def _show_bookmarks(self):
        self.btnPrevious.setIcon(QIcon(resources.IMAGES['book-left']))
        self.btnNext.setIcon(QIcon(resources.IMAGES['book-right']))
        self.bookmarksAction.setChecked(True)
        self.breakpointsAction.setChecked(False)
        self.codeAction.setChecked(False)
        self.operation = 1

    def _show_breakpoints(self):
        self.btnPrevious.setIcon(QIcon(resources.IMAGES['break-left']))
        self.btnNext.setIcon(QIcon(resources.IMAGES['break-right']))
        self.bookmarksAction.setChecked(False)
        self.breakpointsAction.setChecked(True)
        self.codeAction.setChecked(False)
        self.operation = 2

    def _show_code_nav(self):
        self.btnPrevious.setIcon(QIcon(resources.IMAGES['nav-code-left']))
        self.btnNext.setIcon(QIcon(resources.IMAGES['nav-code-right']))
        self.bookmarksAction.setChecked(False)
        self.breakpointsAction.setChecked(False)
        self.codeAction.setChecked(True)
        self.operation = 0
