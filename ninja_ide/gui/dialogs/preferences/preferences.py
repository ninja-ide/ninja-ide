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
    QDialog,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
    QTreeWidget,
    QScrollArea,
    QTreeWidgetItem,
    QLabel,
    QHeaderView,
    QStackedLayout,
    QDialogButtonBox
)
from PyQt5.QtCore import (
    Qt,
    pyqtSignal,
    pyqtSlot
)
from ninja_ide import translations


SECTIONS = {
    'GENERAL': 0,
    'EDITOR': 2
}


class Preferences(QDialog):

    configuration = {}
    weight = 0
    # Signals
    savePreferences = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent, Qt.Dialog)
        self.setWindowTitle(translations.TR_PREFERENCES_TITLE)
        self.setMinimumSize(900, 650)
        box = QVBoxLayout(self)
        box.setContentsMargins(3, 3, 3, 3)
        self.setAutoFillBackground(True)
        # Header
        self._header_label = QLabel("")
        header_font = self._header_label.font()
        header_font.setBold(True)
        header_font.setPointSize(header_font.pointSize() + 4)
        self._header_label.setFont(header_font)

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)

        self.tree = QTreeWidget()
        self.tree.header().setHidden(True)
        self.tree.setSelectionMode(QTreeWidget.SingleSelection)
        self.tree.setAnimated(True)
        self.tree.header().setSectionResizeMode(
            0, QHeaderView.ResizeToContents)
        self.tree.setFixedWidth(200)
        hbox.addWidget(self.tree)

        self.stacked = QStackedLayout()
        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.addWidget(self._header_label)
        header_layout.addLayout(self.stacked)
        hbox.addLayout(header_layout)
        box.addLayout(hbox)

        # Footer buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        box.addWidget(button_box)

        # Connections
        button_box.rejected.connect(self.close)
        button_box.accepted.connect(self._save_preferences)
        self.tree.selectionModel().currentRowChanged.connect(
            self._change_current)

        self.load_ui()

    @pyqtSlot()
    def _save_preferences(self):
        self.savePreferences.emit()
        self.close()

    def load_ui(self):
        sections = sorted(
            Preferences.configuration.keys(),
            key=lambda item: Preferences.configuration[item]['weight'])
        for section in sections:
            text = Preferences.configuration[section]['text']
            Widget = Preferences.configuration[section]['widget']
            widget = Widget(self)
            area = QScrollArea()
            area.setWidgetResizable(True)
            area.setWidget(widget)
            self.stacked.addWidget(area)
            index = self.stacked.indexOf(area)
            item = QTreeWidgetItem([text])
            item.setData(0, Qt.UserRole, index)
            self.tree.addTopLevelItem(item)

            # Sort Item Children
            subcontent = Preferences.configuration[section].get(
                'subsections', {})
            subsections = sorted(
                subcontent.keys(), key=lambda item: subcontent[item]['weight'])
            for sub in subsections:
                text = subcontent[sub]['text']
                Widget = subcontent[sub]['widget']
                widget = Widget(self)
                area = QScrollArea()
                area.setWidgetResizable(True)
                area.setWidget(widget)
                self.stacked.addWidget(area)
                index = self.stacked.indexOf(area)
                subitem = QTreeWidgetItem([text])
                subitem.setData(0, Qt.UserRole, index)
                item.addChild(subitem)

        self.tree.expandAll()
        self.tree.setCurrentIndex(self.tree.model().index(0, 0))

    def _change_current(self):
        item = self.tree.currentItem()
        index = item.data(0, Qt.UserRole)
        self.stacked.setCurrentIndex(index)
        self._header_label.setText(item.text(0))

    @classmethod
    def register_configuration(cls, section, widget, text,
                               weight=None, subsection=None):
        if weight is None:
            Preferences.weight += 1
            weight = Preferences.weight
        if subsection is None:
            Preferences.configuration[section] = {
                'widget': widget,
                'weight': weight,
                'text': text
            }
        else:
            config = Preferences.configuration.get(section, {})
            if not config:
                config[section] = {
                    'widget': None,
                    'weight': 100
                }
            subconfig = config.get('subsections', {})
            subconfig[subsection] = {
                'widget': widget,
                'weight': weight,
                'text': text
            }
            config['subsections'] = subconfig
            Preferences.configuration[section] = config

