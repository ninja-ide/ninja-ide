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
import imp
from ninja_ide import resources


class ExtensionRegistry(type):

    extensions = []

    def __new__(cls, classname, bases, attrs):
        klass = super().__new__(cls, classname, bases, attrs)
        if classname != 'Extension':
            extension_name = attrs.get('name', attrs['__module__'])
            klass.name = extension_name
            cls.extensions.append(klass)
        return klass


class Extension(metaclass=ExtensionRegistry):
    """Base class for Editor extensions"""

    name = None
    version = None

    @property
    def enabled(self):
        """Tells if the extension is enabled"""
        return self.__enabled

    @enabled.setter
    def enabled(self, value):
        if value != self.__enabled:
            self.__enabled = value
            if value:
                self.install()
            else:
                self.shutdown()

    def __init__(self, neditor):
        self.__enabled = False
        # NINJA-IDE NEditor ref
        self._neditor = neditor

    def text_cursor(self):
        return self._neditor.textCursor()

    def install(self):
        """Turn on the extension on the NINJA-IDE editor
        This method is called when extension is enabled.
        You may override it if you need to connect editor's signals
        """

    def shutdown(self):
        """Turn off the extension on the NINJA-IDE editor
        This method is called when extension is disabled.
        You may override it if you need to disconnect editor's signals
        """


def discover_all(extensions_dir='.'):
    extensions_dir = os.path.join(resources.PRJ_PATH,
                                  "gui", "editor", "extensions")
    for filename in os.listdir(extensions_dir):
        module_name, ext = os.path.splitext(filename)
        if ext == '.py' and not filename.startswith('__'):
            _file, path, descr = imp.find_module(module_name, [extensions_dir])
            if _file:
                imp.load_module(module_name, _file, path, descr)
