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

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QApplication
from PyQt4.QtGui import QListWidget
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QSizePolicy
from PyQt4.QtGui import QSpacerItem
from PyQt4.QtGui import QPushButton
from PyQt4.QtCore import SIGNAL

from ninja_ide import resources
from ninja_ide import translations
from ninja_ide.core import settings
from ninja_ide.core.file_handling import file_manager
from ninja_ide.gui.ide import IDE
from ninja_ide.gui.dialogs.preferences import preferences
from ninja_ide.gui.dialogs.preferences import preferences_theme_editor


class Theme(QWidget):
    """Theme widget class."""

    def __init__(self, parent):
        super(Theme, self).__init__()
        self._preferences, vbox = parent, QVBoxLayout(self)
        vbox.addWidget(QLabel(self.tr("<b>Select Theme:</b>")))
        self.list_skins = QListWidget()
        self.list_skins.setSelectionMode(QListWidget.SingleSelection)
        vbox.addWidget(self.list_skins)
        self.btn_delete = QPushButton(self.tr("Delete Theme"))
        self.btn_preview = QPushButton(self.tr("Preview Theme"))
        self.btn_create = QPushButton(self.tr("Create Theme"))
        hbox = QHBoxLayout()
        hbox.addWidget(self.btn_delete)
        hbox.addSpacerItem(QSpacerItem(10, 0, QSizePolicy.Expanding,
                           QSizePolicy.Fixed))
        hbox.addWidget(self.btn_preview)
        hbox.addWidget(self.btn_create)
        vbox.addLayout(hbox)
        self._refresh_list()

        self.connect(self.btn_preview, SIGNAL("clicked()"), self.preview_theme)
        self.connect(self.btn_delete, SIGNAL("clicked()"), self.delete_theme)
        self.connect(self.btn_create, SIGNAL("clicked()"), self.create_theme)

        self.connect(self._preferences, SIGNAL("savePreferences()"), self.save)

    def delete_theme(self):
        if self.list_skins.currentRow() != 0:
            file_name = ("%s.qss" % self.list_skins.currentItem().text())
            qss_file = file_manager.create_path(resources.NINJA_THEME_DOWNLOAD,
                                                file_name)
            file_manager.delete_file(qss_file)
            self._refresh_list()

    def create_theme(self):
        designer = preferences_theme_editor.ThemeEditor(self)
        designer.exec_()
        self._refresh_list()

    def showEvent(self, event):
        self._refresh_list()
        super(Theme, self).showEvent(event)

    def _refresh_list(self):
        self.list_skins.clear()
        self.list_skins.addItem("Default")

        files = [file_manager.get_file_name(filename) for filename in
                 file_manager.get_files_from_folder(
                     resources.NINJA_THEME_DOWNLOAD, "qss")]
        files.sort()
        self.list_skins.addItems(files)

        if settings.NINJA_SKIN in files:
            index = files.index(settings.NINJA_SKIN)
            self.list_skins.setCurrentRow(index + 1)
        else:
            self.list_skins.setCurrentRow(0)

    def save(self):
        qsettings = IDE.ninja_settings()
        settings.NINJA_SKIN = self.list_skins.currentItem().text()
        qsettings.setValue("preferences/theme/skin", settings.NINJA_SKIN)
        self.preview_theme()

    def preview_theme(self):
        if self.list_skins.currentRow() == 0:
            qss_file = resources.NINJA_THEME
        else:
            file_name = ("%s.qss" % self.list_skins.currentItem().text())
            qss_file = file_manager.create_path(resources.NINJA_THEME_DOWNLOAD,
                                                file_name)
        with open(qss_file) as f:
            qss = f.read()
        QApplication.instance().setStyleSheet(qss)


preferences.Preferences.register_configuration(
    'THEME',
    Theme,
    translations.TR_PREFERENCES_THEME,
    preferences.SECTIONS['THEME'])
