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

from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtWidgets import QPlainTextEdit
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QPushButton

from PyQt5.QtCore import pyqtSignal

from ninja_ide import translations


class PluginErrorDialog(QDialog):
    """
    Dialog with tabs each tab is a python traceback
    """
    def __init__(self):
        super(PluginErrorDialog, self).__init__()
        self.setWindowTitle(translations.TR_PLUGIN_ERROR_REPORT)
        self.resize(600, 400)
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
        btnAccept.clicked['bool'].connect(self.close)

    def add_traceback(self, plugin_name, traceback_msg):
        """Add a Traceback to the widget on a new tab"""
        traceback_widget = TracebackWidget(traceback_msg)
        self._tabs.addTab(traceback_widget, plugin_name)


class TracebackWidget(QWidget):
    """
    Represents a python traceback
    """

    def __init__(self, traceback_msg):
        super(TracebackWidget, self).__init__()
        vbox = QVBoxLayout(self)
        self._editor = QPlainTextEdit()
        vbox.addWidget(QLabel(translations.TR_TRACEBACK))
        vbox.addWidget(self._editor)
        self._editor.setReadOnly(True)
        self._editor.setLineWrapMode(0)
        self._editor.insertPlainText(traceback_msg)
        self._editor.selectAll()
