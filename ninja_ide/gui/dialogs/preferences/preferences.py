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

from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QTreeWidget
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QScrollArea
from PyQt4.QtGui import QAbstractItemView
from PyQt4.QtGui import QHeaderView
from PyQt4.QtCore import QSize
from PyQt4.QtCore import Qt

from ninja_ide import translations


SECTIONS = {

}


class Preferences(QDialog):

    configuration = []

    def __init__(self, parent=None):
        super(Preferences, self).__init__(parent, Qt.Dialog)
        self.setWindowTitle(translations.TR_PREFERENCES_TITLE)
        self.setMinimumSize(QSize(800, 600))
        self.setMaximumSize(QSize(0, 0))
        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(0, 0, 0, 0)

        self.tree = QTreeWidget()
        self.tree.header().setHidden(True)
        self.tree.setSelectionMode(QTreeWidget.SingleSelection)
        self.tree.setAnimated(True)
        self.tree.header().setHorizontalScrollMode(
            QAbstractItemView.ScrollPerPixel)
        self.tree.header().setResizeMode(0, QHeaderView.ResizeToContents)
        self.tree.header().setStretchLastSection(False)
        self.tree.setFixedWidth(200)
        self.area = QScrollArea()
        hbox.addWidget(self.tree)
        hbox.addWidget(self.area)

    @classmethod
    def register_configuration(cls, section, widget, subsection=None):
        pass