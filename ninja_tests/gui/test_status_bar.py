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

import sys

# Import this before Qt to set the correct API
import ninja_ide  # lint:ok

from PyQt4.QtGui import QApplication

from ninja_ide.gui import status_bar
from ninja_ide.gui.main_panel import main_container
from ninja_tests import BaseTest
from ninja_tests import gui


class StatusBarTestCase(BaseTest):

    def setUp(self):
        super(StatusBarTestCase, self).setUp()
        self.app = QApplication(sys.argv)
        self.parent = gui.FakeParent()
        self.patch(main_container.editor, 'Editor', gui.FakeEditor)
        self.main = main_container.MainContainer(None)
        self.main._parent = self.parent
        self.status = status_bar.StatusBar()

    def test_show(self):
        editor = self.main.add_editor()
        editor.setPlainText('ninja test')
        editor.selectAll()
        data = []

        def fake_find_matches(*arg):
            data.append(arg)

        self.patch(self.status._searchWidget, 'find_matches',
            fake_find_matches)
        self.status.show()
        expected = [(editor, True)]
        self.assertEqual(data, expected)