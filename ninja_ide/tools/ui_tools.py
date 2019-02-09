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
import math
import collections
from urllib.parse import urlparse, urlunparse

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QToolButton
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QCompleter
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QItemDelegate
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtWidgets import QShortcut
from PyQt5.QtWidgets import QTreeWidgetItem
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QStyle

from PyQt5.QtGui import QKeyEvent
from PyQt5.QtGui import QLinearGradient
from PyQt5.QtGui import QPalette
from PyQt5.QtGui import QPainter
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtGui import QBrush
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QPixmapCache
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QPen
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QImage
from PyQt5.QtGui import QKeySequence
from PyQt5.QtGui import qGray
from PyQt5.QtGui import qRgba
from PyQt5.QtGui import qAlpha

from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtPrintSupport import QPrintPreviewDialog

from PyQt5.QtCore import Qt
from PyQt5.QtCore import QSize
from PyQt5.QtCore import pyqtProperty
from PyQt5.QtCore import QDir
from PyQt5.QtCore import QUrl
from PyQt5.QtCore import QObject
from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QEvent
from PyQt5.QtCore import QTimeLine
from PyQt5.QtCore import QRect
from PyQt5.QtCore import QPoint
from PyQt5.QtCore import QPropertyAnimation

from ninja_ide import resources
from ninja_ide.core import settings
from ninja_ide.core.file_handling import file_manager
from ninja_ide.core.file_handling.file_manager import NinjaIOException
from ninja_ide.tools import json_manager


from ninja_ide.tools.logger import NinjaLogger

logger = NinjaLogger('ninja_ide.tools.ui_tools')


###############################################################################
# ToolBar
###############################################################################

class Tab(QObject):

    def __init__(self, parent):
        QObject.__init__(self, parent)
        self._toolbar = parent
        self.icon = None
        self.text = ""
        self.has_menu = False
        self.enabled = True
        self._fader = 0
        self._animator = QPropertyAnimation(self)
        self._animator.setPropertyName(b"fader")
        self._animator.setTargetObject(self)

    def fade_in(self):
        self._animator.stop()
        self._animator.setDuration(80)
        self._animator.setEndValue(1)
        self._animator.start()

    def fade_out(self):
        self._animator.stop()
        self._animator.setDuration(160)
        self._animator.setEndValue(0)
        self._animator.start()

    def _set_fader(self, value):
        self._fader = value
        self._toolbar.update()

    def _get_fader(self):
        return self._fader

    fader = pyqtProperty(float, fget=_get_fader, fset=_set_fader)


