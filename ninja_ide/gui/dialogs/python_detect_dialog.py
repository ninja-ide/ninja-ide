# -*- coding: utf-8 -*-

from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QListWidget
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QSpacerItem
from PyQt4.QtGui import QSizePolicy
from PyQt4.QtCore import QSettings
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QSize
from PyQt4.QtCore import SIGNAL

from ninja_ide import resources
from ninja_ide.core import settings


class PythonDetectDialog(QDialog):

    def __init__(self, suggested, parent=None):
        super(PythonDetectDialog, self).__init__(parent, Qt.Dialog)
        self.setMaximumSize(QSize(0, 0))
        self.setWindowTitle("Configure Python Path")

        vbox = QVBoxLayout(self)

        lblMessage = QLabel(self.tr("We have detected that you are using " +
            "Windows,\nplease choose the proper " +
            "Python application for you:"))
        vbox.addWidget(lblMessage)

        self.listPaths = QListWidget()
        self.listPaths.setSelectionMode(QListWidget.SingleSelection)
        vbox.addWidget(self.listPaths)

        hbox = QHBoxLayout()
        hbox.addSpacerItem(QSpacerItem(1, 0, QSizePolicy.Expanding))
        btnCancel = QPushButton(self.tr("Cancel"))
        btnAccept = QPushButton(self.tr("Accept"))
        hbox.addWidget(btnCancel)
        hbox.addWidget(btnAccept)
        vbox.addLayout(hbox)

        self.connect(btnAccept, SIGNAL("clicked()"), self._set_python_path)
        self.connect(btnCancel, SIGNAL("clicked()"), self.close)

        for path in suggested:
            self.listPaths.addItem(path)
        self.listPaths.setCurrentRow(0)

    def _set_python_path(self):
        python_path = self.listPaths.currentItem().text()

        qsettings = QSettings(resources.SETTINGS_PATH, QSettings.IniFormat)
        settings.PYTHON_PATH = python_path
        settings.PYTHON_PATH_CONFIGURED_BY_USER = True
        qsettings.setValue('preferences/execution/pythonPath', python_path)
        qsettings.setValue('preferences/execution/pythonPathConfigured', True)
        self.close()