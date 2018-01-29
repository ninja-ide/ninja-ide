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
from __future__ import print_function

import os
import sqlite3
import pickle
try:
    import Queue
except:
    import queue as Queue  # lint:ok

from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import (
    QObject,
    QThread,
    QDir,
    QFile,
    QTextStream
)

from ninja_ide import resources
from ninja_ide import translations
from ninja_ide.extensions import handlers
from ninja_ide.gui.ide import IDE
from ninja_ide.core.file_handling import file_manager
from ninja_ide.core import settings

from ninja_ide.tools.logger import NinjaLogger


logger = NinjaLogger('ninja_ide.tools.locator')

mapping_symbols = {}
files_paths = {}


# @ FILES
# < CLASSES
# > FUNCTIONS
# - MODULE ATTRIBUTES
# ! NO PYTHON FILES
# . SYMBOLS IN THIS FILE
# / TABS OPENED
# : LINE NUMBER
FILTERS = {
    'files': '@',
    'classes': '<',
    'functions': '>',
    'attribs': '-',
    'non-python': '!',
    'this-file': '.',
    'tabs': '/',
    'lines': ':'}


db_path = os.path.join(resources.NINJA_KNOWLEDGE_PATH, 'locator.db')


def _initialize_db():
    locator_db = sqlite3.connect(db_path)
    cur = locator_db.cursor()
    cur.execute("create table if not exists "
                "locator(path text PRIMARY KEY, stat integer, data blob)")
    locator_db.commit()
    locator_db.close()


# Initialize Database and open connection
_initialize_db()


# TODO: Clean non existent paths from the DB


class GoToDefinition(QObject):
    """This class is used Go To Definition feature."""

    def __init__(self):
        super(GoToDefinition, self).__init__()
        self._thread = LocateSymbolsThread()
        self._thread.finished.connect(self._load_results)
        # self.connect(self._thread, SIGNAL("finished()"), self._load_results)
        self._thread.finished.connect(self._cleanup)
        # self.connect(self._thread, SIGNAL("finished()"), self._cleanup)
        self._thread.terminated.connect(self._cleanup)
        # self.connect(self._thread, SIGNAL("terminated()"), self._cleanup)

    def _cleanup(self):
        self._thread.wait()

    def navigate_to(self, function, filePath, isVariable):
        self._thread.find(function, filePath, isVariable)

    def _load_results(self):
        main_container = IDE.get_service('main_container')
        if not main_container:
            return
        if len(self._thread.results) == 1:
            main_container.open_file(
                filename=self._thread.results[0][1],
                line=self._thread.results[0][2])
        elif len(self._thread.results) == 0:
            # TODO: Check imports
            QMessageBox.information(
                main_container,
                translations.TR_DEFINITION_NOT_FOUND,
                translations.TR_DEFINITION_NOT_FOUND_BODY)
        else:
            tool_dock = IDE.get_service("tools_dock")
            tool_dock.show_results(self._thread.results)


class ResultItem(object):
    """The Representation of each item found with the locator."""

    def __init__(self, symbol_type='', name='', path='', lineno=-1):
        if name:
            self.type = symbol_type  # Function, Class, etc
            self.name = name
            self.path = path
            self.lineno = lineno
            self.comparison = self.name
            index = self.name.find('(')
            if index != -1:
                self.comparison = self.name[:index]
        else:
            raise TypeError("name is not a string or unicode.")

    def __str__(self):
        return self.name

    def __len__(self):
        return len(self.name)

    def __iter__(self):
        for i in self.name:
            yield i

    def __getitem__(self, index):
        return self.name[index]


