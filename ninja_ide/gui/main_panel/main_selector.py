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

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout
)
from PyQt5.QtQuickWidgets import QQuickWidget
from PyQt5.QtCore import (
    pyqtSignal,
    Qt
)
from ninja_ide.tools import ui_tools


class MainSelector(QWidget):
    changeCurrent = pyqtSignal(int)
    ready = pyqtSignal()
    animationCompleted = pyqtSignal()
    removeWidget = pyqtSignal(int)

    def __init__(self, parent=None):
        super(MainSelector, self).__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        # Create the QML user interface.
        view = QQuickWidget()
        view.setClearColor(Qt.transparent)
        view.setResizeMode(QQuickWidget.SizeRootObjectToView)
        view.setSource(ui_tools.get_qml_resource("MainSelector.qml"))
        self._root = view.rootObject()
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        vbox.addWidget(view)

        # self._root.open[int].connect(lambda i: self.changeCurrent.emit(i))
        # self._root.open[int].connect(self._clean_removed)
        # self._root.ready.connect(lambda: self.ready.emit())
        # self._root.animationCompleted.connect(
        #    lambda: self.animationCompleted.emit())

    def set_model(self, model):
        self._root.start()
        for index, path in model:
            self._root.add_widget(path)

    def set_preview(self, index, preview_path):
        self._root.add_preview(index, preview_path)

    def close_selector(self):
        self._root.close_selector()

    def start_animation(self):
        # self._root.start_animation()
        self._root.forceActiveFocus()

    def open_item(self, index):
        """Open the item at index."""
        self._root.select_item(index)

    def _clean_removed(self):
        # FIXME:
        removed = sorted(self._root.get_removed().toVariant(), reverse=True)
        for r in removed:
            self.removeWidget.emit(r)
        self._root.clean_removed()
