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

import collections

from PyQt4.QtGui import QSplitter
from PyQt4.QtGui import QTabWidget
from PyQt4.QtGui import QIcon

from ninja_ide.gui.ide import IDE
from ninja_ide.gui.explorer import actions
from ninja_ide.tools import ui_tools

from ninja_ide.tools.logger import NinjaLogger

logger = NinjaLogger('ninja_ide.gui.explorer.explorer_container')


#TODO: Support undock/redock y split

class ExplorerContainer(QSplitter):

###############################################################################
# ExplorerContainer SIGNALS
###############################################################################

    """
    updateLocator()
    goToDefinition(int)
    projectOpened(QString)
    projectClosed(QString)
    """

###############################################################################

    __TABS = []
    __created = False

    def __init__(self, parent=None):
        super(ExplorerContainer, self).__init__(parent)
        self.create_tab_widget()

        IDE.register_service('explorer_container', self)

        connections = (
            {'target': 'central_container',
            'signal_name': "splitterBaseRotated()",
            'slot': self.rotate_tab_position},
            {'target': 'central_container',
            'signal_name': 'splitterBaseRotated()',
            'slot': self.rotate_tab_position},
        )

        IDE.register_signals('explorer_container', connections)
        self.__created = True

    @classmethod
    def register_tab(cls, tab_name, obj, icon=None):
        """Register a tab providing the service name and the instance."""
        cls.__TABS.append((tab_name, obj, icon))
        if cls.__created:
            explorer.add_tab(tab_name, obj, icon)

    def install(self):
        ide = IDE.get_service('ide')
        ide.place_me_on("explorer_container", self, "lateral")

        for tabname, obj, icon in self.__TABS:
            self.add_tab(tabname, obj, icon)

        if self.count() == 0:
            self.hide()
        ui_tools.install_shortcuts(self, actions.ACTIONS, ide)

    def create_tab_widget(self):
        tab_widget = QTabWidget()
        tab_widget.setTabPosition(QTabWidget.East)
        tab_widget.setMovable(True)
        self.addWidget(tab_widget)

    def add_tab(self, tabname, obj, icon=None):
        if icon is not None:
            self.widget(0).addTab(obj, QIcon(icon), tabname)
        else:
            self.widget(0).addTab(obj, tabname)
        func = getattr(obj, 'install_tab', None)
        if isinstance(func, collections.Callable):
            func()

    def change_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()

    def rotate_tab_position(self):
        for i in range(self.count()):
            widget = self.widget(i)
            if widget.tabPosition() == QTabWidget.East:
                widget.setTabPosition(QTabWidget.West)
            else:
                widget.setTabPosition(QTabWidget.East)

    def shortcut_index(self, index):
        self.setCurrentIndex(index)


explorer = ExplorerContainer()