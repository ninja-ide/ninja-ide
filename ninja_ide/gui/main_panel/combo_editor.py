# -*- coding: utf-8 -*-

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QFrame
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QStackedLayout
from PyQt4.QtGui import QStyle
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QComboBox
from PyQt4.QtGui import QSizePolicy
from PyQt4.QtGui import QPushButton
from PyQt4.QtCore import SIGNAL

from ninja_ide import translations


class ComboEditor(QWidget):

    def __init__(self, original=False):
        super(ComboEditor, self).__init__()
        self.__original = original
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)

        self.bar = ActionBar()
        self.connect(self.bar, SIGNAL("changeCurrent(PyQt_PyObject)"),
            self.set_current)
        vbox.addWidget(self.bar)

        self.stacked = QStackedLayout()
        vbox.addLayout(self.stacked)

    def currentWidget(self):
        return self.stacked.currentWidget()

    def add_editor(self, neditable):
        """Add Editor Widget to the UI area."""
        if neditable.editor:
            self.stacked.addWidget(neditable.editor)
            self.bar.add_item(neditable.display_name, neditable)

            # Editor Signals
            self.connect(neditable.editor, SIGNAL("cursorPositionChanged()"),
                self._update_cursor_position)

            # Connect file system signals only in the original
            if self.__original:
                pass

    def set_current(self, neditable):
        self.stacked.setCurrentWidget(neditable.editor)
        self._update_cursor_position(ignore_sender=True)
        neditable.editor.setFocus()

    def widget(self, index):
        return self.stacked.widget(index)

    def count(self):
        """Return the number of editors opened."""
        return self.stacked.count()

    def _update_cursor_position(self, ignore_sender=False):
        obj = self.sender()
        editor = self.stacked.currentWidget()
        # Check if it's current to avoid signals from other splits.
        if ignore_sender or editor == obj:
            line = editor.textCursor().blockNumber() + 1
            col = editor.textCursor().columnNumber()
            self.bar.update_line_col(line, col)


class ActionBar(QFrame):
    """
    SIGNALS:
    @changeCurrent(PyQt_PyObject)
    """

    def __init__(self):
        super(ActionBar, self).__init__()
        self.setObjectName("actionbar")
        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(1, 1, 1, 1)

        self.combo = QComboBox()
        self.combo.setObjectName("combotab")
        self.connect(self.combo, SIGNAL("currentIndexChanged(int)"),
            self.current_changed)
        hbox.addWidget(self.combo)

        self.lbl_checks = QLabel('')
        self.lbl_checks.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        hbox.addWidget(self.lbl_checks)

        self._pos_text = "Ln: %d, Col: %d"
        self.lbl_position = QLabel(self._pos_text % (0, 0))
        self.lbl_position.setObjectName("position")
        self.lbl_position.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        hbox.addWidget(self.lbl_position)

        self.btn_close = QPushButton(
            self.style().standardIcon(QStyle.SP_DialogCloseButton), '')
        self.btn_close.setObjectName('navigation_button')
        self.btn_close.setToolTip(translations.TR_CLOSE_SPLIT)
        self.btn_close.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        hbox.addWidget(self.btn_close)

    def add_item(self, text, data):
        self.combo.addItem(text, data)
        self.combo.setCurrentIndex(self.combo.count() - 1)

    def current_changed(self, index):
        data = self.combo.itemData(index)
        self.emit(SIGNAL("changeCurrent(PyQt_PyObject)"), data)

    def update_line_col(self, line, col):
        self.lbl_position.setText(self._pos_text % (line, col))