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
from functools import partial
from PyQt5.QtWidgets import (
    # QSplitter,
    QMenu,
    QTabWidget
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from ninja_ide import translations
from ninja_ide.gui.ide import IDE
from ninja_ide.gui import dynamic_splitter
from ninja_ide.tools.logger import NinjaLogger

logger = NinjaLogger('ninja_ide.gui.explorer.explorer_container')


# TODO: Each tab should handle close and reopen and notify the explorer

class ExplorerContainer(dynamic_splitter.DynamicSplitter):

    # ExplorerContainer SIGNALS

    """
    goToDefinition(int)
    projectOpened(QString)
    projectClosed(QString)
    """

    __TABS = collections.OrderedDict()
    __created = False

    def __init__(self, orientation=Qt.Vertical):
        super(ExplorerContainer, self).__init__(orientation)
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
        self._widget_index = 0
        self.__splitted_tabs = {}
        self.menu = QMenu()
        action_split = self.menu.addAction(translations.TR_SPLIT_TAB)
        action_split.triggered.connect(self._split_widget)
        self.action_undock = self.menu.addAction(translations.TR_UNDOCK)
        self.action_undock.triggered.connect(self._undock_widget)
        self.actionCloseSplit = self.menu.addAction(
            translations.TR_CLOSE_SPLIT)
        self.actionCloseSplit.triggered.connect(self._close_split)
        self.menu_move_to_split = self.menu.addMenu(
            translations.TR_MOVE_TO_SPLIT)

        IDE.register_signals('explorer_container', connections)
        self.__created = True

    @classmethod
    def register_tab(cls, tab_name, obj, icon=None):
        """ Register a tab providing the service name and the instance """

        cls.__TABS[obj] = (tab_name, icon)
        if cls.__created:
            explorer.add_tab(tab_name, obj, icon)

    def install(self):
        ide = IDE.get_service('ide')
        ide.place_me_on("explorer_container", self, "lateral")
        ide.goingDown.connect(self.save_configuration)

        for obj in ExplorerContainer.__TABS:
            tabname, icon = ExplorerContainer.__TABS[obj]
            self.add_tab(tabname, obj, icon)
            obj.dockWidget['PyQt_PyObject'].connect(self._dock_widget)
            obj.undockWidget.connect(self._undock_widget)
            if hasattr(obj, "changeTitle"):
                obj.changeTitle.connect(self._change_tab_title)

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
        for i in range(self.count()):
            tab_widget = self.widget(i)
            index = tab_widget.indexOf(widget)
            if index != -1:
                data = ExplorerContainer.__TABS[widget]
                data = tuple([title] + list(data[1:]))
                ExplorerContainer.__TABS[widget] = data
                tab_widget.setTabText(index, title)
                break

    def _undock_widget(self):
        tab_widget = self.widget(self._widget_index)
        bar = tab_widget.tabBar()
        index = bar.tabAt(self._point)
        widget = tab_widget.widget(index)
        widget.setParent(None)
        widget.resize(500, 500)
        widget.show()

        if tab_widget.count() == 0:
            central = IDE.get_service('central_container')
            central.change_lateral_visibility()

    def _split_widget(self):
        current_tab_widget = self.widget(self._widget_index)
        if current_tab_widget.count() == 1:
            return
        tab_widget = self.create_tab_widget()
        index_widget = self.indexOf(tab_widget)
        tab_widget = self.widget(self._widget_index)
        bar = tab_widget.tabBar()
        index = bar.tabAt(self._point)
        widget = tab_widget.widget(index)

        tabname, icon = ExplorerContainer.__TABS[widget]
        self.add_tab(tabname, widget, icon, index_widget)
        self._reset_size()

    def _close_split(self):
        self._move_to_split(0)

    def _move_to_split(self, index_widget=-1):
        obj = self.sender()
        if index_widget == -1:
            index_widget = int(obj.text()) - 1

        tab_widget = self.widget(self._widget_index)
        bar = tab_widget.tabBar()
        index = bar.tabAt(self._point)
        widget = tab_widget.widget(index)
        tabname, icon = ExplorerContainer.__TABS[widget]
        self.add_tab(tabname, widget, icon, index_widget)

        if tab_widget.count() == 0:
            tab_widget.deleteLater()

        self._reset_size()

    def _reset_size(self):
        sizes = [self.height() / self.count()] * self.count()
        self.setSizes(sizes)

    def create_tab_widget(self):
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("QTabWidget::pane {border: 0;}")
        tab_widget.setTabPosition(QTabWidget.East)
        tab_widget.setMovable(True)
        tab_widget.setDocumentMode(True)
        tabBar = tab_widget.tabBar()
        tabBar.hide()
        tabBar.setContextMenuPolicy(Qt.CustomContextMenu)
        self.addWidget(tab_widget)
        index = self.indexOf(tab_widget)
        tabBar.customContextMenuRequested['const QPoint&'].connect(
            lambda point: self.show_tab_context_menu(index, point))
        return tab_widget

    def add_tab(self, tabname, obj, icon=None, widget_index=0):
        obj.setWindowTitle(tabname)
        if icon is not None:
            qicon = QIcon(icon)
            self.widget(widget_index).addTab(obj, qicon, tabname)
            obj.setWindowIcon(qicon)
        else:
            self.widget(widget_index).addTab(obj, tabname)
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

    def show_tab_context_menu(self, widget_index, point):
        bar = self.widget(widget_index).tabBar()
        self._point = point
        self._widget_index = widget_index
        if widget_index != 0:
            self.action_undock.setVisible(False)
            self.actionCloseSplit.setVisible(True)
        else:
            self.action_undock.setVisible(True)
            self.actionCloseSplit.setVisible(False)

        self.menu_move_to_split.clear()
        has_split = self.count() > 1
        if has_split:
            for i in range(1, self.count() + 1):
                action = self.menu_move_to_split.addAction("%d" % i)
                action.triggered.connect(partial(self._move_to_split, -1))
        self.menu_move_to_split.setEnabled(has_split)
        self.menu.exec_(bar.mapToGlobal(point))

    def enterEvent(self, event):
        super(ExplorerContainer, self).enterEvent(event)
        for index in range(self.count()):
            bar = self.widget(index).tabBar()
            bar.show()

    def leaveEvent(self, event):
        super(ExplorerContainer, self).leaveEvent(event)
        for index in range(self.count()):
            bar = self.widget(index).tabBar()
            bar.hide()

    def save_configuration(self):

        # ninja_settings = IDE.ninja_settings()
        # ninja_settings.setValue("explorer/tabs", self.__splitted_tabs)
        pass


explorer = ExplorerContainer()
