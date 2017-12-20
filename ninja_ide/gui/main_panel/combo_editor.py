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
# from __future__ import absolute_import
# from __future__ import unicode_literals

import bisect

from PyQt5.QtWidgets import (
    QApplication,
    QMessageBox,
    # QDialog,
    QSpacerItem,
    QWidget,
    QMenu,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QStackedLayout,
    QStyle,
    QLabel,
    QComboBox,
    QSizePolicy,
    QPushButton,
    QToolButton
)
from PyQt5.QtGui import (
    QCursor,
    QClipboard,
    QColor,
    QIcon,
    QPalette
)
from PyQt5.QtCore import (
    # QSize,
    Qt,
    pyqtSignal,
    pyqtSlot,
    QModelIndex,
    QAbstractItemModel
)

from ninja_ide import translations
from ninja_ide.extensions import handlers
from ninja_ide.core import settings
from ninja_ide.gui.ide import IDE
from ninja_ide.tools import ui_tools
from ninja_ide.gui.theme import NTheme
from . import set_language


class ComboEditor(ui_tools.StyledBar):
    # Signals
    closeSplit = pyqtSignal('PyQt_PyObject')
    splitEditor = pyqtSignal(
        'PyQt_PyObject', 'PyQt_PyObject', Qt.Orientation)
    allFilesClosed = pyqtSignal()
    about_to_close_combo_editor = pyqtSignal()

    def __init__(self, original=False):
        super(ComboEditor, self).__init__(None)
        self.__original = original
        self.__undocked = []
        self._symbols_index = []
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)

        self.bar = ActionBar(main_combo=original)
        vbox.addWidget(self.bar)

        # Info bar
        self.info_bar = InfoBar(self)
        self.info_bar.setVisible(False)
        vbox.addWidget(self.info_bar)

        self.stacked = QStackedLayout()
        vbox.addLayout(self.stacked)

        self._main_container = IDE.get_service('main_container')

        if not self.__original:
            self._main_container.fileOpened['QString'].connect(
                self._file_opened_by_main)

        # self.bar.combo.showComboSelector.connect(
        #    lambda: self._main_container.change_tab())
        self.bar.change_current['PyQt_PyObject',
                                int].connect(self._set_current)
        self.bar.splitEditor[bool].connect(self.split_editor)
        self.bar.runFile['QString'].connect(self._run_file)
        self.bar.closeSplit.connect(lambda: self.closeSplit.emit(self))
        self.bar.addToProject['QString'].connect(self._add_to_project)
        self.bar.showFileInExplorer['QString'].connect(
            self._show_file_in_explorer)
        self.bar.goToSymbol[int].connect(self._go_to_symbol)
        self.bar.undockEditor.connect(self.undock_editor)
        self.bar.reopenTab['QString'].connect(
            lambda path: self._main_container.open_file(path))

        self.bar.code_navigator.previousPressed.connect(self._navigate_code)
        self.bar.code_navigator.nextPressed.connect(self._navigate_code)
        # self.connect(self.bar, SIGNAL("recentTabsModified()"),
        #             lambda: self._main_container.recent_files_changed())
        # self.connect(self.bar.code_navigator.btnPrevious,
        #                SIGNAL("clicked()"),
        #             lambda: self._navigate_code(False))
        # self.connect(self.bar.code_navigator.btnNext, SIGNAL("clicked()"),
        #             lambda: self._navigate_code(True))

    def _navigate_code(self, operation, forward=True):
        self._main_container.navigate_code_history(operation, forward)
    #    op = self.bar.code_navigator.operation
    #    self._main_container.navigate_code_history(val, op)

    def current_editor(self):
        return self.stacked.currentWidget()

    def setFocus(self):
        super(ComboEditor, self).setFocus()
        self.current_editor().setFocus()
        self._editor_with_focus()

    def _file_opened_by_main(self, path):
        index = self.stacked.currentIndex()
        ninjaide = IDE.get_service('ide')
        editable = ninjaide.get_or_create_editable(path)
        self.add_editor(editable)
        self.bar.set_current_by_index(index)
        if index == -1:
            self.bar.set_current_by_index(0)

    def add_editor(self, neditable, keep_index=False):
        """Add Editor Widget to the UI area."""
        if neditable.editor:
            if self.__original:
                editor = neditable.editor
            else:
                editor = neditable.editor.clone()
                # editor = self._main_container.create_editor_from_editable(
                #    neditable)
            current_index = self.stacked.currentIndex()
            new_index = self.stacked.addWidget(editor)
            self.stacked.setCurrentIndex(new_index)
            self.bar.add_item(neditable.display_name, neditable)
            # Bar is not visible because all the files have been closed,
            # so if a new file is opened, show the bar
            if not self.bar.isVisible():
                self.bar.setVisible(True)
            if keep_index:
                self.bar.set_current_by_index(current_index)
            # Connections
            neditable.fileClosing.connect(self._close_file)
            editor.editorFocusObtained.connect(self._editor_with_focus)
            editor.modificationChanged.connect(self._editor_modified)
            neditable.checkersUpdated.connect(self._show_notification_icon)
            # Connect file system signals only in the original
            if self.__original:
                neditable.askForSaveFileClosing.connect(self._ask_for_save)
                neditable.fileChanged.connect(self._file_has_been_modified)
            # Editor Signals
            editor.cursor_position_changed[int, int].connect(
                self._update_cursor_position)
            editor.current_line_changed[int].connect(self._set_current_symbol)
            """
            # self.connect(editor, SIGNAL("editorFocusObtained()"),
            #             self._editor_with_focus)
            editor.editorFocusObtained.connect(self._editor_with_focus)
            neditable.fileSaved['PyQt_PyObject'].connect(
                self._update_combo_info)
            neditable.fileSaved['PyQt_PyObject'].connect(
                self._update_symbols)
            editor.modificationChanged[bool].connect(self._editor_modified)
            neditable.checkersUpdated.connect(self._show_notification_icon)

            # Connect file system signals only in the original
            neditable.fileClosing['PyQt_PyObject'].connect(self._close_file)
            if self.__original:
                neditable.askForSaveFileClosing['PyQt_PyObject'].connect(
                    self._ask_for_save)

                neditable.fileChanged['PyQt_PyObject'].connect(
                    self._file_has_been_modified)
                self.info_bar.reloadClicked.connect(neditable.reload_file)

            # Load Symbols
            self._load_symbols(neditable)
            """

    def show_combo_file(self):
        self.bar.combo.showPopup()

    def show_combo_symbol(self):
        self.bar.symbols_combo.showPopup()

    def show_combo_set_language(self):
        self.bar.set_language_combo.showPopup()

    def unlink_editors(self):
        for index in range(self.stacked.count()):
            widget = self.stacked.widget(index)
            # widget.setDocument(QsciDocument())

    def clone(self):
        combo = ComboEditor()
        for neditable in self.bar.get_editables():
            combo.add_editor(neditable)
        return combo

    def split_editor(self, orientation):
        new_combo = self.clone()
        self.splitEditor.emit(self, new_combo, orientation)
        # new_widget = ComboEditor()
        # for neditable in self.bar.get_editables():
        #    new_widget.add_editor(neditable)
        # self.splitEditor.emit(self, new_widget, orientation_vertical)
        # for neditable in self.bar.get_editables():
        #    new_widget.add_editor(neditable)
        # self.splitEditor.emit(self, new_widget, orientationVertical)
        # self.emit(SIGNAL("splitEditor(PyQt_PyObject, PyQt_PyObject, bool)"),
        #          self, new_widget, orientationVertical)

    def undock_editor(self):
        new_combo = ComboEditor()
        for neditable in self.bar.get_editables():
            new_combo.add_editor(neditable)
        self.__undocked.append(new_combo)
        new_combo.setWindowTitle("NINJA-IDE")
        editor = self.current_editor()
        new_combo.set_current(editor.neditable)
        new_combo.resize(700, 500)
        new_combo.about_to_close_combo_editor.connect(self._remove_undock)
        new_combo.show()

    def _remove_undock(self):
        widget = self.sender()
        self.__undocked.remove(widget)

    def close_current_file(self):
        self.bar.about_to_close_file()

    def _close_file(self, neditable):
        index = self.bar.close_file(neditable)
        layoutItem = self.stacked.takeAt(index)
        # neditable.editor.completer.cc.unload_module()
        self._add_to_last_opened(neditable.file_path)
        layoutItem.widget().deleteLater()

        if self.stacked.isEmpty():
            self.bar.hide()
            self.allFilesClosed.emit()

    def _add_to_last_opened(self, path):
        if path not in settings.LAST_OPENED_FILES:
            settings.LAST_OPENED_FILES.append(path)
            if len(settings.LAST_OPENED_FILES) > settings.MAX_REMEMBER_TABS:
                self.__lastOpened = self.__lastOpened[1:]
            print("RecentTabsModified")
            # self.emit(SIGNAL("recentTabsModified()"))

    def _editor_with_focus(self):
        # if self._main_container.current_widget is not self:
        self._main_container.combo_area = self
        editor = self.current_editor()
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
        self.info_bar.show_message(translations.TR_FILE_MODIFIED_OUTSIDE)
        # val = QMessageBox.No
        # fileName = neditable.file_path
        # val = QMessageBox.question(
        #    self, translations.TR_FILE_HAS_BEEN_MODIFIED,
        #    "%s%s" % (fileName, translations.TR_FILE_MODIFIED_OUTSIDE),
        #    QMessageBox.Yes | QMessageBox.No)
        # if val == QMessageBox.Yes:
        #    neditable.reload_file()

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
            editor = self.current_editor()
            self._update_cursor_position(ignore_sender=True)
            editor.setFocus()
            self._main_container.current_editor_changed(
                neditable.file_path)
            self._load_symbols(neditable)
            # self._show_file_in_explorer(neditable.file_path)
            neditable.update_checkers_display()

    def widget(self, index):
        return self.stacked.widget(index)

    def count(self):
        """Return the number of editors opened."""
        return self.stacked.count()

    def _update_cursor_position(self, line=0, col=0, ignore_sender=False):
        obj = self.sender()
        editor = self.current_editor()
        # Check if it's current to avoid signals from other splits.
        if ignore_sender or editor == obj:
            line += 1
            self.bar.update_line_col(line, col)

    def _set_current_symbol(self, line, ignore_sender=False):
        obj = self.sender()
        editor = self.current_editor()
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
        # FIXME: index 0 invalid
        line = self._symbols_index[index]
        editor = self.current_editor()
        editor.go_to_line(line)

    def _update_symbols(self, neditable):
        editor = self.current_editor()
        # Check if it's current to avoid signals from other splits.
        if editor == neditable.editor:
            self._load_symbols(neditable)

    def _update_combo_info(self, neditable):
        self.bar.update_item_text(neditable, neditable.display_name)
        self._main_container.current_editor_changed(neditable.file_path)

    def _load_symbols(self, neditable):
        symbols_handler = handlers.get_symbols_handler('py')
        source = neditable.editor.text
        source = source.encode(neditable.editor.encoding)
        symbols, symbols_simplified = symbols_handler.obtain_symbols(
            source, simple=True)
        self._symbols_index = sorted(symbols_simplified.keys())
        symbols_simplified = sorted(
            list(symbols_simplified.items()), key=lambda x: x[0])
        self.bar.add_symbols(symbols_simplified)
        line, _ = neditable.editor.cursor_position
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
                # FIXME: sucks
                else:
                    icon = QIcon(checker.checker_icon)
                break
        self.bar.update_item_icon(neditable, icon)

    def show_menu_navigation(self):
        self.bar.code_navigator.show_menu_navigation()

    def closeEvent(self, event):
        self.about_to_close_combo_editor.emit()
        # self.emit(SIGNAL("aboutToCloseComboEditor()"))
        super(ComboEditor, self).closeEvent(event)

    def reject(self):
        if not self.__original:
            super(ComboEditor, self).reject()


