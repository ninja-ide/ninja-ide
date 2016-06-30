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

from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtQuickWidgets import QQuickWidget

from ninja_ide.tools import ui_tools


class MainSelector(QWidget):
    removeWidget = pyqtSignal(int)
    changeCurrent = pyqtSignal(int)
    ready = pyqtSignal()
    animationCompleted = pyqtSignal()
    closePreviewer = pyqtSignal()
    def __init__(self, parent=None):
        super(MainSelector, self).__init__(parent)
        # Create the QML user interface.
        self.view = QQuickWidget()
        self.view.setResizeMode(QQuickWidget.SizeRootObjectToView)
        self.view.engine().quit.connect(self.hide)
        self.view.setSource(ui_tools.get_qml_resource("MainSelector.qml"))
        self._root = self.view.rootObject()
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        vbox.addWidget(self.view)

        self._root.open[int].connect(self.changeCurrent.emit)
        self._root.open[int].connect(self._clean_removed)
        self._root.ready.connect(self.ready.emit)
        self._root.closePreviewer.connect(self.closePreviewer.emit)
        self._root.animationCompleted.connect(self.animationCompleted.emit)

    def set_model(self, model):
        for index, path, closable in model:
            self.add_to_model(index, path, closable)

    @pyqtSlot(int, "QString", bool)
    def add_to_model(self, i, path, type_state):
        self._root.add_widget(i, path, type_state)

    def set_preview(self, index, preview_path):
        self._root.add_preview(index, preview_path)

    def close_selector(self):
        self._root.close_selector()

    def GoTo_GridPreviews(self):#start_animation
        self._root.start_animation()
        self._root.forceActiveFocus()

    def showPreview(self):
        self._root.showPreview()
        self._root.forceActiveFocus()

    def open_item(self, index):
        """Open the item at index."""
        self._root.select_item(index)

    def _clean_removed(self):
        removed = sorted(self._root.get_removed(), reverse=True)
        print("_clean_removed", removed)
        for r in removed:
            self.removeWidget.emit(r)
        self._root.clean_removed()