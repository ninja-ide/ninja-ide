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

from string import maketrans

from PyQt4.QtGui import QFrame
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL
from PyQt4.QtDeclarative import QDeclarativeView

from ninja_ide.core import settings
from ninja_ide.tools import ui_tools


class Notification(QFrame):
    """Notification class with the Logic for the QML UI"""

    def __init__(self, parent=None):
        super(Notification, self).__init__(None, Qt.ToolTip)
        self._parent = parent
        self._duration = 3000
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setStyleSheet("background:transparent")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFixedHeight(30)
        # Create the QML user interface.
        view = QDeclarativeView()
        view.setResizeMode(QDeclarativeView.SizeRootObjectToView)
        view.setSource(ui_tools.get_qml_resource("Notification.qml"))
        self._root = view.rootObject()
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        vbox.addWidget(view)

        self.connect(self._root, SIGNAL("close()"), self.close)

    def showEvent(self, event):
        """Method takes an event to show the Notification"""
        super(Notification, self).showEvent(event)
        width, pgeo = self._parent.width(), self._parent.geometry()
        conditional_vertical = settings.NOTIFICATION_POSITION in (0, 1)
        conditional_horizontal = settings.NOTIFICATION_POSITION in (0, 2)
        x = pgeo.left() if conditional_horizontal else pgeo.right()
        y = (pgeo.bottom() - self.height()
             if conditional_vertical else pgeo.top())
        self.setFixedWidth(width)
        self.setGeometry(x, y, self.width(), self.height())
        background_color = str(settings.NOTIFICATION_COLOR)
        foreground_color = str(settings.NOTIFICATION_COLOR).lower().translate(
            maketrans('0123456789abcdef', 'fedcba9876543210'))
        self._root.setColor(background_color, foreground_color)
        self._root.start(self._duration)

    def set_message(self, text='', duration=3000):
        """Method that takes str text and int duration to setup Notification"""
        self._root.setText(text)
        self._duration = duration