class LocateSymbolsThread(QThread):

    def __init__(self):
        super(LocateSymbolsThread, self).__init__()
        self.results = []
        self._cancel = False
        self.locations = []
        self.execute = None
        self.dirty = False
        self._search = None
        self._isVariable = None

        # Locator Knowledge
        self._locator_db = None

    def find(self, search, filePath, isVariable):
        self.cancel()
        self.execute = self.go_to_definition
        self._filePath = filePath
        self._search = search
        self._isVariable = isVariable
        self._cancel = False
        self.start()

    def find_code_location(self):
        self.cancel()
        self.wait()
        self._cancel = False
        if not self.isRunning():
            global mapping_symbols
            global files_paths
            mapping_symbols = {}
            files_paths = {}
            self.execute = self.locate_code
            self.start()

    def find_file_code_location(self, path):
        self._file_path = path
        if not self._file_path:
            return
        if not self.isRunning():
            self.execute = self.locate_file_code
            self.start()

    def run(self):
        self.results = []
        self.locations = []
        self.execute()
        if self._cancel:
            self.results = []
            self.locations = []
        self._cancel = False
        self._search = None
        self._isVariable = None
        if self._locator_db is not None:
            self._locator_db.commit()
            self._locator_db.close()
            self._locator_db = None

    def _save_file_symbols(self, path, stat, data):
        if self._locator_db is not None:
            pdata = pickle.dumps(data, pickle.HIGHEST_PROTOCOL)
            cur = self._locator_db.cursor()
            cur.execute("INSERT OR REPLACE INTO locator values (?, ?, ?)",
                        (path, stat, sqlite3.Binary(pdata)))
            self._locator_db.commit()

    def _get_file_symbols(self, path):
        if self._locator_db is not None:
            cur = self._locator_db.cursor()
            cur.execute("SELECT * FROM locator WHERE path=:path",
                        {'path': path})
            return cur.fetchone()

    def locate_code(self):
        self._locator_db = sqlite3.connect(db_path)
        ide = IDE.get_service('ide')
        projects = ide.filesystem.get_projects()
        if not projects:
            return
        projects = list(projects.values())
        for nproject in projects:
            if self._cancel:
                break
            current_dir = QDir(nproject.path)
            # Skip not readable dirs!
            if not current_dir.isReadable():
                continue

            queue_folders = Queue.Queue()
            queue_folders.put(current_dir)
            files_paths[nproject.path] = list()
            self.__locate_code_in_project(queue_folders, nproject)
        self.dirty = True
        self.get_locations()

    def __locate_code_in_project(self, queue_folders, nproject):
        file_filter = QDir.Files | QDir.NoDotAndDotDot | QDir.Readable
        dir_filter = QDir.Dirs | QDir.NoDotAndDotDot | QDir.Readable
        while not self._cancel and not queue_folders.empty():
            current_dir = QDir(queue_folders.get())
            # Skip not readable dirs!
            if not current_dir.isReadable():
                continue

            # Collect all sub dirs!
            current_sub_dirs = current_dir.entryInfoList(dir_filter)
            for one_dir in current_sub_dirs:
                queue_folders.put(one_dir.absoluteFilePath())

            # all files in sub_dir first apply the filters
            current_files = current_dir.entryInfoList(
                ['*{0}'.format(x) for x in nproject.extensions], file_filter)
            # process all files in current dir!
            global files_paths
            for one_file in current_files:
                try:
                    self._grep_file_symbols(one_file.absoluteFilePath(),
                                            one_file.fileName())
                    files_paths[nproject.path].append(
                        one_file.absoluteFilePath())
                except Exception as reason:
                    logger.error(
                        '__locate_code_in_project, error: %r' % reason)
                    logger.error(
                        '__locate_code_in_project fail for file: %r' %
                        one_file.absoluteFilePath())

    def locate_file_code(self):
        self._locator_db = sqlite3.connect(db_path)
        file_name = file_manager.get_basename(self._file_path)
        try:
            self._grep_file_symbols(self._file_path, file_name)
            self.dirty = True
        except Exception as reason:
            logger.error('locate_file_code, error: %r' % reason)

    def go_to_definition(self):
        self.dirty = True
        self.results = []
        locations = self.get_locations()
        if self._isVariable:
            preResults = [
                [file_manager.get_basename(x.path), x.path, x.lineno, '']
                for x in locations
                if (x.type == FILTERS['attribs']) and (x.name == self._search)]
        else:
            preResults = [
                [file_manager.get_basename(x.path), x.path, x.lineno, '']
                for x in locations
                if ((x.type == FILTERS['functions']) or
                    (x.type == FILTERS['classes'])) and
                   (x.name.startswith(self._search))]
        for data in preResults:
            file_object = QFile(data[1])
            if not file_object.open(QFile.ReadOnly):
                return

            stream = QTextStream(file_object)
            line_index = 0
            line = stream.readLine()
            while not self._cancel and not stream.atEnd():
                if line_index == data[2]:
                    data[3] = line
                    self.results.append(data)
                    break
                # take the next line!
                line = stream.readLine()
                line_index += 1

    def get_locations(self):
        if self.dirty:
            self.convert_map_to_array()
            self.dirty = False
        return self.locations

    def get_this_file_symbols(self, path):
        global mapping_symbols
        symbols = mapping_symbols.get(path, ())
        try:
            if not symbols:
                file_name = file_manager.get_basename(path)
                self._grep_file_symbols(path, file_name)
                symbols = mapping_symbols.get(path, ())
            symbols = sorted(symbols[1:], key=lambda item: item.name)
        except Exception as reason:
            logger.error('get_this_file_symbols, error: %r' % reason)
        return symbols

    def convert_map_to_array(self):
        global mapping_symbols
        self.locations = [x for location in mapping_symbols
                          for x in mapping_symbols[location]]
        self.locations = sorted(self.locations, key=lambda item: item.name)

    def _grep_file_symbols(self, file_path, file_name):
        # type - file_name - file_path
        global mapping_symbols
        exts = settings.SYNTAX.get('python')['extension']
        file_ext = file_manager.get_file_extension(file_path)
        if file_ext not in exts:
            mapping_symbols[file_path] = [
                ResultItem(symbol_type=FILTERS['non-python'], name=file_name,
                           path=file_path, lineno=-1)]
        else:
            mapping_symbols[file_path] = [
                ResultItem(symbol_type=FILTERS['files'], name=file_name,
                           path=file_path, lineno=-1)]
        data = self._get_file_symbols(file_path)
        # FIXME: stat not int
        mtime = int(os.stat(file_path).st_mtime)
        if data is not None and (mtime == int(data[1])):
            try:
                results = pickle.loads(data[2])
                mapping_symbols[file_path] += results
                return
            except:
                print("ResultItem couldn't be loaded, let's analyze it again'")
        # obtain a symbols handler for this file extension
        lang = settings.LANGUAGE_MAP.get(file_ext)
        symbols_handler = handlers.get_symbols_handler(lang)
        if symbols_handler is None:
            return
        results = []
        with open(file_path) as f:
            content = f.read()
            symbols = symbols_handler.obtain_symbols(
                content,
                filename=file_path)
            self.__parse_symbols(symbols, results, file_path)

        if results:
            self._save_file_symbols(file_path, mtime, results)
            mapping_symbols[file_path] += results

    def __parse_symbols(self, symbols, results, file_path):
        if "classes" in symbols:
            self.__parse_class(symbols, results, file_path)
        if 'attributes' in symbols:
            self.__parse_attributes(symbols, results, file_path)
        if 'functions' in symbols:
            self.__parse_functions(symbols, results, file_path)

    def __parse_class(self, symbols, results, file_path):
        clazzes = symbols['classes']
        for claz in clazzes:
            line_number = clazzes[claz]['lineno'] - 1
            members = clazzes[claz]['members']
            results.append(ResultItem(symbol_type=FILTERS['classes'],
                           name=claz, path=file_path,
                           lineno=line_number))
            if 'attributes' in members:
                for attr in members['attributes']:
                    line_number = members['attributes'][attr] - 1
                    results.append(ResultItem(symbol_type=FILTERS['attribs'],
                                   name=attr, path=file_path,
                                   lineno=line_number))
            if 'functions' in members:
                for func in members['functions']:
                    line_number = members['functions'][func]['lineno'] - 1
                    results.append(ResultItem(
                        symbol_type=FILTERS['functions'], name=func,
                        path=file_path, lineno=line_number))
                    self.__parse_symbols(
                        members['functions'][func]['functions'],
                        results, file_path)
            if 'classes' in members:
                self.__parse_class(members, results, file_path)

    def __parse_attributes(self, symbols, results, file_path):
        attributes = symbols['attributes']
        for attr in attributes:
            line_number = attributes[attr] - 1
            results.append(ResultItem(symbol_type=FILTERS['attribs'],
                           name=attr, path=file_path,
                           lineno=line_number))

    def __parse_functions(self, symbols, results, file_path):
        functions = symbols['functions']
        for func in functions:
            line_number = functions[func]['lineno'] - 1
            results.append(ResultItem(
                symbol_type=FILTERS['functions'], name=func,
                path=file_path, lineno=line_number))
            self.__parse_symbols(functions[func]['functions'],
                                 results, file_path)

    def get_symbols_for_class(self, file_path, clazzName):
        results = []
        with open(file_path) as f:
            content = f.read()
            ext = file_manager.get_file_extension(file_path)
            # obtain a symbols handler for this file extension
            symbols_handler = handlers.get_symbols_handler(ext)
            symbols = symbols_handler.obtain_symbols(content,
                                                     filename=file_path)
            self.__parse_symbols(symbols, results, file_path)
        return results

    def cancel(self):
        self._cancel = True
