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
        with base_init as open(os.path.join(self.path, "__init__.py")):
            self.init_file(base_init, "py")

        #Create a setup.py
        #Create a basic main file

    def update_layout(self):
        """
        If you must (notice the version attribute) you can update a given
        project environment.
        You should save versions somehow in said project
        """
        pass

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