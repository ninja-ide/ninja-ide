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

import bisect

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QClipboard
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QMenu
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QStackedLayout
from PyQt5.QtWidgets import QStyle
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QSpacerItem
from PyQt5.QtCore import QSize
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import Qt
from PyQt5.Qsci import QsciDocument
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import Q_ENUMS

from ninja_ide import translations
from ninja_ide.extensions import handlers
from ninja_ide.core import settings
from ninja_ide.gui.ide import IDE
from ninja_ide.gui.main_panel import files_handler


try:
    # For Python2
    str = unicode  # lint:ok
except NameError:
    # We are in Python3
    pass


class ComboEditor(QDialog):
    
    closeSplit = pyqtSignal(QWidget)#closeSplit
    allFilesClosed = pyqtSignal()
    splitEditor = pyqtSignal("QWidget*", "QWidget*", bool)
    recentTabsModified = pyqtSignal()
    aboutToCloseComboEditor = pyqtSignal()

    class NAVIGATE:
        prev = 0
        next = 1

    Q_ENUMS(NAVIGATE)

    def __init__(self, original=False, Force_Free=False):
        super(ComboEditor, self).__init__(None)#, Qt.WindowStaysOnTopHint)
        self.__original = original
        self.Force_Free = Force_Free
        self.__undocked = []
        self._single_undocked = []
        self._symbols_index = []
        self.__OFiles = []
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)

        self.bar = ActionBar(main_combo=original)
        vbox.addWidget(self.bar)

        self.stacked = QStackedLayout()
        vbox.addLayout(self.stacked)

        self._main_container = IDE.get_service('main_container')

        if not self.__original and not self.Force_Free:
            self._main_container.fileOpened.connect(self._file_opened_by_main)

        # QApplication.instance().focusChanged["QWidget*", "QWidget*"].connect(\
        #     lambda w1, w2: QTimer.singleShot(10, lambda w1=w1, w2=w2: print("\n\nQApplication::focusChanged::", w1, w2)))

        self.bar.combo.showComboSelector.connect(self._main_container.change_tab)
        self.bar.changeCurrent.connect(self._set_current)
        self.bar.editorSplited.connect(self.split_editor)
        self.bar.runFile[str].connect(self._run_file)
        self.bar.closeFile.connect(lambda: self.closeSplit.emit(self))
        self.bar.addToProject[str].connect(self._add_to_project)
        self.bar.showFileInExplorer.connect(self._show_file_in_explorer)
        self.bar.goToSymbol.connect(self._go_to_symbol)
        self.bar.undockedEditor.connect(self.undock_editor)
        self.bar.undockedThisEditor.connect(self.single_undock_editor)
        self.bar.reopenTab[str].connect(self._main_container.open_file)
        self.bar.recentTabsModified.connect(self._main_container.recent_files_changed)
        self.bar.code_navigator.btnPrevious.clicked['bool'].connect(lambda: self._navigate_code(self.NAVIGATE.prev))
        self.bar.code_navigator.btnNext.clicked['bool'].connect(lambda: self._navigate_code(self.NAVIGATE.prev))

        # QTimer.singleShot(39999, lambda : print("\n\ncombo:-:", self))

    # def closeEvent(self, event):
    #     for comboeditor in self._single_undocked:
    #         print("has undocked", comboeditor)
    #         comboeditor.reject()
    #         comboeditor.deleteLater()

    #     self.bar._close_all_files()
    #     super(ComboEditor, self).closeEvent(event)

    def _navigate_code(self, val):
        op = self.bar.code_navigator.operation
        self._main_container.navigate_code_history(val, op)

    def currentWidget(self):
        return self.stacked.currentWidget()

    def setFocus(self):
        super(ComboEditor, self).setFocus()
        w = self.stacked.currentWidget()
        if w:
            w.setFocus()
        self._editor_with_focus()

    def _file_opened_by_main(self, path):
        index = self.stacked.currentIndex()
        ninjaide = IDE.getInstance()
        editable = ninjaide.get_or_create_editable(path)
        print("_file_opened_by_main", editable)
        self.add_editor(editable)
        self.bar.set_current_by_index(index)
        if index == -1:
            self.bar.set_current_by_index(0)

    def add_editor(self, neditable, keep_index=False):
        """Add Editor Widget to the UI area."""
        if neditable.editor:
            if self.__original or self.Force_Free:
                editor = neditable.editor
                print("\n\nadd_editor() ignora por ahora!", editor)
                
                # disconnect old Signals
                try:
                    editor.cursorPositionChanged[int, int].disconnect()
                except TypeError:
                    pass
                try:
                    editor.editorFocusObtained.disconnect()
                except TypeError:
                    pass
                try:
                    editor.currentLineChanged.disconnect()
                except TypeError:
                    pass
                try:
                    editor.modificationChanged['bool'].disconnect()
                except TypeError:
                    pass
                try:
                    neditable.checkersUpdated.disconnect()
                except TypeError:
                    pass
                try:
                    neditable.fileSaved.disconnect()
                except TypeError:
                    pass
                
                # Disonnect file system signals only in the original
                try:
                    neditable.fileClosing.disconnect()
                except TypeError:
                    pass
                if self.__original:
                    try:
                        neditable.askForSaveFileClosing.disconnect()
                    except TypeError:
                        pass
                    try:
                        neditable.fileChanged.disconnect()
                    except TypeError:
                        pass

            else:
                editor = self._main_container.create_editor_from_editable(
                    neditable)

            index = self.stacked.currentIndex()
            self.stacked.addWidget(editor)
            self.bar.add_item(neditable.display_name, neditable)
            if keep_index:
                self.bar.set_current_by_index(index)

            # Editor Signals
            editor.cursorPositionChanged[int, int].connect(self._update_cursor_position)
            editor.editorFocusObtained.connect(self._editor_with_focus)
            editor.currentLineChanged.connect(self._set_current_symbol)
            editor.modificationChanged['bool'].connect(self._editor_modified)
            neditable.checkersUpdated.connect(self._show_notification_icon)
            neditable.fileSaved.connect(self._update_symbols)
            neditable.fileSaved.connect(self._update_combo_info)

            # Connect file system signals only in the original
            neditable.fileClosing.connect(self._close_file)
            if self.__original:
                neditable.askForSaveFileClosing.connect(self._ask_for_save)
                neditable.fileChanged.connect(self._file_has_been_modified)

            # Load Symbols
            self._load_symbols(neditable)

    def show_combo_file(self):
        print("show_combo_file")
        self.bar.combo.showPopup()

    def show_combo_symbol(self):
        self.bar.symbols_combo.showPopup()


    def getOpenedFiles(self):
        return self.__OFiles.copy()

    def addOpenedFiles(self, fil):
        self.__OFiles.append(fil)


    def unlink_editors(self):
        for index in range(self.stacked.count()):
            widget = self.stacked.widget(index)
            widget.setDocument(QsciDocument())

    def split_editor(self, orientationVertical):
        new_widget = ComboEditor()
        for neditable in self.bar.get_editables():
            print("\nsplit_editor", neditable, new_widget)
            new_widget.add_editor(neditable)
        self.splitEditor.emit(self, new_widget, orientationVertical)

    def undock_editor(self):
        new_combo = ComboEditor()
        new_combo.setWindowTitle("NINJA-IDE")
        self.add_Undocked(new_combo)
        for neditable in self.bar.get_editables():
            print("undock_editor", neditable)
            new_combo.add_editor(neditable)
        new_combo.resize(500, 500)
        new_combo.aboutToCloseComboEditor.connect(self._remove_undock)
        new_combo.show()

    def _remove_undock(self):
        print("_remove_undock", self.sender())
        widget = self.sender()
        self.sub_Undocked(widget)

    def add_Undocked(self, u):
        self.__undocked.append(u)

    def sub_Undocked(self, u):
        self.__undocked.remove(u)

    def add_SingleUndocked(self, u):
        self._single_undocked.append(u)

    def sub_SingleUndocked(self, u):
        self._single_undocked.remove(u)

    # aún no se ha puesto en funcionamiento!. 
    def single_split_editor(self, orientationVertical):
        new_widget = ComboEditor()
        for neditable in self.bar.get_editables():
            print("\nsingle_split_editor", neditable, new_widget)
            new_widget.add_editor(neditable)
        self.splitEditor.emit(self, new_widget, orientationVertical)

    def single_undock_editor(self):
        new_combo = ComboEditor(Force_Free=True)
        new_combo.setWindowTitle("NINJA-IDE")
        self.add_SingleUndocked(new_combo)
 
        wid = self.stacked.takeAt(self.stacked.currentIndex()).widget()
        ide = IDE.getInstance()
        ide.unload_NEditable(wid)
        neditable = self.bar.take_editable()
        print("\n\nsingle_undock_editor:::", neditable, neditable.editor, wid, neditable.nfile)
       
        if self.stacked.isEmpty():
            self.allFilesClosed.emit()

        new_combo.add_editor(neditable)
        new_combo.stacked.setCurrentIndex(0)# new_combo.stacked.setCurrentWidget(wid)
        new_combo.resize(500, 500)
        new_combo.aboutToCloseComboEditor.connect(self.single__remove_undock)
        new_combo.show()

    def single__remove_undock(self):
        print("single__remove_undock", self.sender())
        widget = self.sender()
        self.sub_SingleUndocked(widget)
        ##widget.deleteLater()

    def bind_Editable(self, editable):
        self.bar.add_item(neditable.display_name, editable)


    def close_current_file(self):
        self.bar.about_to_close_file()

    def _close_file(self, neditable):
        index = self.bar.close_file(neditable)
        layoutItem = self.stacked.takeAt(index)
        #neditable.editor.completer.cc.unload_module()
        self._add_to_last_opened(neditable.file_path)
        layoutItem.widget().deleteLater()

        if self.stacked.isEmpty():
            self.allFilesClosed.emit()

    def _add_to_last_opened(self, path):
        if path not in settings.LAST_OPENED_FILES:
            settings.LAST_OPENED_FILES.append(path)
            if len(settings.LAST_OPENED_FILES) > settings.MAX_REMEMBER_TABS:
                self.__lastOpened = self.__lastOpened[1:]
            self.recentTabsModified.emit()

    def _editor_with_focus(self):
        if self._main_container.current_widget is not self:
            self._main_container.current_widget = self
            editor = self.stacked.currentWidget()
            self._main_container.current_editor_changed(
                editor.neditable.file_path)
            self._load_symbols(editor.neditable)
            editor.neditable.update_checkers_display()

    def _ask_for_save(self, neditable):
        val = QMessageBox.No
        fileName = neditable.nfile.file_name
        val = QMessageBox.question(
            self, (self.tr('The file %s was not saved') %
                   fileName),
            self.tr("Do you want to save before closing?"),
            QMessageBox.Yes | QMessageBox.No |
            QMessageBox.Cancel)
        if val == QMessageBox.No:
            neditable.nfile.close(force_close=True)
        elif val == QMessageBox.Yes:
            neditable.ignore_checkers = True
            self._main_container.save_file(neditable.editor)
            neditable.nfile.close()

    def _file_has_been_modified(self, neditable):
        val = QMessageBox.No
        fileName = neditable.file_path
        val = QMessageBox.question(
            self, translations.TR_FILE_HAS_BEEN_MODIFIED,
            "%s%s" % (fileName, translations.TR_FILE_MODIFIED_OUTSIDE),
            QMessageBox.Yes | QMessageBox.No)
        if val == QMessageBox.Yes:
            neditable.reload_file()

    def _run_file(self, path):
        self._main_container.run_file(path)

    def _add_to_project(self, path):
        self._main_container._add_to_project(path)

    def _show_file_in_explorer(self, path):
        '''Connected to ActionBar's showFileInExplorer(QString)
        signal, forwards the file path on to the main container.'''
        self._main_container._show_file_in_explorer(path)

    def set_current(self, neditable):
        if neditable:
            self.bar.set_current_file(neditable)

    def _set_current(self, neditable, index):
        if neditable:
            self.stacked.setCurrentIndex(index)
            editor = self.stacked.currentWidget()
            self._update_cursor_position(ignore_sender=True)
            editor.setFocus()
            self._main_container.current_editor_changed(
                neditable.file_path)
            self._load_symbols(neditable)
            self._show_file_in_explorer(neditable.file_path)
            neditable.update_checkers_display()

    def widget(self, index):
        return self.stacked.widget(index)

    def count(self):
        """Return the number of editors opened."""
        return self.stacked.count()

    def _update_cursor_position(self, line=0, col=0, ignore_sender=False):
        obj = self.sender()
        editor = self.stacked.currentWidget()
        # Check if it's current to avoid signals from other splits.
        if ignore_sender or editor == obj:
            line += 1
            self.bar.update_line_col(line, col)

    def _set_current_symbol(self, line, ignore_sender=False):
        obj = self.sender()
        editor = self.stacked.currentWidget()
        # Check if it's current to avoid signals from other splits.
        if ignore_sender or editor == obj:
            index = bisect.bisect(self._symbols_index, line)
            if (index >= len(self._symbols_index) or
                    self._symbols_index[index] > (line + 1)):
                index -= 1
            self.bar.set_current_symbol(index)

    def _editor_modified(self, value):
        obj = self.sender()
        neditable = obj.neditable
        if value:
            text = "\u2022 %s" % neditable.display_name
            self.bar.update_item_text(neditable, text)
        else:
            self.bar.update_item_text(neditable, neditable.display_name)

    def _go_to_symbol(self, index):
        print("_go_to_symbol in index:", index)
        line = self._symbols_index[index]
        editor = self.stacked.currentWidget()
        editor.go_to_line(line)

    def _update_symbols(self, neditable):
        editor = self.stacked.currentWidget()
        # Check if it's current to avoid signals from other splits.
        if editor == neditable.editor:
            self._load_symbols(neditable)

    def _update_combo_info(self, neditable):
        self.bar.update_item_text(neditable, neditable.display_name)
        self._main_container.current_editor_changed(neditable.file_path)

    def _load_symbols(self, neditable):
        symbols_handler = handlers.get_symbols_handler('py')
        source = neditable.editor.text()
        source = source.encode(neditable.editor.encoding)
        symbols, symbols_simplified = symbols_handler.obtain_symbols(
            source, simple=True)
        self._symbols_index = sorted(symbols_simplified.keys())
        symbols_simplified = sorted(
            list(symbols_simplified.items()), key=lambda x: x[0])
        self.bar.add_symbols(symbols_simplified)
        line, _ = neditable.editor.getCursorPosition()
        self._set_current_symbol(line, True)
        tree_symbols = IDE.get_service('symbols_explorer')
        tree_symbols.update_symbols_tree(symbols, neditable.file_path)

    def _show_notification_icon(self, neditable):
        checkers = neditable.sorted_checkers
        icon = QIcon()
        for items in checkers:
            checker, color, _ = items
            if checker.checks:
                if isinstance(checker.checker_icon, int):
                    icon = self.style().standardIcon(checker.checker_icon)
                elif isinstance(checker.checker_icon, str):
                    icon = QIcon(checker.checker_icon)
                break
        self.bar.update_item_icon(neditable, icon)

    def show_menu_navigation(self):
        self.bar.code_navigator.show_menu_navigation()

    def closeEvent(self, event):
        for comboeditor in self._single_undocked:
            print("has undocked", comboeditor)
            comboeditor.reject()
            comboeditor.deleteLater()

        self.bar._close_all_files()
        self.aboutToCloseComboEditor.emit()
        super(ComboEditor, self).closeEvent(event)

    def reject(self):
        if not self.__original:
            super(ComboEditor, self).reject()