class ToolBar(QWidget):

    currentChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.setMinimumWidth(40)
        self.setAttribute(Qt.WA_Hover, True)
        self.setFocusPolicy(Qt.NoFocus)
        self.setMouseTracking(True)

        self.__hover_index = -1
        self.__current_index = -1
        self.__tabs = []

    def insert_tab(self, index, icon=None):
        tab = Tab(self)
        tab.icon = icon
        self.__tabs.insert(index, tab)
        if self.__current_index >= index:
            self.__current_index += 1
        self.updateGeometry()

    def add_tab(self, icon):
        tab = Tab(self)
        tab.icon = icon
        self.__tabs.append(tab)
        self.__current_index += 1
        self.updateGeometry()

    def current_index(self):
        return self.__current_index

    def set_current_index(self, index):
        if index != self.__current_index:
            self.__current_index = index
            self.update()
            self.currentChanged.emit(index)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(event.rect(), QColor("#2e3135"))

        for index in range(self.count()):
            if index != self.current_index():
                self._paint_tab(painter, index)

        if self.current_index() != -1:
            self._paint_tab(painter, self.current_index())

    def _paint_tab(self, painter, index):
        if not self._is_valid_index(index):
            return

        painter.save()
        tab = self.__tabs[index]
        rect = self._tab_rect(index)
        selected = index == self.__current_index
        enabled = self._is_enabled(index)

        if selected:
            painter.fillRect(rect, QColor("#161719"))

        tab_icon_rect = QRect(rect)
        if selected:
            color = QColor(255, 255, 255, 160)
        else:
            color = QColor(0, 0, 0, 110)
        painter.setPen(color)

        fader = self.__tabs[index].fader
        if fader > 0 and not selected and enabled:
            painter.save()
            painter.setOpacity(fader)
            painter.fillRect(rect, QColor("#424242"))
            painter.restore()

        if tab.icon is not None:
            icon_rect = QRect(0, 0, 20, 20)
            icon_rect.moveCenter(tab_icon_rect.center())
            tab.icon.paint(painter, rect)

        painter.setOpacity(1.0)
        if enabled:
            painter.setPen(QColor("#ffffff"))
        else:
            painter.setPen(QColor("blue"))
        painter.translate(0, -1)

        painter.restore()

    def sizeHint(self):
        sh = self._tab_size_hint()
        return QSize(sh.width(), sh.height() * len(self))

    def minimumSizeHint(self):
        sh = self._tab_size_hint(minimum=True)
        return QSize(sh.width(), sh.height() * len(self))

    def enterEvent(self, event):
        self.__hover_rect = QRect()
        self.__hover_index = -1

    def leaveEvent(self, event):
        self.__hover_index = -1
        self.__hover_rect = QRect()
        for tab in self.__tabs:
            tab.fade_out()

    def mousePressEvent(self, event):
        event.accept()
        for index in range(len(self)):
            rect = self._tab_rect(index)
            if rect.contains(event.pos()):
                if self._is_enabled(index):
                    self.__current_index = index
                    self.update()
                    self.currentChanged.emit(self.__current_index)
                break

    def mouseMoveEvent(self, event):
        new_hover = -1
        for index in range(len(self)):
            area = self._tab_rect(index)
            if area.contains(event.pos()):
                new_hover = index
                break

        if new_hover == self.__hover_index:
            return

        if self._is_valid_index(self.__hover_index):
            self.__tabs[self.__hover_index].fade_out()

        self.__hover_index = new_hover

        if self._is_valid_index(self.__hover_index):
            self.__tabs[self.__hover_index].fade_in()
            self.__hover_rect = self._tab_rect(self.__hover_index)

    def _is_enabled(self, index):
        if index < len(self) and index >= 0:
            return self.__tabs[index].enabled
        return False

    def _tab_rect(self, index):
        sh = self._tab_size_hint()
        if sh.height() * len(self.__tabs) > self.height():
            sh.setHeight(self.height() / len(self.__tabs))
        return QRect(0, index * sh.height(), sh.width(), sh.height())

    def _tab_size_hint(self, minimum=False):
        bold_font = self.font()
        bold_font.setPointSizeF(7.5)
        bold_font.setBold(True)
        fm = QFontMetrics(bold_font)
        spacing = 10
        width = 40 + spacing + 2
        max_label_width = 0
        for tab in self.__tabs:
            _width = fm.width(tab.text)
            if _width > max_label_width:
                max_label_width = _width
        icon_height = 0 if minimum else 32
        return QSize(
            max(width, max_label_width + 4),
            icon_height + spacing + fm.height())

    def _is_valid_index(self, index):
        return index >= 0 and index < len(self.__tabs)

    def __len__(self):
        return len(self.__tabs)

    def count(self):
        return len(self)


###############################################################################
# Fancy Tool Button
###############################################################################

