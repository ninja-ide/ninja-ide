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
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QStyleOption
from PyQt5.QtWidgets import QStyle

from PyQt5.QtGui import QPainter
from PyQt5.QtGui import QColor

from ninja_ide.tools import ui_tools
from ninja_ide.gui.ide import IDE


class ToolBar(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("toolbar")
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self._action_layout = QVBoxLayout()
        self._action_layout.setContentsMargins(0, 0, 0, 0)
        spacer = QVBoxLayout(self)
        spacer.addLayout(self._action_layout)
        spacer.addStretch()
        spacer.addSpacing(2)
        spacer.setContentsMargins(0, 0, 0, 0)

    def add_action(self, action):
        button = ui_tools.CoolToolButton(action, self)
        self._action_layout.addWidget(button)

    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)


class NToolBar(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 1, 0)
        layout.setSpacing(0)

        self._toolbar = ToolBar(self)
        layout.addWidget(self._toolbar)

        self._action_bar = ActionBar(self)
        self.add_corner_widget(self._action_bar)

        IDE.register_service("toolbar", self)

    def add_actionbar_item(self, action):
        self._action_bar.add_action(action)

    def add_action(self, action):
        self._toolbar.add_action(action)

    def add_corner_widget(self, widget):
        self.layout().addWidget(widget)


class ActionBar(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("toolbar_actionbar")
        self._action_layout = QVBoxLayout()
        self._action_layout.setContentsMargins(0, 0, 0, 0)
        spacer = QVBoxLayout(self)
        spacer.addLayout(self._action_layout)
        spacer.addSpacing(10)
        spacer.setContentsMargins(0, 0, 0, 0)
        spacer.setSpacing(0)
        self.setContentsMargins(0, 0, 0, 0)

    def add_action(self, action=None):
        button = ui_tools.CoolToolButton(action=action, parent=self)
        self._action_layout.addWidget(button)

    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)

    def minimumSizeHint(self):
        return self.sizeHint()
