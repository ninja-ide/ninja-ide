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

import os
import re
import sqlite3
import pickle
try:
    import Queue
except:
    import queue as Queue  # lint:ok

from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QBrush
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QFrame
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QListWidgetItem
from PyQt4.QtGui import QListWidget
from PyQt4.QtGui import QStyle
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QPushButton
from PyQt4.QtCore import QObject
from PyQt4.QtCore import QSize
from PyQt4.QtCore import QThread
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QDir
from PyQt4.QtCore import QFile
from PyQt4.QtCore import QTextStream
from PyQt4.QtCore import SIGNAL

from ninja_ide import resources
from ninja_ide import translations
from ninja_ide.extensions import handlers
from ninja_ide.gui.ide import IDE
from ninja_ide.core.file_handling import file_manager
from ninja_ide.core import settings

from ninja_ide.tools.logger import NinjaLogger


logger = NinjaLogger('ninja_ide.tools.locator')

mapping_symbols = {}


#@ FILES
#< CLASSES
#> FUNCTIONS
#- MODULE ATTRIBUTES
#! NO PYTHON FILES
#. SYMBOLS IN THIS FILE
#/ TABS OPENED
#: LINE NUMBER
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
        "locator(path text, stat integer, data blob)")
    locator_db.commit()
    locator_db.close()


# Initialize Database and open connection
_initialize_db()


#TODO: Clean non existent paths from the DB


class GoToDefinition(QObject):
    """This class is used Go To Definition feature."""

    def __init__(self):
        super(GoToDefinition, self).__init__()
        self._thread = LocateSymbolsThread()
        self.connect(self._thread, SIGNAL("finished()"), self._load_results)
        self.connect(self._thread, SIGNAL("finished()"), self._cleanup)
        self.connect(self._thread, SIGNAL("terminated()"), self._cleanup)

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
                cursorPosition=self._thread.results[0][2],
                positionIsLineNumber=True)
        elif len(self._thread.results) == 0:
            #TODO: Check imports
            QMessageBox.information(main_container,
                translations.TR_DEFINITION_NOT_FOUND,
                translations.TR_DEFINITION_NOT_FOUND_BODY)
        else:
            tool_dock = IDE.get_service("tools_dock")
            tool_dock.show_results(self._thread.results)


