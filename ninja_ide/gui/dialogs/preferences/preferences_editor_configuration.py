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
from PyQt4.QtGui import QGridLayout
from PyQt4.QtGui import QSpacerItem
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QSpinBox
from PyQt4.QtGui import QSizePolicy
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL

from ninja_ide import translations
from ninja_ide.core import settings
from ninja_ide.gui.ide import IDE
from ninja_ide.gui.dialogs.preferences import preferences


class EditorConfiguration(QWidget):

    def __init__(self, parent):
        super(EditorConfiguration, self).__init__()
        self._preferences = parent
        vbox = QVBoxLayout(self)

        #Indentation
        groupBoxFeatures = QGroupBox(
            translations.TR_PREFERENCES_EDITOR_CONFIG_FEATURES)
        formFeatures = QGridLayout(groupBoxFeatures)
        formFeatures.addWidget(QLabel(
            translations.TR_PREFERENCES_EDITOR_CONFIG_INDENTATION),
            1, 0, Qt.AlignRight)
        self._spin = QSpinBox()
        self._spin.setAlignment(Qt.AlignRight)
        self._spin.setMinimum(1)
        self._spin.setValue(settings.INDENT)
        formFeatures.addWidget(self._spin, 1, 1, alignment=Qt.AlignTop)
        self._checkUseTabs = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_CONFIG_USE_TABS)
        self._checkUseTabs.setChecked(settings.USE_TABS)
        self.connect(self._checkUseTabs, SIGNAL("stateChanged(int)"),
            self._change_tab_spaces)
        formFeatures.addWidget(self._checkUseTabs, 1, 2, alignment=Qt.AlignTop)
        if settings.USE_TABS:
            self._spin.setSuffix(
                translations.TR_PREFERENCES_EDITOR_CONFIG_TAB_SIZE)
        else:
            self._spin.setSuffix(
                translations.TR_PREFERENCES_EDITOR_CONFIG_SPACES)
        #Margin Line
        formFeatures.addWidget(QLabel(
            translations.TR_PREFERENCES_EDITOR_CONFIG_MARGIN_LINE), 2, 0,
            Qt.AlignRight)
        self._spinMargin = QSpinBox()
        self._spinMargin.setMaximum(200)
        self._spinMargin.setValue(settings.MARGIN_LINE)
        formFeatures.addWidget(self._spinMargin, 2, 1, alignment=Qt.AlignTop)
        self._checkShowMargin = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_CONFIG_SHOW_MARGIN_LINE)
        self._checkShowMargin.setChecked(settings.SHOW_MARGIN_LINE)
        formFeatures.addWidget(self._checkShowMargin, 2, 2,
            alignment=Qt.AlignTop)
        #End of line
        self._checkEndOfLine = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_CONFIG_END_OF_LINE)
        self._checkEndOfLine.setChecked(settings.USE_PLATFORM_END_OF_LINE)
        formFeatures.addWidget(self._checkEndOfLine, 3, 1,
            alignment=Qt.AlignTop)
        #Find Errors
        self._checkHighlightLine = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_CONFIG_ERROR_HIGHLIGHTING)
        self._checkHighlightLine.setChecked(settings.UNDERLINE_NOT_BACKGROUND)
        formFeatures.addWidget(self._checkHighlightLine, 4, 1, 1, 2,
            alignment=Qt.AlignTop)
        self._checkErrors = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_CONFIG_FIND_ERRORS)
        self._checkErrors.setChecked(settings.FIND_ERRORS)
        formFeatures.addWidget(self._checkErrors, 5, 1, 1, 2,
            alignment=Qt.AlignTop)
        self.connect(self._checkErrors, SIGNAL("stateChanged(int)"),
            self._disable_show_errors)
        self._showErrorsOnLine = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_CONFIG_SHOW_TOOLTIP_ERRORS)
        self._showErrorsOnLine.setChecked(settings.ERRORS_HIGHLIGHT_LINE)
        self.connect(self._showErrorsOnLine, SIGNAL("stateChanged(int)"),
            self._enable_errors_inline)
        formFeatures.addWidget(self._showErrorsOnLine, 6, 2, 1, 1, Qt.AlignTop)
        #Find Check Style
        self._checkStyle = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_CONFIG_SHOW_PEP8)
        self._checkStyle.setChecked(settings.CHECK_STYLE)
        formFeatures.addWidget(self._checkStyle, 7, 1, 1, 2,
            alignment=Qt.AlignTop)
        self.connect(self._checkStyle, SIGNAL("stateChanged(int)"),
            self._disable_check_style)
        self._checkStyleOnLine = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_CONFIG_SHOW_TOOLTIP_PEP8)
        self._checkStyleOnLine.setChecked(settings.CHECK_HIGHLIGHT_LINE)
        self.connect(self._checkStyleOnLine, SIGNAL("stateChanged(int)"),
            self._enable_check_inline)
        formFeatures.addWidget(self._checkStyleOnLine, 8, 2, 1, 1, Qt.AlignTop)
        # Python3 Migration
        self._showMigrationTips = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_CONFIG_SHOW_MIGRATION)
        self._showMigrationTips.setChecked(settings.SHOW_MIGRATION_TIPS)
        formFeatures.addWidget(self._showMigrationTips, 9, 1, 1, 2,
            Qt.AlignTop)
        #Center On Scroll
        self._checkCenterScroll = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_CONFIG_CENTER_SCROLL)
        self._checkCenterScroll.setChecked(settings.CENTER_ON_SCROLL)
        formFeatures.addWidget(self._checkCenterScroll, 10, 1, 1, 2,
            alignment=Qt.AlignTop)
        #Remove Trailing Spaces add Last empty line automatically
        self._checkTrailing = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_CONFIG_REMOVE_TRAILING)
        self._checkTrailing.setChecked(settings.REMOVE_TRAILING_SPACES)
        formFeatures.addWidget(self._checkTrailing, 11, 1, 1, 2,
            alignment=Qt.AlignTop)
        #Show Tabs and Spaces
        self._checkShowSpaces = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_CONFIG_SHOW_TABS_AND_SPACES)
        self._checkShowSpaces.setChecked(settings.SHOW_TABS_AND_SPACES)
        formFeatures.addWidget(self._checkShowSpaces, 12, 1, 1, 2,
            alignment=Qt.AlignTop)
        self._allowWordWrap = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_CONFIG_WORD_WRAP)
        self._allowWordWrap.setChecked(settings.ALLOW_WORD_WRAP)
        formFeatures.addWidget(self._allowWordWrap, 13, 1, 1, 2,
            alignment=Qt.AlignTop)
        self._checkForDocstrings = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_CONFIG_CHECK_FOR_DOCSTRINGS)
        self._checkForDocstrings.setChecked(settings.CHECK_FOR_DOCSTRINGS)
        formFeatures.addWidget(self._checkForDocstrings, 14, 1, 1, 2,
            alignment=Qt.AlignTop)

        vbox.addWidget(groupBoxFeatures)
        vbox.addItem(QSpacerItem(0, 10, QSizePolicy.Expanding,
            QSizePolicy.Expanding))

        self.connect(self._preferences, SIGNAL("savePreferences()"), self.save)

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
            self._spin.setSuffix(
                translations.TR_PREFERENCES_EDITOR_CONFIG_SPACES)
        else:
            self._spin.setSuffix(
                translations.TR_PREFERENCES_EDITOR_CONFIG_TAB_SIZE)

    def save(self):
        qsettings = IDE.ninja_settings()
        qsettings.setValue('preferences/editor/indent', self._spin.value())
        settings.INDENT = self._spin.value()
        endOfLine = self._checkEndOfLine.isChecked()
        qsettings.setValue('preferences/editor/platformEndOfLine', endOfLine)
        settings.USE_PLATFORM_END_OF_LINE = endOfLine
        margin_line = self._spinMargin.value()
        qsettings.setValue('preferences/editor/marginLine', margin_line)
        settings.MARGIN_LINE = margin_line
        settings.pep8mod_update_margin_line_length(margin_line)
        qsettings.setValue('preferences/editor/showMarginLine',
            self._checkShowMargin.isChecked())
        settings.SHOW_MARGIN_LINE = self._checkShowMargin.isChecked()
        settings.UNDERLINE_NOT_BACKGROUND = \
            self._checkHighlightLine.isChecked()
        qsettings.setValue('preferences/editor/errorsUnderlineBackground',
            settings.UNDERLINE_NOT_BACKGROUND)
        qsettings.setValue('preferences/editor/errors',
            self._checkErrors.isChecked())
        settings.FIND_ERRORS = self._checkErrors.isChecked()
        qsettings.setValue('preferences/editor/errorsInLine',
            self._showErrorsOnLine.isChecked())
        settings.ERRORS_HIGHLIGHT_LINE = self._showErrorsOnLine.isChecked()
        qsettings.setValue('preferences/editor/checkStyle',
            self._checkStyle.isChecked())
        settings.CHECK_STYLE = self._checkStyle.isChecked()
        qsettings.setValue('preferences/editor/showMigrationTips',
            self._showMigrationTips.isChecked())
        settings.SHOW_MIGRATION_TIPS = self._showMigrationTips.isChecked()
        qsettings.setValue('preferences/editor/checkStyleInline',
            self._checkStyleOnLine.isChecked())
        settings.CHECK_HIGHLIGHT_LINE = self._checkStyleOnLine.isChecked()
        qsettings.setValue('preferences/editor/centerOnScroll',
            self._checkCenterScroll.isChecked())
        settings.CENTER_ON_SCROLL = self._checkCenterScroll.isChecked()
        qsettings.setValue('preferences/editor/removeTrailingSpaces',
            self._checkTrailing.isChecked())
        settings.REMOVE_TRAILING_SPACES = self._checkTrailing.isChecked()
        qsettings.setValue('preferences/editor/showTabsAndSpaces',
            self._checkShowSpaces.isChecked())
        settings.SHOW_TABS_AND_SPACES = self._checkShowSpaces.isChecked()
        qsettings.setValue('preferences/editor/useTabs',
            self._checkUseTabs.isChecked())
        settings.USE_TABS = self._checkUseTabs.isChecked()
        qsettings.setValue('preferences/editor/allowWordWrap',
            self._allowWordWrap.isChecked())
        settings.ALLOW_WORD_WRAP = self._allowWordWrap.isChecked()
        qsettings.setValue('preferences/editor/checkForDocstrings',
            self._checkForDocstrings.isChecked())
        settings.CHECK_FOR_DOCSTRINGS = self._checkForDocstrings.isChecked()

        #main_container = self._ide.get_service('main_container')
        #if main_container:
            #main_container.reset_editor_flags()
            #main_container.call_editors_function("set_tab_usage")
        #if settings.USE_TABS:
            #settings.pep8mod_add_ignore("W191")
        #else:
            #settings.pep8mod_remove_ignore("W191")
        #settings.pep8mod_refresh_checks()
        #main_container.MainContainer().update_editor_margin_line()


preferences.Preferences.register_configuration('EDITOR', EditorConfiguration,
    translations.TR_PREFERENCES_EDITOR_CONFIGURATION,
    weight=0, subsection='CONFIGURATION')