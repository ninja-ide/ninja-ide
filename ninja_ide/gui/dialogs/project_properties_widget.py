# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os
import sys

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
from PyQt4.QtGui import QPlainTextEdit
from PyQt4.QtGui import QComboBox
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QFileDialog
from PyQt4.QtGui import QMessageBox
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import Qt

from ninja_ide import resources
from ninja_ide.core import file_manager
from ninja_ide.core import settings
from ninja_ide.tools import json_manager
from ninja_ide.tools import ui_tools


class ProjectProperties(QDialog):

    def __init__(self, item, parent=None):
        QDialog.__init__(self, parent, Qt.Dialog)
        self.setModal(True)
        self._item = item
        self.setWindowTitle(self.tr("Project Properties"))
        vbox = QVBoxLayout(self)
        self.tab_widget = QTabWidget()
        self.projectData = ProjectData(self)
        self.projectExecution = ProjectExecution(self)
        self.tab_widget.addTab(self.projectData, self.tr("Project Data"))
        self.tab_widget.addTab(self.projectExecution,
            self.tr("Project Execution"))

        vbox.addWidget(self.tab_widget)
        self.btnSave = QPushButton(self.tr("Save"))
        self.btnCancel = QPushButton(self.tr("Cancel"))
        hbox = QHBoxLayout()
        hbox.addWidget(self.btnCancel)
        hbox.addWidget(self.btnSave)

        vbox.addLayout(hbox)

        self.connect(self.btnCancel, SIGNAL("clicked()"), self.close)
        self.connect(self.btnSave, SIGNAL("clicked()"), self.save_properties)

    def save_properties(self):
        if unicode(self.projectData.name.text()).strip() == '':
            QMessageBox.critical(self, self.tr("Properties Invalid"),
                self.tr("The Project must have a name."))
            return
        tempName = self._item.name
        self._item.name = unicode(self.projectData.name.text())
        self._item.description = unicode(
            self.projectData.description.toPlainText())
        self._item.license = unicode(self.projectData.cboLicense.currentText())
        self._item.mainFile = unicode(self.projectExecution.path.text())
        self._item.url = unicode(self.projectData.url.text())
        self._item.projectType = unicode(self.projectData.txtType.text())
        self._item.pythonPath = unicode(
            self.projectExecution.txtPythonPath.text())
        self._item.preExecScript = unicode(
            self.projectExecution.txtPreExec.text())
        self._item.postExecScript = unicode(
            self.projectExecution.txtPostExec.text())
        self._item.programParams = unicode(
            self.projectExecution.txtParams.text())
        self._item.venv = unicode(self.projectExecution.txtVenvPath.text())
        extensions = unicode(self.projectData.txtExtensions.text()).split(', ')
        self._item.extensions = tuple(extensions)
        #save project properties
        project = {}
        project['name'] = self._item.name
        project['description'] = self._item.description
        project['url'] = self._item.url
        project['license'] = self._item.license
        project['mainFile'] = self._item.mainFile
        project['project-type'] = self._item.projectType
        project['supported-extensions'] = self._item.extensions
        project['pythonPath'] = self._item.pythonPath
        project['preExecScript'] = self._item.preExecScript
        project['postExecScript'] = self._item.postExecScript
        project['venv'] = self._item.venv
        project['programParams'] = self._item.programParams
        if tempName != self._item.name and \
            file_manager.file_exists(self._item.path, tempName + '.nja'):
            file_manager.delete_file(self._item.path, tempName + '.nja')
        json_manager.create_ninja_project(
            self._item.path, self._item.name, project)
        self._item.setText(0, self._item.name)
        self._item.setToolTip(0, self._item.name)
        if self._item.extensions != settings.SUPPORTED_EXTENSIONS:
            self._item._parent._refresh_project(self._item)
        self.close()


