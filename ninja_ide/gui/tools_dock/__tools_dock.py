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

from PyQt5.QtWidgets import (
    QWidget
)
from ninja_ide.gui.ide import IDE


class ToolsDock(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedHeight(30)
        IDE.register_service("tools_dock", self)

    def install(self):

        ninja_ide = IDE.get_service("ide")
        # ninja_ide.place_me_on("tools_dock", self, "central")


ToolsDock()
