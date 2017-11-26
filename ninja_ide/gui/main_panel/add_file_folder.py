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

import os

from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtQuickWidgets import QQuickWidget

from ninja_ide.gui.ide import IDE
from ninja_ide.core.file_handling import file_manager
from ninja_ide.tools import ui_tools


class AddFileFolderWidget(QDialog):
    """LocatorWidget class with the Logic for the QML UI"""

    def __init__(self, parent=None):
        super(AddFileFolderWidget, self).__init__(
            parent, Qt.Dialog | Qt.FramelessWindowHint)
        self._main_container = parent
        self.setModal(True)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background:transparent;")
        self.setFixedHeight(70)
        self.setFixedWidth(650)
        # Create the QML user interface.
        self.view = QQuickWidget()
        self.view.setResizeMode(QQuickWidget.SizeRootObjectToView)
        self.view.setSource(ui_tools.get_qml_resource("AddFileFolder.qml"))
        self._root = self.view.rootObject()
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        vbox.addWidget(self.view)

        self._base_path = ""

        self._create_file_operation = True

        self._root.create.connect(self._create)

    def create_file(self, base_path, project_path):
        self._create_file_operation = True
        self._base_path = project_path
        base_path = os.path.relpath(base_path, project_path)
        self._root.setDialogType(self._create_file_operation)
        self._root.setBasePath(base_path + os.path.sep)
        self.show()

    def create_folder(self, base_path, project_path):
        self._create_file_operation = False
        self._base_path = project_path
        base_path = os.path.relpath(base_path, project_path)
        self._root.setDialogType(self._create_file_operation)
        self._root.setBasePath(base_path + os.path.sep)
        self.show()

    def showEvent(self, event):
        """Method takes an event to show the Notification"""
        super(AddFileFolderWidget, self).showEvent(event)
        ninjaide = IDE.get_service("ide")
        point = self._main_container.mapToGlobal(self.view.pos())
        x = point.x() + (ninjaide.width() / 2) - (self.width() / 2)
        self.move(x, point.y())
        self.view.setFocus()
        self._root.activateInput()

    @pyqtSlot(str)
    def _create(self, path):
        """Open the item received."""
        if self._create_file_operation:
            path = os.path.join(self._base_path, path)
            folder = os.path.split(path)[0]
            if not os.path.exists(folder):
                file_manager.create_folder(folder)
            ninjaide = IDE.getInstance()
            current_nfile = ninjaide.get_or_create_nfile(path)
            current_nfile.create()
            main_container = IDE.get_service('main_container')
            if main_container:
                main_container.open_file(path)
        else:
            path = os.path.join(self._base_path, path)
            if not os.path.exists(path):
                file_manager.create_folder(path)
        self.hide()

    def hideEvent(self, event):
        super(AddFileFolderWidget, self).hideEvent(event)
        self._root.cleanText()
