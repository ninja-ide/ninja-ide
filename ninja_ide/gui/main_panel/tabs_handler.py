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

from PyQt4.QtGui import QFrame
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL
from PyQt4.QtDeclarative import QDeclarativeView

from ninja_ide.gui.ide import IDE
from ninja_ide.tools import ui_tools


class TabsHandler(QFrame):

    def __init__(self, parent=None):
        super(TabsHandler, self).__init__(None,
            Qt.FramelessWindowHint | Qt.Popup)
        self._main_container = parent
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background:transparent;")
        # Create the QML user interface.
        self.view = QDeclarativeView()
        self.view.setResizeMode(QDeclarativeView.SizeRootObjectToView)
        self.view.setSource(ui_tools.get_qml_resource("TabsHandler.qml"))
        self._root = self.view.rootObject()
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        vbox.addWidget(self.view)

        self._model = {}
        self._max_index = 0

        self.connect(self._root, SIGNAL("open(QString)"), self._open)

    def _open(self, path):
        self._main_container.open_file(path)
        index = self._model[path]
        self._max_index = max(self._max_index, index) + 1
        self._model[path] = self._max_index
        self.hide()

    def _add_model(self):
        ninjaide = IDE.get_service("ide")
        files = ninjaide.filesystem.get_files()
        files_data = list(files.values())
        # Update model
        old = set(self._model.keys())
        new = set([nfile.file_path for nfile in files_data])
        result = old - new
        for item in result:
            del self._model[item]
        model = []
        for nfile in files_data:
            if nfile.file_path not in self._model:
                self._model[nfile.file_path] = 0
            neditable = ninjaide.get_or_create_editable(nfile.file_path)
            checkers = neditable.sorted_checkers
            checks = []
            for items in checkers:
                checker, color, _ = items
                if checker.dirty:
                    checks.append(
                        {"checker_text": checker.dirty_text,
                         "checker_color": color})
            modified = neditable.document.isModified()
            model.append([nfile.file_name, nfile.file_path, checks, modified])
        model = sorted(model, key=lambda x: self._model[x[1]], reverse=True)
        self._root.set_model(model)

    def showEvent(self, event):
        self._add_model()
        width = max(self._main_container.width() / 3, 300)
        height = max(self._main_container.height() / 2, 400)
        self.view.setFixedWidth(width)
        self.view.setFixedHeight(height)
        super(TabsHandler, self).showEvent(event)
        self._root.show_animation()
        point = self._main_container.mapToGlobal(self.view.pos())
        y_diff = self._main_container.combo_header_size
        self.move(point.x(), point.y() + y_diff)
        self.view.setFocus()

    def next_item(self):
        if not self.isVisible():
            self.show()
        self._root.next_item()

    def previous_item(self):
        if not self.isVisible():
            self.show()
        self._root.previous_item()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.hide()
        elif (event.modifiers() == Qt.ControlModifier and
                event.key() == Qt.Key_PageDown) or event.key() == Qt.Key_Down:
            self._root.next_item()
        elif (event.modifiers() == Qt.ControlModifier and
                event.key() == Qt.Key_PageUp) or event.key() == Qt.Key_Up:
            self._root.previous_item()
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self._root.open_item()
        super(TabsHandler, self).keyPressEvent(event)