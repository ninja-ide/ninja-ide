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
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QSettings

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
        self._splitterBaseSizes = None
        self._splitterInsideSizes = None
        self.lateralPanel = LateralPanel()

        self._add_functions = {
            "central": self._insert_widget_region0,
            "lateral": self._insert_widget_region1,
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
        connects = (
            {"target": "main_container",
            "signal_name": "cursorPositionChange(int, int)",
            "slot": self.update_column_number},
        )
        IDE.register_service('central_container', self)
        IDE.register_signals("central_container", connects)

    def install(self):
        ide = IDE.get_service('ide')
        ui_tools.install_shortcuts(self, actions.ACTIONS_CENTRAL, ide)

    def show_copypaste_history_popup(self):
        self.lateralPanel.combo.showPopup()

    def update_column_number(self, row, col):
        self.lateralPanel.update_line_col(row, col)

    def add_to_region(self, name, obj, region, top=False):
        self._add_functions.get(region, lambda x: None)(obj, top)
        self._items[name] = obj

    def get_item(self, name):
        return self._items.get(name, None)

    def _insert_widget_region0(self, container, top=False):
        self._splitterInside.add_widget(container, top)

    def _insert_widget_region1(self, container, top=False):
        if not self.lateralPanel.has_component:
            self.lateralPanel.add_component(container)
            self._splitterBase.add_widget(self.lateralPanel, top)
        else:
            self._splitterBase.add_widget(container, top)

    def hide_all(self):
        """Hide/Show all the containers except the editor."""
        menu_bar = IDE.get_service('menu_bar')
        tools_dock = IDE.get_service('tools_dock')
        toolbar = IDE.get_service('toolbar')
        if menu_bar and menu_bar.isVisible():
            if self.lateralPanel:
                self.lateralPanel.hide()
            if tools_dock:
                tools_dock.hide()
            if toolbar:
                toolbar.hide()
            if menu_bar:
                menu_bar.hide()
        else:
            if self.lateralPanel:
                self.lateralPanel.show()
            if toolbar:
                toolbar.show()
            if menu_bar:
                menu_bar.show()

    def showEvent(self, event):
        #Show Event
        super(CentralWidget, self).showEvent(event)
        #Avoid recalculate the panel sizes if they are already loaded
        if self._splitterBase.count() == 2:
            return
        if not event.spontaneous():
            self.change_region1_visibility()
        if bin(settings.UI_LAYOUT)[-1] == '1':
            self.splitter_base_rotate()
        if bin(settings.UI_LAYOUT >> 1)[-1] == '1':
            self.splitter_region1_rotate()
        if bin(settings.UI_LAYOUT >> 2)[-1] == '1':
            self.splitter_base_orientation()
        #Rearrange widgets on Window
        qsettings = QSettings(resources.SETTINGS_PATH, QSettings.IniFormat)
        #Lists of sizes as list of QVariant- heightList = [QVariant, QVariant]
        heightList = list(qsettings.value("window/central/insideSize",
            [(self.height() / 3) * 2, self.height() / 3]))
        widthList = list(qsettings.value("window/central/baseSize",
            [(self.width() / 6) * 5, self.width() / 6]))
        self._splitterInsideSizes = [int(heightList[0]), int(heightList[1])]
        self._splitterBaseSizes = [int(widthList[0]), int(widthList[1])]
        #Set the sizes to splitters
        self._splitterInside.setSizes(self._splitterInsideSizes)
        self._splitterBase.setSizes(self._splitterBaseSizes)
        self.tool.setVisible(
            qsettings.value("window/show_region1", False, type=bool))

    #def splitter_base_rotate(self):
        #w1, w2 = self._splitterBase.widget(0), self._splitterBase.widget(1)
        #self._splitterBase.insertWidget(0, w2)
        #self._splitterBase.insertWidget(1, w1)
        #self.emit(SIGNAL("splitterBaseRotated()"))

    #def splitter_base_orientation(self):
        #if self._splitterBase.orientation() == Qt.Horizontal:
            #self._splitterBase.setOrientation(Qt.Vertical)
        #else:
            #self._splitterBase.setOrientation(Qt.Horizontal)

    #def splitter_inside_rotate(self):
        #w1, w2 = self._splitterMain.widget(0), self._splitterMain.widget(1)
        #self._splitterMain.insertWidget(0, w2)
        #self._splitterMain.insertWidget(1, w1)

    #def splitter_inside_orientation(self):
        #if self._splitterInside.orientation() == Qt.Horizontal:
            #self._splitterInside.setOrientation(Qt.Vertical)
        #else:
            #self._splitterInside.setOrientation(Qt.Horizontal)

    def get_area_sizes(self):
        if self.lateralPanel and self.lateralPanel.isVisible():
            self._splitterBaseSizes = self._splitterBase.sizes()
        return self._splitterBaseSizes

    def get_inside_sizes(self):
        region1 = self._splitterInside.widget(1)
        if region1.isVisible():
            self._splitterInsideSizes = self._splitterInside.sizes()
        return self._splitterInsideSizes


class LateralPanel(QWidget):

    def __init__(self, parent=None):
        super(LateralPanel, self).__init__(parent)
        self.has_component = False
        self.vbox = QVBoxLayout(self)
        self.vbox.setContentsMargins(0, 0, 0, 0)
        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        self.labelText = "Ln: %s, Col: %s"
        self.labelCursorPosition = QLabel(self.trUtf8(self.labelText % (0, 0)))
        hbox.addWidget(self.labelCursorPosition)
        self.combo = QComboBox()
        ui_tools.ComboBoxButton(self.combo, self.combo.clear,
            self.style().standardPixmap(self.style().SP_TrashIcon))
        self.combo.setToolTip(self.trUtf8("Select the item from the Paste "
            "Historial list.\nYou can Copy items into this list with: "
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

    def update_line_col(self, line, col):
        self.labelCursorPosition.setText(self.trUtf8(
            self.labelText % (line, col)))

    def add_new_copy(self, copy):
        self.combo.insertItem(0, copy)
        self.combo.setCurrentIndex(0)
        if self.combo.count() > settings.COPY_HISTORY_BUFFER:
            self.combo.removeItem(self.combo.count() - 1)

    def get_paste(self):
        return self.combo.currentText()


central = CentralWidget()