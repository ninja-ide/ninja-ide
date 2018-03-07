# -*- coding: utf-8 -*-


from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QWidget,
    QShortcut
)
from PyQt5.QtGui import QKeySequence
from PyQt5.QtQuickWidgets import QQuickWidget
from PyQt5.QtCore import Qt

from ninja_ide import resources
from ninja_ide.gui.ide import IDE
from ninja_ide.tools import ui_tools


class SplitOrientation(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent, Qt.Dialog | Qt.FramelessWindowHint)
        self._operations = {'row': False, 'col': True}
        self.setModal(True)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background:transparent;")
        self.setFixedHeight(150)
        self.setFixedWidth(290)
        # Create the QML user interface.
        view = QQuickWidget()
        view.setClearColor(Qt.transparent)
        view.rootContext().setContextProperty("theme", resources.QML_COLORS)
        view.setResizeMode(QQuickWidget.SizeRootObjectToView)
        view.setSource(ui_tools.get_qml_resource("SplitOrientation.qml"))
        self._root = view.rootObject()
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        vbox.addWidget(view)
        view.setFocusPolicy(Qt.StrongFocus)

        short_esc = QShortcut(QKeySequence(Qt.Key_Escape), self)
        short_esc.activated.connect(self.hide)
        self._root.selected['QString'].connect(self._split_operation)

    def _split_operation(self, orientation):
        main_container = IDE.get_service("main_container")
        main_container.show_split(self._operations[orientation])
        self.hide()
