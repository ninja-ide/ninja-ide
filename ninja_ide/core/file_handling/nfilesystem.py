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
from PyQt4.QtCore import QObject, SIGNAL
from ninja.core.file_handling.nfile import NFile


class NVirtualFolder(QObject):
    def __init__(self, path, *args, **kwargs):
        self.__path = path  # an os representation of the path
        self.__nodes = []
        #Listen to will save and will create

    def list(self):
        for each_node in self.__nodes:
            yield each_node.path, each_node

    def list_all(self):
        for each_item in os.listdir(self.__path):
            yield os.path.isdir(each_item), each_item

    def _exists(self):
        return os.path.exists(self.__path)

    def create(self):
        #Make this a class method that returns a Nvirtualfolder and creates
        #the given folder if it does not exists
        os.mkdir(self.__path)

    def add_node(self, node):
        #TODO: Do some magic here to hook watcher or not
        self.connect(SIGNAL("willSave(QString, QString)"),
                                                        self.__save_child)
        self.connect(SIGNAL("willMove(PyQt_PyObject, QString, QString)"),
                                                        self.__move_child)
        self.connect(SIGNAL("willDelete(PyQt_PyObject, PyQt_PyObject)"),
                                                            self.__delete_child)
        self.connect(SIGNAL("willOverWrite(PyQt_PyObject, QString, QString)"),
                                                            self.__overwrite)
        self.__nodes.append(node)

    def __save_child(self, temp_path, final_path):
        if not self._exists():
            self.create()

    def __delete_child(self, signal_handler, child_path):
        pass

    def __move_child(self, signal_handler, old_path, new_path):
        pass

    def __overwrite(self, signal_handler, old_path, new_path):
        pass


class NVirtualFileSystem(QObject):
    def __init__(self, *args, **kwargs):
        self.__tree = {}
        self.__watchables = {}
        super(NVirtualFileSystem, self).__init__(*args, **kwargs)

    def open(self, path, folder=False):
        if os.path.isfile(path):
            if path in self._tree:
                fopen = self.__tree.get(path)
            else:
                fopen = self.__tree.setdefault(path, NFile(path))
                self._append_into_watchable(path, fopen)

        elif os.path.isdir(path):
            fopen = self.__tree.setdefault(path, NVirtualFolder(path))
            self._append_into_watchable(path, fopen)
        elif folder:
            fopen = self.__tree.setdefault(path, self.create_folder(path))
            self._append_into_watchable(path, fopen)
        else:
            fopen = self.__tree.setdefault(path, NFile(path))
            self._append_into_watchable(path, fopen)
        return fopen

    def create_folder(self, path):
        folder = NVirtualFolder(path)
        self._append_into_watchable(path, folder)
        return folder

    def _append_into_watchable(self, path, fopen):
        #Lets take the path that looks the most like ours
        for each_watchable in sorted(self.__watchables.keys(), reverse=True):
            if path.startswith(each_watchable):
                return self.__watchables[each_watchable].add_node(fopen)

    def list(self, path=None):
        if path is None:
            for each_key in self.__watchables.keys():
                yield each_key
        else:
            folder = self.__tree.get(path, None)
            if folder and isinstance(folder, NVirtualFolder):
                return folder.list()
