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

from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QTreeWidget
from PyQt5.QtWidgets import QTreeWidgetItem
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal

from ninja_ide.gui.ide import IDE
from ninja_ide import translations


class Results(QWidget):

    """Show results of occurrences in files inside the tools dock."""

    def __init__(self, parent):
        super(Results, self).__init__(parent)
        self._parent = parent
        vbox = QVBoxLayout(self)
        self._tree = QTreeWidget()
        self._tree.setHeaderLabels((translations.TR_CONTENT,
            translations.TR_FILE, translations.TR_LINE))
        self._tree.header().setHorizontalScrollMode(
            QAbstractItemView.ScrollPerPixel)
        self._tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self._tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self._tree.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self._tree.header().setStretchLastSection(True)
        self._tree.sortByColumn(1, Qt.AscendingOrder)

        vbox.addWidget(self._tree)

        #Signals
        self._tree.itemActivated['QTreeWidgetItem*', int].connect(self._open_result)
        self._tree.itemClicked['QTreeWidgetItem*', int].connect(self._open_result)

    def _open_result(self, item, col):
        """Get the data of the selected item and open the file."""
        filename = item.toolTip(1)
        line = int(item.text(2)) - 1
        main_container = IDE.get_service('main_container')
        if main_container:
            main_container.open_file(filename=filename, line=line)
        self._parent.hide()

    def update_result(self, items):
        """Update the result tree with the new items."""
        self._tree.clear()
        for i in items:
            item = QTreeWidgetItem(self._tree, (i[3], i[0], str(i[2] + 1)))
            item.setToolTip(1, i[1])
