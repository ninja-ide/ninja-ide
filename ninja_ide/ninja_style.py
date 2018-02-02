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

from PyQt5.QtWidgets import QProxyStyle
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QStyleFactory
from PyQt5.QtGui import QPalette
from PyQt5.QtGui import QColor

from ninja_ide import resources


class NinjaStyle(QProxyStyle):

    def __init__(self, theme):
        QProxyStyle.__init__(self)
        self.setBaseStyle(QStyleFactory.create("fusion"))
        self._palette = theme["palette"]
        self._qss = theme["stylesheet"]

    def polish(self, args):
        if isinstance(args, QPalette):
            palette = args
            for role, color in self._palette.items():
                qcolor = QColor(color)
                color_group = QPalette.All
                if role.endswith("Disabled"):
                    role = role.split("Disabled")[0]
                    color_group = QPalette.Disabled
                elif role.endswith("Inactive"):
                    role = role.split("Inactive")[0]
                    qcolor.setAlpha(90)
                    color_group = QPalette.Inactive
                color_role = getattr(palette, role)
                palette.setBrush(color_group, color_role, qcolor)
        elif isinstance(args, QApplication):
            # Set style sheet
            filename = os.path.join(resources.NINJA_QSS, self._qss)
            with open(filename + ".qss") as fileaccess:
                qss = fileaccess.read()
            args.setStyleSheet(qss)
        return QProxyStyle.polish(self, args)
