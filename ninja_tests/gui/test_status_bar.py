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

from PyQt4.QtGui import QApplication

from ninja_ide.gui import status_bar
from ninja_tests import BaseTest


class StatusBarTestCase(BaseTest):

    def setUp(self):
        super(StatusBarTestCase, self).setUp()
        self.app = QApplication(sys.argv)
        self.status = status_bar.StatusBar()

    def test_yes(self):
        self.assertTrue(True)