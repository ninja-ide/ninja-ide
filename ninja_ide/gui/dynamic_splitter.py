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
    QSplitter,
    # QWidget,
    QSplitterHandle
)
from PyQt5.QtGui import (
    QPainter,
    QRegion
)
from PyQt5.QtCore import (
    Qt,
    pyqtSignal
)
from ninja_ide.gui.main_panel import combo_editor
from ninja_ide.gui.theme import NTheme


class DynamicSplitter(QSplitter):
    closeDynamicSplit = pyqtSignal("PyQt_PyObject", "PyQt_PyObject")

    def __init__(self, orientation=Qt.Horizontal):
        QSplitter.__init__(self, orientation)
        self.setHandleWidth(1)
        self.child_splitters = []

    def add_widget(self, widget, top=False):
        if top:
            self.insertWidget(0, widget)
        else:
            self.addWidget(widget)
        if isinstance(widget, combo_editor.ComboEditor):
            widget.splitEditor['PyQt_PyObject',
                               'PyQt_PyObject', bool].connect(self.split)
            widget.closeSplit['PyQt_PyObject'].connect(self.close_split)

    def createHandle(self):
        return SplitterHandle(self.orientation(), self)

    def split(self, current_widget, new_widget, orientation_vertical):
        # #FIXME: el primero no splitea WTF!!!!
        orientation = Qt.Horizontal
        if orientation_vertical:
            orientation = Qt.Vertical
        splitter = self.__class__(orientation)
        splitter.add_widget(new_widget)
        splitter.setOrientation(orientation)
        self.add_widget(splitter)
        self.setOrientation(orientation)
        self.setSizes([1 for i in range(self.count())])
        new_widget.setFocus()

    def close_split(self, widget):
        # index = self.indexOf(widget)
        # combo_widget = self.widget(index)
        # widget.deleteLater()
        # self.closeDynamicSplit.emit(self, combo_widget)
        pass

    """
    def add_widget(self, widget, top=False):
        if top:
            self.insertWidget(0, widget)
        else:
            self.addWidget(widget)
        if isinstance(widget, combo_editor.ComboEditor):
            widget.splitEditor['PyQt_PyObject', 'PyQt_PyObject',
                               bool].connect(self.split)
            widget.closeSplit['PyQt_PyObject'].connect(self.close_split)

    def split(self, current_widget, new_widget, orientation_vertical):
        orientation = Qt.Horizontal
        if orientation_vertical:
            orientation = Qt.Vertical
        index = self.indexOf(current_widget)
        if self.count() == 2:
            splitter = self.__class__(orientation=orientation)
            self.insertWidget(index, splitter)
            splitter.add_widget(current_widget)
            splitter.add_widget(new_widget)
            self.setSizes([1, 1])
            splitter.setSizes([1, 1])
            # splitter.setSizes(self._get_sizes(current_widget, orientation))
        else:
            self.add_widget(new_widget)
            self.setOrientation(orientation)
            # self.setSizes(self._get_sizes(self, orientation))
            self.setSizes([1, 1])
        new_widget.setFocus()

    def close_split(self, widget):
        index = self.indexOf(widget)
        if index == -1:
            return
        new_index = int(index == 0)
        combo_widget = self.widget(new_index)
        widget.unlink_editors()
        widget.deleteLater()
        self.closeDynamicSplit.emit(self, combo_widget)
        combo_widget.setFocus()

    def _get_sizes(self, widget, orientation):
        sizes = [1, 1]
        if orientation == Qt.Vertical:
            height = widget.height() / 2
            sizes = [height, height]
        else:
            width = widget.width()
            sizes = [width, width]
        return sizes

    def close_dynamic_split(self, split, widget):
        index = self.indexOf(split)
        if index == -1:
            return
        self.insert_widget(index, widget)
        split.deleteLater()

    def createHandle(self):
        return SplitterHandle(self.orientation(), self)

    """


class SplitterHandle(QSplitterHandle):

    def __init__(self, orientation=Qt.Horizontal, parent=None):
        super().__init__(orientation, parent)
        self.setMask(QRegion(self.contentsRect()))
        self.setAttribute(Qt.WA_MouseNoMask, True)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(event.rect(), NTheme.get_color('Splitter'))

    def resizeEvent(self, event):
        if self.orientation() == Qt.Horizontal:
            self.setContentsMargins(2, 0, 2, 0)
        else:
            self.setContentsMargins(0, 2, 0, 2)
        self.setMask(QRegion(self.contentsRect()))
        super().resizeEvent(event)