class FancyButton(QToolButton):

    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_Hover, True)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        if text:
            self.setText(text)
        self._fader = 0

    def _set_fader(self, value):
        self._fader = value
        self.update()

    def _get_fader(self):
        return self._fader

    fader = pyqtProperty(float, fget=_get_fader, fset=_set_fader)

    def event(self, event):
        if event.type() == QEvent.Enter:
            self.anim = QPropertyAnimation(self, b"fader")
            self.anim.setDuration(150)
            self.anim.setEndValue(1.0)
            self.anim.start(QPropertyAnimation.DeleteWhenStopped)
        elif event.type() == QEvent.Leave:
            self.anim = QPropertyAnimation(self, b"fader")
            self.anim.setDuration(124)
            self.anim.setEndValue(0.0)
            self.anim.start(QPropertyAnimation.DeleteWhenStopped)
        else:
            return QToolButton.event(self, event)
        return False

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.isEnabled() and not self.isDown() and not self.isChecked():
            painter.save()
            hover_color = QColor("#424242")
            faded_hover_color = QColor(hover_color)
            faded_hover_color.setAlpha(int(self._fader * hover_color.alpha()))
            painter.fillRect(event.rect(), faded_hover_color)
            painter.restore()
        elif self.isDown() or self.isChecked():
            painter.save()
            selected_color = QColor("#090909")
            painter.fillRect(event.rect(), selected_color)
            painter.restore()
        # fm = QFontMetrics(painter.font())
        # rect = QRect(-3, 2, self.rect().width(), fm.height())
        rect = event.rect()
        icon_rect = QRect(0, 0, 22, 22)
        self.icon().paint(painter, icon_rect, Qt.AlignVCenter)
        painter.drawText(
            rect.adjusted(0, 0, -3, 0),
            Qt.AlignRight | Qt.AlignVCenter, self.text())

    def sizeHint(self):
        self.ensurePolished()
        s = self.fontMetrics().size(Qt.TextSingleLine, self.text())
        s.setWidth(s.width() + 25)
        return s.expandedTo(QApplication.globalStrut())

###############################################################################
# Cool Tool Button
###############################################################################

class CoolToolButton(QToolButton):

    def __init__(self, action=None, parent=None):
        super().__init__(parent)

        self._fader = 0
        if action is not None:
            self.setDefaultAction(action)
        self.setAttribute(Qt.WA_Hover, True)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

    def _set_fader(self, value):
        self._fader = value
        self.update()

    def _get_fader(self):
        return self._fader

    fader = pyqtProperty(float, fget=_get_fader, fset=_set_fader)

    def event(self, event):
        if event.type() == QEvent.Enter:
            self.anim = QPropertyAnimation(self, b"fader")
            self.anim.setDuration(150)
            self.anim.setEndValue(1.0)
            self.anim.start(QPropertyAnimation.DeleteWhenStopped)
        elif event.type() == QEvent.Leave:
            self.anim = QPropertyAnimation(self, b"fader")
            self.anim.setDuration(124)
            self.anim.setEndValue(0.0)
            self.anim.start(QPropertyAnimation.DeleteWhenStopped)
        else:
            return QToolButton.event(self, event)
        return False

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.isEnabled() and not self.isDown() and not self.isChecked():
            painter.save()
            hover_color = QColor("#424242")
            faded_hover_color = QColor(hover_color)
            faded_hover_color.setAlpha(int(self._fader * hover_color.alpha()))
            painter.fillRect(event.rect(), faded_hover_color)
            painter.restore()
        elif self.isDown() or self.isChecked():
            painter.save()
            selected_color = QColor("#161719")
            painter.fillRect(event.rect(), selected_color)
            painter.restore()

        is_titled = bool(self.defaultAction().property("titled"))
        icon_rect = QRect(0, 0, 32, 32)
        icon_rect.moveCenter(event.rect().center())

        if is_titled:
            font = painter.font()
            center_rect = event.rect()
            font.setPointSizeF(6)
            fm = QFontMetrics(font)
            line_height = fm.height()
            text_flags = Qt.AlignHCenter | Qt.AlignTop
            project_name = self.defaultAction().property("heading")
            if project_name is not None:
                center_rect.adjust(0, line_height, 0, 0)
                icon_rect.moveTop(center_rect.top())
            else:
                icon_rect.moveCenter(center_rect.center())
            self.icon().paint(painter, icon_rect, Qt.AlignCenter)
            painter.setFont(font)
            r = QRect(0, 5, self.rect().width(), line_height)
            painter.setPen(Qt.white)
            margin = 5
            available_width = r.width() - margin
            ellided_project_name = fm.elidedText(
                project_name, Qt.ElideMiddle, available_width)
            painter.drawText(r, text_flags, ellided_project_name)
        else:
            self.icon().paint(painter, icon_rect, Qt.AlignCenter)

    def sizeHint(self):
        button_size = self.iconSize().expandedTo(QSize(48, 48))
        return button_size

    def minimumSizeHint(self):
        return QSize(8, 8)


