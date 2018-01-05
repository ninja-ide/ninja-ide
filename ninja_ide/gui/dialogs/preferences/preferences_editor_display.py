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
    QSpinBox,
    QLabel,
    QGroupBox,
    QCheckBox
)
from PyQt5.QtCore import Qt
from ninja_ide import translations
from ninja_ide.gui.dialogs.preferences import preferences
# from ninja_ide.gui.ide import IDE


class EditorDisplay(QWidget):
    """EditorDisplay widget class"""

    def __init__(self, parent):
        super().__init__(parent)
        self._preferences = parent
        container = QVBoxLayout(self)
        # Groups
        group1 = QGroupBox(translations.TR_PREFERENCES_EDITOR_DISPLAY_WRAPPING)
        group2 = QGroupBox(translations.TR_PREFERENCES_EDITOR_DISPLAY)
        group3 = QGroupBox(translations.TR_PREFERENCES_EDITOR_DISPLAY_LINT)

        # Text wrapping
        hbox = QHBoxLayout(group1)
        self._check_text_wrapping = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_DISPLAY_ENABLE_TEXT_WRAPPING)
        hbox.addWidget(self._check_text_wrapping)
        hbox.addStretch(1)
        hbox.addWidget(
            QLabel(
                translations.TR_PREFERENCES_EDITOR_DISPLAY_RIGHT_MARGIN_LABEL))
        self._spin_margin_line = QSpinBox()
        hbox.addWidget(self._spin_margin_line)

        # Display features
        vbox = QVBoxLayout(group2)
        self._check_platform_eol = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_CONFIG_END_OF_LINE)
        vbox.addWidget(self._check_platform_eol)
        self._check_lineno = QCheckBox(translations.TR_DISPLAY_LINE_NUMBERS)
        vbox.addWidget(self._check_lineno)
        self._check_highlight_brackets = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_DISPLAY_HIGHLIGHT_BRACKETS)
        vbox.addWidget(self._check_highlight_brackets)
        self._check_current_line = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_DISPLAY_HIGHLIGHT_CURRENT_LINE)
        vbox.addWidget(self._check_current_line)
        self._check_show_tabs = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_CONFIG_SHOW_TABS_AND_SPACES)
        vbox.addWidget(self._check_show_tabs)
        self._check_highlight_results = QCheckBox(
            translations.TR_HIGHLIGHT_RESULT_ON_SCROLLBAR)
        vbox.addWidget(self._check_highlight_results)
        self._check_center_on_scroll = QCheckBox(
            translations.TR_CENTER_ON_SCROLL)
        vbox.addWidget(self._check_center_on_scroll)

        # Linter
        vbox = QVBoxLayout(group3)
        self._check_find_errors = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_CONFIG_FIND_ERRORS)
        vbox.addWidget(self._check_find_errors)
        self._check_show_tooltip_error = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_CONFIG_SHOW_TOOLTIP_ERRORS)
        vbox.addWidget(
            self._check_show_tooltip_error, alignment=Qt.AlignCenter)
        self._check_highlight_pep8 = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_CONFIG_SHOW_PEP8)
        vbox.addWidget(self._check_highlight_pep8)
        self._check_show_tooltip_pep8 = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_CONFIG_SHOW_TOOLTIP_PEP8)
        vbox.addWidget(self._check_show_tooltip_pep8, alignment=Qt.AlignCenter)

        container.addWidget(group1)
        container.addWidget(group2)
        container.addWidget(group3)
        container.addStretch(1)
        self._preferences.savePreferences.connect(self._save)

    def _save(self):
        pass


preferences.Preferences.register_configuration(
    'EDITOR',
    EditorDisplay,
    "Display",
    weight=1,
    subsection="EDITOR"
)
