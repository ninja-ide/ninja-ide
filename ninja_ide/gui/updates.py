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

import urllib
import webbrowser
from distutils import version

from PyQt4.QtGui import QSystemTrayIcon
from PyQt4.QtGui import QAction
from PyQt4.QtGui import QMenu
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QMessageBox
from PyQt4.QtCore import QThread
from PyQt4.QtCore import SIGNAL

import ninja_ide
from ninja_ide import resources
from ninja_ide.tools import json_manager
from ninja_ide.tools.logger import NinjaLogger

logger = NinjaLogger('ninja_ide.gui.updates')


class TrayIconUpdates(QSystemTrayIcon):
    """Tray Icon to show Updates of new versions.
    @ SIGNALS:
    @ closeTrayIcon()
    """

    def __init__(self, parent):
        super(TrayIconUpdates, self).__init__(parent)
        icon = QIcon(":img/iconUpdate")
        self.setIcon(icon)
        self.setup_menu()
        self.ide_version = '0'
        self.download_link = ''

        notify = parent.ninja_settings().value(
            'preferences/general/notifyUpdates', True, type=bool)
        if notify:
            self.thread = ThreadUpdates()
            self.connect(self.thread,
                SIGNAL("versionReceived(QString, QString)"),
                self._show_messages)
            self.thread.start()

    def setup_menu(self, show_downloads=False):
        self.menu = QMenu()
        if show_downloads:
            self.download = QAction((self.tr("Download Version: %s!") %
                self.ide_version),
                self, triggered=self._show_download)
            self.menu.addAction(self.download)
            self.menu.addSeparator()
        self.quit_action = QAction(self.tr("Close Update Notifications"),
            self, triggered=self._close)
        self.menu.addAction(self.quit_action)

        self.setContextMenu(self.menu)

    def _show_messages(self, ide_version, download):
        self.ide_version = str(ide_version)
        self.download_link = str(download)
        try:
            local_version = version.LooseVersion(ninja_ide.__version__)
            web_version = version.LooseVersion(self.ide_version)
            if local_version < web_version:
                if self.supportsMessages():
                    self.setup_menu(True)
                    self.showMessage(self.tr("NINJA-IDE Updates"),
                        self.tr("New Version of NINJA-IDE\nAvailable: ") +
                        self.ide_version +
                        self.tr("\n\nCheck the Update Menu in the NINJA-IDE "
                                "System Tray icon to Download!"),
                        QSystemTrayIcon.Information, 10000)
                else:
                    button = QMessageBox.information(self.parent(),
                        self.tr("NINJA-IDE Updates"),
                        self.tr("New Version of NINJA-IDE\nAvailable: ") +
                        self.ide_version)
                    if button == QMessageBox.Ok:
                        self._show_download()
            else:
                self._close()
        except Exception as reason:
            logger.warning('Versions can not be compared: %r', reason)
            self._close()
        finally:
            self.thread.wait()

    def _close(self):
        self.emit(SIGNAL("closeTrayIcon()"))

    def _show_download(self):
        webbrowser.open(self.download_link)
        self._close()


class ThreadUpdates(QThread):

    def __init__(self):
        QThread.__init__(self)

    def run(self):
        try:
            #Check for IDE Updates
            ninja_version = urllib.urlopen(resources.UPDATES_URL)
            ide = json_manager.parse(ninja_version)
        except:
            ide = {}
            logger.info('no connection available')
        self.emit(SIGNAL("versionReceived(QString, QString)"),
            ide.get('version', '0'), ide.get('downloads', ''))