###############################################################################
# Custom Table CheckableHeaderTable
###############################################################################

class CheckableHeaderTable(QTableWidget):
    """ QTableWidget subclassed with QCheckBox on Header to select all items """

    stateChanged=pyqtSignal(int, name="stateChanged")

    def __init__(self, parent=None, *args):
        """ init CheckableHeaderTable and add custom widgets and connections """
        super(QTableWidget, self).__init__(parent, *args)
        self.chkbox = QCheckBox(self.horizontalHeader())
        self.chkbox.stateChanged.connect(self.change_items_selection)

    def change_items_selection(self, state):
        """ de/select all items iterating over all table rows at column 0 """
        for i in range(self.rowCount()):
            item = self.item(i, 0)
            if item is not None:
                item.setCheckState(state)


def load_table(table, headers, data, checkFirstColumn=True):
    table.setHorizontalHeaderLabels(headers)
    table.horizontalHeader().setStretchLastSection(True)
    table.setSelectionBehavior(QAbstractItemView.SelectRows)
    for i in range(table.rowCount()):
        table.removeRow(0)
    for r, row in enumerate(data):
        table.insertRow(r)
        for index, colItem in enumerate(row):
            item = QTableWidgetItem(colItem)
            table.setItem(r, index, item)
            if index == 0 and checkFirstColumn:
                item.setData(Qt.UserRole, row)
                item.setCheckState(Qt.Unchecked)
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled |
                    Qt.ItemIsUserCheckable)
            else:
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)


def remove_get_selected_items(table, data):
    rows = table.rowCount()
    pos = rows - 1
    selected = []
    for i in range(rows):
        if table.item(pos - i, 0) is not None and \
        table.item(pos - i, 0).checkState() == Qt.Checked:
            selected.append(data.pop(pos - i))
            table.removeRow(pos - i)
    return selected


class LoadingItem(QLabel):

    def __init__(self):
        super(LoadingItem, self).__init__()
        #self.movie = QMovie(resources.IMAGES['loading'])
        #self.setMovie(self.movie)
        #self.movie.setScaledSize(QSize(16, 16))
        #self.movie.start()

    def add_item_to_tree(self, folder, tree, item_type=None, parent=None):
        if item_type is None:
            item = QTreeWidgetItem()
            item.setText(0, (self.tr('       LOADING: "%s"') % folder))
        else:
            item = item_type(parent,
                (self.tr('       LOADING: "%s"') % folder), folder)
        tree.addTopLevelItem(item)
        tree.setItemWidget(item, 0, self)
        return item


###############################################################################
# Thread with Callback
###############################################################################

class ThreadExecution(QThread):

    executionFinished = pyqtSignal(object,name="executionFinished")

    def __init__(self, functionInit=None, args=None, kwargs=None):
        super(ThreadExecution, self).__init__()
        QThread.__init__(self)
        self.execute = functionInit
        self.result = None
        self.storage_values = None
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self.signal_return = None

    def run(self):
        if self.execute:
            self.result = self.execute(*self.args, **self.kwargs)
        self.executionFinished.emit(self.signal_return)
        self.signal_return = None


