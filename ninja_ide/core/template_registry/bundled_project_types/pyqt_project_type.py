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
    QWizardPage,
    QVBoxLayout,
    QFrame,
    QLineEdit,
    QLabel,
    QComboBox,
    QGridLayout
)
from ninja_ide import translations
from ninja_ide.core.template_registry.ntemplate_registry import BaseProjectType
from ninja_ide.core.template_registry.bundled_project_types import initial_page
from ninja_ide.tools import json_manager


MAIN = """
import sys
from PyQt5.QtWidgets import QApplication
from {module} import {classname}


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = {classname}()
    widget.show()
    sys.exit(app.exec_())

"""

WIDGET = """
from PyQt5.QtWidgets import {baseclass}


class {classname}({baseclass}):

    def __init__(self, parent=None):
        super().__init__(parent)
"""


class PyQtWidgetsProject(BaseProjectType):

    type_name = "PyQt Widgets Application"
    layout_version = "0.1"
    category = "PyQt"
    description = "Creates a PyQt application for the desktop."

    @classmethod
    def wizard_pages(cls):
        return [InitialPage(), SecondPage()]

    def create_layout(self, wizard):
        base_class = wizard.field("base_class")
        class_name = wizard.field("class_name").title()
        module = base_class.lower()[1:]
        # Create project path
        project_path = os.path.join(self.path, self.name)
        self._create_path(project_path)
        # Create main file
        filepath = os.path.join(project_path, "main.py")
        with open(filepath, "w") as base_main:
            self.init_file(base_main, filepath)
            base_main.write(MAIN.format(module=module, classname=class_name))
        # Create widget file
        filepath = os.path.join(project_path, module + ".py")
        with open(filepath, "w") as widget_file:
            self.init_file(widget_file, filepath)
            widget_file.write(
                WIDGET.format(baseclass=base_class, classname=class_name))
        # Create ninja project file
        project = {}
        project["name"] = self.name
        project["project-type"] = self.category
        project["mainFile"] = "main.py"
        json_manager.create_ninja_project(project_path, self.name, project)
        self._open_project(project_path)


class InitialPage(initial_page.InitialPage):

    def __init__(self):
        super().__init__()
        self.setTitle(translations.TR_WIZARD_PYQT_PROJECT_TITLE)
        self.setSubTitle(translations.TR_WIZARD_PYQT_PROJECT_SUBTITLE)


class SecondPage(QWizardPage):

    def __init__(self):
        super().__init__()
        self.setTitle(translations.TR_WIZARD_PYQT_PROJECT_TITLE_SECOND_PAGE)
        self.setSubTitle(
            translations.TR_WIZARD_PYQT_PROJECT_SUBTITLE_SECOND_PAGE)
        vbox = QVBoxLayout(self)
        frame = QFrame(self)
        frame.setFrameShape(QFrame.StyledPanel)
        vbox.addWidget(frame)
        # Fields
        fields_box = QGridLayout(frame)
        fields_box.addWidget(
            QLabel(translations.TR_WIZARD_PYQT_CLASS_NAME), 0, 0)
        self._line_class_name = QLineEdit()
        self.registerField("class_name*", self._line_class_name)
        fields_box.addWidget(self._line_class_name, 0, 1)

        fields_box.addWidget(
            QLabel(translations.TR_WIZARD_PYQT_BASE_CLASS), 1, 0)
        self._combo_class_name = QComboBox()
        self._combo_class_name.addItems(["QWidget", "QMainWindow", "QDialog"])
        self.registerField(
            "base_class", self._combo_class_name, property="currentText")
        fields_box.addWidget(self._combo_class_name, 1, 1)

        fields_box.addWidget(
            QLabel(translations.TR_WIZARD_PYQT_WIDGET_FILE), 2, 0)
        self._line_widget_file = QLineEdit()
        self._line_widget_file.setReadOnly(True)
        fields_box.addWidget(self._line_widget_file, 2, 1)
        self._combo_class_name.currentTextChanged.connect(
            self.__update_line_widget)
        self.__update_line_widget(self._combo_class_name.currentText())

    def __update_line_widget(self, text):
        text = text.lower()[1:] + ".py"
        self._line_widget_file.setText(text)


PyQtWidgetsProject.register()
