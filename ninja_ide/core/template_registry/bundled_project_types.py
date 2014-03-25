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

from ninja_ide.core.template_registry.ntemplate_registry import BaseProjectType


SETUP_PY_FILE = \
    r"""
    #BEWARE: This is a minimal version you will most likely need to extend it
    from setuptools import setup, find_packages

    setup(name='%s',
          version='1.0',
          packages=find_packages(),
          )
"""

BASIC_HELLO = \
    r"""
    #This is a sample yet useful program, for python 3
    def hello_world():
        print("hello world, this is %s's main")
    """


class PythonProject(BaseProjectType):

    type_name = "Basic Python Project"
    layout_version = "0.1"
    category = "Python"
    encoding_string = {"py", "# -*- coding: %s -*-"}
    single_line_comment = {"py", "#"}
    description = \
        """A plugin that creates the layout for a basic python project
        """

    def __init__(self, *args, **kwargs):
        super(PythonProject, self).__init__(*args, **kwargs)

    def create_layout(self):
        """
        Create set of folders and files required for a basic python project
        """
        full_path = os.path.expanduser(self.path)
        split_path = full_path.split(os.path.sep)
        full_path = ""
        for each_folder in split_path:
            if each_folder:
                full_path += each_folder + "/"
            else:
                full_path += "/"
            if not os.path.exists(full_path):
                os.mkdir(full_path)

        #Create a single init file
        filepath = os.path.join(self.path, "__init__.py")
        with open(filepath, "r") as base_init:
            self.init_file(base_init, filepath)

        #Create a setup.py
        filepath = os.path.join(self.path, "setup.py")
        with open(filepath, "r") as base_setup:
            self.init_file(base_setup, filepath)
            base_setup.write(SETUP_PY_FILE % self.name)

        #Create a basic main file
        filepath = os.path.join(self.path, "main.py")
        with open(filepath, "r") as base_main:
            self.init_file(base_main, filepath)
            base_setup.write(BASIC_HELLO % self.name)

    def get_project_api(self):
        """
        Here we expect you to return a QMenu with wathever you need inside.
        Bare in mind that we will add this to the context menu on the
        project tree but we might use it elsewere, not guaranteed.
        """
        pass

    def get_project_file_api(self):
        """
        This is exactly the same as 'get_project_api' but for files.
        You should return a tuple containing:
        (evaluate_pertinence_function, QMenu)
        Where evaluate_pertinence is a function that will receive the file
        path and return True/False if the QMenu is apt for said file.
        """
        pass


PythonProject.register()