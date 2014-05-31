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

from tempfile import mkdtemp

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtWebKit import QWebView
from PyQt4.QtCore import QUrl
from PyQt4.QtWebKit import QWebSettings


class WebRender(QWidget):

    """Render a web page inside the tools dock area."""

    def __init__(self):
        super(WebRender, self).__init__()
        vbox, temporary_directory = QVBoxLayout(self), mkdtemp()
        # Web Frame
        self.webFrame = QWebView()  # QWebView = QWebFrame + QWebSettings
        self.webFrame.setStyleSheet("QWebView{ background:#fff }")  # no dark bg
        settings = self.webFrame.settings()  # QWebSettings instance
        settings.setDefaultTextEncoding("utf-8")
        settings.setIconDatabasePath(temporary_directory)
        settings.setLocalStoragePath(temporary_directory)
        settings.setOfflineStoragePath(temporary_directory)
        settings.setOfflineWebApplicationCachePath(temporary_directory)
        settings.setAttribute(QWebSettings.DeveloperExtrasEnabled, True)
        settings.setAttribute(QWebSettings.LocalStorageEnabled, True)
        settings.setAttribute(QWebSettings.OfflineStorageDatabaseEnabled, True)
        settings.setAttribute(QWebSettings.PluginsEnabled, True)
        settings.setAttribute(QWebSettings.DnsPrefetchEnabled, True)
        settings.setAttribute(QWebSettings.JavascriptCanOpenWindows, True)
        settings.setAttribute(QWebSettings.JavascriptCanCloseWindows, True)
        settings.setAttribute(QWebSettings.JavascriptCanAccessClipboard, True)
        settings.setAttribute(QWebSettings.SpatialNavigationEnabled, True)
        settings.setAttribute(
            QWebSettings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(
            QWebSettings.OfflineWebApplicationCacheEnabled, True)
        vbox.addWidget(self.webFrame)

    def render_page(self, url):
        """Render a web page from a local file."""
        self.webFrame.load(QUrl('file:///' + url))

    def render_from_html(self, html, url=None):
        """Render a webpage from a string."""
        url = url and QUrl(url) or ""
        self.webFrame.setHtml(html, url)
