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

from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QListWidget
from PyQt5.QtWidgets import QTreeView
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtWidgets import QFileSystemModel
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtCore import QDir

from ninja_ide import translations


class AddToProject(QDialog):
    """Dialog to let the user choose one of the folders from the opened proj"""

    def __init__(self, projects, parent=None):
        super(AddToProject, self).__init__(parent)
        # pathProjects must be a list
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

        btnAdd.clicked.connect(self._select_path)
        btnCancel.clicked.connect(self.close)
        self._list.currentItemChanged.connect(self._project_changed)

    def _project_changed(self, item, previous):
        # FIXME, this is not being called, at least in osx
        for each_project in self._projects:
            if each_project.name == item.text():
                self.load_tree(each_project)

    def load_tree(self, project):
        """Load the tree view on the right based on the project selected."""
        qfsm = QFileSystemModel()
        qfsm.setRootPath(project.path)
        load_index = qfsm.index(qfsm.rootPath())
        qfsm.setFilter(QDir.AllDirs | QDir.NoDotAndDotDot)
        qfsm.setNameFilterDisables(False)
        pext = ["*{0}".format(x) for x in project.extensions]
        qfsm.setNameFilters(pext)

        self._tree.setModel(qfsm)
        self._tree.setRootIndex(load_index)

        t_header = self._tree.header()
        t_header.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        t_header.setSectionResizeMode(0, QHeaderView.Stretch)
        t_header.setStretchLastSection(False)
        t_header.setSectionsClickable(True)

        self._tree.hideColumn(1)  # Size
        self._tree.hideColumn(2)  # Type
        self._tree.hideColumn(3)  # Modification date

        # FIXME: Changing the name column's title requires some magic
        # Please look at the project tree

    def _select_path(self):
        """Set pathSelected to the folder selected in the tree."""
        path = self._tree.model().filePath(self._tree.currentIndex())
        if path:
            self.pathSelected = path
            self.close()