class ThreadProjectExplore(QThread):

    def __init__(self):
        super(ThreadProjectExplore, self).__init__()
        self.execute = lambda: None
        self._folder_path = None
        self._item = None
        self._extensions = None

    def open_folder(self, folder):
        self._folder_path = folder
        self.execute = self._thread_open_project
        self.start()

    def refresh_project(self, path, item, extensions):
        self._folder_path = path
        self._item = item
        self._extensions = extensions
        self.execute = self._thread_refresh_project
        self.start()

    def run(self):
        self.execute()

    def _thread_refresh_project(self):
        if self._extensions != settings.SUPPORTED_EXTENSIONS:
            folderStructure = file_manager.open_project_with_extensions(
                self._folder_path, self._extensions)
        else:
            try:
                folderStructure = file_manager.open_project(self._folder_path)
            except NinjaIOException:
                pass  # There is not much we can do at this point

        if folderStructure and (folderStructure.get(self._folder_path,
                                                [None, None])[1] is not None):
            folderStructure[self._folder_path][1].sort()
            values = (self._folder_path, self._item, folderStructure)
            self.emit(SIGNAL("folderDataRefreshed(PyQt_PyObject)"), values)

    def _thread_open_project(self):
        try:
            project = json_manager.read_ninja_project(self._folder_path)
            extensions = project.get('supported-extensions',
                settings.SUPPORTED_EXTENSIONS)
            if extensions != settings.SUPPORTED_EXTENSIONS:
                structure = file_manager.open_project_with_extensions(
                    self._folder_path, extensions)
            else:
                structure = file_manager.open_project(self._folder_path)

            self.emit(SIGNAL("folderDataAcquired(PyQt_PyObject)"),
                (self._folder_path, structure))
        except:
            self.emit(SIGNAL("folderDataAcquired(PyQt_PyObject)"),
                (self._folder_path, None))


###############################################################################
# LOADING ANIMATION OVER THE WIDGET
###############################################################################


class Overlay(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        palette = QPalette(self.palette())
        palette.setColor(palette.Background, Qt.transparent)
        self.setPalette(palette)
        self.counter = 0

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(event.rect(), QBrush(QColor(255, 255, 255, 127)))
        painter.setPen(QPen(Qt.NoPen))

        for i in range(6):
            x_pos = self.width() / 2 + 30 * \
                math.cos(2 * math.pi * i / 6.0) - 10
            y_pos = self.height() / 2 + 30 * \
                math.sin(2 * math.pi * i / 6.0) - 10
            if (self.counter / 5) % 6 == i:
                linear_gradient = QLinearGradient(
                    x_pos + 10, x_pos, y_pos + 10, y_pos)
                linear_gradient.setColorAt(0, QColor(135, 206, 250))
                linear_gradient.setColorAt(1, QColor(0, 0, 128))
                painter.setBrush(QBrush(linear_gradient))
            else:
                linear_gradient = QLinearGradient(
                    x_pos - 10, x_pos, y_pos + 10, y_pos)
                linear_gradient.setColorAt(0, QColor(105, 105, 105))
                linear_gradient.setColorAt(1, QColor(0, 0, 0))
                painter.setBrush(QBrush(linear_gradient))
            painter.drawEllipse(
                x_pos,
                y_pos,
                20, 20)

        painter.end()

    def showEvent(self, event):
        self.timer = self.startTimer(50)
        self.counter = 0

    def timerEvent(self, event):
        self.counter += 1
        self.update()


###############################################################################
# PRINT FILE
###############################################################################


def print_file(fileName, printFunction):
    """This method print a file

    This method print a file, fileName is the default fileName,
    and printFunction is a funcion that takes a QPrinter
    object and print the file,
    the print method
    More info on:http://doc.qt.nokia.com/latest/printing.html"""

    printer = QPrinter(QPrinter.HighResolution)
    printer.setPageSize(QPrinter.A4)
    printer.setOutputFileName(fileName)
    printer.setDocName(fileName)

    preview = QPrintPreviewDialog(printer)
    preview.paintRequested[QPrinter].connect(printFunction)
    size = QApplication.instance().desktop().screenGeometry()
    width = size.width() - 100
    height = size.height() - 100
    preview.setMinimumSize(width, height)
    preview.exec_()

###############################################################################
# FADING ANIMATION
###############################################################################


class FaderWidget(QWidget):

    def __init__(self, old_widget, new_widget):
        QWidget.__init__(self, new_widget)
        self.old_pixmap = QPixmap(new_widget.size())
        old_widget.render(self.old_pixmap)
        self.pixmap_opacity = 1.0

        self.timeline = QTimeLine()
        self.timeline.valueChanged.connect(self.animate)
        self.timeline.finished.connect(self.close)
        self.timeline.setDuration(300)
        self.timeline.start()

        self.resize(new_widget.size())
        self.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setOpacity(self.pixmap_opacity)
        painter.drawPixmap(0, 0, self.old_pixmap)

    def animate(self, value):
        self.pixmap_opacity = 1.0 - value
        self.repaint()


###############################################################################
# Enhanced UI Widgets
###############################################################################

class LineEditButton(QLineEdit):

    buttonClicked = pyqtSignal()

    def __init__(self, icon, parent=None):
        super().__init__(parent)
        if isinstance(icon, str):
            icon = QIcon(icon)
        self._button = QPushButton(icon, '', self)
        self._button.setCursor(Qt.ArrowCursor)
        self._button.clicked.connect(self.buttonClicked.emit)
        frame_width = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth)
        btn_size = self._button.sizeHint()
        self.setMinimumSize(
            max(self.minimumSizeHint().width(),
                btn_size.width() + frame_width * 2 + 2),
            max(self.minimumSizeHint().height(),
                btn_size.height() + frame_width * 2 + 2)
        )

    def resizeEvent(self, event):
        btn_size = self._button.sizeHint()
        frame_width = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth)
        self._button.move(self.rect().right() - frame_width - btn_size.width(),
                          (self.rect().bottom() - btn_size.height() + 1) / 2)
        super().resizeEvent(event)


