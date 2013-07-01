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
from __future__ import unicode_literals

import sys
import os
import re
import threading
import shutil

from PyQt4 import QtCore

from ninja_ide.core import settings

if sys.version_info.major == 3:
    python3 = True
else:
    python3 = False


#Lock to protect the file's writing operation
file_store_content_lock = threading.Lock()


class NinjaIOException(Exception):
    """
    IO operation's exception
    """
    pass


class NinjaFileExistsException(Exception):
    """
    Try to override existing file without confirmation exception.
    """

    def __init__(self, filename=''):
        Exception.__init__(self, 'The file already exists.')
        self.filename = filename


def create_init_file(folderName):
    """Create a __init__.py file in the folder received."""
    if not os.path.isdir(folderName):
        raise NinjaIOException("The destination folder does not exist")
    name = os.path.join(folderName, '__init__.py')
    if file_exists(name):
        raise NinjaFileExistsException(name)
    f = open(name, 'w')
    f.flush()
    f.close()


def create_init_file_complete(folderName):
    """Create a __init__.py file in the folder received.

    This __init__.py will contain the information of the files inside
    this folder."""
    if not os.path.isdir(folderName):
        raise NinjaIOException("The destination folder does not exist")
    patDef = re.compile('^def .+')
    patClass = re.compile('^class .+')
    patExt = re.compile('.+\\.py')
    files = os.listdir(folderName)
    files = list(filter(patExt.match, files))
    files.sort()
    imports_ = []
    for f in files:
        read = open(os.path.join(folderName, f), 'r')
        imp = [re.split('\\s|\\(', line)[1] for line in read.readlines()
               if patDef.match(line) or patClass.match(line)]
        imports_ += ['from ' + f[:-3] + ' import ' + i for i in imp]
    name = os.path.join(folderName, '__init__.py')
    fi = open(name, 'w')
    for import_ in imports_:
        fi.write(import_ + '\n')
    fi.flush()
    fi.close()


def create_folder(folderName, add_init_file=True):
    """Create a new Folder inside the one received as a param."""
    if os.path.exists(folderName):
        raise NinjaIOException("The folder already exist")
    os.mkdir(folderName)
    if add_init_file:
        create_init_file(folderName)


def create_tree_folders(folderName):
    """Create a group of folders, one inside the other."""
    if os.path.exists(folderName):
        raise NinjaIOException("The folder already exist")
    os.makedirs(folderName)


def folder_exists(folderName):
    """Check if a folder already exists."""
    return os.path.isdir(folderName)


def file_exists(path, fileName=''):
    """Check if a file already exists."""
    if fileName != '':
        path = os.path.join(path, fileName)
    return os.path.isfile(path)


def _search_coding_line(txt):
    """Search a pattern like this: # -*- coding: utf-8 -*-."""
    coding_pattern = "coding[:=]\s*([-\w.]+)"
    pat_coding = re.search(coding_pattern, txt)
    if pat_coding and pat_coding.groups()[0] != 'None':
        return pat_coding.groups()[0]
    return None


def get_file_encoding(content):
    """Try to get the encoding of the file using the PEP 0263 rules
    search the first or the second line of the file
    Returns the encoding or the default UTF-8
    """
    encoding = None
    lines_to_check = content.split("\n", 2)
    for index in range(2):
        if len(lines_to_check) > index:
            line_encoding = _search_coding_line(lines_to_check[index])
            if line_encoding:
                encoding = line_encoding
                break
    #if not encoding is set then use UTF-8 as default
    if encoding is None:
        encoding = "UTF-8"
    return encoding


def read_file_content(fileName):
    """Read a file content, this function is used to load Editor content."""
    try:
        with open(fileName, 'rU') as f:
            content = f.read()
    except IOError as reason:
        raise NinjaIOException(reason)
    except:
        raise
    return content


def get_basename(fileName):
    """Get the name of a file or folder specified in a path."""
    if fileName.endswith(os.path.sep):
        fileName = fileName[:-1]
    return os.path.basename(fileName)


def get_folder(fileName):
    """Get the name of the folder containing the file or folder received."""
    return os.path.dirname(fileName)


