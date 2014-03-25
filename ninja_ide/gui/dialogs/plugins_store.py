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

from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtDeclarative import QDeclarativeView
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL

from ninja_ide import translations
from ninja_ide.tools import ui_tools
from ninja_ide.core.encapsulated_env import nenvironment


class PluginsStore(QDialog):

    def __init__(self, parent=None):
        super(PluginsStore, self).__init__(parent, Qt.Dialog)
        self.setWindowTitle(translations.TR_MANAGE_PLUGINS)
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        self.view = QDeclarativeView()
        self.view.setMinimumWidth(800)
        self.view.setMinimumHeight(600)
        self.view.setResizeMode(QDeclarativeView.SizeRootObjectToView)
        self.view.setSource(ui_tools.get_qml_resource("PluginsStore.qml"))
        self.root = self.view.rootObject()
        vbox.addWidget(self.view)
        self._plugins = {}
        self._plugins_inflate = []

        self.nenv = nenvironment.NenvEggSearcher()
        self.connect(self.nenv, SIGNAL("searchCompleted(PyQt_PyObject)"),
                     self.callback)
        self.connect(self.root, SIGNAL("inflatePlugin(int)"),
                     self._update_plugin_metadata)

        self.status = self.nenv.do_search()

    def callback(self, values):
        self.root.showGrid()
        for i, plugin in enumerate(values):
            plugin.identifier = i + 1
            self.root.addPlugin(plugin.identifier, plugin.name,
                                plugin.summary, plugin.version)
            self._plugins[plugin.identifier] = plugin

    def _update_plugin_metadata(self, identifier):
        pluginShallow = self._plugins[identifier]

        def update_content(plugin):
            self.root.updatePlugin(plugin.identifier, plugin.author)

        self.connect(pluginShallow,
                     SIGNAL("pluginMetadataInflated(PyQt_PyObject)"),
                     update_content)
        self._plugins_inflate.append(pluginShallow.inflate())
