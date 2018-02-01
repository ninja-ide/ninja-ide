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
# from ninja_ide.gui.ide import IDE


class DynamicSplitter(QSplitter):

    def __init__(self, orientation=Qt.Horizontal):
        super().__init__(orientation)
        self.setHandleWidth(1)

    def add_widget(self, widget, top=False):
        if top:
            self.insertWidget(0, widget)
        else:
            self.addWidget(widget)
        if isinstance(widget, combo_editor.ComboEditor):
            widget.splitEditor.connect(self.split)
            widget.closeSplit.connect(self.close_split)

    def split(self, current, widget, orientation):
        index = self.indexOf(current)
        if index == -1:
            return
        if self.count() == 1:
            self.setOrientation(orientation)
            self.add_widget(widget)
        else:
            new_splitter = DynamicSplitter()
            new_splitter.setOrientation(orientation)
            new_splitter.add_widget(current)
            new_splitter.add_widget(widget)
            self.insertWidget(index, new_splitter)
            new_splitter.setSizes([1 for _ in range(self.count())])
            self.setSizes([1 for _ in range(self.count())])
        widget.setFocus()

    def close_split(self, combo):
        index = self.indexOf(combo)
        if index == -1:
            return
        new_index = 0
        if index == 0:
            new_index = 1
        if self.count() == 2:
            combo.deleteLater()
            self.widget(new_index).setFocus()
        else:
            self.deleteLater()

    def createHandle(self):
        return SplitterHandle(self.orientation(), self)


class SplitterHandle(QSplitterHandle):

    def __init__(self, orientation=Qt.Horizontal, parent=None):
        super().__init__(orientation, parent)
        self.setMask(QRegion(self.contentsRect()))
        self.setAttribute(Qt.WA_MouseNoMask, True)

    def paintEvent(self, event):
        painter = QPainter(self)
        # painter.fillRect(event.rect(), theme.get_color('Splitter'))

    def resizeEvent(self, event):
        if self.orientation() == Qt.Horizontal:
            self.setContentsMargins(2, 0, 2, 0)
        else:
            self.setContentsMargins(0, 2, 0, 2)
        self.setMask(QRegion(self.contentsRect()))
        super().resizeEvent(event)
