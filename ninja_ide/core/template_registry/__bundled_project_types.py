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

from ninja_ide.core.template_registry.ntemplate_registry import BaseProjectType


SETUP_PY_FILE = """
# BEWARE: This is a minimal version you will most likely need to extend it
from setuptools import setup, find_packages

setup(
    name='%s',
    version='1.0',
    packages=find_packages(),

)"""

BASIC_HELLO = """
# This is a sample yet useful program, for python 3


def hello_world():
    print("hello world, this is %s's main")

"""


class PythonVenvProject(BaseProjectType):
    type_name = "Basic Python Project with Venv"
    layout_version = "0.1"
    category = "Python"


class PythonProject(BaseProjectType):

    type_name = "Basic Python Project"
    layout_version = "0.1"
    category = "Python"
    encoding_string = {"py": "# -*- coding: %s -*-"}
    single_line_comment = {"py": "# "}
    description = \
        """This wizard will create a basic Python project.
        """

    def __init__(self, *args, **kwargs):
        super(PythonProject, self).__init__(*args, **kwargs)

    def create_layout(self):
        """
        Create set of folders and files required for a basic python project
        """
        # Create project path
        project_path = os.path.join(self.path, self.name)
        self._create_path(project_path)
        # Create a single init file
        filepath = os.path.join(project_path, "__init__.py")
        with open(filepath, "w") as base_init:
            self.init_file(base_init, filepath)
        # Create a setup.py
        filepath = os.path.join(project_path, "setup.py")
        with open(filepath, "w") as base_setup:
            self.init_file(base_setup, filepath)
            base_setup.write(SETUP_PY_FILE % self.name)
        # Create a basic main file
        filepath = os.path.join(project_path, "main.py")
        with open(filepath, "w") as base_main:
            self.init_file(base_main, filepath)
            base_main.write(BASIC_HELLO % self.name)
        from ninja_ide.tools import json_manager
        project = {}
        project["name"] = self.name
        project["license"] = self.license_text
        json_manager.create_ninja_project(project_path, self.name, project)

    def get_project_api(self):
        """
        Here we expect you to return a QMenu with wathever you need inside.
        Bare in mind that we will add this to the context menu on the
        project tree but we might use it elsewere, not guaranteed.
        """
        pass

    def get_project_file_api(self):
        """
        This is exactly the same as 'get_project_api' but for files.
        You should return a tuple containing:
        (evaluate_pertinence_function, QMenu)
        Where evaluate_pertinence is a function that will receive the file
        path and return True/False if the QMenu is apt for said file.
        """
        pass

    def get_project_wizard_pages(self):
        return []

    def wizard_callback(self):
        pass

    @classmethod
    def wizard_pages(cls):
        from PyQt5.QtWidgets import (
            QWizardPage, QVBoxLayout, QLineEdit, QGridLayout, QLabel, QStyle,
            QFileDialog, QFrame, QComboBox
        )
        from PyQt5.QtGui import QIcon
        from ninja_ide.tools import ui_tools
        from ninja_ide.utils import utils

        class Page(QWizardPage):

            def __init__(self):
                super().__init__()
                vbox = QVBoxLayout(self)
                self.setTitle("Python Project")
                frame = QFrame()
                frame.setLineWidth(2)
                vbox.addStretch(1)
                frame.setFrameShape(QFrame.StyledPanel)
                vbox.addWidget(frame)
                box = QGridLayout(frame)
                box.addWidget(QLabel("Project Name:"), 0, 0)
                self._line_project_name = QLineEdit()
                self.registerField("name*", self._line_project_name)
                box.addWidget(self._line_project_name, 0, 1)
                box.addWidget(QLabel("Create in:"), 1, 0)
                self.line = QLineEdit()
                self.registerField("path", self.line)
                choose_dir_action = self.line.addAction(
                    QIcon(self.style().standardPixmap(
                        self.style().SP_DirIcon)), QLineEdit.TrailingPosition)
                box.addWidget(self.line, 1, 1)
                box.addWidget(QLabel("Interpreter:"), 2, 0)
                line_interpreter = QComboBox()
                line_interpreter.setEditable(True)
                line_interpreter.addItems(utils.get_python())
                box.addWidget(line_interpreter, 2, 1)
                # from ninja_ide.utils import utils
                choose_dir_action.triggered.connect(self._choose_dir)
                self.line.setText(utils.get_home_dir())

            def _choose_dir(self):
                directory = QFileDialog.getExistingDirectory(
                    self, "Choose Directory", "~")
                if directory:
                    self.line.setText(directory)

        return [Page()]


class DjangoProject(BaseProjectType):

    type_name = "Django Project"
    layout_version = "0.1"
    category = "Django"
    description = "Lalalallaal django"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class PyQtProject(BaseProjectType):

    type_name = "PyQt Project"
    layout_version = "0.1"
    category = "PyQt"
    description = "Lalallaal PyQt"

    @classmethod
    def wizard_pages(cls):
        from PyQt5.QtWidgets import QWizardPage
        p = QWizardPage()
        p.setTitle("PPPPPP")
        p.setSubTitle("Pyqslaldsald ")
        return [p]


class GitProject(BaseProjectType):

    type_name = "Git"
    layout_version = "0.1"
    category = "Clone Project"
    description = "Clones a Git repository"


# Register bundled projects
PythonProject.register()
PythonVenvProject.register()
DjangoProject.register()
PyQtProject.register()
GitProject.register()
