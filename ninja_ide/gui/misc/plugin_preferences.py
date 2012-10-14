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
from PyQt4.QtGui import QTabWidget
from PyQt4.QtGui import QVBoxLayout

from ninja_ide.core import plugin_manager

from ninja_ide.tools.logger import NinjaLogger

logger = NinjaLogger('ninja_ide.gui.misc.plugin_preferences')


class PluginPreferences(QWidget):
    """
    Plugins section widget in NINJA-IDE Preferences
    """
    def __init__(self):
        QWidget.__init__(self)
        self.plugin_manager = plugin_manager.PluginManager()
        vbox = QVBoxLayout(self)
        self._tabs = QTabWidget()
        vbox.addWidget(self._tabs)
        #load widgets
        self._load_widgets()

    def _load_widgets(self):
        logger.info("Loading plugins preferences widgets")
        #Collect the preferences widget for each active plugin
        for plugin in self.plugin_manager.get_active_plugins():
            plugin_name = plugin.metadata.get('name')
            try:
                preferences_widget = plugin.get_preferences_widget()
                if preferences_widget:
                    self._tabs.addTab(preferences_widget, plugin_name)
            except Exception as reason:
                logger.error("Unable to add the preferences widget (%s): %s",
                    plugin_name, reason)
                continue

    def save(self):
        logger.info("Saving plugins preferences")
        for i in range(self._tabs.count()):
            try:
                self._tabs.widget(i).save()
            except Exception as reason:
                logger.error("Unable to save preferences (%s): %s",
                    self._tabs.tabText(i), reason)
                continue
