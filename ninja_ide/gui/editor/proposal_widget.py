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

from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QListView
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtWidgets import QApplication

from PyQt5.QtGui import QIcon

from PyQt5.QtCore import QAbstractListModel
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QEvent
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QSize

from ninja_ide.core import settings


class ProposalItem(object):
    __slots__ = ("text", "type")

    def __init__(self, text):
        self.text = text
        self.type = None

    @property
    def lower_text(self):
        return self.text.lower()


class ProposalModel(QAbstractListModel):
    """
    List model for proposals
    """

    def __init__(self, proposals, parent=None):
        super().__init__(parent)
        self.__original_proposals = proposals
        self.__current_proposals = proposals

    def rowCount(self, index=None):
        return len(self.__current_proposals)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() >= len(self.__current_proposals):
            return None
        if role == Qt.DisplayRole:
            return self.__current_proposals[index.row()].text
        elif role == Qt.DecorationRole:
            return QIcon(
                ":img/%s" % self.__current_proposals[index.row()].type)
        return None

    def item(self, index):
        return self.__current_proposals[index]

    def has_proposals(self):
        return len(self.__current_proposals) > 0

    def filter(self, prefix):
        if not prefix:
            return
        prefix = prefix.lower()
        new_data = [item for item in self.__original_proposals
                    if item.lower_text.startswith(prefix)]
        self.__current_proposals = new_data
        self.layoutChanged.emit()


class ProposalView(QListView):
    """
    View for proposals
    """

    MAX_VISIBLE_ITEMS = 10

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(settings.FONT)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerItem)

    def select_row(self, row):
        self.setCurrentIndex(self.model().index(row, 0))

    def select_first(self):
        self.select_row(0)

    def select_last(self):
        self.select_row(self.model().rowCount() - 1)

    def row_selected(self):
        return self.currentIndex().row()

    def is_first_selected(self):
        return self.row_selected() == 0

    def is_last_selected(self):
        return self.row_selected() == self.model().rowCount() - 1

    def calculate_size(self):
        """Determine size by calculating the space of the visible items"""

        visible_items = min(self.model().rowCount(), self.MAX_VISIBLE_ITEMS)
        first_visible_row = self.verticalScrollBar().value()
        option = self.viewOptions()
        size_hint = QSize()
        for index in range(visible_items):
            tmp_size = self.itemDelegate().sizeHint(
                option, self.model().index(index + first_visible_row, 0))
            if size_hint.width() < tmp_size.width():
                size_hint = tmp_size

        height = size_hint.height()
        height *= visible_items
        size_hint.setHeight(height)
        return size_hint


class ProposalWidget(QFrame):
    """
    Proposal Widget for display completions and snippets
    """

    proposalItemActivated = pyqtSignal("PyQt_PyObject")

    def __init__(self, parent):
        super().__init__(parent)
        # self.setWindowFlags(Qt.SubWindow | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self._editor = parent
        self._model = None
        self._prefix = None
        self.setFrameStyle(QFrame.NoFrame)
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        self._proposal_view = ProposalView()
        self._proposal_view.installEventFilter(self)
        vbox.addWidget(self._proposal_view)

        self._proposal_view.verticalScrollBar().valueChanged.connect(
            self.update_size_and_position)

        self.hide()

    def set_model(self, model):
        if self._model is not None:
            self._model.deleteLater()
            del self._model
            self._model = None
        self._model = model
        self._proposal_view.setModel(self._model)

    def show_proposal(self, prefix=None):
        self._proposal_view.select_first()
        self.update_size_and_position()
        self.show()
        self._proposal_view.setFocus()

    def update_size_and_position(self):
        size_hint = self._proposal_view.calculate_size()
        frame_width = self.frameWidth()
        width = size_hint.width() + frame_width * 2 + 30
        height = size_hint.height() + frame_width * 2
        desktop = QApplication.instance().desktop()
        # screen = desktop.availableGeometry(self._editor)
        screen = desktop.screenGeometry(desktop.screenNumber(self._editor))
        cr = self._editor.cursorRect()
        pos = cr.bottomLeft()
        rx = pos.x() + 60
        pos.setX(rx)
        if pos.y() + height > screen.bottom():
            pos.setY(max(0, cr.top() - height))
        if pos.x() + width > screen.right():
            pos.setX(max(0, screen.y() - width))
        self.setGeometry(pos.x(), pos.y(), min(width, screen.width()),
                         min(height, screen.height()))

    def eventFilter(self, obj, event):
        if event.type() == QEvent.FocusOut:
            self.abort()
            return True
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Escape:
                self.abort()
                event.accept()
                return True
            elif event.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Tab):
                self.abort()
                self.insert_proposal()
                return True
            elif event.key() == Qt.Key_Up:
                if self._proposal_view.is_first_selected():
                    self._proposal_view.select_last()
                    return True
                return False
            elif event.key() == Qt.Key_Down:
                if self._proposal_view.is_last_selected():
                    self._proposal_view.select_first()
                    return True
                return False
            elif event.key() in (Qt.Key_Left, Qt.Key_Right, Qt.Key_Home,
                                 Qt.Key_Backspace, Qt.Key_End):
                # We want these navigation keys to work in the editor
                pass
            else:
                pass
            QApplication.sendEvent(self._editor, event)
            if self.isVisible():
                w = self._editor.word_under_cursor().selectedText()
                self._proposal_view.model().filter(w)
                if not self._proposal_view.model().has_proposals():
                    self.abort()
                self.update_size_and_position()
            return True

        return False

    def insert_proposal(self):
        if self._proposal_view.currentIndex().isValid():
            row = self._proposal_view.currentIndex().row()
            item = self._proposal_view.model().item(row)
            self.proposalItemActivated.emit(item)

    def abort(self):
        if self.isVisible():
            self.close()
        self._editor.setFocus()
