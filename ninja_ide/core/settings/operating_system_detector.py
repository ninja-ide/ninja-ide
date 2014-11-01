# -*- coding: utf-8 -*-


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


"""Operating System Detector for Ninja-IDE."""


# imports
import os
import sys

from PyQt4.QtGui import QFont
from PyQt4.QtCore import QDir
from PyQt4.QtCore import QFileInfo

from ninja_ide.core.settings import *  # lint:ok


###############################################################################
# OS DETECTOR
###############################################################################


# Use this flags instead of sys.platform spreaded in the source code
IS_WINDOWS = False

IS_MAC_OS = False

OS_KEY = "Ctrl"

FONT = QFont('Monospace', 12)


if sys.platform.startswith("darwin"):
    from PyQt4.QtGui import QKeySequence
    from PyQt4.QtCore import Qt

    FONT = QFont('Monaco', 12)
    OS_KEY = QKeySequence(Qt.CTRL).toString(QKeySequence.NativeText)
    IS_MAC_OS = True
elif sys.platform.startswith("win"):
    FONT = QFont('Courier', 12)
    IS_WINDOWS = True


def detect_python_path():
    """Function to detect Python interpreter executable."""
    suggested, dirs = [], []

    if (IS_WINDOWS and PYTHON_EXEC_CONFIGURED_BY_USER) or not IS_WINDOWS:
        return suggested

    try:
        drives = [QDir.toNativeSeparators(d.absolutePath())
                  for d in QDir.drives()]

        for drive in drives:
            info = QFileInfo(drive)
            if info.isReadable():
                dirs += [os.path.join(drive, folder)
                         for folder in os.listdir(drive)]
        for folder in dirs:
            file_path = os.path.join(folder, "python.exe")
            if ("python" in folder.lower()) and os.path.exists(file_path):
                suggested.append(file_path)
    except Exception as error:
        print((error, "Detection couldnt be executed."))
    finally:
        return suggested
