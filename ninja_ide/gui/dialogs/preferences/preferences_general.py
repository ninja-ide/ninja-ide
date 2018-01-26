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

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QGroupBox,
    QSpinBox,
    QCheckBox,
    QFileDialog,
    QLineEdit,
    QGridLayout,
    QComboBox,
    QMessageBox,
    QStyle
)
from PyQt5.QtCore import (
    Qt,
    pyqtSignal
)
from ninja_ide.gui.dialogs.preferences import preferences
from ninja_ide import translations
from ninja_ide.tools import ui_tools
from ninja_ide.core import settings
from ninja_ide.gui.ide import IDE


class GeneralConfiguration(QWidget):
    """General configuration class"""

    def __init__(self, parent):
        super().__init__()
        self._preferences = parent
        vbox = QVBoxLayout(self)

        # Groups
        group_box_start = QGroupBox(translations.TR_PREFERENCES_GENERAL_START)
        group_box_close = QGroupBox(translations.TR_PREFERENCES_GENERAL_CLOSE)
        group_box_workspace = QGroupBox(
            translations.TR_PREFERENCES_GENERAL_WORKSPACE)
        group_box_reset = QGroupBox(translations.TR_PREFERENCES_GENERAL_RESET)
        group_box_swap = QGroupBox(
            translations.TR_PREFERENCES_GENERAL_SWAPFILE)
        group_box_modification = QGroupBox(
            translations.TR_PREFERENCES_GENERAL_EXTERNALLY_MOD)

        # Group start
        box_start = QVBoxLayout(group_box_start)
        self._check_last_session = QCheckBox(
            translations.TR_PREFERENCES_GENERAL_LOAD_LAST_SESSION)
        self._check_notify_updates = QCheckBox(
            translations.TR_PREFERENCES_GENERAL_NOTIFY_UPDATES)
        box_start.addWidget(self._check_last_session)
        box_start.addWidget(self._check_notify_updates)
        # Group close
        box_close = QVBoxLayout(group_box_close)
        self._check_confirm_exit = QCheckBox(
            translations.TR_PREFERENCES_GENERAL_CONFIRM_EXIT)
        box_close.addWidget(self._check_confirm_exit)
        # Workspace and Project
        grid_workspace = QGridLayout(group_box_workspace)
        self._text_workspace = QLineEdit()
        choose_workspace_action = self._text_workspace.addAction(
            self.style().standardIcon(self.style().SP_DirIcon),
            QLineEdit.TrailingPosition)
        clear_workspace_action = self._text_workspace.addAction(
            self.style().standardIcon(self.style().SP_LineEditClearButton),
            QLineEdit.TrailingPosition)
        self._text_workspace.setReadOnly(True)
        grid_workspace.addWidget(
            QLabel(translations.TR_PREFERENCES_GENERAL_WORKSPACE), 0, 0)
        grid_workspace.addWidget(self._text_workspace, 0, 1)

        # Resetting prefences
        box_reset = QVBoxLayout(group_box_reset)
        btn_reset = QPushButton(
            translations.TR_PREFERENCES_GENERAL_RESET_PREFERENCES)
        box_reset.addWidget(btn_reset)

        # Swap File
        box_swap = QGridLayout(group_box_swap)
        box_swap.addWidget(QLabel(
            translations.TR_PREFERENCES_GENERAL_SWAPFILE_LBL), 0, 0)
        self._combo_swap_file = QComboBox()
        self._combo_swap_file.addItems([
            translations.TR_PREFERENCES_GENERAL_SWAPFILE_DISABLE,
            translations.TR_PREFERENCES_GENERAL_SWAPFILE_ENABLE
        ])
        self._combo_swap_file.currentIndexChanged.connect(
            self._change_swap_widgets_state)
        box_swap.addWidget(self._combo_swap_file, 0, 1)
        box_swap.addWidget(QLabel(
            translations.TR_PREFERENCES_GENERAL_SWAPFILE_SYNC_INTERVAL), 1, 0)
        self._spin_swap = QSpinBox()
        self._spin_swap.setSuffix("s")
        self._spin_swap.setRange(5, 600)
        self._spin_swap.setSingleStep(5)
        box_swap.addWidget(self._spin_swap, 1, 1)

        # Externally modification
        box_mod = QHBoxLayout(group_box_modification)
        box_mod.addWidget(
            QLabel(translations.TR_PREFERENCES_GENERAL_EXTERNALLY_MOD_LABEL))
        self._combo_mod = QComboBox()
        self._combo_mod.addItems(["Ask", "Reload", "Ignore"])
        box_mod.addWidget(self._combo_mod)

        # Add groups to main layout
        vbox.addWidget(group_box_start)
        vbox.addWidget(group_box_close)
        vbox.addWidget(group_box_workspace)
        vbox.addWidget(group_box_swap)
        vbox.addWidget(group_box_modification)
        vbox.addWidget(group_box_reset, alignment=Qt.AlignLeft)
        vbox.addSpacerItem(
            QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding))

        # Settings
        qsettings = IDE.ninja_settings()
        qsettings.beginGroup("ide")
        self._check_last_session.setChecked(
            qsettings.value("loadFiles", defaultValue=True, type=bool))
        self._check_notify_updates.setChecked(
            qsettings.value("notifyUpdates", defaultValue=True, type=bool))
        qsettings.endGroup()
        self._combo_swap_file.setCurrentIndex(settings.SWAP_FILE)
        self._spin_swap.setValue(settings.SWAP_FILE_INTERVAL)
        self._text_workspace.setText(settings.WORKSPACE)
        self._combo_mod.setCurrentIndex(settings.RELOAD_FILE)
        self._check_confirm_exit.setChecked(settings.CONFIRM_EXIT)
        # Connections
        btn_reset.clicked.connect(self._reset_preferences)
        choose_workspace_action.triggered.connect(self._load_workspace)
        clear_workspace_action.triggered.connect(self._text_workspace.clear)
        self._preferences.savePreferences.connect(self.save)

    def _change_swap_widgets_state(self, index):
        if index == 0:
            self._spin_swap.setEnabled(False)
        else:
            self._spin_swap.setEnabled(True)

    def _reset_preferences(self):
        """Reset all preferences to default values"""

        result = QMessageBox.question(
            self,
            translations.TR_PREFERENCES_GENERAL_RESET_TITLE,
            translations.TR_PREFERENCES_GENERAL_RESET_BODY,
            buttons=QMessageBox.Yes | QMessageBox.No
        )
        if result == QMessageBox.Yes:
            qsettings = IDE.ninja_settings()
            qsettings.clear()
            self._preferences.close()

    def _load_workspace(self):
        """Ask the user for a Workspace path"""
        path = QFileDialog.getExistingDirectory(
            self, translations.TR_PREFERENCES_GENERAL_SELECT_WORKSPACE)
        self._text_workspace.setText(path)

    def save(self):
        """Save all preferences values"""

        qsettings = IDE.ninja_settings()
        qsettings.beginGroup("ide")

        settings.CONFIRM_EXIT = self._check_confirm_exit.isChecked()
        qsettings.setValue("confirmExit", settings.CONFIRM_EXIT)
        qsettings.setValue("loadFiles", self._check_last_session.isChecked())
        qsettings.setValue("notifyUpdates",
                           self._check_notify_updates.isChecked())
        settings.WORKSPACE = self._text_workspace.text()
        qsettings.setValue("workspace", settings.WORKSPACE)
        settings.RELOAD_FILE = self._combo_mod.currentIndex()
        qsettings.setValue("reloadSetting", settings.RELOAD_FILE)

        settings.SWAP_FILE = self._combo_swap_file.currentIndex()
        qsettings.setValue("swapFile", settings.SWAP_FILE)
        settings.SWAP_FILE_INTERVAL = self._spin_swap.value()
        qsettings.setValue("swapFileInterval", settings.SWAP_FILE_INTERVAL)

        qsettings.endGroup()


preferences.Preferences.register_configuration(
    'GENERAL',
    GeneralConfiguration,
    translations.TR_PREFERENCES_GENERAL,
    preferences.SECTIONS['GENERAL']
)

"""
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
    # General Configuration class

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
        # sk the user for a Color
        choosed_color = QColorDialog.getColor()
        if choosed_color.isValid():
            self._notification_choosed_color = choosed_color.name()

    def _load_workspace(self):
        # Ask the user for a Workspace path
        path = QFileDialog.getExistingDirectory(
            self, translations.TR_PREFERENCES_GENERAL_SELECT_WORKSPACE)
        self._txtWorkspace.setText(path)

    def _load_python_path(self):
        # Ask the user for a Python path
        path = QFileDialog.getOpenFileName(
            self, translations.TR_PREFERENCES_GENERAL_SELECT_PYTHON_PATH)
        if path:
            self._txtPythonPath.setText(path)

    def save(self):
        # Method to Save all preferences values
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
        # Method to Reset all Preferences to default values
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
"""
