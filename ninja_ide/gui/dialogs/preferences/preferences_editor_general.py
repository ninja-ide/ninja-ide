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

import copy

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QGroupBox
from PyQt4.QtGui import QCheckBox
from PyQt4.QtGui import QGridLayout
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QListWidget
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QSpinBox
from PyQt4.QtGui import QFontDialog
from PyQt4.QtGui import QPushButton
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL

from ninja_ide import resources
from ninja_ide import translations
from ninja_ide.core import settings
from ninja_ide.gui.ide import IDE
from ninja_ide.gui.dialogs.preferences import preferences
from ninja_ide.tools import json_manager


class EditorGeneral(QWidget):

    def __init__(self, parent):
        super(EditorGeneral, self).__init__()
        self._preferences = parent
        vbox = QVBoxLayout(self)
        self.original_style = copy.copy(resources.CUSTOM_SCHEME)
        self.current_scheme = 'default'
        self._modified_editors = []
        self._font = settings.FONT

        groupBoxMini = QGroupBox(
            translations.TR_PREFERENCES_EDITOR_GENERAL_MINIMAP)
        groupBoxTypo = QGroupBox(
            translations.TR_PREFERENCES_EDITOR_GENERAL_TYPOGRAPHY)
        groupBoxScheme = QGroupBox(
            translations.TR_PREFERENCES_EDITOR_GENERAL_SCHEME)

        #Minimap
        formMini = QGridLayout(groupBoxMini)
        formMini.setContentsMargins(5, 15, 5, 5)
        self._checkShowMinimap = QCheckBox()
        self._spinMaxOpacity = QSpinBox()
        self._spinMaxOpacity.setMaximum(100)
        self._spinMaxOpacity.setMinimum(0)
        self._spinMinOpacity = QSpinBox()
        self._spinMinOpacity.setMaximum(100)
        self._spinMinOpacity.setMinimum(0)
        self._spinSize = QSpinBox()
        self._spinSize.setMaximum(100)
        self._spinSize.setMinimum(0)
        formMini.addWidget(QLabel(
            translations.TR_PREFERENCES_EDITOR_GENERAL_ENABLE_MINIMAP), 0, 0,
            Qt.AlignRight)
        formMini.addWidget(QLabel(
            translations.TR_PREFERENCES_EDITOR_GENERAL_MAX_OPACITY), 1, 0,
            Qt.AlignRight)
        formMini.addWidget(QLabel(
            translations.TR_PREFERENCES_EDITOR_GENERAL_MIN_OPACITY), 2, 0,
            Qt.AlignRight)
        formMini.addWidget(QLabel(
            translations.TR_PREFERENCES_EDITOR_GENERAL_AREA_MINIMAP), 3, 0,
            Qt.AlignRight)
        formMini.addWidget(self._checkShowMinimap, 0, 1)
        formMini.addWidget(self._spinMaxOpacity, 1, 1)
        formMini.addWidget(self._spinMinOpacity, 2, 1)
        formMini.addWidget(self._spinSize, 3, 1)
        #Typo
        gridTypo = QGridLayout(groupBoxTypo)
        gridTypo.setContentsMargins(5, 15, 5, 5)
        self._btnEditorFont = QPushButton('')
        gridTypo.addWidget(QLabel(
            translations.TR_PREFERENCES_EDITOR_GENERAL_EDITOR_FONT), 0, 0,
            Qt.AlignRight)
        gridTypo.addWidget(self._btnEditorFont, 0, 1)
        #Scheme
        vboxScheme = QVBoxLayout(groupBoxScheme)
        vboxScheme.setContentsMargins(5, 15, 5, 5)
        self._listScheme = QListWidget()
        vboxScheme.addWidget(self._listScheme)

        vbox.addWidget(groupBoxMini)
        vbox.addWidget(groupBoxTypo)
        vbox.addWidget(groupBoxScheme)

        #Settings
        qsettings = IDE.ninja_settings()
        qsettings.beginGroup('preferences')
        qsettings.beginGroup('editor')
        self._checkShowMinimap.setChecked(settings.SHOW_MINIMAP)
        self._spinMaxOpacity.setValue(settings.MINIMAP_MAX_OPACITY * 100)
        self._spinMinOpacity.setValue(settings.MINIMAP_MIN_OPACITY * 100)
        self._spinSize.setValue(settings.SIZE_PROPORTION * 100)
        btnText = ', '.join(self._font.toString().split(',')[0:2])
        self._btnEditorFont.setText(btnText)
        self._listScheme.clear()
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
        qsettings.endGroup()
        qsettings.endGroup()

        #Signals
        self.connect(self._btnEditorFont,
            SIGNAL("clicked()"), self._load_editor_font)
        self.connect(self._listScheme, SIGNAL("itemSelectionChanged()"),
            self._preview_style)
        self.connect(self._preferences, SIGNAL("savePreferences()"), self.save)

    def hideEvent(self, event):
        super(EditorGeneral, self).hideEvent(event)
        resources.CUSTOM_SCHEME = self.original_style
        for editorWidget in self._modified_editors:
            try:
                editorWidget.restyle(editorWidget.lang)
            except RuntimeError:
                print 'the editor has been removed'

    def _preview_style(self):
        scheme = self._listScheme.currentItem().text()
        if scheme == self.current_scheme:
            return
        main_container = IDE.get_service('main_container')
        if not main_container:
            return
        editorWidget = main_container.get_current_editor()
        if editorWidget is not None:
            resources.CUSTOM_SCHEME = self._schemes.get(scheme,
                resources.COLOR_SCHEME)
            editorWidget.restyle(editorWidget.lang)
            self._modified_editors.append(editorWidget)
        self.current_scheme = scheme

    def _load_editor_font(self):
        try:
            font, ok = QFontDialog.getFont(self._font, self)
            if ok:
                self._font = font
                btnText = ', '.join(self._font.toString().split(',')[0:2])
                self._btnEditorFont.setText(btnText)
        except:
            QMessageBox.warning(self,
                translations.TR_PREFERENCES_EDITOR_GENERAL_FONT_MESSAGE_TITLE,
                translations.TR_PREFERENCES_EDITOR_GENERAL_FONT_MESSAGE_BODY)

    def save(self):
        qsettings = IDE.ninja_settings()
        settings.FONT = self._font
        qsettings.setValue('preferences/editor/font', settings.FONT)
        settings.SHOW_MINIMAP = self._checkShowMinimap.isChecked()
        settings.MINIMAP_MAX_OPACITY = self._spinMaxOpacity.value() / 100.0
        settings.MINIMAP_MIN_OPACITY = self._spinMinOpacity.value() / 100.0
        settings.SIZE_PROPORTION = self._spinSize.value() / 100.0
        qsettings.setValue('preferences/editor/minimapMaxOpacity',
            settings.MINIMAP_MAX_OPACITY)
        qsettings.setValue('preferences/editor/minimapMinOpacity',
            settings.MINIMAP_MIN_OPACITY)
        qsettings.setValue('preferences/editor/minimapSizeProportion',
            settings.SIZE_PROPORTION)
        qsettings.setValue('preferences/editor/minimapShow',
            settings.SHOW_MINIMAP)
        scheme = self._listScheme.currentItem().text()
        resources.CUSTOM_SCHEME = self._schemes.get(scheme,
            resources.COLOR_SCHEME)
        qsettings.setValue('preferences/editor/scheme', scheme)


preferences.Preferences.register_configuration('EDITOR', EditorGeneral,
    translations.TR_PREFERENCES_EDITOR_GENERAL, preferences.SECTIONS['EDITOR'])