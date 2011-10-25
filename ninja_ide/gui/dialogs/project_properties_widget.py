# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os
import sys

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
        grid = QGridLayout(self)
        grid.addWidget(QLabel(self.tr("Name:")), 0, 0)
        self.name = QLineEdit()
        if self._item.name == '':
            self.name.setText(file_manager.get_basename(self._item.path))
        else:
            self.name.setText(self._item.name)
        grid.addWidget(self.name, 0, 1)
        grid.addWidget(QLabel(self.tr("Project Type:")), 1, 0)
        self.txtType = QLineEdit()
        completer = QCompleter(sorted(settings.PROJECT_TYPES))
        completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.txtType.setCompleter(completer)
        self.txtType.setText(self._item.projectType)
        grid.addWidget(self.txtType, 1, 1)
        grid.addWidget(QLabel(self.tr("Description:")), 2, 0)
        self.description = QPlainTextEdit()
        self.description.setPlainText(self._item.description)
        grid.addWidget(self.description, 2, 1)
        grid.addWidget(QLabel(self.tr("URL:")), 3, 0)
        self.url = QLineEdit()
        self.url.setText(self._item.url)
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
        index = self.cboLicense.findText(self._item.license)
        self.cboLicense.setCurrentIndex(index)
        grid.addWidget(self.cboLicense, 4, 1)
        grid.addWidget(QLabel(self.tr("Main File:")), 5, 0)
        self.path = QLineEdit()
        ui_tools.LineEditButton(self.path, self.path.clear,
            self.style().standardPixmap(self.style().SP_TrashIcon))
        self.path.setText(self._item.mainFile)
        self.path.setReadOnly(True)
        self.btnBrowse = QPushButton(QIcon(
            self.style().standardPixmap(self.style().SP_FileIcon)), '')
        hbox = QHBoxLayout()
        hbox.addWidget(self.path)
        hbox.addWidget(self.btnBrowse)
        grid.addLayout(hbox, 5, 1)

        self.txtExtensions = QLineEdit()
        self.txtExtensions.setText(str(', '.join(self._item.extensions)))
        grid.addWidget(QLabel(self.tr("Supported Extensions:")), 6, 0)
        grid.addWidget(self.txtExtensions, 6, 1)

        self.txtPythonPath = QLineEdit()
        self.txtPythonPath.setText(self._item.pythonPath)
        self.btnPythonPath = QPushButton(QIcon(resources.IMAGES['open']), '')
        grid.addWidget(QLabel(self.tr("Python Path:")), 7, 0)
        grid.addWidget(self.txtPythonPath, 7, 1)
        grid.addWidget(self.btnPythonPath, 7, 2)

        self.txtParams = QLineEdit()
        self.txtParams.setToolTip(
            self.tr("Separate the params with commas (ie: help, verbose)"))
        self.txtParams.setText(self._item.programParams)
        grid.addWidget(QLabel(self.tr("Params:")), 8, 0)
        grid.addWidget(self.txtParams, 8, 1)

        #Widgets for virtualenv properties
        self.txtVenvPath = QLineEdit()
        ui_tools.LineEditButton(self.txtVenvPath, self.txtVenvPath.clear,
            self.style().standardPixmap(self.style().SP_TrashIcon))
        self.txtVenvPath.setText(self._item.venv)
        self.txtVenvPath.setReadOnly(True)
        self.btnVenvPath = QPushButton(QIcon(resources.IMAGES['open']), '')
        grid.addWidget(QLabel(self.tr("Virtualenv Folder:")), 9, 0)
        grid.addWidget(self.txtVenvPath, 9, 1)
        grid.addWidget(self.btnVenvPath, 9, 2)

        self.btnSave = QPushButton(self.tr("Save"))
        self.btnCancel = QPushButton(self.tr("Cancel"))
        hbox3 = QHBoxLayout()
        hbox3.addWidget(self.btnCancel)
        hbox3.addWidget(self.btnSave)
        grid.addLayout(hbox3, 10, 1)

        self.connect(self.btnBrowse, SIGNAL("clicked()"), self.select_file)
        self.connect(self.btnCancel, SIGNAL("clicked()"), self.close)
        self.connect(self.btnSave, SIGNAL("clicked()"), self.save_properties)
        self.connect(self.btnPythonPath, SIGNAL("clicked()"),
            self._load_python_path)
        self.connect(self.btnVenvPath, SIGNAL("clicked()"),
            self._load_python_venv)

    def _load_python_path(self):
        path = unicode(QFileDialog.getOpenFileName(
            self, self.tr("Select Python Path")))
        self.txtPythonPath.setText(path)

    def _load_python_venv(self):
        venv = unicode(QFileDialog.getExistingDirectory(
            self, self.tr("Select Virtualenv Folder")))
        if sys.platform == 'win32':
            venv = os.path.join(venv, 'Scripts', 'python')
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
                        self._item.path, '(*.py);;(*.*)'))
        if fileName != '':
            fileName = file_manager.convert_to_relative(
                self._item.path, fileName)
            self.path.setText(fileName)

    def save_properties(self):
        if str(self.name.text()).strip() == '':
            QMessageBox.critical(self, self.tr("Properties Invalid"),
                self.tr("The Project must have a name."))
            return
        tempName = self._item.name
        self._item.name = unicode(self.name.text())
        self._item.description = unicode(self.description.toPlainText())
        self._item.license = unicode(self.cboLicense.currentText())
        self._item.mainFile = unicode(self.path.text())
        self._item.url = unicode(self.url.text())
        self._item.projectType = unicode(self.txtType.text())
        self._item.pythonPath = unicode(self.txtPythonPath.text())
        self._item.programParams = unicode(self.txtParams.text())
        self._item.venv = unicode(self.txtVenvPath.text())
        extensions = unicode(self.txtExtensions.text()).split(', ')
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
