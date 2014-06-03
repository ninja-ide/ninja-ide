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
from PyQt4.QtGui import QMenu
from PyQt4.QtGui import QTabWidget
from PyQt4.QtGui import QIcon
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import Qt

from ninja_ide import translations
from ninja_ide.gui.ide import IDE

from ninja_ide.tools.logger import NinjaLogger

logger = NinjaLogger('ninja_ide.gui.explorer.explorer_container')


#TODO: Support undock/redock y split
#TODO: Each tab should handle close and reopen and notify the explorer

class ExplorerContainer(QSplitter):

###############################################################################
# ExplorerContainer SIGNALS
###############################################################################

    """
    goToDefinition(int)
    projectOpened(QString)
    projectClosed(QString)
    """

###############################################################################

    __TABS = collections.OrderedDict()
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

        self._point = None
        self.menu = QMenu()
        actionUndock = self.menu.addAction(translations.TR_UNDOCK)
        self.connect(actionUndock, SIGNAL("activated()"), self._undock_widget)

        IDE.register_signals('explorer_container', connections)
        self.__created = True

    @classmethod
    def register_tab(cls, tab_name, obj, icon=None):
        """Register a tab providing the service name and the instance."""
        cls.__TABS[obj] = (tab_name, icon)
        if cls.__created:
            explorer.add_tab(tab_name, obj, icon)

    def install(self):
        ide = IDE.get_service('ide')
        ide.place_me_on("explorer_container", self, "lateral")

        for obj in ExplorerContainer.__TABS:
            tabname, icon = ExplorerContainer.__TABS[obj]
            self.add_tab(tabname, obj, icon)
            self.connect(obj, SIGNAL("dockWidget(PyQt_PyObject)"),
                         self._dock_widget)
            self.connect(obj, SIGNAL("undockWidget()"),
                         self._undock_widget)
            self.connect(obj, SIGNAL("changeTitle(PyQt_PyObject, QString)"),
                         self._change_tab_title)

        if self.count() == 0:
            self.hide()

    def _dock_widget(self, widget):
        tab_widget = self.widget(0)
        if tab_widget.count() == 0:
            central = IDE.get_service('central_container')
            central.change_lateral_visibility()
        tabname, icon = ExplorerContainer.__TABS[widget]
        self.add_tab(tabname, widget, icon)

    def _change_tab_title(self, widget, title):
        tab_widget = self.widget(0)
        index = tab_widget.indexOf(widget)
        data = ExplorerContainer.__TABS[widget]
        data = tuple([title] + list(data[1:]))
        ExplorerContainer.__TABS[widget] = data
        tab_widget.setTabText(index, title)

    def _undock_widget(self):
        bar = self.widget(0).tabBar()
        index = bar.tabAt(self._point)
        tab_widget = self.widget(0)
        widget = tab_widget.widget(index)
        widget.setParent(None)
        widget.resize(500, 500)
        widget.show()

        if tab_widget.count() == 0:
            central = IDE.get_service('central_container')
            central.change_lateral_visibility()

    def create_tab_widget(self):
        tab_widget = QTabWidget()
        tab_widget.setTabPosition(QTabWidget.East)
        tab_widget.setMovable(True)
        tabBar = tab_widget.tabBar()
        tabBar.hide()
        tabBar.setContextMenuPolicy(Qt.CustomContextMenu)
        self.connect(
            tabBar,
            SIGNAL("customContextMenuRequested(const QPoint&)"),
            self.show_tab_context_menu)
        self.addWidget(tab_widget)

    def add_tab(self, tabname, obj, icon=None):
        obj.setWindowTitle(tabname)
        if icon is not None:
            qicon = QIcon(icon)
            self.widget(0).addTab(obj, qicon, tabname)
            obj.setWindowIcon(qicon)
        else:
            self.widget(0).addTab(obj, tabname)
        func = getattr(obj, 'install_tab', None)
        if isinstance(func, collections.Callable):
            func()

    def rotate_tab_position(self):
        for i in range(self.count()):
            widget = self.widget(i)
            if widget.tabPosition() == QTabWidget.East:
                widget.setTabPosition(QTabWidget.West)
            else:
                widget.setTabPosition(QTabWidget.East)

    def shortcut_index(self, index):
        self.setCurrentIndex(index)

    def show_tab_context_menu(self, point):
        bar = self.widget(0).tabBar()
        self._point = point
        self.menu.exec_(bar.mapToGlobal(point))

    def enterEvent(self, event):
        super(ExplorerContainer, self).enterEvent(event)
        bar = self.widget(0).tabBar()
        bar.show()

    def leaveEvent(self, event):
        super(ExplorerContainer, self).leaveEvent(event)
        bar = self.widget(0).tabBar()
        bar.hide()


explorer = ExplorerContainer()