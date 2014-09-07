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

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QSizePolicy
from PyQt4.QtGui import QSpacerItem
from PyQt4.QtGui import QTabWidget
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QGridLayout
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QCompleter
from PyQt4.QtGui import QDirModel
from PyQt4.QtGui import QPlainTextEdit
from PyQt4.QtGui import QComboBox
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QFileDialog
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QSpinBox
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL

from ninja_ide import translations
from ninja_ide.core.file_handling import file_manager
from ninja_ide.core import settings
from ninja_ide.tools import ui_tools

from ninja_ide.tools.logger import NinjaLogger
logger = NinjaLogger('ninja_ide.gui.dialogs.project_properties_widget')
DEBUG = logger.debug


# http://opensource.org/licenses/alphabetical
LICENCES = (
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
        self.projectData = ProjectData(self)
        self.projectExecution = ProjectExecution(self)
        self.projectMetadata = ProjectMetadata(self)
        self.tab_widget.addTab(self.projectData, translations.TR_PROJECT_DATA)
        self.tab_widget.addTab(self.projectExecution,
                               translations.TR_PROJECT_EXECUTION)
        self.tab_widget.addTab(self.projectMetadata,
                               translations.TR_PROJECT_METADATA)

        vbox.addWidget(self.tab_widget)
        self.btnSave = QPushButton(translations.TR_SAVE)
        self.btnCancel = QPushButton(translations.TR_CANCEL)
        hbox = QHBoxLayout()
        hbox.addWidget(self.btnCancel)
        hbox.addWidget(self.btnSave)

        vbox.addLayout(hbox)

        self.connect(self.btnCancel, SIGNAL("clicked()"), self.close)
        self.connect(self.btnSave, SIGNAL("clicked()"), self.save_properties)

    def save_properties(self):
        """Show warning message if Project Name is empty"""
        if not len(self.projectData.name.text().strip()):
            QMessageBox.critical(self, translations.TR_PROJECT_SAVE_INVALID,
                                 translations.TR_PROJECT_INVALID_MESSAGE)
            return

        self.project.name = self.projectData.name.text()
        self.project.description = self.projectData.description.toPlainText()
        self.project.license = self.projectData.cboLicense.currentText()
        self.project.main_file = self.projectExecution.path.text()
        self.project.url = self.projectData.url.text()
        self.project.project_type = self.projectData.txtType.text()
        # FIXME
        self.project.python_exec = \
            self.projectExecution.txtPythonInterpreter.text()
        self.project.python_path = \
            self.projectExecution.txtPythonPath.toPlainText()
        self.project.additional_builtins = [
            e for e in
            self.projectExecution.additional_builtins.text().split(' ') if e]
        self.project.pre_exec_script = self.projectExecution.txtPreExec.text()
        self.project.post_exec_script = self.projectExecution.txtPostExec.text()
        self.project.program_params = self.projectExecution.txtParams.text()
        self.project.venv = self.projectExecution.txtVenvPath.text()
        extensions = self.projectData.txtExtensions.text().split(', ')
        self.project.extensions = tuple(extensions)
        self.project.indentation = self.projectData.spinIndentation.value()
        self.project.use_tabs = bool(
            self.projectData.checkUseTabs.currentIndex())
        related = self.projectMetadata.txt_projects.toPlainText()
        related = [_path for _path in related.split('\n') if len(_path.strip())]
        self.project.related_projects = related
        self.project.save_project_properties()

        self.parent.refresh_file_filters()

        self.close()


class ProjectData(QWidget):
    """Project Data widget class"""

    def __init__(self, parent):
        super(ProjectData, self).__init__()
        self._parent = parent
        grid = QGridLayout(self)
        grid.addWidget(QLabel(translations.TR_PROJECT_NAME), 0, 0)
        self.name = QLineEdit()
        if not len(self._parent.project.name):
            self.name.setText(file_manager.get_basename(
                self._parent.project.path))
        else:
            self.name.setText(self._parent.project.name)
        grid.addWidget(self.name, 0, 1)
        grid.addWidget(QLabel(translations.TR_PROJECT_LOCATION), 1, 0)
        self.txtPath = QLineEdit()
        self.txtPath.setReadOnly(True)
        self.txtPath.setText(self._parent.project.path)
        grid.addWidget(self.txtPath, 1, 1)
        grid.addWidget(QLabel(translations.TR_PROJECT_TYPE), 2, 0)
        self.txtType = QLineEdit()
        completer = QCompleter(sorted(settings.PROJECT_TYPES))
        completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.txtType.setCompleter(completer)
        self.txtType.setPlaceholderText("python")
        self.txtType.setText(self._parent.project.project_type)
        grid.addWidget(self.txtType, 2, 1)
        grid.addWidget(QLabel(translations.TR_PROJECT_DESCRIPTION), 3, 0)
        self.description = QPlainTextEdit()
        self.description.setPlainText(self._parent.project.description)
        grid.addWidget(self.description, 3, 1)
        grid.addWidget(QLabel(translations.TR_PROJECT_URL), 4, 0)
        self.url = QLineEdit()
        self.url.setText(self._parent.project.url)
        self.url.setPlaceholderText('https://www.{}.com'.format(getuser()))
        grid.addWidget(self.url, 4, 1)
        grid.addWidget(QLabel(translations.TR_PROJECT_LICENSE), 5, 0)
        self.cboLicense = QComboBox()
        self.cboLicense.addItems(LICENCES)
        self.cboLicense.setCurrentIndex(12)
        index = self.cboLicense.findText(self._parent.project.license)
        self.cboLicense.setCurrentIndex(index)
        grid.addWidget(self.cboLicense, 5, 1)

        self.txtExtensions = QLineEdit()
        self.txtExtensions.setText(', '.join(self._parent.project.extensions))
        self.txtExtensions.setToolTip(
            translations.TR_PROJECT_EXTENSIONS_TOOLTIP)
        grid.addWidget(QLabel(translations.TR_PROJECT_EXTENSIONS), 6, 0)
        grid.addWidget(self.txtExtensions, 6, 1)
        labelTooltip = QLabel(translations.TR_PROJECT_EXTENSIONS_INSTRUCTIONS)
        grid.addWidget(labelTooltip, 7, 1)

        grid.addWidget(QLabel(translations.TR_PROJECT_INDENTATION), 8, 0)
        self.spinIndentation = QSpinBox()
        self.spinIndentation.setValue(self._parent.project.indentation)
        self.spinIndentation.setRange(2, 10)
        self.spinIndentation.setValue(4)
        self.spinIndentation.setSingleStep(2)
        grid.addWidget(self.spinIndentation, 8, 1)
        self.checkUseTabs = QComboBox()
        self.checkUseTabs.addItems([
            translations.TR_PREFERENCES_EDITOR_CONFIG_SPACES.capitalize(),
            translations.TR_PREFERENCES_EDITOR_CONFIG_TABS.capitalize()])
        self.checkUseTabs.setCurrentIndex(int(self._parent.project.use_tabs))
        grid.addWidget(self.checkUseTabs, 8, 2)


class ProjectExecution(QWidget):
    """Project Execution widget class"""

    def __init__(self, parent):
        super(ProjectExecution, self).__init__()
        self._parent = parent
        grid = QGridLayout(self)

        grid.addWidget(QLabel(translations.TR_PROJECT_MAIN_FILE), 0, 0)
        self.path = QLineEdit()
        self.path.setPlaceholderText(
            os.path.join(os.path.expanduser("~"), 'path', 'to', 'main.py'))
        ui_tools.LineEditButton(
            self.path, self.path.clear,
            self.style().standardPixmap(self.style().SP_TrashIcon))
        self.path.setText(self._parent.project.main_file)
        self.path.setReadOnly(True)
        self.btnBrowse = QPushButton(QIcon(
            self.style().standardPixmap(self.style().SP_FileIcon)), '')
        grid.addWidget(self.path, 0, 1)
        grid.addWidget(self.btnBrowse, 0, 2)

        # this should be changed, and ALL pythonPath names to
        # python_custom_interpreter or something like that. this is NOT the
        # PYTHONPATH
        self.txtPythonInterpreter = QLineEdit()
        self.txtPythonInterpreter.setText(self._parent.project.python_exec)
        self.txtPythonInterpreter.setCompleter(QCompleter(
            ('python', 'python2', 'python3', 'python.exe', 'pythonw.exe')))
        self.txtPythonInterpreter.setPlaceholderText("python")
        self.btnPythonPath = QPushButton(QIcon(":img/open"), '')
        grid.addWidget(QLabel(
            translations.TR_PROJECT_PYTHON_INTERPRETER), 1, 0)
        grid.addWidget(self.txtPythonInterpreter, 1, 1)
        grid.addWidget(self.btnPythonPath, 1, 2)

        grid.addWidget(QLabel(translations.TR_PROJECT_PYTHON_PATH), 2, 0)
        self.txtPythonPath = QPlainTextEdit()  # TODO : better widget
        self.txtPythonPath.setPlainText(self._parent.project.python_path)
        self.txtPythonPath.setToolTip(translations.TR_PROJECT_PATH_PER_LINE)
        grid.addWidget(self.txtPythonPath, 2, 1)

        # Additional builtins/globals for pyflakes
        grid.addWidget(QLabel(translations.TR_PROJECT_BUILTINS), 3, 0)
        self.additional_builtins = QLineEdit()
        self.additional_builtins.setText(
            ' '.join(self._parent.project.additional_builtins))
        self.additional_builtins.setToolTip(
            translations.TR_PROJECT_BUILTINS_TOOLTIP)
        grid.addWidget(self.additional_builtins, 3, 1)

        self.txtPreExec = QLineEdit()
        ui_tools.LineEditButton(
            self.txtPreExec, self.txtPreExec.clear,
            self.style().standardPixmap(self.style().SP_TrashIcon))
        self.txtPreExec.setReadOnly(True)
        self.txtPreExec.setText(self._parent.project.pre_exec_script)
        self.txtPreExec.setPlaceholderText(
            os.path.join(os.path.expanduser("~"), 'path', 'to', 'script.sh'))
        self.btnPreExec = QPushButton(QIcon(":img/open"), '')
        grid.addWidget(QLabel(translations.TR_PROJECT_PRE_EXEC), 4, 0)
        grid.addWidget(self.txtPreExec, 4, 1)
        grid.addWidget(self.btnPreExec, 4, 2)
        self.txtPostExec = QLineEdit()
        ui_tools.LineEditButton(
            self.txtPostExec, self.txtPostExec.clear,
            self.style().standardPixmap(self.style().SP_TrashIcon))
        self.txtPostExec.setReadOnly(True)
        self.txtPostExec.setText(self._parent.project.post_exec_script)
        self.txtPostExec.setPlaceholderText(
            os.path.join(os.path.expanduser("~"), 'path', 'to', 'script.sh'))
        self.btnPostExec = QPushButton(QIcon(":img/open"), '')
        grid.addWidget(QLabel(translations.TR_PROJECT_POST_EXEC), 5, 0)
        grid.addWidget(self.txtPostExec, 5, 1)
        grid.addWidget(self.btnPostExec, 5, 2)

        grid.addItem(QSpacerItem(5, 10, QSizePolicy.Expanding,
                     QSizePolicy.Expanding), 6, 0)

        # Properties
        grid.addWidget(QLabel(translations.TR_PROJECT_PROPERTIES), 7, 0)
        self.txtParams = QLineEdit()
        self.txtParams.setToolTip(translations.TR_PROJECT_PARAMS_TOOLTIP)
        self.txtParams.setText(self._parent.project.program_params)
        self.txtParams.setPlaceholderText('verbose, debug, force')
        grid.addWidget(QLabel(translations.TR_PROJECT_PARAMS), 8, 0)
        grid.addWidget(self.txtParams, 8, 1)
        #Widgets for virtualenv properties
        self.txtVenvPath = QLineEdit()
        ui_tools.LineEditButton(
            self.txtVenvPath, self.txtVenvPath.clear,
            self.style().standardPixmap(self.style().SP_TrashIcon))
        self.txtVenvPath.setText(self._parent.project.venv)
        self._dir_completer = QCompleter()
        self._dir_completer.setModel(QDirModel(self._dir_completer))
        self.txtVenvPath.setCompleter(self._dir_completer)
        self.txtVenvPath.setPlaceholderText(
            os.path.join(os.path.expanduser("~"), 'path', 'to', 'virtualenv'))
        self.btnVenvPath = QPushButton(QIcon(":img/open"), '')
        grid.addWidget(QLabel(translations.TR_PROJECT_VIRTUALENV), 9, 0)
        grid.addWidget(self.txtVenvPath, 9, 1)
        grid.addWidget(self.btnVenvPath, 9, 2)

        self.connect(self.btnBrowse, SIGNAL("clicked()"), self.select_file)
        self.connect(self.btnPythonPath, SIGNAL("clicked()"),
                     self._load_python_path)
        self.connect(self.btnVenvPath, SIGNAL("clicked()"),
                     self._load_python_venv)
        self.connect(self.btnPreExec, SIGNAL("clicked()"),
                     self.select_pre_exec_script)
        self.connect(self.btnPostExec, SIGNAL("clicked()"),
                     self.select_post_exec_script)

    def _load_python_path(self):
        """Ask the user a python path and set its value"""
        path = QFileDialog.getOpenFileName(
            self, translations.TR_PROJECT_SELECT_PYTHON_PATH)
        self.txtPythonInterpreter.setText(path)

    def _load_python_venv(self):
        """Ask the user a python venv and set its value"""
        venv = QFileDialog.getExistingDirectory(
            self, translations.TR_PROJECT_SELECT_VIRTUALENV)
        if sys.platform == 'win32':
            venv = os.path.join(venv, 'Scripts', 'python.exe')
        else:
            venv = os.path.join(venv, 'bin', 'python')
        #check if venv folder exists
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
        fileName = QFileDialog.getOpenFileName(
            self, translations.TR_PROJECT_SELECT_MAIN_FILE,
            self._parent.project.path,
            'Python PY(*.py);;Python Bytecode(*.py[codw]);;*(*.*)')
        if fileName != '':
            fileName = file_manager.convert_to_relative(
                self._parent.project.path, fileName)
            self.path.setText(fileName)

    def select_pre_exec_script(self):
        """Ask the user a python pre-exec script and set its value"""
        fileName = QFileDialog.getOpenFileName(
            self, translations.TR_PROJECT_SELECT_PRE_SCRIPT,
            self._parent.project.path,
            '*(*.*);;Bash(*.sh);;Python PY(*.py);;Python Bytecode(*.py[codw]);;'
            'Bat(*.bat);;Cmd(*.cmd);;Exe(*.exe);;Bin(*.bin);;App(*.app)')
        if fileName != '':
            fileName = file_manager.convert_to_relative(
                self._parent.project.path, fileName)
            self.txtPreExec.setText(fileName)

    def select_post_exec_script(self):
        """Ask the user a python post-exec script and set its value"""
        fileName = QFileDialog.getOpenFileName(
            self, translations.TR_PROJECT_SELECT_POST_SCRIPT,
            self._parent.project.path,
            '*(*.*);;Bash(*.sh);;Python PY(*.py);;Python Bytecode(*.py[codw]);;'
            'Bat(*.bat);;Cmd(*.cmd);;Exe(*.exe);;Bin(*.bin);;App(*.app)')
        if fileName != '':
            fileName = file_manager.convert_to_relative(
                self._parent.project.path, fileName)
            self.txtPostExec.setText(fileName)


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
