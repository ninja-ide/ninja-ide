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


# Get project types
# Project type is language
# Should have subtype, which is pyqt, ninja plugin, pytk, etc...

# We provide the first window of the wizard, to do this everyone will inherit
# from us
from PyQt4.QtGui import QDialog
from PyQt4.QtCore import Qt


class NewProjectTypeChooser(QDialog):

    def __init__(self, parent=None):
        super(NewProjectTypeChooser, self).__init__(parent, Qt.Dialog)
        pass
