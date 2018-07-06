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

from PyQt5.QtWidgets import QSplitter

from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal

from ninja_ide.gui.main_panel import combo_editor


class DynamicSplitter(QSplitter):

    closeDynamicSplit = pyqtSignal("PyQt_PyObject", "PyQt_PyObject")
    needUpdateSizes = pyqtSignal()

    def __init__(self, orientation=Qt.Horizontal):
        super().__init__(orientation)
        self.setOpaqueResize(False)

    def add_widget(self, widget, top=False):
        if top:
            self.insertWidget(0, widget)
        else:
            self.addWidget(widget)
        if isinstance(widget, combo_editor.ComboEditor):
            widget.splitEditor.connect(self.split)
            widget.closeSplit.connect(self.close_split)

    def insert_widget(self, index, widget):
        self.insertWidget(index, widget)
        if isinstance(widget, combo_editor.ComboEditor):
            widget.splitEditor.connect(self.split)
            widget.closeSplit.connect(self.close_split)

    def split(self, current, new_widget, orientation):
        index = self.indexOf(current)
        if index == -1:
            return
        sizes = self._get_sizes(current, orientation)
        if self.count() == 2:
            sizes = self._get_sizes(current, orientation)
            splitter = DynamicSplitter(orientation)
            splitter.closeDynamicSplit.connect(self.close_dynamic_split)
            self.insertWidget(index, splitter)
            splitter.add_widget(current)
            splitter.add_widget(new_widget)
            splitter.setSizes(sizes)

        else:
            self.add_widget(new_widget)
            self.setOrientation(orientation)
            sizes = self._get_sizes(self, orientation)
            self.setSizes(sizes)
        new_widget.setFocus()

    def close_dynamic_split(self, split, widget):
        index = self.indexOf(split)
        if index == -1:
            return
        self.insert_widget(index, widget)
        split.hide()
        split.deleteLater()

    def _get_sizes(self, widget, orientation):
        sizes = [1, 1]
        if orientation == Qt.Vertical:
            height = widget.height() / 2
            sizes = [height, height]
        else:
            width = widget.width()
            sizes = [width, width]
        return sizes

    def close_split(self, widget):
        index = self.indexOf(widget)
        if index == -1:
            return
        widget.hide()
        widget.deleteLater()

        new_index = int(index == 0)
        combo_widget = self.widget(new_index)
        if combo_widget is None:
            self.hide()
            self.deleteLater()
            return
        self.closeDynamicSplit.emit(self, combo_widget)
        combo_widget.setFocus()