def store_file_content(fileName, content, addExtension=True, newFile=False):
    """Save content on disk with the given file name."""
    if fileName == '':
        raise Exception()
    ext = (os.path.splitext(fileName)[-1])[1:]
    if ext == '' and addExtension:
        fileName += '.py'
    if newFile and file_exists(fileName):
        raise NinjaFileExistsException(fileName)
    try:
        flags = QtCore.QIODevice.WriteOnly | QtCore.QIODevice.Truncate
        f = QtCore.QFile(fileName)
        if settings.use_platform_specific_eol():
            flags |= QtCore.QIODevice.Text

        if not f.open(flags):
            raise NinjaIOException(f.errorString())

        stream = QtCore.QTextStream(f)
        encoding = get_file_encoding(content)
        if encoding:
            stream.setCodec(encoding)

        encoded_stream = stream.codec().fromUnicode(content)
        f.write(encoded_stream)
        f.flush()
        f.close()
    except:
        raise
    return os.path.abspath(fileName)


def open_project(path):
    """Return a dict structure containing the info inside a folder."""
    if not os.path.exists(path):
        raise NinjaIOException("The folder does not exist")
    d = {}
    for root, dirs, files in os.walk(path, followlinks=True):
        d[root] = [[f for f in files
                    if (os.path.splitext(f.lower())[-1]) in
                    settings.SUPPORTED_EXTENSIONS],
                   dirs]
    return d


def open_project_with_extensions(path, extensions):
    """Return a dict structure containing the info inside a folder.

    This function uses the extensions specified by each project."""
    if not os.path.exists(path):
        raise NinjaIOException("The folder does not exist")
    d = {}
    for root, dirs, files in os.walk(path, followlinks=True):
        d[root] = [[f for f in files
                    if (os.path.splitext(f.lower())[-1]) in extensions or
                    '.*' in extensions],
                   dirs]
    return d


def delete_file(path, fileName=None):
    """Delete the proper file.

    If fileName is None, path and fileName are joined to create the
    complete path, otherwise path is used to delete the file."""
    if fileName:
        path = os.path.join(path, fileName)
    if os.path.isfile(path):
        os.remove(path)


def delete_folder(path, fileName=None):
    """Delete the proper folder."""
    if fileName:
        path = os.path.join(path, fileName)
    if os.path.isdir(path):
        shutil.rmtree(path)


def rename_file(old, new):
    """Rename a file, changing its name from 'old' to 'new'."""
    if os.path.isfile(old):
        if file_exists(new):
            raise NinjaFileExistsException(new)
        os.rename(old, new)
        return new
    return ''


def get_file_extension(fileName):
    """Get the file extension in the form of: 'py'"""
    return os.path.splitext(fileName.lower())[-1][1:]


def get_file_name(fileName):
    """Get the file name, without the extension."""
    return os.path.splitext(fileName)[0]


def get_module_name(fileName):
    """Get the name of the file without the extension."""
    module = os.path.basename(fileName)
    return (os.path.splitext(module)[0])


def convert_to_relative(basePath, fileName):
    """Convert a absolut path to relative based on its start with basePath."""
    if fileName.startswith(basePath):
        fileName = fileName.replace(basePath, '')
        if fileName.startswith(os.path.sep):
            fileName = fileName[1:]
    return fileName


def create_path(*args):
    """Join the paths provided in order to create an absolut path."""
    return os.path.join(*args)


def belongs_to_folder(path, fileName):
    """Determine if fileName is located under path structure."""
    if not path.endswith(os.path.sep):
        path += os.path.sep
    return fileName.startswith(path)


def get_last_modification(fileName):
    """Get the last time the file was modified."""
    return QtCore.QFileInfo(fileName).lastModified()


def has_write_permission(fileName):
    """Check if the file has writing permissions."""
    return os.access(fileName, os.W_OK)


def check_for_external_modification(fileName, old_mtime):
    """Check if the file was modified outside ninja."""
    new_modification_time = get_last_modification(fileName)
    #check the file mtime attribute calling os.stat()
    if new_modification_time > old_mtime:
        return True
    return False


def get_files_from_folder(folder, ext):
    """Get the files in folder with the specified extension."""
    try:
        filesExt = os.listdir(folder)
    except:
        filesExt = []
    filesExt = [f for f in filesExt if f.endswith(ext)]
    return filesExt


def is_supported_extension(filename, extensions=None):
    if extensions is None:
        extensions = settings.SUPPORTED_EXTENSIONS
    if os.path.splitext(filename.lower())[-1] in extensions:
        return True
    return False
