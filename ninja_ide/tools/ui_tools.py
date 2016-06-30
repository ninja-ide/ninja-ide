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

import os
import math
import collections
import sys
if sys.version_info[0] >= 3:
    from urllib.parse import urlparse, urlunparse
else:
    from urlparse import urlparse, urlunparse

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QCompleter
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QLinearGradient
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtPrintSupport import QPrintPreviewDialog
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QShortcut
from PyQt5.QtGui import QPainter
from PyQt5.QtGui import QBrush
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QPen
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QTreeWidgetItem
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QSize
from PyQt5.QtCore import QDir
from PyQt5.QtCore import QUrl
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QThread
from PyQt5.QtCore import QEvent
from PyQt5.QtCore import QTimeLine

from ninja_ide import resources
from ninja_ide.core import settings
from ninja_ide.core.file_handling import file_manager
from ninja_ide.core.file_handling.file_manager import NinjaIOException
from ninja_ide.tools import json_manager

from ninja_ide.tools.logger import NinjaLogger

logger_tools = NinjaLogger('ninja_ide.tools.ui_tools')


###############################################################################
# Custom Table CheckableHeaderTable
###############################################################################

class CheckableHeaderTable(QTableWidget):
    """ QTableWidget subclassed with QCheckBox on Header to select all items """

    def __init__(self, parent=None, *args):
        """ init CheckableHeaderTable and add custom widgets and connections """
        super(QTableWidget, self).__init__(parent, *args)
        self.chkbox = QCheckBox(self.horizontalHeader())
        self.chkbox.stateChanged[int].connect(self.change_items_selection)

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
    executionFinished = pyqtSignal(object)
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
            self.folderDataRefreshed.emit(values)

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

            self.folderDataAcquired.emit((self._folder_path, structure))
        except:
            self.folderDataAcquired.emit((self._folder_path, None))


###############################################################################
# LOADING ANIMATION OVER THE WIDGET
###############################################################################


class Overlay(QWidget):

    def __init__(self, parent=None):
        super(Overlay, self).__init__(parent)
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
        super(FaderWidget, self).__init__(new_widget)

        self.old_pixmap = QPixmap(new_widget.size())
        old_widget.render(self.old_pixmap)
        self.pixmap_opacity = 1.0

        self.timeline = QTimeLine()
        self.timeline.valueChanged['qreal'].connect(self.animate)
        self.timeline.finished.connect(self.close)
        self.timeline.setDuration(500)
        self.timeline.start()

        self.resize(new_widget.size())
        self.show()

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setOpacity(self.pixmap_opacity)
        painter.drawPixmap(0, 0, self.old_pixmap)
        painter.end()

    def animate(self, value):
        self.pixmap_opacity = 1.0 - value
        self.repaint()


###############################################################################
# Enhanced UI Widgets
###############################################################################

class LineEditButton(object):

    def __init__(self, lineEdit, operation, icon=None):
        hbox = QHBoxLayout(lineEdit)
        hbox.setSpacing(0)
        lineEdit.setLayout(hbox)
        hbox.addStretch()
        btnOperation = QPushButton(lineEdit)
        btnOperation.setObjectName('line_button')
        if icon:
            btnOperation.setIcon(QIcon(icon))
            btnOperation.setIconSize(QSize(16, 16))
        hbox.addWidget(btnOperation)
        btnOperation.clicked.connect(operation)


class ComboBoxButton(object):

    def __init__(self, combo, operation, icon=None):
        hbox = QHBoxLayout(combo)
        hbox.setDirection(hbox.RightToLeft)
        hbox.setSpacing(0)
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
        super(LineEditCount, self).__init__()
        hbox = QHBoxLayout(lineEdit)
        hbox.setSpacing(0)
        lineEdit.setLayout(hbox)
        hbox.addStretch()
        self.counter = QLabel(lineEdit)
        hbox.addWidget(self.counter)
        lineEdit.setStyleSheet("padding-right: 2px;")
        lineEdit.setTextMargins(0, 0, 60, 0)

    def update_count(self, index, total, hasSearch=False):
        """Update the values displayed in the line edit counter."""
        message = "%s / %s" % (index, total)
        self.counter.setText(message)
        self.counter.setStyleSheet("background: none;color: gray;")
        if index == 0 and total == 0 and hasSearch:
            self.counter.setStyleSheet(
                "background: #e73e3e;color: white;border-radius: 5px;")


class LineEditTabCompleter(QLineEdit):

    def __init__(self, completer, type=QCompleter.PopupCompletion):
        super(LineEditTabCompleter, self).__init__()
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
        actionCompletion.triggered.connect(self.change_completion_type)
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


def install_shortcuts(obj, actions, ide):
    short = resources.get_shortcut
    for action in actions:
        short_key = action.get("shortcut", None)
        action_data = action.get("action", None)
        connect = action.get("connect", None)
        if connect == "open_project_properties":
            print("\nregistrando ::open_project_properties;  obj:", obj)

        shortcut = None
        item_ui = None
        func = None
        if connect:
            func = getattr(obj, connect, None)

        if short_key and not action_data:
            if isinstance(short_key, QKeySequence):
                shortcut = QShortcut(short_key, ide)
            else:
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
            image_name = action_data.get('image', None)
            section = action_data.get('section', None)
            weight = action_data.get('weight', None)
            keysequence = action_data.get('keysequence', None)
            if image_name:
                if isinstance(image_name, int):
                    icon = ide.style().standardIcon(image_name)
                    item_ui.setIcon(icon)
                elif isinstance(image_name, str):
                    icon = QIcon(":img/" + image_name)
                    item_ui.setIcon(icon)
            if short_key and not is_menu:
                item_ui.setShortcut(short(short_key))
                item_ui.setShortcutContext(Qt.ApplicationShortcut)
            elif keysequence and not is_menu:
                item_ui.setShortcut(short(keysequence))
                item_ui.setShortcutContext(Qt.ApplicationShortcut)
            if isinstance(func, collections.Callable) and not is_menu:
                item_ui.triggered['bool'].connect(lambda s, f=func: f())
            if section and section[0] is not None and weight:
                ide.register_menuitem(item_ui, section, weight)
                if image_name and not is_menu:
                    ide.register_toolbar(item_ui, section, weight)

        if short_key and shortcut:
            ide.register_shortcut(short_key, shortcut, item_ui)


def get_qml_resource(qmlpath):
    path_qml = QDir.fromNativeSeparators(
        os.path.join(resources.QML_FILES, qmlpath))
    # print("get_qml_resource:1:",path_qml, urlparse(path_qml))
    contain = False
    try:
        import virtualenv
        path_qml = urlunparse(urlparse(path_qml)._replace(scheme='file'))
        contain = True
    except ImportError:
        # path_qml = "file:///"+path_qml
        pass
    # print("get_qml_resource:2:",path_qml)
    if contain:
        return QUrl(path_qml)
    else:
        return QUrl.fromLocalFile(path_qml)


class TabShortcuts(QShortcut):

    def __init__(self, key, parent, index):
        super(TabShortcuts, self).__init__(key, parent)
        self.index = index