class ResultItem(object):
    """The Representation of each item found with the locator."""

    def __init__(self, type='', name='', path='', lineno=-1):
        if name:
            self.type = type  # Function, Class, etc
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
        self._cancel = False
        if not self.isRunning():
            global mapping_symbols
            mapping_symbols = {}
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
            cur.execute("INSERT INTO locator values (?, ?, ?)",
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
        for path in projects:
            if self._cancel:
                break
            nproject = projects[path]
            current_dir = QDir(nproject.path)
            #Skip not readable dirs!
            if not current_dir.isReadable():
                continue

            queue_folders = Queue.Queue()
            queue_folders.put(current_dir)
            self.__locate_code_in_project(queue_folders, nproject)
        self.dirty = True
        self.get_locations()

    def __locate_code_in_project(self, queue_folders, nproject):
        file_filter = QDir.Files | QDir.NoDotAndDotDot | QDir.Readable
        dir_filter = QDir.Dirs | QDir.NoDotAndDotDot | QDir.Readable
        while not self._cancel and not queue_folders.empty():
            current_dir = QDir(queue_folders.get())
            #Skip not readable dirs!
            if not current_dir.isReadable():
                continue

            #Collect all sub dirs!
            current_sub_dirs = current_dir.entryInfoList(dir_filter)
            for one_dir in current_sub_dirs:
                queue_folders.put(one_dir.absoluteFilePath())

            #all files in sub_dir first apply the filters
            current_files = current_dir.entryInfoList(
                ['*{0}'.format(x) for x in nproject.extensions], file_filter)
            #process all files in current dir!
            for one_file in current_files:
                try:
                    self._grep_file_symbols(one_file.absoluteFilePath(),
                        one_file.fileName())
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
                #take the next line!
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
        #type - file_name - file_path
        global mapping_symbols
        exts = settings.SYNTAX.get('python')['extension']
        file_ext = file_manager.get_file_extension(file_path)
        if file_ext not in exts:
            mapping_symbols[file_path] = [
                ResultItem(type=FILTERS['non-python'], name=file_name,
                    path=file_path, lineno=-1)]
        else:
            mapping_symbols[file_path] = [
                ResultItem(type=FILTERS['files'], name=file_name,
                        path=file_path, lineno=-1)]
        data = self._get_file_symbols(file_path)
        mtime = int(os.stat(file_path).st_mtime)
        if data is not None and (mtime == int(data[1])):
            results = pickle.loads(str(data[2]))
            mapping_symbols[file_path] += results
            return
        #obtain a symbols handler for this file extension
        symbols_handler = handlers.get_symbols_handler(file_ext)
        if symbols_handler is None:
            return
        results = []
        with open(file_path) as f:
            content = f.read()
            symbols = symbols_handler.obtain_symbols(content,
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
            results.append(ResultItem(type=FILTERS['classes'],
                name=claz, path=file_path,
                lineno=line_number))
            if 'attributes' in members:
                for attr in members['attributes']:
                    line_number = members['attributes'][attr] - 1
                    results.append(ResultItem(type=FILTERS['attribs'],
                        name=attr, path=file_path,
                        lineno=line_number))
            if 'functions' in members:
                for func in members['functions']:
                    line_number = members['functions'][func]['lineno'] - 1
                    results.append(ResultItem(
                        type=FILTERS['functions'], name=func,
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
            results.append(ResultItem(type=FILTERS['attribs'],
                name=attr, path=file_path,
                lineno=line_number))

    def __parse_functions(self, symbols, results, file_path):
        functions = symbols['functions']
        for func in functions:
            line_number = functions[func]['lineno'] - 1
            results.append(ResultItem(
                type=FILTERS['functions'], name=func,
                path=file_path, lineno=line_number))
            self.__parse_symbols(functions[func]['functions'],
                    results, file_path)

    def get_symbols_for_class(self, file_path, clazzName):
        results = []
        with open(file_path) as f:
            content = f.read()
            ext = file_manager.get_file_extension(file_path)
            #obtain a symbols handler for this file extension
            symbols_handler = handlers.get_symbols_handler(ext)
            symbols = symbols_handler.obtain_symbols(content,
                filename=file_path)
            self.__parse_symbols(symbols, results, file_path)
        return results

    def cancel(self):
        self._cancel = True


class CodeLocatorWidget(QWidget):

    def __init__(self, parent=None):
        super(CodeLocatorWidget, self).__init__(parent)
        #Parent is StatusBar
        self.locate_symbols = LocateSymbolsThread()

        hLocator = QHBoxLayout(self)
        hLocator.setContentsMargins(0, 0, 0, 0)
        self._btnClose = QPushButton(
            self.style().standardIcon(QStyle.SP_DialogCloseButton), '')
        self._completer = LocatorCompleter(self)

        hLocator.addWidget(self._btnClose)
        hLocator.addWidget(self._completer)

        self.connect(self.locate_symbols, SIGNAL("finished()"), self._cleanup)
        self.connect(self.locate_symbols, SIGNAL("terminated()"),
            self._cleanup)
        self.connect(self._completer, SIGNAL("hidden()"),
            lambda: self.emit(SIGNAL("hidden()")))

    def _cleanup(self):
        self.locate_symbols.wait()

    def explore_code(self):
        self.locate_symbols.find_code_location()

    def explore_file_code(self, path):
        self.locate_symbols.find_file_code_location(path)

    def show_suggestions(self):
        self._completer.setFocus()
        self._completer.complete()

    def setVisible(self, val):
        if not val:
            self._completer.popup.setVisible(False)
            self._completer.setText('')
        super(CodeLocatorWidget, self).setVisible(val)


class LocateItem(QListWidgetItem):

    """Create QListWidgetItem that contains the proper icon and file data."""

    icons = {FILTERS['functions']: ":img/function",
        FILTERS['files']: ":img/tree-python",
        FILTERS['classes']: ":img/class",
        FILTERS['non-python']: ":img/tree-code",
        FILTERS['attribs']: ":img/attribute"}

    def __init__(self, data):
        super(LocateItem, self).__init__(QIcon(self.icons[data.type]), "\n")
        self.data = data


class LocateWidget(QLabel):

    """Create a styled QLabel that will show the info."""

    def __init__(self, data):
        super(LocateWidget, self).__init__()
        self.name = data.name
        self.path = data.path
        self.set_not_selected()

    def set_selected(self):
        locator_name = resources.CUSTOM_SCHEME.get('locator-name-selected',
            resources.COLOR_SCHEME['locator-name-selected'])
        locator_path = resources.CUSTOM_SCHEME.get('locator-path-selected',
            resources.COLOR_SCHEME['locator-path-selected'])
        self.setText("<span style='color: {2};'>{0}</span><br>"
            "<span style='font-size: 12px; color: {3};'>({1})</span>".format(
                self.name, self.path, locator_name, locator_path))

    def set_not_selected(self):
        locator_name = resources.CUSTOM_SCHEME.get('locator-name',
            resources.COLOR_SCHEME['locator-name'])
        locator_path = resources.CUSTOM_SCHEME.get('locator-path',
            resources.COLOR_SCHEME['locator-path'])
        self.setText("<span style='color: {2};'>{0}</span><br>"
            "<span style='font-size: 12px; color: {3};'>({1})</span>".format(
                self.name, self.path, locator_name, locator_path))


class LocatorCompleter(QLineEdit):

    def __init__(self, parent):
        super(LocatorCompleter, self).__init__(parent)
        self._parent = parent
        self.__prefix = ''
        self.popup = PopupCompleter()
        self.filterPrefix = re.compile(r'(@|<|>|-|!|\.|/|:)')
        self.tempLocations = []
        self.setMinimumWidth(700)
        self.items_in_page = 0
        self.page_items_step = 10
        self._line_jump = -1

        self._filter_actions = {
            '@': self._filter_generic,
            '<': self._filter_generic,
            '>': self._filter_generic,
            '-': self._filter_generic,
            '!': self._filter_generic,
            '.': self._filter_this_file,
            '/': self._filter_tabs,
            ':': self._filter_lines
        }

        self.connect(self, SIGNAL("textChanged(QString)"),
            self.set_prefix)

        self.connect(self.popup.listWidget,
            SIGNAL("itemPressed(QListWidgetItem*)"), self._go_to_location)

    def set_prefix(self, prefix):
        """Set the prefix for the completer."""
        self.__prefix = prefix.lower()
        self._refresh_filter()

    def complete(self):
        self.popup.reload(self.filter())
        self.popup.setFixedWidth(self.width())
        point = self._parent.mapToGlobal(self.pos())
        self.popup.show()
        self.popup.move(point.x(), point.y() - self.popup.height())

    def _create_list_widget_items(self, locations):
        """Create a list of items (using pages for results to speed up)."""
        #The list is regenerated when the locate metadata is updated
        #for example: open project, etc.
        #Create the list items
        begin = self.items_in_page
        self.items_in_page += self.page_items_step
        locations_view = [(LocateItem(x), LocateWidget(x))
            for x in locations[begin:self.items_in_page]]
        return locations_view

    def filter(self):
        self._line_jump = -1
        self.items_in_page = 0

        filterOptions = self.filterPrefix.split(self.__prefix.lstrip())
        if filterOptions[0] == '':
            del filterOptions[0]

        index = 0
        while index < len(filterOptions):
            filter_action = self._filter_actions.get(filterOptions[index])
            if filter_action is None:
                break
            index = filter_action(filterOptions, index)
        if len(filterOptions) == 0:
            self.tempLocations = self._parent.locate_symbols.get_locations()
        return self._create_list_widget_items(self.tempLocations)

    def _filter_generic(self, filterOptions, index):
        at_start = (index == 0)
        if at_start:
            self.tempLocations = [
                x for x in self._parent.locate_symbols.get_locations()
                    if x.type == filterOptions[0] and
                    x.comparison.lower().find(filterOptions[1]) > -1]
        else:
            currentItem = self.popup.listWidget.currentItem()
            filter_data = None
            if type(currentItem) is LocateItem:
                filter_data = currentItem.data
            if filterOptions[index - 2] == FILTERS['classes'] and filter_data:
                symbols = self._parent.locate_symbols.get_symbols_for_class(
                    filter_data.path, filter_data.name)
                self.tempLocations = symbols
            elif filter_data:
                global mapping_symbols
                self.tempLocations = mapping_symbols.get(filter_data.path, [])
            self.tempLocations = [x for x in self.tempLocations
                    if x.type == filterOptions[index] and
                    x.comparison.lower().find(filterOptions[index + 1]) > -1]
        return index + 2

    def _filter_this_file(self, filterOptions, index):
        at_start = (index == 0)
        if at_start:
            main_container = IDE.get_service('main_container')
            editorWidget = None
            if main_container:
                editorWidget = main_container.get_current_editor()
            index += 2
            if editorWidget:
                exts = settings.SYNTAX.get('python')['extension']
                file_ext = file_manager.get_file_extension(
                    editorWidget.file_path)
                if file_ext in exts:
                    filterOptions.insert(0, FILTERS['files'])
                else:
                    filterOptions.insert(0, FILTERS['non-python'])
                filterOptions.insert(1, editorWidget.file_path)
                self.tempLocations = \
                    self._parent.locate_symbols.get_this_file_symbols(
                        editorWidget.file_path)
                search = filterOptions[index + 1].lstrip()
                self.tempLocations = [x for x in self.tempLocations
                    if x.comparison.lower().find(search) > -1]
        else:
            del filterOptions[index + 1]
            del filterOptions[index]
        return index

    def _filter_tabs(self, filterOptions, index):
        at_start = (index == 0)
        if at_start:
            ninjaide = IDE.get_service('ide')
            opened = ninjaide.filesystem.get_files()
            self.tempLocations = [ResultItem(FILTERS['files'],
                opened[f].file_name, opened[f].file_path) for f in opened]
            index += 2
        else:
            del filterOptions[index + 1]
            del filterOptions[index]
        return index

    def _filter_lines(self, filterOptions, index):
        at_start = (index == 0)
        if at_start:
            main_container = IDE.get_service('main_container')
            editorWidget = None
            if main_container:
                editorWidget = main_container.get_current_editor()
            index = 2
            if editorWidget:
                exts = settings.SYNTAX.get('python')['extension']
                file_ext = file_manager.get_file_extension(
                    editorWidget.file_path)
                if file_ext in exts:
                    filterOptions.insert(0, FILTERS['files'])
                else:
                    filterOptions.insert(0, FILTERS['non-python'])
                filterOptions.insert(1, editorWidget.file_path)
            self.tempLocations = [
                x for x in self._parent.locate_symbols.get_locations()
                    if x.type == filterOptions[0] and
                    x.path == filterOptions[1]]
        if filterOptions[index + 1].isdigit():
            self._line_jump = int(filterOptions[index + 1]) - 1
        return index + 2

    def _refresh_filter(self):
        has_text = len(self.text()) != 0
        self.popup.refresh(self.filter(), has_text)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            item = self.popup.listWidget.currentItem()
            self.setText(item.data.comparison)
            return

        super(LocatorCompleter, self).keyPressEvent(event)
        currentRow = self.popup.listWidget.currentRow()
        if event.key() == Qt.Key_Down:
            count = self.popup.listWidget.count()
            #If the current position is greater than the amount of items in
            #the list - 6, then try to fetch more items in the list.
            if currentRow >= (count - 6):
                locations = self._create_list_widget_items(self.tempLocations)
                self.popup.fetch_more(locations)
            #While the current position is lower that the list size go to next
            if currentRow != count - 1:
                self.popup.listWidget.setCurrentRow(
                    self.popup.listWidget.currentRow() + 1)
        elif event.key() == Qt.Key_Up:
            #while the current position is greater than 0, go to previous
            if currentRow > 0:
                self.popup.listWidget.setCurrentRow(
                    self.popup.listWidget.currentRow() - 1)
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            #If the user press enter, go to the item selected
            item = self.popup.listWidget.currentItem()
            self._go_to_location(item)

    def _go_to_location(self, item):
        if type(item) is LocateItem:
            self._open_item(item.data)
        self.emit(SIGNAL("hidden()"))

    def focusOutEvent(self, event):
        """Hide Popup on focus lost."""
        self.emit(SIGNAL("hidden()"))
        super(LocatorCompleter, self).focusOutEvent(event)

    def _open_item(self, data):
        """Open the item received."""
        main_container = IDE.get_service('main_container')
        if not main_container:
            return
        jump = data.lineno if self._line_jump == -1 else self._line_jump
        main_container.open_file(data.path, jump, None, True)


class PopupCompleter(QFrame):

    def __init__(self):
        super(PopupCompleter, self).__init__(
            None, Qt.FramelessWindowHint | Qt.ToolTip)
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        self.listWidget = QListWidget()
        self.listWidget.setMinimumHeight(350)
        vbox.addWidget(self.listWidget)

        self.listWidget.currentItemChanged.connect(self._repaint_items)

    def _repaint_items(self, current, previous):
        if current is not None:
            widget = self.listWidget.itemWidget(current)
            if widget is not None:
                widget.set_selected()
        if previous is not None:
            widget = self.listWidget.itemWidget(previous)
            if widget is not None:
                widget.set_not_selected()

    def reload(self, model):
        """Reload the data of the Popup Completer, and restart the state."""
        self.listWidget.clear()
        self.add_help()
        for item in model:
            self.listWidget.addItem(item[0])
            self.listWidget.setItemWidget(item[0], item[1])
        self.listWidget.setCurrentRow(8)

    def clear(self):
        """Remove all the items of the list (deleted), and reload the help."""
        self.listWidget.clear()

    def refresh(self, model, has_text=True):
        """Refresh the list when the user search for some word."""
        self.listWidget.clear()
        if not has_text:
            self.add_help()
        for item in model:
            self.listWidget.addItem(item[0])
            self.listWidget.setItemWidget(item[0], item[1])
        if model:
            self.listWidget.setCurrentItem(model[0][0])
        else:
            self.add_no_found()

    def fetch_more(self, model):
        """Add more items to the list on user scroll."""
        for item in model:
            self.listWidget.addItem(item[0])
            self.listWidget.setItemWidget(item[0], item[1])

    def add_no_found(self):
        """Load no results found message"""
        noFoundItem = self._create_help_item(":img/delete",
                translations.TR_NO_RESULTS)
        self.listWidget.addItem(noFoundItem)

    def add_help(self):
        #Load help
        fileItem = self._create_help_item(":img/locate-file",
                         translations.TR_ONLY_FILES)
        self.listWidget.addItem(fileItem)
        classItem = self._create_help_item(":img/locate-class",
                        translations.TR_ONLY_CLASSES)
        self.listWidget.addItem(classItem)
        methodItem = self._create_help_item(
                        ":img/locate-function",
                        translations.TR_ONLY_METHODS)
        self.listWidget.addItem(methodItem)
        attributeItem = self._create_help_item(
                            ":img/locate-attributes",
                            translations.TR_ONLY_ATRIBUTES)
        self.listWidget.addItem(attributeItem)
        thisFileItem = self._create_help_item(
                    ":img/locate-on-this-file",
                    translations.TR_ONLY_CLASSES_METHODS)
        self.listWidget.addItem(thisFileItem)
        tabsItem = self._create_help_item(":img/locate-tab",
                translations.TR_ONLY_CURRENT_EDITORS)
        self.listWidget.addItem(tabsItem)
        lineItem = self._create_help_item(":img/locate-line",
                translations.TR_GO_TO_LINE)
        self.listWidget.addItem(lineItem)
        nonPythonItem = self._create_help_item(
                ":img/locate-nonpython",
                translations.TR_ONLY_NON_PYTHON)
        self.listWidget.addItem(nonPythonItem)

    def _create_help_item(self, image, text):
        Item = QListWidgetItem(QIcon(image), text)
        font = Item.font()
        font.setBold(True)
        Item.setSizeHint(QSize(20, 30))
        Item.setBackground(QBrush(Qt.lightGray))
        Item.setForeground(QBrush(Qt.black))
        Item.setFont(font)
        return Item