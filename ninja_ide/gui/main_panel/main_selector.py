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

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtCore import SIGNAL
from PyQt4.QtDeclarative import QDeclarativeView

from ninja_ide.tools import ui_tools


class MainSelector(QWidget):

    def __init__(self, parent=None):
        super(MainSelector, self).__init__(parent)
        # Create the QML user interface.
        view = QDeclarativeView()
        view.setResizeMode(QDeclarativeView.SizeRootObjectToView)
        view.setSource(ui_tools.get_qml_resource("MainSelector.qml"))
        self._root = view.rootObject()
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        vbox.addWidget(view)

        self.connect(self._root, SIGNAL("open(int)"),
                     lambda i: self.emit(SIGNAL("changeCurrent(int)"), i))
        self.connect(self._root, SIGNAL("open(int)"), self._clean_removed)
        self.connect(self._root, SIGNAL("ready()"),
                     lambda: self.emit(SIGNAL("ready()")))
        self.connect(self._root, SIGNAL("animationCompleted()"),
                     lambda: self.emit(SIGNAL("animationCompleted()")))

    def set_model(self, model):
        for index, path, closable in model:
            self._root.add_widget(index, path, closable)

    def set_preview(self, index, preview_path):
        self._root.add_preview(index, preview_path)

    def close_selector(self):
        self._root.close_selector()

    def start_animation(self):
        self._root.start_animation()
        self._root.forceActiveFocus()

    def open_item(self, index):
        """Open the item at index."""
        self._root.select_item(index)

    def _clean_removed(self):
        removed = sorted(self._root.get_removed(), reverse=True)
        for r in removed:
            self.emit(SIGNAL("removeWidget(int)"), r)
        self._root.clean_removed()