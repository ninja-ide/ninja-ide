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

from PyQt5.QtCore import QObject

from ninja_ide.gui.ide import IDE


class ConflictingTypeForCategory(Exception):

    def __init__(self, project_type, category):
        self.__project_type = project_type
        self.__category = category
        super(ConflictingTypeForCategory, self).__init__()

    def __repr__(self):
        return "%s already has a type %s" % (self.__project_type,
                                             self.__category)

    def message(self):
        return repr(self)


class NTemplateRegistry(QObject):
    """
    Hold refere
    """

    def __init__(self):
        self.__project_types = {}
        self.__types_by_category = {}
        super(NTemplateRegistry, self).__init__()
        IDE.register_service("template_registry", self)

    def register_project_type(self, project_type):
        if project_type.compound_name() in self.__project_types.keys():
            raise ConflictingTypeForCategory(
                project_type.type_name,
                project_type.category
            )
        else:
            self.__project_types[project_type.compound_name()] = project_type
            # This is here mostly for convenience
            self.__types_by_category.setdefault(
                project_type.category, []).append(project_type)

    def list_project_types(self):
        return self.__project_types.keys()

    def list_project_categories(self):
        return self.__types_by_category.keys()

    def list_templates_for_cateogory(self, category):
        return self.__types_by_category.get(category, [])

    def get_project_type(self, project_type):
        return self.__project_types.get(project_type, None)

    @classmethod
    def create_compound_name(cls, type_name, category):
        return "%s_%s" % (type_name, category)


class BaseProjectType(QObject):
    """
    Any Project type defined should inherit from this.
    The only mandatory method is create_layout
    """

    type_name = "No Type"
    layout_version = "0.0"
    category = "No Category"
    encoding_string = {}
    single_line_comment = {}
    description = "No Description"

    def __init__(self, name, path, licence_text, licence_short_name="GPLv3",
                 base_encoding="utf-8"):
        self.name = name
        self.path = path
        self.base_encoding = base_encoding
        self.licence_short_name = licence_short_name
        self.licence_text = licence_text
        super(BaseProjectType, self).__init__()

    @classmethod
    def compound_name(cls):
        return NTemplateRegistry.create_compound_name(
            cls.type_name, cls.category)

    @classmethod
    def register(cls):
        """
        Just a convenience method that registers a given type
        """
        tr = IDE.get_service("template_registry")
        try:
            tr.register_project_type(cls)
        except ConflictingTypeForCategory:
            pass
        finally:
            return tr.get_project_type(cls.compound_name())

    def _create_path(self, path=None):
        path = path if path else self.path
        full_path = os.path.expanduser(path)
        split_path = full_path.split(os.path.sep)
        full_path = ""
        for each_folder in split_path:
            if each_folder:
                full_path += each_folder + "/"
            else:
                full_path += "/"
            if not os.path.exists(full_path):
                os.mkdir(full_path)

    @classmethod
    def wizard_pages(cls):
        """Return the pages to be displayed in the wizard."""

        raise NotImplementedError("%s lacks wizard_pages" %
                                  cls.__name__)

    @classmethod
    def from_dict(cls, results):
        """Create an instance from this project type using the wizard result"""
        raise NotImplementedError("%s lacks from_dict" %
                                  cls.__name__)

    def get_file_extension(self, filename):
        _, extension = os.path.splitext(filename)
        return extension[1:]

    def init_file(self, fd, filepath):
        """
        Adds encoding line and licence if possible
        """
        ext = self.get_file_extension(filepath)
        if self.base_encoding and (ext in self.encoding_string):
            fd.write(self.encoding_string[ext] % self.base_encoding + '\n')
        if self.licence_text and (ext in self.single_line_comment):
            for each_line in self.licence_text.splitlines():
                fd.write(self.single_line_comment[ext] + each_line + '\n')

    def _create_file(self, path, content):
        with open(path, "w") as writable:
            self.init_file(writable, path)
            writable.write(content)

    def create_layout(self, wizard):
        """
        Create set of folders and files required for this project bootstrap
        """
        raise NotImplementedError("%s lacks create_layout" %
                                  self.__class__.__name__)

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

    def get_project_wizard_pages(self):
        pass

    def wizard_callback(self):
        pass

    def _open_project(self, path):
        """Open Project based on path into Explorer"""

        projects_explorer = IDE.get_service("projects_explorer")
        projects_explorer.open_project_folder(path)


template_registry = NTemplateRegistry()
