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
    QCheckBox,
    QGroupBox
)
from ninja_ide import translations
from ninja_ide.core import settings
from ninja_ide.gui.ide import IDE
from ninja_ide.gui.dialogs.preferences import preferences


class EditorIntelliSense(QWidget):
    """Manage preferences about IntelliSense"""

    def __init__(self, parent):
        super().__init__(parent)
        self._preferences = parent
        container = QVBoxLayout(self)

        group_1 = QGroupBox(translations.TR_COMPLETE_CHARS)

        vbox = QVBoxLayout(group_1)
        self._check_braces = QCheckBox(translations.TR_COMPLETE_BRACKETS)
        vbox.addWidget(self._check_braces)
        self._check_quotes = QCheckBox(translations.TR_COMPLETE_QUOTES)
        vbox.addWidget(self._check_quotes)
        container.addWidget(group_1)
        container.addStretch(1)

        # Initial settings
        self._check_braces.setChecked(settings.AUTOCOMPLETE_BRACKETS)
        self._check_quotes.setChecked(settings.AUTOCOMPLETE_QUOTES)

        self._preferences.savePreferences.connect(self._save)

    def _save(self):

        qsettings = IDE.editor_settings()

        qsettings.beginGroup("editor")
        qsettings.beginGroup("intellisense")

        settings.AUTOCOMPLETE_BRACKETS = self._check_braces.isChecked()
        qsettings.setValue("autocomplete_brackets",
                           settings.AUTOCOMPLETE_BRACKETS)
        settings.AUTOCOMPLETE_QUOTES = self._check_quotes.isChecked()
        qsettings.setValue("autocomplete_quotes",
                           settings.AUTOCOMPLETE_QUOTES)

        qsettings.endGroup()
        qsettings.endGroup()


preferences.Preferences.register_configuration(
    "EDITOR",
    EditorIntelliSense,
    "IntelliSense",
    weight=2,
    subsection="IntelliSense"
)
