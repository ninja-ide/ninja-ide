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
from PyQt4.QtGui import QKeySequence
from PyQt4.QtGui import QSizePolicy
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QComboBox
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtCore import Qt

from ninja_ide import resources
from ninja_ide.core import settings
from ninja_ide.gui import actions
from ninja_ide.gui import dynamic_splitter
from ninja_ide.gui.ide import IDE
from ninja_ide.tools import ui_tools


class CentralWidget(QWidget):

###############################################################################
# CentralWidget SIGNALS
###############################################################################

    """
    splitterCentralRotated()
    """

###############################################################################

    def __init__(self, parent=None):
        super(CentralWidget, self).__init__(parent)
        self.parent = parent
        #This variables are used to save the splitter sizes before hide
        self.lateralPanel = LateralPanel()

        self._add_functions = {
            "central": self._insert_widget_inside,
            "lateral": self._insert_widget_base,
        }
        self._items = {}

        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(0)
        #Create Splitters to divide the UI 3 regions
        self._splitterBase = dynamic_splitter.DynamicSplitter(Qt.Horizontal)
        self._splitterInside = dynamic_splitter.DynamicSplitter(Qt.Vertical)
        self._splitterBase.addWidget(self._splitterInside)

        #Add to Main Layout
        hbox.addWidget(self._splitterBase)
        IDE.register_service('central_container', self)

    def install(self):
        ide = IDE.get_service('ide')
        ui_tools.install_shortcuts(self, actions.ACTIONS_CENTRAL, ide)

    def show_copypaste_history_popup(self):
        self.lateralPanel.combo.showPopup()

    def add_to_region(self, name, obj, region, top=False):
        self._add_functions.get(region, lambda x: None)(obj, top)
        self._items[name] = obj

    def get_item(self, name):
        return self._items.get(name, None)

    def _insert_widget_inside(self, container, top=False):
        self._splitterInside.add_widget(container, top)

    def _insert_widget_base(self, container, top=False):
        if not self.lateralPanel.has_component:
            self.lateralPanel.add_component(container)
            self._splitterBase.add_widget(self.lateralPanel, top)
        else:
            self._splitterBase.add_widget(container, top)

    def change_lateral_visibility(self):
        if self.lateralPanel.isVisible():
            self.lateralPanel.hide()
        else:
            self.lateralPanel.show()

    def hide_all(self):
        """Hide/Show all the containers except the editor."""
        tools_dock = IDE.get_service('tools_dock')
        toolbar = IDE.get_service('toolbar')
        if (self.lateralPanel.isVisible() or tools_dock.isVisible() or
                toolbar.isVisible()):
            if self.lateralPanel:
                self.lateralPanel.hide()
            if tools_dock:
                tools_dock.hide()
            if toolbar:
                toolbar.hide()
        else:
            if self.lateralPanel:
                self.lateralPanel.show()
            if tools_dock:
                tools_dock.show()
            if toolbar:
                toolbar.show()

    def showEvent(self, event):
        #Show Event
        super(CentralWidget, self).showEvent(event)
        if bin(settings.UI_LAYOUT)[-1] == '1':
            self.splitter_base_rotate()
        if bin(settings.UI_LAYOUT >> 1)[-1] == '1':
            self.splitter_inside_rotate()
        if bin(settings.UI_LAYOUT >> 2)[-1] == '1':
            self.splitter_base_orientation()
        #Rearrange widgets on Window
        qsettings = IDE.ninja_settings()
        #Lists of sizes as list of QVariant- heightList = [QVariant, QVariant]
        heightSize = qsettings.value("window/central/insideSplitterSize", None)
        widthSize = qsettings.value("window/central/baseSplitterSize", None)
        lateralVisible = qsettings.value("window/central/lateralVisible", True,
            type=bool)
        if heightSize is None:
            self._splitterInside.setSizes([(self.height() / 3) * 2,
                                         self.height() / 3])
        else:
            self._splitterInside.restoreState(heightSize)
        if widthSize is None:
            self._splitterBase.setSizes([900, 100])
        else:
            self._splitterBase.restoreState(widthSize)
        if not lateralVisible:
            self.lateralPanel.hide()

    def splitter_base_rotate(self):
        w1, w2 = self._splitterBase.widget(0), self._splitterBase.widget(1)
        self._splitterBase.insertWidget(0, w2)
        self._splitterBase.insertWidget(1, w1)

    def splitter_base_orientation(self):
        if self._splitterBase.orientation() == Qt.Horizontal:
            self._splitterBase.setOrientation(Qt.Vertical)
        else:
            self._splitterBase.setOrientation(Qt.Horizontal)

    def splitter_inside_rotate(self):
        w1, w2 = self._splitterMain.widget(0), self._splitterMain.widget(1)
        self._splitterMain.insertWidget(0, w2)
        self._splitterMain.insertWidget(1, w1)

    def splitter_inside_orientation(self):
        if self._splitterInside.orientation() == Qt.Horizontal:
            self._splitterInside.setOrientation(Qt.Vertical)
        else:
            self._splitterInside.setOrientation(Qt.Horizontal)

    def save_configuration(self):
        qsettings = IDE.ninja_settings()
        #Save the size of de splitters
        qsettings.setValue("window/central/baseSplitterSize",
            self._splitterBase.saveState())
        qsettings.setValue("window/central/insideSplitterSize",
            self._splitterInside.saveState())
        qsettings.setValue("window/central/lateralVisible",
            self.lateralPanel.isVisible())

    def get_paste(self):
        return self.lateralPanel.get_paste()

    def add_copy(self, text):
        self.lateralPanel.add_new_copy(text)


class LateralPanel(QWidget):

    def __init__(self, parent=None):
        super(LateralPanel, self).__init__(parent)
        self.has_component = False
        self.vbox = QVBoxLayout(self)
        self.vbox.setContentsMargins(0, 0, 0, 0)
        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        self.combo = QComboBox()
        ui_tools.ComboBoxButton(self.combo, self.combo.clear,
            self.style().standardPixmap(self.style().SP_TrashIcon))
        self.combo.setToolTip(self.trUtf8("Select the item from the Paste "
            "History list.\nYou can Copy items into this list with: "
            "%s\nor Paste them using: %s") %
                (resources.get_shortcut("History-Copy").toString(
                    QKeySequence.NativeText),
                resources.get_shortcut("History-Paste").toString(
                    QKeySequence.NativeText)))
        self.combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        hbox.addWidget(self.combo)
        self.vbox.addLayout(hbox)

    def add_component(self, widget):
        self.vbox.insertWidget(0, widget)
        self.has_component = True

    def add_new_copy(self, copy):
        self.combo.insertItem(0, copy)
        self.combo.setCurrentIndex(0)
        if self.combo.count() > settings.COPY_HISTORY_BUFFER:
            self.combo.removeItem(self.combo.count() - 1)

    def get_paste(self):
        return self.combo.currentText()


central = CentralWidget()