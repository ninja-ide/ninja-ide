# -*- coding: utf-8 -*-
from __future__ import absolute_import

import sys
import os
import time

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QListWidget
from PyQt4.QtGui import QListWidgetItem
from PyQt4.QtCore import QUrl
from PyQt4.QtCore import QString
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
from ninja_ide.tools import styles


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
            self.webFrame.reload()

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

    def start_page_operations(self, url):
        opt = file_manager.get_basename(unicode(url.toString()))
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
        styles.set_style(self, 'recent-project')
        self.load_items()

    def load_items(self):
        self.clear()
        settings = QSettings()
        listByFavorites = []
        listNoneFavorites = []
        recent_projects_dict = settings.value(
                  'recentProjects', {}).toMap()
        #Filter for favorites
        for recent_project_path, content in recent_projects_dict.iteritems():
            if content.toMap()[QString("isFavorite")].toBool():
                listByFavorites.append((recent_project_path,
                    content.toMap()[QString("lastopen")].toDateTime()))
            else:
                listNoneFavorites.append((recent_project_path,
                    content.toMap()[QString("lastopen")].toDateTime()))
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
        if file_manager.folder_exists(unicode(path)):
            item = QListWidgetItem("")
            widget = recent_project_item.RecentProjectItem(path, content, item)
            self.connect(widget, SIGNAL(" clicked (QString)"),
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
