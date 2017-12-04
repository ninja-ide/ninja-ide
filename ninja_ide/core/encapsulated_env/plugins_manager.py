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

from PyQt5.QtCore import QObject

from ninja_ide.gui.ide import IDE


class PluginsManager(QObject):

    def __init__(self):
        super(PluginsManager, self).__init__()

    def get_activated_plugins(self):
        qsettings = IDE.ninja_settings()
        return qsettings.value('plugins/registry/activated', [])

    def get_failstate_plugins(self):
        qsettings = IDE.ninja_settings()
        return qsettings.value('plugins/registry/failure', [])

    def get_to_activate_plugins(self):
        qsettings = IDE.ninja_settings()
        return qsettings.value('plugins/registry/toactivate', [])

    def set_to_activate_plugins(self, to_activate):
        qsettings = IDE.ninja_settings()
        qsettings.setValue('plugins/registry/toactivate', to_activate)

    def set_activated_plugins(self, activated):
        qsettings = IDE.ninja_settings()
        qsettings.setValue('plugins/registry/activated', activated)

    def set_failstate_plugins(self, failure):
        qsettings = IDE.ninja_settings()
        qsettings.setValue('plugins/registry/failure', failure)

    def activate_plugin(self, plugin):
        """
        Receives PluginMetadata instance and activates its given plugin
        BEWARE: We do not do any kind of checking about if the plugin is
        actually installed.
        """
        plugin_name = plugin.name
        to_activate = self.get_to_activate_plugins()
        to_activate.append(plugin_name)
        self.set_to_activate_plugins(to_activate)
        self.__activate_plugin(plugin, plugin_name)

    def load_all_plugins(self):
        to_activate = self.get_to_activate_plugins()
        for each_plugin in to_activate:
            self.__activate_plugin(__import__(each_plugin), each_plugin)

    def __activate_plugin(self, plugin, plugin_name):
        """
        Receives the actual plugin module and tries activate or marks
        as failure
        """
        activated = self.get_activated_plugins()
        failure = self.get_failstate_plugins()

        try:
            plugin.activate()
        except Exception:
            # This plugin can no longer be activated
            if plugin_name in activated:
                activated.remove(plugin_name)
            if plugin_name not in failure:
                failure.append(plugin_name)
        else:
            activated.append(plugin_name)
            if plugin_name in failure:
                failure.remove(plugin_name)
        finally:
            self.set_activated_plugins(activated)
            self.set_failstate_plugins(failure)
