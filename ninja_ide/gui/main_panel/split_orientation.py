# -*- coding: utf-8 -*-


from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtCore import Qt
from PyQt4.QtDeclarative import QDeclarativeView

from ninja_ide.tools import ui_tools


class SplitOrientation(QDialog):

    def __init__(self, parent=None):
        super(SplitOrientation, self).__init__(parent,
            Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background:transparent;")
        self.setFixedHeight(180)
        self.setFixedWidth(315)
        # Create the QML user interface.
        view = QDeclarativeView()
        view.setResizeMode(QDeclarativeView.SizeRootObjectToView)
        view.setSource(ui_tools.get_qml_resource("SplitOrientation.qml"))
        self._root = view.rootObject()
        vbox = QVBoxLayout(self)
        vbox.addWidget(view)
