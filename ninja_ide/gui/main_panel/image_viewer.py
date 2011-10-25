# -*- coding: utf-8 -*-
from __future__ import absolute_import

from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QPixmap

from ninja_ide.gui.main_panel import itab_item


class ImageViewer(QLabel, itab_item.ITabItem):

    def __init__(self, image):
        QLabel.__init__(self)
        itab_item.ITabItem.__init__(self)
        pixmap = QPixmap(image)
        self.setPixmap(pixmap)
        self._id = image
