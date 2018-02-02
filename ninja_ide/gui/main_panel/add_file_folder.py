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

import os

from PyQt5.QtWidgets import (
    QDialog,
    QShortcut,
    QVBoxLayout
)

from PyQt5.QtGui import QKeySequence
from PyQt5.QtQuickWidgets import QQuickWidget
from PyQt5.QtCore import (
    Qt,
    pyqtSlot
)

from ninja_ide import resources
from ninja_ide.tools import ui_tools
from ninja_ide.gui.ide import IDE
from ninja_ide.core.file_handling import file_manager


class AddFileFolderWidget(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent, Qt.Dialog | Qt.FramelessWindowHint)
        self._main_container = parent
        self.setModal(True)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedWidth(650)
        # Create the QML UI
        view = QQuickWidget()
        view.rootContext().setContextProperty("theme", resources.QML_COLORS)
        view.setResizeMode(QQuickWidget.SizeRootObjectToView)
        view.setSource(ui_tools.get_qml_resource("AddFileFolder.qml"))
        self._root = view.rootObject()
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        vbox.addWidget(view)

        self._base_path = ""
        self._create_file_operation = True

        short_esc = QShortcut(QKeySequence(Qt.Key_Escape), self)
        short_esc.activated.connect(self.close)

        # Connection
        self._root.create.connect(self._create)

    def create_file(self, base_path, project_path):
        self._create_file_operation = True
        self._base_path = project_path
        path = os.path.relpath(base_path, project_path) + os.path.sep
        if base_path == project_path:
            path = ""
        self._root.setDialogType(self._create_file_operation)
        self._root.setBasePath(path)
        self.show()

    def create_folder(self, base_path, project_path):
        self._create_file_operation = False
        self._base_path = project_path
        path = os.path.relpath(base_path, project_path) + os.path.sep
        if base_path == project_path:
            path = ""
        self._root.setDialogType(self._create_file_operation)
        self._root.setBasePath(path)
        self.show()

    @pyqtSlot('QString')
    def _create(self, path):
        """Open the item received"""

        if self._create_file_operation:
            path = os.path.join(self._base_path, path)
            folder = os.path.split(path)[0]
            if not os.path.exists(folder):
                file_manager.create_folder(folder)
            ide = IDE.get_service("ide")
            current_nfile = ide.get_or_create_nfile(path)
            current_nfile.create()
            main_container = IDE.get_service("main_container")
            main_container.open_file(path)
        else:
            path = os.path.join(self._base_path, path)
            if not os.path.exists(path):
                file_manager.create_folder(path)
        self.close()
