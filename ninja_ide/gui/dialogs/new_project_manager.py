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

from PyQt4.QtGui import (
    QDialog,
    QVBoxLayout,
    QListWidget,
    QListWidgetItem,
    QHBoxLayout,
    QLabel,
    QTextBrowser,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
)
from PyQt4.QtCore import (
    Qt,
    SIGNAL,
)

from ninja_ide import translations
from ninja_ide.gui.ide import IDE


class NewProjectManager(QDialog):

    def __init__(self, parent=None):
        super(NewProjectManager, self).__init__(parent, Qt.Dialog)
        self.setWindowTitle(translations.TR_NEW_PROJECT)
        self.setMinimumHeight(500)
        vbox = QVBoxLayout(self)
        vbox.addWidget(QLabel(translations.TR_CHOOSE_TEMPLATE))
        vbox.addWidget(QLabel(translations.TR_TAB_PROJECTS))

        hbox = QHBoxLayout()
        self.list_projects = QListWidget()
        self.list_projects.setProperty("wizard", True)
        hbox.addWidget(self.list_projects)

        self.list_templates = QListWidget()
        self.list_templates.setProperty("wizard", True)
        hbox.addWidget(self.list_templates)

        self.text_info = QTextBrowser()
        self.text_info.setProperty("wizard", True)
        hbox.addWidget(self.text_info)

        vbox.addLayout(hbox)

        hbox2 = QHBoxLayout()
        cancel = QPushButton(translations.TR_CANCEL)
        choose = QPushButton(translations.TR_CHOOSE)
        hbox2.addSpacerItem(QSpacerItem(1, 0, QSizePolicy.Expanding,
                            QSizePolicy.Fixed))
        hbox2.addWidget(cancel)
        hbox2.addWidget(choose)
        vbox.addLayout(hbox2)

        self.template_registry = IDE.get_service("template_registry")
        categories = self.template_registry.list_project_categories()
        for category in categories:
            self.list_projects.addItem(category)

        self.connect(cancel, SIGNAL("clicked()"), self.close)
        self.connect(choose, SIGNAL("clicked()"), self._start_wizard)
        self.connect(self.list_projects,
                     SIGNAL("itemSelectionChanged()"),
                     self._project_selected)
        self.connect(self.list_templates,
                     SIGNAL("itemSelectionChanged()"),
                     self._template_selected)

    def _project_selected(self):
        self.list_templates.clear()
        item = self.list_projects.currentItem()
        category = item.text()
        for template in self.template_registry.list_templates_for_cateogory(
                category):
            item = QListWidgetItem(template.type_name)
            item.setData(Qt.UserRole, template)
            item = self.list_templates.addItem(item)

    def _template_selected(self):
        item = self.list_templates.currentItem()
        ptype = item.data(Qt.UserRole)
        self.text_info.setText(ptype.description)

    def _start_wizard(self):
        item = self.list_templates.currentItem()
        if item is not None:
            ptype = item.data(Qt.UserRole)