class ActionBar(ui_tools.StyledBar):
    """
    SIGNALS:
    @changeCurrent(PyQt_PyObject)
    @runFile(QString)
    @reopenTab(QString)
    @recentTabsModified()
    """
    change_current = pyqtSignal('PyQt_PyObject', int)
    splitEditor = pyqtSignal(bool)
    runFile = pyqtSignal('QString')
    closeSplit = pyqtSignal()
    addToProject = pyqtSignal('QString')
    showFileInExplorer = pyqtSignal('QString')
    goToSymbol = pyqtSignal(int)
    undockEditor = pyqtSignal()
    reopenTab = pyqtSignal('QString')

    def __init__(self, main_combo=False):
        super(ActionBar, self).__init__()
        # self.setObjectName("actionbar")
        self.setProperty('gradient', True)
        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(0)

        # self.lbl_checks = QLabel('')
        # self.lbl_checks.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        # self.lbl_checks.setFixedWidth(48)
        # self.lbl_checks.setVisible(False)
        # hbox.addWidget(self.lbl_checks)
        # self.combo = ComboFiles()
        self.combo_files = QComboBox()
        self.combo_files.setProperty("border", True)
        # self.combo_files.setProperty("border_bottom", True)
        self.combo_files.setProperty("gradient", True)
        self.combo_files.setSizeAdjustPolicy(
            QComboBox.AdjustToMinimumContentsLengthWithIcon)
        # self.combo.setIconSize(QSize(16, 16))
        # model = QStandardItemModel()
        # self.combo.setModel(model)
        # self.combo.view().setDragDropMode(QAbstractItemView.InternalMove)
        self.combo_files.setMaximumWidth(300)
        self.combo_files.currentIndexChanged[int].connect(self.current_changed)
        # self.combo.setObjectName("combotab")
        # self.connect(self.combo, SIGNAL("currentIndexChanged(int)"),
        #             self.current_changed)
        self.combo_files.setToolTip(translations.TR_COMBO_FILE_TOOLTIP)
        self.combo_files.setContextMenuPolicy(Qt.CustomContextMenu)
        self.combo_files.customContextMenuRequested.connect(
            self._context_menu_requested)
        hbox.addWidget(self.combo_files)

        self.symbols_combo = QComboBox()
        # self.symbols_combo.setStyleSheet("QComboBox { combobox-popup: 0; }")
        self.symbols_combo.setProperty("border", True)
        # self.symbols_combo.setProperty("border_bottom", True)
        self.symbols_combo.setProperty("gradient", True)
        self.symbols_combo.setSizeAdjustPolicy(
            QComboBox.AdjustToMinimumContentsLengthWithIcon)
        # self.symbols_combo.setIconSize(QSize(16, 16))
        self.symbols_combo.setObjectName("combo_symbols")
        self.symbols_combo.activated[int].connect(self.current_symbol_changed)
        # self.connect(self.symbols_combo, SIGNAL("activated(int)"),
        #             self.current_symbol_changed)
        hbox.addWidget(self.symbols_combo)


        self.code_navigator = CodeNavigator()
        hbox.addWidget(self.code_navigator)
        # FIXME: set property for other themes
        self._pos_text = "Line: %d, Col: %d"
        # self.lbl_position = QLabel(self._pos_text % (0, 0))
        # self._go_to_line_widget = go_to_line.GoToLine(self)
        # self.lbl_position = ui_tools.ClickeableLabel(self._pos_text % (0, 0))
        self.lbl_position = QLabel()
        # self.lbl_position.setProperty("border_bottom", True)
        self.lbl_position.setProperty("gradient", True)
        self.lbl_position.setText(self._pos_text % (0, 0))
        # self.lbl_position.setAutoFillBackground(True)
        # self.lbl_position.clicked.connect(self._on_lbl_position_clicked)
        # FIXME: falla con split. ARREGLADO
        margin = self.style().pixelMetric(
            QStyle.PM_LayoutHorizontalSpacing) / 2
        self.lbl_position.setContentsMargins(margin, 0, margin, 0)
        self.lbl_position.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        hbox.addWidget(self.lbl_position)

        # self.btn_close = QPushButton(
        #    self.style().standardIcon(QStyle.SP_DialogCloseButton), '')
        # self.btn_close.setIconSize(QSize(16, 16))
        self.btn_close = QToolButton()
        # self.btn_close.setProperty("border_bottom", True)
        self.btn_close.setProperty("gradient", True)
        # self.btn_close.setAutoRaise(True)
        # self.btn_close.setFixedHeight(24)
        # self.btn_close.setIcon(QIcon(":img/close"))

        if main_combo:
            self.btn_close.setIcon(
                ui_tools.colored_icon(
                    ':img/close', NTheme.get_color('IconBaseColor')))
            self.btn_close.setToolTip(translations.TR_CLOSE_FILE)
            self.btn_close.clicked.connect(self.about_to_close_file)
        else:
            self.btn_close.setIcon(
                ui_tools.colored_icon(
                    ':img/close', "#ff9222"))
            self.btn_close.setToolTip(translations.TR_CLOSE_SPLIT)
            self.btn_close.clicked.connect(self.close_split)
        self.btn_close.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        hbox.addWidget(self.btn_close)

        # Added for set language
        self._setter_language = set_language.SetLanguageFile()

    # def _on_lbl_position_clicked(self):
    #    main_container = IDE.get_service("main_container")
    #    editor_widget = main_container.get_current_editor()
        # self._go_to_line_widget.set_line_count(editor_widget.line_count())
        # self._go_to_line_widget.show()

    def resizeEvent(self, event):
        super(ActionBar, self).resizeEvent(event)
        if event.size().width() < 400:
            self.symbols_combo.hide()
            self.code_navigator.hide()
            self.lbl_position.hide()
        else:
            self.symbols_combo.show()
            self.code_navigator.show()
            self.lbl_position.show()

    def add_item(self, text, neditable):
        """Add a new item to the combo and add the neditable data."""

        self.combo_files.addItem(text, neditable)
        self.combo_files.setCurrentIndex(self.combo_files.count() - 1)

    def get_editables(self):
        editables = []
        for index in range(self.combo_files.count()):
            neditable = self.combo_files.itemData(index)
            editables.append(neditable)
        return editables

    def add_symbols(self, symbols):
        """Add the symbols to the symbols's combo."""

        mo = Model(symbols)
        self.symbols_combo.setModel(mo)
        # self.symbols_combo.clear()
        # for symbol in symbols:
        #    data = symbol[1]
        #    if data[1] == 'f':
        #        icon = QIcon(":img/function")
        #    else:
        #        icon = QIcon(":img/class")
        #    self.symbols_combo.addItem(icon, data[0])

    def set_current_symbol(self, index):
        self.symbols_combo.setCurrentIndex(index + 1)

    def update_item_icon(self, neditable, icon):
        index = self.combo_files.findData(neditable)
        self.combo_files.setItemIcon(index, icon)

    def update_item_text(self, neditable, text):
        index = self.combo_files.findData(neditable)
        self.combo_files.setItemText(index, text)

    def current_changed(self, index):
        """Change the current item in the combo."""
        neditable = self.combo_files.itemData(index)
        self.change_current.emit(neditable, index)
        # self.emit(SIGNAL("changeCurrent(PyQt_PyObject, int)"),
        #            neditable, index)

    def current_symbol_changed(self, index):
        """Change the current symbol in the combo."""
        if index == 0:
            return
        self.goToSymbol.emit(index - 1)

    def set_language_combo_changed(self, index):
        """Change the current language of editor."""
        self._setter_language.set_language_to_editor(index)

    def update_line_col(self, line, col):
        """Update the line and column position."""
        self.lbl_position.setText(self._pos_text % (line, col))

    def _context_menu_requested(self, point):
        """Display context menu for the combo file."""
        if self.combo_files.count() == 0:
            # If there is not an Editor opened, don't show the menu
            return
        menu = QMenu()
        # actionAdd = menu.addAction(translations.TR_ADD_TO_PROJECT)
        # actionRun = menu.addAction(translations.TR_RUN_FILE)
        # menuSyntax = menu.addMenu(translations.TR_CHANGE_SYNTAX)
        show_folder = menu.addAction("Show Containing Folder")
        # self._create_menu_syntax(menuSyntax)
        menu.addSeparator()
        # actionClose = menu.addAction(translations.TR_CLOSE_FILE)
        # actionCloseAll = menu.addAction(translations.TR_CLOSE_ALL_FILES)
        # actionCloseAllNotThis = menu.addAction(
        #    translations.TR_CLOSE_OTHER_FILES)
        # menu.addSeparator()
        # actionSplitH = menu.addAction(translations.TR_SPLIT_VERTICALLY)
        # actionSplitV = menu.addAction(translations.TR_SPLIT_HORIZONTALLY)
        # menu.addSeparator()
        # actionCopyPath = menu.addAction(
        #    translations.TR_COPY_FILE_PATH_TO_CLIPBOARD)
        # actionShowFileInExplorer = menu.addAction(
        #    translations.TR_SHOW_FILE_IN_EXPLORER)
        # actionReopen = menu.addAction(translations.TR_REOPEN_FILE)
        action_undock = menu.addAction(translations.TR_UNDOCK_EDITOR)
        # if len(settings.LAST_OPENED_FILES) == 0:
        #    actionReopen.setEnabled(False)

        # set language action
        menu_set_language = menu.addMenu(translations.TR_SET_LANGUAGE)
        self._set_list_languages(menu_set_language)

        # Connect actions
        action_undock.triggered.connect(self._undock_editor)
        show_folder.triggered.connect(self._show_containing_folder)
        # self.connect(actionSplitH, SIGNAL("triggered()"),
        #             lambda: self._split(False))
        # self.connect(actionSplitV, SIGNAL("triggered()"),
        #             lambda: self._split(True))
        # self.connect(actionRun, SIGNAL("triggered()"),
        #             self._run_this_file)
        # self.connect(actionAdd, SIGNAL("triggered()"),
        #             self._add_to_project)
        # self.connect(actionClose, SIGNAL("triggered()"),
        #             self.about_to_close_file)
        # self.connect(actionCloseAllNotThis, SIGNAL("triggered()"),
        #             self._close_all_files_except_this)
        # self.connect(actionCloseAll, SIGNAL("triggered()"),
        #             self._close_all_files)
        # self.connect(actionCopyPath, SIGNAL("triggered()"),
        #             self._copy_file_location)
        # self.connect(actionShowFileInExplorer, SIGNAL("triggered()"),
        #             self._show_file_in_explorer)
        # self.connect(actionReopen, SIGNAL("triggered()"),
        #             self._reopen_last_tab)
        # self.connect(actionUndock, SIGNAL("triggered()"),
        #             self._undock_editor)

        menu.exec_(QCursor.pos())

    def _set_list_languages(self, menu_set_language):
        for l in self._setter_language.get_list_of_language():
            if l is None:
                continue
            action = menu_set_language.addAction(l)
            action.triggered.connect(lambda checked, language=l:
                                     self._set_language_action(language))

    def _set_language_action(self, language):
        self._setter_language.set_language_to_editor(language)

    def _show_containing_folder(self):
        # FIXME: mover y cross platform
        main_container = IDE.get_service("main_container")
        editor_widget = main_container.get_current_editor()
        filename = editor_widget.file_path
        import subprocess
        from ninja_ide.core.file_handling import file_manager
        folder = file_manager.get_folder(filename)
        subprocess.call(["xdg-open", folder])

    def _create_menu_syntax(self, menuSyntax):
        """Create Menu with the list of syntax supported."""
        syntax = list(settings.SYNTAX.keys())
        syntax.sort()
        for syn in syntax:
            menuSyntax.addAction(syn)
            # self.connect(menuSyntax, SIGNAL("triggered(QAction*)"),
            #             self._reapply_syntax)

    def _reapply_syntax(self, syntaxAction):
        # TODO
        if [self.currentIndex(), syntaxAction] != self._resyntax:
            self._resyntax = [self.currentIndex(), syntaxAction]
            # self.emit(SIGNAL("syntaxChanged(QWidget, QString)"),
            #          self.currentWidget(), syntaxAction.text())

    def set_current_file(self, neditable):
        index = self.combo_files.findData(neditable)
        self.combo_files.setCurrentIndex(index)

    def set_current_by_index(self, index):
        self.combo_files.setCurrentIndex(index)

    @pyqtSlot()
    def about_to_close_file(self, index=None):
        """Close the NFile object."""

        parent = self.parent().parentWidget()  # Splitter
        if parent.count() > 1:
            return
        if index is None:
            index = self.combo_files.currentIndex()
        neditable = self.combo_files.itemData(index)
        if neditable:
            neditable.nfile.close()

    def close_split(self):
        self.closeSplit.emit()
        # self.emit(SIGNAL("closeSplit()"))

    def close_file(self, neditable):
        """Receive the confirmation to close the file."""
        index = self.combo_files.findData(neditable)
        self.combo_files.removeItem(index)
        return index

    def _run_this_file(self):
        """Execute the current file."""
        neditable = self.combo.itemData(self.combo.currentIndex())
        print("Emitir runFile")
        # self.emit(SIGNAL("runFile(QString)"), neditable.file_path)

    def _add_to_project(self):
        """Emit a signal to let someone handle the inclusion of the file
        inside a project."""
        neditable = self.combo.itemData(self.combo.currentIndex())
        print("Emitir adToProject")
        # self.emit(SIGNAL("addToProject(QString)"), neditable.file_path)

    def _show_file_in_explorer(self):
        '''Triggered when the "Show File in Explorer" context
        menu action is selected. Emits the "showFileInExplorer(QString)"
        signal with the current file's full path as argument.'''
        neditable = self.combo.itemData(self.combo.currentIndex())
        print("Emitir showFileInExplorer")
        # self.emit(SIGNAL("showFileInExplorer(QString)"), neditable.file_path)

    def _reopen_last_tab(self):
        print("Emitir reopenTab y recentTabsModified")
        # self.emit(SIGNAL("reopenTab(QString)"),
        #          settings.LAST_OPENED_FILES.pop())
        # self.emit(SIGNAL("recentTabsModified()"))

    def _undock_editor(self):
        self.undockEditor.emit()

    def _split(self, orientation):
        print("emitir splitEditor")
        # self.emit(SIGNAL("splitEditor(bool)"), orientation)

    def _copy_file_location(self):
        """Copy the path of the current opened file to the clipboard."""
        neditable = self.combo.itemData(self.combo.currentIndex())
        QApplication.clipboard().setText(neditable.file_path,
                                         QClipboard.Clipboard)

    def _close_all_files(self):
        """Close all the files opened."""
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

    def showPopup(self):
        self.showComboSelector.emit()


