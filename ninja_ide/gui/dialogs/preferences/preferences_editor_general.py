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

from PyQt5.QtWidgets import (
    QWidget,
    QComboBox,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QCheckBox,
    QGridLayout,
    QMessageBox,
    QListWidget,
    QListView,
    QLabel,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QFontDialog,
    QFontComboBox,
    QPushButton
)
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtCore import (
    QAbstractListModel,
    Qt,
    QSize
)

from ninja_ide import resources
from ninja_ide import translations
from ninja_ide.core import settings
from ninja_ide.core.file_handling import file_manager
from ninja_ide.gui.ide import IDE
from ninja_ide.gui.dialogs.preferences import preferences
# from ninja_ide.gui.dialogs.preferences import preferences_editor_scheme_designer
from ninja_ide.tools import json_manager


class ListModelScheme(QAbstractListModel):

    def __init__(self, schemes):
        super().__init__()
        self.__schemes = schemes
        self._font = None

    def rowCount(self, index):
        return len(self.__schemes)

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self.__schemes[index.row()].name
        elif role == Qt.BackgroundColorRole:
            return QColor(self.__schemes[index.row()].color)
        elif role == Qt.ForegroundRole:
            return QColor(self.__schemes[0].color)
        elif role == Qt.FontRole:
            return self._font

    def set_font(self, font):
        self._font = font


class EditorGeneral(QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self._preferences = parent
        vbox = QVBoxLayout(self)
        self._font = settings.FONT

        # Group widgets
        group_typo = QGroupBox(
            translations.TR_PREFERENCES_EDITOR_GENERAL_TYPOGRAPHY)
        group_scheme = QGroupBox("Editor Color Scheme")

        # Font settings
        grid_typo = QGridLayout(group_typo)
        self._btn_editor_font = QPushButton('')
        grid_typo.addWidget(QLabel(
            translations.TR_PREFERENCES_EDITOR_GENERAL_EDITOR_FONT), 0, 0)
        grid_typo.addWidget(self._btn_editor_font, 0, 1)
        self._check_font_antialiasing = QCheckBox("Antialiasing")
        grid_typo.addWidget(self._check_font_antialiasing, 1, 0)

        # Scheme settings
        box = QVBoxLayout(group_scheme)
        self._combo_themes = QComboBox()
        box.addWidget(self._combo_themes)
        schemes = json_manager.load_editor_schemes()
        for scheme_name, colors in schemes.items():
            self._combo_themes.addItem(scheme_name, colors)
        self.__current_scheme = settings.EDITOR_SCHEME

        # self._list_view_scheme = QListView()
        # schemes = json_manager.load_editor_schemes()
        # from collections import namedtuple
        # CategoryEntry = namedtuple('CategoryEntry', 'name color')
        # list_of_categories = []
        # for scheme_name, categories in schemes.items():
        #     for category_name in categories.keys():
        #         category = CategoryEntry(
        #             category_name,
        #             categories[category_name]['color']
        #         )
        #         list_of_categories.append(category)

        # model = ListModelScheme(list_of_categories)
        # model.set_font(self._font)
        # self._list_view_scheme.setModel(model)
        # box.addWidget(self._list_view_scheme)
        # Add group widgets
        vbox.addWidget(group_typo)
        vbox.addWidget(group_scheme)
        vbox.addItem(
            QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding))
        # Initial Settings
        btn_text = ', '.join(self._font.toString().split(',')[0:2])
        self._btn_editor_font.setText(btn_text)
        self._check_font_antialiasing.setChecked(settings.FONT_ANTIALIASING)
        self._combo_themes.setCurrentText(settings.EDITOR_SCHEME)
        # Connections
        self._btn_editor_font.clicked.connect(self._load_editor_font)
        self._preferences.savePreferences.connect(self._save)

    def _load_editor_font(self):
        font, ok = QFontDialog.getFont(self._font, self)
        if ok:
            self._font = font
            btn_text = ', '.join(self._font.toString().split(',')[0:2])
            self._btn_editor_font.setText(btn_text)

    def _save(self):
        qsettings = IDE.editor_settings()

        settings.FONT = self._font
        qsettings.setValue("editor/general/default_font", settings.FONT)
        settings.FONT_ANTIALIASING = self._check_font_antialiasing.isChecked()
        qsettings.setValue("editor/general/font_antialiasing",
                           settings.FONT_ANTIALIASING)
        settings.EDITOR_SCHEME = self._combo_themes.currentText()
        qsettings.setValue("editor/general/scheme",
                           settings.EDITOR_SCHEME)

        scheme = self._combo_themes.currentText()
        if scheme != self.__current_scheme:
            index = self._combo_themes.currentIndex()
            colors = self._combo_themes.itemData(index)
            resources.COLOR_SCHEME = colors
            main = IDE.get_service("main_container")
            main.restyle_editor()


