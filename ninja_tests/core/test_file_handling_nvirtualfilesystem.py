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
from PyQt4.QtCore import QObject

import unittest
import os
#import tempfile

#from ninja_ide.core.file_handling.nfile import NFile

from ninja_ide.core.file_handling import nfilesystem
NVirtualFileSystem = nfilesystem.NVirtualFileSystem

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))


class FakeNProject(QObject):

    def __init__(self, path):
        self.path = path
        super(FakeNProject, self).__init__()


class FakeNFile(QObject):

    def __init__(self, path=""):
        self.path = path
        super(FakeNFile, self).__init__()

nfilesystem.NFile = FakeNFile


class NVirtualFileSystemTestCase(unittest.TestCase):
    """Test NVirtualFileSystem API works"""

    def test_supports_adding_nproject(self):
        nvfs = NVirtualFileSystem()
        project_path = "a given path"
        project = FakeNProject(project_path)
        nvfs.open_project(project)
        self.assertIn(project_path, nvfs._NVirtualFileSystem__projects)

    def test_adding_repeated_nproject_is_ignored(self):
        nvfs = NVirtualFileSystem()
        project_path = "a given path"
        project = FakeNProject(project_path)
        project2 = FakeNProject(project_path)
        self.assertNotEqual(project, project2)
        nvfs.open_project(project)
        self.assertIn(project_path, nvfs._NVirtualFileSystem__projects)
        nvfs.open_project(project2)
        self.assertEqual(nvfs._NVirtualFileSystem__projects[project_path],
                        project)

    def test_files_get_attached_to_project(self):
        nvfs = NVirtualFileSystem()
        project_path = "a given path"
        project = FakeNProject(project_path)
        nvfs.get_file(project_path)
        nvfs.open_project(project)
        nfile = nvfs._NVirtualFileSystem__tree[project_path]
        self.assertEqual(project,
                        nvfs._NVirtualFileSystem__reverse_project_map[nfile])

    def test_close_file_is_handled(self):
        pass

if __name__ == '__main__':
    unittest.main()