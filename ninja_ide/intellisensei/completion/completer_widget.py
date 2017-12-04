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

from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QWidget,
    QListWidget,
    QListWidgetItem,
    # QDialog,
    QVBoxLayout
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import (
    QThread,
    QSize,
    Qt
)
from ninja_ide.intellisensei.completion import code_completion
from ninja_ide.intellisensei.completion import completion_delegate
from ninja_ide.tools.ui_tools import colored_icon


class CodeCompletionWidget(QFrame):

    def __init__(self, neditor):
        super().__init__(None, Qt.FramelessWindowHint | Qt.ToolTip)
        self._neditor = neditor
        # Code completion worker
        self._cc_worker = QThread()
        self._cc = code_completion.CodeCompletion()
        self._cc.moveToThread(self._cc_worker)
        box = QVBoxLayout(self)
        box.setContentsMargins(0, 0, 0, 0)
        self._completion_list = QListWidget()
        self._completion_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        delegate = completion_delegate.CompletionDelegate()
        # self._completion_list.setItemDelegate(delegate)
        box.addWidget(self._completion_list)

        self._icons = {
            'class': ':img/class',
            'function': ':img/function',
            'attr': ':img/attr',
            'instance': ':img/instance',
            'statement': ':img/statement'
        }
        # Key operations
        self._key_operations = {
            Qt.Key_Down: self.next_item,
            Qt.Key_Up: self.previous_item,
            Qt.Key_Escape: self.hide_completer,
            Qt.Key_Tab: self.insert_completion,
            Qt.Key_Return: self.insert_completion
        }
        self.__desktop = QApplication.instance().desktop()
        # Connections
        self._neditor.post_key_press.connect(self.process_key_event)
        self._cc_worker.started.connect(self._cc.collect_completions)
        self._cc.completionsReady.connect(self.__show_completions)

    def __show_completions(self, completions):
        self._add_proposals(completions)
        self.set_geometry()
        self.show()

    def _add_proposals(self, proposals):
        self._completion_list.clear()

        for proposal in proposals:
            item = QListWidgetItem()
            item.setText(proposal['name'])
            item.setIcon(QIcon(self._icons[proposal['type']]))
            # item.setData(Qt.DisplayRole, proposal['name'])
            # item.setData(Qt.UserRole + 1, proposal['desc'])
            # item.setData(Qt.DecorationRole, self._icons.get(proposal['type']))
            self._completion_list.addItem(item)
        self._completion_list.setCurrentRow(0)

    def set_geometry(self):
        cursor_rect = self._neditor.cursorRect()
        desktop_geo = self.__desktop.availableGeometry(self._neditor)
        point = self._neditor.mapToGlobal(cursor_rect.topLeft())
        cursor_rect.moveTopLeft(point)
        width = 450
        # Calculate the height
        max_visible_items = 10
        visible_items = min(
            self._completion_list.model().rowCount(), max_visible_items)
        opt = self._completion_list.viewOptions()
        model = self._completion_list.model()
        height = self._completion_list.itemDelegate().sizeHint(
            opt, model.index(0)).height()
        height *= visible_items
        orientation = (point.y() + height) < desktop_geo.height()
        if orientation:
            cursor_rect.moveTop(cursor_rect.bottom())
        cursor_rect.setWidth(width)
        cursor_rect.setHeight(height)
        self.setFixedHeight(height)
        if not orientation:
            cursor_rect.moveBottom(cursor_rect.top())
        xpos = desktop_geo.width() - (point.x() + width)
        if xpos < 0:
            cursor_rect.moveLeft(cursor_rect.left() + xpos)
        # else:
        #     cursor_rect.moveRight(cursor_rect.right() + 50)
        self.setGeometry(cursor_rect)

    def process_pre_key_event(self, event):
        if not self.isVisible():
            return
        key = event.key()
        operation = self._key_operations.get(key, lambda: False)()
        if operation is None:
            return True
        return False

    def process_key_event(self, event):
        if self.isVisible():
            # Collect new proposals based on prefix
            self.__prefix = self._neditor._text_under_cursor()
            if self.__prefix is None:
                return
            proposals = []
            for completion in self._cc.proposals:
                name = completion['name']
                len_prefix = len(self.__prefix)
                if name[:len_prefix] == self.__prefix:
                    proposals.append(completion)
            if proposals:
                self._add_proposals(proposals)
                self.set_geometry()
            else:
                self.hide_completer()
        key = event.key()
        if key == Qt.Key_Period:
            self.complete()

    def insert_completion(self):
        to_insert = self._completion_list.currentItem().text()
        if self.__prefix:
            to_insert = to_insert[len(self.__prefix):]
        self._neditor.textCursor().insertText(to_insert)
        self.hide_completer()

    def complete(self):
        self._cc.clean_up()
        # Get data from editor
        source = self._neditor.text
        lineno, offset = self._neditor.cursor_position
        self.__prefix = self._neditor._text_under_cursor()
        # Prepare the worker and run thread
        self._cc.prepare(source, lineno, offset)
        self._cc_worker.start()

    def hide_completer(self):
        self.hide()
        # Stop thread
        self.__prefix = ''
        self._cc_worker.quit()
        self._cc_worker.wait(10)

    def previous_item(self):
        new_row = self._completion_list.currentRow() - 1
        if new_row >= 0:
            self._completion_list.setCurrentRow(new_row)
        else:
            self._completion_list.setCurrentRow(
                self._completion_list.count() - 1)

    def next_item(self):
        new_row = self._completion_list.currentRow() + 1
        if new_row < self._completion_list.count():
            self._completion_list.setCurrentRow(new_row)
        else:
            self._completion_list.setCurrentRow(0)