class ComboBoxButton(object):

    def __init__(self, combo, operation, icon=None):
        hbox = QHBoxLayout(combo)
        hbox.setDirection(hbox.RightToLeft)
        # hbox.setMargin(0)
        combo.setLayout(hbox)
        hbox.addStretch()
        btnOperation = QPushButton(combo)
        btnOperation.setObjectName('combo_button')
        if icon:
            btnOperation.setIcon(QIcon(icon))
            btnOperation.setIconSize(QSize(16, 16))
        hbox.addWidget(btnOperation)
        btnOperation.clicked.connect(operation)


class LineEditCount(QObject):

    """Show summary results inside the line edit, for counting some property."""

    def __init__(self, lineEdit):
        QObject.__init__(self)
        hbox = QHBoxLayout(lineEdit)
        hbox.setContentsMargins(0, 0, 0, 0)
        lineEdit.setLayout(hbox)
        hbox.addStretch()
        self.counter = QLabel(lineEdit)
        hbox.addWidget(self.counter)
        lineEdit.setStyleSheet("padding-right: 2px; padding-left: 2px;")

    def update_count(self, index, total, hasSearch=False):
        """Update the values displayed in the line edit counter."""

        message = "%s / %s" % (index, total)
        self.counter.setText(message)
        if total > 0:
            self.counter.setStyleSheet("background: #73c990;")
        else:
            self.counter.setStyleSheet("background: #6a6ea9;")
        if index == 0 and total == 0 and hasSearch:
            self.counter.setStyleSheet("background: #e73e3e;color: white;")


class LineEditTabCompleter(QLineEdit):

    def __init__(self, completer, type=QCompleter.PopupCompletion):
        QLineEdit.__init__(self)
        self.completer = completer
        self.setTextMargins(0, 0, 5, 0)
        self.completionType = type
        self.completer.setCompletionMode(self.completionType)

    def event(self, event):
        if (event.type() == QEvent.KeyPress) and (event.key() == Qt.Key_Tab):
            if self.completionType == QCompleter.InlineCompletion:
                eventTab = QKeyEvent(QEvent.KeyPress,
                    Qt.Key_End, Qt.NoModifier)
                super(LineEditTabCompleter, self).event(eventTab)
            else:
                completion = self.completer.currentCompletion()
                if os.path.isdir(completion):
                    completion += os.path.sep
                self.selectAll()
                self.insert(completion)
                self.completer.popup().hide()
            return True
        return super(LineEditTabCompleter, self).event(event)

    def contextMenuEvent(self, event):
        popup_menu = self.createStandardContextMenu()

        if self.completionType == QCompleter.InlineCompletion:
            actionCompletion = QAction(
                self.tr("Set completion type to: Popup Completion"), self)
        else:
            actionCompletion = QAction(
                self.tr("Set completion type to: Inline Completion"), self)
        self.connect(actionCompletion, SIGNAL("triggered()"),
            self.change_completion_type)
        popup_menu.insertSeparator(popup_menu.actions()[0])
        popup_menu.insertAction(popup_menu.actions()[0], actionCompletion)

        #show menu
        popup_menu.exec_(event.globalPos())

    def change_completion_type(self):
        if self.completionType == QCompleter.InlineCompletion:
            self.completionType = QCompleter.PopupCompletion
        else:
            self.completionType = QCompleter.InlineCompletion
        self.completer.setCompletionMode(self.completionType)
        self.setFocus()


