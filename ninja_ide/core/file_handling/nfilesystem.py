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
from PyQt4.QtCore import QObject
from ninja.core.file_handling.nfile import NFile


class NVirtualFolder(QObject):
    def __init__(self, path, node, *args, **kwargs):
        self.__path = path # an os representation of the path
        self.__nodes = []
        #Listen to will save and will create

    def list(self):
        pass

    def create(self):
        #Make this a class method that returns a Nvirtualfolder and creates the given folder if it does not exists
        pass # Create this folder if it does not exist

    def add_node(self, node):
        #TODO: Do some magic here to hook watcher or not
        self.__nodes.append(node)


class NVirtualFileSystem(QObject):
    def __init__(self, *args, **kwargs):
        self.__tree = {}
        self.__watchables = {}
        super(NVirtualFileSystem, self).__init__(*args, **kwargs)

    def open(self, path):
        if os.path.isfile(path):
            if path in self._tree:
                fopen = self.__tree.get(path)
            else:
                fopen = self.__tree.setdefault(path, NFile(path))
                self._append_into_watchable(path, fopen)

        elif os.path.isdir(path):
            fopen = self.__watchables.setdefault(path, NVirtualFolder(path))
        else:
            fopen = self.create_file(path)
            self._append_into_watchable(path, fopen)
        return fopen

    def create_file(self, path):
        pass

    def create_folder(self, path):
        pass

    def _append_into_watchable(self, path, fopen):
        #Lets take the path that looks the most like ours
        for each_watchable in sorted(self.__watchables.keys(), reverse=True):
            if path.startswith(each_watchable):
                return self.__watchables[each_watchable].add_node(fopen)





