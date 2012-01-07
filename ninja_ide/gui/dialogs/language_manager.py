# *-* coding: utf-8 *-*
from __future__ import absolute_import

import os
import urllib2

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QVBoxLayout
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
        self.setModal(True)
        self.resize(700, 500)

        vbox = QVBoxLayout(self)
        self._tabs = QTabWidget()
        vbox.addWidget(self._tabs)
        btnReload = QPushButton(self.tr("Reload"))
        btnReload.setMaximumWidth(100)
        vbox.addWidget(btnReload)
        self.overlay = ui_tools.Overlay(self)
        self.overlay.show()

        self._languages = []
        self._loading = True
        self.downloadItems = []

        #Load Themes with Thread
        self.connect(btnReload, SIGNAL("clicked()"), self._reload_languages)
        self._thread = ui_tools.ThreadCallback(self.execute_thread)
        self.connect(self._thread, SIGNAL("finished()"),
            self.load_languages_data)
        self._reload_languages()

    def _reload_languages(self):
        self.overlay.show()
        self._loading = True
        self._thread.execute = self.execute_thread
        self._thread.start()

    def load_languages_data(self):
        if self._loading:
            self._tabs.clear()
            self._languageWidget = languageWidget(self, self._languages)
            self._tabs.addTab(self._languageWidget,
                self.tr("Languages"))
            self._loading = False
        self.overlay.hide()

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
            descriptor_languages = urllib2.urlopen(resources.LANGUAGES_URL)
            languages = json_manager.parse(descriptor_languages)
            languages = [[name, languages[name]] for name in languages]
            local_languages = self.get_local_languages()
            languages = [languages[i] for i in range(len(languages)) if \
                os.path.basename(languages[i][1]) not in local_languages]
            self._languages = languages
        except urllib2.URLError:
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
            content = urllib2.urlopen(url)
            f = open(fileName, 'wb')
            f.write(content.read())
            f.close()
        except urllib2.URLError:
            return


class languageWidget(QWidget):

    def __init__(self, parent, languages):
        QWidget.__init__(self, parent)
        self._parent = parent
        self._languages = languages
        vbox = QVBoxLayout(self)
        self._table = QTableWidget(1, 2)
        self._table.removeRow(0)
        vbox.addWidget(self._table)
        ui_tools.load_table(self._table, ['Language', 'URL'], self._languages)
        btnUninstall = QPushButton('Download')
        btnUninstall.setMaximumWidth(100)
        vbox.addWidget(btnUninstall)
        self._table.setColumnWidth(0, 200)

        self.connect(btnUninstall, SIGNAL("clicked()"),
            self._download_language)

    def _download_language(self):
        languages = ui_tools.remove_get_selected_items(self._table,
            self._languages)
        self._parent.download_language(languages)
