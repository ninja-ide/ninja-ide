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

import unittest
import os

from ninja_ide.core import file_manager
from ninja_ide.core import settings


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))


class FileManagerTestCase(unittest.TestCase):

    def setUp(self):
        global CURRENT_DIR
        self.examples_dir = os.path.join(CURRENT_DIR, 'examples')

    def test_read_file_content(self):
        filename = os.path.join(self.examples_dir, 'file_for_tests.py')
        content = file_manager.read_file_content(filename)
        expected = ("# -*- coding: utf-8 -*-\n\nprint 'testing'\n"
                    "print 'ñandú testing'\n").encode('utf-8')
        self.assertEqual(content, expected)

    def __store_file_content(self, filename, content):
        return file_manager.store_file_content(filename, content)

    def test_change_eol_file_unix_content(self):
        # Write in Unix mode (Default)
        settings.END_OF_LINE = 'Unix'
        filename = os.path.join(self.examples_dir, 'file_for_tests_write.py')
        content = "# -*- coding: utf-8 -*-\n\nprint('testing')"
        self.__store_file_content(filename, content)
        with open(filename) as f:
            binary_content = f.read()
        expected = "# -*- coding: utf-8 -*-\n\nprint('testing')"
        self.assertEqual(binary_content, expected)

    def test_change_eol_file_windows_content(self):
        # Write in Windows mode
        settings.END_OF_LINE = 'Windows'
        filename = os.path.join(self.examples_dir, 'file_for_tests_write.py')
        content = "# -*- coding: utf-8 -*-\n\nprint('testing')"
        self.__store_file_content(filename, content)
        with open(filename) as f:
            binary_content = f.read()
        expected = "# -*- coding: utf-8 -*-\r\n\r\nprint('testing')"
        self.assertEqual(binary_content, expected)

    def test_change_eol_file_mac_content(self):
        # Write in Mac mode
        settings.END_OF_LINE = 'Mac'
        filename = os.path.join(self.examples_dir, 'file_for_tests_write.py')
        content = "# -*- coding: utf-8 -*-\n\nprint('testing')"
        self.__store_file_content(filename, content)
        with open(filename) as f:
            binary_content = f.read()
        expected = "# -*- coding: utf-8 -*-\r\rprint('testing')"
        self.assertEqual(binary_content, expected)


if __name__ == '__main__':
    unittest.main()
