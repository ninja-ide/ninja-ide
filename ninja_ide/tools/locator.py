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

import re
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
from ninja_ide.gui.ide import IDE
from ninja_ide.core.file_handling import file_manager
from ninja_ide.core import settings

from ninja_ide.tools.logger import NinjaLogger


logger = NinjaLogger('ninja_ide.tools.locator')

mapping_locations = {}


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


class Locator(QObject):
    """This class is used Go To Definition feature."""

    def __init__(self):
        QObject.__init__(self)
        self._thread = LocateThread()
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
            QMessageBox.information(main_container,
                self.tr("Definition Not Found"),
                self.tr("This Definition does not belong to this Project."))
        else:
            tool_dock = IDE.get_service("tools_dock")
            tool_dock.show_results(self._thread.results)

    def get_classes_from_project(self, projectPath):
        global mapping_locations
        filesFromProject = [filePath for filePath in
            mapping_locations if filePath.startswith(projectPath)]
        classes = [item
            for key in filesFromProject
            for item in mapping_locations[key]
            if item[0] == FILTERS['classes']]
        return classes


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


class LocateThread(QThread):

    def __init__(self):
        QThread.__init__(self)
        self.results = []
        self._cancel = False
        self.locations = []
        self.execute = self.go_to_definition
        self.dirty = False
        self._search = None
        self._isVariable = None

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
            global mapping_locations
            mapping_locations = {}
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
        self.execute()
        self._cancel = False
        self._search = None
        self._isVariable = None

    def locate_code(self):
        ide = IDE.get_service('ide')
        projects = ide.get_opened_projects()
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
                    self._grep_file_locate(one_file.absoluteFilePath(),
                        one_file.fileName())
                except Exception as reason:
                    logger.error(
                        '__locate_code_in_project, error: %r' % reason)
                    logger.error(
                        '__locate_code_in_project fail for file: %r' %
                        one_file.absoluteFilePath())

    def locate_file_code(self):
        file_name = file_manager.get_basename(self._file_path)
        try:
            self._grep_file_locate(self._file_path, file_name)
            self.dirty = True
            self.execute = self.locate_code
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
        self._search = None
        self._isVariable = None

    def get_locations(self):
        if self.dirty:
            self.convert_map_to_array()
            self.dirty = False
        return self.locations

    def get_this_file_locations(self, path):
        global mapping_locations
        thisFileLocations = mapping_locations.get(path, ())
        try:
            if not thisFileLocations:
                file_name = file_manager.get_basename(path)
                self._grep_file_locate(path, file_name)
                thisFileLocations = mapping_locations.get(path, ())
            thisFileLocations = sorted(thisFileLocations[1:],
                key=lambda item: item.name)
        except Exception as reason:
            logger.error('get_this_file_locations, error: %r' % reason)
        return thisFileLocations

    def convert_map_to_array(self):
        global mapping_locations
        self.locations = [x for location in mapping_locations
            for x in mapping_locations[location]]
        self.locations = sorted(self.locations, key=lambda item: item.name)

    def _grep_file_locate(self, file_path, file_name):
        #type - file_name - file_path
        global mapping_locations
        #TODO: Check if the last know state of the file is valid and load that
        exts = settings.SYNTAX.get('python')['extension']
        file_ext = file_manager.get_file_extension(file_path)
        if file_ext not in exts:
            mapping_locations[file_path] = [
                ResultItem(type=FILTERS['non-python'], name=file_name,
                    path=file_path, lineno=0)]
        else:
            mapping_locations[file_path] = [
                ResultItem(type=FILTERS['files'], name=file_name,
                        path=file_path, lineno=0)]
        #obtain a symbols handler for this file extension
        symbols_handler = settings.get_symbols_handler(file_ext)
        if symbols_handler is None:
            return
        results = []
        with open(file_path) as f:
            content = f.read()
            symbols = symbols_handler.obtain_symbols(content,
                filename=file_path)
            self.__parse_symbols(symbols, results, file_path)

        if results:
            mapping_locations[file_path] += results

    def __parse_symbols(self, symbols, results, file_path):
        if "classes" in symbols:
            self.__parse_class(symbols, results, file_path)
        if 'attributes' in symbols:
            self.__parse_attributes(symbols, results, file_path)
        if 'functions' in symbols:
            self.__parse_functions(symbols, results, file_path)

    def __parse_class(self, symbols, results, file_path):
        for claz in symbols['classes']:
            line_number = symbols['classes'][claz]['lineno'] - 1
            members = symbols['classes'][claz]['members']
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
        for attr in symbols['attributes']:
            line_number = symbols['attributes'][attr] - 1
            results.append(ResultItem(type=FILTERS['attribs'],
                name=attr, path=file_path,
                lineno=line_number))

    def __parse_functions(self, symbols, results, file_path):
        for func in symbols['functions']:
            line_number = symbols['functions'][func]['lineno'] - 1
            results.append(ResultItem(
                type=FILTERS['functions'], name=func,
                path=file_path, lineno=line_number))
            self.__parse_symbols(symbols['functions'][func]['functions'],
                    results, file_path)

    def get_symbols_for_class(self, file_path, clazzName):
        results = []
        with open(file_path) as f:
            content = f.read()
            ext = file_manager.get_file_extension(file_path)
            #obtain a symbols handler for this file extension
            symbols_handler = settings.get_symbols_handler(ext)
            symbols = symbols_handler.obtain_symbols(content,
                filename=file_path)
            self.__parse_symbols(symbols, results, file_path)
        return results

    def cancel(self):
        self._cancel = True
        self.results = []
        self.locations = []


