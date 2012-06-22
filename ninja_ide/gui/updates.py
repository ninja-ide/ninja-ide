# *-* coding: UTF-8 *-*

import urllib
import webbrowser
import logging
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
from ninja_ide.core import settings
from ninja_ide.tools import json_manager


logger = logging.getLogger('ninja_ide.gui.updates')


class TrayIconUpdates(QSystemTrayIcon):

    def __init__(self, parent):
        QSystemTrayIcon.__init__(self, parent)
        icon = QIcon(resources.IMAGES['iconUpdate'])
        self.setIcon(icon)
        self.setup_menu()
        self.ide_version = '0'
        self.download_link = ''

        if settings.NOTIFY_UPDATES:
            self.thread = ThreadUpdates()

            self.connect(self.thread,
                SIGNAL("versionReceived(QString, QString)"),
                self._show_messages)
            self.thread.start()
        else:
            self.show = self.hide

    def setup_menu(self, show_downloads=False):
        self.menu = QMenu()
        if show_downloads:
            self.download = QAction(self.tr("Download Version: %1!").arg(
                self.ide_version),
                self, triggered=self._show_download)
            self.menu.addAction(self.download)
            self.menu.addSeparator()
        self.quit_action = QAction(self.tr("Close Update Notifications"),
            self, triggered=self.hide)
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
                        self.tr("New Version of NINJA-IDE\nAvailable: ") + \
                        self.ide_version + \
                        self.tr("\n\nCheck the Update Icon Menu to Download!"),
                        QSystemTrayIcon.Information, 10000)
                else:
                    button = QMessageBox.information(self.parent(),
                        self.tr("NINJA-IDE Updates"),
                        self.tr("New Version of NINJA-IDE\nAvailable: ") + \
                        self.ide_version)
                    if button == QMessageBox.Ok:
                        self._show_download()
            else:
                self.hide()
        except Exception, reason:
            print reason
            logger.warning('Versions can not be compared: %r', reason)
            self.hide()

    def _show_download(self):
        webbrowser.open(self.download_link)
        self.hide()


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
