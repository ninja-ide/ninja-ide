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
import unittest
import os
from ninja_ide.core.plugin_manager import PluginManager


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
PLUGIN_NOT_VALID_NAME = 'test_NOT_plugin.plugin'
PLUGIN_VALID_NAME = 'test_plugin.plugin'


class PluginManagerTestCase(unittest.TestCase):
    def setUp(self):
        global CURRENT_DIR
        plugin_dir = os.path.join(CURRENT_DIR, 'plugins')
        self.pm = PluginManager(plugin_dir, None)

    def test_discover(self):
        self.assertEqual(len(self.pm), 0)
        self.pm.discover()
        self.assertEqual(len(self.pm), 1)

    def test_magic_method_contains(self):
        global PLUGIN_VALID_NAME, PLUGIN_NOT_VALID_NAME
        self.pm.discover()
        self.assertEqual(PLUGIN_VALID_NAME in self.pm, True)
        self.assertEqual(PLUGIN_NOT_VALID_NAME in self.pm, False)

    def test_magic_method_getitem(self):
        global PLUGIN_VALID_NAME, PLUGIN_NOT_VALID_NAME
        self.pm.discover()
        self.assertTrue(self.pm['test_plugin.plugin'])
        self.assertRaises(KeyError, self.pm.__getitem__, PLUGIN_NOT_VALID_NAME)


if __name__ == '__main__':
    unittest.main()
