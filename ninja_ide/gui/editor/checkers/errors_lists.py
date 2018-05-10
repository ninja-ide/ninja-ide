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
import os
import uuid

from PyQt5.QtWidgets import (
    QDialog,
    QWidget,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QListWidget,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QListWidgetItem
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import (
    pyqtSignal,
    pyqtSlot,
    QModelIndex,
    QAbstractItemModel,
    QTimer,
    Qt
)
from PyQt5.QtQuickWidgets import QQuickWidget
from ninja_ide.core import settings
from ninja_ide import resources
from ninja_ide.gui.ide import IDE
from ninja_ide.tools import ui_tools
from ninja_ide import translations
from ninja_ide.gui.explorer.explorer_container import ExplorerContainer


class ErrorsWidget(QDialog):

    dockWidget = pyqtSignal('PyQt_PyObject')
    undockWidget = pyqtSignal('PyQt_PyObject')

    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowStaysOnTopHint)
        box = QVBoxLayout(self)
        box.setContentsMargins(0, 0, 0, 0)
        box.setSpacing(0)
        # Errors
        # self._list_errors = QListWidget()
        # self._list_errors.setWordWrap(True)
        # self._list_errors.setSortingEnabled(True)
        # # PEP8
        # self._list_pep8 = QListWidget()
        # self._list_pep8.setWordWrap(True)
        # self._list_pep8.setSortingEnabled(True)
        hbox = QHBoxLayout()
        hbox.setContentsMargins(5, 3, 5, 3)
        self._list = ErrorsList()
        hbox.addWidget(self._list)
        # if settings.CHECK_STYLE:
        #     self._btn_pep8 = QPushButton("PEP8: ON")
        # else:
        #     self._btn_pep8 = QPushButton("PEP8: OFF")
        # self._pep8_label = QLabel("PEP8 Errors: %s" % 0)
        # hbox.addWidget(self._pep8_label)
        # hbox.addSpacerItem(QSpacerItem(1, 0, QSizePolicy.Expanding))
        # hbox.addWidget(self._btn_pep8)
        box.addLayout(hbox)
        # box.addWidget(self._list_pep8)
        # box.addWidget(self._list_errors)

        # Connections
        # self._list_errors.clicked.connect(self.__on_pep8_item_selected)
        # self._list_pep8.clicked.connect(self.__on_pep8_item_selected)
        # self._btn_pep8.clicked.connect(self._turn_on_off_pep8)
        # Register service
        IDE.register_service("tab_errors", self)
        ExplorerContainer.register_tab(translations.TR_TAB_ERRORS, self)

    # def install_tab(self):
    #     ide = IDE.get_service('ide')
        # self.connect(ide, SIGNAL("goingDown()"), self.close)

    @pyqtSlot()
    def __on_pep8_item_selected(self):
        main_container = IDE.get_service("main_container")
        neditor = main_container.get_current_editor()
        if neditor is not None:
            # lineno = self._list_pep8.currentItem().data(Qt.UserRole)
            # neditor.go_to_line(lineno)
            neditor.setFocus()

    @pyqtSlot()
    def _turn_on_off_pep8(self):
        """Change the status of the lint checker state"""
        # settings.CHECK_STYLE = not settings.CHECK_STYLE
        # if settings.CHECK_STYLE:
        #     self._btn_pep8.setText("PEP8: ON")
        #     self._list_pep8.show()
        # else:
        #     self._btn_pep8.setText("PEP8: OFF")
        #     self._list_pep8.hide()
        # TODO: emit a singal to main container

    def refresh_pep8_list(self, errors):
        print(len(errors))
        # self._list_pep8.clear()
        # for lineno, message in errors.items():
        #     lineno_str = 'L%s\t' % str(lineno + 1)
        #     item = QListWidgetItem(lineno_str + message.split('\n')[0])
        #     item.setData(Qt.UserRole, lineno)
        #     self._list_pep8.addItem(item)
        # self._pep8_label.setText("PEP8 Errors: %s" % len(errors))

    def refresh_error_list(self, errors):
        print(len(errors))
        # self._outRefresh = False
        # self._list_errors.clear()
        for lineno, message in errors.items():
            print(lineno, message)
            # lineno_str = 'L%s\t' % str(lineno + 1)
            # item = QListWidgetItem(lineno_str + message[0])
            # item.setToolTip(lineno_str + message[0])
            # item.setData(Qt.UserRole, lineno)
            # self._list_errors.addItem(item)

        # self.errorsLabel.setText(self.tr("Static Errors: %s") %
        #                          len(errors))
        # self._outRefresh = True

    def reject(self):
        if self.parent() is None:
            self.dockWidget.emit(self)

    def closeEvent(self, event):
        self.dockWidget.emit(self)
        event.ignore()


