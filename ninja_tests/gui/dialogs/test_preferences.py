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

# Import this before Qt to set the correct API
import ninja_ide  # lint:ok

from PyQt4.QtGui import QApplication
from PyQt4.QtGui import QKeySequence
from PyQt4.QtGui import QTreeWidgetItem
from PyQt4.QtCore import Qt

from ninja_ide import resources
from ninja_ide.gui.dialogs import preferences
from ninja_ide.gui.misc import shortcut_manager
from ninja_tests import gui
from ninja_tests import BaseTest


class PreferencesEditorConfigurationTestCase(BaseTest):

    @classmethod
    def setUpClass(cls):
        cls._app = QApplication([])

    @classmethod
    def tearDownClass(cls):
        del cls._app

    def setUp(self):
        super(PreferencesEditorConfigurationTestCase, self).setUp()
        self.settings = gui.FakeQSettings()
        self.patch(preferences, 'QSettings', lambda: self.settings)
        self.editor_completion = preferences.EditorConfiguration()

    def _check_values(self, errors, indent, checkStyle, marginLine,
                      checkForDocstrings, showMarginLine,
                      errorsInLine, centerOnScroll, checkStyleInline,
                      useTabs, highlightWholeLine, removeTrailingSpaces,
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


class PreferencesShortcutManagerConfigurationTestCase(BaseTest):

    @classmethod
    def setUpClass(cls):
        cls._app = QApplication([])

    @classmethod
    def tearDownClass(cls):
        del cls._app

    def setUp(self):
        super(PreferencesShortcutManagerConfigurationTestCase, self).setUp()
        self.settings = gui.FakeQSettings()
        self.patch(shortcut_manager, 'QSettings', lambda: self.settings)
        self.patch(resources, 'QSettings', lambda: self.settings)
        # Test data
        custom_default_data = {
            "New-file": QKeySequence(Qt.CTRL + Qt.Key_N)
        }
        # patch shortcuts with test data
        self.patch(resources, 'CUSTOM_SHORTCUTS', custom_default_data)
        self.shortcuts_manager = shortcut_manager.ShortcutConfiguration()

    def test_load_default_shortcuts(self):
        shorts_count = self.shortcuts_manager.result_widget.topLevelItemCount()
        item = self.shortcuts_manager.result_widget.topLevelItem(0)
        shortcut_keys = item.text(1)
        # Expected data
        expected_key = QKeySequence(Qt.CTRL + Qt.Key_N)
        expected_key_str = expected_key.toString(QKeySequence.NativeText)
        # Just one shortcut should be loaded
        self.assertEqual(shorts_count, 1)
        # The key should be the same as the expected
        self.assertEqual(shortcut_keys, expected_key_str)

    def test_save_shortcuts(self):
        data = []

        def called():
            data.append(True)

        actions = gui.FakeActions()
        setattr(actions, 'update_shortcuts', called)
        self.patch(shortcut_manager.actions, 'Actions', lambda: actions)
        self.shortcuts_manager.result_widget.clear()
        key = QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_N)
        key_str = key.toString(QKeySequence.NativeText)
        tree_data = ["New File", key_str, "New-File"]
        item = QTreeWidgetItem(self.shortcuts_manager.result_widget, tree_data)
        item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        # Before save there is nothing in QSettings
        self.assertEqual(self.settings.value("New-File", None), None)
        # Save
        self.shortcuts_manager.save()
        # After save there is a value for New-File QSettings
        self.assertEqual(self.settings.values["New-File"], key_str)
        # After save check if NINJA call the update_shortcuts in actios.Actions
        self.assertEqual(data, [True])
