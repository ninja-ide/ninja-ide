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
    QWidget,
    QSizePolicy,
    QToolTip,
)
from PyQt5.QtGui import (
    QPainter,
    QColor,
)
from PyQt5.QtCore import (
    QObject,
    QSize,
    QRect,
    Qt,
    QEvent,
    QPropertyAnimation,
    pyqtProperty,
)

BAR_BACKGROUND_COLOR = '#232323'
BAR_BUTTON_HOVER_COLOR = '#434343'
BAR_BUTTON_SELECTED_COLOR = '#55555'
BAR_BUTTON_TEXT_COLOR = '#f9f9f9'

# FIXME: icon property (we can use FontAwesome in text property)


class ToolButton(QObject):

    def __init__(self, text: str, bar=None):
        super().__init__(bar)
        self.text = text
        self.tooltip: str = None
        self._fader = 0
        self._animator = QPropertyAnimation()
        self._animator.setPropertyName(b'fader')
        self._animator.setTargetObject(self)

    @pyqtProperty(float)
    def fader(self):
        return self._fader

    @fader.setter
    def fader(self, value: float):
        self._fader = value
        self.parent().update()

    def fade_in(self):
        self._animator.stop()
        self._animator.setDuration(80)
        self._animator.setEndValue(1)
        self._animator.start()

    def fade_out(self):
        self._animator.stop()
        self._animator.setDuration(100)
        self._animator.setEndValue(0)
        self._animator.start()


class ToolBar(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.setFocusPolicy(Qt.NoFocus)
        self.setAttribute(Qt.WA_Hover)
        self.setMouseTracking(True)

        self._tabs: list = []
        self._current_index = -1
        self._hover_index = -1

    @property
    def current_index(self) -> int:
        return self._current_index

    def insert_tab(self, index: int, label: str, tooltip: str = None):
        tab = ToolButton(text=label, bar=self)
        if tooltip is not None:
            tab.tooltip = tooltip
        self._tabs.insert(index, tab)

    def remove_tab(self, index: int):
        tab_to_remove = self._tabs.pop(index)
        tab_to_remove.deleteLater()

    def set_tab_tooltip(self, index: int, tooltip: str):
        self._tabs[index].tooltip = tooltip

    def tab_tooltip(self, index: int) -> str:
        return self._tabs[index].tooltip

    def count(self) -> int:
        return len(self._tabs)

    def sizeHint(self) -> QSize:
        tab_sh = self.tab_size_hint()
        return QSize(tab_sh.width(), tab_sh.height() * self.count())

    def tab_size_hint(self) -> QSize:
        return QSize(30, 30)

    def tab_rect(self, index: int) -> QRect:
        tab_sh = self.tab_size_hint()
        return QRect(
            0,
            index * tab_sh.height(),
            tab_sh.width(),
            tab_sh.height()
        )

    def enterEvent(self, event):
        self._hover_index = -1

    def leaveEvent(self, event):
        for tab in self._tabs:
            tab.fade_out()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(event.rect(), QColor(BAR_BACKGROUND_COLOR))

        # Paint tabs
        painter.save()
        for i, tab in enumerate(self._tabs):
            self.paint_button(painter, tab, i)
        painter.restore()

    def paint_button(self, painter, btn, index):
        painter.save()

        rec = self.tab_rect(index)

        # Paint selected
        is_selected = self._current_index == index
        if is_selected:
            painter.fillRect(rec, QColor(BAR_BUTTON_SELECTED_COLOR))

        # Fader
        fader = btn.fader
        if fader > 0:
            painter.save()
            painter.setOpacity(fader)
            painter.fillRect(rec, QColor(BAR_BUTTON_HOVER_COLOR))
            painter.restore()

        # Paint text
        painter.setPen(QColor(BAR_BUTTON_TEXT_COLOR))
        painter.drawText(rec, Qt.AlignCenter, btn.text)

        painter.restore()

    def mouseMoveEvent(self, event):
        hover_index = -1
        for i, tab in enumerate(self._tabs):
            rec = self.tab_rect(i)
            if rec.contains(event.pos()):
                hover_index = i
                break

        if self._hover_index == hover_index:
            return

        if self._hover_index != -1:
            self._tabs[self._hover_index].fade_out()
        self._hover_index = hover_index

        if self._hover_index != -1:
            self._tabs[self._hover_index].fade_in()

    def mousePressEvent(self, event):
        for i, tab in enumerate(self._tabs):
            rec = self.tab_rect(i)
            if rec.contains(event.pos()):
                if self._current_index != i:
                    self._current_index = i
                break

    def event(self, event):
        if event.type() == QEvent.ToolTip:
            tooltip = self.tab_tooltip(self._hover_index)
            QToolTip.showText(event.globalPos(), tooltip, self)
            return True

        return super().event(event)


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication, QHBoxLayout, QPlainTextEdit
    app = QApplication([])
    w = QWidget()
    layout = QHBoxLayout(w)
    tb = ToolBar()
    tb.insert_tab(0, 'hola', 'queeeee ondaaaaaa')
    tb.insert_tab(1, 'chau')
    tb.insert_tab(1, 'chau')
    tb.insert_tab(1, 'chau')
    layout.addWidget(tb)
    layout.addWidget(QPlainTextEdit())
    w.show()
    app.exec_()
