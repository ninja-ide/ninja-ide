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

from PyQt5.QtWidgets import QGraphicsView
from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QGraphicsPixmapItem

from PyQt5.QtGui import QPainter
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QBrush

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import Qt

from ninja_ide import translations
from ninja_ide.core.file_handling import file_manager


class ImageViewer(QGraphicsView):

    scaleFactorChanged = pyqtSignal(float)
    imageSizeChanged = pyqtSignal("QSize")

    SCALE_FACTOR = 1.2

    def __init__(self, filename):
        super().__init__()
        self.image_filename = filename
        self.setScene(QGraphicsScene(self))
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setFrameShape(QGraphicsView.NoFrame)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        # Menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_menu)
        # Draw background
        pix = QPixmap(64, 64)
        pix.fill(QColor("#1e1e1e"))
        painter = QPainter(pix)
        color = QColor(20, 20, 20)
        painter.fillRect(0, 0, 32, 32, color)
        painter.fillRect(32, 32, 32, 32, color)
        painter.end()
        self.setBackgroundBrush(QBrush(pix))

    def _show_menu(self, point):
        menu = QMenu(self)
        fit_action = menu.addAction(translations.TR_FIT_TO_SCREEN)
        fit_action.triggered.connect(self.fit_to_screen)
        restore_action = menu.addAction(translations.TR_RESTORE_SIZE)
        restore_action.triggered.connect(self.restore_to_original_size)

        menu.exec_(self.mapToGlobal(point))

    def display_name(self):
        return file_manager.get_basename(self.image_filename)

    def create_scene(self):
        pixmap = QPixmap(self.image_filename)
        size = pixmap.size()
        self.imageSizeChanged.emit(size)
        self._item = QGraphicsPixmapItem(pixmap)
        self._item.setCacheMode(QGraphicsPixmapItem.NoCache)
        self._item.setZValue(0)
        self.scene().addItem(self._item)
        self.__emit_scale_factor()

    def __emit_scale_factor(self):
        factor = self.transform()
        self.scaleFactorChanged.emit(factor.m11())

    def zoom_in(self):
        self.__scale(self.SCALE_FACTOR)

    def zoom_out(self):
        self.__scale(1 / self.SCALE_FACTOR)

    def __scale(self, factor):
        current = self.transform().m11()
        new = current * factor
        actual = factor
        if new > 1000:
            actual = 1000 / current
        elif new < 0.001:
            actual = 0.001 / current
        self.scale(actual, actual)
        self.__emit_scale_factor()

    def drawBackground(self, painter, rect):
        painter.save()
        painter.resetTransform()
        painter.drawTiledPixmap(
            self.viewport().rect(), self.backgroundBrush().texture())
        painter.restore()

    def restore_to_original_size(self):
        self.resetTransform()
        self.__emit_scale_factor()

    def fit_to_screen(self):
        self.fitInView(self._item, Qt.KeepAspectRatio)
        self.__emit_scale_factor()

    def wheelEvent(self, event):
        factor = self.SCALE_FACTOR ** (event.angleDelta().y() / 240.0)
        self.__scale(factor)
        event.accept()