class ActionBar(QFrame):
    """
    SIGNALS:
    @changeCurrent(PyQt_PyObject)
    @runFile(QString)
    @reopenTab(QString)
    @recentTabsModified()
    """
    changeCurrent = pyqtSignal('QObject*', int)
    runFile = pyqtSignal(str)
    reopenTab = pyqtSignal(str)
    recentTabsModified = pyqtSignal()
    closeFile = pyqtSignal()# closeSplit
    editorSplited = pyqtSignal(bool)# splitEditor, hasSplitEditor
    addToProject = pyqtSignal(str)
    showFileInExplorer = pyqtSignal(str)
    goToSymbol = pyqtSignal(int)
    dockedWidget = pyqtSignal("QObject*")
    undockedWidget = pyqtSignal()
    undockedEditor = pyqtSignal()
    undockedThisEditor = pyqtSignal()

    class ORIENTATION:
        Horizontal = 0
        Vertical = 1

    Q_ENUMS(ORIENTATION)
            
    def __init__(self, main_combo=False):
        super(ActionBar, self).__init__()
        self.setObjectName("actionbar")
        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(1, 1, 1, 1)
        hbox.setSpacing(1)

        self.lbl_checks = QLabel('')
        self.lbl_checks.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.lbl_checks.setFixedWidth(48)
        self.lbl_checks.setVisible(False)
        hbox.addWidget(self.lbl_checks)

        self.combo = ComboFiles(undocked=not main_combo)
        # por aca iria 'self.combo.setContainer()'
        self.combo.setIconSize(QSize(16, 16))
        #model = QStandardItemModel()
        #self.combo.setModel(model)
        #self.combo.view().setDragDropMode(QAbstractItemView.InternalMove)
        self.combo.setMaximumWidth(300)
        self.combo.setObjectName("combotab")
        self.combo.currentIndexChanged[int].connect(self.current_changed)
        self.combo.setToolTip(translations.TR_COMBO_FILE_TOOLTIP)
        self.combo.setContextMenuPolicy(Qt.CustomContextMenu)
        self.combo.customContextMenuRequested['const QPoint &'].connect(self._context_menu_requested)
        hbox.addWidget(self.combo)
        #QTimer.singleShot(50000, lambda: print("singleShot", self.combo.showPopup()))

        self.symbols_combo = QComboBox()
        self.symbols_combo.setIconSize(QSize(16, 16))
        self.symbols_combo.setObjectName("combo_symbols")
        self.symbols_combo.activated[int].connect(self.current_symbol_changed)
        hbox.addWidget(self.symbols_combo)

        self.code_navigator = CodeNavigator()
        hbox.addWidget(self.code_navigator)

        self.createContextualMenu()

        self._pos_text = "Line: %d, Col: %d"
        # self.lbl_position = QLabel(self._pos_text % (0, 0))
        # self.lbl_position.setObjectName("position")
        # self.lbl_position.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        # hbox.addWidget(self.lbl_position)
        # hbox.addSpacerItem(QSpacerItem(10,10, QSizePolicy.Expanding))
        hbox.addSpacing(100)

        btn_close = QPushButton(
            self.style().standardIcon(QStyle.SP_DialogCloseButton), '')
        btn_close.setIconSize(QSize(16, 16))
        if main_combo:
            btn_close.setObjectName('navigation_button')
            btn_close.setToolTip(translations.TR_CLOSE_FILE)
            btn_close.clicked['bool'].connect(lambda s: self.about_to_close_file())
        else:
            btn_close.setObjectName('close_split')
            btn_close.setToolTip(translations.TR_CLOSE_SPLIT)
            btn_close.clicked['bool'].connect(self.close_split)
        btn_close.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        hbox.addWidget(btn_close)

    def resizeEvent(self, event):
        super(ActionBar, self).resizeEvent(event)
        if event.size().width() < 350:
            self.symbols_combo.hide()
            self.code_navigator.hide()
            # self.lbl_position.hide()
        else:
            self.symbols_combo.show()
            self.code_navigator.show()
            # self.lbl_position.show()

    def add_item(self, text, neditable):
        """Add a new item to the combo and add the neditable data."""
        self.combo.addItem(text, neditable)
        self.combo.setCurrentIndex(self.combo.count() - 1)

    def take_editable(self, index=-1):
        return self.combo.take_editable()

    def get_editable(self, index=-1):
        return self.combo.get_editable(index)

    def get_editables(self):
        return self.combo.get_editables()

    # def clearItems(self):
    #     self.combo.clearItems()
        
    def add_symbols(self, symbols):
        """Add the symbols to the symbols's combo."""
        self.symbols_combo.clear()
        for symbol in symbols:
            data = symbol[1]
            if data[1] == 'f':
                icon = QIcon(":img/function")
            else:
                icon = QIcon(":img/class")
            self.symbols_combo.addItem(icon, data[0])

    def set_current_symbol(self, index):
        self.symbols_combo.setCurrentIndex(index)

    def update_item_icon(self, neditable, icon):
        index = self.combo.findData(neditable)
        self.combo.setItemIcon(index, icon)

    def update_item_text(self, neditable, text):
        index = self.combo.findData(neditable)
        self.combo.setItemText(index, text)

    def current_changed(self, index):
        """Change the current item in the combo."""
        neditable = self.combo.itemData(index)
        self.changeCurrent.emit(neditable, index)

    def current_symbol_changed(self, index):
        """Change the current symbol in the combo."""
        self.goToSymbol.emit(index)

    def update_line_col(self, line, col):
        """Update the line and column position."""
        #self.lbl_position.setText(self._pos_text % (line, col))
        IDE.getInstance().showMessageStatus(self._pos_text % (line, col))


    def createContextualMenu(self):
        menu = QMenu()
        self.menu = menu
        
        actionAdd = menu.addAction(translations.TR_ADD_TO_PROJECT)
        actionRun = menu.addAction(translations.TR_RUN_FILE)
        menuSyntax = menu.addMenu(translations.TR_CHANGE_SYNTAX)
        self._create_menu_syntax(menuSyntax)
        menu.addSeparator()
        actionClose = menu.addAction(translations.TR_CLOSE_FILE)
        actionCloseAll = menu.addAction(translations.TR_CLOSE_ALL_FILES)
        actionCloseAllNotThis = menu.addAction(
            translations.TR_CLOSE_OTHER_FILES)
        menu.addSeparator()
        actionSplitH = menu.addAction(translations.TR_SPLIT_VERTICALLY)
        actionSplitV = menu.addAction(translations.TR_SPLIT_HORIZONTALLY)
        menu.addSeparator()
        actionCopyPath = menu.addAction(
            translations.TR_COPY_FILE_PATH_TO_CLIPBOARD)
        actionShowFileInExplorer = menu.addAction(
            translations.TR_SHOW_FILE_IN_EXPLORER)
        actionReopen = menu.addAction(translations.TR_REOPEN_FILE)
        actionUndock = menu.addAction(translations.TR_UNDOCK_EDITOR)
        actionUndockThis = menu.addAction("UndockThis")

        if len(settings.LAST_OPENED_FILES) == 0:
            actionReopen.setEnabled(False)
        #Connect actions
        actionSplitH.triggered['bool'].connect(lambda s: self._split(self.ORIENTATION.Horizontal))
        actionSplitV.triggered['bool'].connect(lambda s: self._split(self.ORIENTATION.Vertical))
        actionRun.triggered['bool'].connect(lambda s: self._run_this_file())
        actionAdd.triggered['bool'].connect(lambda s: self._add_to_project())
        actionClose.triggered['bool'].connect(lambda s: self.about_to_close_file())
        actionCloseAllNotThis.triggered['bool'].connect(lambda s: self._close_all_files_except_this())
        actionCloseAll.triggered['bool'].connect(lambda s: self._close_all_files())
        actionCopyPath.triggered['bool'].connect(lambda s: self._copy_file_location())
        actionShowFileInExplorer.triggered['bool'].connect(lambda s: self._show_file_in_explorer())
        actionReopen.triggered['bool'].connect(lambda s: self._reopen_last_tab())
        actionUndock.triggered['bool'].connect(lambda s: self.undockedEditor.emit())
        actionUndockThis.triggered['bool'].connect(lambda s: self.undockedThisEditor.emit())

    def _context_menu_requested(self, point):
        """Display context menu for the combo file."""
        if self.combo.count() == 0:
            # If there is not an Editor opened, don't show the menu
            return

        self.menu.exec_(self.mapToGlobal(point))#QCursor.pos())

    def _create_menu_syntax(self, menuSyntax):
        """Create Menu with the list of syntax supported."""
        syntax = list(settings.SYNTAX.keys())
        syntax.sort()
        for syn in syntax:
            act = menuSyntax.addAction(syn)
            act.triggered['bool'].connect(lambda s: QMessageBox.critical(self, "Beta Info", "Can not construct this segment!"))#self._reapply_syntax

    def _reapply_syntax(self, syntaxAction):
        #TODO
        if [self.combo.currentIndex(), syntaxAction] != self._resyntax:
            self._resyntax = [self.combo.currentIndex(), syntaxAction]
            self.syntaxChangedemit(self.currentWidget(), syntaxAction.text())

    def set_current_file(self, neditable):
        index = self.combo.findData(neditable)
        self.combo.setCurrentIndex(index)

    def set_current_by_index(self, index):
        self.combo.setCurrentIndex(index)

    def about_to_close_file(self, index=None):
        """Close the NFile object."""
        print("\n\nabout_to_close_file")
        if index is None:
            index = self.combo.currentIndex()
        neditable = self.combo.itemData(index)
        if neditable:
            print("\n\nabout_to_close_file:", self.combo.count(), index, self.combo.currentIndex())
            neditable.nfile.close()

    def close_split(self):
        self.closeFile.emit()

    def close_file(self, neditable):
        """Receive the confirmation to close the file."""
        index = self.combo.findData(neditable)
        self.combo.removeItem(index)
        return index

    def _run_this_file(self):
        """Execute the current file."""
        neditable = self.combo.itemData(self.combo.currentIndex())
        self.runFile.emit(neditable.file_path)

    def _add_to_project(self):
        """Emit a signal to let someone handle the inclusion of the file
        inside a project."""
        neditable = self.combo.itemData(self.combo.currentIndex())
        self.addToProject.emit(neditable.file_path)

    def _show_file_in_explorer(self):
        '''Triggered when the "Show File in Explorer" context
        menu action is selected. Emits the "showFileInExplorer(QString)"
        signal with the current file's full path as argument.'''
        neditable = self.combo.itemData(self.combo.currentIndex())
        self.showFileInExplorer.emit(neditable.file_path)

    def _reopen_last_tab(self):
        self.reopenTab.emit(settings.LAST_OPENED_FILES.pop())
        self.recentTabsModified.emit()

    # def _undock_editor(self):
    #     self.undockEditor.emit()

    def _split(self, orientation):
        self.editorSplited.emit(orientation)

    def _copy_file_location(self):
        """Copy the path of the current opened file to the clipboard."""
        neditable = self.combo.itemData(self.combo.currentIndex())
        QApplication.clipboard().setText(neditable.file_path,
                                         QClipboard.Clipboard)

    def _close_all_files(self):
        """Close all the files opened."""
        print("_close_all_files")
        for i in range(self.combo.count()):
            self.about_to_close_file(0)

    def _close_all_files_except_this(self):
        """Close all the files except the current one."""
        neditable = self.combo.itemData(self.combo.currentIndex())
        for i in reversed(list(range(self.combo.count()))):
            ne = self.combo.itemData(i)
            if ne is not neditable:
                self.about_to_close_file(i)