class CustomDelegate(QItemDelegate):
    """ Always adds uppercase text """

    def __init__(self, parent=None):
        QItemDelegate.__init__(self, parent)

    def setEditorData(self, editor, index):
        if editor.text().strip():
            QItemDelegate.setEditorData(self, editor, index)

    def setModelData(self, editor, model, index):
        text = editor.text().upper()
        model.setData(index, text)


class ClickeableLabel(QLabel):

    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        self.clicked.emit()


def install_shortcuts(obj, actions, ide):
    short = resources.get_shortcut
    for action in actions:
        short_key = action.get("shortcut", None)
        action_data = action.get("action", None)
        connect = action.get("connect", None)
        shortcut = None
        item_ui = None
        func = None
        if connect is not None:
            func = getattr(obj, connect, None)

        if short_key and not action_data:
            if isinstance(short_key, QKeySequence):
                shortcut = QShortcut(short_key, ide)
            else:
                if short(short_key) is None:
                    logger.warning("Not shorcut for %s" % short_key)
                    continue
                shortcut = QShortcut(short(short_key), ide)
            shortcut.setContext(Qt.ApplicationShortcut)
            if isinstance(func, collections.Callable):
                shortcut.activated.connect(func)
        if action_data:
            is_menu = action_data.get('is_menu', False)
            if is_menu:
                item_ui = QMenu(action_data['text'], ide)
            else:
                item_ui = QAction(action_data['text'], ide)
                object_name = "%s.%s" % (obj.__class__.__name__, connect)
                item_ui.setObjectName(object_name)
                # FIXME: Configurable
                item_ui.setIconVisibleInMenu(False)
            image_name = action_data.get('image', None)
            section = action_data.get('section', None)
            weight = action_data.get('weight', None)
            keysequence = action_data.get('keysequence', None)
            if image_name:
                if isinstance(image_name, int):
                    icon = ide.style().standardIcon(image_name)
                    item_ui.setIcon(icon)
                elif isinstance(image_name, str):
                    if image_name.startswith("/home"):
                        icon = QIcon(image_name)
                    else:
                        icon = QIcon(":img/" + image_name)
                    item_ui.setIcon(icon)
            if short_key and not is_menu:
                if short(short_key) is None:
                    logger.warning("Not shortcut for %s" % short_key)
                    continue
                item_ui.setShortcut(short(short_key))
                # Add tooltip with append shortcut
                item_ui.setToolTip(
                    tooltip_with_shortcut(item_ui.text(), short(short_key)))
                item_ui.setShortcutContext(Qt.ApplicationShortcut)
            elif keysequence and not is_menu:
                item_ui.setShortcut(short(keysequence))
                item_ui.setShortcutContext(Qt.ApplicationShortcut)
            if isinstance(func, collections.Callable) and not is_menu:
                item_ui.triggered.connect(lambda _, func=func: func())
            if section and section[0] is not None and weight:
                ide.register_menuitem(item_ui, section, weight)
                if image_name and not is_menu:
                    ide.register_toolbar(item_ui, section, weight)

        if short_key and shortcut:
            ide.register_shortcut(short_key, shortcut, item_ui)


