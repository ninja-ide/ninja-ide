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

from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QUrl
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWebKitWidgets import QWebView

from ninja_ide.core.file_handling import file_manager


class BrowserWidget(QWidget):

###############################################################################
# RecentProjectItem SIGNALS
###############################################################################
    """
    openProject(QString)
    openPreferences()
    dontOpenStartPage()
    """
    openProject = pyqtSignal(str)
    openPreferences = pyqtSignal()
    dontOpenStartPage = pyqtSignal()
###############################################################################

    def __init__(self, url, process=None, parent=None):
        super(BrowserWidget, self).__init__(parent)
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
        #self.emit(SIGNAL(opt))
        getattr(self, url.toString()).emit()


    def shutdown_pydoc(self):
        if self._process is not None:
            self._process.kill()

    def find_match(self, word, back=False, sensitive=False, whole=False):
        self.webFrame.page().findText(word)
