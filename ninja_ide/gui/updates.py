# *-* coding: UTF-8 *-*

import urllib
import webbrowser
import logging

from PyQt4.QtGui import QSystemTrayIcon
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

        if settings.NOTIFY_UPDATES:
            self.thread = ThreadUpdates()

            self.connect(self, SIGNAL("messageClicked()"), self._show_download)
            self.connect(self.thread, SIGNAL("finished()"),
                            self._show_messages)
            self.thread.start()
        else:
            self.show = self.hide

    def _show_messages(self):
        try:
            if self._convert_version_to_float(ninja_ide.__version__) \
            < self._convert_version_to_float(self.thread.ide['version']):
                if self.supportsMessages():
                    self.showMessage(self.tr("NINJA-IDE Updates"),
                        self.tr("New Version of NINJA-IDE\nAvailable: ") + \
                        self.thread.ide['version'] +
                        self.tr("\n\nClick here to Download"),
                        QSystemTrayIcon.Information, 10000)
                else:
                    button = QMessageBox.information(self.parent(),
                        self.tr("NINJA-IDE Updates"),
                        self.tr("New Version of NINJA-IDE\nAvailable: ") + \
                        self.thread.ide['version'])
                    if button == QMessageBox.Ok:
                        self._show_download()
            else:
                self.hide()
        except:
            logger.warning('Versions can not be compared.')
            self.hide()

    def _convert_version_to_float(self, version):
        number = 0
        if version.lower().find('beta') != -1:
            number = float(version.split('-')[0]) - 0.02
        elif version.lower().find('rc') != -1:
            number = float(version.split('-')[0]) - 0.01
        elif version.lower().find('dev') != -1:
            number = float(version.split('-')[0]) - 0.03
        else:
            number = float(version)
        return number

    def _show_download(self):
        webbrowser.open(self.thread.ide['downloads'])
        self.hide()


class ThreadUpdates(QThread):

    def __init__(self):
        QThread.__init__(self)
        self.ide = {}
#        self.plugins = []

    def run(self):
        try:
            #Check for IDE Updates
            ninja_version = urllib.urlopen(resources.UPDATES_URL)
            self.ide = json_manager.parse(ninja_version)

#            available = ninja_ide.core.available_plugins()
#            local_plugins = ninja_ide.core.local_plugins()
#            updates = []
#            for lp in local_plugins:
#                if lp in available:
#                    ava = available.pop(lp)
#                    if float(ava[1]) > float(local_plugins[lp][1]):
#                        updates += [[lp, ava[0], ava[1], ava[2]]]
#            self.plugins = updates
        except:
            logger.info('no connection available')
