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


class ThemesManagerWidget(QDialog):

    def __init__(self, parent):
        QDialog.__init__(self, parent, Qt.Dialog)
        self.setWindowTitle(self.tr("Themes Manager"))
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

        self._schemes = []
        self._loading = True
        self.downloadItems = []

        #Load Themes with Thread
        self.connect(btnReload, SIGNAL("clicked()"), self._reload_themes)
        self._thread = ui_tools.ThreadCallback(self.execute_thread)
        self.connect(self._thread, SIGNAL("finished()"), self.load_skins_data)
        self._reload_themes()

    def _reload_themes(self):
        self.overlay.show()
        self._loading = True
        self._thread.execute = self.execute_thread
        self._thread.start()

    def load_skins_data(self):
        if self._loading:
            self._tabs.clear()
            self._schemeWidget = SchemeWidget(self, self._schemes)
            self._tabs.addTab(self._schemeWidget, self.tr("Editor Schemes"))
            self._loading = False
        self.overlay.hide()

    def download_scheme(self, scheme):
        self.overlay.show()
        self.downloadItems = scheme
        self._thread.execute = self._download_scheme_thread
        self._thread.start()

    def resizeEvent(self, event):
        self.overlay.resize(event.size())
        event.accept()

    def execute_thread(self):
        try:
            descriptor_schemes = urllib2.urlopen(resources.SCHEMES_URL)
            schemes = json_manager.parse(descriptor_schemes)
            schemes = [[name, schemes[name]] for name in schemes]
            local_schemes = self.get_local_schemes()
            schemes = [schemes[i] for i in range(len(schemes)) if \
                os.path.basename(schemes[i][1]) not in local_schemes]
            self._schemes = schemes
        except urllib2.URLError:
            self._schemes = []

    def get_local_schemes(self):
        if not file_manager.folder_exists(resources.EDITOR_SKINS):
            file_manager.create_tree_folders(resources.EDITOR_SKINS)
        schemes = os.listdir(resources.EDITOR_SKINS)
        schemes = [s for s in schemes if s.endswith('.color')]
        return schemes

    def _download_scheme_thread(self):
        for d in self.downloadItems:
            self.download(d[1], resources.EDITOR_SKINS)

    def download(self, url, folder):
        fileName = os.path.join(folder, os.path.basename(url))
        try:
            content = urllib2.urlopen(url)
            f = open(fileName, 'w')
            f.write(content.read())
            f.close()
        except urllib2.URLError:
            return


class SchemeWidget(QWidget):

    def __init__(self, parent, schemes):
        QWidget.__init__(self, parent)
        self._parent = parent
        self._schemes = schemes
        vbox = QVBoxLayout(self)
        self._table = QTableWidget(1, 2)
        self._table.removeRow(0)
        vbox.addWidget(self._table)
        ui_tools.load_table(self._table, ['Name', 'URL'], self._schemes)
        btnUninstall = QPushButton('Download')
        btnUninstall.setMaximumWidth(100)
        vbox.addWidget(btnUninstall)
        self._table.setColumnWidth(0, 200)

        self.connect(btnUninstall, SIGNAL("clicked()"), self._download_scheme)

    def _download_scheme(self):
        schemes = ui_tools.remove_get_selected_items(self._table,
            self._schemes)
        self._parent.download_scheme(schemes)