class CodeLocatorWidget(QWidget):

    def __init__(self, parent):
        QWidget.__init__(self, parent)
        #Parent is StatusBar
        self.statusBar = parent
        self._thread = LocateThread()
        self._thread.execute = self._thread.locate_code

        hLocator = QHBoxLayout(self)
        hLocator.setContentsMargins(0, 0, 0, 0)
        self._btnClose = QPushButton(
            self.style().standardIcon(QStyle.SP_DialogCloseButton), '')
        self._btnGo = QPushButton(
            self.style().standardIcon(QStyle.SP_ArrowRight), self.tr('Go!'))
        self._completer = LocateCompleter(self)

        hLocator.addWidget(self._btnClose)
        hLocator.addWidget(self._completer)
        hLocator.addWidget(self._btnGo)

        self.connect(self._thread, SIGNAL("finished()"), self._cleanup)
        self.connect(self._thread, SIGNAL("terminated()"), self._cleanup)

    def _cleanup(self):
        self._thread.wait()

    def explore_code(self):
        self._thread.find_code_location()

    def explore_file_code(self, path):
        self._thread.find_file_code_location(path)

    def show_suggestions(self):
        self._completer.complete()

    def setVisible(self, val):
        if self._completer.frame:
            self._completer.frame.setVisible(False)
            self._completer.setText('')
        QWidget.setVisible(self, val)


class LocateItem(QListWidgetItem):

    """Create QListWidgetItem that contains the proper icon and file data."""

    icons = {FILTERS['functions']: resources.IMAGES['function'],
        FILTERS['files']: resources.IMAGES['tree-python'],
        FILTERS['classes']: resources.IMAGES['class'],
        FILTERS['non-python']: resources.IMAGES['tree-code'],
        FILTERS['attribs']: resources.IMAGES['attribute']}

    def __init__(self, data):
        QListWidgetItem.__init__(self, QIcon(self.icons[data.type]), "\n")
        self._data = data


class LocateWidget(QLabel):

    """Create a styled QLabel that will show the info."""

    def __init__(self, data):
        QLabel.__init__(self)
        self.name = data.name
        self.path = data.path
        locator_name = resources.CUSTOM_SCHEME.get('locator-name',
            resources.COLOR_SCHEME['locator-name'])
        locator_path = resources.CUSTOM_SCHEME.get('locator-path',
            resources.COLOR_SCHEME['locator-path'])
        self.setText("<span style='color: {2};'>{0}</span><br>"
            "<span style='font-size: 12px; color: {3};'>({1})</span>".format(
                data.name, data.path, locator_name, locator_path))

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


