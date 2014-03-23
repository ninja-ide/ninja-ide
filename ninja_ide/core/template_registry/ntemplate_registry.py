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
from PyQt4.QtCore import QObject


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

    def register_project_type(self, ptype):
        if ptype.compount_name in self.__project_types.keys():
            self.__project_types[ptype.compound_name] = ptype
            #This is here mostly for convenience
            self.__types_by_category.setdefault(ptype.cateogory,
                                                []).append(ptype)
        else:
            raise ConflictingTypeForCategory(ptype.name, ptype.category)

    def list_project_types(self):
        return self.__registry_data.keys()

    def list_project_categories(self):
        return self.__types_by_category.keys()

    def list_templates_for_cateogory(self, category):
        return self.__types_by_category.get(category, [])

    def get_project_type(self, ptype):
        return self.__project_types.get(ptype, None)


class BaseProjectType(QObject):
    """
    Any Project type defined should inherit from this.
    The only mandatory method is create_layout
    """

    def __init__(self, category, name, path, version=None):
        self.name = name
        self.category = category
        self.path = path
        self.description = ""
        self.layout_version = version
        super(BaseProjectType, self).__init__()

    @property
    def compound_name(self):
        return "%s_%s" % (self.name, self.category)

    def create_layout(self):
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
