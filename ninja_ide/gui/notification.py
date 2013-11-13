# -*- coding: utf-8 -*-

from PyQt4.QtGui import QFrame
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL
from PyQt4.QtDeclarative import QDeclarativeView

from ninja_ide.tools import ui_tools


class Notification(QFrame):

    def __init__(self, parent=None):
        super(Notification, self).__init__(None, Qt.ToolTip)
        self._parent = parent
        self._duration = 3000
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setStyleSheet("background:transparent;")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFixedHeight(30)
        # Create the QML user interface.
        view = QDeclarativeView()
        view.setResizeMode(QDeclarativeView.SizeRootObjectToView)
        view.setSource(ui_tools.get_qml_resource("Notification.qml"))
        self._root = view.rootObject()
        vbox = QVBoxLayout(self)
        vbox.addWidget(view)
        self._height = self.height()

        self.connect(self._root, SIGNAL("close()"), self.close)

    def showEvent(self, event):
        super(Notification, self).showEvent(event)
        width = self._parent.width() / 2
        x = self._parent.geometry().left()
        y = self._parent.geometry().bottom() - self._height
        self.setFixedWidth(width)
        self.setGeometry(x, y, self.width(), self.height())
        self._root.start(3000)

    def set_message(self, text='', duration=3000):
        self._root.setText(text)
        self._duration = duration