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
from PyQt4.QtCore import QObject, QFile, QIODevice, QTextStream, SIGNAL

#FIXME: Obtain these form a getter
from ninja_ide.core import settings
from ninja_ide.tools.utils import SignalFlowControl
from file_manager import NinjaIOException, NinjaNoFileNameException, \
get_file_encoding

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
    file when the watched, that should deppend on it notifies a change.
"""


class NFile(QObject):
    """
    """

    def __init__(self, path=None):
        """
        """
        self._file_path = path
        self.__created = False
        super(NFile, self).__init__()
        if not self._exists():
            self.__created = True

    def _exists(self):
        """
        Check if we have been created with a path and if such path exists
        In case there is no path, we are most likely a new file.
        """
        file_exists = False
        if self._file_path and os.path.exists(self._file_path):
            file_exists = True
        return file_exists

    def save(self, content, path=None, copy=False):
        """
        Write a temprorary file with .tnj extension and copy it over the
        original one.
        .nsf = Ninja Swap File
        #FIXME: Where to locate addExtension, does not fit here
        """
        save_path = path and path or self._file_path
        if not copy:
            self._file_path = save_path

        if not save_path:
            raise NinjaNoFileNameException("I am asked to write a "
                                "file but no one told me where")
        swap_save_path = u"%s.nsp" % save_path

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
        #SIGNAL: Will save (temp, definitive) to warn folder to do something
        self.emit(SIGNAL("willSave(QString, QString)"), swap_save_path,
                                                        save_path)
        shutil.move(swap_save_path, save_path)
        if not (path and copy):
            self.reset_state()

    def reset_state(self):
        """
        #FIXE: to have a ref to changed I need to have the doc here
        """
        self._created = False

    def read(self, path=None):
        """
        Read the file or fail
        """
        open_path = path and path or self._file_path
        self._file_path = open_path
        if not self._file_path:
            raise NinjaNoFileNameException("I am asked to read a "
                                    "file but no one told me from where")
        try:
            with open(open_path, 'rU') as f:
                content = f.read()
        except IOError as reason:
            raise NinjaIOException(reason)
        return content

    def move(self, new_path):
        """
        Phisically move the file
        """
        if self._exists():
            signal_handler = SignalFlowControl()
            #SIGNALL: WILL MOVE TO, to warn folder to exist
            self.emit(SIGNAL("willMove(Qt_PyQtObject, QString, QString)"),
                                                            signal_handler,
                                                            self._file_path,
                                                            new_path)
            if signal_handler.stopped():
                return
            if os.path.exists(new_path):
                signal_handler = SignalFlowControl()
                self.emit(
                    SIGNAL("willOverWrite(Qt_PyQtObject, QString, QString)"),
                                    signal_handler, self._file_path, new_path)
                if signal_handler.stopped():
                    return

            shutil.move(self._file_path, new_path)
        self._file_path = new_path
        return

    def copy(self, new_path):
        """
        Copy the file to a new path
        """
        raise NotImplementedError("Have not yet found use for this")

    def delete(self, force=False):
        """
        This deletes the object and closes the file.
        """
        #if created but exists this file migth to someone else
        self.close()
        if ((not self._created) or force) and self._exists():
            DEBUG("Deleting our own NFile %s" % self._file_path)
            signal_handler = SignalFlowControl()
            self.emit(SIGNAL("willDelete(PyQt_PyObject, PyQt_PyObject)"),
                                                        signal_handler, self)
            if not signal_handler.stopped():
                os.remove(self._file_path)

    def close(self):
        """
        Lets let people know we are going down so they can act upon
        As you can see close does nothing but let everyone know that we are
        not saved yet
        """
        DEBUG("About to close NFile")
        if self._created:
            self.emit(SIGNAL("neverSavedFileClosing(QString)"),
                        self._file_path)
        else:
            self.emit(SIGNAL("fileClosing(QString)"), self._file_path)
