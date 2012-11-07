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

import sys

# Import this before Qt to set the correct API
import ninja_ide  # lint:ok

from PyQt4.QtGui import QApplication

from ninja_ide.gui.dialogs import preferences
from ninja_tests import gui
from ninja_tests import BaseTest


class PreferencesEditorConfigurationTestCase(BaseTest):

    def setUp(self):
        super(PreferencesEditorConfigurationTestCase, self).setUp()
        self.app = QApplication(sys.argv)
        self.settings = gui.FakeQSettings()
        self.patch(preferences, 'QSettings', lambda: self.settings)
        self.editor_completion = preferences.EditorConfiguration()

    def _check_values(self, errors, indent, checkStyle, marginLine,
        checkForDocstrings, showMarginLine, errorsInLine, centerOnScroll,
        checkStyleInline, useTabs, highlightWholeLine, removeTrailingSpaces,
        showTabsAndSpaces, allowWordWrap):
        self.assertEqual(self.settings.values['errors'], errors)
        self.assertEqual(self.settings.values['indent'], indent)
        self.assertEqual(self.settings.values['checkStyle'], checkStyle)
        self.assertEqual(self.settings.values['marginLine'], marginLine)
        self.assertEqual(self.settings.values['checkForDocstrings'],
            checkForDocstrings)
        self.assertEqual(self.settings.values['showMarginLine'],
            showMarginLine)
        self.assertEqual(self.settings.values['errorsInLine'], errorsInLine)
        self.assertEqual(self.settings.values['centerOnScroll'],
            centerOnScroll)
        self.assertEqual(self.settings.values['checkStyleInline'],
            checkStyleInline)
        self.assertEqual(self.settings.values['useTabs'], useTabs)
        self.assertEqual(self.settings.values['highlightWholeLine'],
            highlightWholeLine)
        self.assertEqual(self.settings.values['removeTrailingSpaces'],
            removeTrailingSpaces)
        self.assertEqual(self.settings.values['showTabsAndSpaces'],
            showTabsAndSpaces)
        self.assertEqual(self.settings.values['allowWordWrap'], allowWordWrap)

    def test_save(self):
        main = preferences.main_container.MainContainer()
        data = []

        def called():
            data.append(True)

        self.patch(main, 'update_editor_margin_line', called)
        self.patch(preferences.pep8mod, 'refresh_checks', called)
        actions = gui.FakeActions()
        self.patch(preferences.actions, 'Actions', lambda: actions)
        self.editor_completion.save()

        self.assertTrue(actions.reset_editor_flags_executed)
        self.assertEqual('set_tab_usage', actions.func_name)
        self.assertEqual([], preferences.pep8mod.options.ignore)
        self.assertEqual([True, True], data)
        self._check_values(True, 4, True, 80, False, True, True, True, True,
            False, True, True, True, False)
