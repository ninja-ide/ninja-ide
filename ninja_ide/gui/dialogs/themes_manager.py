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
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QDialog
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL

from ninja_ide import resources
from ninja_ide.core.file_handling import file_manager
from ninja_ide.tools import ui_tools
from ninja_ide.tools import json_manager


class ThemesManagerWidget(QDialog):
    """Themes manager dialog class"""

    def __init__(self, parent):
        QDialog.__init__(self, parent, Qt.Dialog)
        self.setWindowTitle(self.tr("Themes Manager"))
        self.setMinimumSize(ui_tools.get_modal_size())

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

        self._schemes = []
        self._loading = True
        self.downloadItems = []

        #Load Themes with Thread
        self.connect(btnReload, SIGNAL("clicked()"), self._reload_themes)
        self._thread = ui_tools.ThreadExecution(self.execute_thread)
        self.connect(self._thread, SIGNAL("finished()"), self.load_skins_data)
        self.connect(btn_close, SIGNAL('clicked()'), self.close)
        self._reload_themes()

    def _reload_themes(self):
        """Display the overlay and reload all themes"""
        self.overlay.show()
        self._loading = True
        self._thread.execute = self.execute_thread
        self._thread.start()

    def load_skins_data(self):
        """Load all schemes data"""
        if self._loading:
            self._tabs.clear()
            self._schemeWidget = SchemeWidget(self, self._schemes)
            self._tabs.addTab(self._schemeWidget, self.tr("Editor Schemes"))
            self._loading = False
        self.overlay.hide()
        self._thread.wait()

    def download_scheme(self, scheme):
        """Download an argument scheme"""
        self.overlay.show()
        self.downloadItems = scheme
        self._thread.execute = self._download_scheme_thread
        self._thread.start()

    def resizeEvent(self, event):
        """Handle Resize event"""
        self.overlay.resize(event.size())
        event.accept()

    def execute_thread(self):
        """Execute a download thread"""
        try:
            descriptor_schemes = urlopen(resources.SCHEMES_URL)
            schemes = json_manager.parse(descriptor_schemes)
            schemes = [(d['name'], d['download']) for d in schemes]
            local_schemes = self.get_local_schemes()
            schemes = [schemes[i] for i in range(len(schemes)) if
                os.path.basename(schemes[i][1]) not in local_schemes]
            self._schemes = schemes
        except URLError:
            self._schemes = []

    def get_local_schemes(self):
        """Return all already available local schemes"""
        if not file_manager.folder_exists(resources.EDITOR_SKINS):
            file_manager.create_tree_folders(resources.EDITOR_SKINS)
        schemes = os.listdir(resources.EDITOR_SKINS)
        schemes = [s for s in schemes if s.lower().endswith('.color')]
        return schemes

    def _download_scheme_thread(self):
        """Iterate over all items downloading them"""
        for d in self.downloadItems:
            self.download(d[1], resources.EDITOR_SKINS)

    def download(self, url, folder):
        """Download argument url on arguement folder"""
        fileName = os.path.join(folder, os.path.basename(url))
        try:
            content = urlopen(url)
            with open(fileName, 'w') as f:
                f.write(content.read())
        except URLError:
            return


class SchemeWidget(QWidget):
    """Scheme internal widget class for Scheme Manager parent window"""

    def __init__(self, parent, schemes):
        QWidget.__init__(self, parent)
        self._parent = parent
        self._schemes = schemes
        vbox = QVBoxLayout(self)
        self._table = ui_tools.CheckableHeaderTable(1, 2)
        self._table.removeRow(0)
        vbox.addWidget(self._table)
        ui_tools.load_table(self._table, [self.tr('Name'), self.tr('URL')],
            self._schemes)
        btnUninstall = QPushButton(self.tr('Download'))
        btnUninstall.setMaximumWidth(100)
        vbox.addWidget(btnUninstall)
        self._table.setColumnWidth(0, 200)
        self._table.setSortingEnabled(True)
        self._table.setAlternatingRowColors(True)
        self.connect(btnUninstall, SIGNAL("clicked()"), self._download_scheme)

    def _download_scheme(self):
        """Download an scheme calling parent class method"""
        schemes = ui_tools.remove_get_selected_items(self._table, self._schemes)
        self._parent.download_scheme(schemes)