'''class EditorGeneral(QWidget):
    """EditorGeneral widget class."""

    def __init__(self, parent):
        super(EditorGeneral, self).__init__()
        self._preferences, vbox = parent, QVBoxclass EditorGeneral(QWidget):
    """EditorGeneral widget class."""

    def __init__(self, parent):
        super(EditorGeneral, self).__init__()
        self._preferences, vbox = parent, QVBoxLayout(self)
        self.original_style = copy.copy(resources.CUSTOM_SCHEME)
        self.current_scheme, self._modified_editors = 'default', []
        self._font = settings.FONT

        groupBoxMini = QGroupBox(
            translations.TR_PREFERENCES_EDITOR_GENERAL_MINIMAP)
        groupBoxDocMap = QGroupBox(
            translations.TR_PREFERENCES_EDITOR_GENERAL_DOCMAP)
        groupBoxTypo = QGroupBox(
            translations.TR_PREFERENCES_EDITOR_GENERAL_TYPOGRAPHY)
        groupBoxScheme = QGroupBox(
            translations.TR_PREFERENCES_EDITOR_GENERAL_SCHEME)

        boxMiniAndDocMap = QHBoxLayout()
        # Minimap
        formMini = QGridLayout(groupBoxMini)
        formMini.setContentsMargins(5, 15, 5, 5)
        self._checkShowMinimap = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_GENERAL_ENABLE_MINIMAP)
        self._spinMaxOpacity = QSpinBox()
        self._spinMaxOpacity.setRange(0, 100)
        self._spinMaxOpacity.setSuffix("% Max.")
        self._spinMinOpacity = QSpinBox()
        self._spinMinOpacity.setRange(0, 100)
        self._spinMinOpacity.setSuffix("% Min.")
        self._spinSize = QSpinBox()
        self._spinSize.setMaximum(100)
        self._spinSize.setMinimum(0)
        self._spinSize.setSuffix(
            translations.TR_PREFERENCES_EDITOR_GENERAL_AREA_MINIMAP)
        formMini.addWidget(self._checkShowMinimap, 0, 1)
        formMini.addWidget(QLabel(
            translations.TR_PREFERENCES_EDITOR_GENERAL_SIZE_MINIMAP), 1, 0,
            Qt.AlignRight)
        formMini.addWidget(self._spinSize, 1, 1)
        formMini.addWidget(QLabel(
            translations.TR_PREFERENCES_EDITOR_GENERAL_OPACITY), 2, 0,
            Qt.AlignRight)
        formMini.addWidget(self._spinMinOpacity, 2, 1)
        formMini.addWidget(self._spinMaxOpacity, 2, 2)
        boxMiniAndDocMap.addWidget(groupBoxMini)
        # Document Map
        formDocMap = QGridLayout(groupBoxDocMap)
        self._checkShowDocMap = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_GENERAL_ENABLE_DOCMAP)
        self._checkShowSlider = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_GENERAL_DOCMAP_SLIDER)
        self._checkOriginalScroll = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_GENERAL_ORIGINAL_SCROLLBAR)
        self._checkCurrentLine = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_GENERAL_DOCMAP_CURRENT_LINE)
        self._checkSearchLines = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_GENERAL_DOCMAP_SEARCH_LINES)
        self._spinWidth = QSpinBox()
        self._spinWidth.setRange(5, 40)
        formDocMap.addWidget(self._checkShowDocMap, 0, 0)
        formDocMap.addWidget(self._checkShowSlider, 0, 1)
        formDocMap.addWidget(self._checkOriginalScroll, 0, 2)
        formDocMap.addWidget(self._checkCurrentLine, 1, 0)
        formDocMap.addWidget(self._checkSearchLines, 1, 1)
        formDocMap.addWidget(QLabel(
            translations.TR_PREFERENCES_EDITOR_GENERAL_DOCMAP_WIDTH), 2, 0)
        formDocMap.addWidget(self._spinWidth, 2, 1)
        boxMiniAndDocMap.addWidget(groupBoxDocMap)
        # Typo
        gridTypo = QGridLayout(groupBoxTypo)
        gridTypo.setContentsMargins(5, 15, 5, 5)
        self._btnEditorFont = QPushButton('')
        gridTypo.addWidget(QLabel(
            translations.TR_PREFERENCES_EDITOR_GENERAL_EDITOR_FONT), 0, 0,
            Qt.AlignRight)
        gridTypo.addWidget(self._btnEditorFont, 0, 1)
        # Scheme
        vboxScheme = QVBoxLayout(groupBoxScheme)
        vboxScheme.setContentsMargins(5, 15, 5, 5)
        self._listScheme = QListWidget()
        vboxScheme.addWidget(self._listScheme)
        hbox = QHBoxLayout()
        btnDownload = QPushButton(
            translations.TR_PREFERENCES_EDITOR_DOWNLOAD_SCHEME)
        btnDownload.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        btnDownload.clicked.connect(self._open_schemes_manager)
        hbox.addWidget(btnDownload)
        btnAdd = QPushButton(QIcon(":img/add"),
                             translations.TR_EDITOR_CREATE_SCHEME)
        btnAdd.setIconSize(QSize(16, 16))
        btnAdd.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        btnAdd.clicked.connect(self._open_schemes_designer)
        btnRemove = QPushButton(QIcon(":img/delete"),
                                translations.TR_EDITOR_REMOVE_SCHEME)
        btnRemove.setIconSize(QSize(16, 16))
        btnRemove.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        btnRemove.clicked.connect(self._remove_scheme)
        hbox.addSpacerItem(QSpacerItem(1, 0, QSizePolicy.Expanding))
        hbox.addWidget(btnAdd)
        hbox.addWidget(btnRemove)
        vboxScheme.addLayout(hbox)

        vbox.addLayout(boxMiniAndDocMap)
        vbox.addWidget(groupBoxTypo)
        vbox.addWidget(groupBoxScheme)

        # Settings
        qsettings = IDE.ninja_settings()
        qsettings.beginGroup('preferences')
        qsettings.beginGroup('editor')
        self._checkShowMinimap.setChecked(settings.SHOW_MINIMAP)
        if settings.IS_MAC_OS:
            self._spinMinOpacity.setValue(100)
            self._spinMaxOpacity.setValue(100)
            self._spinMinOpacity.setDisabled(True)
            self._spinMaxOpacity.setDisabled(True)
        else:
            self._spinMinOpacity.setValue(settings.MINIMAP_MIN_OPACITY * 100)
            self._spinMaxOpacity.setValue(settings.MINIMAP_MAX_OPACITY * 100)
        self._checkShowDocMap.setChecked(settings.SHOW_DOCMAP)
        self._checkShowSlider.setChecked(settings.DOCMAP_SLIDER)
        self._checkOriginalScroll.setChecked(settings.EDITOR_SCROLLBAR)
        self._checkCurrentLine.setChecked(settings.DOCMAP_CURRENT_LINE)
        self._checkSearchLines.setChecked(settings.DOCMAP_SEARCH_LINES)
        self._spinWidth.setValue(settings.DOCMAP_WIDTH)
        self._spinSize.setValue(settings.SIZE_PROPORTION * 100)
        btnText = ', '.join(self._font.toString().split(',')[0:2])
        self._btnEditorFont.setText(btnText)
        self._listScheme.clear()
        self._listScheme.addItem('default')
        # self._schemes = json_manager.load_editor_skins()
        self._schemes = []
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

        # Signals
        self._btnEditorFont.clicked.connect(self._load_editor_font)
        self._listScheme.itemSelectionChanged.connect(self._preview_style)
        self._preferences.savePreferences.connect(self.save)

    def _open_schemes_manager(self):
        ninjaide = IDE.get_service("ide")
        ninjaide.show_schemes()
        # refresh schemes

    def _open_schemes_designer(self):
        name = self._listScheme.currentItem().text()
        scheme = self._schemes.get(name, resources.COLOR_SCHEME)
        designer = preferences_editor_scheme_designer.EditorSchemeDesigner(
            scheme, self)
        designer.exec_()
        if designer.saved:
            scheme_name = designer.line_name.text()
            scheme = designer.original_style
            self._schemes[scheme_name] = scheme
            result = self._listScheme.findItems(scheme_name, Qt.MatchExactly)
            if not result:
                self._listScheme.addItem(scheme_name)

    def _remove_scheme(self):
        name = self._listScheme.currentItem().text()
        fileName = ('{0}.color'.format(
            file_manager.create_path(resources.EDITOR_SKINS, name)))
        file_manager.delete_file(fileName)
        item = self._listScheme.takeItem(self._listScheme.currentRow())
        del item

    def hideEvent(self, event):
        super(EditorGeneral, self).hideEvent(event)
        resources.CUSTOM_SCHEME = self.original_style
        for editorWidget in self._modified_editors:
            try:
                editorWidget.restyle(editorWidget.lang)
            except RuntimeError:
                print('the editor has been removed')

    def _preview_style(self):
        scheme = self._listScheme.currentItem().text()
        if scheme == self.current_scheme:
            return
        main_container = IDE.get_service('main_container')
        if not main_container:
            return
        editorWidget = main_container.get_current_editor()
        if editorWidget is not None:
            resources.CUSTOM_SCHEME = self._schemes.get(
                scheme,
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
            QMessageBox.warning(
                self,
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
        settings.SHOW_DOCMAP = self._checkShowDocMap.isChecked()
        settings.DOCMAP_SLIDER = self._checkShowSlider.isChecked()
        settings.EDITOR_SCROLLBAR = self._checkOriginalScroll.isChecked()
        settings.DOCMAP_CURRENT_LINE = self._checkCurrentLine.isChecked()
        settings.DOCMAP_SEARCH_LINES = self._checkSearchLines.isChecked()
        settings.DOCMAP_WIDTH = self._spinWidth.value()
        qsettings.setValue('preferences/editor/docmapShow',
                           settings.SHOW_DOCMAP)
        qsettings.setValue('preferences/editor/docmapSlider',
                           settings.DOCMAP_SLIDER)
        qsettings.setValue('preferences/editor/editorScrollBar',
                           settings.EDITOR_SCROLLBAR)
        qsettings.setValue('preferences/editor/docmapCurrentLine',
                           settings.DOCMAP_CURRENT_LINE)
        qsettings.setValue('preferences/editor/docmapSearchLines',
                           settings.DOCMAP_SEARCH_LINES)
        qsettings.setValue('preferences/editor/docmapWidth',
                           settings.DOCMAP_WIDTH)
        scheme = self._listScheme.currentItem().text()
        resources.CUSTOM_SCHEME = self._schemes.get(scheme,
                                                    resources.COLOR_SCHEME)
        qsettings.setValue('preferences/editor/scheme', scheme)
Layout(self)
        self.original_style = copy.copy(resources.CUSTOM_SCHEME)
        self.current_scheme, self._modified_editors = 'default', []
        self._font = settings.FONT

        groupBoxMini = QGroupBox(
            translations.TR_PREFERENCES_EDITOR_GENERAL_MINIMAP)
        groupBoxDocMap = QGroupBox(
            translations.TR_PREFERENCES_EDITOR_GENERAL_DOCMAP)
        groupBoxTypo = QGroupBox(
            translations.TR_PREFERENCES_EDITOR_GENERAL_TYPOGRAPHY)
        groupBoxScheme = QGroupBox(
            translations.TR_PREFERENCES_EDITOR_GENERAL_SCHEME)

        boxMiniAndDocMap = QHBoxLayout()
        # Minimap
        formMini = QGridLayout(groupBoxMini)
        formMini.setContentsMargins(5, 15, 5, 5)
        self._checkShowMinimap = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_GENERAL_ENABLE_MINIMAP)
        self._spinMaxOpacity = QSpinBox()
        self._spinMaxOpacity.setRange(0, 100)
        self._spinMaxOpacity.setSuffix("% Max.")
        self._spinMinOpacity = QSpinBox()
        self._spinMinOpacity.setRange(0, 100)
        self._spinMinOpacity.setSuffix("% Min.")
        self._spinSize = QSpinBox()
        self._spinSize.setMaximum(100)
        self._spinSize.setMinimum(0)
        self._spinSize.setSuffix(
            translations.TR_PREFERENCES_EDITOR_GENERAL_AREA_MINIMAP)
        formMini.addWidget(self._checkShowMinimap, 0, 1)
        formMini.addWidget(QLabel(
            translations.TR_PREFERENCES_EDITOR_GENERAL_SIZE_MINIMAP), 1, 0,
            Qt.AlignRight)
        formMini.addWidget(self._spinSize, 1, 1)
        formMini.addWidget(QLabel(
            translations.TR_PREFERENCES_EDITOR_GENERAL_OPACITY), 2, 0,
            Qt.AlignRight)
        formMini.addWidget(self._spinMinOpacity, 2, 1)
        formMini.addWidget(self._spinMaxOpacity, 2, 2)
        boxMiniAndDocMap.addWidget(groupBoxMini)
        # Document Map
        formDocMap = QGridLayout(groupBoxDocMap)
        self._checkShowDocMap = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_GENERAL_ENABLE_DOCMAP)
        self._checkShowSlider = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_GENERAL_DOCMAP_SLIDER)
        self._checkOriginalScroll = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_GENERAL_ORIGINAL_SCROLLBAR)
        self._checkCurrentLine = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_GENERAL_DOCMAP_CURRENT_LINE)
        self._checkSearchLines = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_GENERAL_DOCMAP_SEARCH_LINES)
        self._spinWidth = QSpinBox()
        self._spinWidth.setRange(5, 40)
        formDocMap.addWidget(self._checkShowDocMap, 0, 0)
        formDocMap.addWidget(self._checkShowSlider, 0, 1)
        formDocMap.addWidget(self._checkOriginalScroll, 0, 2)
        formDocMap.addWidget(self._checkCurrentLine, 1, 0)
        formDocMap.addWidget(self._checkSearchLines, 1, 1)
        formDocMap.addWidget(QLabel(
            translations.TR_PREFERENCES_EDITOR_GENERAL_DOCMAP_WIDTH), 2, 0)
        formDocMap.addWidget(self._spinWidth, 2, 1)
        boxMiniAndDocMap.addWidget(groupBoxDocMap)
        # Typo
        gridTypo = QGridLayout(groupBoxTypo)
        gridTypo.setContentsMargins(5, 15, 5, 5)
        self._btnEditorFont = QPushButton('')
        gridTypo.addWidget(QLabel(
            translations.TR_PREFERENCES_EDITOR_GENERAL_EDITOR_FONT), 0, 0,
            Qt.AlignRight)
        gridTypo.addWidget(self._btnEditorFont, 0, 1)
        # Scheme
        vboxScheme = QVBoxLayout(groupBoxScheme)
        vboxScheme.setContentsMargins(5, 15, 5, 5)
        self._listScheme = QListWidget()
        vboxScheme.addWidget(self._listScheme)
        hbox = QHBoxLayout()
        btnDownload = QPushButton(
            translations.TR_PREFERENCES_EDITOR_DOWNLOAD_SCHEME)
        btnDownload.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        btnDownload.clicked.connect(self._open_schemes_manager)
        hbox.addWidget(btnDownload)
        btnAdd = QPushButton(QIcon(":img/add"),
                             translations.TR_EDITOR_CREATE_SCHEME)
        btnAdd.setIconSize(QSize(16, 16))
        btnAdd.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        btnAdd.clicked.connect(self._open_schemes_designer)
        btnRemove = QPushButton(QIcon(":img/delete"),
                                translations.TR_EDITOR_REMOVE_SCHEME)
        btnRemove.setIconSize(QSize(16, 16))
        btnRemove.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        btnRemove.clicked.connect(self._remove_scheme)
        hbox.addSpacerItem(QSpacerItem(1, 0, QSizePolicy.Expanding))
        hbox.addWidget(btnAdd)
        hbox.addWidget(btnRemove)
        vboxScheme.addLayout(hbox)

        vbox.addLayout(boxMiniAndDocMap)
        vbox.addWidget(groupBoxTypo)
        vbox.addWidget(groupBoxScheme)

        # Settings
        qsettings = IDE.ninja_settings()
        qsettings.beginGroup('preferences')
        qsettings.beginGroup('editor')
        self._checkShowMinimap.setChecked(settings.SHOW_MINIMAP)
        if settings.IS_MAC_OS:
            self._spinMinOpacity.setValue(100)
            self._spinMaxOpacity.setValue(100)
            self._spinMinOpacity.setDisabled(True)
            self._spinMaxOpacity.setDisabled(True)
        else:
            self._spinMinOpacity.setValue(settings.MINIMAP_MIN_OPACITY * 100)
            self._spinMaxOpacity.setValue(settings.MINIMAP_MAX_OPACITY * 100)
        self._checkShowDocMap.setChecked(settings.SHOW_DOCMAP)
        self._checkShowSlider.setChecked(settings.DOCMAP_SLIDER)
        self._checkOriginalScroll.setChecked(settings.EDITOR_SCROLLBAR)
        self._checkCurrentLine.setChecked(settings.DOCMAP_CURRENT_LINE)
        self._checkSearchLines.setChecked(settings.DOCMAP_SEARCH_LINES)
        self._spinWidth.setValue(settings.DOCMAP_WIDTH)
        self._spinSize.setValue(settings.SIZE_PROPORTION * 100)
        btnText = ', '.join(self._font.toString().split(',')[0:2])
        self._btnEditorFont.setText(btnText)
        self._listScheme.clear()
        self._listScheme.addItem('default')
        # self._schemes = json_manager.load_editor_skins()
        self._schemes = []
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

        # Signals
        self._btnEditorFont.clicked.connect(self._load_editor_font)
        self._listScheme.itemSelectionChanged.connect(self._preview_style)
        self._preferences.savePreferences.connect(self.save)

    def _open_schemes_manager(self):
        ninjaide = IDE.get_service("ide")
        ninjaide.show_schemes()
        # refresh schemes

    def _open_schemes_designer(self):
        name = self._listScheme.currentItem().text()
        scheme = self._schemes.get(name, resources.COLOR_SCHEME)
        designer = preferences_editor_scheme_designer.EditorSchemeDesigner(
            scheme, self)
        designer.exec_()
        if designer.saved:
            scheme_name = designer.line_name.text()
            scheme = designer.original_style
            self._schemes[scheme_name] = scheme
            result = self._listScheme.findItems(scheme_name, Qt.MatchExactly)
            if not result:
                self._listScheme.addItem(scheme_name)

    def _remove_scheme(self):
        name = self._listScheme.currentItem().text()
        fileName = ('{0}.color'.format(
            file_manager.create_path(resources.EDITOR_SKINS, name)))
        file_manager.delete_file(fileName)
        item = self._listScheme.takeItem(self._listScheme.currentRow())
        del item

    def hideEvent(self, event):
        super(EditorGeneral, self).hideEvent(event)
        resources.CUSTOM_SCHEME = self.original_style
        for editorWidget in self._modified_editors:
            try:
                editorWidget.restyle(editorWidget.lang)
            except RuntimeError:
                print('the editor has been removed')

    def _preview_style(self):
        scheme = self._listScheme.currentItem().text()
        if scheme == self.current_scheme:
            return
        main_container = IDE.get_service('main_container')
        if not main_container:
            return
        editorWidget = main_container.get_current_editor()
        if editorWidget is not None:
            resources.CUSTOM_SCHEME = self._schemes.get(
                scheme,
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
            QMessageBox.warning(
                self,
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
        settings.SHOW_DOCMAP = self._checkShowDocMap.isChecked()
        settings.DOCMAP_SLIDER = self._checkShowSlider.isChecked()
        settings.EDITOR_SCROLLBAR = self._checkOriginalScroll.isChecked()
        settings.DOCMAP_CURRENT_LINE = self._checkCurrentLine.isChecked()
        settings.DOCMAP_SEARCH_LINES = self._checkSearchLines.isChecked()
        settings.DOCMAP_WIDTH = self._spinWidth.value()
        qsettings.setValue('preferences/editor/docmapShow',
                           settings.SHOW_DOCMAP)
        qsettings.setValue('preferences/editor/docmapSlider',
                           settings.DOCMAP_SLIDER)
        qsettings.setValue('preferences/editor/editorScrollBar',
                           settings.EDITOR_SCROLLBAR)
        qsettings.setValue('preferences/editor/docmapCurrentLine',
                           settings.DOCMAP_CURRENT_LINE)
        qsettings.setValue('preferences/editor/docmapSearchLines',
                           settings.DOCMAP_SEARCH_LINES)
        qsettings.setValue('preferences/editor/docmapWidth',
                           settings.DOCMAP_WIDTH)
        scheme = self._listScheme.currentItem().text()
        resources.CUSTOM_SCHEME = self._schemes.get(scheme,
                                                    resources.COLOR_SCHEME)
        qsettings.setValue('preferences/editor/scheme', scheme)
'''

preferences.Preferences.register_configuration(
    'EDITOR',
    EditorGeneral,
    translations.TR_PREFERENCES_EDITOR_GENERAL,
    preferences.SECTIONS['EDITOR'])
