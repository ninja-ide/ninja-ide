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
from __future__ import unicode_literals

import time

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QUrl
from PyQt4.QtCore import SIGNAL
from PyQt4.QtWebKit import QWebView

from ninja_ide.core import file_manager
from ninja_ide.gui.main_panel import itab_item


class BrowserWidget(QWidget, itab_item.ITabItem):

###############################################################################
# RecentProjectItem SIGNALS
###############################################################################
    """
    openProject(QString)
    openPreferences()
    dontOpenStartPage()
    """
###############################################################################

    def __init__(self, url, process=None, parent=None):
        QWidget.__init__(self, parent)
        itab_item.ITabItem.__init__(self)
        self._id = url
        self._process = process
        vbox = QVBoxLayout(self)
        #Web Frame
        self.webFrame = QWebView(self)
        self.webFrame.setAcceptDrops(False)

        self.webFrame.load(QUrl(url))

        vbox.addWidget(self.webFrame)

        if process is not None:
            time.sleep(0.5)
            self.webFrame.load(QUrl(url))

        self.webFrame.page().currentFrame().setScrollBarPolicy(
            Qt.Vertical, Qt.ScrollBarAsNeeded)
        self.webFrame.page().currentFrame().setScrollBarPolicy(
            Qt.Horizontal, Qt.ScrollBarAsNeeded)

    def start_page_operations(self, url):
        opt = file_manager.get_basename(url.toString())
        self.emit(SIGNAL(opt))

    def shutdown_pydoc(self):
        if self._process is not None:
            self._process.kill()

    def find_match(self, word, back=False, sensitive=False, whole=False):
        self.webFrame.page().findText(word)