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

from PyQt5.QtWidgets import QScrollArea
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap


class ImageViewer(QScrollArea):

    def __init__(self, image):
        super(ImageViewer, self).__init__()

        self.label = QLabel()
        pixmap = QPixmap(image)
        self.label.setPixmap(pixmap)
        self.setWidget(self.label)
