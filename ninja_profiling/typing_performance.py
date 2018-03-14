#!/usr/bin/env python3
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

import sys
import time

from PyQt5.QtWidgets import QApplication

from PyQt5.QtCore import QTimer
from PyQt5.QtCore import Qt

from PyQt5.QtTest import QTest

sys.path.append("..")

from ninja_ide.tools import json_manager
from ninja_ide import resources

from ninja_ide.core.file_handling import nfile
from ninja_ide.gui.editor import neditable
from ninja_ide.gui.editor.editor import NEditor
from ninja_ide.gui.syntax_registry import syntax_registry  # noqa

json_manager.load_syntax()
themes = json_manager.load_editor_schemes()
resources.COLOR_SCHEME = themes["Ninja Dark"]

qapp = QApplication(sys.argv)

ninja_editor = NEditor(neditable=neditable.NEditable(nfile.NFile()))
ninja_editor.side_widgets.remove("CodeFoldingWidget")
ninja_editor.side_widgets.remove("MarkerWidget")
ninja_editor.side_widgets.remove("TextChangeWidget")
ninja_editor.side_widgets.update_viewport()
ninja_editor.side_widgets.resize()
ninja_editor.register_syntax_for()
ninja_editor.showMaximized()


click_times = {}

with open(sys.argv[1]) as fp:
    text = fp.read()


def click(key):
    clock_before = time.clock()

    if isinstance(key, str):
        QTest.keyClicks(ninja_editor, key)
    else:
        QTest.keyClick(ninja_editor, key)
    while qapp.hasPendingEvents():
        qapp.processEvents()

    clock_after = time.clock()
    ms = int((clock_after - clock_before) * 100)
    click_times[ms] = click_times.get(ms, 0) + 1


def test():
    clock_before = time.clock()

    for line in text.splitlines():
        indent_width = len(line) - len(line.lstrip())
        while ninja_editor.textCursor().positionInBlock() > indent_width:
            click(Qt.Key_Backspace)
        for i in range(
                indent_width - ninja_editor.textCursor().positionInBlock()):
            click(Qt.Key_Space)

        line = line[indent_width:]
        for char in line:
            click(char)
        click(Qt.Key_Enter)

    clock_after = time.clock()
    typing_time = clock_after - clock_before
    print("Typed {} chars in {} sec. {} ms per character".format(
        len(text), typing_time, typing_time * 1000 / len(text)))
    print("Time per click: Count of clicks")

    click_time_keys = sorted(click_times.keys())
    for click_time_key in click_time_keys:
        print("     %5dms:      %4d" % (
            click_time_key, click_times[click_time_key]))
    qapp.quit()


QTimer.singleShot(0, test)
qapp.exec_()
