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
from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QSizePolicy
from PyQt4.QtGui import QSpacerItem
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QListWidget
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QHBoxLayout

from ninja_ide.core import file_manager
from ninja_ide.gui.main_panel import itab_item


class TabGroup(QWidget, itab_item.ITabItem):

    def __init__(self, project, name, actions):
        QWidget.__init__(self)
        itab_item.ITabItem.__init__(self)
        vbox = QVBoxLayout(self)
        self.actions = actions
        self.project = project
        self.ID = self.project
        self.name = name
        self.tabs = []
        self.listWidget = QListWidget()
        hbox = QHBoxLayout()
        btnExpand = QPushButton(self.tr("Expand this Files"))
        btnExpandAll = QPushButton(self.tr("Expand all Groups"))
        hbox.addWidget(btnExpandAll)
        hbox.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding))
        hbox.addWidget(btnExpand)
        vbox.addLayout(hbox)
        vbox.addWidget(self.listWidget)

        self.connect(btnExpand, SIGNAL("clicked()"), self.expand_this)
        self.connect(btnExpandAll, SIGNAL("clicked()"),
            self.actions.deactivate_tabs_groups)

    def add_widget(self, widget):
        self.tabs.append(widget)
        self.listWidget.addItem(widget.ID)

    def expand_this(self):
        self.actions.group_tabs_together()
        for tab in self.tabs:
            tabName = file_manager.get_basename(tab.ID)
            self.actions.ide.mainContainer.add_tab(tab, tabName)
        index = self.actions.ide.mainContainer._tabMain.indexOf(self)
        self.actions.ide.mainContainer._tabMain.removeTab(index)
        self.tabs = []
        self.listWidget.clear()

    def only_expand(self):
        for tab in self.tabs:
            tabName = file_manager.get_basename(tab.ID)
            self.actions.ide.mainContainer.add_tab(tab, tabName)
        index = self.actions.ide.mainContainer._tabMain.indexOf(self)
        self.actions.ide.mainContainer._tabMain.removeTab(index)
        self.tabs = []
        self.listWidget.clear()
