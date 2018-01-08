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


class Extension(object):
    """Base class for Editor extensions"""

    name = None  # Identifier

    @property
    def actived(self):
        """Tells if the extension is enabled"""

    @actived.setter
    def actived(self, value):
        if value != self.__actived:
            self.__actived = value
            if value:
                self.install()
            else:
                self.shutdown()

    def __init__(self):
        self.name = self.__class__.__name__
        self._neditor = None
        self.__actived = False

    def initialize(self, neditor):
        """Initialize the extension"""

        self._neditor = neditor  # NINJA-IDE Neditor ref
        self.actived = True

    def text_cursor(self):
        """Returns the current QTextCursor"""

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
