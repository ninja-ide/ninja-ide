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

import sys
import os
import time

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QListWidget
from PyQt4.QtGui import QListWidgetItem
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QUrl
from PyQt4.QtCore import QSettings
from PyQt4.QtCore import SIGNAL
from PyQt4.QtWebKit import QWebView
from PyQt4.QtWebKit import QWebPage
from PyQt4.QtWebKit import QWebSettings
from PyQt4.QtWebKit import QWebPluginFactory


from ninja_ide import resources
from ninja_ide.core import file_manager
from ninja_ide.gui.main_panel import itab_item
from ninja_ide.gui.main_panel import recent_project_item


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
        QWebSettings.globalSettings().setAttribute(
            QWebSettings.PluginsEnabled, True)
        self.webFrame = QWebView(self)
        self.webFrame.setAcceptDrops(False)
        factory = WebPluginFactory(self)

        self.webFrame.page().setPluginFactory(factory)
        self.webFrame.load(QUrl(url))

        vbox.addWidget(self.webFrame)

        if process is not None:
            time.sleep(0.5)
            self.webFrame.load(QUrl(url))

        if url == resources.START_PAGE_URL:
            self.webFrame.page().setLinkDelegationPolicy(
                QWebPage.DelegateAllLinks)
            self.connect(self.webFrame, SIGNAL("linkClicked(QUrl)"),
                self.start_page_operations)
            if sys.platform == "win32":
                content = file_manager.read_file_content(self.ID)
                pathCss = os.path.join(
                    resources.PRJ_PATH, 'doc', 'css', 'style.css')
                pathJs = os.path.join(resources.PRJ_PATH, 'doc', 'js', 'libs')
                pathImg = os.path.join(resources.PRJ_PATH, 'doc', 'img')
                content = content.replace('css/style.css',
                    pathCss).replace(
                    'src="js/libs/', 'src="%s\\' % pathJs).replace(
                    'src="img/', 'src="%s\\' % pathImg)
                self.webFrame.setHtml(content)
            self._id = 'Start Page'
            policy = Qt.ScrollBarAlwaysOff
        else:
            policy = Qt.ScrollBarAsNeeded
        self.webFrame.page().currentFrame().setScrollBarPolicy(
            Qt.Vertical, policy)
        self.webFrame.page().currentFrame().setScrollBarPolicy(
            Qt.Horizontal, policy)

    def start_page_operations(self, url):
        opt = file_manager.get_basename(url.toString())
        self.emit(SIGNAL(opt))

    def shutdown_pydoc(self):
        if self._process is not None:
            self._process.kill()

    def find_match(self, word, back=False, sensitive=False, whole=False):
        self.webFrame.page().findText(word)

    def open_project(self, path):
        self.emit(SIGNAL("openProject(QString)"), path)


class WebPluginList(QListWidget):

    def __init__(self, browserReference):
        self.browser_referece = browserReference
        QListWidget.__init__(self)
        self.setMouseTracking(True)
        self.load_items()

    def load_items(self):
        self.clear()
        settings = QSettings()
        listByFavorites = []
        listNoneFavorites = []
        recent_projects_dict = dict(settings.value('recentProjects', {}))
        #Filter for favorites
        for recent_project_path, content in list(recent_projects_dict.items()):
            if bool(dict(content)["isFavorite"]):
                listByFavorites.append((recent_project_path,
                    content["lastopen"]))
            else:
                listNoneFavorites.append((recent_project_path,
                    content["lastopen"]))
        if len(listByFavorites) > 1:
            # sort by date favorites
            listByFavorites = sorted(listByFavorites,
                key=lambda date: listByFavorites[1])

        if len(listNoneFavorites) > 1:
            #sort by date last used
            listNoneFavorites = sorted(listNoneFavorites,
                key=lambda date: listNoneFavorites[1])

        for recent_project_path in listByFavorites:
            self.append_to_list(recent_project_path[0],
                recent_projects_dict[recent_project_path[0]])

        for recent_project_path in listNoneFavorites:
                self.append_to_list(recent_project_path[0],
                     recent_projects_dict[recent_project_path[0]])

    def append_to_list(self, path, content):
        if file_manager.folder_exists(path):
            item = QListWidgetItem("")
            widget = recent_project_item.RecentProjectItem(path, content, item)
            self.connect(widget, SIGNAL("clicked(QString)"),
                self._open_selected)
            self.connect(widget, SIGNAL("favoriteChange(bool)"),
                self._favorite_changed)
            self.connect(widget, SIGNAL("deleteMe(QListWidgetItem)"),
                self._delete_recent_project_item)
            self.addItem(item)
            self.setItemWidget(item, widget)

    def _favorite_changed(self, value):
        self.load_items()

    def _delete_recent_project_item(self, item):
        self.takeItem(self.row(item))

    def _open_selected(self, path):
        self.browser_referece.open_project(path)


class WebPluginFactory(QWebPluginFactory):

    def __init__(self, parent=None):
        QWebPluginFactory.__init__(self, parent)
        self.browser_reference = parent

    def create(self, mimeType, url, names, values):
        if mimeType == "x-pyqt/widget":
            return WebPluginList(self.browser_reference)

    def plugins(self):
        plugin = QWebPluginFactory.Plugin()
        plugin.name = "PyQt QListWidget"
        plugin.description = "List of Recent Projects"
        mimeType = QWebPluginFactory.MimeType()
        mimeType.name = "x-pyqt/widget"
        mimeType.description = "PyQt QListWidget"
        mimeType.fileExtensions = []
        plugin.mimeTypes = [mimeType]
        return [plugin]
