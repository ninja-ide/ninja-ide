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
from PyQt4.QtGui import QGridLayout
from PyQt4.QtGui import QSpacerItem
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QSpinBox
from PyQt4.QtGui import QComboBox
from PyQt4.QtGui import QSizePolicy
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL

from ninja_ide import translations
from ninja_ide.core import settings
from ninja_ide.gui.ide import IDE
from ninja_ide.gui.dialogs.preferences import preferences


class EditorConfiguration(QWidget):
    """EditorConfiguration widget class"""

    def __init__(self, parent):
        super(EditorConfiguration, self).__init__()
        self._preferences, vbox = parent, QVBoxLayout(self)

        # groups
        group1 = QGroupBox(translations.TR_PREFERENCES_EDITOR_CONFIG_INDENT)
        group2 = QGroupBox(translations.TR_PREFERENCES_EDITOR_CONFIG_MARGIN)
        group3 = QGroupBox(translations.TR_LINT_DIRTY_TEXT)
        group4 = QGroupBox(translations.TR_PEP8_DIRTY_TEXT)
        group5 = QGroupBox(translations.TR_HIGHLIGHTER_EXTRAS)
        group6 = QGroupBox(translations.TR_TYPING_ASSISTANCE)
        group7 = QGroupBox(translations.TR_DISPLAY_ERRORS)

        # groups container
        container_widget_with_all_preferences = QWidget()
        formFeatures = QGridLayout(container_widget_with_all_preferences)

        # Indentation
        hboxg1 = QHBoxLayout(group1)
        hboxg1.setContentsMargins(5, 15, 5, 5)
        self._spin, self._checkUseTabs = QSpinBox(), QComboBox()
        self._spin.setRange(1, 10)
        self._spin.setValue(settings.INDENT)
        hboxg1.addWidget(self._spin)
        self._checkUseTabs.addItems([
            translations.TR_PREFERENCES_EDITOR_CONFIG_SPACES.capitalize(),
            translations.TR_PREFERENCES_EDITOR_CONFIG_TABS.capitalize()])
        self._checkUseTabs.setCurrentIndex(int(settings.USE_TABS))
        hboxg1.addWidget(self._checkUseTabs)
        formFeatures.addWidget(group1, 0, 0)

        # Margin Line
        hboxg2 = QHBoxLayout(group2)
        hboxg2.setContentsMargins(5, 15, 5, 5)
        self._checkShowMargin = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_CONFIG_SHOW_MARGIN_LINE)
        self._checkShowMargin.setChecked(settings.SHOW_MARGIN_LINE)
        hboxg2.addWidget(self._checkShowMargin)
        self._spinMargin = QSpinBox()
        self._spinMargin.setRange(50, 100)
        self._spinMargin.setSingleStep(2)
        self._spinMargin.setValue(settings.MARGIN_LINE)
        hboxg2.addWidget(self._spinMargin)
        hboxg2.addWidget(QLabel(translations.TR_CHARACTERS))
        formFeatures.addWidget(group2, 0, 1)

        # Display Errors
        hboxDisplay = QHBoxLayout(group7)
        hboxDisplay.setContentsMargins(5, 15, 5, 5)
        self._checkHighlightLine = QComboBox()
        self._checkHighlightLine.addItems([
            translations.TR_PREFERENCES_EDITOR_CONFIG_ERROR_USE_BACKGROUND,
            translations.TR_PREFERENCES_EDITOR_CONFIG_ERROR_USE_UNDERLINE])
        self._checkHighlightLine.setCurrentIndex(
            int(settings.UNDERLINE_NOT_BACKGROUND))
        hboxDisplay.addWidget(self._checkHighlightLine)
        formFeatures.addWidget(group7, 1, 0, 1, 0)

        # Find Lint Errors (highlighter)
        vboxg3 = QVBoxLayout(group3)
        self._checkErrors = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_CONFIG_FIND_ERRORS)
        self._checkErrors.setChecked(settings.FIND_ERRORS)
        self.connect(self._checkErrors, SIGNAL("stateChanged(int)"),
                     self._disable_show_errors)
        self._showErrorsOnLine = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_CONFIG_SHOW_TOOLTIP_ERRORS)
        self._showErrorsOnLine.setChecked(settings.ERRORS_HIGHLIGHT_LINE)
        self.connect(self._showErrorsOnLine, SIGNAL("stateChanged(int)"),
                     self._enable_errors_inline)
        vboxg3.addWidget(self._checkErrors)
        vboxg3.addWidget(self._showErrorsOnLine)
        formFeatures.addWidget(group3, 2, 0)

        # Find PEP8 Errors (highlighter)
        vboxg4 = QVBoxLayout(group4)
        vboxg4.setContentsMargins(5, 15, 5, 5)
        self._checkStyle = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_CONFIG_SHOW_PEP8)
        self._checkStyle.setChecked(settings.CHECK_STYLE)
        self.connect(self._checkStyle, SIGNAL("stateChanged(int)"),
                     self._disable_check_style)
        vboxg4.addWidget(self._checkStyle)
        self._checkStyleOnLine = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_CONFIG_SHOW_TOOLTIP_PEP8)
        self._checkStyleOnLine.setChecked(settings.CHECK_HIGHLIGHT_LINE)
        self.connect(self._checkStyleOnLine, SIGNAL("stateChanged(int)"),
                     self._enable_check_inline)
        vboxg4.addWidget(self._checkStyleOnLine)
        formFeatures.addWidget(group4, 2, 1)

        # Show Python3 Migration, DocStrings and Spaces (highlighter)
        vboxg5 = QVBoxLayout(group5)
        vboxg5.setContentsMargins(5, 15, 5, 5)
        self._showMigrationTips = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_CONFIG_SHOW_MIGRATION)
        self._showMigrationTips.setChecked(settings.SHOW_MIGRATION_TIPS)
        vboxg5.addWidget(self._showMigrationTips)
        self._checkForDocstrings = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_CONFIG_CHECK_FOR_DOCSTRINGS)
        self._checkForDocstrings.setChecked(settings.CHECK_FOR_DOCSTRINGS)
        vboxg5.addWidget(self._checkForDocstrings)
        self._checkShowSpaces = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_CONFIG_SHOW_TABS_AND_SPACES)
        self._checkShowSpaces.setChecked(settings.SHOW_TABS_AND_SPACES)
        vboxg5.addWidget(self._checkShowSpaces)
        self._checkIndentationGuide = QCheckBox(
            translations.TR_SHOW_INDENTATION_GUIDE)
        self._checkIndentationGuide.setChecked(settings.SHOW_INDENTATION_GUIDE)
        vboxg5.addWidget(self._checkIndentationGuide)
        formFeatures.addWidget(group5, 3, 0)

        # End of line, Center On Scroll, Trailing space, Word wrap
        vboxg6 = QVBoxLayout(group6)
        vboxg6.setContentsMargins(5, 15, 5, 5)
        self._checkEndOfLine = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_CONFIG_END_OF_LINE)
        self._checkEndOfLine.setChecked(settings.USE_PLATFORM_END_OF_LINE)
        vboxg6.addWidget(self._checkEndOfLine)
        self._checkCenterScroll = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_CONFIG_CENTER_SCROLL)
        self._checkCenterScroll.setChecked(settings.CENTER_ON_SCROLL)
        vboxg6.addWidget(self._checkCenterScroll)
        self._checkTrailing = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_CONFIG_REMOVE_TRAILING)
        self._checkTrailing.setChecked(settings.REMOVE_TRAILING_SPACES)
        vboxg6.addWidget(self._checkTrailing)
        self._allowWordWrap = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_CONFIG_WORD_WRAP)
        self._allowWordWrap.setChecked(settings.ALLOW_WORD_WRAP)
        vboxg6.addWidget(self._allowWordWrap)
        formFeatures.addWidget(group6, 3, 1)

        # pack all the groups
        vbox.addWidget(container_widget_with_all_preferences)
        vbox.addItem(QSpacerItem(0, 10, QSizePolicy.Expanding,
                     QSizePolicy.Expanding))

        self.connect(self._preferences, SIGNAL("savePreferences()"), self.save)

    def _enable_check_inline(self, val):
        """Method that takes a value to enable the inline style checking"""
        if val == Qt.Checked:
            self._checkStyle.setChecked(True)

    def _enable_errors_inline(self, val):
        """Method that takes a value to enable the inline errors checking"""
        if val == Qt.Checked:
            self._checkErrors.setChecked(True)

    def _disable_check_style(self, val):
        """Method that takes a value to disable the inline style checking"""
        if val == Qt.Unchecked:
            self._checkStyleOnLine.setChecked(False)

    def _disable_show_errors(self, val):
        """Method that takes a value to disable the inline errors checking"""
        if val == Qt.Unchecked:
            self._showErrorsOnLine.setChecked(False)

    def save(self):
        """Method to save settings"""
        qsettings = IDE.ninja_settings()
        settings.USE_TABS = bool(self._checkUseTabs.currentIndex())
        qsettings.setValue('preferences/editor/useTabs',
                           settings.USE_TABS)
        margin_line = self._spinMargin.value()
        settings.MARGIN_LINE = margin_line
        settings.pep8mod_update_margin_line_length(margin_line)
        qsettings.setValue('preferences/editor/marginLine', margin_line)
        settings.SHOW_MARGIN_LINE = self._checkShowMargin.isChecked()
        qsettings.setValue('preferences/editor/showMarginLine',
                           settings.SHOW_MARGIN_LINE)
        settings.INDENT = self._spin.value()
        qsettings.setValue('preferences/editor/indent', settings.INDENT)
        endOfLine = self._checkEndOfLine.isChecked()
        settings.USE_PLATFORM_END_OF_LINE = endOfLine
        qsettings.setValue('preferences/editor/platformEndOfLine', endOfLine)
        settings.UNDERLINE_NOT_BACKGROUND = \
            bool(self._checkHighlightLine.currentIndex())
        qsettings.setValue('preferences/editor/errorsUnderlineBackground',
                           settings.UNDERLINE_NOT_BACKGROUND)
        settings.FIND_ERRORS = self._checkErrors.isChecked()
        qsettings.setValue('preferences/editor/errors', settings.FIND_ERRORS)
        settings.ERRORS_HIGHLIGHT_LINE = self._showErrorsOnLine.isChecked()
        qsettings.setValue('preferences/editor/errorsInLine',
                           settings.ERRORS_HIGHLIGHT_LINE)
        settings.CHECK_STYLE = self._checkStyle.isChecked()
        qsettings.setValue('preferences/editor/checkStyle',
                           settings.CHECK_STYLE)
        settings.SHOW_MIGRATION_TIPS = self._showMigrationTips.isChecked()
        qsettings.setValue('preferences/editor/showMigrationTips',
                           settings.SHOW_MIGRATION_TIPS)
        settings.CHECK_HIGHLIGHT_LINE = self._checkStyleOnLine.isChecked()
        qsettings.setValue('preferences/editor/checkStyleInline',
                           settings.CHECK_HIGHLIGHT_LINE)
        settings.CENTER_ON_SCROLL = self._checkCenterScroll.isChecked()
        qsettings.setValue('preferences/editor/centerOnScroll',
                           settings.CENTER_ON_SCROLL)
        settings.REMOVE_TRAILING_SPACES = self._checkTrailing.isChecked()
        qsettings.setValue('preferences/editor/removeTrailingSpaces',
                           settings.REMOVE_TRAILING_SPACES)
        settings.ALLOW_WORD_WRAP = self._allowWordWrap.isChecked()
        qsettings.setValue('preferences/editor/allowWordWrap',
                           settings.ALLOW_WORD_WRAP)
        settings.SHOW_TABS_AND_SPACES = self._checkShowSpaces.isChecked()
        qsettings.setValue('preferences/editor/showTabsAndSpaces',
                           settings.SHOW_TABS_AND_SPACES)
        settings.SHOW_INDENTATION_GUIDE = (
            self._checkIndentationGuide.isChecked())
        qsettings.setValue('preferences/editor/showIndentationGuide',
                           settings.SHOW_INDENTATION_GUIDE)
        settings.CHECK_FOR_DOCSTRINGS = self._checkForDocstrings.isChecked()
        qsettings.setValue('preferences/editor/checkForDocstrings',
                           settings.CHECK_FOR_DOCSTRINGS)

        if settings.USE_TABS:
            settings.pep8mod_add_ignore("W191")
        else:
            settings.pep8mod_remove_ignore("W191")
        settings.pep8mod_refresh_checks()


preferences.Preferences.register_configuration(
    'EDITOR', EditorConfiguration,
    translations.TR_PREFERENCES_EDITOR_CONFIGURATION,
    weight=0, subsection='CONFIGURATION')
