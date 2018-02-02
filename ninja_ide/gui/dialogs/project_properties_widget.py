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

import os
import sys
from getpass import getuser

from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QDialogButtonBox
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QCompleter
from PyQt5.QtWidgets import QDirModel
from PyQt5.QtWidgets import QPlainTextEdit
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QSpinBox
from PyQt5.QtCore import Qt

from ninja_ide import translations
from ninja_ide.core.file_handling import file_manager
from ninja_ide.tools import utils
from ninja_ide.gui.ide import IDE

from ninja_ide.tools.logger import NinjaLogger
logger = NinjaLogger('ninja_ide.gui.dialogs.project_properties_widget')
DEBUG = logger.debug


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


class ProjectProperties(QDialog):
    """Project Properties widget class"""

    def __init__(self, project, parent=None):
        super(ProjectProperties, self).__init__(parent, Qt.Dialog)
        self.parent = parent
        self.project = project
        self.setWindowTitle(translations.TR_PROJECT_PROPERTIES)
        self.resize(600, 500)
        vbox = QVBoxLayout(self)
        self.tab_widget = QTabWidget()
        self.project_data = ProjectData(self)
        self.project_execution = ProjectExecution(self)
        self.projectMetadata = ProjectMetadata(self)
        self.tab_widget.addTab(self.project_data, translations.TR_PROJECT_DATA)
        self.tab_widget.addTab(self.project_execution,
                               translations.TR_PROJECT_EXECUTION)
        self.tab_widget.addTab(self.projectMetadata,
                               translations.TR_PROJECT_METADATA)

        vbox.addWidget(self.tab_widget)

        button_box = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        vbox.addWidget(button_box)

        button_box.rejected.connect(self.close)
        button_box.accepted.connect(self.save_properties)

    def save_properties(self):
        self.project.name = self.project_data.name
        self.project.project_type = self.project_data.project_type
        self.project.description = self.project_data.description
        self.project.url = self.project_data.url
        self.project.license = self.project_data.license
        self.project.extensions = self.project_data.extensions
        self.project.indentation = self.project_data.indentation
        self.project.use_tabs = self.project_data.use_tabs

        self.project.main_file = self.project_execution.main_file
        self.project.python_exec = self.project_execution.interpreter
        self.project.pre_exec_script = self.project_execution.pre_script
        self.project.post_exec_script = self.project_execution.post_script
        self.project.program_params = self.project_execution.params

        # Save NProject
        self.project.save_project_properties()
        self.parent.refresh_file_filters()
        self.close()

    '''def save_properties(self):
        """Show warning message if Project Name is empty"""
        if not len(self.projectData.name.text().strip()):
            QMessageBox.critical(self, translations.TR_PROJECT_SAVE_INVALID,
                                 translations.TR_PROJECT_INVALID_MESSAGE)
            return

        self.project.name = self.projectData.name.text()
        self.project.description = self.projectData.description.toPlainText()
        self.project.license = self.projectData._combo_license.currentText()
        self.project.main_file = self.projectExecution.path.text()
        self.project.url = self.projectData.url.text()
        self.project.project_type = self.projectData.line_type.text()
        # FIXME
        self.project.python_exec = \
            self.projectExecution.line_interpreter.text()
        self.project.python_path = \
            self.projectExecution.txt_python_path.toPlainText()
        self.project.additional_builtins = [
            e for e in
            self.projectExecution.additional_builtins.text().split(' ') if e]
        self.project.pre_exec_script = self.projectExecution._line_pre_exec.text()
        self.project.post_exec_script = self.projectExecution._line_post_exec.text()
        self.project.program_params = self.projectExecution._line_params.text()
        self.project.venv = self.projectExecution.txtVenvPath.text()
        extensions = self.projectData._line_extensions.text().split(', ')
        self.project.extensions = tuple(extensions)
        self.project.indentation = self.projectData._spin_indentation.value()
        self.project.use_tabs = bool(
            self.projectData._combo_tabs_or_spaces.currentIndex())
        related = self.projectMetadata.txt_projects.toPlainText()
        related = [_path for _path in related.split('\n') if len(_path.strip())]
        self.project.related_projects = related
        self.project.save_project_properties()

        self.parent.refresh_file_filters()

        self.close()'''


