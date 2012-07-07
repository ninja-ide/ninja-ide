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

from PyQt4.QtCore import QObject
from PyQt4.QtCore import SIGNAL

from ninja_ide.gui import central_widget
from ninja_ide.gui.dialogs import plugins_manager
from ninja_ide.gui.dialogs import themes_manager
from ninja_ide.gui.dialogs import language_manager


class MenuPlugins(QObject):

    def __init__(self, menuPlugins):
        QObject.__init__(self)

        manageAction = menuPlugins.addAction(self.tr("Manage Plugins"))
        skinsAction = menuPlugins.addAction(self.tr("Editor Schemes"))
        languagesAction = menuPlugins.addAction(self.tr("Languages Manager"))
        menuPlugins.addSeparator()

        self.connect(manageAction, SIGNAL("triggered()"), self._show_manager)
        self.connect(skinsAction, SIGNAL("triggered()"), self._show_themes)
        self.connect(languagesAction, SIGNAL("triggered()"),
            self._show_languages)

    def _show_manager(self):
        manager = plugins_manager.PluginsManagerWidget(
            central_widget.CentralWidget())
        manager.exec_()
        if manager._requirements:
            d = plugins_manager.DependenciesHelpDialog(manager._requirements)
            d.exec_()

    def _show_languages(self):
        manager = language_manager.LanguagesManagerWidget(
            central_widget.CentralWidget())
        manager.show()

    def _show_themes(self):
        manager = themes_manager.ThemesManagerWidget(
            central_widget.CentralWidget())
        manager.show()
