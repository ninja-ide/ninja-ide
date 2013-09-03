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
import tempfile

from ninja_ide.core.file_handling.nfile import NFile
from ninja_ide.core.file_handling.file_manager import \
            NinjaNoFileNameException, NinjaIOException

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))


class NfileTestCase(unittest.TestCase):
    """Test Nfile API works"""

    def setUp(self):
        """
        """
        global CURRENT_DIR
        self._existing_file = tempfile.NamedTemporaryFile()
        self._non_existing_file = tempfile.NamedTemporaryFile()
        self._trash_files = []

    def tearDown(self):
        """
        """
        self._existing_file.close()
        for each_file in self._trash_files:
            if os.path.exists(each_file):
                os.remove(each_file)

    def get_temp_file_name(self):
        """tempfile seems to lack a proper way to obtain disposable filenames"""
        a_temp_file = tempfile.NamedTemporaryFile()
        temp_file = a_temp_file.name
        a_temp_file.close()
        self._trash_files.append(temp_file)
        return temp_file

    def test_knows_if_exists(self):
        """If the file exists, can NFile tell?"""
        existing_nfile = NFile(self._existing_file.name)
        self.assertTrue(existing_nfile._exists())

    def test_knows_if_desnt_exists(self):
        """If the file does not exists, can NFile tell?"""
        existing_nfile = NFile(self._non_existing_file.name)
        self._non_existing_file.close()
        self.assertFalse(existing_nfile._exists())

    def test_save_no_filename_raises(self):
        """If there is no filename associated to the nfile we
        should get error"""
        no_filename_file = NFile()
        self.assertRaises(NinjaNoFileNameException, no_filename_file.save,
                            ("dumb content",))

    def test_creates_if_doesnt_exist(self):
        temp_name = self.get_temp_file_name()
        self.assertFalse(os.path.exists(temp_name))
        a_nfile = NFile(temp_name)
        a_nfile.save("empty content")
        self.assertTrue(os.path.exists(temp_name))

    def test_actual_content_is_saved(self):
        file_content = "empty content"
        temp_name = self.get_temp_file_name()
        self.assertFalse(os.path.exists(temp_name))
        a_nfile = NFile(temp_name)
        a_nfile.save(file_content)
        a_file = open(temp_name, "r")
        a_file_content = a_file.read()
        self.assertEqual(a_file_content, file_content)

    def test_saves_to_filepath(self):
        temp_name = self.get_temp_file_name()
        self.assertFalse(os.path.exists(temp_name))
        a_nfile = NFile(temp_name)
        self.assertFalse(os.path.exists(a_nfile._file_path))
        a_nfile.save("empty content")
        self.assertTrue(os.path.exists(a_nfile._file_path))

    def test_path_overrides_filepath(self):
        temp_name = self.get_temp_file_name()
        temp_name_path = self.get_temp_file_name()
        #Since we cant assure the two paths are differents we do this
        temp_name_path = u"%s_really_unique" % temp_name_path
        self._trash_files.append(temp_name_path)
        self.assertNotEqual(temp_name, temp_name_path)
        self.assertFalse(os.path.exists(temp_name))
        a_nfile = NFile(temp_name)
        self.assertFalse(os.path.exists(a_nfile._file_path))
        a_nfile.save("empty content", path=temp_name_path)
        self.assertFalse(os.path.exists(temp_name))
        self.assertTrue(os.path.exists(temp_name_path))

    def test_path_is_set_as_new_nfile_filepath(self):
        temp_name = self.get_temp_file_name()
        temp_name_path = self.get_temp_file_name()
        #Since we cant assure the two paths are differents we do this
        temp_name_path = u"%s_really_unique" % temp_name_path
        self._trash_files.append(temp_name_path)
        self.assertNotEqual(temp_name, temp_name_path)
        a_nfile = NFile(temp_name)
        self.assertNotEqual(temp_name_path, a_nfile._file_path)
        new_nfile = a_nfile.save("empty content", path=temp_name_path)
        self.assertEqual(temp_name_path, new_nfile._file_path)
        self.assertEqual(temp_name, a_nfile._file_path)

    def test_copy_flag_saves_to_path_only(self):
        temp_name = self.get_temp_file_name()
        temp_name_path = self.get_temp_file_name()
        #Since we cant assure the two paths are differents we do this
        temp_name_path = u"%s_really_unique" % temp_name_path
        self._trash_files.append(temp_name_path)
        self.assertNotEqual(temp_name, temp_name_path)
        a_nfile = NFile(temp_name)
        a_nfile.save("empty content", path=temp_name_path)
        self.assertFalse(os.path.exists(temp_name))
        self.assertTrue(os.path.exists(temp_name_path))

    def test_file_is_read_properly(self):
        to_load_file = tempfile.NamedTemporaryFile()
        load_text = "Something to load"
        to_load_file.write(load_text)
        to_load_file.seek(0)  # FIXME: buffer errors could break this
        a_nfile = NFile(to_load_file.name)
        content = a_nfile.read()
        self.assertEqual(content, load_text)

    def test_file_read_blows_when_nonexistent_path(self):
        a_nfile = NFile()
        self.assertRaises(NinjaNoFileNameException, a_nfile.read)

    def test_file_read_blows_on_nonexistent_file(self):
        temp_name = self.get_temp_file_name()
        a_nfile = NFile(temp_name)
        self.assertRaises(NinjaIOException, a_nfile.read)

    def test_file_is_moved(self):
        temp_name = self.get_temp_file_name()
        new_temp_name = u"%s_new" % temp_name
        self._trash_files.append(new_temp_name)
        test_content = "zero"
        temp_file = open(temp_name, "w")
        temp_file.write(test_content)
        temp_file.close()
        a_nfile = NFile(temp_name)
        a_nfile.move(new_temp_name)
        self.assertTrue(os.path.exists(new_temp_name))
        read_test_content = open(new_temp_name, "r").read()
        self.assertEqual(read_test_content, test_content)
        self.assertFalse(os.path.exists(temp_name))

    def test_move_changes_filepath(self):
        temp_name = self.get_temp_file_name()
        new_temp_name = u"%s_new" % temp_name
        self._trash_files.append(new_temp_name)
        test_content = "zero"
        temp_file = open(temp_name, "w")
        temp_file.write(test_content)
        temp_file.close()
        a_nfile = NFile(temp_name)
        a_nfile.move(new_temp_name)
        self.assertEqual(a_nfile._file_path, new_temp_name)

    def test_filepath_changes_even_if_inexistent(self):
        temp_name = self.get_temp_file_name()
        a_nfile = NFile()
        a_nfile.move(temp_name)
        self.assertEqual(a_nfile._file_path, temp_name)


if __name__ == '__main__':
    unittest.main()