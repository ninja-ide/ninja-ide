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
from __future__ import unicode_literals

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QLabel
from PyQt4.QtCore import SIGNAL

from ninja_ide import translations
from ninja_ide.gui.dialogs.preferences import preferences


class Plugins(QWidget):
    """Plugins widget class."""

    def __init__(self, parent):
        super(Plugins, self).__init__()
        self._preferences, vbox = parent, QVBoxLayout(self)
        label = QLabel(translations.TR_PREFERENCES_PLUGINS_MAIN)
        vbox.addWidget(label)

        self.connect(self._preferences, SIGNAL("savePreferences()"), self.save)

    def save(self):
        pass


preferences.Preferences.register_configuration(
    'PLUGINS',
    Plugins,
    translations.TR_PREFERENCES_PLUGINS,
    preferences.SECTIONS['PLUGINS'])
