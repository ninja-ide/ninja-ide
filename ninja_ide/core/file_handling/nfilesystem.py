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
from PyQt5.QtWidgets import QFileSystemModel
from PyQt5.QtCore import (
    QObject,
    QDir,
    pyqtSignal
)
from ninja_ide.core.file_handling.nfile import NFile
from ninja_ide.tools import ui_tools
from ninja_ide.tools.logger import NinjaLogger
logger = NinjaLogger('ninja_ide.core.file_handling.nfilesystem')


class NVirtualFileSystem(QObject):
    # Signals
    projectOpened = pyqtSignal('QString')
    projectClosed = pyqtSignal('QString')

    def __init__(self, *args, **kwargs):
        self.__tree = {}
        self.__watchables = {}
        self.__projects = {}
        # bc maps are cheap but my patience is not
        self.__reverse_project_map = {}
        super(NVirtualFileSystem, self).__init__(*args, **kwargs)

    def list_projects(self):
        return list(self.__projects.keys())

    def open_project(self, project):
        project_path = project.path
        qfsm = None  # Should end up having a QFileSystemModel
        if project_path not in self.__projects:
            qfsm = QFileSystemModel()
            project.model = qfsm
            qfsm.setRootPath(project_path)
            qfsm.setFilter(QDir.AllDirs | QDir.Files | QDir.NoDotAndDotDot)
            # If set to true items that dont match are displayed disabled
            qfsm.setNameFilterDisables(False)
            pext = ["*{0}".format(x) for x in project.extensions]
            logger.debug(pext)
            qfsm.setNameFilters(pext)
            self.__projects[project_path] = project
            self.__check_files_for(project_path)
            self.projectOpened.emit(project_path)
        else:
            qfsm = self.__projects[project_path]
        return qfsm

    def refresh_name_filters(self, project):
        qfsm = project.model
        if qfsm:
            pext = ["*{0}".format(x) for x in project.extensions]
            logger.debug(pext)
            qfsm.setNameFilters(pext)

    def close_project(self, project_path):
        if project_path in self.__projects:
            project_root = self.__projects[project_path]
            nfiles = list(self.__tree.values())
            for nfile in nfiles:
                if self.__reverse_project_map[nfile] == project_root:
                    del self.__tree[nfile.file_path]
                    nfile.close()
            # This might not be needed just being extra cautious
            del self.__projects[project_path].model
            del self.__projects[project_path]
            self.projectClosed.emit(project_path)

    def __check_files_for(self, project_path):
        project = self.__projects[project_path]
        for each_file_path in list(self.__tree.keys()):
            nfile = self.__tree[each_file_path]
            if nfile.file_path.startswith(project_path):
                self.__reverse_project_map[nfile] = project

    def __closed_file(self, nfile_path):
        if nfile_path in self.__tree:
            del self.__tree[nfile_path]
        if nfile_path in self.__reverse_project_map:
            del self.__reverse_project_map[nfile_path]
        if nfile_path in self.__watchables:
            del self.__watchables[nfile_path]

    def __add_file(self, nfile):
        nfile.fileClosing['QString', bool].connect(self.__closed_file)
        existing_paths = sorted(list(self.__projects.keys()), reverse=True)
        self.__tree[nfile.file_path] = nfile
        for each_path in existing_paths:
            if nfile.file_path.startswith(each_path):
                project = self.__projects[each_path]
                self.__reverse_project_map[nfile] = project
                return project

    def get_file(self, nfile_path=None):
        if nfile_path is None:
            return NFile(nfile_path)
        if os.path.isdir(nfile_path):
            return None
        if nfile_path not in self.__tree:
            nfile = NFile(nfile_path)
            self.__add_file(nfile)
        elif nfile_path in self.__tree:
            nfile = self.__tree[nfile_path]
        else:
            nfile = NFile()
            nfile.saveAsNewFile['PyQt_PyObject',
                                'QString',
                                'QString'].connect(self.__file_copied)
        return nfile

    def __file_copied(self, nfile, old_path, new_path):
        self.__add_file(nfile)

    def get_projects(self):
        return self.__projects

    def get_project_for_file(self, filename):
        nfile = self.get_file(filename)
        project = self.__reverse_project_map.get(nfile, None)
        return project

    def get_files(self):
        return self.__tree
