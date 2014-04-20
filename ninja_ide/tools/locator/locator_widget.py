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

from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL
from PyQt4.QtDeclarative import QDeclarativeView

from ninja_ide.core import settings
from ninja_ide.tools import ui_tools


class LocatorWidget(QDialog):
    """LocatorWidget class with the Logic for the QML UI"""

    def __init__(self, parent=None):
        super(LocatorWidget, self).__init__(
            parent, Qt.Dialog | Qt.FramelessWindowHint)
        self._parent = parent
        self.setModal(True)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background:transparent;")
        self.setFixedHeight(400)
        self.setFixedWidth(500)
        # Create the QML user interface.
        view = QDeclarativeView()
        view.setResizeMode(QDeclarativeView.SizeRootObjectToView)
        view.setSource(ui_tools.get_qml_resource("Locator.qml"))
        self._root = view.rootObject()
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        vbox.addWidget(view)

    def showEvent(self, event):
        """Method takes an event to show the Notification"""
        super(LocatorWidget, self).showEvent(event)
        #width, pgeo = self._parent.width() / 2, self._parent.geometry()
        #conditional_vertical = settings.NOTIFICATION_POSITION in (0, 1)
        #conditional_horizont = settings.NOTIFICATION_POSITION in (0, 2)
        #x = pgeo.left() if conditional_horizont else pgeo.right()
        #y = pgeo.bottom() if conditional_vertical else pgeo.top() - self._height
        #self.setFixedWidth(width)
        x = (self._parent.width() / 2) - (self.width() / 2)
        y = 0
        #y = self._parent.y() + self._main_container.combo_header_size
        self.setGeometry(x, y, self.width(), self.height())
        self._root.activateInput()
        #background_color = str(settings.NOTIFICATION_COLOR)
        #foreground_color = str(settings.NOTIFICATION_COLOR).lower().translate(
            #maketrans('0123456789abcdef', 'fedcba9876543210'))
        #self._root.setColor(background_color, foreground_color)
        #self._root.start(self._duration)