class LocateCompleter(QLineEdit):

    def __init__(self, parent):
        QLineEdit.__init__(self, parent)
        self._parent = parent
        self.__prefix = ''
        self.frame = PopupCompleter()
        self.filterPrefix = re.compile(r'^(@|<|>|-|!|\.|/|:)(\s)*')
        self.advancePrefix = re.compile(r'(@|<|>|-|!|/|:)')
        self.tempLocations = []
        self.setMinimumWidth(700)
        self.items_in_page = 0
        self.page_items_step = 10
        self._filterData = [None, None, None, None]
        self._line_jump = -1

        self.connect(self, SIGNAL("textChanged(QString)"),
            self.set_prefix)

        self.connect(self.frame.listWidget,
            SIGNAL("itemPressed(QListWidgetItem*)"), self._go_to_location)

    def set_prefix(self, prefix):
        """Set the prefix for the completer."""
        self.__prefix = prefix.lower()
        self._refresh_filter()

    def complete(self):
        self.frame.reload(self.filter())
        self.frame.setFixedWidth(self.width())
        point = self._parent.mapToGlobal(self.pos())
        self.frame.show()
        self.frame.move(point.x(), point.y() - self.frame.height())

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
        #Clean the objects from the listWidget
        inCurrentFile = False
        filterOptions = self.advancePrefix.split(self.__prefix.lstrip())
        if filterOptions[0] == '':
            del filterOptions[0]

        if len(filterOptions) > 2:
            if FILTERS['files'] in (filterOptions[1], filterOptions[2]):
                self._advanced_filter_by_file(filterOptions)
            else:
                self._advanced_filter(filterOptions)
            return self._create_list_widget_items(self.tempLocations)
        # Clear frame after advance filter because advance filter
        # ask for the first element in the popup
        self.tempLocations = []
        self.frame.clear()

        #if the user type any of the prefix
        if self.filterPrefix.match(self.__prefix):
            filterOption = self.__prefix[:1]
            main_container = IDE.get_service('main_container')
            #if the prefix is "." it means only the metadata of current file
            if main_container and filterOption == FILTERS['this-file']:
                inCurrentFile = True
                editorWidget = main_container.get_actual_editor()
                if editorWidget:
                    self.tempLocations = \
                        self._parent._thread.get_this_file_locations(
                            editorWidget.ID)
                    self.__prefix = self.__prefix[1:].lstrip()
                    self.tempLocations = [x for x in self.tempLocations
                        if x.comparison.lower().find(self.__prefix) > -1]
            elif filterOption == FILTERS['tabs']:
                tab1, tab2 = main_container.get_opened_documents()
                opened = tab1 + tab2
                self.tempLocations = [ResultItem(FILTERS['files'],
                    file_manager.get_basename(f[0]), f[0])
                    for f in opened]
                self.__prefix = self.__prefix[1:].lstrip()
            elif main_container and filterOption == FILTERS['lines']:
                editorWidget = main_container.get_actual_editor()
                self.tempLocations = [
                    x for x in self._parent._thread.get_locations()
                        if x.type == FILTERS['files'] and
                        x.path == editorWidget.ID]
                inCurrentFile = True
                if filterOptions[1].isdigit():
                    self._line_jump = int(filterOptions[1]) - 1
            else:
                #Is not "." filter by the other options
                self.tempLocations = [
                    x for x in self._parent._thread.get_locations()
                    if x.type == filterOption]
                #Obtain the user input without the filter prefix
                self.__prefix = self.__prefix[1:].lstrip()
        else:
            self.tempLocations = self._parent._thread.get_locations()

        if self.__prefix and not inCurrentFile:
            #if prefix (user search now) is not empty, filter words that1
            #contain the user input
            self.tempLocations = [x for x in self.tempLocations
                if x.comparison.lower().find(self.__prefix) > -1]

        return self._create_list_widget_items(self.tempLocations)

    def _advanced_filter(self, filterOptions):
        was_this_file = filterOptions[0] == FILTERS['this-file']
        if was_this_file:
            previous_filter = filterOptions[0]
            filterOptions[0] = FILTERS['files']
            main_container = IDE.get_service('main_container')
            editorWidget = None
            if main_container:
                editorWidget = main_container.get_actual_editor()
            if editorWidget:
                filterOptions.insert(1, editorWidget.ID)
            if previous_filter == FILTERS['lines']:
                filterOptions.insert(2, ':')
        elif filterOptions[0] in (
             FILTERS['classes'], FILTERS['files'], FILTERS['tabs']):
            currentItem = self.frame.listWidget.currentItem()
            if type(currentItem) is LocateItem:
                if currentItem._data.type in (FILTERS['files'],
                   FILTERS['classes']):
                    self._filterData = currentItem._data
            if filterOptions[0] == FILTERS['classes']:
                filterOptions.insert(0, FILTERS['files'])
                filterOptions.insert(1, self._filterData.path)
            else:
                filterOptions[1] = self._filterData.path
        if was_this_file and len(filterOptions) > 4:
            currentItem = self.frame.listWidget.currentItem()
            if type(currentItem) is LocateItem:
                if currentItem._data.type == FILTERS['classes']:
                    self._filterData = currentItem._data
        global mapping_locations
        filePath = filterOptions[1]

        moveIndex = 0
        if len(filterOptions) > 4 and filterOptions[2] == FILTERS['classes']:
            moveIndex = 2
            if self._filterData.type == FILTERS['classes']:
                self._classFilter = self._filterData.name
            symbols = self._parent._thread.get_symbols_for_class(filePath,
                self._classFilter)
            self.tempLocations = [x for x in symbols
                if x.type == filterOptions[4]]
        elif len(filterOptions) == 4 and filterOptions[2] == FILTERS['lines']:
            self.tempLocations = [
                x for x in self.tempLocations if x.path == filePath]
            if filterOptions[3].isdigit():
                self._line_jump = int(filterOptions[3]) - 1
                return
        else:
            self.tempLocations = [
                x for x in mapping_locations.get(filePath, [])
                if x.type == filterOptions[2]]
        moveIndex += 3
        if len(filterOptions) > moveIndex and filterOptions[moveIndex]:
            self.tempLocations = [x for x in self.tempLocations
              if x.comparison.lower().find(filterOptions[moveIndex]) > -1]

    def _advanced_filter_by_file(self, filterOptions):
        if filterOptions[1] == FILTERS['files']:
            index = 2
        else:
            index = 3
        self.tempLocations = [x for x in self.tempLocations
            if file_manager.get_basename(x.path).lower().find(
                filterOptions[index]) > -1]

    def _refresh_filter(self):
        has_text = len(self.text()) != 0
        self.frame.refresh(self.filter(), has_text)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            item = self.frame.listWidget.currentItem()
            self.setText(item._data.comparison)
            return

        QLineEdit.keyPressEvent(self, event)
        currentRow = self.frame.listWidget.currentRow()
        if event.key() == Qt.Key_Down:
            count = self.frame.listWidget.count()
            #If the current position is greater than the amount of items in
            #the list - 6, then try to fetch more items in the list.
            if currentRow >= (count - 6):
                locations = self._create_list_widget_items(self.tempLocations)
                self.frame.fetch_more(locations)
            #While the current position is lower that the list size go to next
            if currentRow != count - 1:
                self.frame.listWidget.setCurrentRow(
                    self.frame.listWidget.currentRow() + 1)
        elif event.key() == Qt.Key_Up:
            #while the current position is greater than 0, go to previous
            if currentRow > 0:
                self.frame.listWidget.setCurrentRow(
                    self.frame.listWidget.currentRow() - 1)
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            #If the user press enter, go to the item selected
            item = self.frame.listWidget.currentItem()
            self._go_to_location(item)

    def _go_to_location(self, item):
        if type(item) is LocateItem:
            self._open_item(item._data)
        self.emit(SIGNAL("hidden(PyQt_PyObject)"), self)

    def focusOutEvent(self, event):
        """Hide Popup on focus lost."""
        self.emit(SIGNAL("hidden(PyQt_PyObject)"), self)
        QLineEdit.focusOutEvent(self, event)

    def _open_item(self, data):
        """Open the item received."""
        main_container = IDE.get_service('main_container')
        if not main_container:
            return
        jump = data.lineno if self._line_jump != -1 else self._line_jump
        main_container.open_file(data.path, jump, None, True)