def tooltip_with_shortcut(tip: str, shortcut) -> str:
    tooltip = "{} <span style='color: gray; font-size: small'>{}</span>"
    return tooltip.format(tip, shortcut.toString())


def get_qml_resource(qmlpath):
    path_qml = QDir.fromNativeSeparators(
        os.path.join(resources.QML_FILES, qmlpath))
    path_qml = urlunparse(urlparse(path_qml)._replace(scheme='file'))
    return QUrl(path_qml)


def draw_icon(icon, rect, painter, icon_mode, shadow=False):
    cache = icon.pixmap(rect.size())
    dip_offset = QPoint(1, -2)

    cache = QPixmap()
    pixname = "icon {0} {1} {2}".format(
        icon.cacheKey(), icon_mode, rect.height()
    )
    if QPixmapCache.find(pixname) is None:
        pix = icon.pixmap(rect.size())
        device_pixel_ratio = pix.devicePixelRatio()
        radius = 3 * device_pixel_ratio
        offset = dip_offset * device_pixel_ratio
        cache = QPixmap(pix.size() + QSize(radius * 2, radius * 2))
        cache.fill(Qt.transparent)

        cache_painter = QPainter(cache)

        if icon_mode == QIcon.Disabled:
            im = pix.toImage().convertToFormat(QImage.Format_ARGB32)
            for y in range(0, im.height()):
                scanline = im.scanLine(y)
                for x in range(0, im.width()):
                    pixel = scanline
                    intensity = qGray(pixel)
                    scanline = qRgba(
                        intensity, intensity, intensity, qAlpha(pixel))
                    scanline += 1
            pix = QPixmap.fromImage(im)

        # Draw shadow
        tmp = QImage(pix.size() + QSize(radius * 2, radius * 2),
                     QImage.Format_ARGB32_Premultiplied)
        tmp.fill(Qt.transparent)

        tmp_painter = QPainter(tmp)
        tmp_painter.setCompositionMode(QPainter.CompositionMode_Source)
        tmp_painter.drawPixmap(
            QRect(radius, radius, pix.width(), pix.height()), pix)
        tmp_painter.end()

        # Blur the alpha channel
        blurred = QImage(tmp.size(), QImage.Format_ARGB32_Premultiplied)
        blur_painter = QPainter(blurred)
        blur_painter.end()

        # tmp = blurred

        tmp_painter.begin(tmp)
        tmp_painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        tmp_painter.fillRect(tmp.rect(), QColor(0, 0, 0, 150))
        tmp_painter.end()

        tmp_painter.begin(tmp)
        tmp_painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        tmp_painter.fillRect(tmp.rect(), QColor(0, 0, 0, 150))
        tmp_painter.end()

        # Draw the blurred drop shadow
        cache_painter.drawImage(
            QRect(0, 0, cache.rect().width(), cache.rect().height()), tmp)
        # Draw the actual pixmap
        cache_painter.drawPixmap(
            QRect(QPoint(radius, radius) + offset,
                  QSize(pix.width(), pix.height())), pix)
        cache_painter.end()
        cache.setDevicePixelRatio(device_pixel_ratio)
        QPixmapCache.insert(pixname, cache)

    target_rect = cache.rect()
    target_rect.setSize(target_rect.size() / cache.devicePixelRatio())
    target_rect.moveCenter(rect.center() - dip_offset)
    painter.drawPixmap(target_rect, cache)


def colored_icon(name, color):
    pix = QPixmap(name)
    mask = pix.createMaskFromColor(QColor(Qt.black), Qt.MaskOutColor)
    if isinstance(color, str):
        color = QColor(color)
    pix.fill(color)
    pix.setMask(mask)
    return QIcon(pix)


def get_icon(name, color=None):
    if color is None:
        # Normal icon
        return QIcon(':img/%s' % name)
    if not name.startswith(':img'):
        name = ':img/%s' % name
    return colored_icon(name, color)


class TabShortcuts(QShortcut):

    def __init__(self, key, parent, index):
        super(TabShortcuts, self).__init__(key, parent)
        self.index = index
