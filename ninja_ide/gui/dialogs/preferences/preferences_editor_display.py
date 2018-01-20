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
    QCheckBox,
    QComboBox
)
from PyQt5.QtCore import Qt
from ninja_ide.core import settings
from ninja_ide import translations
from ninja_ide.gui.dialogs.preferences import preferences
from ninja_ide.gui.ide import IDE


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
        vbox = QVBoxLayout(group1)
        self._check_text_wrapping = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_DISPLAY_ENABLE_TEXT_WRAPPING)
        vbox.addWidget(self._check_text_wrapping)
        self._check_margin_line = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_DISPLAY_RIGHT_MARGIN_LABEL)
        hbox = QHBoxLayout()
        hbox.addWidget(self._check_margin_line)
        self._spin_margin_line = QSpinBox()
        hbox.addWidget(self._spin_margin_line)
        self._check_margin_line_background = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_DISPLAY_RIGHT_MARGIN_BACKGROUND)
        hbox.addWidget(self._check_margin_line_background)
        vbox.addLayout(hbox)

        # Display features
        vbox = QVBoxLayout(group2)
        self._check_platform_eol = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_CONFIG_END_OF_LINE)
        vbox.addWidget(self._check_platform_eol)
        self._check_lineno = QCheckBox(translations.TR_DISPLAY_LINE_NUMBERS)
        vbox.addWidget(self._check_lineno)
        self._check_indentation_guides = QCheckBox(
            translations.TR_SHOW_INDENTATION_GUIDES)
        vbox.addWidget(self._check_indentation_guides)
        self._check_text_changes = QCheckBox(
            translations.TR_DISPLAY_TEXT_CHANGES)
        vbox.addWidget(self._check_text_changes)
        self._check_brace_matching = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_DISPLAY_HIGHLIGHT_BRACKETS)
        vbox.addWidget(self._check_brace_matching)
        hbox = QHBoxLayout()
        self._check_current_line = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_DISPLAY_HIGHLIGHT_CURRENT_LINE)
        self._combo_current_line = QComboBox()
        self._combo_current_line.addItems([
            "Full",
            "Simple"
        ])
        self._check_current_line.stateChanged.connect(
            lambda state: self._combo_current_line.setEnabled(state))
        hbox.addWidget(self._check_current_line)
        hbox.addWidget(self._combo_current_line)
        vbox.addLayout(hbox)
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
        self._check_highlight_pep8.stateChanged.connect(
            lambda state: self._check_show_tooltip_pep8.setEnabled(state))

        container.addWidget(group1)
        container.addWidget(group2)
        container.addWidget(group3)
        container.addStretch(1)

        # Settings
        self._check_text_wrapping.setChecked(settings.ALLOW_WORD_WRAP)
        self._check_highlight_pep8.setChecked(settings.CHECK_STYLE)
        self._check_indentation_guides.setChecked(
            settings.SHOW_INDENTATION_GUIDES)
        self._check_find_errors.setChecked(settings.FIND_ERRORS)
        self._check_show_tooltip_pep8.setEnabled(settings.CHECK_STYLE)
        self._check_show_tabs.setChecked(settings.SHOW_TABS_AND_SPACES)
        self._check_margin_line.setChecked(settings.SHOW_MARGIN_LINE)
        self._check_text_changes.setChecked(settings.SHOW_TEXT_CHANGES)
        self._spin_margin_line.setValue(settings.MARGIN_LINE)
        self._check_margin_line_background.setChecked(
            settings.MARGIN_LINE_BACKGROUND)
        self._check_current_line.setChecked(settings.HIGHLIGHT_CURRENT_LINE)
        self._combo_current_line.setCurrentIndex(
            settings.HIGHLIGHT_CURRENT_LINE_MODE)
        self._check_brace_matching.setChecked(settings.BRACE_MATCHING)
        self._check_lineno.setChecked(settings.SHOW_LINE_NUMBERS)

        self._preferences.savePreferences.connect(self._save)

    def _save(self):
        qsettings = IDE.editor_settings()

        qsettings.beginGroup("editor")
        qsettings.beginGroup("display")

        settings.ALLOW_WORD_WRAP = self._check_text_wrapping.isChecked()
        qsettings.setValue("allow_word_wrap", settings.ALLOW_WORD_WRAP)
        settings.SHOW_TABS_AND_SPACES = self._check_show_tabs.isChecked()
        qsettings.setValue("show_whitespaces",
                           settings.SHOW_TABS_AND_SPACES)
        settings.SHOW_INDENTATION_GUIDES = \
            self._check_indentation_guides.isChecked()
        # qsettings.setValue("show_indentation_guides",
        #                    settings.SHOW_INDENTATION_GUIDES)
        settings.SHOW_MARGIN_LINE = self._check_margin_line.isChecked()
        qsettings.setValue("margin_line", settings.SHOW_MARGIN_LINE)
        settings.MARGIN_LINE = self._spin_margin_line.value()
        qsettings.setValue("margin_line_position", settings.MARGIN_LINE)
        settings.MARGIN_LINE_BACKGROUND = \
            self._check_margin_line_background.isChecked()
        qsettings.setValue("margin_line_background",
                           settings.MARGIN_LINE_BACKGROUND)
        settings.HIGHLIGHT_CURRENT_LINE = self._check_current_line.isChecked()
        qsettings.setValue("highlight_current_line",
                           settings.HIGHLIGHT_CURRENT_LINE)
        settings.HIGHLIGHT_CURRENT_LINE_MODE = \
            self._combo_current_line.currentIndex()
        qsettings.setValue("current_line_mode",
                           settings.HIGHLIGHT_CURRENT_LINE_MODE)
        settings.BRACE_MATCHING = self._check_brace_matching.isChecked()
        qsettings.setValue("brace_matching", settings.BRACE_MATCHING)
        settings.SHOW_LINE_NUMBERS = self._check_lineno.isChecked()
        qsettings.setValue("show_line_numbers", settings.SHOW_LINE_NUMBERS)
        settings.SHOW_TEXT_CHANGES = self._check_text_changes.isChecked()
        qsettings.setValue("show_text_changes", settings.SHOW_TEXT_CHANGES)

        settings.CHECK_STYLE = self._check_highlight_pep8.isChecked()
        qsettings.setValue("check_style", settings.CHECK_STYLE)
        settings.FIND_ERRORS = self._check_find_errors.isChecked()
        qsettings.setValue("check_errors", settings.FIND_ERRORS)

        qsettings.endGroup()
        qsettings.endGroup()

        # editor = main_container.get_current_editor()
        # if editor is not None:
            # FIXME: improve
        #    editor.show_whitespaces = settings.SHOW_TABS_AND_SPACES
        #    editor.set_current_line_highlighter(
        #        settings.HIGHLIGHT_CURRENT_LINE)
        #    editor.set_current_line_highlighter_mode(
        #        settings.HIGHLIGHT_CURRENT_LINE_MODE)
        #    editor.set_brace_matching(settings.BRACE_MATCHING)
        #    editor.show_line_numbers(settings.SHOW_LINE_NUMBERS)


preferences.Preferences.register_configuration(
    'EDITOR',
    EditorDisplay,
    "Display",
    weight=1,
    subsection="EDITOR"
)
