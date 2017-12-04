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
    QTreeWidget,
    QTreeWidgetItem,
    QWidget,
    QVBoxLayout
)
from ninja_ide.gui.ide import IDE

# FIXME: se ejecuta 2 veces refresh, proviene de _set_current combo editor
# FIXME: analizar todo el proyecto


class ErrorsTree(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        IDE.register_service("errors_tree", self)
        box = QVBoxLayout(self)
        box.setContentsMargins(0, 0, 0, 0)
        self._tree = QTreeWidget()
        self._tree.header().setHidden(True)
        self._tree.setAnimated(True)
        box.addWidget(self._tree)

    def refresh(self, errors, path):
        self._tree.clear()
        parent = QTreeWidgetItem(self._tree, [path])
        for lineno, msg in errors.items():
            item = QTreeWidgetItem(parent, [msg])
            self._tree.addTopLevelItem(item)

    def display_name(self):
        return 'Errors'


# FIXME: if stm
ErrorsTree()
