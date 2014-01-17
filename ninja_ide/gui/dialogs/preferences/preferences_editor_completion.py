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


class EditorCompletion(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        vbox = QVBoxLayout(self)

        groupBoxClose = QGroupBox(self.tr("Complete:"))
        formClose = QGridLayout(groupBoxClose)
        self._checkParentheses = QCheckBox(self.tr("Parentheses: ()"))
        self._checkParentheses.setChecked('(' in settings.BRACES)
        self._checkKeys = QCheckBox(self.tr("Keys: {}"))
        self._checkKeys.setChecked('{' in settings.BRACES)
        self._checkBrackets = QCheckBox(self.tr("Brackets: []"))
        self._checkBrackets.setChecked('[' in settings.BRACES)
        self._checkSimpleQuotes = QCheckBox(self.tr("Simple Quotes: ''"))
        self._checkSimpleQuotes.setChecked("'" in settings.QUOTES)
        self._checkDoubleQuotes = QCheckBox(self.tr("Double Quotes: \"\""))
        self._checkDoubleQuotes.setChecked('"' in settings.QUOTES)
        self._checkCompleteDeclarations = QCheckBox(
            self.tr("Complete Declarations\n"
            "(execute the opposite action with: %s).") %
                resources.get_shortcut("Complete-Declarations").toString(
                    QKeySequence.NativeText))
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

        groupBoxCode = QGroupBox(self.tr("Code Completion:"))
        formCode = QGridLayout(groupBoxCode)
        self._checkCodeDot = QCheckBox(
            self.tr("Activate Code Completion with: \".\""))
        self._checkCodeDot.setChecked(settings.CODE_COMPLETION)
        formCode.addWidget(self._checkCompleteDeclarations, 5, 1,
            alignment=Qt.AlignTop)

        formCode.addWidget(self._checkCodeDot, 6, 1, alignment=Qt.AlignTop)
        vbox.addWidget(groupBoxCode)
        vbox.addItem(QSpacerItem(0, 10, QSizePolicy.Expanding,
            QSizePolicy.Expanding))

    def save(self):
        qsettings = QSettings(resources.SETTINGS_PATH, QSettings.IniFormat)
        qsettings.beginGroup('preferences')
        qsettings.beginGroup('editor')
        qsettings.setValue('parentheses', self._checkParentheses.isChecked())
        if self._checkParentheses.isChecked():
            settings.BRACES['('] = ')'
        elif ('(') in settings.BRACES:
            del settings.BRACES['(']
        qsettings.setValue('brackets', self._checkBrackets.isChecked())
        if self._checkBrackets.isChecked():
            settings.BRACES['['] = ']'
        elif ('[') in settings.BRACES:
            del settings.BRACES['[']
        qsettings.setValue('keys', self._checkKeys.isChecked())
        if self._checkKeys.isChecked():
            settings.BRACES['{'] = '}'
        elif ('{') in settings.BRACES:
            del settings.BRACES['{']
        qsettings.setValue('simpleQuotes', self._checkSimpleQuotes.isChecked())
        if self._checkSimpleQuotes.isChecked():
            settings.QUOTES["'"] = "'"
        elif ("'") in settings.QUOTES:
            del settings.QUOTES["'"]
        qsettings.setValue('doubleQuotes', self._checkDoubleQuotes.isChecked())
        if self._checkDoubleQuotes.isChecked():
            settings.QUOTES['"'] = '"'
        elif ('"') in settings.QUOTES:
            del settings.QUOTES['"']
        qsettings.setValue('codeCompletion', self._checkCodeDot .isChecked())
        settings.CODE_COMPLETION = self._checkCodeDot.isChecked()
        settings.COMPLETE_DECLARATIONS = \
            self._checkCompleteDeclarations.isChecked()
        qsettings.setValue("completeDeclarations",
            settings.COMPLETE_DECLARATIONS)
        qsettings.endGroup()
        qsettings.endGroup()