class ComboFiles(QComboBox):
    showComboSelector = pyqtSignal()
    def __init__(self, undocked, parent=None):
        super(ComboFiles, self).__init__()
        self.block = False
        self.undocked = undocked
        self.__parent = parent if parent else IDE.get_service("main_container")
        self._files_handler = files_handler.FilesHandler(self)
    #     self.highlighted[int].connect(lambda i: print("highlighted", i))
    #     QTimer.singleShot(5000, self.test)

    # def test(self):
    #     print("_files_handler", self._files_handler.show())

    def showPopup(self):
        print("showPopup", self._files_handler.isVisible(), self._files_handler.view.isVisible())
        #super(ComboFiles, self).showPopup()# agregado!
        if not self._files_handler.view.isVisible() and not self.block:
            # self.showComboSelector.emit()
            self._files_handler.show()
        else:
            self.block = False
            self._files_handler.hide()

    def hidePopup(self):
        print("hidePopup", self._files_handler.isVisible(), self._files_handler.view.isVisible())
        self.block = True
        self._files_handler.hide()

    @property
    def container(self):
        return self.__parent

    @container.setter
    def setContainer(self, p):
        self.__parent = p

    @property
    def opened_files(self):
        # editables = []
        # for index in range(self.count()):
        #     neditable = self.itemData(index)
        #     editables.append(neditable.nfile)
        #     print("\nopened_files[i]", type(neditable), neditable.editor)
        # return editables
        return self.get_editables()

    def take_editable(self, index=-1):#dismiss
        if index == -1:
            index = self.currentIndex()
        edit = self.itemData(index)
        self.removeItem(index)
        return edit

    def get_editable(self, index=-1):
        if index == -1:
            index = self.currentIndex()
        return self.itemData(index)

    def get_editables(self):
        editables = []
        for index in range(self.count()):
            neditable = self.itemData(index)
            editables.append(neditable)
            # print("\nget_editable[i]", type(neditable), neditable.editor)
        return editables


    def keyPressEvent(self, event):
        print("event.key()", event.key())
        if event.key() == Qt.Key_Slash:
            items = QApplication.instance().topLevelWidgets()
            print("keyPressEvent()", self._files_handler, self._files_handler.isVisible(),\
                self._files_handler.view.isVisible(), self._files_handler.windowFlags(),\
                bool(self._files_handler.windowFlags() & Qt.WindowStaysOnTopHint) ) 
            print("items", items, self.parent(), len(items),\
                QApplication.instance().activePopupWidget(),\
                QApplication.instance().activeModalWidget(),\
                QApplication.instance().activeWindow(),\
                self._files_handler.view.isVisibleTo(self),\
                self._files_handler.visibleRegion() )
        else:
            super(ComboFiles, self).keyPressEvent(event)

    def mousePressEvent(self, event):
        print("\nCOMBOEDITOR.mousePressEvent", self._files_handler.isVisible(), self._files_handler.view.isVisible())
        if self._files_handler.view.isVisible():
            # event.ignore()
            # event.accept()
            self.hidePopup()
            return
        super(ComboFiles, self).mousePressEvent(event)
        

