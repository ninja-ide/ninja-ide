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
import tempfile
import pytest

from ninja_ide.core.file_handling import nfile
from ninja_ide.core.file_handling.file_manager import NinjaNoFileNameException
from ninja_ide.core.file_handling.file_manager import NinjaIOException

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

# Test Nfile API works


def test_knows_if_exists():
    """If the file exists, can NFile tell?"""
    temp_file = tempfile.NamedTemporaryFile()
    existing_nfile = nfile.NFile(temp_file.name)
    assert existing_nfile._exists()


def test_knows_if_doesnt_exists():
    """If the file does not exists, can NFile tell?"""
    temp_file = tempfile.NamedTemporaryFile()
    existing_nfile = nfile.NFile(temp_file.name)
    temp_file.close()
    assert not existing_nfile._exists()


def test_save_no_filename_raises():
    """If there is no filename associated to the nfile we should get error"""
    no_filename_file = nfile.NFile()
    with pytest.raises(NinjaNoFileNameException) as info:
        no_filename_file.save("dumb content")
    assert str(info.value) == "I am asked to write a file but no one told me"\
                              " where"


def test_creates_if_doesnt_exist():
    temp_name = tempfile.NamedTemporaryFile().name
    assert not os.path.exists(temp_name)
    a_nfile = nfile.NFile(temp_name)
    a_nfile.save("empty content")
    assert os.path.exists(temp_name)


def test_actual_content_is_saved():
    content = "empty content"
    temp_name = tempfile.NamedTemporaryFile().name
    assert not os.path.exists(temp_name)
    a_nfile = nfile.NFile(temp_name)
    a_nfile.save(content)
    a_file = open(temp_name)
    a_file_content = a_file.read()
    assert a_file_content == content
    a_file.close()


def test_saves_to_filepath():
    temp_name = tempfile.NamedTemporaryFile().name
    assert not os.path.exists(temp_name)
    a_nfile = nfile.NFile(temp_name)
    assert not os.path.exists(a_nfile.file_path)
    a_nfile.save("content")
    assert os.path.exists(a_nfile.file_path)


def test_path_overrides_filepath():
    temp_name = tempfile.NamedTemporaryFile().name
    temp_name_path = tempfile.NamedTemporaryFile().name
    temp_name_path = "%s_really_unique" % temp_name_path
    assert temp_name != temp_name_path
    assert not temp_name == temp_name_path
    a_nfile = nfile.NFile(temp_name)
    assert not os.path.exists(a_nfile.file_path)
    a_nfile.save("content", path=temp_name_path)
    assert not os.path.exists(temp_name)
    assert os.path.exists(temp_name_path)


def test_path_is_set_as_new_nfile_filepath():
    temp_name = tempfile.NamedTemporaryFile().name
    temp_name_path = tempfile.NamedTemporaryFile().name
    temp_name_path = "%s_really_unique" % temp_name_path
    assert temp_name != temp_name_path
    a_nfile = nfile.NFile(temp_name)
    assert temp_name_path != a_nfile.file_path
    new_nfile = a_nfile.save("content", path=temp_name_path)
    assert temp_name_path == new_nfile.file_path
    assert temp_name != a_nfile.file_path


def test_copy_flag_saves_to_path_only():
    temp_name = tempfile.NamedTemporaryFile().name
    temp_name_path = tempfile.NamedTemporaryFile().name
    temp_name_path = u"%s_really_unique" % temp_name_path
    assert temp_name != temp_name_path
    a_nfile = nfile.NFile(temp_name)
    a_nfile.save("content", path=temp_name_path)
    assert not os.path.exists(temp_name)
    assert os.path.exists(temp_name_path)


def test_file_is_read_properly():
    to_load_file = tempfile.NamedTemporaryFile()
    load_text = "Something to load"
    to_load_file.write(load_text.encode())
    to_load_file.seek(0)
    a_nfile = nfile.NFile(to_load_file.name)
    content = a_nfile.read()
    assert content == load_text


def test_file_read_blows_when_nonexistent_path():
    a_nfile = nfile.NFile()
    with pytest.raises(NinjaNoFileNameException):
        a_nfile.read()


def test_file_read_blows_on_nonexistent_file():
    temp_name = tempfile.NamedTemporaryFile().name
    a_nfile = nfile.NFile(temp_name)
    with pytest.raises(NinjaIOException):
        a_nfile.read()


def test_file_is_moved():
    temp_name = tempfile.NamedTemporaryFile().name
    new_temp_name = "%s_new" % temp_name
    test_content = "zero"
    temp_file = open(temp_name, "w")
    temp_file.write(test_content)
    temp_file.close()
    a_nfile = nfile.NFile(temp_name)
    a_nfile.move(new_temp_name)
    assert os.path.exists(new_temp_name)
    read_test_content = open(new_temp_name, "r")
    assert read_test_content.read() == test_content
    read_test_content.close()
    assert not os.path.exists(temp_name)


def test_move_changes_filepath():
    temp_name = tempfile.NamedTemporaryFile().name
    new_temp_name = "%s_new" % temp_name
    test_content = "zero"
    temp_file = open(temp_name, "w")
    temp_file.write(test_content)
    temp_file.close()
    a_nfile = nfile.NFile(temp_name)
    a_nfile.move(new_temp_name)
    assert a_nfile.file_path == new_temp_name


def test_filepath_changes_even_if_inexistent():
    temp_name = tempfile.NamedTemporaryFile().name
    a_nfile = nfile.NFile()
    a_nfile.move(temp_name)
    assert a_nfile.file_path == temp_name
