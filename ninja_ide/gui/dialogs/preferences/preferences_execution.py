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

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QGroupBox
from PyQt4.QtGui import QCheckBox
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QFileDialog
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QComboBox
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QCompleter
from PyQt4.QtGui import QDirModel
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QDir

from ninja_ide import translations
from ninja_ide.core import settings
from ninja_ide.gui.ide import IDE
from ninja_ide.gui.dialogs.preferences import preferences


class GeneralExecution(QWidget):
    """General Execution widget class"""

    def __init__(self, parent):
        super(GeneralExecution, self).__init__()
        vbox = QVBoxLayout(self)

        groupExecution = QGroupBox(translations.TR_WORKSPACE_PROJECTS)
        grid = QVBoxLayout(groupExecution)

        #Python Path
        hPath = QHBoxLayout()
        self._txtPythonPath = QLineEdit()
        self._btnPythonPath = QPushButton(QIcon(':img/open'), '')
        self.completer, self.dirs = QCompleter(self), QDirModel(self)
        self.dirs.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot)
        self.completer.setModel(self.dirs)
        self._txtPythonPath.setCompleter(self.completer)
        hPath.addWidget(QLabel(translations.TR_SELECT_PYTHON_EXEC))
        hPath.addWidget(self._txtPythonPath)
        hPath.addWidget(self._btnPythonPath)
        grid.addLayout(hPath)
        #Python Miscellaneous Execution options
        self.check_B = QCheckBox(translations.TR_SELECT_EXEC_OPTION_B)
        self.check_d = QCheckBox(translations.TR_SELECT_EXEC_OPTION_D)
        self.check_E = QCheckBox(translations.TR_SELECT_EXEC_OPTION_E)
        self.check_O = QCheckBox(translations.TR_SELECT_EXEC_OPTION_O)
        self.check_OO = QCheckBox(translations.TR_SELECT_EXEC_OPTION_OO)
        self.check_Q = QCheckBox(translations.TR_SELECT_EXEC_OPTION_Q)
        self.comboDivision = QComboBox()
        self.comboDivision.addItems(['old', 'new', 'warn', 'warnall'])
        self.check_s = QCheckBox(translations.TR_SELECT_EXEC_OPTION_s)
        self.check_S = QCheckBox(translations.TR_SELECT_EXEC_OPTION_S)
        self.check_t = QCheckBox(translations.TR_SELECT_EXEC_OPTION_T)
        self.check_tt = QCheckBox(translations.TR_SELECT_EXEC_OPTION_TT)
        self.check_v = QCheckBox(translations.TR_SELECT_EXEC_OPTION_V)
        self.check_W = QCheckBox(translations.TR_SELECT_EXEC_OPTION_W)
        self.comboWarning = QComboBox()
        self.comboWarning.addItems(
            ['default', 'ignore', 'all', 'module', 'once', 'error'])
        self.check_x = QCheckBox(translations.TR_SELECT_EXEC_OPTION_X)
        self.check_3 = QCheckBox(translations.TR_SELECT_EXEC_OPTION_3)
        grid.addWidget(self.check_B)
        grid.addWidget(self.check_d)
        grid.addWidget(self.check_E)
        grid.addWidget(self.check_O)
        grid.addWidget(self.check_OO)
        hDiv = QHBoxLayout()
        hDiv.addWidget(self.check_Q)
        hDiv.addWidget(self.comboDivision)
        grid.addLayout(hDiv)
        grid.addWidget(self.check_s)
        grid.addWidget(self.check_S)
        grid.addWidget(self.check_t)
        grid.addWidget(self.check_tt)
        grid.addWidget(self.check_v)
        hWarn = QHBoxLayout()
        hWarn.addWidget(self.check_W)
        hWarn.addWidget(self.comboWarning)
        grid.addLayout(hWarn)
        grid.addWidget(self.check_x)
        grid.addWidget(self.check_3)

        #Settings
        self._txtPythonPath.setText(settings.PYTHON_EXEC)
        options = settings.EXECUTION_OPTIONS.split()
        if '-B' in options:
            self.check_B.setChecked(True)
        if '-d' in options:
            self.check_d.setChecked(True)
        if '-E' in options:
            self.check_E.setChecked(True)
        if '-O' in options:
            self.check_O.setChecked(True)
        if '-OO' in options:
            self.check_OO.setChecked(True)
        if settings.EXECUTION_OPTIONS.find('-Q') > -1:
            self.check_Q.setChecked(True)
            index = settings.EXECUTION_OPTIONS.find('-Q')
            opt = settings.EXECUTION_OPTIONS[index + 2:].split(' ', 1)[0]
            index = self.comboDivision.findText(opt)
            self.comboDivision.setCurrentIndex(index)
        if '-s' in options:
            self.check_s.setChecked(True)
        if '-S' in options:
            self.check_S.setChecked(True)
        if '-t' in options:
            self.check_t.setChecked(True)
        if '-tt' in options:
            self.check_tt.setChecked(True)
        if '-v' in options:
            self.check_v.setChecked(True)
        if settings.EXECUTION_OPTIONS.find('-W') > -1:
            self.check_W.setChecked(True)
            index = settings.EXECUTION_OPTIONS.find('-W')
            opt = settings.EXECUTION_OPTIONS[index + 2:].split(' ', 1)[0]
            index = self.comboWarning.findText(opt)
            self.comboWarning.setCurrentIndex(index)
        if '-x' in options:
            self.check_x.setChecked(True)
        if '-3' in options:
            self.check_3.setChecked(True)

        vbox.addWidget(groupExecution)

        #Signals
        self.connect(self._btnPythonPath,
            SIGNAL("clicked()"), self._load_python_path)

    def _load_python_path(self):
        """Ask the user for a Python Path"""
        path = QFileDialog.getOpenFileName(self,
            translations.TR_SELECT_SELECT_PYTHON_EXEC)
        if path:
            self._txtPythonPath.setText(path)

    def save(self):
        """Save all the Execution Preferences"""
        qsettings = IDE.ninja_settings()
        qsettings.beginGroup('preferences')
        qsettings.beginGroup('execution')
        qsettings.setValue('pythonPath', self._txtPythonPath.text())
        settings.PYTHON_PATH = self._txtPythonPath.text()
        options = ''
        if self.check_B.isChecked():
            options += ' -B'
        if self.check_d.isChecked():
            options += ' -d'
        if self.check_E.isChecked():
            options += ' -E'
        if self.check_O.isChecked():
            options += ' -O'
        if self.check_OO.isChecked():
            options += ' -OO'
        if self.check_Q.isChecked():
            options += ' -Q' + self.comboDivision.currentText()
        if self.check_s.isChecked():
            options += ' -s'
        if self.check_S.isChecked():
            options += ' -S'
        if self.check_t.isChecked():
            options += ' -t'
        if self.check_tt.isChecked():
            options += ' -tt'
        if self.check_v.isChecked():
            options += ' -v'
        if self.check_W.isChecked():
            options += ' -W' + self.comboWarning.currentText()
        if self.check_x.isChecked():
            options += ' -x'
        if self.check_3.isChecked():
            options += ' -3'
        settings.EXECUTION_OPTIONS = options
        qsettings.setValue('executionOptions', options)
        qsettings.endGroup()
        qsettings.endGroup()


preferences.Preferences.register_configuration('GENERAL', GeneralExecution,
    translations.TR_PREFERENCES_EXECUTION,
    weight=1, subsection='EXECUTION')