class CodeNavigator(QWidget):

    nextPressed = pyqtSignal(int, bool)  # Operation, forward
    previousPressed = pyqtSignal(int, bool)

    def __init__(self):
        super(CodeNavigator, self).__init__()
        self.setContextMenuPolicy(Qt.DefaultContextMenu)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setContentsMargins(0, 0, 0, 0)
        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(0, 0, 0, 0)
        if settings.IS_MAC_OS:
            hbox.setSpacing(10)
        else:
            hbox.setSpacing(0)
        self.btnPrevious = QToolButton()
        self.btnPrevious.clicked.connect(self._on_previous_pressed)
        self.btnPrevious.setIcon(ui_tools.get_icon('navigate-left'))
        self.btnPrevious.setProperty("gradient", True)
        self.btnPrevious.setToolTip(translations.TR_TOOLTIP_NAV_BUTTONS)
        self.btnNext = QToolButton()
        self.btnNext.clicked.connect(self._on_next_pressed)
        self.btnNext.setIcon(ui_tools.get_icon('navigate-right'))
        self.btnNext.setProperty("gradient", True)
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

        # self.connect(self.codeAction, SIGNAL("triggered()"),
        #             self._show_code_nav)
        # self.connect(self.breakpointsAction, SIGNAL("triggered()"),
        #             self._show_breakpoints)
        # self.connect(self.bookmarksAction, SIGNAL("triggered()"),
        #             self._show_bookmarks)

    def contextMenuEvent(self, event):
        self.show_menu_navigation()

    def show_menu_navigation(self):
        self.menuNavigate.exec_(QCursor.pos())

    @pyqtSlot()
    def _on_previous_pressed(self):
        self.previousPressed.emit(self.operation, False)

    @pyqtSlot()
    def _on_next_pressed(self):
        self.previousPressed.emit(self.operation, True)

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