"""
from __future__ import absolute_import
from __future__ import unicode_literals

from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QTreeWidget
from PyQt4.QtGui import QTreeWidgetItem
from PyQt4.QtGui import QStackedLayout
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QScrollArea
from PyQt4.QtGui import QAbstractItemView
from PyQt4.QtGui import QHeaderView
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QSpacerItem
from PyQt4.QtGui import QSizePolicy
from PyQt4.QtCore import QSize
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL

from ninja_ide import translations


SECTIONS = {
    'GENERAL': 0,
    'INTERFACE': 1,
    'EDITOR': 2,
    'PLUGINS': 3,
    'THEME': 4,
}


class Preferences(QDialog):

    configuration = {}
    weight = 0

    def __init__(self, parent=None):
        super(Preferences, self).__init__(parent, Qt.Dialog)
        self.setWindowTitle(translations.TR_PREFERENCES_TITLE)
        self.setMinimumSize(QSize(900, 600))
        vbox = QVBoxLayout(self)
        hbox = QHBoxLayout()
        vbox.setContentsMargins(0, 0, 5, 5)
        hbox.setContentsMargins(0, 0, 0, 0)

        self.tree = QTreeWidget()
        self.tree.header().setHidden(True)
        self.tree.setSelectionMode(QTreeWidget.SingleSelection)
        self.tree.setAnimated(True)
        self.tree.header().setHorizontalScrollMode(
            QAbstractItemView.ScrollPerPixel)
        self.tree.header().setResizeMode(0, QHeaderView.ResizeToContents)
        self.tree.header().setStretchLastSection(False)
        self.tree.setFixedWidth(200)
        self.stacked = QStackedLayout()
        hbox.addWidget(self.tree)
        hbox.addLayout(self.stacked)
        vbox.addLayout(hbox)

        hbox_footer = QHBoxLayout()
        self._btnSave = QPushButton(translations.TR_SAVE)
        self._btnCancel = QPushButton(translations.TR_CANCEL)
        hbox_footer.addSpacerItem(QSpacerItem(1, 0, QSizePolicy.Expanding))
        hbox_footer.addWidget(self._btnCancel)
        hbox_footer.addWidget(self._btnSave)
        vbox.addLayout(hbox_footer)

        self.connect(self.tree, SIGNAL("itemSelectionChanged()"),
                     self._change_current)
        self.connect(self._btnCancel, SIGNAL("clicked()"), self.close)
        self.connect(self._btnSave, SIGNAL("clicked()"),
                     self._save_preferences)

        self.load_ui()
        self.tree.setCurrentItem(self.tree.topLevelItem(0))

    def _save_preferences(self):
        self.emit(SIGNAL("savePreferences()"))
        self.close()

    def load_ui(self):
        sections = sorted(
            list(Preferences.configuration.keys()),
            key=lambda item: Preferences.configuration[item]['weight'])
        for section in sections:
            text = Preferences.configuration[section]['text']
            Widget = Preferences.configuration[section]['widget']
            widget = Widget(self)
            area = QScrollArea()
            area.setWidgetResizable(True)
            area.setWidget(widget)
            self.stacked.addWidget(area)
            index = self.stacked.indexOf(area)
            item = QTreeWidgetItem([text])
            item.setData(0, Qt.UserRole, index)
            self.tree.addTopLevelItem(item)

            #Sort Item Children
            subcontent = Preferences.configuration[section].get(
                'subsections', {})
            subsections = sorted(list(subcontent.keys()),
                                 key=lambda item: subcontent[item]['weight'])
            for sub in subsections:
                text = subcontent[sub]['text']
                Widget = subcontent[sub]['widget']
                widget = Widget(self)
                area = QScrollArea()
                area.setWidgetResizable(True)
                area.setWidget(widget)
                self.stacked.addWidget(area)
                index = self.stacked.indexOf(area)
                subitem = QTreeWidgetItem([text])
                subitem.setData(0, Qt.UserRole, index)
                item.addChild(subitem)

        self.tree.expandAll()

    def _change_current(self):
        item = self.tree.currentItem()
        index = item.data(0, Qt.UserRole)
        self.stacked.setCurrentIndex(index)

    @classmethod
    def register_configuration(cls, section, widget, text, weight=None,
                               subsection=None):
        if weight is None:
            Preferences.weight += 1
            weight = Preferences.weight
        if not subsection:
            Preferences.configuration[section] = {'widget': widget,
                                                  'weight': weight,
                                                  'text': text}
        else:
            config = Preferences.configuration.get(section, {})
            if not config:
                config[section] = {'widget': None, 'weight': 100}
            subconfig = config.get('subsections', {})
            subconfig[subsection] = {'widget': widget, 'weight': weight,
                                     'text': text}
            config['subsections'] = subconfig
            Preferences.configuration[section] = config
"""
