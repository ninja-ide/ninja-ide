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
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QGroupBox
from PyQt4.QtGui import QCheckBox
from PyQt4.QtGui import QComboBox
from PyQt4.QtGui import QGridLayout
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QFileDialog
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QColorDialog
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL

from ninja_ide import translations
from ninja_ide.core import settings
from ninja_ide.gui.ide import IDE
from ninja_ide.gui.dialogs.preferences import preferences
from ninja_ide.tools import ui_tools


class GeneralConfiguration(QWidget):
    """General Configuration class"""

    def __init__(self, parent):
        super(GeneralConfiguration, self).__init__()
        self._preferences = parent
        vbox = QVBoxLayout(self)

        groupBoxStart = QGroupBox(translations.TR_PREFERENCES_GENERAL_START)
        groupBoxClose = QGroupBox(translations.TR_PREFERENCES_GENERAL_CLOSE)
        groupBoxWorkspace = QGroupBox(
            translations.TR_PREFERENCES_GENERAL_WORKSPACE)
        groupBoxNoti = QGroupBox(translations.TR_NOTIFICATION)
        groupBoxReset = QGroupBox(translations.TR_PREFERENCES_GENERAL_RESET)

        #Start
        vboxStart = QVBoxLayout(groupBoxStart)
        self._checkLastSession = QCheckBox(
            translations.TR_PREFERENCES_GENERAL_LOAD_LAST_SESSION)
        self._checkActivatePlugins = QCheckBox(
            translations.TR_PREFERENCES_GENERAL_ACTIVATE_PLUGINS)
        self._checkNotifyUpdates = QCheckBox(
            translations.TR_PREFERENCES_GENERAL_NOTIFY_UPDATES)
        self._checkShowStartPage = QCheckBox(
            translations.TR_PREFERENCES_GENERAL_SHOW_START_PAGE)
        vboxStart.addWidget(self._checkLastSession)
        vboxStart.addWidget(self._checkActivatePlugins)
        vboxStart.addWidget(self._checkNotifyUpdates)
        vboxStart.addWidget(self._checkShowStartPage)
        #Close
        vboxClose = QVBoxLayout(groupBoxClose)
        self._checkConfirmExit = QCheckBox(
            translations.TR_PREFERENCES_GENERAL_CONFIRM_EXIT)
        vboxClose.addWidget(self._checkConfirmExit)
        #Workspace and Project
        gridWorkspace = QGridLayout(groupBoxWorkspace)
        self._txtWorkspace = QLineEdit()
        ui_tools.LineEditButton(
            self._txtWorkspace,
            self._txtWorkspace.clear,
            self.style().standardPixmap(self.style().SP_TrashIcon))
        self._txtWorkspace.setReadOnly(True)
        self._btnWorkspace = QPushButton(QIcon(':img/openFolder'), '')
        gridWorkspace.addWidget(
            QLabel(translations.TR_PREFERENCES_GENERAL_WORKSPACE), 0, 0,
            Qt.AlignRight)
        gridWorkspace.addWidget(self._txtWorkspace, 0, 1)
        gridWorkspace.addWidget(self._btnWorkspace, 0, 2)
        self._txtExtensions = QLineEdit()
        self._txtExtensions.setToolTip(
            translations.TR_PROJECT_EXTENSIONS_TOOLTIP)
        gridWorkspace.addWidget(QLabel(
            translations.TR_PREFERENCES_GENERAL_SUPPORTED_EXT), 1, 0,
            Qt.AlignRight)
        gridWorkspace.addWidget(self._txtExtensions, 1, 1)
        labelTooltip = QLabel(translations.TR_PROJECT_EXTENSIONS_INSTRUCTIONS)
        gridWorkspace.addWidget(labelTooltip, 2, 1)

        # Notification
        hboxNoti, self._notify_position = QHBoxLayout(groupBoxNoti), QComboBox()
        self._notify_position.addItems(
            [translations.TR_BOTTOM + "-" + translations.TR_LEFT,
             translations.TR_BOTTOM + "-" + translations.TR_RIGHT,
             translations.TR_TOP + "-" + translations.TR_LEFT,
             translations.TR_TOP + "-" + translations.TR_RIGHT])
        self._notify_color = QPushButton(
            translations.TR_EDITOR_SCHEME_PICK_COLOR)
        self._notification_choosed_color = settings.NOTIFICATION_COLOR
        hboxNoti.addWidget(QLabel(translations.TR_POSITION_ON_SCREEN))
        hboxNoti.addWidget(self._notify_position)
        hboxNoti.addWidget(self._notify_color, 0, Qt.AlignRight)

        # Resetting preferences
        vboxReset = QVBoxLayout(groupBoxReset)
        self._btnReset = QPushButton(
            translations.TR_PREFERENCES_GENERAL_RESET_PREFERENCES)
        vboxReset.addWidget(self._btnReset, alignment=Qt.AlignLeft)

        #Settings
        qsettings = IDE.ninja_settings()
        qsettings.beginGroup('preferences')
        qsettings.beginGroup('general')
        self._checkLastSession.setChecked(
            qsettings.value('loadFiles', True, type=bool))
        self._checkActivatePlugins.setChecked(
            qsettings.value('activatePlugins', defaultValue=True, type=bool))
        self._checkNotifyUpdates.setChecked(
            qsettings.value('preferences/general/notifyUpdates',
                            defaultValue=True, type=bool))
        self._checkShowStartPage.setChecked(settings.SHOW_START_PAGE)
        self._checkConfirmExit.setChecked(settings.CONFIRM_EXIT)
        self._txtWorkspace.setText(settings.WORKSPACE)
        extensions = ', '.join(settings.SUPPORTED_EXTENSIONS)
        self._txtExtensions.setText(extensions)
        self._notify_position.setCurrentIndex(settings.NOTIFICATION_POSITION)
        qsettings.endGroup()
        qsettings.endGroup()

        vbox.addWidget(groupBoxStart)
        vbox.addWidget(groupBoxClose)
        vbox.addWidget(groupBoxWorkspace)
        vbox.addWidget(groupBoxNoti)
        vbox.addWidget(groupBoxReset)

        #Signals
        self.connect(self._btnWorkspace, SIGNAL("clicked()"),
                     self._load_workspace)
        self.connect(self._notify_color, SIGNAL("clicked()"), self._pick_color)
        self.connect(self._btnReset, SIGNAL('clicked()'),
                     self._reset_preferences)
        self.connect(self._preferences, SIGNAL("savePreferences()"), self.save)

    def _pick_color(self):
        """Ask the user for a Color"""
        choosed_color = QColorDialog.getColor()
        if choosed_color.isValid():
            self._notification_choosed_color = choosed_color.name()

    def _load_workspace(self):
        """Ask the user for a Workspace path"""
        path = QFileDialog.getExistingDirectory(
            self, translations.TR_PREFERENCES_GENERAL_SELECT_WORKSPACE)
        self._txtWorkspace.setText(path)

    def _load_python_path(self):
        """Ask the user for a Python path"""
        path = QFileDialog.getOpenFileName(
            self, translations.TR_PREFERENCES_GENERAL_SELECT_PYTHON_PATH)
        if path:
            self._txtPythonPath.setText(path)

    def save(self):
        """Method to Save all preferences values"""
        qsettings = IDE.ninja_settings()
        qsettings.setValue('preferences/general/loadFiles',
                           self._checkLastSession.isChecked())
        qsettings.setValue('preferences/general/activatePlugins',
                           self._checkActivatePlugins.isChecked())
        qsettings.setValue('preferences/general/notifyUpdates',
                           self._checkNotifyUpdates.isChecked())
        qsettings.setValue('preferences/general/showStartPage',
                           self._checkShowStartPage.isChecked())
        qsettings.setValue('preferences/general/confirmExit',
                           self._checkConfirmExit.isChecked())
        settings.CONFIRM_EXIT = self._checkConfirmExit.isChecked()
        qsettings.setValue('preferences/general/workspace',
                           self._txtWorkspace.text())
        settings.WORKSPACE = self._txtWorkspace.text()
        extensions = str(self._txtExtensions.text()).split(',')
        extensions = [e.strip() for e in extensions]
        qsettings.setValue('preferences/general/supportedExtensions',
                           extensions)
        settings.SUPPORTED_EXTENSIONS = list(extensions)
        settings.NOTIFICATION_POSITION = self._notify_position.currentIndex()
        qsettings.setValue('preferences/general/notification_position',
                           settings.NOTIFICATION_POSITION)
        settings.NOTIFICATION_COLOR = self._notification_choosed_color
        qsettings.setValue('preferences/general/notification_color',
                           settings.NOTIFICATION_COLOR)

    def _reset_preferences(self):
        """Method to Reset all Preferences to default values"""
        result = QMessageBox.question(
            self,
            translations.TR_PREFERENCES_GENERAL_RESET_TITLE,
            translations.TR_PREFERENCES_GENERAL_RESET_BODY,
            buttons=QMessageBox.Yes | QMessageBox.No)
        if result == QMessageBox.Yes:
            qsettings = IDE.ninja_settings()
            qsettings.clear()
            self._preferences.close()


preferences.Preferences.register_configuration(
    'GENERAL', GeneralConfiguration,
    translations.TR_PREFERENCES_GENERAL, preferences.SECTIONS['GENERAL'])
