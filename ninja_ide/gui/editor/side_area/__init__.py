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

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import (
    QColor,
    QPainter
)
from ninja_ide import resources


class SideArea(QWidget):
    """
    Base class for editor side areas
    """

    # FIXME: update width on resize
    def __init__(self, neditor):
        QWidget.__init__(self, neditor)
        self.object_name = self.__class__.__name__
        self.__background_color = QColor(resources.get_color('SidebarBackground'))
        neditor.updateRequest.connect(self.update)
        self.neditor = neditor

    def paintEvent(self, event):
        if self.isVisible():
            painter = QPainter(self)
            painter.fillRect(event.rect(), self.__background_color)
