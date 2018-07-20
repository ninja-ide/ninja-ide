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
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QStyle
from PyQt5.QtWidgets import QStylePainter
from PyQt5.QtWidgets import QStyleOptionFrame
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QStyledItemDelegate

from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QColor

from PyQt5.QtCore import QAbstractListModel
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QModelIndex
from PyQt5.QtCore import QEvent
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import QPoint
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QSize

from ninja_ide.core import settings

# TODO: implement delegate


class ProposalItem(object):
    """
    The ProposalItem class acts as an interface for representing an assist
    proposal item.
    """
    __slots__ = ("text", "type", "detail", "__icon")

    def __init__(self, text):
        self.text = text
        self.type = None
        self.detail = None
        self.__icon = None

    @property
    def lower_text(self):
        return self.text.lower()

    @property
    def icon(self):
        return self.__icon

    def set_icon(self, icon_name):
        self.__icon = QIcon(":img/{}".format(icon_name))

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "<ProposalItem:%s:%s>" % (self.text, self.type)


class ProposalModel(QAbstractListModel):
    """
    List model for proposals
    """

    PROPOSALS_STEP = 20

    def __init__(self, parent=None):
        super().__init__(parent)

    def fetchMore(self, parent):
        remainder = len(self.__current_proposals) - self.__item_count
        items_to_fetch = min(self.PROPOSALS_STEP, remainder)
        self.beginInsertRows(
            QModelIndex(), self.__item_count,
            self.__item_count + items_to_fetch - 1)
        self.__item_count += items_to_fetch
        self.endInsertRows()

    def canFetchMore(self, parent):
        if self.__item_count < len(self.__current_proposals):
            return True
        return False

    def set_items(self, items):
        self.beginResetModel()
        self.__current_proposals = items
        self.__original_proposals = items
        self.__item_count = self.PROPOSALS_STEP
        self.endResetModel()

    def rowCount(self, index=None):
        count = self.__item_count
        if len(self.__current_proposals) < count:
            count = len(self.__current_proposals)
        return count

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() >= len(self.__current_proposals):
            return None
        item = self.__current_proposals[index.row()]
        if role == Qt.DisplayRole:
            return item.text
        elif role == Qt.DecorationRole:
            return item.icon
        elif role == Qt.UserRole:
            return item.type
        elif role == Qt.WhatsThisRole:
            return item.detail
        return None

    def item(self, index):
        return self.__current_proposals[index]

    def has_proposals(self):
        return len(self.__current_proposals) > 0

    def filter(self, prefix):
        if not prefix:
            # Reset
            self.__current_proposals = self.__original_proposals
            return
        self.__current_proposals = [item for item in self.__original_proposals
                                    if item.lower_text.startswith(
                                        prefix.lower())]

    def is_pre_filtered(self, prefix):
        return self.__prefix and prefix == self.__prefix


class ProposalDelegate(QStyledItemDelegate):
    """Custom delegate that adds the proposal type"""

    def paint(self, painter, opt, index):
        self.initStyleOption(opt, index)
        painter.save()
        widget = opt.widget
        widget.style().drawControl(
            QStyle.CE_ItemViewItem, opt, painter, widget)
        proposal_type = index.data(Qt.UserRole)
        font = painter.font()
        font.setItalic(True)
        font.setPointSize(font.pointSize() * 0.98)
        painter.setFont(font)
        if opt.state & QStyle.State_Selected:
            painter.setPen(QColor(opt.palette.text()))
        else:
            painter.setPen(
                opt.palette.color(opt.palette.Disabled, opt.palette.Text))
        rect = opt.rect
        # Just a margin
        rect.setRight(rect.right() - 10)
        painter.drawText(rect, Qt.AlignRight, proposal_type)
        painter.restore()

    def sizeHint(self, opt, index):
        sh = super().sizeHint(opt, index)
        return QSize(sh.width() + 130, sh.height())


class ProposalView(QListView):
    """
    View for proposals
    """

    MAX_VISIBLE_ITEMS = 10

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(settings.FONT)
        # self.setFrameStyle(QFrame.NoFrame)
        self.setUniformItemSizes(True)
        self.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
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

    def info_frame_position(self):
        r = self.rectForIndex(self.currentIndex())
        point = QPoint((self.parentWidget().mapToGlobal(
            self.parentWidget().rect().topRight()
        )).x() + 3, self.mapToGlobal(r.topRight()).y() - self.verticalOffset())
        return point

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


class InfoFrame(QFrame):
    """Widget to show call tips"""

    def __init__(self, parent):
        super().__init__(parent, Qt.ToolTip | Qt.WindowStaysOnTopHint)
        self.setObjectName("custom_tip")
        self.setFocusPolicy(Qt.NoFocus)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self._label = QLabel()
        self._label.setStyleSheet("border: none")
        font = parent.font()
        font.setPointSize(font.pointSize() * 0.9)
        self._label.setFont(font)
        self._label.setSizePolicy(
            QSizePolicy.Fixed, self._label.sizePolicy().verticalPolicy())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.addWidget(self._label)

    def set_text(self, text):
        self._label.setText(text)

    def paintEvent(self, event):
        p = QStylePainter(self)
        opt = QStyleOptionFrame()
        opt.initFrom(self)
        p.drawPrimitive(QStyle.PE_PanelTipLabel, opt)
        p.end()

    def calculate_width(self):
        desk = QApplication.desktop()
        desk_width = desk.availableGeometry(desk.primaryScreen()).width()
        if desk.isVirtualDesktop():
            desk_width = desk.width()
        widget_margins = self.contentsMargins()
        layout_margins = self.layout().contentsMargins()
        margins = widget_margins.left() + widget_margins.right() + \
            layout_margins.left() + layout_margins.right()
        self._label.setMaximumWidth(desk_width - self.pos().x() - margins)


