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


class SideWidget(QWidget):
    """
    Base class for editor side widgets
    """

    def __init__(self):
        QWidget.__init__(self)
        self.object_name = self.__class__.__name__
        self.order = -1

    def register(self, neditor):
        """Set the NEditor instance as the parent widget

        When override this method, call super!
        """
        self.setParent(neditor)
        self._neditor = neditor

    def paintEvent(self, event):
        if self.isVisible():
            background_color = QColor(
                resources.COLOR_SCHEME.get("editor.sidebar.background"))
                # resources.get_color('SidebarBackground'))
            painter = QPainter(self)
            painter.fillRect(event.rect(), background_color)

    def setVisible(self, value):
        """Show/Hide the widget"""
        QWidget.setVisible(self, value)
        self._neditor.side_widgets.update_viewport()
