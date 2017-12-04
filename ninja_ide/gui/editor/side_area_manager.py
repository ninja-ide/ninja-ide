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

"""Manager for side areas"""

from PyQt5.QtCore import (
    QObject,
    pyqtSlot,
    pyqtSignal
)


class SideAreaManager(QObject):

    updateViewportMarginsRequested = pyqtSignal(int)

    def __init__(self, neditor):
        super().__init__()
        self.neditor = neditor
        self.__widgets = {}
        self.neditor.blockCountChanged.connect(self._update_margins)

    def add_area(self, widget):
        widget.setParent(self.neditor)
        self.__widgets[widget.object_name] = widget

    @pyqtSlot()
    def _update_margins(self):
        print("Updating margins...")
        total_width = 0
        for side_area in self.__widgets.values():
            width = side_area.width()
            total_width += width
        self.updateViewportMarginsRequested.emit(total_width)
