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
from __future__ import unicode_literals

from PyQt5.QtCore import (
    QSettings,
    pyqtSignal
)


class NSettings(QSettings):
    """Extend QSettings to emit a signal when a value change."""

    valueChanged = pyqtSignal("QString", "PyQt_PyObject")

    def __init__(self, path, fformat=QSettings.IniFormat):
        super().__init__(path, fformat)

    def setValue(self, key, value):
        super().setValue(key, value)
        self.valueChanged.emit(key, value)


'''class NSettings(QSettings):

    """
    Extend QSettings to emit a signal when a value change.
    @signals:
    valueChanged(QString, PyQt_PyObject)
    """
    valueChanged = pyqtSignal('PyQt_PyObject', 'QString', 'PyQt_PyObject')

    def __init__(self, path, obj=None, fformat=QSettings.IniFormat, prefix=''):
        super(NSettings, self).__init__(path, fformat)
        self.__prefix = prefix
        self.__object = obj

    def setValue(self, key, value):
        super(NSettings, self).setValue(key, value)
        key = "%s_%s" % (self.__prefix, key)
        self.valueChanged.emit(self.__object, key, value)
'''