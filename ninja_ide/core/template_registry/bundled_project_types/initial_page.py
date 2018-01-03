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

"""
This page is common in all projects
"""
import sys
import os
from PyQt5.QtWidgets import (
    QWizardPage,
    QVBoxLayout,
    QComboBox,
    QFrame,
    QPlainTextEdit,
    QLabel,
    QGridLayout,
    QLineEdit,
    QFileDialog
)
from ninja_ide.core.file_handling import file_manager
from ninja_ide import translations
from ninja_ide.tools import utils

# http://opensource.org/licenses/alphabetical
LICENSES = (
    'Academic Free License', 'Apache License 2.0',
    'Apple Public Source License', 'Artistic License', 'Artistic license',
    'Common Development and Distribution License',
    'Common Public Attribution License', 'Eclipse Public License',
    'Educational Community License', 'European Union Public License',
    'GNU Affero General Public License', 'GNU General Public License v2',
    'GNU General Public License v3', 'GNU Lesser General Public License 2.1',
    'GNU Lesser General Public License 3.0', 'MIT license',
    'Microsoft Public License', 'Microsoft Reciprocal License',
    'Mozilla Public License 1.1', 'Mozilla Public License 2.0',
    'NASA Open Source Agreement', 'New BSD License 3-Clause',
    'Non-Profit Open Software License', 'Old BSD License 2-Clause',
    'Open Software License', 'Other', 'Other Open Source', 'PHP License',
    'PostgreSQL License', 'Proprietary', 'Python Software License',
    'Simple Public License', 'W3C License', 'Zope Public License',
    'zlib license')


class InitialPage(QWizardPage):

    def __init__(self):
        super().__init__()
        vbox = QVBoxLayout(self)
        frame = QFrame(self)
        vbox.addStretch(1)
        frame.setFrameShape(QFrame.StyledPanel)
        vbox.addWidget(frame)
        # Fields
        fields_box = QGridLayout(frame)
        # Project name
        fields_box.addWidget(QLabel(translations.TR_WIZARD_PROJECT_NAME), 0, 0)
        self._line_project_name = QLineEdit("untitled")
        self.registerField("name*", self._line_project_name)
        fields_box.addWidget(self._line_project_name, 0, 1)
        # Project location
        fields_box.addWidget(
            QLabel(translations.TR_WIZARD_PROJECT_LOCATION), 1, 0)
        self._line_location = QLineEdit()
        self._line_location.setReadOnly(True)
        self._line_location.setText(utils.get_home_dir())
        self.registerField("path", self._line_location)
        choose_dir_act = self._line_location.addAction(
            self.style().standardIcon(
                self.style().SP_DirIcon), QLineEdit.TrailingPosition)
        fields_box.addWidget(self._line_location, 1, 1)
        # Project description
        fields_box.addWidget(QLabel(translations.TR_PROJECT_DESCRIPTION), 2, 0)
        self._txt_desciption = QPlainTextEdit()
        fields_box.addWidget(self._txt_desciption, 2, 1)
        self.registerField("description", self._txt_desciption)
        # Project license
        fields_box.addWidget(QLabel(translations.TR_PROJECT_LICENSE), 3, 0)
        combo_license = QComboBox()
        combo_license.addItems(LICENSES)
        combo_license.setCurrentIndex(12)
        fields_box.addWidget(combo_license, 3, 1)
        self.registerField("license", combo_license, property="currentText")
        # Project interpreter
        fields_box.addWidget(
            QLabel(translations.TR_WIZARD_PROJECT_INTERPRETER), 4, 0)
        combo_interpreter = QComboBox()
        combo_interpreter.addItems(utils.get_python())
        combo_interpreter.setCurrentText(sys.executable)
        fields_box.addWidget(combo_interpreter, 4, 1)
        self.registerField("interpreter", combo_interpreter)
        # Connections
        self._line_project_name.textChanged.connect(self._on_text_changed)
        choose_dir_act.triggered.connect(self._choose_dir)

    def _choose_dir(self):
        dirname = QFileDialog.getExistingDirectory(
            self, translations.TR_WIZARD_CHOOSE_DIR, utils.get_home_dir())
        if dirname:
            self._line_location.setText(dirname)

    @property
    def location(self):
        return self._line_location.text()

    @property
    def project_name(self):
        return self._line_project_name.text()

    def _on_text_changed(self):
        ok = self.validate()
        if not ok:
            self._line_project_name.setStyleSheet("background-color: red")
        else:
            self._line_project_name.setStyleSheet("background-color: none;")

    def validate(self):
        ok = True
        project_path = os.path.join(self.location, self.project_name)
        if file_manager.folder_exists(project_path):
            ok = False
        return ok

    def isComplete(self):
        val = super().isComplete()
        return val and self.validate()
