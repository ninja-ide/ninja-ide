# -*- coding: utf-8 -*-

import os
from urlparse import urlparse, urlunparse

from PyQt4.QtGui import QFrame
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtCore import QDir
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QUrl
from PyQt4.QtDeclarative import QDeclarativeView

from ninja_ide import resources


class Notification(QFrame):

    def __init__(self, parent=None):
        super(Notification, self).__init__()
        self._parent = parent
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setStyleSheet("background:transparent;")
        self.setWindowFlags(Qt.FramelessWindowHint)
        #self.setMinimumHeight(120)
        # Create the QML user interface.
        view = QDeclarativeView()
        view.setResizeMode(QDeclarativeView.SizeRootObjectToView)
        path_qml = QDir.fromNativeSeparators(
            os.path.join(resources.QML_FILES, "Notification.qml"))
        path_qml = urlunparse(urlparse(path_qml)._replace(scheme='file'))
        view.setSource(QUrl(path_qml))
        self.root = view.rootObject()
        vbox = QVBoxLayout(self)
        vbox.addWidget(view)

    def showEvent(self, event):
        super(Notification, self).showEvent(event)
        point = self._parent.central.mapToGlobal(self._parent.pos())
        self.move(point.x(), point.y())

    def set_text(self, text=''):
        self.root.set_text(text)