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
import json
import shutil
import unittest
import tempfile

from ninja_ide.tools.json_manager import read_ninja_plugin
from ninja_ide.tools.json_manager import read_ninja_project
from ninja_ide.tools.json_manager import create_ninja_project


class TestNinjaProject(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_create_ninja_project(self):

        path = self.tmpdir
        project = 'This is My Project'
        structure = dict(foo='bar')

        create_ninja_project(path, project, structure)
        expected_name = 'this_is_my_project.nja'

        self.assertTrue(expected_name in os.listdir(path))
        with open(os.path.join(path, expected_name), 'r') as fp:
            content = json.load(fp)
            assert content['foo'] == 'bar'

    def test_create_ninja_project_with_lot_of_spaces_in_name(self):

        path = self.tmpdir
        project = 'This is My         Project '
        structure = dict(foo='bar')

        create_ninja_project(path, project, structure)
        expected_name = 'this_is_my_________project.nja'

        self.assertTrue(expected_name in os.listdir(path))
        with open(os.path.join(path, expected_name), 'r') as fp:
            content = json.load(fp)
            assert content['foo'] == 'bar'

    def test_read_ninja_project(self):

        path = self.tmpdir
        project = 'This is My Project'
        structure = dict(foo='bar')

        structure = read_ninja_project(path)
        self.assertEqual(structure, dict())

        structure = dict(foo='bar')
        create_ninja_project(path, project, structure)
        structure = read_ninja_project(path)
        assert structure['foo'] == 'bar'

    def test_read_ninja_bad_file_project(self):

        path = self.tmpdir
        frula_file = os.path.join(path, 'frula.nja')
        with open(frula_file, 'w') as fp:
            fp.write('frula\n')

        structure = read_ninja_project(path)
        assert structure == dict()

    def test_read_ninja_plugin(self):

        path = self.tmpdir
        content = dict(samurai='ki')
        plugin_file = os.path.join(path, 'samurai.plugin')
        with open(plugin_file, 'w') as fp:
            json.dump(content, fp)

        structure = read_ninja_plugin(path)
        assert structure['samurai'] == 'ki'

    def test_read_ninja_bad_file_plugin(self):

        path = self.tmpdir
        frula_file = os.path.join(path, 'frula.plugin')
        with open(frula_file, 'w') as fp:
            fp.write('frula\n')

        structure = read_ninja_plugin(path)
        assert structure == dict()


if __name__ == '__main__':
    unittest.main()