class ErrorsList(QWidget):

    def __init__(self, parent=None):
        super(ErrorsList, self).__init__()
        # super(ErrorsList, self).__init__(None, Qt.Popup)
        # self.setAttribute(Qt.WA_TranslucentBackground)
        # self.setFixedWidth(500)
        # self.setFixedHeight(400)
        # self._main_container = parent
        # Create the QML user interface.
        self.view = QQuickWidget()
        self.view.rootContext().setContextProperty(
            "theme", resources.QML_COLORS)
        self.view.setResizeMode(QQuickWidget.SizeRootObjectToView)
        self.view.setSource(ui_tools.get_qml_resource("ErrorsList.qml"))
        self._root = self.view.rootObject()
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        vbox.addWidget(self.view)

        # self._model = {}
        # self._temp_files = {}
        # self._max_index = 0

        # self._root.open.connect(self._open)
        # self._root.close.connect(self._close)
        # self._root.fuzzySearch.connect(self._fuzzy_search)
        # self._root.hide.connect(self.hide)

    def _open(self, path, temp, project):
        if project:
            path = os.path.join(os.path.split(project)[0], path)
            self._main_container.open_file(path)
        elif temp:
            nfile = self._temp_files[temp]
            ninjaide = IDE.get_service("ide")
            neditable = ninjaide.get_or_create_editable(nfile=nfile)
            self._main_container.combo_area.set_current(neditable)
        else:
            self._main_container.open_file(path)
            index = self._model[path]
            self._max_index = max(self._max_index, index) + 1
            self._model[path] = self._max_index
        self.hide()

    def _close(self, path, temp):
        if temp:
            nfile = self._temp_files.get(temp, None)
        else:
            ninjaide = IDE.get_service("ide")
            nfile = ninjaide.get_or_create_nfile(path)
        if nfile is not None:
            nfile.close()

    def _add_model(self):
        ninjaide = IDE.get_service("ide")
        # files = ninjaide.opened_files
        # # Update model
        # old = set(self._model.keys())
        # new = set([nfile.file_path for nfile in files])
        # result = old - new
        # for item in result:
        #     del self._model[item]
        # current_editor = self._main_container.get_current_editor()
        # current_path = None
        # if current_editor:
        #     current_path = current_editor.file_path
        # model = []
        # for nfile in files:
        #     if (nfile.file_path not in self._model and
        #             nfile.file_path is not None):
        #         self._model[nfile.file_path] = 0
        #     neditable = ninjaide.get_or_create_editable(nfile=nfile)
        #     checkers = neditable.sorted_checkers
        #     checks = []
        #     for items in checkers:
        #         checker, color, _ = items
        #         if checker.dirty:
        #             checks.append({
        #                 "checker_text": checker.dirty_text,
        #                 "checker_color": color
        #             })
        #     modified = neditable.editor.is_modified
        #     temp_file = str(uuid.uuid4()) if nfile.file_path is None else ""
        #     filepath = nfile.file_path if nfile.file_path is not None else ""
        #     model.append([nfile.file_name, filepath, checks, modified,
        #                   temp_file])
        #     if temp_file:
        #         self._temp_files[temp_file] = nfile
        # if current_path:
        #     index = self._model[current_path]
        #     self._max_index = max(self._max_index, index) + 1
        #     self._model[current_path] = self._max_index
        # model = sorted(model, key=lambda x: self._model.get(x[1], False),
        #                reverse=True)
        # self._root.set_model(model)

    def showEvent(self, event):
        # self._add_model()
        # editor_widget = self._main_container.get_current_editor()
        # widget = self._main_container.get_current_editor()
        # if widget is None:
        #    widget = self._main_container
        # if self._main_container.splitter.count() < 2:
        #    width = max(widget.width() / 2, 400)
        #     height = max(widget.height() / 2, 300)
        # else:
        #    width = widget.width()
        #    height = widget.height()
        # self.view.setFixedWidth(width)
        # self.view.setFixedHeight(height)

        super(ErrorsList, self).showEvent(event)
        # self._root.show_animation()
        # point = editor_widget.mapToGlobal(self.view.pos())
        # self.move(point.x(), point.y())
        # # Trick
        # QTimer.singleShot(100, self.__set_focus)

    def __set_focus(self):
        self.view.setFocus()
        self._root.activateInput()

    def hideEvent(self, event):
        super(ErrorsList, self).hideEvent(event)
        self._temp_files = {}
        self._root.clear_model()
        # Recovery focus
        editor_widget = self._main_container.get_current_editor()
        if editor_widget is not None:
            editor_widget.setFocus()

    def next_item(self):
        if not self.isVisible():
            self.show()
        # self._root.next_item()

    def previous_item(self):
        if not self.isVisible():
            self.show()
        self._root.previous_item()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.hide()
        elif (event.modifiers() == Qt.ControlModifier and
                event.key() == Qt.Key_Tab):
            self._root.next_item()
        elif (event.modifiers() == Qt.ControlModifier and
                event.key() == Qt.Key_PageDown) or event.key() == Qt.Key_Down:
            self._root.next_item()
        elif (event.modifiers() == Qt.ControlModifier and
                event.key() == Qt.Key_PageUp) or event.key() == Qt.Key_Up:
            self._root.previous_item()
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self._root.open_item()
        super(ErrorsList, self).keyPressEvent(event)


