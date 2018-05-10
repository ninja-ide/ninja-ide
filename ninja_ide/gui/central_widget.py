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

from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
)

from PyQt5.QtCore import Qt

from ninja_ide.gui import actions
from ninja_ide.gui import dynamic_splitter
from ninja_ide.gui.ide import IDE
from ninja_ide.tools import ui_tools


class CentralWidget(QWidget):
    """
    splitterCentralRotated()
    """

    def __init__(self, parent=None):
        super(CentralWidget, self).__init__(parent)
        self.parent = parent
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        # This variables are used to save the splitter sizes before hide
        self.lateral_panel = LateralPanel()

        self._add_functions = {
            "central": self._insert_widget_inside,
            "lateral": self._insert_widget_base,
        }
        self._items = {}

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(0)
        # Create Splitters to divide the UI 3 regions
        self._splitter_base = dynamic_splitter.DynamicSplitter(Qt.Horizontal)
        self._splitter_base.setOpaqueResize(True)
        self._splitter_inside = dynamic_splitter.DynamicSplitter(Qt.Vertical)
        self._splitter_inside.setOpaqueResize(True)
        self._splitter_base.addWidget(self._splitter_inside)

        # Add to Main Layout
        hbox.addWidget(self._splitter_base)
        vbox.addLayout(hbox)
        tool = IDE.get_service('tools_dock')
        vbox.addWidget(tool.buttons_widget)
        IDE.register_service('central_container', self)

    def install(self):
        ide = IDE.get_service('ide')
        ui_tools.install_shortcuts(self, actions.ACTIONS_CENTRAL, ide)

        ide.goingDown.connect(self.save_configuration)

    def show_copypaste_history_popup(self):
        self.lateral_panel.combo.showPopup()

    def add_to_region(self, name, obj, region, top=False):
        self._add_functions.get(region, lambda x: None)(obj, top)
        self._items[name] = obj

    def get_item(self, name):
        return self._items.get(name, None)

    def _insert_widget_inside(self, container, top=False):
        self._splitter_inside.add_widget(container, top)

    def _insert_widget_base(self, container, top=False):
        if not self.lateral_panel.has_component:
            self.lateral_panel.add_component(container)
            self._splitter_base.add_widget(self.lateral_panel, top)
        else:
            self._splitter_base.add_widget(container, top)

    def change_lateral_visibility(self):
        if self.lateral_panel.isVisible():
            self.lateral_panel.hide()
        else:
            self.lateral_panel.show()

    def is_lateral_panel_visible(self):
        return self.lateral_panel.isVisible()

    def hide_all(self):
        """ Hide/Show all the containers except the editor """

        # tools_dock = IDE.get_service('tools_dock')
        toolbar = IDE.get_service('toolbar')
        if (self.lateral_panel.isVisible() or toolbar.isVisible()):
            if self.lateral_panel:
                self.lateral_panel.hide()
            if toolbar:
                toolbar.hide()
        else:
            if self.lateral_panel:
                self.lateral_panel.show()
            if toolbar:
                toolbar.show()

    def showEvent(self, event):
        super(CentralWidget, self).showEvent(event)
        # if bin(settings.UI_LAYOUT)[-1] == '1':
        #    self.splitter_base_rotate()
        # if bin(settings.UI_LAYOUT >> 1)[-1] == '1':
        #    self.splitter_inside_rotate()
        # if bin(settings.UI_LAYOUT >> 2)[-1] == '1':
        #    self.splitter_base_orientation()
        # Rearrange widgets on Window
        qsettings = IDE.ninja_settings()
        # Lists of sizes as list of QVariant- heightList = [QVariant, QVariant]
        height_size = qsettings.value(
            "window/central/inside_splitter_size", None)
        width_size = qsettings.value(
            "window/central/base_splitter_size", None)
        lateral_visible = qsettings.value(
            "window/central/lateral_visible", True, type=bool)
        if height_size is None:
            self._splitter_inside.setSizes([(self.height() / 3) * 2,
                                           self.height() / 3])
        else:
            self._splitter_inside.restoreState(height_size)
        if width_size is None:
            self._splitter_base.setSizes([900, 300])
        else:
            self._splitter_base.restoreState(width_size)
        if not lateral_visible:
            self.lateral_panel.hide()

    def splitter_base_rotate(self):
        w1, w2 = self._splitter_base.widget(0), self._splitter_base.widget(1)
        self._splitter_base.insertWidget(0, w2)
        self._splitter_base.insertWidget(1, w1)

    def splitter_base_orientation(self):
        if self._splitter_base.orientation() == Qt.Horizontal:
            self._splitter_base.setOrientation(Qt.Vertical)
        else:
            self._splitter_base.setOrientation(Qt.Horizontal)

    def splitter_inside_rotate(self):
        w1, w2 = self._splitterMain.widget(0), self._splitterMain.widget(1)
        self._splitterMain.insertWidget(0, w2)
        self._splitterMain.insertWidget(1, w1)

    def splitter_inside_orientation(self):
        if self._splitter_inside.orientation() == Qt.Horizontal:
            self._splitter_inside.setOrientation(Qt.Vertical)
        else:
            self._splitter_inside.setOrientation(Qt.Horizontal)

    def save_configuration(self):
        """Save the size of the splitters"""

        qsettings = IDE.ninja_settings()
        qsettings.setValue("window/central/base_splitter_size",
                           self._splitter_base.saveState())
        qsettings.setValue("window/central/inside_splitter_size",
                           self._splitter_inside.saveState())
        qsettings.setValue("window/central/lateral_visible",
                           self.lateral_panel.isVisible())

    def get_paste(self):
        return self.lateral_panel.get_paste()

    def add_copy(self, text):
        self.lateral_panel.add_new_copy(text)


class LateralPanel(QWidget):

    def __init__(self, parent=None):
        super(LateralPanel, self).__init__(parent)
        self.has_component = False
        self.vbox = QVBoxLayout(self)
        self.vbox.setContentsMargins(0, 0, 0, 0)
        self.vbox.setSpacing(0)
        # hbox = QHBoxLayout()
        # hbox.setContentsMargins(0, 0, 0, 0)
        # hbox.setSpacing(0)
        # self.combo = QComboBox()
        # ui_tools.ComboBoxButton(self.combo, self.combo.clear,
        #    self.style().standardPixmap(self.style().SP_TrashIcon))
        # FIXME: translations
        # self.combo.setToolTip("Select the item from the Paste "
        #    "History list.\nYou can Copy items into this list with: "
        #    "%s\nor Paste them using: {}".format(
        #        resources.get_shortcut("History-Copy").toString(
        #            QKeySequence.NativeText),
        #        resources.get_shortcut("History-Paste").toString(
        #            QKeySequence.NativeText)))
        # self.combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        # hbox.addWidget(self.combo)
        # self.vbox.addLayout(hbox)

    def add_component(self, widget):
        self.vbox.insertWidget(0, widget)
        self.has_component = True

    def add_new_copy(self, copy):
        pass
        # self.combo.insertItem(0, copy)
        # self.combo.setCurrentIndex(0)
        # if self.combo.count() > settings.COPY_HISTORY_BUFFER:
        #    self.combo.removeItem(self.combo.count() - 1)

    def get_paste(self):
        pass
        # return self.combo.currentText()


central = CentralWidget()
