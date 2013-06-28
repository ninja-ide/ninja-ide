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


import os
import unittest

from ninja_tests.tools.jsonmanager import samples

from ninja_ide import resources
from ninja_ide.core import settings
from ninja_ide.tools.json_manager import load_syntax


class TestSyntaxLoader(unittest.TestCase):
    ''' We test the loader method from the json manager
    that is in charge of loading syntax files
    '''

    def setUp(self):

        self.samples = os.path.dirname(samples.__file__)
        self.goodsamples = os.path.join(self.samples, 'goodfiles')
        self.badsamples = os.path.join(self.samples, 'badfiles')
        # Clean SYNTAX before each test
        settings.SYNTAX = {}

    def test_load_nice_json_syntax_file(self):

        resources.SYNTAX_FILES = self.goodsamples

        py_syntax_name = 'python'
        py_syntax_file = os.path.join(self.goodsamples,
                                      py_syntax_name + '.json')

        assert os.path.isfile(py_syntax_file) is True

        self.assertTrue(py_syntax_name not in settings.SYNTAX)
        load_syntax()
        self.assertTrue(py_syntax_name in settings.SYNTAX)

        python_syntax = settings.SYNTAX["python"]
        extensions = python_syntax['extension']
        for kw in extensions:
            self.assertTrue(kw in settings.EXTENSIONS)
            self.assertEquals(settings.EXTENSIONS[kw], py_syntax_name)

    def test_load_bad_json_syntax_file(self):

        resources.SYNTAX_FILES = self.badsamples

        py_syntax_name = 'python'
        py_syntax_file = os.path.join(self.goodsamples,
                                      py_syntax_name + '.json')

        assert os.path.isfile(py_syntax_file) is True

        self.assertTrue(py_syntax_name not in settings.SYNTAX)
        load_syntax()
        self.assertTrue(py_syntax_name not in settings.SYNTAX)


if __name__ == '__main__':
    unittest.main()
