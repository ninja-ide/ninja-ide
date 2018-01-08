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
    QCheckBox,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QSizePolicy,
    QSpinBox,
    QGroupBox,
)
from ninja_ide.core import settings
from ninja_ide import translations
from ninja_ide.gui.ide import IDE
from ninja_ide.gui.dialogs.preferences import preferences


class Behavior(QWidget):
    """Behavior widget class"""

    def __init__(self, parent=None):
        super().__init__()
        self._preferences = parent
        container = QVBoxLayout(self)

        # Groups
        group_box_onsaving = QGroupBox(
            translations.TR_PREFERENCES_EDITOR_BEHAVIOR_ONSAVING)
        group_box_indentation = QGroupBox(
            translations.TR_PREFERENCES_EDITOR_BEHAVIOR_INDENTATION)
        group_box_mouse_kbr = QGroupBox(
            translations.TR_PREFERENCES_EDITOR_BEHAVIOR_MOUSE_KEYBOARD)

        # On saving
        vbox = QVBoxLayout(group_box_onsaving)
        self._check_remove_spaces = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_BEHAVIOR_CLEAN_WHITESPACES)
        vbox.addWidget(self._check_remove_spaces)
        self._check_add_new_line = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_BEHAVIOR_ADD_NEW_LINE)
        vbox.addWidget(self._check_add_new_line)

        # Indentation
        hbox = QHBoxLayout(group_box_indentation)
        self._combo_tab_policy = QComboBox()
        self._combo_tab_policy.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._combo_tab_policy.addItems([
            translations.TR_PREFERENCES_EDITOR_BEHAVIOR_SPACES_ONLY,
            translations.TR_PREFERENCES_EDITOR_BEHAVIOR_TABS_ONLY
        ])
        hbox.addWidget(self._combo_tab_policy)
        hbox.addWidget(
            QLabel(translations.TR_PREFERENCES_EDITOR_BEHAVIOR_INDENT_SIZE))
        self._spin_indent_size = QSpinBox()
        hbox.addWidget(self._spin_indent_size)

        # Mouse and keyboard
        vbox = QVBoxLayout(group_box_mouse_kbr)
        self._check_scroll_wheel = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_BEHAVIOR_SCROLL_WHEEL)
        vbox.addWidget(self._check_scroll_wheel)
        self._check_hide_cursor = QCheckBox(
            translations.TR_PREFERENCES_EDITOR_BEHAVIOR_HIDE_CURSOR)
        vbox.addWidget(self._check_hide_cursor)
        hbox = QHBoxLayout()
        hbox.addWidget(
            QLabel(translations.TR_PREFERENCES_EDITOR_BEHAVIOR_SHOW_TOOLTIPS))
        self._combo_tooltips = QComboBox()
        self._combo_tooltips.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._combo_tooltips.addItems([
            translations.TR_PREFERENCES_EDITOR_BEHAVIOR_TOOLTIPS_MOUSE_OVER,
            translations.TR_PREFERENCES_EDITOR_BEHAVIOR_TOOLTIPS_SHIFT
        ])
        hbox.addWidget(self._combo_tooltips)
        vbox.addLayout(hbox)

        container.addWidget(group_box_onsaving)
        container.addWidget(group_box_indentation)
        container.addWidget(group_box_mouse_kbr)
        container.addStretch(1)

        # Settings
        self._check_remove_spaces.setChecked(settings.REMOVE_TRAILING_SPACES)
        self._check_add_new_line.setChecked(settings.ADD_NEW_LINE_AT_EOF)
        self._check_hide_cursor.setChecked(settings.HIDE_MOUSE_CURSOR)
        self._check_scroll_wheel.setChecked(settings.SCROLL_WHEEL_ZOMMING)
        self._combo_tab_policy.setCurrentIndex(bool(settings.USE_TABS))
        self._spin_indent_size.setValue(settings.INDENT)

        self._preferences.savePreferences.connect(self._save)

    def _save(self):
        qsettings = IDE.ninja_settings()
        editor_settings = IDE.editor_settings()

        qsettings.beginGroup("editor")
        editor_settings.beginGroup("editor")
        qsettings.beginGroup("behavior")
        editor_settings.beginGroup("behavior")

        settings.REMOVE_TRAILING_SPACES = self._check_remove_spaces.isChecked()
        qsettings.setValue("removeTrailingSpaces",
                           settings.REMOVE_TRAILING_SPACES)
        settings.ADD_NEW_LINE_AT_EOF = self._check_add_new_line.isChecked()
        qsettings.setValue("addNewLineAtEnd", settings.ADD_NEW_LINE_AT_EOF)
        settings.HIDE_MOUSE_CURSOR = self._check_hide_cursor.isChecked()
        qsettings.setValue("hideMouseCursor", settings.HIDE_MOUSE_CURSOR)
        settings.SCROLL_WHEEL_ZOMMING = self._check_scroll_wheel.isChecked()
        qsettings.setValue("scrollWheelZomming", settings.SCROLL_WHEEL_ZOMMING)

        settings.USE_TABS = bool(self._combo_tab_policy.currentIndex())
        editor_settings.setValue("use_tabs", settings.USE_TABS)
        settings.INDENT = self._spin_indent_size.value()
        editor_settings.setValue("indentation_width", settings.INDENT)

        qsettings.endGroup()
        qsettings.endGroup()
        editor_settings.endGroup()
        editor_settings.endGroup()


preferences.Preferences.register_configuration(
    "EDITOR",
    Behavior,
    translations.TR_PREFERENCES_EDITOR_BEHAVIOR,
    weight=0,
    subsection="BEHAVIOR"
)