"""
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QWidget,
    # QDialog,
    QVBoxLayout
)
from PyQt5.QtQuick import QQuickView
from PyQt5.QtCore import (
    QThread,
    Qt,
    pyqtSlot
)
from ninja_ide.intellisensei.completion import code_completion
from ninja_ide.tools import ui_tools
from ninja_ide.gui import theme

# FIXME: insert cs completions


class CodeCompletionWidget(QFrame):

    TYPES = {
        'class': 'class',
        'function': 'func',
        'instance': 'obj',
        'statement': 'stmt',
        'param': 'param',
        'keyword': 'kword',
        'module': 'mod'
    }

    TYPE_COLORS = {
        'class': '#804becc9',
        'function': '#80ff555a',
        'instance': '#8066ff99',
        'statement': '#80a591c6',
        'param': '#80f9d170',
        'keyword': '#8018ffd6',
        'module': '#80ff884d'
    }

    def __init__(self, neditor, parent=None):
        super().__init__(parent, Qt.ToolTip | Qt.FramelessWindowHint)
        self._neditor = neditor
        # Code completion worker and thread
        self._cc_thread = QThread()
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._cc = code_completion.CodeCompletion()
        self._cc.moveToThread(self._cc_thread)
        self.__prefix = ''
        self.__proposals = []
        # QML interface
        view = QQuickView()
        view.setColor(Qt.transparent)
        view.setClearBeforeRendering(True)
        view.rootContext().setContextProperty("theme", theme.COLORS)
        view.setResizeMode(QQuickView.SizeRootObjectToView)
        view.setSource(ui_tools.get_qml_resource("Completer.qml"))
        box = QVBoxLayout(self)
        box.setContentsMargins(0, 0, 0, 0)
        box.addWidget(QWidget.createWindowContainer(view))
        # To access the QML object
        self._root = view.rootObject()
        # Key operations
        self._key_operations = {
            Qt.Key_Down: self.next_item,
            Qt.Key_Up: self.previous_item,
            Qt.Key_Escape: self.hide_completer,
            Qt.Key_Tab: self.insert_completion,
            Qt.Key_Return: self.insert_completion
        }

        self.__desktop = QApplication.instance().desktop()
        # Connections
        self._neditor.post_key_press.connect(self.process_key_event)
        self._cc_thread.started.connect(self._cc.collect_completions)
        self._cc.completionsReady.connect(self.__show_completions)
        self._root.insertCompletion.connect(self.insert_completion)

    @pyqtSlot('PyQt_PyObject')
    def __show_completions(self, completions):
        self._root.clear()
        for completion in completions:
            type_ = completion['type']
            name = completion['name']
            self._root.addItem(
                self.TYPES[type_],
                name,
                self.TYPE_COLORS[type_])
        self.set_geometry()
        self.show()

    def process_pre_key_event(self, event):
        if not self.isVisible():
            return
        key = event.key()
        operation = self._key_operations.get(key, lambda: False)()
        if operation is None:
            return True
        return False

    def process_key_event(self, event):
        if self.isVisible():
            # Collect new completions based on prefix
            self._root.clear()
            self.__prefix = self._neditor._text_under_cursor()
            proposals = []
            for completion in self._cc.proposals:
                name = completion['name']
                len_prefix = len(self.__prefix)
                if name[:len_prefix] == self.__prefix:
                    proposals.append(completion)
            if proposals:
                for proposal in proposals:
                    name = proposal['name']
                    type_ = proposal['type']
                    self._root.addItem(
                        self.TYPES[type_],
                        name,
                        self.TYPE_COLORS[type_]
                    )
                    self.set_geometry()
            else:
                self.hide_completer()
        key = event.key()
        ctrl = bool(event.modifiers() & Qt.ControlModifier)
        force_completion = key == Qt.Key_Space and ctrl
        if key == Qt.Key_Period or force_completion:
            self.complete()

    def insert_completion(self):
        to_insert = self._root.currentItem()
        if self.__prefix:
            to_insert = to_insert[len(self.__prefix):]
        self._neditor.textCursor().insertText(to_insert)
        self.hide_completer()

    def complete(self):
        if self._neditor.is_comment():
            return
        self._cc.clean_up()
        # Get data from editor
        source = self._neditor.text
        lineno, offset = self._neditor.cursor_position
        self.__prefix = self._neditor._text_under_cursor()
        # Prepare the worker and run thread
        self._cc.prepare(source, lineno, offset)
        self._cc_thread.start()

    def hide_completer(self):
        self.hide()
        self.__prefix = ''
        self.__stop_thread()

    def __stop_thread(self):
        self._cc_thread.quit()
        self._cc_thread.wait(100)

    def set_geometry(self):
        cursor_rect = self._neditor.cursorRect()
        desktop_geo = self.__desktop.availableGeometry(self._neditor)
        point = self._neditor.mapToGlobal(cursor_rect.topLeft())
        cursor_rect.moveTopLeft(point)
        orientation = (point.y() + 200) < desktop_geo.height()
        if orientation:
            cursor_rect.moveTop(cursor_rect.bottom())
        cursor_rect.setWidth(500)
        cursor_rect.setHeight(self._root.getHeight())
        if not orientation:
            cursor_rect.moveBottom(cursor_rect.top())
        xpos = desktop_geo.width() - (point.x() + 100)
        if xpos < 0:
            cursor_rect.moveLeft(cursor_rect.left() + xpos)
        else:
            cursor_rect.moveRight(cursor_rect.right() + 50)
        self.setGeometry(cursor_rect)

    def next_item(self):
        self._root.nextItem()

    def previous_item(self):
        self._root.previousItem()
"""
