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

from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QListWidget
from PyQt4.QtGui import QTreeView
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QAbstractItemView
from PyQt4.QtGui import QFileSystemModel
from PyQt4.QtGui import QHeaderView
from PyQt4.QtCore import QDir
from PyQt4.QtCore import SIGNAL

from ninja_ide import translations


class AddToProject(QDialog):
    """Dialog to let the user choose one of the folders from the opened proj"""

    def __init__(self, projects, parent=None):
        super(AddToProject, self).__init__(parent)
        #pathProjects must be a list
        self._projects = projects
        self.setWindowTitle(translations.TR_ADD_FILE_TO_PROJECT)
        self.pathSelected = ''
        vbox = QVBoxLayout(self)

        hbox = QHBoxLayout()
        self._list = QListWidget()
        for project in self._projects:
            self._list.addItem(project.name)
        self._list.setCurrentRow(0)
        self._tree = QTreeView()
        #self._tree.header().setHidden(True)
        self._tree.setSelectionMode(QTreeView.SingleSelection)
        self._tree.setAnimated(True)
        self.load_tree(self._projects[0])
        hbox.addWidget(self._list)
        hbox.addWidget(self._tree)
        vbox.addLayout(hbox)

        hbox2 = QHBoxLayout()
        btnAdd = QPushButton(translations.TR_ADD_HERE)
        btnCancel = QPushButton(translations.TR_CANCEL)
        hbox2.addWidget(btnCancel)
        hbox2.addWidget(btnAdd)
        vbox.addLayout(hbox2)

        self.connect(btnCancel, SIGNAL("clicked()"), self.close)
        self.connect(btnAdd, SIGNAL("clicked()"), self._select_path)

    def load_tree(self, project):
        """Load the tree view on the right based on the project selected."""
        qfsm = QFileSystemModel()
        #FIXME it's not loading the proper folder, just the root /
        qfsm.setRootPath(project.path)
        qfsm.setFilter(QDir.AllDirs | QDir.NoDotAndDotDot)
        qfsm.setNameFilterDisables(False)
        pext = ["*{0}".format(x) for x in project.extensions]
        qfsm.setNameFilters(pext)
        self._tree.setModel(qfsm)

        t_header = self._tree.header()
        t_header.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        t_header.setResizeMode(0, QHeaderView.Stretch)
        t_header.setStretchLastSection(False)
        t_header.setClickable(True)

        self._tree.hideColumn(1)  # Size
        self._tree.hideColumn(2)  # Type
        self._tree.hideColumn(3)  # Modification date

    def _select_path(self):
        """Set pathSelected to the folder selected in the tree."""
        path = self._tree.model().filePath(self._tree.currentIndex())
        if path:
            self.pathSelected = path
            self.close()