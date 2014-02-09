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

from PyQt4.QtGui import QSplitter
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL


class DynamicSplitter(QSplitter):

    def __init__(self, orientation=Qt.Horizontal):
        super(DynamicSplitter, self).__init__(orientation)

    def add_widget(self, widget, top=False):
        if top:
            self.insertWidget(0, widget)
        else:
            self.addWidget(widget)
        self.connect(widget,
            SIGNAL("splitEditor(PyQt_PyObject, PyQt_PyObject, bool)"),
            self.split)
        self.connect(widget,
            SIGNAL("closeSplit(PyQt_PyObject)"),
            self.close_split)

    def insert_widget(self, index, widget):
        self.insertWidget(index, widget)
        self.connect(widget,
            SIGNAL("splitEditor(PyQt_PyObject, PyQt_PyObject, bool)"),
            self.split)
        self.connect(widget,
            SIGNAL("closeSplit(PyQt_PyObject)"),
            self.close_split)

    def split(self, current, new_widget, orientationVertical=False):
        index = self.indexOf(current)
        if index == -1:
            return
        orientation = Qt.Horizontal
        if orientationVertical:
            orientation = Qt.Vertical
        if self.count() == 2:
            splitter = DynamicSplitter(orientation)
            self.connect(splitter,
                SIGNAL("closeDynamicSplit(PyQt_PyObject, PyQt_PyObject)"),
                self.close_dynamic_split)
            self.insertWidget(index, splitter)
            splitter.add_widget(current)
            splitter.add_widget(new_widget)
        else:
            self.add_widget(new_widget)
            self.setOrientation(orientation)
        new_widget.setFocus()

    def close_split(self, widget):
        index = self.indexOf(widget)
        if index == -1:
            return
        new_index = int(index == 0)
        combo_widget = self.widget(new_index)
        self.emit(SIGNAL("closeDynamicSplit(PyQt_PyObject, PyQt_PyObject)"),
            self, combo_widget)
        widget.deleteLater()
        combo_widget.setFocus()

    def close_dynamic_split(self, split, widget):
        index = self.indexOf(split)
        if index == -1:
            return
        self.insert_widget(index, widget)
        split.deleteLater()