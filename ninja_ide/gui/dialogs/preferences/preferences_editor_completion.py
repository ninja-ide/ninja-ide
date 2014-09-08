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
from PyQt4.QtGui import QSizePolicy
from PyQt4.QtGui import QKeySequence
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL

from ninja_ide import translations
from ninja_ide import resources
from ninja_ide.core import settings
from ninja_ide.gui.ide import IDE
from ninja_ide.gui.dialogs.preferences import preferences


class EditorCompletion(QWidget):

    def __init__(self, parent):
        super(EditorCompletion, self).__init__()
        self._preferences = parent
        vbox = QVBoxLayout(self)

        groupBoxClose = QGroupBox(translations.TR_PREF_EDITOR_COMPLETE)
        formClose = QGridLayout(groupBoxClose)
        formClose.setContentsMargins(5, 15, 5, 5)
        self._checkParentheses = QCheckBox(
            translations.TR_PREF_EDITOR_PARENTHESES + " ()")
        self._checkParentheses.setChecked('(' in settings.BRACES)
        self._checkKeys = QCheckBox(translations.TR_PREF_EDITOR_KEYS + " {}")
        self._checkKeys.setChecked('{' in settings.BRACES)
        self._checkBrackets = QCheckBox(
            translations.TR_PREF_EDITOR_BRACKETS + " []")
        self._checkBrackets.setChecked('[' in settings.BRACES)
        self._checkSimpleQuotes = QCheckBox(
            translations.TR_PREF_EDITOR_SIMPLE_QUOTES)
        self._checkSimpleQuotes.setChecked("'" in settings.QUOTES)
        self._checkDoubleQuotes = QCheckBox(
            translations.TR_PREF_EDITOR_DOUBLE_QUOTES)
        self._checkDoubleQuotes.setChecked('"' in settings.QUOTES)
        self._checkCompleteDeclarations = QCheckBox(
            translations.TR_PREF_EDITOR_COMPLETE_DECLARATIONS.format(
            resources.get_shortcut("Complete-Declarations").toString(
                    QKeySequence.NativeText)))
        self._checkCompleteDeclarations.setChecked(
            settings.COMPLETE_DECLARATIONS)
        formClose.addWidget(self._checkParentheses, 1, 1,
            alignment=Qt.AlignTop)
        formClose.addWidget(self._checkKeys, 1, 2, alignment=Qt.AlignTop)
        formClose.addWidget(self._checkBrackets, 2, 1, alignment=Qt.AlignTop)
        formClose.addWidget(self._checkSimpleQuotes, 2, 2,
            alignment=Qt.AlignTop)
        formClose.addWidget(self._checkDoubleQuotes, 3, 1,
            alignment=Qt.AlignTop)
        vbox.addWidget(groupBoxClose)

        groupBoxCode = QGroupBox(translations.TR_PREF_EDITOR_CODE_COMPLETION)
        formCode = QGridLayout(groupBoxCode)
        formCode.setContentsMargins(5, 15, 5, 5)
        self._checkCodeDot = QCheckBox(
            translations.TR_PREF_EDITOR_ACTIVATE_COMPLETION)
        self._checkCodeDot.setChecked(settings.CODE_COMPLETION)
        formCode.addWidget(self._checkCompleteDeclarations, 5, 1,
            alignment=Qt.AlignTop)

        formCode.addWidget(self._checkCodeDot, 6, 1, alignment=Qt.AlignTop)
        vbox.addWidget(groupBoxCode)
        vbox.addItem(QSpacerItem(0, 10, QSizePolicy.Expanding,
            QSizePolicy.Expanding))

        self.connect(self._preferences, SIGNAL("savePreferences()"), self.save)

    def save(self):
        qsettings = IDE.ninja_settings()
        if self._checkParentheses.isChecked():
            settings.BRACES['('] = ')'
        elif ('(') in settings.BRACES:
            del settings.BRACES['(']
        qsettings.setValue('preferences/editor/parentheses',
            self._checkParentheses.isChecked())
        if self._checkBrackets.isChecked():
            settings.BRACES['['] = ']'
        elif ('[') in settings.BRACES:
            del settings.BRACES['[']
        qsettings.setValue('preferences/editor/brackets',
            self._checkBrackets.isChecked())
        if self._checkKeys.isChecked():
            settings.BRACES['{'] = '}'
        elif ('{') in settings.BRACES:
            del settings.BRACES['{']
        qsettings.setValue('preferences/editor/keys',
            self._checkKeys.isChecked())
        if self._checkSimpleQuotes.isChecked():
            settings.QUOTES["'"] = "'"
        elif ("'") in settings.QUOTES:
            del settings.QUOTES["'"]
        qsettings.setValue('preferences/editor/simpleQuotes',
            self._checkSimpleQuotes.isChecked())
        if self._checkDoubleQuotes.isChecked():
            settings.QUOTES['"'] = '"'
        elif ('"') in settings.QUOTES:
            del settings.QUOTES['"']
        qsettings.setValue('preferences/editor/doubleQuotes',
            self._checkDoubleQuotes.isChecked())
        settings.CODE_COMPLETION = self._checkCodeDot.isChecked()
        qsettings.setValue('preferences/editor/codeCompletion',
            self._checkCodeDot .isChecked())
        settings.COMPLETE_DECLARATIONS = \
            self._checkCompleteDeclarations.isChecked()
        qsettings.setValue("preferences/editor/completeDeclarations",
            settings.COMPLETE_DECLARATIONS)


preferences.Preferences.register_configuration(
    'EDITOR', EditorCompletion,
    translations.TR_PREFERENCES_EDITOR_COMPLETION,
    weight=1, subsection='COMPLETION')