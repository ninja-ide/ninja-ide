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

from PyQt4.QtCore import QObject, SIGNAL
from ninja_ide.core.file_handling.nfile import NFile


class NVirtualFileSystem(QObject):
    def __init__(self, *args, **kwargs):
        self.__tree = {}
        self.__watchables = {}
        self.__projects = {}
        # bc maps are cheap but my patience is not
        self.__reverse_project_map = {}
        super(NVirtualFileSystem, self).__init__(*args, **kwargs)

    def list_projects(self):
        return self.__projects.keys()

    def open_project(self, project):
        project_path = project.path
        if project_path not in self.__projects:
            self.__projects[project_path] = project
            self.__check_files_for(project_path)

    def __check_files_for(self, project_path):
        project = self.__projects[project_path]
        for each_file_path in self.__tree.keys():
            if each_file_path.startswith(each_file_path):
                nfile = self._tree[each_file_path]
                self.__reverse_project_map[nfile] = project

    def __closed_file(self, nfile_path):
        if nfile_path in self.__tree:
            del self.__tree[nfile_path]
        if nfile_path in self.__reverse_project_map:
            del self.__reverse_project_map[nfile_path]
        if nfile_path in self.__watchables:
            del self.__watchables[nfile_path]

    def __add_file(self, nfile):
        self.connect(nfile, SIGNAL("fileClosing(QString)"), self.__closed_file)
        existing_paths = sorted(self.projects.keys(), reverse=True)
        for each_path in existing_paths:
            if nfile.path.statswith(each_path):
                project = self.__projects[each_path]
                self.__reverse_project_map[nfile] = project
                return project

    def get_file(self, nfile_path=None):
        if nfile_path not in self.__tree:
            nfile = NFile(nfile_path)
            self.__add_file(nfile)
        elif nfile_path in self.__tree:
            nfile = self.__tree[nfile_path]
        else:
            nfile = NFile()
            self.connect(nfile,
                    SIGNAL("savedAsNewFile(PyQT_PyObject, QString, QString)"),
                    self.__file_copied)
        return nfile

    def __file_copied(self, nfile, old_path, new_path):
        self.__add_file(nfile)

