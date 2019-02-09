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
import shutil

from PyQt5.QtCore import QObject
from PyQt5.QtCore import QFile
from PyQt5.QtCore import QFileSystemWatcher
from PyQt5.QtCore import QIODevice
from PyQt5.QtCore import QTextStream
from PyQt5.QtCore import pyqtSignal

from ninja_ide import translations
# FIXME: Obtain these form a getter
from ninja_ide.core import settings
from ninja_ide.tools.utils import SignalFlowControl
from .file_manager import NinjaIOException, NinjaNoFileNameException, \
    get_file_encoding, get_basename, get_file_extension

from ninja_ide.tools.logger import NinjaLogger
logger = NinjaLogger('ninja_ide.core.file_handling.nfile')
DEBUG = logger.debug

"""
How to continue:
    We need to have a filesystem representation object, said object, registers
    himself into the IDE on its __init__.py, thus avoiding all kinds of
    circular imports, this way all objects should start registering themselves
    and fail individually if they cant.
    So, to this object, whoever creates new NFiles should ask for a it, this
    way it keeps record of the files and can do closing when receives
    terminate from the ide, and decides to call a changed callback from each
    file when the watched, that should depend on it notifies a change.
"""


class NFile(QObject):
    """
    SIGNALS:
    @askForSaveFileClosing(QString)
    @fileClosing(QString)
    @fileChanged()
    @willDelete(PyQt_PyObject, PyQt_PyObject)
    @willOverWrite(PyQt_PyObject, QString, QString)
    @willMove(Qt_PyQtObject, QString, QString)
    @willSave(QString, QString)
    @savedAsNewFile(PyQt_PyObject, QString, QString)
    @gotAPath(PyQt_PyObject)
    @willAttachToExistingFile(PyQt_PyObject, QString)
    """
    fileChanged = pyqtSignal()
    fileRemoved = pyqtSignal()
    fileReaded = pyqtSignal()
    willAttachToExistingFile = pyqtSignal('PyQt_PyObject', 'QString')
    gotAPath = pyqtSignal('PyQt_PyObject')
    willSave = pyqtSignal('QString', 'QString')
    willMove = pyqtSignal('PyQt_PyObject', 'QString', 'QString')
    willOverWrite = pyqtSignal('PyQt_PyObject', 'QString', 'QString')
    willCopyTo = pyqtSignal('PyQt_PyObject', 'QString', 'QString')
    willDelete = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject')
    fileClosing = pyqtSignal('QString', bool)

    def __init__(self, path=None):
        """
        """
        self._file_path = path
        self.__created = False
        self.__watcher = None
        self.__mtime = None
        super(NFile, self).__init__()
        if not self._exists():
            self.__created = True

    @property
    def file_name(self):
        """"Returns filename of nfile"""
        file_name = None
        if self._file_path is None:
            file_name = translations.TR_NEW_DOCUMENT
        else:
            file_name = get_basename(self._file_path)
        return file_name

    @property
    def display_name(self):
        """Returns a pretty name to be displayed by tabs"""
        display_name = self.file_name
        if self._file_path is not None and not self.has_write_permission():
            display_name += translations.TR_READ_ONLY
        return display_name

    @property
    def is_new_file(self):
        return self.__created

    def file_ext(self):
        """"Returns extension of nfile"""
        if self._file_path is None:
            return ''
        return get_file_extension(self._file_path)

    @property
    def file_path(self):
        """"Returns file path of nfile"""
        return self._file_path

    def start_watching(self):
        """Create a file system watcher and connect its fileChanged
        SIGNAL to our _file_changed SLOT"""
        if self.__watcher is None:
            self.__watcher = QFileSystemWatcher(self)
            self.__watcher.fileChanged['const QString&'].connect(
                self._file_changed)
        if self._file_path is not None:
            self.__mtime = os.path.getmtime(self._file_path)
            self.__watcher.addPath(self._file_path)

    def _file_changed(self, path):
        if self._exists():
            current_mtime = os.path.getmtime(self._file_path)
            if current_mtime != self.__mtime:
                self.__mtime = current_mtime
                self.fileChanged.emit()
        # FIXME: for swap file
        # else:
        #     self.fileRemoved.emit()

    def has_write_permission(self):
        if not self._exists():
            return True
        return os.access(self._file_path, os.W_OK)

    def _exists(self):
        """
        Check if we have been created with a path and if such path exists
        In case there is no path, we are most likely a new file.
        """
        file_exists = False
        if self._file_path and os.path.exists(self._file_path):
            file_exists = True
        return file_exists

    def attach_to_path(self, new_path):
        if os.path.exists(new_path):
            signal_handler = SignalFlowControl()
            self.willAttachToExistingFile.emit(signal_handler, new_path)
            if signal_handler.stopped():
                    return
        self._file_path = new_path
        self.gotAPath.emit(self)
        return self._file_path

    def create(self):
        if self.__created:
            self.save("")
        self.__created = False

    def save(self, content, path=None):
        """
        Write a temporary file with .tnj extension and copy it over the
        original one.
        .nsf = Ninja Swap File
        # FIXME: Where to locate addExtension, does not fit here
        """
        new_path = False
        if path:
            self.attach_to_path(path)
            new_path = True

        save_path = self._file_path

        if not save_path:
            raise NinjaNoFileNameException("I am asked to write a "
                                           "file but no one told me where")
        swap_save_path = "%s.nsp" % save_path

        # If we have a file system watcher, remove the file path
        # from its watch list until we are done making changes.
        if self.__watcher is not None:
            self.__watcher.removePath(save_path)

        flags = QIODevice.WriteOnly | QIODevice.Truncate
        f = QFile(swap_save_path)
        if settings.use_platform_specific_eol():
            flags |= QIODevice.Text

        if not f.open(flags):
            raise NinjaIOException(f.errorString())

        stream = QTextStream(f)
        encoding = get_file_encoding(content)
        if encoding:
            stream.setCodec(encoding)

        encoded_stream = stream.codec().fromUnicode(content)
        f.write(encoded_stream)
        f.flush()
        f.close()
        # SIGNAL: Will save (temp, definitive) to warn folder to do something
        self.willSave.emit(swap_save_path, save_path)
        self.__mtime = os.path.getmtime(swap_save_path)
        shutil.move(swap_save_path, save_path)
        self.reset_state()

        # If we have a file system watcher, add the saved path back
        # to its watch list, otherwise create a watcher and start
        # watching
        if self.__watcher is not None:
            if new_path:
                # self.__watcher.removePath(self.__watcher.files()[0])
                self.__watcher.addPath(self._file_path)
            else:
                self.__watcher.addPath(save_path)
        else:
            self.start_watching()
        return self

    def reset_state(self):
        """
        #FIXE: to have a ref to changed I need to have the doc here
        """
        self.__created = False

    def read(self, path=None):
        """
        Read the file or fail
        """
        open_path = path and path or self._file_path
        self._file_path = open_path
        if not self._file_path:
            raise NinjaNoFileNameException("I am asked to read a file "
                                           "but no one told me from where")
        try:
            with open(open_path, 'r') as f:
                content = f.read()
        except (IOError, UnicodeDecodeError) as reason:
            raise NinjaIOException(reason)
        self.fileReaded.emit()
        return content

    def move(self, new_path):
        """
        Phisically move the file
        """
        if self._exists():
            signal_handler = SignalFlowControl()
            # SIGNALL: WILL MOVE TO, to warn folder to exist
            self.willMove.emit(signal_handler,
                               self._file_path,
                               new_path)
            if signal_handler.stopped():
                return
            if os.path.exists(new_path):
                signal_handler = SignalFlowControl()
                self.willOverWrite.emit(signal_handler,
                                        self._file_path,
                                        new_path)
                if signal_handler.stopped():
                    return
            if self.__watcher is not None:
                self.__watcher.removePath(self._file_path)
            shutil.move(self._file_path, new_path)
            if self.__watcher:
                self.__watcher.addPath(new_path)
        self._file_path = new_path

    def copy(self, new_path):
        """
        Copy the file to a new path
        """
        if self._exists():
            signal_handler = SignalFlowControl()
            # SIGNALL: WILL COPY TO, to warn folder to exist
            self.willCopyTo.emit(signal_handler,
                                 self._file_path,
                                 new_path)
            if signal_handler.stopped():
                return
            if os.path.exists(new_path):
                signal_handler = SignalFlowControl()
                self.willOverWrite.emit(signal_handler,
                                        self._file_path,
                                        new_path)
                if signal_handler.stopped():
                    return

            shutil.copy(self._file_path, new_path)

    def delete(self, force=False):
        """
        This deletes the object and closes the file.
        """
        # if created but exists this file migth to someone else
        self.close()
        if ((not self.__created) or force) and self._exists():
            DEBUG("Deleting our own NFile %s" % self._file_path)
            signal_handler = SignalFlowControl()
            self.willDelete.emit(signal_handler, self)
            if not signal_handler.stopped():
                if self.__watcher is not None:
                    self.__watcher.removePath(self._file_path)
                os.remove(self._file_path)

    def close(self, force_close=False):
        """
        Lets let people know we are going down so they can act upon
        As you can see close does nothing but let everyone know that we are
        not saved yet
        """
        DEBUG("About to close NFile")
        self.fileClosing.emit(self._file_path, force_close)

    def remove_watcher(self):
        if self.__watcher is not None:
            self.__watcher.removePath(self._file_path)
