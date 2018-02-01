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

from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QStyle
from PyQt5.QtWidgets import QToolBar
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QSize

from ninja_ide import resources
from ninja_ide import translations
from ninja_ide.core import settings
from ninja_ide.core.file_handling import file_manager
from ninja_ide.gui.ide import IDE
from ninja_ide.gui.dialogs.preferences import preferences


class Interface(QWidget):
    """Interface widget class."""

    def __init__(self, parent):
        super(Interface, self).__init__()
        self._preferences, vbox = parent, QVBoxLayout(self)
        self.toolbar_settings = settings.TOOLBAR_ITEMS

        groupBoxExplorer = QGroupBox(
            translations.TR_PREFERENCES_INTERFACE_EXPLORER_PANEL)
        group_theme = QGroupBox(
            translations.TR_PREFERENCES_THEME)
        group_hdpi = QGroupBox(translations.TR_PREFERENCES_SCREEN_RESOLUTION)
        # groupBoxToolbar = QGroupBox(
        #    translations.TR_PREFERENCES_INTERFACE_TOOLBAR_CUSTOMIZATION)
        groupBoxLang = QGroupBox(
            translations.TR_PREFERENCES_INTERFACE_LANGUAGE)

       # Explorers
        vboxExplorer = QVBoxLayout(groupBoxExplorer)
        self._checkProjectExplorer = QCheckBox(
            translations.TR_PREFERENCES_SHOW_EXPLORER)
        self._checkSymbols = QCheckBox(
            translations.TR_PREFERENCES_SHOW_SYMBOLS)
        self._checkWebInspetor = QCheckBox(
            translations.TR_PREFERENCES_SHOW_WEB_INSPECTOR)
        self._checkFileErrors = QCheckBox(
            translations.TR_PREFERENCES_SHOW_FILE_ERRORS)
        self._checkMigrationTips = QCheckBox(
            translations.TR_PREFERENCES_SHOW_MIGRATION)
        vboxExplorer.addWidget(self._checkProjectExplorer)
        vboxExplorer.addWidget(self._checkSymbols)
        vboxExplorer.addWidget(self._checkWebInspetor)
        vboxExplorer.addWidget(self._checkFileErrors)
        vboxExplorer.addWidget(self._checkMigrationTips)
        # Theme
        vbox_theme = QVBoxLayout(group_theme)
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel(translations.TR_PREFERENCES_NINJA_THEME))
        self._combobox_themes = QComboBox()
        # self._combobox_themes.addItems(theme.available_theme_names())
        self._combobox_themes.setCurrentText(settings.NINJA_SKIN)
        hbox.addWidget(self._combobox_themes)
        vbox_theme.addLayout(hbox)
        vbox_theme.addWidget(
            QLabel(translations.TR_PREFERENCES_REQUIRES_RESTART))
        # HDPI
        hbox = QHBoxLayout(group_hdpi)
        self._combo_resolution = QComboBox()
        self._combo_resolution.addItems([
            translations.TR_PREFERENCES_SCREEN_NORMAL,
            translations.TR_PREFERENCES_SCREEN_AUTO_HDPI,
            translations.TR_PREFERENCES_SCREEN_CUSTOM_HDPI
        ])
        self._combo_resolution.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Fixed)
        hbox.addWidget(self._combo_resolution)
        self._line_custom_hdpi = QLineEdit()
        self._line_custom_hdpi.setPlaceholderText("1.5")
        hbox.addWidget(self._line_custom_hdpi)
        #GUI - Toolbar
        #vbox_toolbar = QVBoxLayout(groupBoxToolbar)
        #hbox_select_items = QHBoxLayout()
        #label_toolbar = QLabel(translations.TR_PREFERENCES_TOOLBAR_ITEMS)
        #label_toolbar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        #hbox_select_items.addWidget(label_toolbar)
        #self._comboToolbarItems = QComboBox()
        #self._load_combo_data(self._comboToolbarItems)
        #self._btnItemAdd = QPushButton(QIcon(":img/add"), '')
        #self._btnItemAdd.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        #self._btnItemAdd.setIconSize(QSize(16, 16))
        #self._btnItemRemove = QPushButton(QIcon(':img/delete'), '')
        #self._btnItemRemove.setIconSize(QSize(16, 16))
        #self._btnDefaultItems = QPushButton(
            #translations.TR_PREFERENCES_TOOLBAR_DEFAULT)
        #self._btnDefaultItems.setSizePolicy(QSizePolicy.Fixed,
                                            #QSizePolicy.Fixed)
        #self._btnItemRemove.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        #hbox_select_items.addWidget(self._comboToolbarItems)
        #hbox_select_items.addWidget(self._btnItemAdd)
        #hbox_select_items.addWidget(self._btnItemRemove)
        #hbox_select_items.addWidget(self._btnDefaultItems)
        #vbox_toolbar.addLayout(hbox_select_items)
        #self._toolbar_items = QToolBar()
        #self._toolbar_items.setObjectName("custom")
        #self._toolbar_items.setToolButtonStyle(Qt.ToolButtonIconOnly)
        #self._load_toolbar()
        #vbox_toolbar.addWidget(self._toolbar_items)
        #vbox_toolbar.addWidget(QLabel(
            #translations.TR_PREFERENCES_TOOLBAR_CONFIG_HELP))
        # Language
        vboxLanguage = QVBoxLayout(groupBoxLang)
        vboxLanguage.addWidget(QLabel(
            translations.TR_PREFERENCES_SELECT_LANGUAGE))
        self._comboLang = QComboBox()
        self._comboLang.setEnabled(False)
        vboxLanguage.addWidget(self._comboLang)
        vboxLanguage.addWidget(QLabel(
            translations.TR_PREFERENCES_REQUIRES_RESTART))

        # Load Languages
        self._load_langs()

        # Settings
        self._checkProjectExplorer.setChecked(
            settings.SHOW_PROJECT_EXPLORER)
        self._checkSymbols.setChecked(settings.SHOW_SYMBOLS_LIST)
        self._checkWebInspetor.setChecked(settings.SHOW_WEB_INSPECTOR)
        self._checkFileErrors.setChecked(settings.SHOW_ERRORS_LIST)
        self._checkMigrationTips.setChecked(settings.SHOW_MIGRATION_LIST)
        self._line_custom_hdpi.setText(settings.CUSTOM_SCREEN_RESOLUTION)
        index = 0
        if settings.HDPI:
            index = 1
        elif settings.CUSTOM_SCREEN_RESOLUTION:
            index = 2
        self._combo_resolution.setCurrentIndex(index)

        vbox.addWidget(groupBoxExplorer)
        vbox.addWidget(group_theme)
        vbox.addWidget(group_hdpi)
        # vbox.addWidget(groupBoxToolbar)
        vbox.addWidget(groupBoxLang)
        vbox.addStretch(1)

        # Signals
        # self.connect(self._btnItemAdd, SIGNAL("clicked()"),
        #             # self.toolbar_item_added)
        # self.connect(self._btnItemRemove, SIGNAL("clicked()"),
        #             # self.toolbar_item_removed)
        # self.connect(self._btnDefaultItems, SIGNAL("clicked()"),
        #             # self.toolbar_items_default)
        self._combo_resolution.currentIndexChanged.connect(
            self._on_resolution_changed)
        self._preferences.savePreferences.connect(self.save)

    def _on_resolution_changed(self, index):
        enabled = False
        if index == 2:
            enabled = True
        self._line_custom_hdpi.setEnabled(enabled)
    #def toolbar_item_added(self):
        #data = self._comboToolbarItems.itemData(
            #self._comboToolbarItems.currentIndex())
        #if data not in self.toolbar_settings or data == 'separator':
            #selected = self.actionGroup.checkedAction()
            #if selected is None:
                #self.toolbar_settings.append(data)
            #else:
                #dataAction = selected.data()
                #self.toolbar_settings.insert(
                    #self.toolbar_settings.index(dataAction) + 1, data)
            #self._load_toolbar()

