# -*- coding: utf-8 -*-
from __future__ import absolute_import

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QTreeWidget
from PyQt4.QtGui import QTreeWidgetItem
from PyQt4.QtGui import QAbstractItemView
from PyQt4.QtGui import QHeaderView
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QString

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
        self.connect(self._tree, SIGNAL("itemClicked(QTreeWidgetItem*, int)"),
            self._open_result)

    def _open_result(self, item, col):
        filename = unicode(item.toolTip(1))
        line = int(item.text(2)) - 1
        main_container.MainContainer().open_file(
                fileName=filename,
                cursorPosition=line,
                positionIsLineNumber=True)
        self._parent.hide()

    def update_result(self, items):
        self._tree.clear()
        for i in items:
            item = QTreeWidgetItem(self._tree,
                (i[3], i[0], QString.number(i[2] + 1)))
            item.setToolTip(1, i[1])
