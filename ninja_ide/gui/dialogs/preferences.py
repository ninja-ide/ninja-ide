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

import os
import copy
import getpass

from PyQt4.QtGui import QApplication
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QKeySequence
from PyQt4.QtGui import QSpacerItem
from PyQt4.QtGui import QColorDialog
from PyQt4.QtGui import QColor
from PyQt4.QtGui import QScrollArea
from PyQt4.QtGui import QFrame
from PyQt4.QtGui import QActionGroup
from PyQt4.QtGui import QStyle
from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QGroupBox
from PyQt4.QtGui import QCheckBox
from PyQt4.QtGui import QComboBox
from PyQt4.QtGui import QSpinBox
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QToolBar
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QGridLayout
from PyQt4.QtGui import QTabWidget
from PyQt4.QtGui import QSizePolicy
from PyQt4.QtGui import QListWidget
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QFileDialog
from PyQt4.QtGui import QFontDialog
from PyQt4.QtGui import QFont
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QSize
from PyQt4.QtCore import QSettings
from PyQt4.QtCore import SIGNAL

from ninja_ide import resources
from ninja_ide.gui import central_widget
from ninja_ide.gui import actions
from ninja_ide.gui.editor import editor
from ninja_ide.gui.misc import misc_container
from ninja_ide.gui.misc import shortcut_manager
from ninja_ide.gui.misc import plugin_preferences
from ninja_ide.gui.main_panel import main_container
from ninja_ide.gui.explorer import explorer_container
from ninja_ide.core import settings
from ninja_ide.core import file_manager
from ninja_ide.tools import ui_tools
from ninja_ide.tools import json_manager


