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

from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QListWidget
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QTextBrowser
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QSpacerItem
from PyQt4.QtGui import QSizePolicy
from PyQt4.QtCore import Qt

from ninja_ide import translations


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
        self.cancel = QPushButton(translations.TR_CANCEL)
        self.choose = QPushButton(translations.TR_CHOOSE)
        hbox.addSpacerItem(QSpacerItem(1, 0, QSizePolicy.Expanding,
            QSizePolicy.Fixed))
        hbox2.addWidget(self.cancel)
        hbox2.addWidget(self.choose)
        vbox.addLayout(hbox2)