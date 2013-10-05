# -*- coding: utf-8 -*-

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QCursor
from PyQt4.QtGui import QMenu
from PyQt4.QtGui import QIcon
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
from PyQt4.QtCore import Qt

from ninja_ide import translations
from ninja_ide import resources


class ComboEditor(QWidget):

    def __init__(self, original=False):
        super(ComboEditor, self).__init__()
        self.__original = original
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)

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
        hbox.setSpacing(1)

        self.lbl_checks = QLabel('')
        self.lbl_checks.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.lbl_checks.setFixedWidth(48)
        self.lbl_checks.setVisible(False)
        hbox.addWidget(self.lbl_checks)

        self.combo = QComboBox()
        self.combo.setMaximumWidth(300)
        self.combo.setObjectName("combotab")
        self.connect(self.combo, SIGNAL("currentIndexChanged(int)"),
            self.current_changed)
        hbox.addWidget(self.combo)

        self.symbols_combo = QComboBox()
        self.symbols_combo.setObjectName("combo_symbols")
        self.connect(self.symbols_combo, SIGNAL("currentIndexChanged(int)"),
            self.current_changed)
        hbox.addWidget(self.symbols_combo)

        self.code_navigator = CodeNavigator()
        hbox.addWidget(self.code_navigator)

        self._pos_text = "Line: %d, Col: %d"
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
        self.combo.addItem(QIcon(resources.IMAGES['bug']), text, data)
        self.combo.setCurrentIndex(self.combo.count() - 1)

    def current_changed(self, index):
        data = self.combo.itemData(index)
        self.emit(SIGNAL("changeCurrent(PyQt_PyObject)"), data)

    def update_line_col(self, line, col):
        self.lbl_position.setText(self._pos_text % (line, col))


class CodeNavigator(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.setContextMenuPolicy(Qt.DefaultContextMenu)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setContentsMargins(0, 0, 0, 0)
        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(1, 1, 5, 1)
        hbox.setSpacing(0)
        self.btnPrevious = QPushButton(
            QIcon(resources.IMAGES['nav-code-left']), '')
        self.btnPrevious.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.btnPrevious.setObjectName('navigation_button')
        self.btnPrevious.setToolTip(
            self.tr("Right click to change navigation options"))
        self.btnNext = QPushButton(
            QIcon(resources.IMAGES['nav-code-right']), '')
        self.btnNext.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.btnNext.setObjectName('navigation_button')
        self.btnNext.setToolTip(
            self.tr("Right click to change navigation options"))
        hbox.addWidget(self.btnPrevious)
        hbox.addWidget(self.btnNext)

        self.menuNavigate = QMenu(self.tr("Navigate"))
        self.codeAction = self.menuNavigate.addAction(
            self.tr("Code Jumps"))
        self.codeAction.setCheckable(True)
        self.codeAction.setChecked(True)
        self.bookmarksAction = self.menuNavigate.addAction(
            self.tr("Bookmarks"))
        self.bookmarksAction.setCheckable(True)
        self.breakpointsAction = self.menuNavigate.addAction(
            self.tr("Breakpoints"))
        self.breakpointsAction.setCheckable(True)

        # 0 = Code Jumps
        # 1 = Bookmarks
        # 2 = Breakpoints
        self.operation = 0

        self.connect(self.codeAction, SIGNAL("triggered()"),
            self._show_code_nav)
        self.connect(self.breakpointsAction, SIGNAL("triggered()"),
            self._show_breakpoints)
        self.connect(self.bookmarksAction, SIGNAL("triggered()"),
            self._show_bookmarks)

    def contextMenuEvent(self, event):
        self.show_menu_navigation()

    def show_menu_navigation(self):
        self.menuNavigate.exec_(QCursor.pos())

    def _show_bookmarks(self):
        self.btnPrevious.setIcon(QIcon(resources.IMAGES['book-left']))
        self.btnNext.setIcon(QIcon(resources.IMAGES['book-right']))
        self.bookmarksAction.setChecked(True)
        self.breakpointsAction.setChecked(False)
        self.codeAction.setChecked(False)
        self.operation = 1

    def _show_breakpoints(self):
        self.btnPrevious.setIcon(QIcon(resources.IMAGES['break-left']))
        self.btnNext.setIcon(QIcon(resources.IMAGES['break-right']))
        self.bookmarksAction.setChecked(False)
        self.breakpointsAction.setChecked(True)
        self.codeAction.setChecked(False)
        self.operation = 2

    def _show_code_nav(self):
        self.btnPrevious.setIcon(QIcon(resources.IMAGES['nav-code-left']))
        self.btnNext.setIcon(QIcon(resources.IMAGES['nav-code-right']))
        self.bookmarksAction.setChecked(False)
        self.breakpointsAction.setChecked(False)
        self.codeAction.setChecked(True)
        self.operation = 0
