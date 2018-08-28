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

from collections import defaultdict

from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QFormLayout
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QDialogButtonBox

from PyQt5.QtQuickWidgets import QQuickWidget

from PyQt5.QtCore import Qt
from PyQt5.QtCore import QPoint
from PyQt5.QtCore import QVariant
from PyQt5.QtCore import QAbstractListModel
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QModelIndex

from ninja_ide import resources
from ninja_ide import translations
from ninja_ide.gui.ide import IDE
from ninja_ide.gui.explorer.explorer_container import ExplorerContainer
from ninja_ide.tools import ui_tools
from ninja_ide.gui.main_panel.marks import Bookmark


class BookmarkWidget(QWidget):
    """Bookmark Widget showing list of bookmarks in explorer container"""

    dockWidget = pyqtSignal('PyQt_PyObject')
    undockWidget = pyqtSignal('PyQt_PyObject')
    dataChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowStaysOnTopHint)
        box = QVBoxLayout(self)
        box.setContentsMargins(0, 0, 0, 0)
        box.setSpacing(0)
        # Model
        self._manager = BookmarkManager()
        # QML UI
        view = QQuickWidget()
        view.setResizeMode(QQuickWidget.SizeRootObjectToView)
        view.rootContext().setContextProperty("bookmarkModel", self._manager)
        view.rootContext().setContextProperty("theme", resources.QML_COLORS)
        view.setSource(ui_tools.get_qml_resource("BookmarkList.qml"))
        box.addWidget(view)

        self._root = view.rootObject()

        self._root.openBookmark.connect(self._open_bookmark)
        self._root.menuRequested.connect(self._show_menu)

        IDE.register_service("bookmarks", self)
        ExplorerContainer.register_tab("Bookmarks", self)

    def install(self):
        """Load bookmarks and connect signals for goingDown"""

        self.load_bookmarks()
        ninjaide = IDE.get_service("ide")
        ninjaide.goingDown.connect(self._on_going_down)

    def _show_menu(self, mousex, mousey, index):
        point = QPoint(mousex, mousey)

        menu = QMenu()
        edit_action = menu.addAction(translations.TR_ADD_BOOKMARK_NOTE)
        remove_action = menu.addAction(translations.TR_REMOVE_BOOKMARK)
        remove_all_action = menu.addAction(
            translations.TR_REMOVE_ALL_BOOKMARKS)

        book = self.bookmark_for_index(index)
        if book is None:
            edit_action.setEnabled(False)
            remove_action.setEnabled(False)

        edit_action.triggered.connect(lambda: self._add_note(index))
        remove_action.triggered.connect(lambda: self.remove_bookmark(book))
        remove_all_action.triggered.connect(self._remove_all_bookmarks)

        menu.exec_(self.mapToGlobal(point))

    def _on_going_down(self):
        self.save_bookmarks()

    def _open_bookmark(self, filename, lineno):
        main_container = IDE.get_service("main_container")
        if main_container is None:
            return
        main_container.open_file(filename, lineno)

    def _add_note(self, index):
        current_bookmark = self._manager.get_bookmark_for_index(index)

        dialog = QDialog(self)
        dialog.setWindowTitle(translations.TR_ADD_BOOKMARK_NOTE_TITLE)
        layout = QFormLayout(dialog)
        note_edit = QLineEdit()
        note_edit.setMinimumWidth(300)
        note_edit.setText(current_bookmark.note)
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addRow(translations.TR_ADD_BOOKMARK_NOTE_LABEL, note_edit)
        layout.addWidget(button_box)

        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)

        if dialog.exec_() == QDialog.Accepted:
            self._manager.update_note(current_bookmark, note_edit.text())

    def add_bookmark(self, mark):
        self._manager.add(mark)
        self.dataChanged.emit()

    def find_bookmark(self, fname, line):
        return self._manager.get(fname, line)

    def remove_bookmark(self, mark):
        self._manager.remove(mark)
        self.dataChanged.emit()

    def _remove_all_bookmarks(self):
        r = QMessageBox.question(
            self, translations.TR_REMOVE_ALL_BOOKMARKS_TITLE,
            translations.TR_REMOVE_ALL_BOOKMARKS_QUESTION,
            QMessageBox.Cancel | QMessageBox.Yes)
        if r == QMessageBox.Yes:
            self.remove_all_bookmarks()

    def remove_all_bookmarks(self):
        self._manager.remove_all()
        self.dataChanged.emit()

    def bookmark_for_index(self, index):
        if index == -1:
            return
        return self._manager.get_bookmark_for_index(index)

    def bookmarks(self, fname):
        return self._manager.bookmarks(fname)

    @property
    def all_bookmarks(self):
        return self._manager.all_bookmarks()

    def reject(self):
        if self.parent() is None:
            self.dockWidget.emit(self)

    def closeEvent(self, event):
        self.dockWidget.emit(self)
        event.ignore()

    def save_bookmarks(self):
        """Save all bookmarks"""
        bookmarks = []
        for bookmark in self._manager.all_bookmarks():
            bookmarks.append((
                bookmark.filename, bookmark.lineno,
                bookmark.linetext, bookmark.note
            ))
        data_settings = IDE.data_settings()
        data_settings.setValue("bookmarks", bookmarks)

    def load_bookmarks(self):
        """Load all bookmarks from data settings"""
        data_settings = IDE.data_settings()
        bookmarks = data_settings.value("bookmarks")
        if bookmarks is None:
            return
        for bookmark_data in bookmarks:
            fname, lineno, linetext, note = bookmark_data
            bookmark = Bookmark(fname, lineno)
            bookmark.linetext = linetext
            bookmark.note = note
            self.add_bookmark(bookmark)


