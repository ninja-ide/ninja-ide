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

import os
import re
import uuid

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtQuickWidgets import QQuickWidget

from ninja_ide import resources
from ninja_ide.gui.ide import IDE
from ninja_ide.tools import ui_tools
from ninja_ide.tools.locator import locator
from ninja_ide.tools.logger import NinjaLogger
logger = NinjaLogger(__name__)


class FilesHandler(QWidget):

    def __init__(self, parent=None):
        super(FilesHandler, self).__init__(
            None, Qt.FramelessWindowHint | Qt.Popup)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._main_container = parent
        # Create the QML user interface.
        self.setFixedHeight(300)
        self.setFixedWidth(400)
        self.view = QQuickWidget()
        self.view.rootContext().setContextProperty(
            "theme", resources.QML_COLORS)
        self.view.setResizeMode(QQuickWidget.SizeRootObjectToView)
        self.view.setSource(ui_tools.get_qml_resource("FilesHandler.qml"))
        # self.view.setClearColor(Qt.transparent)
        self._root = self.view.rootObject()
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        vbox.addWidget(self.view)

        self._model = {}
        self._temp_files = {}
        self._max_index = 0

        self._root.open.connect(self._open)
        self._root.close.connect(self._close)
        self._root.fuzzySearch.connect(self._fuzzy_search)
        self._root.hide.connect(self.hide)

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
        # FIXME: when we have splitters?
        if temp:
            nfile = self._temp_files.get(temp, None)
        else:
            ninjaide = IDE.get_service("ide")
            nfile = ninjaide.get_or_create_nfile(path)
        if nfile is not None:
            nfile.close()

    def _fuzzy_search(self, search):
        search = '.+'.join(re.escape(search).split('\\ '))
        pattern = re.compile(search, re.IGNORECASE)

        model = []
        for project_path in locator.files_paths:
            files_in_project = locator.files_paths[project_path]
            base_project = os.path.basename(project_path)
            for file_path in files_in_project:
                file_path = os.path.join(
                    base_project, os.path.relpath(file_path, project_path))
                if pattern.search(file_path):
                    model.append([os.path.basename(file_path), file_path,
                                  project_path])
        self._root.set_fuzzy_model(model)

    def _add_model(self):
        ninjaide = IDE.get_service("ide")
        files = ninjaide.opened_files
        # Update model
        current_editor = self._main_container.get_current_editor()
        current_path = None
        if current_editor is not None:
            current_path = current_editor.file_path
        model = []
        for nfile in files:
            if nfile.file_path is not None and \
                    nfile.file_path not in self._model:
                self._model[nfile.file_path] = 0
            neditable = ninjaide.get_or_create_editable(nfile=nfile)
            checkers = neditable.sorted_checkers
            checks = []
            for item in checkers:
                checker, color, _ = item
                if checker.dirty:
                    checks.append({
                        "checker_text": checker.dirty_text,
                        "checker_color": color
                    })
            modified = neditable.editor.is_modified
            temp_file = str(uuid.uuid4()) if nfile.file_path is None else ""
            filepath = nfile.file_path if nfile.file_path is not None else ""
            model.append([
                nfile.file_name, filepath,
                checks, modified, temp_file])
            if temp_file:
                self._temp_files[temp_file] = nfile
        if current_path is not None:
            index = self._model[current_path]
            self._max_index = max(self._max_index, index) + 1
            self._model[current_path] = self._max_index
        model = sorted(model, key=lambda x: self._model.get(x[1], False),
                       reverse=True)
        self._root.set_model(model)

    def showEvent(self, event):
        self._add_model()
        editor_widget = self._main_container.get_current_editor()
        simple = False
        if editor_widget.height() < 400 or editor_widget.width() < 350:
            width = editor_widget.width()
            height = self._main_container.height() / 3
            simple = True
        else:
            width = max(editor_widget.width() / 3, 550)
            height = max(editor_widget.height() / 2, 400)

        self.setFixedWidth(width)
        self.setFixedHeight(height)

        self._root.setMode(simple)
        super(FilesHandler, self).showEvent(event)
        # self._root.show_animation()
        point = editor_widget.mapToGlobal(self.view.pos())
        self.move(point)
        # Trick
        QTimer.singleShot(100, self.__set_focus)

    def __set_focus(self):
        self.view.setFocus()
        self._root.activateInput()

    def hideEvent(self, event):
        super(FilesHandler, self).hideEvent(event)
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
        super(FilesHandler, self).keyPressEvent(event)
