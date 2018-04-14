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
import hashlib

from PyQt5.QtCore import QObject
from PyQt5.QtCore import QFile
from PyQt5.QtCore import QTextStream
from PyQt5.QtCore import QIODevice
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import pyqtSlot

from ninja_ide.core import settings
from ninja_ide.gui.ide import IDE
from ninja_ide import resources
from ninja_ide.tools.logger import NinjaLogger

logger = NinjaLogger(__name__)

# TODO: handle untitled files


class NSwapFile(QObject):

    """
    This class implements the hot-exit and autosave feature.

    Ninja will remember unsaved changes to files when you exit by default.
    Hot exit is triggered when the IDE is closed.

    If the auto-save feature is enabled, Ninja will create backup
    files periodically.
    """

    def __init__(self, neditable):
        QObject.__init__(self)
        self._neditable = neditable
        self.__dirty = False

        self.__filename = None

        self.__timer = QTimer(self)
        self.__timer.setSingleShot(True)
        self.__timer.timeout.connect(self._autosave)

        ninjaide = IDE.get_service("ide")
        # Connections
        ninjaide.goingDown.connect(self._on_ide_going_down)
        self._neditable.fileLoaded.connect(self._on_file_loaded)
        self._neditable.fileSaved.connect(self._on_file_saved)
        self._neditable.fileClosing.connect(self._on_file_closing)

    @pyqtSlot()
    def _on_file_closing(self):
        if not self._neditable.new_document:
            self.__remove()
        self.deleteLater()

    @pyqtSlot()
    def _autosave(self):
        if self._neditable.editor.is_modified:
            flags = QIODevice.WriteOnly
            f = QFile(self.filename())
            if not f.open(flags):
                raise IOError(f.errorString())
            content = self._neditable.editor.text
            stream = QTextStream(f)
            encoded_stream = stream.codec().fromUnicode(content)
            f.write(encoded_stream)
            f.flush()
            f.close()

    def filename(self):
        if self.__filename is None:
            self.__filename = self.__unique_filename()
        return self.__filename

    def __unique_filename(self):
        fname = self._neditable.file_path.encode()
        unique_filename = hashlib.md5(fname).hexdigest()
        return os.path.join(resources.BACKUP_FILES, unique_filename)

    def exists(self):
        exists = False
        if os.path.exists(self.filename()):
            exists = True
        return exists

    @pyqtSlot()
    def _on_ide_going_down(self):
        if not self._neditable.new_document:
            self._autosave()

    @pyqtSlot()
    def _on_file_saved(self):
        self.__remove()

    def __remove(self):
        if self.exists():
            logger.debug("Removing backup file...")
            os.remove(self.filename())
            self.__dirty = False

    @property
    def dirty(self):
        return self.__dirty

    @pyqtSlot()
    def _on_file_loaded(self):
        if self._neditable.new_document:
            return
        if os.path.exists(self.filename()):
            logger.debug("Reloaded...")
            self.__dirty = True
            with open(self.filename()) as fp:
                content = fp.read()
            self._neditable.editor.text = content
            self._neditable.document.setModified(True)
        self._neditable.editor.textChanged.connect(self._on_text_changed)

    @pyqtSlot()
    def _on_text_changed(self):
        if not self._neditable.editor.is_modified or not settings.AUTOSAVE:
            return

        if self.__timer.isActive():
            self.__timer.stop()
        self.__timer.start(settings.AUTOSAVE_DELAY)