class PopupCompleter(QFrame):

    def __init__(self):
        QFrame.__init__(self, None, Qt.FramelessWindowHint | Qt.ToolTip)
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
        noFoundItem = self._create_help_item(resources.IMAGES['delete'],
                translations.TR_NO_RESULTS)
        self.listWidget.addItem(noFoundItem)

    def add_help(self):
        #Load help
        fileItem = self._create_help_item(resources.IMAGES['locate-file'],
                         translations.TR_ONLY_FILES)
        self.listWidget.addItem(fileItem)
        classItem = self._create_help_item(resources.IMAGES['locate-class'],
                        translations.TR_ONLY_CLASSES)
        self.listWidget.addItem(classItem)
        methodItem = self._create_help_item(
                        resources.IMAGES['locate-function'],
                        translations.TR_ONLY_METHODS)
        self.listWidget.addItem(methodItem)
        attributeItem = self._create_help_item(
                            resources.IMAGES['locate-attributes'],
                            translations.TR_ONLY_ATRIBUTES)
        self.listWidget.addItem(attributeItem)
        thisFileItem = self._create_help_item(
                    resources.IMAGES['locate-on-this-file'],
                    translations.TR_ONLY_CLASSES_METHODS)
        self.listWidget.addItem(thisFileItem)
        tabsItem = self._create_help_item(resources.IMAGES['locate-tab'],
                translations.TR_ONLY_CURRENT_TABS)
        self.listWidget.addItem(tabsItem)
        lineItem = self._create_help_item(resources.IMAGES['locate-line'],
                translations.TR_GO_TO_LINE)
        self.listWidget.addItem(lineItem)
        nonPythonItem = self._create_help_item(
                resources.IMAGES['locate-nonpython'],
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