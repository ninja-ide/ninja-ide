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

from ninja_ide import translations
from ninja_ide.gui.editor import neditable
from ninja_ide.gui.editor import editor


class ComboTabs(QWidget):

    def __init__(self):
        super(ComboTabs, self).__init__()
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)

        self.bar = ActionBar()
        vbox.addWidget(self.bar)

        self.stacked = QStackedLayout()
        self.editable = neditable.NEditable('')
        self.editor_widget = editor.create_editor(self.editable)
        self.stacked.addWidget(self.editor_widget)
        vbox.addLayout(self.stacked)

    def currentWidget(self):
        return self.editor_widget


class ActionBar(QFrame):

    def __init__(self):
        super(ActionBar, self).__init__()
        self.setObjectName("actionbar")
        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(1, 1, 1, 1)

        combo = QComboBox()
        combo.setObjectName("combotab")
        hbox.addWidget(combo)
        combo.addItem("main_container.py")
        combo.addItem("ide.py")
        combo.addItem("editor.py")

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
