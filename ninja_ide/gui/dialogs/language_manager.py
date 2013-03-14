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

import os
#lint:disable
try:
    from urllib.request import urlopen
    from urllib.error import URLError
except ImportError:
    from urllib2 import urlopen
    from urllib2 import URLError
#lint:enable

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QSpacerItem
from PyQt4.QtGui import QSizePolicy
from PyQt4.QtGui import QTabWidget
from PyQt4.QtGui import QTableWidget
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QDialog
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL

from ninja_ide import resources
from ninja_ide.core import file_manager
from ninja_ide.tools import ui_tools
from ninja_ide.tools import json_manager


class LanguagesManagerWidget(QDialog):

    def __init__(self, parent):
        QDialog.__init__(self, parent, Qt.Dialog)
        self.setWindowTitle(self.tr("Language Manager"))
        self.resize(700, 500)

        vbox = QVBoxLayout(self)
        self._tabs = QTabWidget()
        vbox.addWidget(self._tabs)
        # Footer
        hbox = QHBoxLayout()
        btn_close = QPushButton(self.tr('Close'))
        btnReload = QPushButton(self.tr("Reload"))
        hbox.addWidget(btn_close)
        hbox.addSpacerItem(QSpacerItem(1, 0, QSizePolicy.Expanding))
        hbox.addWidget(btnReload)
        vbox.addLayout(hbox)
        self.overlay = ui_tools.Overlay(self)
        self.overlay.show()

        self._languages = []
        self._loading = True
        self.downloadItems = []

        #Load Themes with Thread
        self.connect(btnReload, SIGNAL("clicked()"), self._reload_languages)
        self._thread = ui_tools.ThreadExecution(self.execute_thread)
        self.connect(self._thread, SIGNAL("finished()"),
            self.load_languages_data)
        self.connect(btn_close, SIGNAL('clicked()'), self.close)
        self._reload_languages()

    def _reload_languages(self):
        self.overlay.show()
        self._loading = True
        self._thread.execute = self.execute_thread
        self._thread.start()

    def load_languages_data(self):
        if self._loading:
            self._tabs.clear()
            self._languageWidget = LanguageWidget(self, self._languages)
            self._tabs.addTab(self._languageWidget,
                self.tr("Languages"))
            self._loading = False
        self.overlay.hide()
        self._thread.wait()

    def download_language(self, language):
        self.overlay.show()
        self.downloadItems = language
        self._thread.execute = self._download_language_thread
        self._thread.start()

    def resizeEvent(self, event):
        self.overlay.resize(event.size())
        event.accept()

    def execute_thread(self):
        try:
            descriptor_languages = urlopen(resources.LANGUAGES_URL)
            languages = json_manager.parse(descriptor_languages)
            languages = [[name, languages[name]] for name in languages]
            local_languages = self.get_local_languages()
            languages = [languages[i] for i in range(len(languages)) if
                os.path.basename(languages[i][1]) not in local_languages]
            self._languages = languages
        except URLError:
            self._languages = []

    def get_local_languages(self):
        if not file_manager.folder_exists(resources.LANGS_DOWNLOAD):
            file_manager.create_tree_folders(resources.LANGS_DOWNLOAD)
        languages = os.listdir(resources.LANGS_DOWNLOAD) + \
            os.listdir(resources.LANGS)
        languages = [s for s in languages if s.endswith('.qm')]
        return languages

    def _download_language_thread(self):
        for d in self.downloadItems:
            self.download(d[1], resources.LANGS_DOWNLOAD)

    def download(self, url, folder):
        fileName = os.path.join(folder, os.path.basename(url))
        try:
            content = urlopen(url)
            f = open(fileName, 'wb')
            f.write(content.read())
            f.close()
        except URLError:
            return


class LanguageWidget(QWidget):

    def __init__(self, parent, languages):
        QWidget.__init__(self, parent)
        self._parent = parent
        self._languages = languages
        vbox = QVBoxLayout(self)
        self._table = QTableWidget(1, 2)
        self._table.removeRow(0)
        vbox.addWidget(self._table)
        ui_tools.load_table(self._table,
            [self.tr('Language'), self.tr('URL')], self._languages)
        btnUninstall = QPushButton(self.tr('Download'))
        btnUninstall.setMaximumWidth(100)
        vbox.addWidget(btnUninstall)
        self._table.setColumnWidth(0, 200)

        self.connect(btnUninstall, SIGNAL("clicked()"),
            self._download_language)

    def _download_language(self):
        languages = ui_tools.remove_get_selected_items(self._table,
            self._languages)
        self._parent.download_language(languages)