class CodeNavigator(QWidget):

    def __init__(self):
        super(CodeNavigator, self).__init__()
        self.setContextMenuPolicy(Qt.DefaultContextMenu)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setContentsMargins(0, 0, 0, 0)
        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(1, 1, 5, 1)
        if settings.IS_MAC_OS:
            hbox.setSpacing(10)
        else:
            hbox.setSpacing(0)
        self.btnPrevious = QPushButton(
            QIcon(":img/nav-code-left"), '')
        self.btnPrevious.setIconSize(QSize(16, 16))
        self.btnPrevious.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.btnPrevious.setObjectName('navigation_button')
        self.btnPrevious.setToolTip(translations.TR_TOOLTIP_NAV_BUTTONS)
        self.btnNext = QPushButton(
            QIcon(":img/nav-code-right"), '')
        self.btnNext.setIconSize(QSize(16, 16))
        self.btnNext.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.btnNext.setObjectName('navigation_button')
        self.btnNext.setToolTip(translations.TR_TOOLTIP_NAV_BUTTONS)
        hbox.addWidget(self.btnPrevious)
        hbox.addWidget(self.btnNext)

        self.menuNavigate = QMenu(self.tr("Navigate"))
        self.codeAction = self.menuNavigate.addAction(
            translations.TR_NAV_CODE_JUMP)
        self.codeAction.setCheckable(True)
        self.codeAction.setChecked(True)
        self.bookmarksAction = self.menuNavigate.addAction(
            translations.TR_NAV_BOOKMARKS)
        self.bookmarksAction.setCheckable(True)
        self.breakpointsAction = self.menuNavigate.addAction(
            translations.TR_NAV_BREAKPOINTS)
        self.breakpointsAction.setCheckable(True)

        # 0 = Code Jumps
        # 1 = Bookmarks
        # 2 = Breakpoints
        self.operation = 0

        self.codeAction.triggered['bool'].connect(lambda s: self._show_code_nav())
        self.breakpointsAction.triggered['bool'].connect(lambda s: self._show_breakpoints())
        self.bookmarksAction.triggered['bool'].connect(lambda s: self._show_bookmarks())

    def contextMenuEvent(self, event):
        self.show_menu_navigation()

    def show_menu_navigation(self):
        self.menuNavigate.exec_(QCursor.pos())

    def _show_bookmarks(self):
        self.btnPrevious.setIcon(QIcon(':img/book-left'))
        self.btnNext.setIcon(QIcon(':img/book-right'))
        self.bookmarksAction.setChecked(True)
        self.breakpointsAction.setChecked(False)
        self.codeAction.setChecked(False)
        self.operation = 1

    def _show_breakpoints(self):
        self.btnPrevious.setIcon(QIcon(':img/break-left'))
        self.btnNext.setIcon(QIcon(':img/break-right'))
        self.bookmarksAction.setChecked(False)
        self.breakpointsAction.setChecked(True)
        self.codeAction.setChecked(False)
        self.operation = 2

    def _show_code_nav(self):
        self.btnPrevious.setIcon(QIcon(':img/nav-code-left'))
        self.btnNext.setIcon(QIcon(':img/nav-code-right'))
        self.bookmarksAction.setChecked(False)
        self.breakpointsAction.setChecked(False)
        self.codeAction.setChecked(True)
        self.operation = 0
