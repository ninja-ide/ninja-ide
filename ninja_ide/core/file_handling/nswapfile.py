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

import os
import tempfile

from PyQt5.QtCore import QObject
from PyQt5.QtCore import QFile
from PyQt5.QtCore import QTextStream
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import QIODevice
from PyQt5.QtCore import QFileDevice
from PyQt5.QtCore import pyqtSignal

from ninja_ide.core import settings
from ninja_ide.tools.logger import NinjaLogger
logger = NinjaLogger(__name__)

SWAP_PATH = tempfile.gettempdir()

# FIXME: maybe it would be better to use binary file
# FIXME: instead of making a copy of the original file, replicate the editing
# actions (insert, remove, etc.). Take a look at QTextDocument.contentsChange
# signal


class NSwapFile(QObject):
    """
    In case Ninja-IDE crash, this can be used to recover the lost data.

    When the user begins to edit an existing file on the disk, this object
    creates a swap file and activates a timer that will execute a function,
    that will update that swap file as soon as the timeout ends (by default,
    is 15 seconds).
    The swap file is deleted when the original file is saved or closed.
    When system or Ninja crash, the swap file exists on disk and Ninja will
    used to recover the lost data.
    """

    canBeRecovered = pyqtSignal()

    def __init__(self, neditable):
        QObject.__init__(self)
        self._neditable = neditable
        self.__swap_file = QFile()
        self.__stream = QTextStream()

        # Activate timer when user typing
        self.__timer = QTimer()
        self.__timer.setSingleShot(True)

        self.__timer.timeout.connect(self._finish_typing)
        self._neditable.fileLoaded.connect(self._file_loaded)
        self._neditable.fileSaved.connect(self._file_saved)

        self.init(tracking=True)

    def init(self, tracking):
        if tracking:
            self._neditable.editor.textChanged.connect(self._start_typing)
            self._neditable.fileClosing.connect(self._file_closed)
        else:
            self._neditable.editor.textChanged.disconnect(self._start_typing)
            self._neditable.fileClosing.disconnect(self._file_closed)

    def _file_closed(self):
        """Editor was closed normally, now remove swap file"""

        self.__remove()

    def _file_saved(self):
        """If file is saved, remove swap file"""

        # Remove old swap file and set the name for the new swap file
        self.__remove()
        self.__update_filename()

    def __remove(self):
        """Remove swap file"""

        if self.__swap_file.fileName() and self.__swap_file.exists():
            self.__stream.setDevice(None)
            self.__swap_file.close()
            self.__swap_file.remove()

    def _file_loaded(self):
        """This slot is executed when a file is loaded on the editor and
        look for swap file, if exists then can be recover"""

        self.__update_filename()
        if self.__swap_file.exists():
            # In recovery process can't edit
            self._neditable.editor.setReadOnly(True)
            # Ok, can be recover
            self.canBeRecovered.emit()

    def __update_filename(self):
        # First clear filename
        self.__swap_file.setFileName("")
        # Get new path
        filename = self.filename()
        self.__swap_file.setFileName(filename)

    def _start_typing(self):
        # Skip if editor is not modified
        if not self._neditable.editor.is_modified:
            return
        # No swap file, no work
        if not self.__swap_file.fileName():
            return
        # Create the file
        if not self.__swap_file.exists():
            self.__swap_file.open(QIODevice.WriteOnly)
            permissions = QFileDevice.ReadOwner | QFileDevice.WriteOwner
            self.__swap_file.setPermissions(permissions)
            self.__stream.setDevice(self.__swap_file)

        if self.__timer.isActive():
            self.__timer.stop()
        # Write swap file to the disk every 10 seconds by default
        self.__timer.start(settings.SWAP_FILE_INTERVAL * 1000)

    def _finish_typing(self):
        if not self.__swap_file.isOpen():
            return
        logger.debug("Now write the swap file...")
        text = self._neditable.editor.text
        self.__swap_file.write(text.encode())
        self.__swap_file.flush()

    def filename(self):
        """Returns the filename for swap file"""

        path, name = os.path.split(
            os.path.join(SWAP_PATH, self._neditable.nfile.file_name))
        filename = os.path.join(path, "%s.ninja-swap" % name)
        return filename

    def recover(self):
        self._neditable.editor.setReadOnly(False)
        # Disconnect signals
        self.init(tracking=False)

        self.__stream.setDevice(self.__swap_file)
        if not self.__swap_file.open(QIODevice.ReadOnly):
            logger.warning("Can't open swap file")
            return
        # Ok
        data = []
        append = data.append
        while not self.__stream.atEnd():
            line = self.__stream.readLine()
            append(line)

        # Set data in the editor
        self._neditable.editor.text = "\n".join(data)
        self._neditable.document.setModified(True)

        # Close swap file
        self.__stream.setDevice(None)
        self.__swap_file.close()
        # Reconnect signals
        self.init(tracking=True)

    def discard(self):
        self._neditable.editor.setReadOnly(False)
        # Remove swap file
        self.__remove()
