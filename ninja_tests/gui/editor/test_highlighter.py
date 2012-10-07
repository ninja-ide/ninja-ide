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
import unittest
from ninja_ide.gui.editor import highlighter
from PyQt4.QtGui import QFont


class HighlighterFormatTestCase(unittest.TestCase):

    def setUp(self):
        self._old_font = u"Monospace"
        highlighter.settings.FONT_FAMILY = self._old_font
        self._color = "#000000"
        self._a_format = highlighter.format(self._color)
        b_i_string = "bold italic"
        self._bold_italic = highlighter.format(self._color, b_i_string)
        self._new_font = u"Arial"
        highlighter.settings.FONT_FAMILY = self._new_font
        self._new_font_format = highlighter.format(self._color)

    def tearDown(self):
        reload(highlighter)

    def test_format_sets_color(self):
        color_name = self._a_format.foreground().color().name()
        self.assertEqual(self._color, color_name)

    def test_format_sets_bold(self):
        bold = QFont.Bold
        f_weight = self._bold_italic.fontWeight()
        self.assertEqual(bold, f_weight)
        f_weight = self._a_format.fontWeight()
        self.assertNotEqual(bold, f_weight)

    def test_format_sets_italic(self):
        italic = self._bold_italic.fontItalic()
        self.assertTrue(italic)
        italic = self._a_format.fontItalic()
        self.assertFalse(italic)

    def test_format_set_font(self):
        font = self._a_format.fontFamily()
        self.assertEqual(self._old_font, font)
        font = self._new_font_format.fontFamily()
        self.assertEqual(self._new_font, font)


if __name__ == '__main__':
    unittest.main()
