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

import queue
import re
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QComboBox,
    QCheckBox,
    QGridLayout,
    QFrame,
    QToolButton,
    QSizePolicy,
    QPushButton,
    QTreeView,
    QLabel,
    QStyle,
    QItemDelegate
)
from PyQt5.QtCore import (
    QObject,
    QDir,
    QAbstractItemModel,
    QFile,
    QTextStream,
    pyqtSignal,
    pyqtSlot,
    QRegExp,
    Qt,
    QRect,
    QThread,
    QModelIndex
)
from PyQt5.QtGui import (
    QColor,
    # QBrush,
    QPalette
)
from ninja_ide.gui.ide import IDE
from ninja_ide.tools import ui_tools
from ninja_ide.core import settings
from ninja_ide.utils import theme


class FindInFilesWorker(QObject):

    finished = pyqtSignal('PyQt_PyObject')

    def find_in_files(self, dir_name, filters, regexp, recursive):
        """Trigger the find in files thread and return the lines found"""

        self._cancel = False
        self.recursive = recursive
        self.search_pattern = regexp
        self.filters = filters
        self.queue = queue.Queue()
        self.queue.put(dir_name)
        self.root_dir = dir_name
        # Start!
        self.start_worker()

    def start_worker(self):
        file_filter = QDir.Files | QDir.NoDotAndDotDot | QDir.Readable
        dir_filter = QDir.Dirs | QDir.NoDotAndDotDot | QDir.Readable
        while not self._cancel and not self.queue.empty():
            current_dir = QDir(self.queue.get())
            # Skip not readable dirs!
            if not current_dir.isReadable():
                continue
            # Collect all sub dirs!
            if self.recursive:
                current_sub_dirs = current_dir.entryInfoList(dir_filter)
                for one_dir in current_sub_dirs:
                    self.queue.put(one_dir.absoluteFilePath())
            # All files in sub_dir first apply the filters
            current_files = current_dir.entryInfoList(
                self.filters, file_filter)
            # Process all files in current dir
            for one_file in current_files:
                self._grep_file(
                    one_file.absoluteFilePath(), one_file.fileName())

    def _grep_file(self, file_path, file_name):
        """Search for each line inside the file"""
        file_obj = QFile(file_path)
        if not file_obj.open(QFile.ReadOnly):
            return
        stream = QTextStream(file_obj)
        lines = []
        append = lines.append
        line_index = 0
        line = stream.readLine()
        while not self._cancel and not stream.atEnd():
            column = self.search_pattern.indexIn(line)
            if column != - 1:
                append((line_index, line))
            # Take the next line
            line = stream.readLine()
            line_index += 1

        import os

        p = os.path.join(self.root_dir, file_path)
        self.finished.emit((p, lines))


class SearchResultTreeView(QTreeView):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._model = SearchResultModel(self)
        self.setItemDelegate(SearchResultDelegate())
        self.setModel(self._model)
        self.header().hide()

    def clear(self):
        self._model.clear()

    def add_result(self, results):
        self._model.add_result(results)


class FindInFilesWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        # Button widgets
        self._btn_clean = QToolButton()
        self._btn_clean.setIcon(
            ui_tools.colored_icon(
                ':img/clean', theme.get_color('IconBaseColor')))
        self._btn_clean.clicked.connect(self._clear_results)

        container = QHBoxLayout(self)
        container.setContentsMargins(3, 0, 3, 0)
        self._actions = FindInFilesActions(self)
        container.addWidget(self._actions)
        self._tree_results = SearchResultTreeView(self)
        container.addWidget(self._tree_results)
        self._main_container = IDE.get_service("main_container")
        # Search worker
        self._search_worker = FindInFilesWorker()
        self._search_thread = QThread()
        self._search_worker.moveToThread(self._search_thread)
        self._search_worker.finished.connect(self._on_worker_finished)
        # self._search_thread.finished.connect(self._search_worker.deleteLater)

        self._actions.searchRequested.connect(self._on_search_requested)
        self._tree_results.activated.connect(self._go_to)

    def _clear_results(self):
        self._tree_results.clear()

    def _go_to(self, index):
        result_item = self._tree_results.model().data(index, Qt.UserRole + 1)
        if result_item.lineno != -1:
            parent = result_item.parent
            file_name = parent.file_path
            lineno = result_item.lineno
            # Open the file and jump to line
            self._main_container.open_file(file_name, line=lineno)

    @pyqtSlot('PyQt_PyObject')
    def _on_worker_finished(self, lines):
        self._tree_results.add_result(lines)

    @pyqtSlot('QString', bool)
    def _on_search_requested(self, to_find, cs):
        ninjaide = IDE.get_service('ide')
        # editor = self._main_container.get_current_editor()
        nproject = ninjaide.get_current_project()
        to_find = QRegExp(to_find, cs)
        filters = re.split(",", '*.py,*.md')
        self._search_worker.find_in_files(
            nproject.path, filters, to_find, True)

    def showEvent(self, event):
        self._actions._line_search.setFocus()
        super().showEvent(event)

    def display_name(self):
        return 'Find in Files'

    def button_widgets(self):
        # Clear results, expand all, collapse all...
        return [self._btn_clean]


class ResultItem(object):

    def __init__(self):
        self.parent = None
        self.file_path = ''
        self.text = ''
        self.lineno = -1


class TreeItem(object):

    def __init__(self, result_item, parent=None):
        self.result = result_item
        self.parent_item = parent
        self.child_items = []

    def append_child(self, item):
        self.child_items.append(item)

    def child(self, row):
        return self.child_items[row]

    def child_count(self):
        return len(self.child_items)

    def data(self):
        return self.result

    def row(self):
        if self.parent_item is not None:
            return self.parent_item.child_items.index(self)
        return 0

    def parent(self):
        return self.parent_item

    def clear_children(self):
        self.child_items.clear()