class ProposalWidget(QFrame):
    """
    Proposal Widget for display completions and snippets
    """

    proposalItemActivated = pyqtSignal("PyQt_PyObject")

    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self._editor = parent
        self._model = None
        self._prefix = None
        self._auto_width = True
        self._info_frame = None
        self._info_timer = QTimer(self)
        self._info_timer.setSingleShot(True)
        self._info_timer.setInterval(100)
        self._info_timer.timeout.connect(self.show_info)
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        self._proposal_view = ProposalView()
        self.setFrameStyle(self._proposal_view.frameStyle())
        self._proposal_view.setFrameStyle(QFrame.NoFrame)
        # self._proposal_view.setItemDelegate(ProposalDelegate())

        self._proposal_view.installEventFilter(self)
        vbox.addWidget(self._proposal_view)

        # Connections
        vertical_scrollbar = self._proposal_view.verticalScrollBar()
        vertical_scrollbar.valueChanged.connect(
            self.update_size_and_position)
        self._proposal_view.clicked.connect(self._handle_view_activation)
        vertical_scrollbar.sliderPressed.connect(self._turn_off_autowidth)
        vertical_scrollbar.sliderReleased.connect(self._turn_on_autowidth)

    def _handle_view_activation(self, index):
        self.abort()
        self.insert_proposal(index.row())

    def show_info(self):
        current = self._proposal_view.currentIndex()
        if not current.isValid():
            return
        info = current.data(Qt.WhatsThisRole)
        if not info:
            if self._info_frame is not None:
                self._info_frame.close()
                self._info_frame = None
            return
        if self._info_frame is None:
            self._info_frame = InfoFrame(self._proposal_view)
        self._info_frame.move(self._proposal_view.info_frame_position())
        self._info_frame.set_text(info)
        self._info_frame.calculate_width()
        self._info_frame.adjustSize()
        self._info_frame.show()
        self._info_frame.raise_()
        self._info_timer.setInterval(0)

    def set_model(self, model):
        if self._model is not None:
            self._model.deleteLater()
            del self._model
            self._model = None
        self._model = model
        self._proposal_view.setModel(self._model)
        self._proposal_view.selectionModel().currentChanged.connect(
            self._info_timer.start)

    def show_proposal(self, prefix=None):
        self._proposal_view.setFont(self._editor.font())
        self.update_size_and_position()
        self.show()
        self._proposal_view.select_first()
        self._proposal_view.setFocus()

    def _turn_off_autowidth(self):
        self._auto_width = False

    def _turn_on_autowidth(self):
        self._auto_width = True
        self.update_size_and_position()

    def update_size_and_position(self):
        if not self._auto_width:
            return
        size_hint = self._proposal_view.calculate_size()
        frame_width = self.frameWidth()
        width = size_hint.width() + frame_width * 2 + 30
        height = size_hint.height() + frame_width * 2
        desktop = QApplication.instance().desktop()
        screen = desktop.screenGeometry(desktop.screenNumber(self._editor))
        if settings.IS_MAC_OS:
            screen = desktop.availableGeometry(
                desktop.screenNumber(self._editor))
        cr = self._editor.cursorRect()
        pos = cr.bottomLeft()
        rx = pos.x() + 60  # FIXME: why 60?
        pos.setX(rx)
        if pos.y() + height > screen.bottom():
            pos.setY(max(0, cr.top() - height))
        if pos.x() + width > screen.right():
            pos.setX(max(0, screen.right() - width))
        self.setGeometry(pos.x(), pos.y(), min(width, screen.width()),
                         min(height, screen.height()))

    def eventFilter(self, obj, event):
        if event.type() == QEvent.FocusOut:
            self.abort()
            if self._info_frame is not None:
                self._info_frame.close()
            return True
        elif event.type() == QEvent.KeyPress:
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
                                 Qt.Key_End):
                self.abort()
            else:
                pass
            QApplication.sendEvent(self._editor, event)
            if self.isVisible():
                self.update_proposal()
            return True

        return False

    def update_proposal(self):
        word = self._editor.word_under_cursor().selectedText()
        self._model.filter(word)
        if not self._model.has_proposals():
            self.abort()
        self._proposal_view.select_first()
        self.update_size_and_position()
        if self._info_frame is not None:
            self._info_frame.move(self._proposal_view.info_frame_position())

    def insert_proposal(self, row=None):
        if row is None:
            if self._proposal_view.currentIndex().isValid():
                row = self._proposal_view.currentIndex().row()
        item = self._proposal_view.model().item(row)
        self.proposalItemActivated.emit(item)

    def abort(self):
        if self.isVisible():
            self.close()
        self._editor.setFocus()
