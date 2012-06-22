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


class ITabItem(object):

    EXTRA_MENU = {}

    def __init__(self):
        self._id = ""    # Should be unique
        self.wasModified = False

        self._parentTab = None

    def get_id(self):
        return self._id

    def set_id(self, id_):
        self._id = id_
        if id_:
            self.newDocument = False

    ID = property(lambda self: self.get_id(), lambda self,
        fileName: self.set_id(fileName))

    def __eq__(self, path):
        """Compares if the path (str) received is equal to the id"""
        return self._id == path

    @classmethod
    def add_extra_menu(cls, menu, lang="py"):
        if not lang in cls.EXTRA_MENU:
            cls.EXTRA_MENU[lang] = []

        cls.EXTRA_MENU[lang].append(menu)
