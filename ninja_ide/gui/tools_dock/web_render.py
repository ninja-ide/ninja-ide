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

    def render_from_html(self, html, url=None):
        url = url and QUrl(url) or ""
        self.webFrame.setHtml(html, url)