class ProjectData(QWidget):
    """Project Data widget class"""

    def __init__(self, parent):
        super(ProjectData, self).__init__()
        self._parent = parent
        grid = QGridLayout(self)
        grid.addWidget(QLabel(translations.TR_PROJECT_NAME), 0, 0)
        self._line_name = QLineEdit()
        if not len(self._parent.project.name):
            self._line_name.setText(file_manager.get_basename(
                self._parent.project.path))
        else:
            self._line_name.setText(self._parent.project.name)
        grid.addWidget(self._line_name, 0, 1)
        grid.addWidget(QLabel(translations.TR_PROJECT_LOCATION), 1, 0)
        self.line_path = QLineEdit()
        self.line_path.setReadOnly(True)
        self.line_path.setText(self._parent.project.path)
        grid.addWidget(self.line_path, 1, 1)
        grid.addWidget(QLabel(translations.TR_PROJECT_TYPE), 2, 0)
        self.line_type = QLineEdit()
        template_registry = IDE.get_service("template_registry")
        completer = QCompleter(template_registry.list_project_categories())
        completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.line_type.setCompleter(completer)
        self.line_type.setPlaceholderText("python")
        self.line_type.setText(self._parent.project.project_type)
        grid.addWidget(self.line_type, 2, 1)
        grid.addWidget(QLabel(translations.TR_PROJECT_DESCRIPTION), 3, 0)
        self._line_description = QPlainTextEdit()
        self._line_description.setPlainText(self._parent.project.description)
        grid.addWidget(self._line_description, 3, 1)
        grid.addWidget(QLabel(translations.TR_PROJECT_URL), 4, 0)
        self._line_url = QLineEdit()
        self._line_url.setText(self._parent.project.url)
        self._line_url.setPlaceholderText(
            'https://www.{}.com'.format(getuser()))
        grid.addWidget(self._line_url, 4, 1)
        grid.addWidget(QLabel(translations.TR_PROJECT_LICENSE), 5, 0)
        self._combo_license = QComboBox()
        self._combo_license.addItems(LICENSES)
        self._combo_license.setCurrentIndex(12)
        index = self._combo_license.findText(self._parent.project.license)
        self._combo_license.setCurrentIndex(index)
        grid.addWidget(self._combo_license, 5, 1)

        self._line_extensions = QLineEdit()
        self._line_extensions.setText(
            ', '.join(self._parent.project.extensions))
        self._line_extensions.setToolTip(
            translations.TR_PROJECT_EXTENSIONS_TOOLTIP)
        grid.addWidget(QLabel(translations.TR_PROJECT_EXTENSIONS), 6, 0)
        grid.addWidget(self._line_extensions, 6, 1)
        labelTooltip = QLabel(translations.TR_PROJECT_EXTENSIONS_INSTRUCTIONS)
        grid.addWidget(labelTooltip, 7, 1)

        grid.addWidget(QLabel(translations.TR_PROJECT_INDENTATION), 8, 0)
        self._spin_indentation = QSpinBox()
        self._spin_indentation.setValue(self._parent.project.indentation)
        self._spin_indentation.setRange(2, 10)
        self._spin_indentation.setValue(4)
        self._spin_indentation.setSingleStep(2)
        grid.addWidget(self._spin_indentation, 8, 1)
        self._combo_tabs_or_spaces = QComboBox()
        self._combo_tabs_or_spaces.addItems([
            translations.TR_PREFERENCES_EDITOR_CONFIG_SPACES.capitalize(),
            translations.TR_PREFERENCES_EDITOR_CONFIG_TABS.capitalize()])
        self._combo_tabs_or_spaces.setCurrentIndex(
            int(self._parent.project.use_tabs))
        grid.addWidget(self._combo_tabs_or_spaces, 9, 1)

    @property
    def name(self):
        return self._line_name.text()

    @property
    def path(self):
        return self.line_path.text()

    @property
    def project_type(self):
        return self.line_type.text()

    @property
    def description(self):
        return self._line_description.toPlainText()

    @property
    def url(self):
        return self._line_url.text()

    @property
    def license(self):
        return self._combo_license.currentText()

    @property
    def extensions(self):
        return list(map(str.strip, self._line_extensions.text().split(',')))

    @property
    def indentation(self):
        return self._spin_indentation.value()

    @property
    def use_tabs(self):
        return bool(self._combo_tabs_or_spaces.currentIndex())


