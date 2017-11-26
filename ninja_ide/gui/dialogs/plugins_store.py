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

import collections
import random

from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QColor
from PyQt5.QtQuickWidgets import QQuickWidget
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal

from ninja_ide import translations
from ninja_ide.tools import ui_tools
from ninja_ide.core.encapsulated_env import nenvironment


class PluginsStore(QDialog):
    processCompleted = pyqtSignal('QObject*')
    def __init__(self, parent=None):
        super(PluginsStore, self).__init__(parent, Qt.Popup)#Qt.Tool
        self.setWindowTitle(translations.TR_MANAGE_PLUGINS)
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        #self.setWindowState(Qt.WindowActive)
        self.view = QQuickWidget()
        self.view.setMinimumWidth(800)
        self.view.setMinimumHeight(600)
        self.view.setResizeMode(QQuickWidget.SizeRootObjectToView)
        self.view.setSource(ui_tools.get_qml_resource("PluginsStore.qml"))
        self.root = self.view.rootObject()
        vbox.addWidget(self.view)
        self._plugins = {}
        self._plugins_inflate = []
        self._plugins_by_tag = collections.defaultdict(list)
        self._plugins_by_author = collections.defaultdict(list)
        self._base_color = QColor("white")
        self._counter = 0
        self._counter_callback = None
        self._inflating_plugins = []
        self._categoryTags = True
        self._search = []
        self.status = None

        # QApplication.instance().focusChanged["QWidget*", "QWidget*"].connect(\
        #     lambda w1, w2, this=self: this.hide() if w1 == this.view else None)

        self.root.loadPluginsGrid.connect(self._load_by_name)
        self.root.close.connect(lambda: print("self.close", self.close()))
        self.root.showPluginDetails[int].connect(self.show_plugin_details)
        self.root.loadTagsGrid.connect(self._load_tags_grid)
        self.root.loadAuthorGrid.connect(self._load_author_grid)
        self.root.search[str].connect(self._load_search_results)
        self.root.loadPluginsForCategory[str].connect(self._load_plugins_for_category)
        self.processCompleted.connect(self._process_complete)

        self.nenv = nenvironment.NenvEggSearcher()
        self.nenv.searchCompleted.connect(self.callback)
        self.status = self.nenv.do_search()

    def _load_by_name(self):
        if self._plugins:
            self.root.showGridPlugins()
            for plugin in list(self._plugins.values()):
                self.root.addPlugin(plugin.identifier, plugin.name,
                                    plugin.summary, plugin.version)

    def _load_plugins_for_category(self, name):
        self.root.showGridPlugins()
        if self._categoryTags:
            for plugin in self._plugins_by_tag[name]:
                self.root.addPlugin(plugin.identifier, plugin.name,
                                    plugin.summary, plugin.version)
        else:
            for plugin in self._plugins_by_author[name]:
                self.root.addPlugin(plugin.identifier, plugin.name,
                                    plugin.summary, plugin.version)

    def callback(self, values):
        self.root.showGridPlugins()
        for i, plugin in enumerate(values):
            plugin.identifier = i + 1
            self.root.addPlugin(plugin.identifier, plugin.name,
                                plugin.summary, plugin.version)
            self._plugins[plugin.identifier] = plugin

    def show_plugin_details(self, identifier):
        plugin = self._plugins[identifier]
        self._counter = 1
        self._counter_callback = self._show_details

        if plugin.shallow:
            plugin.pluginMetadataInflated.connect(self._update_content)
            self._plugins_inflate.append(plugin.inflate())
        else:
            self._update_content(plugin)

    def _load_tags_grid(self):
        self._categoryTags = True
        self._counter = len(self._plugins)
        self.root.updateCategoryCounter(self._counter)
        self._counter_callback = self._show_tags_grid
        self._inflating_plugins = list(self._plugins.values())
        self._loading_function()

    def _load_author_grid(self):
        self._categoryTags = False
        self._counter = len(self._plugins)
        self.root.updateCategoryCounter(self._counter)
        self._counter_callback = self._show_author_grid
        self._inflating_plugins = list(self._plugins.values())
        self._loading_function()

    def _load_search_results(self, search):
        self._search = search.lower().split()
        self._counter = len(self._plugins)
        self.root.updateCategoryCounter(self._counter)
        self._counter_callback = self._show_search_grid
        self._inflating_plugins = list(self._plugins.values())
        self._loading_function()

    def _loading_function(self):
        plugin = self._inflating_plugins.pop()
        if plugin.shallow:
            plugin.pluginMetadataInflated.connect(self._update_content)
            self._plugins_inflate.append(plugin.inflate())
        else:
            self._process_complete(plugin)

    def _process_complete(self, plugin=None):
        self._counter -= 1
        self.root.updateCategoryCounter(self._counter)
        if self._counter == 0:
            self._counter_callback(plugin)
        else:
            self._loading_function()

    def _show_search_grid(self, plugin=None):
        self.root.showGridPlugins()
        for plugin in list(self._plugins.values()):
            keywords = plugin.keywords.lower().split() + [plugin.name.lower()]
            for word in self._search:
                if word in keywords:
                    self.root.addPlugin(plugin.identifier, plugin.name,
                                        plugin.summary, plugin.version)

    def _show_details(self, plugin):
        self.root.displayDetails(plugin.identifier)

    def _show_tags_grid(self, plugin=None):
        tags = sorted(self._plugins_by_tag.keys())
        for tag in tags:
            color = self._get_random_color(self._base_color)
            self.root.addCategory(color.name(), tag)
        self.root.loadingComplete()

    def _show_author_grid(self, plugin=None):
        authors = sorted(self._plugins_by_author.keys())
        for author in authors:
            color = self._get_random_color(self._base_color)
            self.root.addCategory(color.name(), author)
        self.root.loadingComplete()

    def _update_content(self, plugin):
        self.root.updatePlugin(
            plugin.identifier, plugin.author, plugin.author_email,
            plugin.description, plugin.download_url, plugin.home_page,
            plugin.license)
        keywords = plugin.keywords.split()
        for key in keywords:
            plugins = self._plugins_by_tag[key]
            if plugin not in plugins:
                plugins.append(plugin)
                self._plugins_by_tag[key] = plugins
        plugins = self._plugins_by_author[plugin.author]
        if plugin not in plugins:
            plugins.append(plugin)
            self._plugins_by_author[plugin.author] = plugins
        self.processCompleted.emit(plugin)

    def _get_random_color(self, mix=None):
        red = random.randint(0, 256)
        green = random.randint(0, 256)
        blue = random.randint(0, 256)

        # mix the color
        if mix:
            red = (red + mix.red()) / 2
            green = (green + mix.green()) / 2
            blue = (blue + mix.blue()) / 2

        color = QColor(red, green, blue)
        return color
