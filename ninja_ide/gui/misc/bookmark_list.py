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
from __future__ import unicode_literals

import os
import re
try:
    import Queue
except:
    import queue as Queue  # lint:ok

from PyQt4.QtCore import Qt
from PyQt4.QtCore import QDir
from PyQt4.QtCore import QFile
from PyQt4.QtCore import QTextStream
from PyQt4.QtCore import QRegExp
from PyQt4.QtCore import QThread
from PyQt4.QtCore import SIGNAL

from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QSizePolicy
from PyQt4.QtGui import QSpacerItem
from PyQt4.QtGui import QRadioButton
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QGridLayout
from PyQt4.QtGui import QGroupBox
from PyQt4.QtGui import QAbstractItemView
from PyQt4.QtGui import QHeaderView
from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QTreeWidget
from PyQt4.QtGui import QTreeWidgetItem
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QComboBox
from PyQt4.QtGui import QCheckBox
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QFileDialog

from ninja_ide import resources
from ninja_ide.core import file_manager
from ninja_ide.core import settings
from ninja_ide.gui.main_panel import main_container
from ninja_ide.gui.editor import sidebar_widget
from ninja_ide.gui.explorer import explorer_container


class BookmarkListThread(QThread):
    '''
    Emit the signal
    found_pattern(PyQt_PyObject)
    '''

    def bookmark_list_files(self, dir_name):
        self._cancel = False
        self.recursive = True
        self.queue = Queue.Queue()
        self.queue.put(dir_name)
        self.root_dir = dir_name
        #Start!
        self.start()

    def run(self):
        file_filter = QDir.Files | QDir.NoDotAndDotDot | QDir.Readable
        dir_filter = QDir.Dirs | QDir.NoDotAndDotDot | QDir.Readable
        while not self._cancel and not self.queue.empty():
            current_dir = QDir(self.queue.get())
            #Skip not readable dirs!
            if not current_dir.isReadable():
                continue

            #Collect all sub dirs!
            if self.recursive:
                current_sub_dirs = current_dir.entryInfoList(dir_filter)
                for one_dir in current_sub_dirs:
                    self.queue.put(one_dir.absoluteFilePath())

            #all files in sub_dir first apply the filters
            current_files = current_dir.entryInfoList(
                file_filter)
            #process all files in current dir!
            for one_file in current_files:
                self._search_bookmarks_in_file(one_file.absoluteFilePath(),
                    one_file.fileName())

    def _search_bookmarks_in_file(self, file_path, file_name):
        file_object = QFile(file_path)
        if not file_object.open(QFile.ReadOnly):
            return

        blines = settings.BOOKMARKS.get(file_path, None)
        if blines is None:
            return

        stream = QTextStream(file_object)
        lines = []
        line_index = 0
        line = stream.readLine()
        while not self._cancel and not (stream.atEnd() and not line):
            if line_index in blines:
                lines.append((line_index, line))
            #take the next line!
            line = stream.readLine()
            line_index += 1

        #emit a signal!
        relative_file_name = file_manager.convert_to_relative(
            self.root_dir, file_path)
        self.emit(SIGNAL("found_pattern(PyQt_PyObject)"),
            (relative_file_name, lines))

    def cancel(self):
        self._cancel = True


class BookmarkListResult(QTreeWidget):

    def __init__(self):
        QTreeWidget.__init__(self)
        self.setHeaderLabels((self.tr('File'), self.tr('Line')))
        self.header().setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.header().setResizeMode(0, QHeaderView.ResizeToContents)
        self.header().setResizeMode(1, QHeaderView.ResizeToContents)
        self.header().setStretchLastSection(False)
        self.sortByColumn(0, Qt.AscendingOrder)

    def update_result(self, dir_name_root, file_name, items):
        if items:
            root_item = BookmarkListRootItem(self, (file_name, ''),
                dir_name_root)
            root_item.setExpanded(True)
            for line, content in items:
                QTreeWidgetItem(root_item, (content, str(line + 1)))


class BookmarkListRootItem(QTreeWidgetItem):

    def __init__(self, parent, names, dir_name_root):
        QTreeWidgetItem.__init__(self, parent, names)
        self.dir_name_root = dir_name_root


class BookmarkListWidget(QWidget):

    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self._main_container = main_container.MainContainer()
        self._explorer_container = explorer_container.ExplorerContainer()
        self._result_widget = BookmarkListResult()
        self._error_label = QLabel(self.tr("No Results"))
        self._error_label.setVisible(False)
        #Main Layout
        main_hbox = QHBoxLayout(self)
        #Result Layout
        tree_vbox = QVBoxLayout()
        tree_vbox.addWidget(self._result_widget)
        tree_vbox.addWidget(self._error_label)

        main_hbox.addLayout(tree_vbox)

        #signals
        self._bookmark_thread = BookmarkListThread()
        self.connect(self._bookmark_thread, SIGNAL("found_pattern(PyQt_PyObject)"),
            self._found_match)
        self.connect(self._bookmark_thread, SIGNAL("finished()"),
            self._bookmark_finished)
        self.connect(self._result_widget, SIGNAL(
            "itemActivated(QTreeWidgetItem *, int)"), self._go_to)
        self.connect(self._result_widget, SIGNAL(
            "itemClicked(QTreeWidgetItem *, int)"), self._go_to)

        self.connect(self._explorer_container, SIGNAL("projectOpened(QString)"),
            self._bookmark_list_files)
        self.connect(self._explorer_container, SIGNAL("projectClosed(QString)"),
            self._bookmark_list_files)
        self.connect(self._main_container, SIGNAL("bookmarks_changed(PyQt_PyObject)"),
            self._bookmark_list_files)

    def _bookmark_finished(self):
        self._bookmark_thread.wait()
        self._error_label.setVisible(False)
        if not self._result_widget.topLevelItemCount():
            self._error_label.setVisible(True)
        self._result_widget.setFocus()

    def _found_match(self, result):
        file_name = result[0]
        items = result[1]
        dir_name = self._explorer_container.get_actual_project()
        self._result_widget.update_result(
            dir_name, file_name, items)

    def _bookmark_list_files(self):
        self._kill_thread()
        self._result_widget.clear()
        dir_name = self._explorer_container.get_actual_project()
        if dir_name is not None:
            self._bookmark_thread.bookmark_list_files(dir_name)

    def _kill_thread(self):
        if self._bookmark_thread.isRunning():
            self._bookmark_thread.cancel()

    def _go_to(self, item, val):
        if item.text(1):
            parent = item.parent()
            file_name = parent.text(0)
            lineno = item.text(1)
            root_dir_name = parent.dir_name_root
            file_path = file_manager.create_path(root_dir_name, file_name)
            #open the file and jump_to_line
            self._main_container.open_file(file_path)
            self._main_container.editor_jump_to_line(lineno=int(lineno) - 1)