class ProjectExecution(QWidget):
    """Project Execution widget class"""

    def __init__(self, parent):
        super(ProjectExecution, self).__init__()
        self._parent = parent
        grid = QGridLayout(self)

        grid.addWidget(QLabel(translations.TR_PROJECT_MAIN_FILE), 0, 0)
        # Main file
        self.path = QLineEdit()
        choose_main_file_action = QAction(self)
        choose_main_file_action.setIcon(
            self.style().standardIcon(self.style().SP_FileIcon))
        choose_main_file_action.setToolTip(
            translations.TR_PROJECT_SELECT_MAIN_FILE)
        self.path.addAction(
            choose_main_file_action, QLineEdit.TrailingPosition)
        clear_main_file_action = self.path.addAction(
            self.style().standardIcon(self.style().SP_LineEditClearButton),
            QLineEdit.TrailingPosition)
        clear_main_file_action.triggered.connect(self.path.clear)
        self.path.setPlaceholderText(
            os.path.join(os.path.expanduser("~"), 'path', 'to', 'main.py'))
        self.path.setText(self._parent.project.main_file)
        grid.addWidget(self.path, 0, 1)
        # this should be changed, and ALL pythonPath names to
        # python_custom_interpreter or something like that. this is NOT the
        # PYTHONPATH
        self.line_interpreter = QLineEdit()
        choose_interpreter = self.line_interpreter.addAction(
            self.style().standardIcon(self.style().SP_DirIcon),
            QLineEdit.TrailingPosition)
        self.line_interpreter.setText(self._parent.project.python_exec)
        completer = QCompleter(utils.get_python())
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        self.line_interpreter.setCompleter(completer)
        self.line_interpreter.setPlaceholderText("python")
        grid.addWidget(QLabel(
            translations.TR_PROJECT_PYTHON_INTERPRETER), 1, 0)
        grid.addWidget(self.line_interpreter, 1, 1)
        # PYTHONPATH
        grid.addWidget(QLabel(translations.TR_PROJECT_PYTHON_PATH), 2, 0)
        self.txt_python_path = QPlainTextEdit()  # TODO : better widget
        self.txt_python_path.setPlainText(self._parent.project.python_path)
        self.txt_python_path.setToolTip(translations.TR_PROJECT_PATH_PER_LINE)
        grid.addWidget(self.txt_python_path, 2, 1)

        # Additional builtins/globals for pyflakes
        grid.addWidget(QLabel(translations.TR_PROJECT_BUILTINS), 3, 0)
        self.additional_builtins = QLineEdit()
        self.additional_builtins.setText(
            ' '.join(self._parent.project.additional_builtins))
        self.additional_builtins.setToolTip(
            translations.TR_PROJECT_BUILTINS_TOOLTIP)
        grid.addWidget(self.additional_builtins, 3, 1)
        # Pre script
        self._line_pre_exec = QLineEdit()
        choose_pre_exec = QAction(self)
        choose_pre_exec.setToolTip(
            "Choose Script to execute before run project")
        choose_pre_exec.setIcon(
            self.style().standardIcon(self.style().SP_FileIcon))
        self._line_pre_exec.addAction(
            choose_pre_exec, QLineEdit.TrailingPosition)
        clear_pre_action = self._line_pre_exec.addAction(
            self.style().standardIcon(self.style().SP_LineEditClearButton),
            QLineEdit.TrailingPosition)
        clear_pre_action.triggered.connect(self._line_pre_exec.clear)
        self._line_pre_exec.setReadOnly(True)
        self._line_pre_exec.setText(self._parent.project.pre_exec_script)
        self._line_pre_exec.setPlaceholderText(
            os.path.join(os.path.expanduser("~"), 'path', 'to', 'script.sh'))
        grid.addWidget(QLabel(translations.TR_PROJECT_PRE_EXEC), 4, 0)
        grid.addWidget(self._line_pre_exec, 4, 1)
        # Post script
        self._line_post_exec = QLineEdit()
        choose_post_exec = QAction(self)
        choose_post_exec.setToolTip(
            "Choose script to execute after run project")
        choose_post_exec.setIcon(
            self.style().standardIcon(self.style().SP_FileIcon))
        self._line_post_exec.addAction(
            choose_post_exec, QLineEdit.TrailingPosition)
        clear_post_action = self._line_post_exec.addAction(
            self.style().standardIcon(self.style().SP_LineEditClearButton),
            QLineEdit.TrailingPosition)
        clear_post_action.triggered.connect(self._line_post_exec.clear)
        self._line_post_exec.setReadOnly(True)
        self._line_post_exec.setText(self._parent.project.post_exec_script)
        self._line_post_exec.setPlaceholderText(
            os.path.join(os.path.expanduser("~"), 'path', 'to', 'script.sh'))
        grid.addWidget(QLabel(translations.TR_PROJECT_POST_EXEC), 5, 0)
        grid.addWidget(self._line_post_exec, 5, 1)

        # grid.addItem(QSpacerItem(5, 10, QSizePolicy.Expanding,
        #             QSizePolicy.Expanding), 6, 0)

        # Properties
        grid.addWidget(QLabel(translations.TR_PROJECT_PROPERTIES), 7, 0)
        self._line_params = QLineEdit()
        self._line_params.setToolTip(translations.TR_PROJECT_PARAMS_TOOLTIP)
        self._line_params.setText(self._parent.project.program_params)
        self._line_params.setPlaceholderText('verbose, debug, force')
        grid.addWidget(QLabel(translations.TR_PROJECT_PARAMS), 8, 0)
        grid.addWidget(self._line_params, 8, 1)
        # Widgets for virtualenv properties
        self.txtVenvPath = QLineEdit()
        # ui_tools.LineEditButton(
        #    self.txtVenvPath, self.txtVenvPath.clear,
        #    self.style().standardPixmap(self.style().SP_TrashIcon))
        self.txtVenvPath.setText(self._parent.project.venv)
        self._dir_completer = QCompleter()
        self._dir_completer.setModel(QDirModel(self._dir_completer))
        self.txtVenvPath.setCompleter(self._dir_completer)
        self.txtVenvPath.setPlaceholderText(
            os.path.join(os.path.expanduser("~"), 'path', 'to', 'virtualenv'))
        # self.btnVenvPath = QPushButton(QIcon(":img/open"), '')
        grid.addWidget(QLabel(translations.TR_PROJECT_VIRTUALENV), 9, 0)
        grid.addWidget(self.txtVenvPath, 9, 1)
        # grid.addWidget(self.btnVenvPath, 9, 2)

        choose_main_file_action.triggered.connect(self.select_file)
        choose_interpreter.triggered.connect(self._load_python_path)
        choose_pre_exec.triggered.connect(self.select_pre_exec_script)
        choose_post_exec.triggered.connect(self.select_post_exec_script)
        # self.connect(self.btnBrowse, SIGNAL("clicked()"), self.select_file)
        # self.connect(self.btnPythonPath, SIGNAL("clicked()"),
        #             self._load_python_path)
        # self.connect(self.btnVenvPath, SIGNAL("clicked()"),
        #             self._load_python_venv)
        # self.connect(self.btnPreExec, SIGNAL("clicked()"),
        #             self.select_pre_exec_script)
        # self.connect(self.btnPostExec, SIGNAL("clicked()"),
        #             self.select_post_exec_script)

    @property
    def main_file(self):
        return self.path.text()

    @property
    def interpreter(self):
        return self.line_interpreter.text()

    @property
    def pre_script(self):
        return self._line_pre_exec.text()

    @property
    def post_script(self):
        return self._line_post_exec.text()

    @property
    def params(self):
        return self._line_params.text()

    def _load_python_path(self):
        """Ask the user a python path and set its value"""
        path_interpreter = QFileDialog.getOpenFileName(
            self, translations.TR_PROJECT_SELECT_PYTHON_PATH)[0]
        if path_interpreter:
            self.line_interpreter.setText(path_interpreter)

    def _load_python_venv(self):
        """Ask the user a python venv and set its value"""
        venv = QFileDialog.getExistingDirectory(
            self, translations.TR_PROJECT_SELECT_VIRTUALENV)
        if sys.platform == 'win32':
            venv = os.path.join(venv, 'Scripts', 'python.exe')
        else:
            venv = os.path.join(venv, 'bin', 'python')
        # check if venv folder exists
        if not os.path.exists(venv):
            QMessageBox.information(
                self,
                translations.TR_PROJECT_SELECT_VIRTUALENV_MESSAGE_TITLE,
                translations.TR_PROJECT_SELECT_VIRTUALENV_MESSAGE_BODY)
            self.txtVenvPath.setText("")
        else:
            self.txtVenvPath.setText(venv)

    def select_file(self):
        """Ask the user a python main file and set its value"""
        filename, _ = QFileDialog.getOpenFileName(
            self, translations.TR_PROJECT_SELECT_MAIN_FILE,
            self._parent.project.path,
            'Python Files (*.py);;Python Bytecode (*.py[codw]);;All Files(*)')
        if filename:
            filename = file_manager.convert_to_relative(
                self._parent.project.path, filename)
            self.path.setText(filename)

    def select_pre_exec_script(self):
        """Ask the user a python pre-exec script and set its value"""
        filename = QFileDialog.getOpenFileName(
            self, translations.TR_PROJECT_SELECT_PRE_SCRIPT,
            self._parent.project.path,
            '*(*.*);;Bash(*.sh);;Python PY(*.py);;Python Bytecode(*.py[codw]);;'
            'Bat(*.bat);;Cmd(*.cmd);;Exe(*.exe);;Bin(*.bin);;App(*.app)')[0]
        if filename:
            filename = file_manager.convert_to_relative(
                self._parent.project.path, filename)
            self._line_pre_exec.setText(filename)

    def select_post_exec_script(self):
        """Ask the user a python post-exec script and set its value"""
        filename = QFileDialog.getOpenFileName(
            self, translations.TR_PROJECT_SELECT_POST_SCRIPT,
            self._parent.project.path,
            '*(*.*);;Bash(*.sh);;Python PY(*.py);;Python Bytecode(*.py[codw]);;'
            'Bat(*.bat);;Cmd(*.cmd);;Exe(*.exe);;Bin(*.bin);;App(*.app)')[0]
        if filename:
            filename = file_manager.convert_to_relative(
                self._parent.project.path, filename)
            self._line_post_exec.setText(filename)


class ProjectMetadata(QWidget):
    """Project Metadata widget class"""

    def __init__(self, parent):
        super(ProjectMetadata, self).__init__()
        self._parent = parent

        vbox = QVBoxLayout(self)
        vbox.addWidget(QLabel(translations.TR_PROJECT_METADATA_RELATED))
        self.txt_projects = QPlainTextEdit()
        vbox.addWidget(self.txt_projects)
        vbox.addWidget(QLabel(translations.TR_PROJECT_METADATA_TIP))

        paths = '\n'.join(self._parent.project.related_projects)
        self.txt_projects.setPlainText(paths)
        self.txt_projects.setToolTip(translations.TR_PROJECT_PATH_PER_LINE)