class ProjectData(QWidget):

    def __init__(self, parent):
        super(ProjectData, self).__init__()
        self._parent = parent
        grid = QGridLayout(self)
        grid.addWidget(QLabel(self.tr("Name:")), 0, 0)
        self.name = QLineEdit()
        if self._parent._item.name == '':
            self.name.setText(file_manager.get_basename(
                self._parent._item.path))
        else:
            self.name.setText(self._parent._item.name)
        grid.addWidget(self.name, 0, 1)
        grid.addWidget(QLabel(self.tr("Project Type:")), 1, 0)
        self.txtType = QLineEdit()
        completer = QCompleter(sorted(settings.PROJECT_TYPES))
        completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.txtType.setCompleter(completer)
        self.txtType.setText(self._parent._item.projectType)
        grid.addWidget(self.txtType, 1, 1)
        grid.addWidget(QLabel(self.tr("Description:")), 2, 0)
        self.description = QPlainTextEdit()
        self.description.setPlainText(self._parent._item.description)
        grid.addWidget(self.description, 2, 1)
        grid.addWidget(QLabel(self.tr("URL:")), 3, 0)
        self.url = QLineEdit()
        self.url.setText(self._parent._item.url)
        grid.addWidget(self.url, 3, 1)
        grid.addWidget(QLabel(self.tr("Licence:")), 4, 0)
        self.cboLicense = QComboBox()
        self.cboLicense.addItem('Apache License 2.0')
        self.cboLicense.addItem('Artistic License/GPL')
        self.cboLicense.addItem('Eclipse Public License 1.0')
        self.cboLicense.addItem('GNU General Public License v2')
        self.cboLicense.addItem('GNU General Public License v3')
        self.cboLicense.addItem('GNU Lesser General Public License')
        self.cboLicense.addItem('MIT License')
        self.cboLicense.addItem('Mozilla Public License 1.1')
        self.cboLicense.addItem('New BSD License')
        self.cboLicense.addItem('Other Open Source')
        self.cboLicense.addItem('Other')
        self.cboLicense.setCurrentIndex(4)
        index = self.cboLicense.findText(self._parent._item.license)
        self.cboLicense.setCurrentIndex(index)
        grid.addWidget(self.cboLicense, 4, 1)

        self.txtExtensions = QLineEdit()
        self.txtExtensions.setText(
            unicode(', '.join(self._parent._item.extensions)))
        grid.addWidget(QLabel(self.tr("Supported Extensions:")), 5, 0)
        grid.addWidget(self.txtExtensions, 5, 1)