"""
from __future__ import absolute_import

from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QListWidget
from PyQt4.QtGui import QListWidgetItem
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QSpacerItem
from PyQt4.QtGui import QSizePolicy
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL

from ninja_ide import translations
from ninja_ide.core import settings
from ninja_ide.gui.ide import IDE
from ninja_ide.gui.explorer.explorer_container import ExplorerContainer


class ErrorsWidget(QDialog):

###############################################################################
# ERRORS WIDGET SIGNALS
###############################################################################
    pep8Activated(bool)
    lintActivated(bool)
###############################################################################

    def __init__(self, parent=None):
        super(ErrorsWidget, self).__init__(parent, Qt.WindowStaysOnTopHint)
        self.pep8 = None
        self._outRefresh = True

        vbox = QVBoxLayout(self)
        self.listErrors = QListWidget()
        self.listErrors.setSortingEnabled(True)
        self.listPep8 = QListWidget()
        self.listPep8.setSortingEnabled(True)
        hbox_lint = QHBoxLayout()
        if settings.FIND_ERRORS:
            self.btn_lint_activate = QPushButton(self.tr("Lint: ON"))
        else:
            self.btn_lint_activate = QPushButton(self.tr("Lint: OFF"))
        self.errorsLabel = QLabel(self.tr("Static Errors: %s") % 0)
        hbox_lint.addWidget(self.errorsLabel)
        hbox_lint.addSpacerItem(QSpacerItem(1, 0, QSizePolicy.Expanding))
        hbox_lint.addWidget(self.btn_lint_activate)
        vbox.addLayout(hbox_lint)
        vbox.addWidget(self.listErrors)
        hbox_pep8 = QHBoxLayout()
        if settings.CHECK_STYLE:
            self.btn_pep8_activate = QPushButton(self.tr("PEP8: ON"))
        else:
            self.btn_pep8_activate = QPushButton(self.tr("PEP8: OFF"))
        self.pep8Label = QLabel(self.tr("PEP8 Errors: %s") % 0)
        hbox_pep8.addWidget(self.pep8Label)
        hbox_pep8.addSpacerItem(QSpacerItem(1, 0, QSizePolicy.Expanding))
        hbox_pep8.addWidget(self.btn_pep8_activate)
        vbox.addLayout(hbox_pep8)
        vbox.addWidget(self.listPep8)

        self.connect(self.listErrors, SIGNAL("itemSelectionChanged()"),
                     self.errors_selected)
        self.connect(self.listPep8, SIGNAL("itemSelectionChanged()"),
                     self.pep8_selected)
        self.connect(self.btn_lint_activate, SIGNAL("clicked()"),
                     self._turn_on_off_lint)
        self.connect(self.btn_pep8_activate, SIGNAL("clicked()"),
                     self._turn_on_off_pep8)

        IDE.register_service('tab_errors', self)
        ExplorerContainer.register_tab(translations.TR_TAB_ERRORS, self)

    def install_tab(self):
        ide = IDE.get_service('ide')
        self.connect(ide, SIGNAL("goingDown()"), self.close)

    def _turn_on_off_lint(self):
        # Change the status of the lint checker state
        settings.FIND_ERRORS = not settings.FIND_ERRORS
        if settings.FIND_ERRORS:
            self.btn_lint_activate.setText(self.tr("Lint: ON"))
            self.listErrors.show()
        else:
            self.btn_lint_activate.setText(self.tr("Lint: OFF"))
            self.listErrors.hide()
        self.emit(SIGNAL("lintActivated(bool)"), settings.FIND_ERRORS)

    def _turn_on_off_pep8(self):
        # Change the status of the lint checker state
        settings.CHECK_STYLE = not settings.CHECK_STYLE
        if settings.CHECK_STYLE:
            self.btn_pep8_activate.setText(self.tr("PEP8: ON"))
            self.listPep8.show()
        else:
            self.btn_pep8_activate.setText(self.tr("PEP8: OFF"))
            self.listPep8.hide()
        self.emit(SIGNAL("pep8Activated(bool)"), settings.CHECK_STYLE)

    def errors_selected(self):
        main_container = IDE.get_service('main_container')
        if main_container:
            editorWidget = main_container.get_current_editor()
            if editorWidget and self._outRefresh:
                lineno = int(self.listErrors.currentItem().data(Qt.UserRole))
                editorWidget.jump_to_line(lineno)
                editorWidget.setFocus()

    def pep8_selected(self):
        main_container = IDE.get_service('main_container')
        if main_container:
            editorWidget = main_container.get_current_editor()
            if editorWidget and self._outRefresh:
                lineno = int(self.listPep8.currentItem().data(Qt.UserRole))
                editorWidget.jump_to_line(lineno)
                editorWidget.setFocus()

    def refresh_pep8_list(self, pep8):
        self._outRefresh = False
        self.listPep8.clear()
        for lineno in pep8:
            linenostr = 'L%s\t' % str(lineno + 1)
            for data in pep8[lineno]:
                item = QListWidgetItem(linenostr + data.split('\n')[0])
                item.setToolTip(linenostr + data.split('\n')[0])
                item.setData(Qt.UserRole, lineno)
                self.listPep8.addItem(item)
        self.pep8Label.setText(self.tr("PEP8 Errors: %s") %
                               len(pep8))
        self._outRefresh = True

    def refresh_error_list(self, errors):
        self._outRefresh = False
        self.listErrors.clear()
        for lineno in errors:
            linenostr = 'L%s\t' % str(lineno + 1)
            for data in errors[lineno]:
                item = QListWidgetItem(linenostr + data)
                item.setToolTip(linenostr + data)
                item.setData(Qt.UserRole, lineno)
                self.listErrors.addItem(item)
        self.errorsLabel.setText(self.tr("Static Errors: %s") %
                                 len(errors))
        self._outRefresh = True

    def clear(self):
        # Clear the widget
        self.listErrors.clear()
        self.listPep8.clear()

    def reject(self):
        if self.parent() is None:
            self.emit(SIGNAL("dockWidget(PyQt_PyObject)"), self)

    def closeEvent(self, event):
        self.emit(SIGNAL("dockWidget(PyQt_PyObject)"), self)
        event.ignore()

"""


class ModelWarningsErrors(QAbstractItemModel):

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

        # return self.__data[index.row() - 1]

        if role == Qt.DisplayRole:
            return self.__data[index.row() - 1][1][0]
        elif role == Qt.DecorationRole:
            _type = self.__data[index.row() - 1][1][1]
            if _type == 'f':
                icon = QIcon(":img/function")
            elif _type == 'c':
                icon = QIcon(":img/class")
            return icon



if settings.SHOW_ERRORS_LIST:
    errorsWidget = ErrorsWidget()
else:
    errorsWidget = None