##    def toolbar_item_removed(self):
        #data = self._comboToolbarItems.itemData(
            #self._comboToolbarItems.currentIndex())
        #if data in self.toolbar_settings and data != 'separator':
            #self.toolbar_settings.pop(self.toolbar_settings.index(data))
            #self._load_toolbar()
        #elif data == 'separator':
            #self.toolbar_settings.reverse()
            #self.toolbar_settings.pop(self.toolbar_settings.index(data))
            #self.toolbar_settings.reverse()
            #self._load_toolbar()

##    def toolbar_items_default(self):
        #self.toolbar_settings = settings.TOOLBAR_ITEMS_DEFAULT
        #self._load_toolbar()

##    def _load_combo_data(self, combo):
        #self.toolbar_items = {
            #'separator': [QIcon(':img/separator'), 'Add Separtor'],
            #'new-file': [QIcon(resources.IMAGES['new']), self.tr('New File')],
            #'new-project': [QIcon(resources.IMAGES['newProj']),
                #self.tr('New Project')],
            #'save-file': [QIcon(resources.IMAGES['save']),
                #self.tr('Save File')],
            #'save-as': [QIcon(resources.IMAGES['saveAs']), self.tr('Save As')],
            #'save-all': [QIcon(resources.IMAGES['saveAll']),
                #self.tr('Save All')],
            #'save-project': [QIcon(resources.IMAGES['saveAll']),
                #self.tr('Save Project')],
            #'reload-file': [QIcon(resources.IMAGES['reload-file']),
                #self.tr('Reload File')],
            #'open-file': [QIcon(resources.IMAGES['open']),
                #self.tr('Open File')],
            #'open-project': [QIcon(resources.IMAGES['openProj']),
                #self.tr('Open Project')],
            #'activate-profile': [QIcon(resources.IMAGES['activate-profile']),
                #self.tr('Activate Profile')],
            #'deactivate-profile':
                #[QIcon(resources.IMAGES['deactivate-profile']),
                #self.tr('Deactivate Profile')],
            #'print-file': [QIcon(resources.IMAGES['print']),
                #self.tr('Print File')],
            #'close-file':
                #[self.style().standardIcon(QStyle.SP_DialogCloseButton),
                #self.tr('Close File')],
            #'close-projects':
                #[self.style().standardIcon(QStyle.SP_DialogCloseButton),
                #self.tr('Close Projects')],
            #'undo': [QIcon(resources.IMAGES['undo']), self.tr('Undo')],
            #'redo': [QIcon(resources.IMAGES['redo']), self.tr('Redo')],
            #'cut': [QIcon(resources.IMAGES['cut']), self.tr('Cut')],
            #'copy': [QIcon(resources.IMAGES['copy']), self.tr('Copy')],
            #'paste': [QIcon(resources.IMAGES['paste']), self.tr('Paste')],
            #'find': [QIcon(resources.IMAGES['find']), self.tr('Find')],
            #'find-replace': [QIcon(resources.IMAGES['findReplace']),
                #self.tr('Find/Replace')],
            #'find-files': [QIcon(resources.IMAGES['find']),
                #self.tr('Find In files')],
            #'code-locator': [QIcon(resources.IMAGES['locator']),
                #self.tr('Code Locator')],
            #'splith': [QIcon(resources.IMAGES['splitH']),
                #self.tr('Split Horizontally')],
            #'splitv': [QIcon(resources.IMAGES['splitV']),
                #self.tr('Split Vertically')],
            #'follow-mode': [QIcon(resources.IMAGES['follow']),
                #self.tr('Follow Mode')],
            #'zoom-in': [QIcon(resources.IMAGES['zoom-in']), self.tr('Zoom In')],
            #'zoom-out': [QIcon(resources.IMAGES['zoom-out']),
                #self.tr('Zoom Out')],
            #'indent-more': [QIcon(resources.IMAGES['indent-more']),
                #self.tr('Indent More')],
            #'indent-less': [QIcon(resources.IMAGES['indent-less']),
                #self.tr('Indent Less')],
            #'comment': [QIcon(resources.IMAGES['comment-code']),
                #self.tr('Comment')],
            #'uncomment': [QIcon(resources.IMAGES['uncomment-code']),
                #self.tr('Uncomment')],
            #'go-to-definition': [QIcon(resources.IMAGES['go-to-definition']),
                #self.tr('Go To Definition')],
            #'insert-import': [QIcon(resources.IMAGES['insert-import']),
                #self.tr('Insert Import')],
            #'run-project': [QIcon(resources.IMAGES['play']), 'Run Project'],
            #'run-file': [QIcon(resources.IMAGES['file-run']), 'Run File'],
            #'stop': [QIcon(resources.IMAGES['stop']), 'Stop'],
            #'preview-web': [QIcon(resources.IMAGES['preview-web']),
                #self.tr('Preview Web')]}
        #for item in self.toolbar_items:
            #combo.addItem(self.toolbar_items[item][0],
                #self.toolbar_items[item][1], item)
        #combo.model().sort(0)