class InfoBar(QFrame):

    reloadClicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        pal = QPalette()
        pal.setColor(QPalette.Window, QColor("#6a6ea9"))
        pal.setColor(QPalette.WindowText, QColor("white"))
        # self.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.setAutoFillBackground(True)
        self.setPalette(pal)

        hbox = QHBoxLayout(self)

        self.message = QLabel("")
        # self.message.setWordWrap(Qt.TextWordWrap)
        hbox.addWidget(self.message)
        hbox.addSpacerItem(QSpacerItem(1, 0, QSizePolicy.Expanding))
        btn_reload = QPushButton("Reload")
        hbox.addWidget(btn_reload)
        btn_cancel = QPushButton("Cancel")
        hbox.addWidget(btn_cancel)

        # Connections
        btn_reload.clicked.connect(self.__on_reload_clicked)
        btn_cancel.clicked.connect(self.hide)

    def __on_reload_clicked(self):
        self.reloadClicked.emit()
        self.hide()

    def show_message(self, text):
        self.message.setText(text)
        if not self.isVisible():
            self.show()


class Model(QAbstractItemModel):
    def __init__(self, data):
        QAbstractItemModel.__init__(self)
        self.__data = data

    def rowCount(self, parent):
        return len(self.__data) + 1

    def columnCount(self, parent):
        return 1

    def index(self, row, column, parent):
        return self.createIndex(row, column, parent)

    def parent(self, child):
        return QModelIndex()

    def data(self, index, role):
        if not index.isValid():
            return
        if not index.parent().isValid() and index.row() == 0:
            if role == Qt.DisplayRole:
                if self.rowCount(index) > 1:
                    return '<Select Symbol>'
                return '<No Symbols>'
            return
        if role == Qt.DisplayRole:
            return self.__data[index.row() - 1][1][0]
        elif role == Qt.DecorationRole:
            _type = self.__data[index.row() - 1][1][1]
            if _type == 'f':
                icon = QIcon(":img/function")
            elif _type == 'c':
                icon = QIcon(":img/class")
            return icon
