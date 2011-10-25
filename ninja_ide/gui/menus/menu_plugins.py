# *-* coding: utf-8 *-*
from __future__ import absolute_import

from PyQt4.QtCore import QObject
from PyQt4.QtCore import SIGNAL

from ninja_ide.gui import central_widget
from ninja_ide.gui.dialogs import plugins_manager
from ninja_ide.gui.dialogs import themes_manager


class MenuPlugins(QObject):

    def __init__(self, menuPlugins):
        QObject.__init__(self)

        manageAction = menuPlugins.addAction(self.tr("Manage Plugins"))
        skinsAction = menuPlugins.addAction(self.tr("Editor Schemes"))
        menuPlugins.addSeparator()

        self.connect(manageAction, SIGNAL("triggered()"), self._show_manager)
        self.connect(skinsAction, SIGNAL("triggered()"), self._show_themes)

    def _show_manager(self):
        manager = plugins_manager.PluginsManagerWidget(
            central_widget.CentralWidget())
        manager.show()

    def _show_themes(self):
        manager = themes_manager.ThemesManagerWidget(
            central_widget.CentralWidget())
        manager.show()