##    def _load_toolbar(self):
        #pass
        ##self._toolbar_items.clear()
        ##self.actionGroup = QActionGroup(self)
        ##self.actionGroup.setExclusive(True)
        ##for item in self.toolbar_settings:
            ##if item == 'separator':
                ##self._toolbar_items.addSeparator()
            ##else:
                ##action = self._toolbar_items.addAction(
                    ##self.toolbar_items[item][0], self.toolbar_items[item][1])
                ##action.setData(item)
                ##action.setCheckable(True)
                ##self.actionGroup.addAction(action)

    def _load_langs(self):
        langs = file_manager.get_files_from_folder(
            resources.LANGS, '.qm')
        self._languages = ['English'] + \
            [file_manager.get_module_name(lang) for lang in langs]
        self._comboLang.addItems(self._languages)
        if(self._comboLang.count() > 1):
            self._comboLang.setEnabled(True)
        if settings.LANGUAGE:
            index = self._comboLang.findText(settings.LANGUAGE)
        else:
            index = 0
        self._comboLang.setCurrentIndex(index)

    def save(self):
        qsettings = IDE.ninja_settings()

        qsettings.beginGroup("ide")
        qsettings.beginGroup("interface")

        ninja_theme = self._combobox_themes.currentText()
        settings.NINJA_SKIN = ninja_theme
        qsettings.setValue("skin", settings.NINJA_SKIN)
        settings.SHOW_PROJECT_EXPLORER = self._checkProjectExplorer.isChecked()
        qsettings.setValue("showProjectExplorer",
                           settings.SHOW_PROJECT_EXPLORER)
        settings.SHOW_SYMBOLS_LIST = self._checkSymbols.isChecked()
        qsettings.setValue("showSymbolsList", settings.SHOW_SYMBOLS_LIST)
        if self._line_custom_hdpi.isEnabled():
            screen_resolution = self._line_custom_hdpi.text().strip()
            settings.CUSTOM_SCREEN_RESOLUTION = screen_resolution
        else:
            settings.HDPI = bool(self._combo_resolution.currentIndex())
            qsettings.setValue("autoHdpi", settings.HDPI)
            settings.CUSTOM_SCREEN_RESOLUTION = ""
        qsettings.setValue("customScreenResolution",
                           settings.CUSTOM_SCREEN_RESOLUTION)

        qsettings.endGroup()
        qsettings.endGroup()
        # settings.TOOLBAR_ITEMS = self.toolbar_settings
        # lang = self._comboLang.currentText()
        #preferences/interface
        # qsettings.setValue('preferences/interface/showProjectExplorer',
        #                   self._checkProjectExplorer.isChecked())
        # settings.SHOW_PROJECT_EXPLORER = self._checkProjectExplorer.isChecked()
        # qsettings.setValue('preferences/interface/showSymbolsList',
        #                   self._checkSymbols.isChecked())
        # settings.SHOW_SYMBOLS_LIST = self._checkSymbols.isChecked()
        # qsettings.setValue('preferences/interface/showWebInspector',
        #                   self._checkWebInspetor.isChecked())
        # settings.SHOW_WEB_INSPECTOR = self._checkWebInspetor.isChecked()
        # qsettings.setValue('preferences/interface/showErrorsList',
        #                   self._checkFileErrors.isChecked())
        # settings.SHOW_ERRORS_LIST = self._checkFileErrors.isChecked()
        # qsettings.setValue('preferences/interface/showMigrationList',
        #                   self._checkMigrationTips.isChecked())
        # settings.SHOW_MIGRATION_LIST = self._checkMigrationTips.isChecked()
        #qsettings.setValue('preferences/interface/toolbar',
                           #settings.TOOLBAR_ITEMS)
        # qsettings.setValue('preferences/interface/language', lang)
        # lang = lang + '.qm'
        # settings.LANGUAGE = os.path.join(resources.LANGS, lang)
        #ide = IDE.get_service('ide')
        #if ide:
            #ide.reload_toolbar()


preferences.Preferences.register_configuration(
    'GENERAL',
    Interface,
    translations.TR_PREFERENCES_INTERFACE,
    weight=0,
    subsection="INTERFACE"
)
