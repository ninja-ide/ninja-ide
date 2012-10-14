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

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QTreeWidget
from PyQt4.QtGui import QTreeWidgetItem
from PyQt4.QtGui import QAbstractItemView
from PyQt4.QtGui import QHeaderView
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL

from ninja_ide.gui.main_panel import main_container


class Results(QWidget):

    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self._parent = parent
        vbox = QVBoxLayout(self)
        self._tree = QTreeWidget()
        self._tree.setHeaderLabels((self.tr("Content"),
            self.tr('File'), self.tr('Line')))
        self._tree.header().setHorizontalScrollMode(
            QAbstractItemView.ScrollPerPixel)
        self._tree.header().setResizeMode(0, QHeaderView.ResizeToContents)
        self._tree.header().setResizeMode(1, QHeaderView.ResizeToContents)
        self._tree.header().setResizeMode(2, QHeaderView.ResizeToContents)
        self._tree.header().setStretchLastSection(True)
        self._tree.sortByColumn(1, Qt.AscendingOrder)

        vbox.addWidget(self._tree)

        #Signals
        self.connect(self._tree,
            SIGNAL("itemActivated(QTreeWidgetItem*, int)"),
            self._open_result)
        self.connect(self._tree, SIGNAL("itemClicked(QTreeWidgetItem*, int)"),
            self._open_result)

    def _open_result(self, item, col):
        filename = item.toolTip(1)
        line = int(item.text(2)) - 1
        main_container.MainContainer().open_file(
                filename=filename,
                cursorPosition=line,
                positionIsLineNumber=True)
        self._parent.hide()

    def update_result(self, items):
        self._tree.clear()
        for i in items:
            item = QTreeWidgetItem(self._tree, (i[3], i[0], str(i[2] + 1)))
            item.setToolTip(1, i[1])