class ProjectExecution(QWidget):

    def __init__(self, parent):
        super(ProjectExecution, self).__init__()
        self._parent = parent
        grid = QGridLayout(self)

        grid.addWidget(QLabel(self.tr("Main File:")), 0, 0)
        self.path = QLineEdit()
        ui_tools.LineEditButton(self.path, self.path.clear,
            self.style().standardPixmap(self.style().SP_TrashIcon))
        self.path.setText(self._parent._item.mainFile)
        self.path.setReadOnly(True)
        self.btnBrowse = QPushButton(QIcon(
            self.style().standardPixmap(self.style().SP_FileIcon)), '')
        grid.addWidget(self.path, 0, 1)
        grid.addWidget(self.btnBrowse, 0, 2)

        self.txtPythonPath = QLineEdit()
        self.txtPythonPath.setText(self._parent._item.pythonPath)
        self.btnPythonPath = QPushButton(QIcon(resources.IMAGES['open']), '')
        grid.addWidget(QLabel(self.tr("Python Path:")), 1, 0)
        grid.addWidget(self.txtPythonPath, 1, 1)
        grid.addWidget(self.btnPythonPath, 1, 2)

        self.txtPreExec = QLineEdit()
        ui_tools.LineEditButton(self.txtPreExec, self.txtPreExec.clear,
            self.style().standardPixmap(self.style().SP_TrashIcon))
        self.txtPreExec.setReadOnly(True)
        self.txtPreExec.setText(self._parent._item.preExecScript)
        self.btnPreExec = QPushButton(QIcon(resources.IMAGES['open']), '')
        grid.addWidget(QLabel(self.tr("Pre-exec Script:")), 2, 0)
        grid.addWidget(self.txtPreExec, 2, 1)
        grid.addWidget(self.btnPreExec, 2, 2)
        self.txtPostExec = QLineEdit()
        ui_tools.LineEditButton(self.txtPostExec, self.txtPostExec.clear,
            self.style().standardPixmap(self.style().SP_TrashIcon))
        self.txtPostExec.setReadOnly(True)
        self.txtPostExec.setText(self._parent._item.postExecScript)
        self.btnPostExec = QPushButton(QIcon(resources.IMAGES['open']), '')
        grid.addWidget(QLabel(self.tr("Post-exec Script:")), 3, 0)
        grid.addWidget(self.txtPostExec, 3, 1)
        grid.addWidget(self.btnPostExec, 3, 2)

        grid.addItem(QSpacerItem(5, 10, QSizePolicy.Expanding,
            QSizePolicy.Expanding), 4, 0)

        # Properties
        grid.addWidget(QLabel(self.tr("Properties:")), 5, 0)
        self.txtParams = QLineEdit()
        self.txtParams.setToolTip(
            self.tr("Separate the params with commas (ie: help, verbose)"))
        self.txtParams.setText(self._parent._item.programParams)
        grid.addWidget(QLabel(self.tr("Params (comma separated):")), 6, 0)
        grid.addWidget(self.txtParams, 6, 1)
        #Widgets for virtualenv properties
        self.txtVenvPath = QLineEdit()
        ui_tools.LineEditButton(self.txtVenvPath, self.txtVenvPath.clear,
            self.style().standardPixmap(self.style().SP_TrashIcon))
        self.txtVenvPath.setText(self._parent._item.venv)
        self.txtVenvPath.setReadOnly(True)
        self.btnVenvPath = QPushButton(QIcon(resources.IMAGES['open']), '')
        grid.addWidget(QLabel(self.tr("Virtualenv Folder:")), 7, 0)
        grid.addWidget(self.txtVenvPath, 7, 1)
        grid.addWidget(self.btnVenvPath, 7, 2)

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
        path = unicode(QFileDialog.getOpenFileName(
            self, self.tr("Select Python Path")))
        self.txtPythonPath.setText(path)

    def _load_python_venv(self):
        venv = unicode(QFileDialog.getExistingDirectory(
            self, self.tr("Select Virtualenv Folder")))
        if sys.platform == 'win32':
            venv = os.path.join(venv, 'Scripts', 'python.exe')
        else:
            venv = os.path.join(venv, 'bin', 'python')
        #check if venv folder exists
        if not os.path.exists(venv):
            QMessageBox.information(self,
                self.tr("Virtualenv Folder"),
                self.tr("This is not a valid Virtualenv Folder"))
            self.txtVenvPath.setText("")
        else:
            self.txtVenvPath.setText(venv)

    def select_file(self):
        fileName = unicode(QFileDialog.getOpenFileName(
            self, self.tr("Select Main File"),
                        self._parent._item.path, '(*.py);;(*.*)'))
        if fileName != '':
            fileName = file_manager.convert_to_relative(
                self._parent._item.path, fileName)
            self.path.setText(fileName)

    def select_pre_exec_script(self):
        fileName = unicode(QFileDialog.getOpenFileName(
            self, self.tr("Select Pre Execution Script File"),
                        self._parent._item.path, '(*.*)'))
        if fileName != '':
            fileName = file_manager.convert_to_relative(
                self._parent._item.path, fileName)
            self.txtPreExec.setText(fileName)

    def select_post_exec_script(self):
        fileName = unicode(QFileDialog.getOpenFileName(
            self, self.tr("Select Post Execution Script File"),
                        self._parent._item.path, '(*.*)'))
        if fileName != '':
            fileName = file_manager.convert_to_relative(
                self._parent._item.path, fileName)
            self.txtPostExec.setText(fileName)