class PreferencesWidget(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setWindowTitle(self.tr("NINJA-IDE - Preferences"))
        self.setMaximumSize(QSize(0, 0))

        self.overlay = ui_tools.Overlay(self)
        self.overlay.hide()

        #Tabs
        vbox = QVBoxLayout(self)
        self._tabs = QTabWidget()
        self._tabs.setTabPosition(QTabWidget.West)
        self._tabs.setMovable(False)
        self._general = GeneralTab(self)
        self._interface = InterfaceTab(self)
        self._editor = EditorTab()
        self._theme = ThemeTab()
        self._plugins = plugin_preferences.PluginPreferences()
        self._tabs.addTab(self._general, self.tr("General"))
        self._tabs.addTab(self._interface, self.tr("Interface"))
        self._tabs.addTab(self._editor, self.tr("Editor"))
        self._tabs.addTab(self._plugins, self.tr("Plugins"))
        self._tabs.addTab(self._theme, self.tr("Theme"))
        #Buttons (save-cancel)
        hbox = QHBoxLayout()
        self._btnSave = QPushButton(self.tr("Save"))
        self._btnCancel = QPushButton(self.tr("Cancel"))
        hbox = QHBoxLayout()
        hbox.addWidget(self._btnCancel)
        hbox.addWidget(self._btnSave)
        gridFooter = QGridLayout()
        gridFooter.addLayout(hbox, 0, 0, Qt.AlignRight)

        vbox.addWidget(self._tabs)
        vbox.addLayout(gridFooter)

        self.connect(self._btnSave, SIGNAL("clicked()"), self._save)
        self.connect(self._btnCancel, SIGNAL("clicked()"), self._cancel)

    def _cancel(self):
        editorWidget = main_container.MainContainer().get_actual_editor()
        if editorWidget is not None:
            editorWidget.restyle(editorWidget.lang)
        self.close()

    def _save(self):
        for i in range(self._tabs.count()):
            self._tabs.widget(i).save()
        self.close()

    def resizeEvent(self, event):
        self.overlay.resize(event.size())
        event.accept()


class GeneralTab(QWidget):

    def __init__(self, parent):
        QWidget.__init__(self)
        vbox = QVBoxLayout(self)

        self._tabs = QTabWidget()
        self._generalConfiguration = GeneralConfiguration(parent)
        self._generalExecution = GeneralExecution()
        self._shortcutConfiguration = shortcut_manager.ShortcutConfiguration()
        self._tabs.addTab(self._generalConfiguration, self.tr("General"))
        self._tabs.addTab(self._generalExecution, self.tr("Execution"))
        self._tabs.addTab(self._shortcutConfiguration, self.tr("Shortcuts"))

        vbox.addWidget(self._tabs)

    def save(self):
        for i in range(self._tabs.count()):
            self._tabs.widget(i).save()


class GeneralConfiguration(QWidget):

    def __init__(self, dialog):
        QWidget.__init__(self)
        self._dialog = dialog
        vbox = QVBoxLayout(self)

        groupBoxStart = QGroupBox(self.tr("On Start:"))
        groupBoxClose = QGroupBox(self.tr("On Close:"))
        groupBoxWorkspace = QGroupBox(self.tr("Workspace and Project:"))
        groupBoxReset = QGroupBox(self.tr("Reset NINJA-IDE Preferences:"))

        #Start
        vboxStart = QVBoxLayout(groupBoxStart)
        self._checkLastSession = QCheckBox(
            self.tr("Load files from last session"))
        self._checkActivatePlugins = QCheckBox(self.tr("Activate Plugins"))
        self._checkNotifyUpdates = QCheckBox(
            self.tr("Notify me of new updates."))
        self._checkShowStartPage = QCheckBox(self.tr("Show Start Page"))
        vboxStart.addWidget(self._checkLastSession)
        vboxStart.addWidget(self._checkActivatePlugins)
        vboxStart.addWidget(self._checkNotifyUpdates)
        vboxStart.addWidget(self._checkShowStartPage)
        #Close
        vboxClose = QVBoxLayout(groupBoxClose)
        self._checkConfirmExit = QCheckBox(self.tr("Confirm Exit."))
        vboxClose.addWidget(self._checkConfirmExit)
        #Workspace and Project
        gridWorkspace = QGridLayout(groupBoxWorkspace)
        self._txtWorkspace = QLineEdit()
        ui_tools.LineEditButton(self._txtWorkspace,
            self._txtWorkspace.clear,
            self.style().standardPixmap(self.style().SP_TrashIcon))
        self._txtWorkspace.setReadOnly(True)
        self._btnWorkspace = QPushButton(
            QIcon(resources.IMAGES['openFolder']), '')
        gridWorkspace.addWidget(
            QLabel(self.tr("Workspace")), 0, 0, Qt.AlignRight)
        gridWorkspace.addWidget(self._txtWorkspace, 0, 1)
        gridWorkspace.addWidget(self._btnWorkspace, 0, 2)
        self._txtExtensions = QLineEdit()
        gridWorkspace.addWidget(QLabel(
            self.tr("Supported Extensions:")), 1, 0, Qt.AlignRight)
        gridWorkspace.addWidget(self._txtExtensions, 1, 1)

        # Resetting preferences
        vboxReset = QVBoxLayout(groupBoxReset)
        self._btnReset = QPushButton(self.tr("Reset preferences"))
        vboxReset.addWidget(self._btnReset, alignment=Qt.AlignLeft)

        #Settings
        qsettings = QSettings(resources.SETTINGS_PATH, QSettings.IniFormat)
        qsettings.beginGroup('preferences')
        qsettings.beginGroup('general')
        self._checkLastSession.setChecked(
            qsettings.value('loadFiles', True,
                type=bool))
        self._checkActivatePlugins.setChecked(
            qsettings.value('activatePlugins', defaultValue=True,
                type=bool))
        self._checkNotifyUpdates.setChecked(settings.NOTIFY_UPDATES)
        self._checkShowStartPage.setChecked(settings.SHOW_START_PAGE)
        self._checkConfirmExit.setChecked(settings.CONFIRM_EXIT)
        self._txtWorkspace.setText(settings.WORKSPACE)
        extensions = ', '.join(settings.SUPPORTED_EXTENSIONS)
        self._txtExtensions.setText(extensions)
        qsettings.endGroup()
        qsettings.endGroup()

        vbox.addWidget(groupBoxStart)
        vbox.addWidget(groupBoxClose)
        vbox.addWidget(groupBoxWorkspace)
        vbox.addWidget(groupBoxReset)

        #Signals
        self.connect(self._btnWorkspace,
            SIGNAL("clicked()"), self._load_workspace)
        self.connect(self._btnReset,
            SIGNAL('clicked()'), self._reset_preferences)

    def _load_workspace(self):
        path = QFileDialog.getExistingDirectory(
            self, self.tr("Select Workspace"))
        self._txtWorkspace.setText(path)

    def _load_python_path(self):
        path = QFileDialog.getOpenFileName(self, self.tr("Select Python Path"))
        if path:
            self._txtPythonPath.setText(path)

    def save(self):
        qsettings = QSettings(resources.SETTINGS_PATH, QSettings.IniFormat)
        qsettings.beginGroup('preferences')
        qsettings.beginGroup('general')
        qsettings.setValue('loadFiles', self._checkLastSession.isChecked())
        qsettings.setValue('activatePlugins',
            self._checkActivatePlugins.isChecked())
        qsettings.setValue('notifyUpdates',
            self._checkNotifyUpdates.isChecked())
        qsettings.setValue('showStartPage',
            self._checkShowStartPage.isChecked())
        settings.NOTIFY_UPDATES = self._checkNotifyUpdates.isChecked()
        qsettings.setValue('confirmExit', self._checkConfirmExit.isChecked())
        settings.CONFIRM_EXIT = self._checkConfirmExit.isChecked()
        qsettings.setValue('workspace', self._txtWorkspace.text())
        settings.WORKSPACE = self._txtWorkspace.text()
        extensions = str(self._txtExtensions.text()).split(',')
        extensions = [e.strip() for e in extensions]
        qsettings.setValue('supportedExtensions', extensions)
        settings.SUPPORTED_EXTENSIONS = list(extensions)
        qsettings.endGroup()
        qsettings.endGroup()

    def _reset_preferences(self):
        result = QMessageBox.question(self, self.tr("Reset preferences?"),
            self.tr("Are you sure you want to reset your preferences?"),
            buttons=QMessageBox.Yes | QMessageBox.No)
        if result == QMessageBox.Yes:
            QSettings(resources.SETTINGS_PATH, QSettings.IniFormat).clear()
            self._dialog.close()


class GeneralExecution(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        vbox = QVBoxLayout(self)

        groupExecution = QGroupBox(self.tr("Workspace and Project:"))
        grid = QVBoxLayout(groupExecution)

        #Python Path
        hPath = QHBoxLayout()
        self._txtPythonPath = QLineEdit()
        self._btnPythonPath = QPushButton(QIcon(resources.IMAGES['open']), '')
        hPath.addWidget(QLabel(self.tr("Python Path:")))
        hPath.addWidget(self._txtPythonPath)
        hPath.addWidget(self._btnPythonPath)
        grid.addLayout(hPath)
        #Python Miscellaneous Execution options
        self.check_B = QCheckBox(self.tr(
            "-B: don't write .py[co] files on import"))
        self.check_d = QCheckBox(self.tr("-d: debug output from parser"))
        self.check_E = QCheckBox(self.tr(
            "-E: ignore PYTHON* environment variables (such as PYTHONPATH)"))
        self.check_O = QCheckBox(
            self.tr("-O: optimize generated bytecode slightly"))
        self.check_OO = QCheckBox(self.tr(
            "-OO: remove doc-strings in addition to the -O optimizations"))
        self.check_Q = QCheckBox(self.tr("-Q: division options:"))
        self.comboDivision = QComboBox()
        self.comboDivision.addItems(['old', 'new', 'warn', 'warnall'])
        self.check_s = QCheckBox(self.tr(
            "-s: don't add user site directory to sys.path"))
        self.check_S = QCheckBox(self.tr(
            "-S: don't imply 'import site' on initialization"))
        self.check_t = QCheckBox(self.tr(
            "-t: issue warnings about inconsistent tab usage"))
        self.check_tt = QCheckBox(self.tr(
            "-tt: issue errors about inconsistent tab usage"))
        self.check_v = QCheckBox(self.tr(
            "-v: verbose (trace import statements)"))
        self.check_W = QCheckBox(self.tr("-W: warning control:"))
        self.comboWarning = QComboBox()
        self.comboWarning.addItems(
            ['default', 'ignore', 'all', 'module', 'once', 'error'])
        self.check_x = QCheckBox(self.tr("-x: skip first line of source"))
        self.check_3 = QCheckBox(self.tr("-3: warn about Python 3.x "
            "incompatibilities that 2to3 cannot trivially fix"))
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
        self._txtPythonPath.setText(settings.PYTHON_PATH)
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
        path = QFileDialog.getOpenFileName(self, self.tr("Select Python Path"))
        if path:
            self._txtPythonPath.setText(path)

    def save(self):
        qsettings = QSettings(resources.SETTINGS_PATH, QSettings.IniFormat)
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


class InterfaceTab(QWidget):

    def __init__(self, parent):
        QWidget.__init__(self, parent)
        vbox = QVBoxLayout(self)
        self._parent = parent
        self.toolbar_settings = settings.TOOLBAR_ITEMS

        groupBoxExplorer = QGroupBox(self.tr("Explorer Panel:"))
        groupBoxGui = QGroupBox(self.tr("GUI Customization:"))
        groupBoxToolbar = QGroupBox(self.tr("Tool Bar Customization:"))
        groupBoxLang = QGroupBox(self.tr("Language:"))

        #Explorer
        vboxExplorer = QVBoxLayout(groupBoxExplorer)
        self._checkProjectExplorer = QCheckBox(
            self.tr("Show Project Explorer."))
        self._checkSymbols = QCheckBox(self.tr("Show Symbols List."))
        self._checkWebInspetor = QCheckBox(self.tr("Show Web Inspector."))
        self._checkFileErrors = QCheckBox(self.tr("Show File Errors."))
        self._checkMigrationTips = QCheckBox(self.tr("Show Migration Tips."))
        self._checkStatusBarNotifications = QCheckBox(
            self.tr("Show Status Bar Notifications."))
        vboxExplorer.addWidget(self._checkProjectExplorer)
        vboxExplorer.addWidget(self._checkSymbols)
        vboxExplorer.addWidget(self._checkWebInspetor)
        vboxExplorer.addWidget(self._checkFileErrors)
        vboxExplorer.addWidget(self._checkMigrationTips)
        vboxExplorer.addWidget(self._checkStatusBarNotifications)
        #GUI
        self._btnCentralRotate = QPushButton(
            QIcon(resources.IMAGES['splitCPosition']), '')
        self._btnCentralRotate.setIconSize(QSize(64, 64))
        self._btnCentralRotate.setCheckable(True)
        self._btnPanelsRotate = QPushButton(
            QIcon(resources.IMAGES['splitMPosition']), '')
        self._btnPanelsRotate.setIconSize(QSize(64, 64))
        self._btnPanelsRotate.setCheckable(True)
        self._btnCentralOrientation = QPushButton(
            QIcon(resources.IMAGES['splitCRotate']), '')
        self._btnCentralOrientation.setIconSize(QSize(64, 64))
        self._btnCentralOrientation.setCheckable(True)
        gridGuiConfig = QGridLayout(groupBoxGui)
        gridGuiConfig.addWidget(self._btnCentralRotate, 0, 0)
        gridGuiConfig.addWidget(self._btnPanelsRotate, 0, 1)
        gridGuiConfig.addWidget(self._btnCentralOrientation, 0, 2)
        gridGuiConfig.addWidget(QLabel(
            self.tr("Rotate Central")), 1, 0, Qt.AlignCenter)
        gridGuiConfig.addWidget(QLabel(
            self.tr("Rotate Lateral")), 1, 1, Qt.AlignCenter)
        gridGuiConfig.addWidget(QLabel(
            self.tr("Central Orientation")), 1, 2, Qt.AlignCenter)
        #GUI - Toolbar
        vbox_toolbar = QVBoxLayout(groupBoxToolbar)
        hbox_select_items = QHBoxLayout()
        label_toolbar = QLabel(self.tr("Toolbar Items:"))
        label_toolbar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        hbox_select_items.addWidget(label_toolbar)
        self._comboToolbarItems = QComboBox()
        self._load_combo_data(self._comboToolbarItems)
        self._btnItemAdd = QPushButton(
            QIcon(resources.IMAGES['add']), '')
        self._btnItemAdd.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._btnItemRemove = QPushButton(
            QIcon(resources.IMAGES['delete']), '')
        self._btnDefaultItems = QPushButton(self.tr("Default Items"))
        self._btnDefaultItems.setSizePolicy(QSizePolicy.Fixed,
            QSizePolicy.Fixed)
        self._btnItemRemove.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        hbox_select_items.addWidget(self._comboToolbarItems)
        hbox_select_items.addWidget(self._btnItemAdd)
        hbox_select_items.addWidget(self._btnItemRemove)
        hbox_select_items.addWidget(self._btnDefaultItems)
        vbox_toolbar.addLayout(hbox_select_items)
        self._toolbar_items = QToolBar()
        self._toolbar_items.setObjectName("custom")
        self._toolbar_items.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self._load_toolbar()
        vbox_toolbar.addWidget(self._toolbar_items)
        vbox_toolbar.addWidget(QLabel(
            self.tr("The New Item will be inserted after the item selected.")))
        #Language
        vboxLanguage = QVBoxLayout(groupBoxLang)
        vboxLanguage.addWidget(QLabel(self.tr("Select Language:")))
        self._comboLang = QComboBox()
        self._comboLang.setEnabled(False)
        vboxLanguage.addWidget(self._comboLang)
        vboxLanguage.addWidget(QLabel(self.tr('Requires restart...')))

        #Load Languages
        self._load_langs()

        #Settings
        self._checkProjectExplorer.setChecked(
            settings.SHOW_PROJECT_EXPLORER)
        self._checkSymbols.setChecked(settings.SHOW_SYMBOLS_LIST)
        self._checkWebInspetor.setChecked(settings.SHOW_WEB_INSPECTOR)
        self._checkFileErrors.setChecked(settings.SHOW_ERRORS_LIST)
        self._checkMigrationTips.setChecked(settings.SHOW_MIGRATION_LIST)
        self._checkStatusBarNotifications.setChecked(
            settings.SHOW_STATUS_NOTIFICATIONS)
        #ui layout
        self._btnCentralRotate.setChecked(bin(settings.UI_LAYOUT)[-1] == '1')
        self._btnPanelsRotate.setChecked(bin(
            settings.UI_LAYOUT >> 1)[-1] == '1')
        self._btnCentralOrientation.setChecked(
            bin(settings.UI_LAYOUT >> 2)[-1] == '1')

        vbox.addWidget(groupBoxExplorer)
        vbox.addWidget(groupBoxGui)
        vbox.addWidget(groupBoxToolbar)
        vbox.addWidget(groupBoxLang)

        #Signals
        self.connect(self._btnCentralRotate, SIGNAL('clicked()'),
            central_widget.CentralWidget().splitter_central_rotate)
        self.connect(self._btnPanelsRotate, SIGNAL('clicked()'),
            central_widget.CentralWidget().splitter_misc_rotate)
        self.connect(self._btnCentralOrientation, SIGNAL('clicked()'),
            central_widget.CentralWidget().splitter_central_orientation)
        self.connect(self._btnItemAdd, SIGNAL("clicked()"),
            self.toolbar_item_added)
        self.connect(self._btnItemRemove, SIGNAL("clicked()"),
            self.toolbar_item_removed)
        self.connect(self._btnDefaultItems, SIGNAL("clicked()"),
            self.toolbar_items_default)

    def toolbar_item_added(self):
        data = self._comboToolbarItems.itemData(
            self._comboToolbarItems.currentIndex())
        if data not in self.toolbar_settings or data == 'separator':
            selected = self.actionGroup.checkedAction()
            if selected is None:
                self.toolbar_settings.append(data)
            else:
                dataAction = selected.data()
                self.toolbar_settings.insert(
                    self.toolbar_settings.index(dataAction) + 1, data)
            self._load_toolbar()

    def toolbar_item_removed(self):
        data = self._comboToolbarItems.itemData(
            self._comboToolbarItems.currentIndex())
        if data in self.toolbar_settings and data != 'separator':
            self.toolbar_settings.pop(self.toolbar_settings.index(data))
            self._load_toolbar()
        elif data == 'separator':
            self.toolbar_settings.reverse()
            self.toolbar_settings.pop(self.toolbar_settings.index(data))
            self.toolbar_settings.reverse()
            self._load_toolbar()

    def toolbar_items_default(self):
        self.toolbar_settings = settings.TOOLBAR_ITEMS_DEFAULT
        self._load_toolbar()

    def _load_combo_data(self, combo):
        self.toolbar_items = {
            'separator': [QIcon(resources.IMAGES['separator']),
                'Add Separtor'],
            'new-file': [QIcon(resources.IMAGES['new']), self.tr('New File')],
            'new-project': [QIcon(resources.IMAGES['newProj']),
                self.tr('New Project')],
            'save-file': [QIcon(resources.IMAGES['save']),
                self.tr('Save File')],
            'save-as': [QIcon(resources.IMAGES['saveAs']), self.tr('Save As')],
            'save-all': [QIcon(resources.IMAGES['saveAll']),
                self.tr('Save All')],
            'save-project': [QIcon(resources.IMAGES['saveAll']),
                self.tr('Save Project')],
            'reload-file': [QIcon(resources.IMAGES['reload-file']),
                self.tr('Reload File')],
            'open-file': [QIcon(resources.IMAGES['open']),
                self.tr('Open File')],
            'open-project': [QIcon(resources.IMAGES['openProj']),
                self.tr('Open Project')],
            'activate-profile': [QIcon(resources.IMAGES['activate-profile']),
                self.tr('Activate Profile')],
            'deactivate-profile':
                [QIcon(resources.IMAGES['deactivate-profile']),
                self.tr('Deactivate Profile')],
            'print-file': [QIcon(resources.IMAGES['print']),
                self.tr('Print File')],
            'close-file':
                [self.style().standardIcon(QStyle.SP_DialogCloseButton),
                self.tr('Close File')],
            'close-projects':
                [self.style().standardIcon(QStyle.SP_DialogCloseButton),
                self.tr('Close Projects')],
            'undo': [QIcon(resources.IMAGES['undo']), self.tr('Undo')],
            'redo': [QIcon(resources.IMAGES['redo']), self.tr('Redo')],
            'cut': [QIcon(resources.IMAGES['cut']), self.tr('Cut')],
            'copy': [QIcon(resources.IMAGES['copy']), self.tr('Copy')],
            'paste': [QIcon(resources.IMAGES['paste']), self.tr('Paste')],
            'find': [QIcon(resources.IMAGES['find']), self.tr('Find')],
            'find-replace': [QIcon(resources.IMAGES['findReplace']),
                self.tr('Find/Replace')],
            'find-files': [QIcon(resources.IMAGES['find']),
                self.tr('Find In files')],
            'code-locator': [QIcon(resources.IMAGES['locator']),
                self.tr('Code Locator')],
            'splith': [QIcon(resources.IMAGES['splitH']),
                self.tr('Split Horizontally')],
            'splitv': [QIcon(resources.IMAGES['splitV']),
                self.tr('Split Vertically')],
            'follow-mode': [QIcon(resources.IMAGES['follow']),
                self.tr('Follow Mode')],
            'zoom-in': [QIcon(resources.IMAGES['zoom-in']), self.tr('Zoom In')],
            'zoom-out': [QIcon(resources.IMAGES['zoom-out']),
                self.tr('Zoom Out')],
            'indent-more': [QIcon(resources.IMAGES['indent-more']),
                self.tr('Indent More')],
            'indent-less': [QIcon(resources.IMAGES['indent-less']),
                self.tr('Indent Less')],
            'comment': [QIcon(resources.IMAGES['comment-code']),
                self.tr('Comment')],
            'uncomment': [QIcon(resources.IMAGES['uncomment-code']),
                self.tr('Uncomment')],
            'go-to-definition': [QIcon(resources.IMAGES['go-to-definition']),
                self.tr('Go To Definition')],
            'insert-import': [QIcon(resources.IMAGES['insert-import']),
                self.tr('Insert Import')],
            'run-project': [QIcon(resources.IMAGES['play']), 'Run Project'],
            'run-file': [QIcon(resources.IMAGES['file-run']), 'Run File'],
            'stop': [QIcon(resources.IMAGES['stop']), 'Stop'],
            'preview-web': [QIcon(resources.IMAGES['preview-web']),
                self.tr('Preview Web')]}
        for item in self.toolbar_items:
            combo.addItem(self.toolbar_items[item][0],
                self.toolbar_items[item][1], item)
        combo.model().sort(0)

    def _load_toolbar(self):
        self._toolbar_items.clear()
        self.actionGroup = QActionGroup(self)
        self.actionGroup.setExclusive(True)
        for item in self.toolbar_settings:
            if item == 'separator':
                self._toolbar_items.addSeparator()
            else:
                action = self._toolbar_items.addAction(
                    self.toolbar_items[item][0], self.toolbar_items[item][1])
                action.setData(item)
                action.setCheckable(True)
                self.actionGroup.addAction(action)

    def _load_langs(self):
        langs = file_manager.get_files_from_folder(
            resources.LANGS, '.qm')
        langs_download = file_manager.get_files_from_folder(
            resources.LANGS_DOWNLOAD, '.qm')
        self._languages = ['English'] + \
            [file_manager.get_module_name(lang) for lang in langs] + \
            [file_manager.get_module_name(lang) for lang in langs_download]
        self._comboLang.addItems(self._languages)
        if(self._comboLang.count() > 1):
            self._comboLang.setEnabled(True)
        if settings.LANGUAGE:
            index = self._comboLang.findText(settings.LANGUAGE)
        else:
            index = 0
        self._comboLang.setCurrentIndex(index)

    def save(self):
        settings.TOOLBAR_ITEMS = self.toolbar_settings
        lang = self._comboLang.currentText()
        qsettings = QSettings(resources.SETTINGS_PATH, QSettings.IniFormat)
        qsettings.beginGroup('preferences')
        qsettings.beginGroup('interface')
        previous_state = (settings.SHOW_PROJECT_EXPLORER or
            settings.SHOW_SYMBOLS_LIST or settings.SHOW_MIGRATION_LIST or
            settings.SHOW_ERRORS_LIST or settings.SHOW_WEB_INSPECTOR)
        qsettings.setValue('showProjectExplorer',
            self._checkProjectExplorer.isChecked())
        settings.SHOW_PROJECT_EXPLORER = self._checkProjectExplorer.isChecked()
        if settings.SHOW_PROJECT_EXPLORER:
            explorer_container.ExplorerContainer().add_tab_projects()
        else:
            explorer_container.ExplorerContainer().remove_tab_projects()
        qsettings.setValue('showSymbolsList', self._checkSymbols.isChecked())
        settings.SHOW_SYMBOLS_LIST = self._checkSymbols.isChecked()
        if settings.SHOW_SYMBOLS_LIST:
            explorer_container.ExplorerContainer().add_tab_symbols()
        else:
            explorer_container.ExplorerContainer().remove_tab_symbols()
        qsettings.setValue('showWebInspector',
            self._checkWebInspetor.isChecked())
        settings.SHOW_WEB_INSPECTOR = self._checkWebInspetor.isChecked()
        if settings.SHOW_WEB_INSPECTOR:
            explorer_container.ExplorerContainer().add_tab_inspector()
        else:
            explorer_container.ExplorerContainer().remove_tab_inspector()
        qsettings.setValue('showErrorsList',
            self._checkFileErrors.isChecked())
        settings.SHOW_ERRORS_LIST = self._checkFileErrors.isChecked()
        if settings.SHOW_ERRORS_LIST:
            explorer_container.ExplorerContainer().add_tab_errors()
        else:
            explorer_container.ExplorerContainer().remove_tab_errors()
        qsettings.setValue('showMigrationList',
            self._checkMigrationTips.isChecked())
        settings.SHOW_MIGRATION_LIST = self._checkMigrationTips.isChecked()
        if settings.SHOW_MIGRATION_LIST:
            explorer_container.ExplorerContainer().add_tab_migration()
        else:
            explorer_container.ExplorerContainer().remove_tab_migration()
        qsettings.setValue('showStatusNotifications',
            self._checkStatusBarNotifications.isChecked())
        settings.SHOW_STATUS_NOTIFICATIONS = \
            self._checkStatusBarNotifications.isChecked()
        #ui layout
        uiLayout = 1 if self._btnCentralRotate.isChecked() else 0
        uiLayout += 2 if self._btnPanelsRotate.isChecked() else 0
        uiLayout += 4 if self._btnCentralOrientation.isChecked() else 0
        qsettings.setValue('uiLayout', uiLayout)
        qsettings.setValue('toolbar', settings.TOOLBAR_ITEMS)
        qsettings.setValue('language', lang)
        lang = lang + '.qm'
        settings.LANGUAGE = os.path.join(resources.LANGS, lang)
        qsettings.endGroup()
        qsettings.endGroup()
        actions.Actions().reload_toolbar()
        end_state = (settings.SHOW_PROJECT_EXPLORER or
            settings.SHOW_SYMBOLS_LIST or settings.SHOW_MIGRATION_LIST or
            settings.SHOW_ERRORS_LIST or settings.SHOW_WEB_INSPECTOR)
        if previous_state != end_state:
            actions.Actions().view_explorer_visibility()


class EditorTab(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        vbox = QVBoxLayout(self)

        self._tabs = QTabWidget()
        self._editorGeneral = EditorGeneral()
        self._editorConfiguration = EditorConfiguration()
        self._editorCompletion = EditorCompletion()
        self._editorSchemeDesigner = EditorSchemeDesigner(self)
        self._tabs.addTab(self._editorGeneral, self.tr("General"))
        self._tabs.addTab(self._editorConfiguration, self.tr("Configuration"))
        self._tabs.addTab(self._editorCompletion, self.tr("Completion"))
        self._tabs.addTab(self._editorSchemeDesigner,
            self.tr("Editor Scheme Designer"))

        vbox.addWidget(self._tabs)

    def save(self):
        for i in range(self._tabs.count()):
            self._tabs.widget(i).save()


class EditorGeneral(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        vbox = QVBoxLayout(self)
        self.original_style = copy.copy(resources.CUSTOM_SCHEME)
        self.current_scheme = 'default'

        groupBoxMini = QGroupBox(self.tr("MiniMap:"))
        groupBoxTypo = QGroupBox(self.tr("Typography:"))
        groupBoxScheme = QGroupBox(self.tr("Scheme Color:"))

        #Settings
        qsettings = QSettings(resources.SETTINGS_PATH, QSettings.IniFormat)
        qsettings.beginGroup('preferences')
        qsettings.beginGroup('editor')
        #Minimap
        formMini = QGridLayout(groupBoxMini)
        self._checkShowMinimap = QCheckBox()
        self._checkShowMinimap.setChecked(settings.SHOW_MINIMAP)
        self._spinMaxOpacity = QSpinBox()
        self._spinMaxOpacity.setMaximum(100)
        self._spinMaxOpacity.setMinimum(0)
        self._spinMaxOpacity.setValue(settings.MINIMAP_MAX_OPACITY * 100)
        self._spinMinOpacity = QSpinBox()
        self._spinMinOpacity.setMaximum(100)
        self._spinMinOpacity.setMinimum(0)
        self._spinMinOpacity.setValue(settings.MINIMAP_MIN_OPACITY * 100)
        self._spinSize = QSpinBox()
        self._spinSize.setMaximum(100)
        self._spinSize.setMinimum(0)
        self._spinSize.setValue(settings.SIZE_PROPORTION * 100)
        formMini.addWidget(QLabel(
            self.tr("Enable/Disable MiniMap (Requires restart):\n"
            "(opacity not supported in MAC OS)")), 0, 0,
            Qt.AlignRight)
        formMini.addWidget(QLabel(self.tr("Max Opacity:")), 1, 0,
            Qt.AlignRight)
        formMini.addWidget(QLabel(self.tr("Min Opacity:")), 2, 0,
            Qt.AlignRight)
        formMini.addWidget(QLabel(
            self.tr("Size Area relative to the Editor:")), 3, 0, Qt.AlignRight)
        formMini.addWidget(self._checkShowMinimap, 0, 1)
        formMini.addWidget(self._spinMaxOpacity, 1, 1)
        formMini.addWidget(self._spinMinOpacity, 2, 1)
        formMini.addWidget(self._spinSize, 3, 1)
        #Typo
        gridTypo = QGridLayout(groupBoxTypo)
        self._btnEditorFont = QPushButton(
            ', '.join([settings.FONT_FAMILY, str(settings.FONT_SIZE)]))
        gridTypo.addWidget(QLabel(
            self.tr("Editor Font:")), 0, 0, Qt.AlignRight)
        gridTypo.addWidget(self._btnEditorFont, 0, 1)
        #Scheme
        hbox = QHBoxLayout(groupBoxScheme)
        self._listScheme = QListWidget()
        self._listScheme.addItem('default')
        self._schemes = json_manager.load_editor_skins()
        for item in self._schemes:
            self._listScheme.addItem(item)
        items = self._listScheme.findItems(
            qsettings.value('scheme', defaultValue='',
                type='QString'), Qt.MatchExactly)
        if items:
            self._listScheme.setCurrentItem(items[0])
        else:
            self._listScheme.setCurrentRow(0)
        hbox.addWidget(self._listScheme)
        qsettings.endGroup()
        qsettings.endGroup()

        vbox.addWidget(groupBoxMini)
        vbox.addWidget(groupBoxTypo)
        vbox.addWidget(groupBoxScheme)

        #Signals
        self.connect(self._btnEditorFont,
            SIGNAL("clicked()"), self._load_editor_font)
        self.connect(self._listScheme, SIGNAL("itemSelectionChanged()"),
            self._preview_style)

    def showEvent(self, event):
        super(EditorGeneral, self).showEvent(event)
        self.thread_callback = ui_tools.ThreadExecution(self._get_editor_skins)
        self.connect(self.thread_callback, SIGNAL("finished()"),
            self._show_editor_skins)
        self.thread_callback.start()

    def _get_editor_skins(self):
        qsettings = QSettings(resources.SETTINGS_PATH, QSettings.IniFormat)
        qsettings.beginGroup('preferences')
        qsettings.beginGroup('editor')
        self._schemes = json_manager.load_editor_skins()
        self._selected_scheme = qsettings.value('scheme', defaultValue='',
            type='QString')
        qsettings.endGroup()
        qsettings.endGroup()

    def _show_editor_skins(self):
        self._listScheme.clear()
        self._listScheme.addItem('default')
        for item in self._schemes:
            self._listScheme.addItem(item)
        items = self._listScheme.findItems(
            self._selected_scheme, Qt.MatchExactly)
        if items:
            self._listScheme.setCurrentItem(items[0])
        else:
            self._listScheme.setCurrentRow(0)
        self.thread_callback.wait()

    def hideEvent(self, event):
        super(EditorGeneral, self).hideEvent(event)
        resources.CUSTOM_SCHEME = self.original_style
        editorWidget = main_container.MainContainer().get_actual_editor()
        if editorWidget is not None:
            editorWidget.restyle(editorWidget.lang)
            editorWidget._sidebarWidget.repaint()

    def _preview_style(self):
        scheme = self._listScheme.currentItem().text()
        if scheme == self.current_scheme:
            return
        editorWidget = main_container.MainContainer().get_actual_editor()
        if editorWidget is not None:
            resources.CUSTOM_SCHEME = self._schemes.get(scheme,
                resources.COLOR_SCHEME)
            editorWidget.restyle(editorWidget.lang)
            editorWidget._sidebarWidget.repaint()
        self.current_scheme = scheme

    def _load_editor_font(self):
        try:
            font = self._load_font(
                self._get_font_from_string(self._btnEditorFont.text()), self)
            self._btnEditorFont.setText(font)
        except:
            QMessageBox.warning(self,
                self.tr("Invalid Font"),
                self.tr("This font can not be used in the Editor."))

    def _get_font_from_string(self, font):
        if not font:
            font = QFont(settings.FONT_FAMILY, settings.FONT_SIZE)
        else:
            listFont = font.split(',')
            font = QFont(listFont[0].strip(), int(listFont[1].strip()))
        return font

    def _load_font(self, initialFont, parent=0):
        font, ok = QFontDialog.getFont(initialFont, parent)
        if ok:
            newFont = font.toString().split(',')
        else:
            newFont = initialFont.toString().split(',')
        return newFont[0] + ', ' + newFont[1]

    def save(self):
        qsettings = QSettings(resources.SETTINGS_PATH, QSettings.IniFormat)
        qsettings.beginGroup('preferences')
        qsettings.beginGroup('editor')
        settings.SHOW_MINIMAP = self._checkShowMinimap.isChecked()
        settings.MINIMAP_MAX_OPACITY = self._spinMaxOpacity.value() / 100.0
        settings.MINIMAP_MIN_OPACITY = self._spinMinOpacity.value() / 100.0
        settings.SIZE_PROPORTION = self._spinSize.value() / 100.0
        qsettings.setValue('minimapShow', settings.SHOW_MINIMAP)
        qsettings.setValue('minimapMaxOpacity', settings.MINIMAP_MAX_OPACITY)
        qsettings.setValue('minimapMinOpacity', settings.MINIMAP_MIN_OPACITY)
        qsettings.setValue('minimapSizeProportion', settings.SIZE_PROPORTION)
        fontText = self._btnEditorFont.text().replace(' ', '')
        settings.FONT_FAMILY = fontText.split(',')[0]
        settings.FONT_SIZE = int(fontText.split(',')[1])
        qsettings.setValue('fontFamily', settings.FONT_FAMILY)
        qsettings.setValue('fontSize', settings.FONT_SIZE)
        editorWidget = main_container.MainContainer().get_actual_editor()
        scheme = self._listScheme.currentItem().text()
        self.original_style = resources.CUSTOM_SCHEME
        if editorWidget is not None:
            editorWidget.set_font(settings.FONT_FAMILY, settings.FONT_SIZE)
        qsettings.setValue('scheme', scheme)
        resources.CUSTOM_SCHEME = self._schemes.get(scheme,
            resources.COLOR_SCHEME)
        qsettings.endGroup()
        qsettings.endGroup()
        main_container.MainContainer().apply_editor_theme(settings.FONT_FAMILY,
            settings.FONT_SIZE)
        misc = misc_container.MiscContainer()
        misc._console.restyle()
        misc._runWidget.set_font(settings.FONT_FAMILY, settings.FONT_SIZE)


class EditorConfiguration(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        vbox = QVBoxLayout(self)

        #Indentation
        groupBoxFeatures = QGroupBox(self.tr("Features:"))
        formFeatures = QGridLayout(groupBoxFeatures)
        formFeatures.addWidget(QLabel(
            self.tr("Indentation Length:")), 1, 0, Qt.AlignRight)
        self._spin = QSpinBox()
        self._spin.setAlignment(Qt.AlignRight)
        self._spin.setMinimum(1)
        self._spin.setValue(settings.INDENT)
        formFeatures.addWidget(self._spin, 1, 1, alignment=Qt.AlignTop)
        self._checkUseTabs = QCheckBox(
            self.tr("Use Tabs."))
        self._checkUseTabs.setChecked(settings.USE_TABS)
        self.connect(self._checkUseTabs, SIGNAL("stateChanged(int)"),
            self._change_tab_spaces)
        formFeatures.addWidget(self._checkUseTabs, 1, 2, alignment=Qt.AlignTop)
        if settings.USE_TABS:
            self._spin.setSuffix(self.tr("  (tab size)"))
        else:
            self._spin.setSuffix(self.tr("  (spaces)"))
        #Margin Line
        formFeatures.addWidget(QLabel(self.tr("Margin Line:")), 2, 0,
            Qt.AlignRight)
        self._spinMargin = QSpinBox()
        self._spinMargin.setMaximum(200)
        self._spinMargin.setValue(settings.MARGIN_LINE)
        formFeatures.addWidget(self._spinMargin, 2, 1, alignment=Qt.AlignTop)
        self._checkShowMargin = QCheckBox(self.tr("Show Margin Line"))
        self._checkShowMargin.setChecked(settings.SHOW_MARGIN_LINE)
        formFeatures.addWidget(self._checkShowMargin, 2, 2,
            alignment=Qt.AlignTop)
        #End of line
        self._checkEndOfLine = QCheckBox(self.tr("Use Platform End of Line"))
        self._checkEndOfLine.setChecked(settings.USE_PLATFORM_END_OF_LINE)
        formFeatures.addWidget(self._checkEndOfLine, 3, 1,
            alignment=Qt.AlignTop)
        #Find Errors
        self._checkHighlightLine = QCheckBox(
            self.tr("Check: Highlight errors using Underline\n"
                "Uncheck: Highlight errors using Background"))
        self._checkHighlightLine.setChecked(settings.UNDERLINE_NOT_BACKGROUND)
        formFeatures.addWidget(self._checkHighlightLine, 4, 1, 1, 2,
            alignment=Qt.AlignTop)
        self._checkErrors = QCheckBox(self.tr("Find and Show Errors."))
        self._checkErrors.setChecked(settings.FIND_ERRORS)
        formFeatures.addWidget(self._checkErrors, 5, 1, 1, 2,
            alignment=Qt.AlignTop)
        self.connect(self._checkErrors, SIGNAL("stateChanged(int)"),
            self._disable_show_errors)
        self._showErrorsOnLine = QCheckBox(
            self.tr("Show Tool tip information about the errors."))
        self._showErrorsOnLine.setChecked(settings.ERRORS_HIGHLIGHT_LINE)
        self.connect(self._showErrorsOnLine, SIGNAL("stateChanged(int)"),
            self._enable_errors_inline)
        formFeatures.addWidget(self._showErrorsOnLine, 6, 2, 1, 1, Qt.AlignTop)
        #Find Check Style
        self._checkStyle = QCheckBox(
            self.tr("Find and Show Check Style errors."))
        self._checkStyle.setChecked(settings.CHECK_STYLE)
        formFeatures.addWidget(self._checkStyle, 7, 1, 1, 2,
            alignment=Qt.AlignTop)
        self.connect(self._checkStyle, SIGNAL("stateChanged(int)"),
            self._disable_check_style)
        self._checkStyleOnLine = QCheckBox(
            self.tr("Show Tool tip information about the PEP8 errors."))
        self._checkStyleOnLine.setChecked(settings.CHECK_HIGHLIGHT_LINE)
        self.connect(self._checkStyleOnLine, SIGNAL("stateChanged(int)"),
            self._enable_check_inline)
        formFeatures.addWidget(self._checkStyleOnLine, 8, 2, 1, 1, Qt.AlignTop)
        # Python3 Migration
        self._showMigrationTips = QCheckBox(
            self.tr("Show Python3 Migration Tips."))
        self._showMigrationTips.setChecked(settings.SHOW_MIGRATION_TIPS)
        formFeatures.addWidget(self._showMigrationTips, 9, 1, 1, 2,
            Qt.AlignTop)
        #Center On Scroll
        self._checkCenterScroll = QCheckBox(
            self.tr("Center on Scroll."))
        self._checkCenterScroll.setChecked(settings.CENTER_ON_SCROLL)
        formFeatures.addWidget(self._checkCenterScroll, 10, 1, 1, 2,
            alignment=Qt.AlignTop)
        #Remove Trailing Spaces add Last empty line automatically
        self._checkTrailing = QCheckBox(self.tr(
            "Remove Trailing Spaces and\nadd Last Line automatically."))
        self._checkTrailing.setChecked(settings.REMOVE_TRAILING_SPACES)
        formFeatures.addWidget(self._checkTrailing, 11, 1, 1, 2,
            alignment=Qt.AlignTop)
        #Show Tabs and Spaces
        self._checkShowSpaces = QCheckBox(self.tr("Show Tabs and Spaces."))
        self._checkShowSpaces.setChecked(settings.SHOW_TABS_AND_SPACES)
        formFeatures.addWidget(self._checkShowSpaces, 12, 1, 1, 2,
            alignment=Qt.AlignTop)
        self._allowWordWrap = QCheckBox(self.tr("Allow Word Wrap."))
        self._allowWordWrap.setChecked(settings.ALLOW_WORD_WRAP)
        formFeatures.addWidget(self._allowWordWrap, 13, 1, 1, 2,
            alignment=Qt.AlignTop)
        self._checkForDocstrings = QCheckBox(
            self.tr("Check for Docstrings in Classes and Functions."))
        self._checkForDocstrings.setChecked(settings.CHECK_FOR_DOCSTRINGS)
        formFeatures.addWidget(self._checkForDocstrings, 14, 1, 1, 2,
            alignment=Qt.AlignTop)

        vbox.addWidget(groupBoxFeatures)
        vbox.addItem(QSpacerItem(0, 10, QSizePolicy.Expanding,
            QSizePolicy.Expanding))

    def _enable_check_inline(self, val):
        if val == Qt.Checked:
            self._checkStyle.setChecked(True)

    def _enable_errors_inline(self, val):
        if val == Qt.Checked:
            self._checkErrors.setChecked(True)

    def _disable_check_style(self, val):
        if val == Qt.Unchecked:
            self._checkStyleOnLine.setChecked(False)

    def _disable_show_errors(self, val):
        if val == Qt.Unchecked:
            self._showErrorsOnLine.setChecked(False)

    def _change_tab_spaces(self, val):
        if val == Qt.Unchecked:
            self._spin.setSuffix(self.tr("  (spaces)"))
        else:
            self._spin.setSuffix(self.tr("  (tab size)"))

    def save(self):
        qsettings = QSettings(resources.SETTINGS_PATH, QSettings.IniFormat)
        qsettings.beginGroup('preferences')
        qsettings.beginGroup('editor')
        qsettings.setValue('indent', self._spin.value())
        settings.INDENT = self._spin.value()
        endOfLine = self._checkEndOfLine.isChecked()
        qsettings.setValue('platformEndOfLine', endOfLine)
        settings.USE_PLATFORM_END_OF_LINE = endOfLine
        margin_line = self._spinMargin.value()
        qsettings.setValue('marginLine', margin_line)
        settings.MARGIN_LINE = margin_line
        settings.pep8mod_update_margin_line_length(margin_line)
        qsettings.setValue('showMarginLine', self._checkShowMargin.isChecked())
        settings.SHOW_MARGIN_LINE = self._checkShowMargin.isChecked()
        settings.UNDERLINE_NOT_BACKGROUND = \
            self._checkHighlightLine.isChecked()
        qsettings.setValue('errorsUnderlineBackground',
            settings.UNDERLINE_NOT_BACKGROUND)
        qsettings.setValue('errors', self._checkErrors.isChecked())
        settings.FIND_ERRORS = self._checkErrors.isChecked()
        qsettings.setValue('errorsInLine', self._showErrorsOnLine.isChecked())
        settings.ERRORS_HIGHLIGHT_LINE = self._showErrorsOnLine.isChecked()
        qsettings.setValue('checkStyle', self._checkStyle.isChecked())
        settings.CHECK_STYLE = self._checkStyle.isChecked()
        qsettings.setValue('showMigrationTips',
            self._showMigrationTips.isChecked())
        settings.SHOW_MIGRATION_TIPS = self._showMigrationTips.isChecked()
        qsettings.setValue('checkStyleInline',
            self._checkStyleOnLine.isChecked())
        settings.CHECK_HIGHLIGHT_LINE = self._checkStyleOnLine.isChecked()
        qsettings.setValue('centerOnScroll',
            self._checkCenterScroll.isChecked())
        settings.CENTER_ON_SCROLL = self._checkCenterScroll.isChecked()
        qsettings.setValue('removeTrailingSpaces',
            self._checkTrailing.isChecked())
        settings.REMOVE_TRAILING_SPACES = self._checkTrailing.isChecked()
        qsettings.setValue('showTabsAndSpaces',
            self._checkShowSpaces.isChecked())
        settings.SHOW_TABS_AND_SPACES = self._checkShowSpaces.isChecked()
        qsettings.setValue('useTabs', self._checkUseTabs.isChecked())
        settings.USE_TABS = self._checkUseTabs.isChecked()
        qsettings.setValue('allowWordWrap', self._allowWordWrap.isChecked())
        settings.ALLOW_WORD_WRAP = self._allowWordWrap.isChecked()
        qsettings.setValue('checkForDocstrings',
            self._checkForDocstrings.isChecked())
        settings.CHECK_FOR_DOCSTRINGS = self._checkForDocstrings.isChecked()
        qsettings.endGroup()
        qsettings.endGroup()
        action = actions.Actions()
        action.reset_editor_flags()
        action.call_editors_function("set_tab_usage")
        if settings.USE_TABS:
            settings.pep8mod_add_ignore("W191")
        else:
            settings.pep8mod_remove_ignore("W191")
        settings.pep8mod_refresh_checks()
        main_container.MainContainer().update_editor_margin_line()


class EditorCompletion(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        vbox = QVBoxLayout(self)

        groupBoxClose = QGroupBox(self.tr("Complete:"))
        formClose = QGridLayout(groupBoxClose)
        self._checkParentheses = QCheckBox(self.tr("Parentheses: ()"))
        self._checkParentheses.setChecked('(' in settings.BRACES)
        self._checkKeys = QCheckBox(self.tr("Keys: {}"))
        self._checkKeys.setChecked('{' in settings.BRACES)
        self._checkBrackets = QCheckBox(self.tr("Brackets: []"))
        self._checkBrackets.setChecked('[' in settings.BRACES)
        self._checkSimpleQuotes = QCheckBox(self.tr("Simple Quotes: ''"))
        self._checkSimpleQuotes.setChecked("'" in settings.QUOTES)
        self._checkDoubleQuotes = QCheckBox(self.tr("Double Quotes: \"\""))
        self._checkDoubleQuotes.setChecked('"' in settings.QUOTES)
        self._checkCompleteDeclarations = QCheckBox(
            self.tr("Complete Declarations\n"
            "(execute the opposite action with: %s).") %
                resources.get_shortcut("Complete-Declarations").toString(
                    QKeySequence.NativeText))
        self._checkCompleteDeclarations.setChecked(
            settings.COMPLETE_DECLARATIONS)
        formClose.addWidget(self._checkParentheses, 1, 1,
            alignment=Qt.AlignTop)
        formClose.addWidget(self._checkKeys, 1, 2, alignment=Qt.AlignTop)
        formClose.addWidget(self._checkBrackets, 2, 1, alignment=Qt.AlignTop)
        formClose.addWidget(self._checkSimpleQuotes, 2, 2,
            alignment=Qt.AlignTop)
        formClose.addWidget(self._checkDoubleQuotes, 3, 1,
            alignment=Qt.AlignTop)
        vbox.addWidget(groupBoxClose)

        groupBoxCode = QGroupBox(self.tr("Code Completion:"))
        formCode = QGridLayout(groupBoxCode)
        self._checkCodeDot = QCheckBox(
            self.tr("Activate Code Completion with: \".\""))
        self._checkCodeDot.setChecked(settings.CODE_COMPLETION)
        formCode.addWidget(self._checkCompleteDeclarations, 5, 1,
            alignment=Qt.AlignTop)

        formCode.addWidget(self._checkCodeDot, 6, 1, alignment=Qt.AlignTop)
        vbox.addWidget(groupBoxCode)
        vbox.addItem(QSpacerItem(0, 10, QSizePolicy.Expanding,
            QSizePolicy.Expanding))

    def save(self):
        qsettings = QSettings(resources.SETTINGS_PATH, QSettings.IniFormat)
        qsettings.beginGroup('preferences')
        qsettings.beginGroup('editor')
        qsettings.setValue('parentheses', self._checkParentheses.isChecked())
        if self._checkParentheses.isChecked():
            settings.BRACES['('] = ')'
        elif ('(') in settings.BRACES:
            del settings.BRACES['(']
        qsettings.setValue('brackets', self._checkBrackets.isChecked())
        if self._checkBrackets.isChecked():
            settings.BRACES['['] = ']'
        elif ('[') in settings.BRACES:
            del settings.BRACES['[']
        qsettings.setValue('keys', self._checkKeys.isChecked())
        if self._checkKeys.isChecked():
            settings.BRACES['{'] = '}'
        elif ('{') in settings.BRACES:
            del settings.BRACES['{']
        qsettings.setValue('simpleQuotes', self._checkSimpleQuotes.isChecked())
        if self._checkSimpleQuotes.isChecked():
            settings.QUOTES["'"] = "'"
        elif ("'") in settings.QUOTES:
            del settings.QUOTES["'"]
        qsettings.setValue('doubleQuotes', self._checkDoubleQuotes.isChecked())
        if self._checkDoubleQuotes.isChecked():
            settings.QUOTES['"'] = '"'
        elif ('"') in settings.QUOTES:
            del settings.QUOTES['"']
        qsettings.setValue('codeCompletion', self._checkCodeDot .isChecked())
        settings.CODE_COMPLETION = self._checkCodeDot.isChecked()
        settings.COMPLETE_DECLARATIONS = \
            self._checkCompleteDeclarations.isChecked()
        qsettings.setValue("completeDeclarations",
            settings.COMPLETE_DECLARATIONS)
        qsettings.endGroup()
        qsettings.endGroup()


class EditorSchemeDesigner(QWidget):

    def __init__(self, parent):
        super(EditorSchemeDesigner, self).__init__()
        self._parent = parent
        vbox = QVBoxLayout(self)
        scrollArea = QScrollArea()
        vbox.addWidget(scrollArea)
        self.original_style = copy.copy(resources.CUSTOM_SCHEME)

        self.txtKeyword = QLineEdit()
        btnKeyword = QPushButton(self.tr("Pick Color"))
        self.txtOperator = QLineEdit()
        btnOperator = QPushButton(self.tr("Pick Color"))
        self.txtBrace = QLineEdit()
        btnBrace = QPushButton(self.tr("Pick Color"))
        self.txtDefinition = QLineEdit()
        btnDefinition = QPushButton(self.tr("Pick Color"))
        self.txtString = QLineEdit()
        btnString = QPushButton(self.tr("Pick Color"))
        self.txtString2 = QLineEdit()
        btnString2 = QPushButton(self.tr("Pick Color"))
        self.txtComment = QLineEdit()
        btnComment = QPushButton(self.tr("Pick Color"))
        self.txtProperObject = QLineEdit()
        btnProperObject = QPushButton(self.tr("Pick Color"))
        self.txtNumbers = QLineEdit()
        btnNumbers = QPushButton(self.tr("Pick Color"))
        self.txtSpaces = QLineEdit()
        btnSpaces = QPushButton(self.tr("Pick Color"))
        self.txtExtras = QLineEdit()
        btnExtras = QPushButton(self.tr("Pick Color"))
        self.txtEditorText = QLineEdit()
        btnEditorText = QPushButton(self.tr("Pick Color"))
        self.txtEditorBackground = QLineEdit()
        btnEditorBackground = QPushButton(self.tr("Pick Color"))
        self.txtEditorSelectionColor = QLineEdit()
        btnEditorSelectionColor = QPushButton(self.tr("Pick Color"))
        self.txtEditorSelectionBackground = QLineEdit()
        btnEditorSelectionBackground = QPushButton(self.tr("Pick Color"))
        self.txtSelectedWord = QLineEdit()
        btnSelectedWord = QPushButton(self.tr("Pick Color"))
        self.txtCurrentLine = QLineEdit()
        btnCurrentLine = QPushButton(self.tr("Pick Color"))
        self.txtFoldArea = QLineEdit()
        btnFoldArea = QPushButton(self.tr("Pick Color"))
        self.txtFoldArrow = QLineEdit()
        btnFoldArrow = QPushButton(self.tr("Pick Color"))
        self.txtLinkNavigate = QLineEdit()
        btnLinkNavigate = QPushButton(self.tr("Pick Color"))
        self.txtBraceBackground = QLineEdit()
        btnBraceBackground = QPushButton(self.tr("Pick Color"))
        self.txtBraceForeground = QLineEdit()
        btnBraceForeground = QPushButton(self.tr("Pick Color"))
        self.txtErrorUnderline = QLineEdit()
        btnErrorUnderline = QPushButton(self.tr("Pick Color"))
        self.txtPep8Underline = QLineEdit()
        btnPep8Underline = QPushButton(self.tr("Pick Color"))
        self.txtSidebarBackground = QLineEdit()
        btnSidebarBackground = QPushButton(self.tr("Pick Color"))
        self.txtSidebarForeground = QLineEdit()
        btnSidebarForeground = QPushButton(self.tr("Pick Color"))

        hbox = QHBoxLayout()
        hbox.addWidget(QLabel(self.tr("<b>New Theme Name:</b>")))
        self.line_name = QLineEdit()
        hbox.addWidget(self.line_name)
        btnSaveScheme = QPushButton(self.tr("Save Scheme!"))
        hbox.addWidget(btnSaveScheme)

        grid = QGridLayout()
        grid.addWidget(QLabel(self.tr("Keyword:")), 0, 0)
        grid.addWidget(self.txtKeyword, 0, 1)
        grid.addWidget(btnKeyword, 0, 2)
        grid.addWidget(QLabel(self.tr("Operator:")), 1, 0)
        grid.addWidget(self.txtOperator, 1, 1)
        grid.addWidget(btnOperator, 1, 2)
        grid.addWidget(QLabel(self.tr("Braces:")), 2, 0)
        grid.addWidget(self.txtBrace, 2, 1)
        grid.addWidget(btnBrace, 2, 2)
        grid.addWidget(QLabel(self.tr("Definition:")), 3, 0)
        grid.addWidget(self.txtDefinition, 3, 1)
        grid.addWidget(btnDefinition, 3, 2)
        grid.addWidget(QLabel(self.tr("String:")), 4, 0)
        grid.addWidget(self.txtString, 4, 1)
        grid.addWidget(btnString, 4, 2)
        grid.addWidget(QLabel(self.tr("String2:")), 5, 0)
        grid.addWidget(self.txtString2, 5, 1)
        grid.addWidget(btnString2, 5, 2)
        grid.addWidget(QLabel(self.tr("Comment:")), 6, 0)
        grid.addWidget(self.txtComment, 6, 1)
        grid.addWidget(btnComment, 6, 2)
        grid.addWidget(QLabel(self.tr("Proper Object:")), 7, 0)
        grid.addWidget(self.txtProperObject, 7, 1)
        grid.addWidget(btnProperObject, 7, 2)
        grid.addWidget(QLabel(self.tr("Numbers:")), 8, 0)
        grid.addWidget(self.txtNumbers, 8, 1)
        grid.addWidget(btnNumbers, 8, 2)
        grid.addWidget(QLabel(self.tr("Spaces:")), 9, 0)
        grid.addWidget(self.txtSpaces, 9, 1)
        grid.addWidget(btnSpaces, 9, 2)
        grid.addWidget(QLabel(self.tr("Extras:")), 10, 0)
        grid.addWidget(self.txtExtras, 10, 1)
        grid.addWidget(btnExtras, 10, 2)
        grid.addWidget(QLabel(self.tr("Editor Text:")), 11, 0)
        grid.addWidget(self.txtEditorText, 11, 1)
        grid.addWidget(btnEditorText, 11, 2)
        grid.addWidget(QLabel(self.tr("Editor Background:")), 12, 0)
        grid.addWidget(self.txtEditorBackground, 12, 1)
        grid.addWidget(btnEditorBackground, 12, 2)
        grid.addWidget(QLabel(self.tr("Editor Selection Color:")), 13, 0)
        grid.addWidget(self.txtEditorSelectionColor, 13, 1)
        grid.addWidget(btnEditorSelectionColor, 13, 2)
        grid.addWidget(QLabel(self.tr("Editor Selection Background:")), 14, 0)
        grid.addWidget(self.txtEditorSelectionBackground, 14, 1)
        grid.addWidget(btnEditorSelectionBackground, 14, 2)
        grid.addWidget(QLabel(self.tr("Editor Selected Word:")), 15, 0)
        grid.addWidget(self.txtSelectedWord, 15, 1)
        grid.addWidget(btnSelectedWord, 15, 2)
        grid.addWidget(QLabel(self.tr("Current Line:")), 16, 0)
        grid.addWidget(self.txtCurrentLine, 16, 1)
        grid.addWidget(btnCurrentLine, 16, 2)
        grid.addWidget(QLabel(self.tr("Fold Area:")), 17, 0)
        grid.addWidget(self.txtFoldArea, 17, 1)
        grid.addWidget(btnFoldArea, 17, 2)
        grid.addWidget(QLabel(self.tr("Fold Arrow:")), 18, 0)
        grid.addWidget(self.txtFoldArrow, 18, 1)
        grid.addWidget(btnFoldArrow, 18, 2)
        grid.addWidget(QLabel(self.tr("Link Navigate:")), 19, 0)
        grid.addWidget(self.txtLinkNavigate, 19, 1)
        grid.addWidget(btnLinkNavigate, 19, 2)
        grid.addWidget(QLabel(self.tr("Brace Background:")), 20, 0)
        grid.addWidget(self.txtBraceBackground, 20, 1)
        grid.addWidget(btnBraceBackground, 20, 2)
        grid.addWidget(QLabel(self.tr("Brace Foreground:")), 21, 0)
        grid.addWidget(self.txtBraceForeground, 21, 1)
        grid.addWidget(btnBraceForeground, 21, 2)
        grid.addWidget(QLabel(self.tr("Error Underline:")), 22, 0)
        grid.addWidget(self.txtErrorUnderline, 22, 1)
        grid.addWidget(btnErrorUnderline, 22, 2)
        grid.addWidget(QLabel(self.tr("PEP8 Underline:")), 23, 0)
        grid.addWidget(self.txtPep8Underline, 23, 1)
        grid.addWidget(btnPep8Underline, 23, 2)
        grid.addWidget(QLabel(self.tr("Sidebar Background:")), 24, 0)
        grid.addWidget(self.txtSidebarBackground, 24, 1)
        grid.addWidget(btnSidebarBackground, 24, 2)
        grid.addWidget(QLabel(self.tr("Sidebar Foreground:")), 25, 0)
        grid.addWidget(self.txtSidebarForeground, 25, 1)
        grid.addWidget(btnSidebarForeground, 25, 2)

        frame = QFrame()
        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addLayout(grid)
        frame.setLayout(vbox)
        scrollArea.setWidget(frame)

        self.connect(self.txtKeyword, SIGNAL("textChanged(QString)"),
            lambda: self.apply_button_style(
                btnKeyword, self.txtKeyword.text()))
        self.connect(self.txtOperator, SIGNAL("textChanged(QString)"),
            lambda: self.apply_button_style(
                btnOperator, self.txtOperator.text()))
        self.connect(self.txtBrace, SIGNAL("textChanged(QString)"),
            lambda: self.apply_button_style(btnBrace, self.txtBrace.text()))
        self.connect(self.txtDefinition, SIGNAL("textChanged(QString)"),
            lambda: self.apply_button_style(
                btnDefinition, self.txtDefinition.text()))
        self.connect(self.txtString, SIGNAL("textChanged(QString)"),
            lambda: self.apply_button_style(btnString, self.txtString.text()))
        self.connect(self.txtString2, SIGNAL("textChanged(QString)"),
            lambda: self.apply_button_style(
                btnString2, self.txtString2.text()))
        self.connect(self.txtSpaces, SIGNAL("textChanged(QString)"),
            lambda: self.apply_button_style(btnSpaces, self.txtSpaces.text()))
        self.connect(self.txtExtras, SIGNAL("textChanged(QString)"),
            lambda: self.apply_button_style(btnExtras, self.txtExtras.text()))
        self.connect(self.txtComment, SIGNAL("textChanged(QString)"),
            lambda: self.apply_button_style(
                btnComment, self.txtComment.text()))
        self.connect(self.txtProperObject, SIGNAL("textChanged(QString)"),
            lambda: self.apply_button_style(
                btnProperObject, self.txtProperObject.text()))
        self.connect(self.txtNumbers, SIGNAL("textChanged(QString)"),
            lambda: self.apply_button_style(btnNumbers,
                self.txtNumbers.text()))
        self.connect(self.txtEditorText, SIGNAL("textChanged(QString)"),
            lambda: self.apply_button_style(
                btnEditorText, self.txtEditorText.text()))
        self.connect(self.txtEditorBackground, SIGNAL("textChanged(QString)"),
            lambda: self.apply_button_style(btnEditorBackground,
                self.txtEditorBackground.text()))
        self.connect(self.txtEditorSelectionColor,
            SIGNAL("textChanged(QString)"),
            lambda: self.apply_button_style(btnEditorSelectionColor,
                self.txtEditorSelectionColor.text()))
        self.connect(self.txtEditorSelectionBackground,
            SIGNAL("textChanged(QString)"),
            lambda: self.apply_button_style(btnEditorSelectionBackground,
                self.txtEditorSelectionBackground.text()))
        self.connect(self.txtCurrentLine, SIGNAL("textChanged(QString)"),
            lambda: self.apply_button_style(
                btnCurrentLine, self.txtCurrentLine.text()))
        self.connect(self.txtSelectedWord, SIGNAL("textChanged(QString)"),
            lambda: self.apply_button_style(
                btnSelectedWord, self.txtSelectedWord.text()))
        self.connect(self.txtFoldArea, SIGNAL("textChanged(QString)"),
            lambda: self.apply_button_style(
                btnFoldArea, self.txtFoldArea.text()))
        self.connect(self.txtFoldArrow, SIGNAL("textChanged(QString)"),
            lambda: self.apply_button_style(
                btnFoldArrow, self.txtFoldArrow.text()))
        self.connect(self.txtLinkNavigate, SIGNAL("textChanged(QString)"),
            lambda: self.apply_button_style(
                btnLinkNavigate, self.txtLinkNavigate.text()))
        self.connect(self.txtBraceBackground, SIGNAL("textChanged(QString)"),
            lambda: self.apply_button_style(btnBraceBackground,
                self.txtBraceBackground.text()))
        self.connect(self.txtBraceForeground, SIGNAL("textChanged(QString)"),
            lambda: self.apply_button_style(btnBraceForeground,
                self.txtBraceForeground.text()))
        self.connect(self.txtErrorUnderline, SIGNAL("textChanged(QString)"),
            lambda: self.apply_button_style(btnErrorUnderline,
                self.txtErrorUnderline.text()))
        self.connect(self.txtPep8Underline, SIGNAL("textChanged(QString)"),
            lambda: self.apply_button_style(
                btnPep8Underline, self.txtPep8Underline.text()))
        self.connect(self.txtSidebarBackground, SIGNAL("textChanged(QString)"),
            lambda: self.apply_button_style(btnSidebarBackground,
                self.txtSidebarBackground.text()))
        self.connect(self.txtSidebarForeground, SIGNAL("textChanged(QString)"),
            lambda: self.apply_button_style(btnSidebarForeground,
                self.txtSidebarForeground.text()))

        self.connect(btnKeyword, SIGNAL("clicked()"),
            lambda: self._pick_color(self.txtKeyword, btnKeyword))
        self.connect(btnOperator, SIGNAL("clicked()"),
            lambda: self._pick_color(self.txtOperator, btnOperator))
        self.connect(btnBrace, SIGNAL("clicked()"),
            lambda: self._pick_color(self.txtBrace, btnBrace))
        self.connect(btnDefinition, SIGNAL("clicked()"),
            lambda: self._pick_color(self.txtDefinition, btnDefinition))
        self.connect(btnString, SIGNAL("clicked()"),
            lambda: self._pick_color(self.txtString, btnString))
        self.connect(btnString2, SIGNAL("clicked()"),
            lambda: self._pick_color(self.txtString2, btnString2))
        self.connect(btnSpaces, SIGNAL("clicked()"),
            lambda: self._pick_color(self.txtSpaces, btnSpaces))
        self.connect(btnExtras, SIGNAL("clicked()"),
            lambda: self._pick_color(self.txtExtras, btnExtras))
        self.connect(btnComment, SIGNAL("clicked()"),
            lambda: self._pick_color(self.txtComment, btnComment))
        self.connect(btnProperObject, SIGNAL("clicked()"),
            lambda: self._pick_color(self.txtProperObject, btnProperObject))
        self.connect(btnNumbers, SIGNAL("clicked()"),
            lambda: self._pick_color(self.txtNumbers, btnNumbers))
        self.connect(btnEditorText, SIGNAL("clicked()"),
            lambda: self._pick_color(self.txtEditorText, btnEditorText))
        self.connect(btnEditorBackground, SIGNAL("clicked()"),
            lambda: self._pick_color(self.txtEditorBackground,
                btnEditorBackground))
        self.connect(btnEditorSelectionColor, SIGNAL("clicked()"),
            lambda: self._pick_color(self.txtEditorSelectionColor,
                btnEditorSelectionColor))
        self.connect(btnEditorSelectionBackground, SIGNAL("clicked()"),
            lambda: self._pick_color(self.txtEditorSelectionBackground,
                btnEditorSelectionBackground))
        self.connect(btnCurrentLine, SIGNAL("clicked()"),
            lambda: self._pick_color(self.txtCurrentLine, btnCurrentLine))
        self.connect(btnSelectedWord, SIGNAL("clicked()"),
            lambda: self._pick_color(self.txtSelectedWord, btnSelectedWord))
        self.connect(btnFoldArea, SIGNAL("clicked()"),
            lambda: self._pick_color(self.txtFoldArea, btnFoldArea))
        self.connect(btnFoldArrow, SIGNAL("clicked()"),
            lambda: self._pick_color(self.txtFoldArrow, btnFoldArrow))
        self.connect(btnLinkNavigate, SIGNAL("clicked()"),
            lambda: self._pick_color(self.txtLinkNavigate, btnLinkNavigate))
        self.connect(btnBraceBackground, SIGNAL("clicked()"),
            lambda: self._pick_color(self.txtBraceBackground,
                btnBraceBackground))
        self.connect(btnBraceForeground, SIGNAL("clicked()"),
            lambda: self._pick_color(self.txtBraceForeground,
                btnBraceForeground))
        self.connect(btnErrorUnderline, SIGNAL("clicked()"),
            lambda: self._pick_color(self.txtErrorUnderline,
                btnErrorUnderline))
        self.connect(btnPep8Underline, SIGNAL("clicked()"),
            lambda: self._pick_color(self.txtPep8Underline, btnPep8Underline))
        self.connect(btnSidebarBackground, SIGNAL("clicked()"),
            lambda: self._pick_color(self.txtSidebarBackground,
                btnSidebarBackground))
        self.connect(btnSidebarForeground, SIGNAL("clicked()"),
            lambda: self._pick_color(self.txtSidebarForeground,
                btnSidebarForeground))

        # Connect Buttons
        for i in range(0, 26):
            item = grid.itemAtPosition(i, 1).widget()
            btn = grid.itemAtPosition(i, 2).widget()
            self.connect(item, SIGNAL("returnPressed()"),
                self._preview_style)
            self.apply_button_style(btn, item.text())

        self.connect(btnSaveScheme, SIGNAL("clicked()"), self.save_scheme)

    def _apply_line_edit_style(self):
        self.txtKeyword.setText(resources.CUSTOM_SCHEME.get('keyword',
            resources.COLOR_SCHEME['keyword']))
        self.txtOperator.setText(resources.CUSTOM_SCHEME.get('operator',
            resources.COLOR_SCHEME['operator']))
        self.txtBrace.setText(resources.CUSTOM_SCHEME.get('brace',
            resources.COLOR_SCHEME['brace']))
        self.txtDefinition.setText(resources.CUSTOM_SCHEME.get('definition',
            resources.COLOR_SCHEME['definition']))
        self.txtString.setText(resources.CUSTOM_SCHEME.get('string',
            resources.COLOR_SCHEME['string']))
        self.txtString2.setText(resources.CUSTOM_SCHEME.get('string2',
            resources.COLOR_SCHEME['string2']))
        self.txtSpaces.setText(resources.CUSTOM_SCHEME.get('spaces',
            resources.COLOR_SCHEME['spaces']))
        self.txtExtras.setText(resources.CUSTOM_SCHEME.get('extras',
            resources.COLOR_SCHEME['extras']))
        self.txtComment.setText(resources.CUSTOM_SCHEME.get('comment',
            resources.COLOR_SCHEME['comment']))
        self.txtProperObject.setText(resources.CUSTOM_SCHEME.get(
            'properObject', resources.COLOR_SCHEME['properObject']))
        self.txtNumbers.setText(resources.CUSTOM_SCHEME.get('numbers',
            resources.COLOR_SCHEME['numbers']))
        self.txtEditorText.setText(resources.CUSTOM_SCHEME.get('editor-text',
            resources.COLOR_SCHEME['editor-text']))
        self.txtEditorBackground.setText(resources.CUSTOM_SCHEME.get(
            'editor-background', resources.COLOR_SCHEME['editor-background']))
        self.txtEditorSelectionColor.setText(resources.CUSTOM_SCHEME.get(
            'editor-selection-color',
            resources.COLOR_SCHEME['editor-selection-color']))
        self.txtEditorSelectionBackground.setText(resources.CUSTOM_SCHEME.get(
            'editor-selection-background',
            resources.COLOR_SCHEME['editor-selection-background']))
        self.txtCurrentLine.setText(resources.CUSTOM_SCHEME.get('current-line',
            resources.COLOR_SCHEME['current-line']))
        self.txtSelectedWord.setText(resources.CUSTOM_SCHEME.get(
            'selected-word', resources.COLOR_SCHEME['selected-word']))
        self.txtFoldArea.setText(resources.CUSTOM_SCHEME.get(
            'fold-area', resources.COLOR_SCHEME['fold-area']))
        self.txtFoldArrow.setText(resources.CUSTOM_SCHEME.get(
            'fold-arrow', resources.COLOR_SCHEME['fold-arrow']))
        self.txtLinkNavigate.setText(resources.CUSTOM_SCHEME.get(
            'linkNavigate', resources.COLOR_SCHEME['linkNavigate']))
        self.txtBraceBackground.setText(resources.CUSTOM_SCHEME.get(
            'brace-background', resources.COLOR_SCHEME['brace-background']))
        self.txtBraceForeground.setText(resources.CUSTOM_SCHEME.get(
            'brace-foreground', resources.COLOR_SCHEME['brace-foreground']))
        self.txtErrorUnderline.setText(resources.CUSTOM_SCHEME.get(
            'error-underline', resources.COLOR_SCHEME['error-underline']))
        self.txtPep8Underline.setText(resources.CUSTOM_SCHEME.get(
            'pep8-underline', resources.COLOR_SCHEME['pep8-underline']))
        self.txtSidebarBackground.setText(resources.CUSTOM_SCHEME.get(
            'sidebar-background',
            resources.COLOR_SCHEME['sidebar-background']))
        self.txtSidebarForeground.setText(resources.CUSTOM_SCHEME.get(
            'sidebar-foreground',
            resources.COLOR_SCHEME['sidebar-foreground']))

    def _pick_color(self, lineedit, btn):
        color = QColorDialog.getColor(QColor(lineedit.text()),
            self, self.tr("Choose Color for: "))
        if color.isValid():
            lineedit.setText(str(color.name()))
            self.apply_button_style(btn, color.name())
            self._preview_style()

    def apply_button_style(self, btn, color_name):
        if QColor(color_name).isValid():
            btn.setAutoFillBackground(True)
            style = ('background: %s; border-radius: 5px; '
                     'padding: 5px;' % color_name)
            btn.setStyleSheet(style)

    def _preview_style(self):
        scheme = {
            "keyword": str(self.txtKeyword.text()),
            "operator": str(self.txtOperator.text()),
            "brace": str(self.txtBrace.text()),
            "definition": str(self.txtDefinition.text()),
            "string": str(self.txtString.text()),
            "string2": str(self.txtString2.text()),
            "comment": str(self.txtComment.text()),
            "properObject": str(self.txtProperObject.text()),
            "numbers": str(self.txtNumbers.text()),
            "spaces": str(self.txtSpaces.text()),
            "extras": str(self.txtExtras.text()),
            "editor-background": str(self.txtEditorBackground.text()),
            "editor-selection-color": str(
                self.txtEditorSelectionColor.text()),
            "editor-selection-background": str(
                self.txtEditorSelectionBackground.text()),
            "editor-text": str(self.txtEditorText.text()),
            "current-line": str(self.txtCurrentLine.text()),
            "selected-word": str(self.txtSelectedWord.text()),
            "fold-area": str(self.txtFoldArea.text()),
            "fold-arrow": str(self.txtFoldArrow.text()),
            "linkNavigate": str(self.txtLinkNavigate.text()),
            "brace-background": str(self.txtBraceBackground.text()),
            "brace-foreground": str(self.txtBraceForeground.text()),
            "error-underline": str(self.txtErrorUnderline.text()),
            "pep8-underline": str(self.txtPep8Underline.text()),
            "sidebar-background": str(self.txtSidebarBackground.text()),
            "sidebar-foreground": str(self.txtSidebarForeground.text())}
        resources.CUSTOM_SCHEME = scheme
        editorWidget = main_container.MainContainer().get_actual_editor()
        if editorWidget is not None:
            editorWidget.restyle(editorWidget.lang)
            editorWidget.highlight_current_line()
            editorWidget._sidebarWidget.repaint()
        return scheme

    def hideEvent(self, event):
        super(EditorSchemeDesigner, self).hideEvent(event)
        resources.CUSTOM_SCHEME = self.original_style
        editorWidget = main_container.MainContainer().get_actual_editor()
        if editorWidget is not None:
            editorWidget.restyle(editorWidget.lang)

    def showEvent(self, event):
        super(EditorSchemeDesigner, self).showEvent(event)
        schemes = self._parent._editorGeneral._schemes
        scheme = self._parent._editorGeneral.current_scheme
        resources.CUSTOM_SCHEME = schemes.get(scheme, resources.COLOR_SCHEME)
        editorWidget = main_container.MainContainer().get_actual_editor()
        if editorWidget is not None:
            editorWidget.restyle(editorWidget.lang)
            editorWidget._sidebarWidget.repaint()
        self._apply_line_edit_style()
        if scheme != 'default':
            self.line_name.setText(scheme)

    def save(self):
        """All the widgets in preferences must contain a save method."""
        pass

    @staticmethod
    def _is_valid_scheme_name(name):
        """Check if a given name is a valid name for an editor scheme.

        Params:
            name := the name to check

        Returns:
            True if and only if the name is okay to use for a scheme

        """
        return not (name in ('', 'default'))

    def save_scheme(self):
        name = self.line_name.text().strip()
        if not self._is_valid_scheme_name(name):
            QMessageBox.information(self, self.tr("Invalid Scheme Name"),
                self.tr("The scheme name you have chosen is invalid.\nPlease "
                    "pick a different name."))
            return
        fileName = ('{0}.color'.format(
            file_manager.create_path(resources.EDITOR_SKINS, name)))
        answer = True
        if file_manager.file_exists(fileName):
            answer = QMessageBox.question(self,
                self.tr("Scheme already exists"),
                (self.tr("Do you want to override the file: %s?") % fileName),
                QMessageBox.Yes, QMessageBox.No)

        if name != '' and answer in (QMessageBox.Yes, True):
            scheme = self._preview_style()
            qsettings = QSettings(resources.SETTINGS_PATH, QSettings.IniFormat)
            qsettings.beginGroup('preferences')
            qsettings.beginGroup('editor')
            if qsettings.value('scheme', defaultValue='',
                type='QString') == name and name != 'default':
                self.original_style = copy.copy(scheme)
            json_manager.save_editor_skins(fileName, scheme)
            QMessageBox.information(self, self.tr("Scheme Saved"),
                    (self.tr("The scheme has been saved at: %s.") % fileName))
        elif answer == QMessageBox.Yes:
            QMessageBox.information(self, self.tr("Scheme Not Saved"),
                self.tr("The name probably is invalid."))


class ThemeTab(QTabWidget):

    def __init__(self):
        super(ThemeTab, self).__init__()
        self.theme_chooser = ThemeChooser()
        self.theme_designer = ThemeDesigner(self)

        self.addTab(self.theme_chooser, self.tr("Theme Chooser"))
        self.addTab(self.theme_designer, self.tr("Theme Designer"))

    def save(self):
        self.theme_chooser.save()


class ThemeChooser(QWidget):

    def __init__(self):
        super(ThemeChooser, self).__init__()
        vbox = QVBoxLayout(self)

        vbox.addWidget(QLabel(self.tr("<b>Select Theme:</b>")))
        self.list_skins = QListWidget()
        self.list_skins.setSelectionMode(QListWidget.SingleSelection)
        vbox.addWidget(self.list_skins)
        self.btn_delete = QPushButton(self.tr("Delete Theme"))
        self.btn_preview = QPushButton(self.tr("Preview Theme"))
        hbox = QHBoxLayout()
        hbox.addWidget(self.btn_delete)
        hbox.addSpacerItem(QSpacerItem(10, 0, QSizePolicy.Expanding,
            QSizePolicy.Fixed))
        hbox.addWidget(self.btn_preview)
        vbox.addLayout(hbox)
        self._refresh_list()

        self.connect(self.btn_preview, SIGNAL("clicked()"), self.preview_theme)
        self.connect(self.btn_delete, SIGNAL("clicked()"), self.delete_theme)

    def delete_theme(self):
        if self.list_skins.currentRow() != 0:
            file_name = ("%s.qss" %
                self.list_skins.currentItem().text())
            qss_file = file_manager.create_path(resources.NINJA_THEME_DOWNLOAD,
                file_name)
            file_manager.delete_file(qss_file)
            self._refresh_list()

    def showEvent(self, event):
        self._refresh_list()
        super(ThemeChooser, self).showEvent(event)

    def _refresh_list(self):
        self.list_skins.clear()
        self.list_skins.addItem("Default")
        self.list_skins.addItem("Classic Theme")

        files = [file_manager.get_file_name(filename) for filename in
            file_manager.get_files_from_folder(
            resources.NINJA_THEME_DOWNLOAD, "qss")]
        files.sort()
        self.list_skins.addItems(files)

        if settings.NINJA_SKIN == 'Default':
            self.list_skins.setCurrentRow(0)
        elif settings.NINJA_SKIN == 'Classic Theme':
            self.list_skins.setCurrentRow(1)
        elif settings.NINJA_SKIN in files:
            index = files.index(settings.NINJA_SKIN)
            self.list_skins.setCurrentRow(index + 1)
        else:
            self.list_skins.setCurrentRow(0)

    def save(self):
        qsettings = QSettings(resources.SETTINGS_PATH, QSettings.IniFormat)
        qsettings.beginGroup('preferences')
        qsettings.beginGroup('theme')
        settings.NINJA_SKIN = self.list_skins.currentItem().text()
        qsettings.setValue("skin", settings.NINJA_SKIN)
        qsettings.endGroup()
        qsettings.endGroup()
        self.preview_theme()

    def preview_theme(self):
        if self.list_skins.currentRow() == 0:
            qss_file = resources.NINJA_THEME
        elif self.list_skins.currentRow() == 1:
            qss_file = resources.NINJA__THEME_CLASSIC
        else:
            file_name = ("%s.qss" %
                self.list_skins.currentItem().text())
            qss_file = file_manager.create_path(resources.NINJA_THEME_DOWNLOAD,
                file_name)
        with open(qss_file) as f:
            qss = f.read()
        QApplication.instance().setStyleSheet(qss)


class ThemeDesigner(QWidget):

    def __init__(self, parent):
        super(ThemeDesigner, self).__init__()
        self._parent = parent
        vbox = QVBoxLayout(self)

        hbox = QHBoxLayout()
        hbox.addWidget(QLabel(self.tr("<b>New Theme Name:</b>")))
        self.line_name = QLineEdit()
        hbox.addWidget(self.line_name)
        self.btn_save = QPushButton(self.tr("Save Theme"))
        hbox.addWidget(self.btn_save)

        self.edit_qss = editor.create_editor(fileName='qss.qss')
        if self.edit_qss._mini:
            self.edit_qss._mini.hide()
        self.edit_qss._mini = None
        self.btn_apply = QPushButton(self.tr("Apply Style Sheet"))
        hbox2 = QHBoxLayout()
        hbox2.addSpacerItem(QSpacerItem(10, 0, QSizePolicy.Expanding,
            QSizePolicy.Fixed))
        hbox2.addWidget(self.btn_apply)
        hbox2.addSpacerItem(QSpacerItem(10, 0, QSizePolicy.Expanding,
            QSizePolicy.Fixed))

        vbox.addLayout(hbox)
        vbox.addWidget(self.edit_qss)
        vbox.addLayout(hbox2)

        self.connect(self.btn_apply, SIGNAL("clicked()"),
            self.apply_stylesheet)
        self.connect(self.btn_save, SIGNAL("clicked()"),
            self.save_stylesheet)

    def showEvent(self, event):
        if not self.edit_qss.document().isModified():
            if self._parent.theme_chooser.list_skins.currentRow() == 0:
                qss_file = resources.NINJA_THEME
            if self._parent.theme_chooser.list_skins.currentRow() == 1:
                qss_file = resources.NINJA__THEME_CLASSIC
            else:
                file_name = ("%s.qss" %
                    self._parent.theme_chooser.list_skins.currentItem().text())
                qss_file = file_manager.create_path(
                    resources.NINJA_THEME_DOWNLOAD, file_name)
            with open(qss_file) as f:
                qss = f.read()
                self.edit_qss.setPlainText(qss)
                self.edit_qss.document().setModified(False)
            self.line_name.setText("%s_%s" %
                (self._parent.theme_chooser.list_skins.currentItem().text(),
                getpass.getuser()))
        super(ThemeDesigner, self).showEvent(event)

    def apply_stylesheet(self):
        qss = self.edit_qss.toPlainText()
        QApplication.instance().setStyleSheet(qss)

    def save_stylesheet(self):
        try:
            file_name = "%s.qss" % self.line_name.text()
            file_name = file_manager.create_path(
                resources.NINJA_THEME_DOWNLOAD, file_name)
            content = self.edit_qss.toPlainText()
            file_manager.store_file_content(file_name, content, newFile=True)
            QMessageBox.information(self, self.tr("Style Sheet Saved"),
                (self.tr("Theme saved at: '%s'." % file_name)))
            self.edit_qss.document().setModified(False)
        except file_manager.NinjaFileExistsException as ex:
            QMessageBox.information(self, self.tr("File Already Exists"),
                (self.tr("Invalid File Name: the file '%s' already exists.") %
                    ex.filename))
