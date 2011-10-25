# -*- coding: utf-8 -*-
from __future__ import absolute_import

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtWebKit import QWebView
from PyQt4.QtCore import QUrl
from PyQt4.QtWebKit import QWebSettings


class WebRender(QWidget):

    def __init__(self):
        QWidget.__init__(self)

        vbox = QVBoxLayout(self)
        #Web Frame
        self.webFrame = QWebView()
        QWebSettings.globalSettings().setAttribute(
            QWebSettings.DeveloperExtrasEnabled, True)
        vbox.addWidget(self.webFrame)

    def render_page(self, url):
        self.webFrame.load(QUrl('file:///' + url))
