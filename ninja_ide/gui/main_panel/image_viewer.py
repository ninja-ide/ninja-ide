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

from PyQt4.QtGui import QScrollArea
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QPixmap

from ninja_ide.gui.main_panel import itab_item


class ImageViewer(QScrollArea, itab_item.ITabItem):

    def __init__(self, image):
        super(ImageViewer, self).__init__()
        itab_item.ITabItem.__init__(self)
        self._id = image

        self.label = QLabel()
        pixmap = QPixmap(image)
        self.label.setPixmap(pixmap)
        self.setWidget(self.label)
