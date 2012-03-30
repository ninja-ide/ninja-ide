# -*- coding: utf-8 -*-
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