class SearchResultDelegate(QItemDelegate):

    def paint(self, painter, option, index):
        painter.save()
        opt = option
        painter.setFont(settings.FONT)  # FIXME
        self.drawBackground(painter, opt, index)
        line_width = self.draw_lines(painter, opt, opt.rect, index)
        r = opt.rect.adjusted(line_width, 0, 0, 0)
        text = index.model().data(index, Qt.DisplayRole)
        # Number of results
        if index.model().hasChildren(index):
            text += ' [{}]'.format(index.model().rowCount(index))
        self.drawDisplay(painter, option, r, text)
        painter.restore()

    def draw_lines(self, painter, option, rect, index):
        padding = 4
        model = index.model()
        lineno = model.data(index, Qt.UserRole)
        if lineno < 1:
            return 0
        is_selected = option.state & QStyle.State_Selected
        lineno_text = str(lineno)
        font_width = painter.fontMetrics().width(lineno_text)
        lineno_width = padding + font_width + padding
        lineno_rect = QRect(rect)
        lineno_rect.setWidth(lineno_width)
        lineno_rect.setX(0)
        color_group = QPalette.Normal
        if not option.state & QStyle.State_Active:
            color_group = QPalette.Inactive
        elif not option.state & QStyle.State_Enabled:
            color_group = QPalette.Disabled
        if is_selected:
            brush = option.palette.brush(color_group, QPalette.Highlight)
        else:
            brush = option.palette.color(color_group, QPalette.Base).darker(111)
        painter.fillRect(lineno_rect, brush)
        opt = option
        opt.font = settings.FONT  # FIXME: performance
        # opt.displayAlignment = Qt.AlignRight | Qt.AlignVCenter
        opt.palette.setColor(color_group, QPalette.Text, Qt.darkGray)
        self.drawDisplay(painter, opt, lineno_rect, lineno_text)
        return lineno_width


class SearchResultModel(QAbstractItemModel):

    def __init__(self, results):
        super().__init__()
        self.root_item = TreeItem(None)

    def add_result(self, result):
        file_path = result[0]
        items = result[1]
        if items:
            parent = ResultItem()
            parent.file_path = file_path
            parent_item = TreeItem(parent, self.root_item)
            self.beginInsertRows(QModelIndex(), 0, 0)
            self.root_item.append_child(parent_item)
            self.endInsertRows()
            for item in items:
                io = ResultItem()
                io.parent = parent
                io.lineno = item[0]
                io.text = item[1]
                item_tree = TreeItem(io, parent_item)
                self.beginInsertRows(QModelIndex(), 0, 0)
                parent_item.append_child(item_tree)
                self.endInsertRows()

    def parent(self, index=QModelIndex()):
        if not index.isValid():
            return QModelIndex()
        child_item = index.internalPointer()
        if not child_item:
            return QModelIndex()
        parent_item = child_item.parent()
        if parent_item == self.root_item:
            return QModelIndex()
        return self.createIndex(parent_item.row(), 0, parent_item)

    def data(self, index, role):
        item = index.internalPointer().data()
        if role == Qt.DisplayRole:
            to_display = item.text if item.text else item.file_path
            return to_display
        elif role == Qt.UserRole:
            return item.lineno
        elif role == Qt.FontRole:
            return settings.FONT
        elif role == Qt.UserRole + 1:
            return item

    def columnCount(self, index):
        return 1

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        if not parent.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()
        child_item = parent_item.child(row)
        if child_item:
            return self.createIndex(row, column, child_item)
        return QModelIndex()

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()
        return parent_item.child_count()

    def clear(self):
        self.beginResetModel()
        self.root_item.clear_children()
        # self.root_item = None
        self.endResetModel()


class FindInFilesActions(QWidget):

    searchRequested = pyqtSignal('QString', bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Ignored)
        self._scope = QComboBox()
        self.ninjaide = IDE.get_service('ide')
        self.ninjaide.filesAndProjectsLoaded.connect(
            self._update_combo_projects)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self._scope)
        widgets_layout = QGridLayout()
        widgets_layout.setContentsMargins(0, 0, 0, 0)
        self._line_search = QLineEdit()
        self._line_search.setPlaceholderText('Search for')
        main_layout.addWidget(self._line_search)
        self._btn_search = QPushButton('Search!')
        self._btn_search.setEnabled(False)
        # TODO: replace
        self._check_cs = QCheckBox('Case Sensitive')
        widgets_layout.addWidget(self._check_cs, 2, 0)
        self._check_wo = QCheckBox('Whole words only')
        widgets_layout.addWidget(self._check_wo, 2, 1)
        self._check_re = QCheckBox('Regular expression')
        widgets_layout.addWidget(self._check_re, 3, 0)
        self._check_recursive = QCheckBox('Recursive')
        widgets_layout.addWidget(self._check_recursive, 3, 1)
        main_layout.addLayout(widgets_layout)
        main_layout.addStretch(1)

        # Connections
        self._line_search.returnPressed.connect(self.search_requested)

    def _update_combo_projects(self):
        projects = self.ninjaide.get_projects()
        self._scope.addItems(projects.keys())

    def search_requested(self):
        text = self._line_search.text()
        if not text.strip():
            return
        has_search = self._line_search.text()
        cs = self._check_cs.isChecked()
        self.searchRequested.emit(has_search, cs)