class BookmarkManager(QAbstractListModel):

    FilenameRole = Qt.UserRole + 1
    LinenumberRole = Qt.UserRole + 2
    NoteRole = Qt.UserRole + 3
    LinetextRole = Qt.UserRole + 4
    DisplaynameRole = Qt.UserRole + 5

    def __init__(self):
        super().__init__()
        self.__bookmarks_map = defaultdict(list)
        self.__bookmarks_list = []

    def roleNames(self):
        return {
            self.FilenameRole: b"filename",
            self.LinenumberRole: b"lineno",
            self.NoteRole: b"note",
            self.LinetextRole: b"linetext",
            self.DisplaynameRole: b"displayname"
        }

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self)

    def update_note(self, book, text):
        """Update note for the bookmark"""
        index = self.__bookmarks_list.index(book)
        if index == -1:
            return

        book.note = text
        self.dataChanged.emit(
            self.index(index, 0, QModelIndex()),
            self.index(index, 0, QModelIndex()))

    def data(self, index, role):
        if not index.isValid() or index.row() < 0 or index.row() >= len(self):
            return QVariant()
        mark = self.__bookmarks_list[index.row()]
        if role == self.FilenameRole:
            return mark.filename
        elif role == self.LinenumberRole:
            return mark.lineno
        elif role == Qt.ToolTipRole:
            return mark.tooltip
        elif role == self.LinetextRole:
            return mark.linetext
        elif role == self.DisplaynameRole:
            return mark.display_name
        elif role == self.NoteRole:
            return mark.note

    def add(self, mark):
        """Add a bookmark"""
        self.beginInsertRows(QModelIndex(), len(self), len(self))
        self.__bookmarks_map[mark.filename].append(mark)
        self.__bookmarks_list.append(mark)
        self.endInsertRows()

    def remove(self, mark):
        """Remove a bookmark"""
        index = self.__bookmarks_list.index(mark)
        self.beginRemoveRows(QModelIndex(), index, index)
        self.__bookmarks_map[mark.filename].remove(mark)
        self.__bookmarks_list.remove(mark)
        self.endRemoveRows()

    def remove_all(self):
        """Remove all bookmarks"""
        while self.rowCount():
            index = self.index(0, 0)
            mark = self.__bookmarks_list[index.row()]
            self.remove(mark)

    def bookmarks(self, fname):
        """Gets bookmarks for a specified filename"""
        return self.__bookmarks_map.get(fname, [])

    def all_bookmarks(self):
        """Gets all bookmarks"""
        return self.__bookmarks_list

    def __len__(self):
        return len(self.__bookmarks_list)

    def get(self, fname, lineno):
        """Gets the bookmark in the specified file and line"""
        mark = None
        marks = self.__bookmarks_map.get(fname)
        if marks:
            for m in marks:
                if m.lineno == lineno:
                    mark = m
                    break
        return mark

    def get_bookmark_for_index(self, index):
        """Get bookmark in the specified index"""
        return self.__bookmarks_list[index]


# Register service
BookmarkWidget()
