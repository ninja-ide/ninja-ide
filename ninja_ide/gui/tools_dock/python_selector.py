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

from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QVBoxLayout

from PyQt5.QtQuickWidgets import QQuickWidget

from PyQt5.QtCore import Qt
from PyQt5.QtCore import QPoint

from ninja_ide.tools import ui_tools
from ninja_ide.gui.ide import IDE


class PythonSelector(QWidget):

    def __init__(self, btn, parent=None):
        super().__init__(parent, Qt.FramelessWindowHint | Qt.Popup)
        self.btn_selector = btn
        self.setAttribute(Qt.WA_TranslucentBackground)
        box = QVBoxLayout(self)
        self.view = QQuickWidget()
        self.view.setClearColor(Qt.transparent)
        self.setFixedWidth(400)
        self.setFixedHeight(200)
        self.view.setResizeMode(QQuickWidget.SizeRootObjectToView)
        self.view.setSource(ui_tools.get_qml_resource("PythonChooser.qml"))

        self._root = self.view.rootObject()
        box.addWidget(self.view)

        self._model = []
        self._root.pythonSelected.connect(self.set_python_interpreter)

    def setVisible(self, visible):
        super().setVisible(visible)
        self.btn_selector.setChecked(visible)

    def showEvent(self, event):
        ide = IDE.get_service("ide")
        move_to = ide.mapToGlobal(QPoint(0, 0))
        move_to -= QPoint(
            -ide.width() + self.width() - 5,
            -ide.height() + self.height() + 20)
        self.move(move_to)
        self._root.setModel(self._model)
        super().showEvent(event)

    def set_python_interpreter(self, path):
        ide = IDE.get_service("ide")
        obj = ide.get_interpreter(path)
        ide.set_interpreter(path)

        self.btn_selector.setText(obj.display_name)
        self.btn_selector.setToolTip(obj.path)

    def add_model(self, interpreters):
        self._model.clear()
        model = []
        for interpreter in interpreters:
            model.append([
                interpreter.display_name,
                interpreter.path,
                interpreter.exec_path
            ])
        self._model = model
        locator = IDE.get_service("interpreter")
        self.btn_selector.setText(locator.current.display_name)
        self.btn_selector.setEnabled(True)

    def hideEvent(self, event):
        super().hideEvent(event)
        self._root.clearModel()
