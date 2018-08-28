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

from PyQt5.QtWidgets import (
    QDialog,
    QWidget,
    QVBoxLayout,
    QHBoxLayout
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import (
    pyqtSignal,
    QModelIndex,
    QAbstractItemModel,
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
        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        self._list = ErrorsList()
        hbox.addWidget(self._list)
        box.addLayout(hbox)

        IDE.register_service("tab_errors", self)
        ExplorerContainer.register_tab(translations.TR_TAB_ERRORS, self)

    def refresh_pep8_list(self, errors):
        model = []
        for lineno, error in errors.items():
            for content in error:
                pos, message, line_content = content
                model.append([message, line_content, lineno, pos[0]])
        self._list.update_pep8_model(model)

    def refresh_error_list(self, errors):
        model = []
        for lineno, error in errors.items():
            for content in error:
                pos, message, line_content = content
                model.append([message, line_content, lineno, pos[0]])
        self._list.update_error_model(model)

    def reject(self):
        if self.parent() is None:
            self.dockWidget.emit(self)

    def closeEvent(self, event):
        self.dockWidget.emit(self)
        event.ignore()


class ErrorsList(QWidget):

    def __init__(self, parent=None):
        super(ErrorsList, self).__init__()
        self._main_container = IDE.get_service("main_container")
        # Create the QML user interface.
        self.view = QQuickWidget()
        self.view.rootContext().setContextProperty(
            "theme", resources.QML_COLORS)
        # Colors from theme
        warn_bug_colors = {}
        warn_bug_colors["warning"] = resources.COLOR_SCHEME.get("editor.pep8")
        warn_bug_colors["bug"] = resources.COLOR_SCHEME.get("editor.checker")
        self.view.rootContext().setContextProperty("colors", warn_bug_colors)
        self.view.setResizeMode(QQuickWidget.SizeRootObjectToView)
        self.view.setSource(ui_tools.get_qml_resource("ErrorsList.qml"))
        self._root = self.view.rootObject()
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        vbox.addWidget(self.view)

        self._root.open.connect(self._open)

    def _open(self, row):
        self._main_container.editor_go_to_line(row)

    def update_pep8_model(self, model):
        self._root.set_pep8_model(model)

    def update_error_model(self, model):
        self._root.set_error_model(model)


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
