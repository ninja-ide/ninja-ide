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
    QGridLayout,
    QGroupBox,
    QCheckBox
)
from ninja_ide.gui.dialogs.preferences import preferences
from ninja_ide.gui.ide import IDE


class EditorDisplay(QWidget):
    """EditorDisplay widget class"""

    def __init__(self, parent):
        super().__init__(parent)
        self._preferences = parent
        container = QVBoxLayout(self)
        # Groups
        group1 = QGroupBox("Display")

        grid_1 = QGridLayout(group1)
        self._check_indentation_guides = QCheckBox("Indentation Guides")
        grid_1.addWidget(self._check_indentation_guides, 0, 0)

        container.addWidget(group1)

        self._preferences.savePreferences.connect(self._save)

    def _save(self):
        # qsettings = IDE.ninja_settings()
        main_container = IDE.get_service("main_container")
        editor = main_container.get_current_editor()
        if editor is not None:
            is_checked = self._check_indentation_guides.isChecked()
            editor.enable_extension('indentation_guides', is_checked)


preferences.Preferences.register_configuration(
    'EDITOR',
    EditorDisplay,
    "Display",
    weight=0,
    subsection="EDITOR"
)