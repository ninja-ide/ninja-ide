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

from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QTabWidget
from PyQt4.QtGui import QPlainTextEdit
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QPushButton

from PyQt4.QtCore import SIGNAL

from ninja_ide.tools import ui_tools
from ninja_ide import translations


class PluginErrorDialog(QDialog):
    """
    Dialog with tabs each tab is a python traceback
    """
    def __init__(self):
        QDialog.__init__(self)
        self.setWindowTitle(translations.TR_PLUGIN_ERROR_REPORT)
        self.setMinimumSize(ui_tools.get_modal_size())
        vbox = QVBoxLayout(self)
        label = QLabel(translations.TR_SOME_PLUGINS_REMOVED)
        vbox.addWidget(label)
        self._tabs = QTabWidget()
        vbox.addWidget(self._tabs)
        hbox = QHBoxLayout()
        btnAccept = QPushButton(translations.TR_ACCEPT)
        btnAccept.setMaximumWidth(100)
        hbox.addWidget(btnAccept)
        vbox.addLayout(hbox)
        #signals
        self.connect(btnAccept, SIGNAL("clicked()"), self.close)

    def add_traceback(self, plugin_name, traceback_msg):
        """Add a Traceback to the widget on a new tab"""
        traceback_widget = TracebackWidget(traceback_msg)
        self._tabs.addTab(traceback_widget, plugin_name)


class TracebackWidget(QWidget):
    """
    Represents a python traceback
    """

    def __init__(self, traceback_msg):
        QWidget.__init__(self)
        vbox = QVBoxLayout(self)
        self._editor = QPlainTextEdit()
        vbox.addWidget(QLabel(translations.TR_TRACEBACK))
        vbox.addWidget(self._editor)
        self._editor.setReadOnly(True)
        self._editor.setLineWrapMode(0)
        self._editor.insertPlainText(traceback_msg)
        self._editor.selectAll()
