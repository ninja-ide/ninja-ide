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


from PyQt4.QtGui import QPushButton, QVBoxLayout, QWidget, QMessageBox

from ninja_ide import translations
from ninja_ide.core import settings
from ninja_ide.gui.explorer.explorer_container import ExplorerContainer
from ninja_ide.gui.ide import IDE

try:
    from PyQt4.QtWebKit import QWebInspector
except:
    settings.WEBINSPECTOR_SUPPORTED = False


class WebInspector(QWidget):
    """WebInspector widget class"""

    def __init__(self, parent):
        QWidget.__init__(self, parent)
        vbox = QVBoxLayout(self)
        self._webInspector = QWebInspector(self)
        vbox.addWidget(self._webInspector)
        self.btnDock = QPushButton(translations.TR_UNDOCK)
        vbox.addWidget(self.btnDock)

        ExplorerContainer.register_tab(translations.TR_TAB_WEB_INSPECTOR, self)
        IDE.register_service('web_inspector', self)

    def refresh_inspector(self):
        """Refresh WebInspector widget by hiding and showing"""
        self._webInspector.hide()
        self._webInspector.show()

    def set_inspection_page(self, page):
        """Method to load an argument page object on the WebInspector"""
        self._webInspector.setPage(page)
        self._webInspector.setVisible(True)


if settings.SHOW_WEB_INSPECTOR and settings.WEBINSPECTOR_SUPPORTED:
    webInspector = WebInspector()
else:
    if not settings.WEBINSPECTOR_SUPPORTED:
        QMessageBox.information(None, translations.TR_TAB_WEB_INSPECTOR,
                                translations.TR_WEB_INSPECTOR_NOT_SUPPORTED)
    webInspector = None
