# -*- coding: utf-8 -*-
from __future__ import absolute_import

import re
import Queue

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
from ninja_ide.gui.explorer import explorer_container
from ninja_ide.gui.misc import misc_container
from ninja_ide.gui.main_panel import main_container
from ninja_ide.core import file_manager
from ninja_ide.core import settings
from ninja_ide.tools import json_manager


mapping_locations = {}


#@ FILES
#< CLASSES
#> FUNCTIONS
#- MODULE ATTRIBUTES
#! NO PYTHON FILES
#. SYMBOLS IN THIS FILE
FILTERS = {
    'files': '@',
    'classes': '<',
    'functions': '>',
    'attribs': '-',
    'non-python': '!',
    'this-file': '.'}


class Locator(QObject):

    def __init__(self):
        QObject.__init__(self)
        self._thread = LocateThread()
        self.connect(self._thread, SIGNAL("finished()"), self._load_results)

    def navigate_to(self, function, filePath, isVariable):
        self._thread.find(function, filePath, isVariable)

    def _load_results(self):
        if len(self._thread.results) == 1:
            main_container.MainContainer().open_file(
                fileName=self._thread.results[0][1],
                cursorPosition=self._thread.results[0][2],
                positionIsLineNumber=True)
        elif len(self._thread.results) == 0:
            QMessageBox.information(main_container.MainContainer(),
                self.tr("Definition Not Found"),
                self.tr("This Definition does not belong to this Project."))
        else:
            misc_container.MiscContainer().show_results(self._thread.results)

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

    def __init__(self, type='', name='', path='', lineno=-1):
        if isinstance(name, str) or isinstance(name, unicode):
            self.type = type
            self.name = name
            self.path = path
            self.lineno = lineno
        else:
            raise TypeError("name is not a string or unicode.")

    def __str__(self):
        return self.data['name']

    def __len__(self):
        return len(self.data['name'])

    def __iter__(self):
        for i in self.data['name']:
            yield i

    def __getitem__(self, index):
        return self.data['name'][index]


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
        self._filePath = filePath
        self._search = search
        self._isVariable = isVariable
        self._cancel = False
        self.start()

    def find_code_location(self):
        self.cancel()
        self._cancel = False
        function_ = r'^(\s)*def(\s)+(\w)+(\s)*\(.*'
        class_ = r'^(\s)*class(\s)+(\w)+.*'
        self.patFunction = re.compile(function_)
        self.patClass = re.compile(class_)
        if not self.isRunning():
            global mapping_locations
            mapping_locations = {}
            self.execute = self.locate_code
            self.start()

    def find_file_code_location(self, path):
        self._file_path = unicode(path)
        if not self._file_path:
            return
        self.execute = self.locate_file_code
        function_ = r'(\s)*def(\s)+(\w)+(\s)*\(.*'
        class_ = r'(\s)*class(\s)+(\w)+.*'
        self.patFunction = re.compile(function_)
        self.patClass = re.compile(class_)
        if not self.isRunning():
            self.start()

    def run(self):
        self.execute()

    def locate_code(self):
        explorerContainer = explorer_container.ExplorerContainer()
        projects_obj = explorerContainer.get_opened_projects()
        projects = [p.path for p in projects_obj]
        if not projects:
            return
        queue = Queue.Queue()
        for project in projects:
            queue.put(project)
        while not self._cancel and not queue.empty():
            current_dir = QDir(queue.get())
            #Skip not readable dirs!
            if not current_dir.isReadable():
                continue

            project_data = project = json_manager.read_ninja_project(
                unicode(current_dir.path()))
            extensions = project_data.get('supported-extensions',
                settings.SUPPORTED_EXTENSIONS)

            queue_folders = Queue.Queue()
            queue_folders.put(current_dir)
            self.__locate_code_in_project(queue_folders, extensions)
        self.dirty = True
        self.get_locations()

    def __locate_code_in_project(self, queue_folders, extensions):
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
                ['*{0}'.format(x) for x in extensions],
                file_filter)
            #process all files in current dir!
            for one_file in current_files:
                self._grep_file_locate(unicode(one_file.absoluteFilePath()),
                    one_file.fileName())

    def locate_file_code(self):
        file_name = file_manager.get_basename(self._file_path)
        self._grep_file_locate(self._file_path, file_name)
        self.dirty = True
        self.execute = self.locate_code

    def go_to_definition(self):
        self.dirty = True
        self.results = []
        locations = self.get_locations()
        if self._isVariable:
            preResults = [
                [file_manager.get_basename(x.path), x.path, x.lineno, ''] \
                for x in locations \
                if (x.type == FILTERS['attribs']) and (x.name == self._search)]
        else:
            preResults = [
                [file_manager.get_basename(x.path), x.path, x.lineno, '']
                for x in locations \
                if ((x.type == FILTERS['functions']) or \
                   (x.type == FILTERS['classes'])) and \
                   (x.name == self._search)]
        for data in preResults:
            file_object = QFile(data[1])
            if not file_object.open(QFile.ReadOnly):
                return

            stream = QTextStream(file_object)
            line_index = 0
            line = stream.readLine()
            while not self._cancel:
                if line_index == data[2]:
                    data[3] = unicode(line)
                    self.results.append(data)
                    break
                #take the next line!
                line = stream.readLine()
                if line.isNull():
                    break
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
        if not thisFileLocations:
            file_name = file_manager.get_basename(path)
            self._grep_file_locate(path, file_name)
            thisFileLocations = mapping_locations.get(path, ())
        thisFileLocations = sorted(thisFileLocations[1:],
            key=lambda item: item.name)
        return thisFileLocations

    def convert_map_to_array(self):
        global mapping_locations
        self.locations = [x for location in mapping_locations
            for x in mapping_locations[location]]
        self.locations = sorted(self.locations, key=lambda item: item.name)

    def _grep_file_locate(self, file_path, file_name):
        #type - file_name - file_path
        global mapping_locations
        exts = settings.SYNTAX.get('python')['extension']
        if file_manager.get_file_extension(unicode(file_name)) not in exts:
            mapping_locations[unicode(file_path)] = [
                ResultItem(type=FILTERS['non-python'], name=unicode(file_name),
                    path=unicode(file_path), lineno=0)]
        else:
            mapping_locations[unicode(file_path)] = [
                ResultItem(type=FILTERS['files'], name=unicode(file_name),
                        path=unicode(file_path), lineno=0)]
        ext = file_manager.get_file_extension(file_path)
        #obtain a symbols handler for this file extension
        symbols_handler = settings.get_symbols_handler(ext)
        if symbols_handler is None:
            return
        results = []
        with open(file_path) as f:
            content = f.read()
            symbols = symbols_handler.obtain_symbols(content)
            if "classes" in symbols:
                for claz in symbols['classes']:
                    line_number = symbols['classes'][claz][0] - 1
                    members = symbols['classes'][claz][1]
                    results.append(ResultItem(type=FILTERS['classes'],
                        name=claz, path=unicode(file_path),
                        lineno=line_number))
                    if 'attributes' in members:
                        for attr in members['attributes']:
                            line_number = members['attributes'][attr] - 1
                            results.append(ResultItem(type=FILTERS['attribs'],
                                name=attr, path=unicode(file_path),
                                lineno=line_number))
                    if 'functions' in members:
                        for func in members['functions']:
                            line_number = members['functions'][func] - 1
                            results.append(ResultItem(
                                type=FILTERS['functions'], name=func,
                                path=unicode(file_path), lineno=line_number))
            if 'attributes' in symbols:
                for attr in symbols['attributes']:
                    line_number = symbols['attributes'][attr] - 1
                    results.append(ResultItem(type=FILTERS['attribs'],
                        name=attr, path=unicode(file_path),
                        lineno=line_number))
            if 'functions' in symbols:
                for func in symbols['functions']:
                    line_number = symbols['functions'][func] - 1
                    results.append(ResultItem(
                        type=FILTERS['functions'], name=func,
                        path=unicode(file_path), lineno=line_number))
        if results:
            mapping_locations[unicode(file_path)] += results

    def get_symbols_for_class(self, file_path, clazzName):
        lines = []
        with open(file_path) as f:
            content = f.read()
            ext = file_manager.get_file_extension(file_path)
            #obtain a symbols handler for this file extension
            symbols_handler = settings.get_symbols_handler(ext)
            symbols = symbols_handler.obtain_symbols(content)
            if "classes" in symbols:
                for claz in symbols['classes']:
                    if claz != clazzName:
                        continue
                    clazz = symbols['classes'][claz]
                    line_number = clazz[0] - 1
                    lines.append(ResultItem(type=FILTERS['classes'], name=claz,
                        path=unicode(file_path), lineno=line_number))
                    if 'attributes' in clazz[1]:
                        for attr in clazz[1]['attributes']:
                            line_number = clazz[1]['attributes'][attr] - 1
                            lines.append(ResultItem(
                                type=FILTERS['attribs'], name=attr,
                                path=unicode(file_path), lineno=line_number))
                    if 'functions' in clazz[1]:
                        for func in clazz[1]['functions']:
                            line_number = clazz[1]['functions'][func] - 1
                            lines.append(ResultItem(type=FILTERS['functions'],
                                name=func, path=unicode(file_path),
                                lineno=line_number))
                    return lines
            return []

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
            self.style().standardIcon(QStyle.SP_ArrowRight), 'Go!')
        self._completer = LocateCompleter(self)

        hLocator.addWidget(self._btnClose)
        hLocator.addWidget(self._completer)
        hLocator.addWidget(self._btnGo)

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
        self.setText(u"{0}<br>"
            "<span style='font-size: 12px; color: grey;'>({1})</span>".format(
                data.name, data.path))


class LocateCompleter(QLineEdit):

    def __init__(self, parent):
        QLineEdit.__init__(self, parent)
        self._parent = parent
        self.__prefix = ''
        self.frame = PopupCompleter()
        self.filterPrefix = re.compile(r'^(@|<|>|-|!|\.)(\s)*')
        self.advancePrefix = re.compile(r'(@|<|>|-|!)')
        self.tempLocations = []
        self.setMinimumWidth(700)
        self.items_in_page = 0
        self.page_items_step = 10
        self._filterData = [None, None, None, None]

        self.connect(self, SIGNAL("textChanged(QString)"),
            self.set_prefix)

    def set_prefix(self, prefix):
        """Set the prefix for the completer."""
        self.__prefix = unicode(prefix.toLower())
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
        locations_view = [(LocateItem(x), LocateWidget(x)) \
            for x in locations[begin:self.items_in_page]]
        return locations_view

    def filter(self):
        self.items_in_page = 0
        #Clean the objects from the listWidget
        inCurrentFile = False
        filterOptions = self.advancePrefix.split(
            unicode(self.__prefix).lstrip())
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
            #if the prefix is "." it means only the metadata of current file
            if filterOption == FILTERS['this-file']:
                inCurrentFile = True
                main = main_container.MainContainer()
                editorWidget = main.get_actual_editor()
                if editorWidget:
                    self.tempLocations = \
                        self._parent._thread.get_this_file_locations(
                            editorWidget.ID)
                    self.__prefix = unicode(self.__prefix)[1:].lstrip()
                    self.tempLocations = [x for x in self.tempLocations \
                        if x.name.lower().find(self.__prefix) > -1]
            else:
                #Is not "." filter by the other options
                self.tempLocations = [
                    x for x in self._parent._thread.get_locations()
                    if x.type == filterOption]
                #Obtain the user input without the filter prefix
                self.__prefix = unicode(self.__prefix)[1:].lstrip()
        else:
            self.tempLocations = self._parent._thread.get_locations()

        if self.__prefix and not inCurrentFile:
            #if prefix (user search now) is not empty, filter words that1
            #contain the user input
            self.tempLocations = [x for x in self.tempLocations \
                if x.name.lower().find(self.__prefix) > -1]

        return self._create_list_widget_items(self.tempLocations)

    def _advanced_filter(self, filterOptions):
        if filterOptions[0] == FILTERS['this-file']:
            filterOptions[0] = FILTERS['files']
            main = main_container.MainContainer()
            editorWidget = main.get_actual_editor()
            if editorWidget:
                filterOptions.insert(1, editorWidget.ID)
        elif filterOptions[0] in (FILTERS['classes'], FILTERS['files']):
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
        global mapping_locations
        filePath = filterOptions[1]

        moveIndex = 0
        if len(filterOptions) > 4 and filterOptions[2] == FILTERS['classes']:
            moveIndex = 2
            if self._filterData.type == FILTERS['classes']:
                self._classFilter = self._filterData.name
            symbols = self._parent._thread.get_symbols_for_class(filePath,
                self._classFilter)
            self.tempLocations = [x for x in symbols \
                if x.type == filterOptions[4]]
        else:
            self.tempLocations = [
                x for x in mapping_locations.get(filePath, []) \
                if x.type == filterOptions[2]]
        if filterOptions[3 + moveIndex]:
            self.tempLocations = [x for x in self.tempLocations \
                if x.name.lower().find(filterOptions[3 + moveIndex]) > -1]

    def _advanced_filter_by_file(self, filterOptions):
        if filterOptions[1] == FILTERS['files']:
            index = 2
        else:
            index = 3
        self.tempLocations = [x for x in self.tempLocations \
            if file_manager.get_basename(x.path).lower().find(
                filterOptions[index]) > -1]

    def _refresh_filter(self):
        self.frame.refresh(self.filter())

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            item = self.frame.listWidget.currentItem()
            self.setText(unicode(item._data[1]))
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
            if type(item) is LocateItem:
                self._open_item(item._data)
            self._parent.statusBar.hide_status()

    def focusOutEvent(self, event):
        """Hide Popup on focus lost."""
        self._parent.statusBar.hide_status()
        QLineEdit.focusOutEvent(self, event)

    def _open_item(self, data):
        """Open the item received."""
        if file_manager.get_file_extension(data.path) in ('jpg', 'png'):
            main_container.MainContainer().open_image(data.path)
        else:
            main_container.MainContainer().open_file(
                data.path, data.lineno, None, True)


class PopupCompleter(QFrame):

    def __init__(self):
        QFrame.__init__(self, None, Qt.FramelessWindowHint | Qt.ToolTip)
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        self.listWidget = QListWidget()
        self.listWidget.setMinimumHeight(300)
        vbox.addWidget(self.listWidget)

    def reload(self, model):
        """Reload the data of the Popup Completer, and restart the state."""
        self.listWidget.clear()
        self.add_help()
        for item in model:
            self.listWidget.addItem(item[0])
            self.listWidget.setItemWidget(item[0], item[1])
        self.listWidget.setCurrentRow(6)

    def clear(self):
        """Remove all the items of the list (deleted), and reload the help."""
        self.listWidget.clear()

    def refresh(self, model):
        """Refresh the list when the user search for some word."""
        self.listWidget.clear()
        for item in model:
            self.listWidget.addItem(item[0])
            self.listWidget.setItemWidget(item[0], item[1])
        if model:
            self.listWidget.setCurrentItem(model[0][0])

    def fetch_more(self, model):
        """Add more items to the list on user scroll."""
        for item in model:
            self.listWidget.addItem(item[0])
            self.listWidget.setItemWidget(item[0], item[1])

    def add_help(self):
        #Load help
        fileItem = QListWidgetItem(
            QIcon(resources.IMAGES['locate-file']),
                '@\t(Filter only by Files)')
        font = fileItem.font()
        font.setBold(True)
        fileItem.setSizeHint(QSize(20, 30))
        fileItem.setBackground(QBrush(Qt.lightGray))
        fileItem.setForeground(QBrush(Qt.black))
        fileItem.setFont(font)
        self.listWidget.addItem(fileItem)
        classItem = QListWidgetItem(
            QIcon(resources.IMAGES['locate-class']),
                '<\t(Filter only by Classes)')
        self.listWidget.addItem(classItem)
        classItem.setSizeHint(QSize(20, 30))
        classItem.setBackground(QBrush(Qt.lightGray))
        classItem.setForeground(QBrush(Qt.black))
        classItem.setFont(font)
        methodItem = QListWidgetItem(
            QIcon(resources.IMAGES['locate-function']),
                '>\t(Filter only by Methods)')
        self.listWidget.addItem(methodItem)
        methodItem.setSizeHint(QSize(20, 30))
        methodItem.setBackground(QBrush(Qt.lightGray))
        methodItem.setForeground(QBrush(Qt.black))
        methodItem.setFont(font)
        attributeItem = QListWidgetItem(
            QIcon(resources.IMAGES['locate-attributes']),
                '-\t(Filter only by Attributes)')
        self.listWidget.addItem(attributeItem)
        attributeItem.setSizeHint(QSize(20, 30))
        attributeItem.setBackground(QBrush(Qt.lightGray))
        attributeItem.setForeground(QBrush(Qt.black))
        attributeItem.setFont(font)
        thisFileItem = QListWidgetItem(
            QIcon(resources.IMAGES['locate-on-this-file']),
                '.\t(Filter only by Classes and Methods in this File)')
        font = thisFileItem.font()
        font.setBold(True)
        thisFileItem.setSizeHint(QSize(20, 30))
        thisFileItem.setBackground(QBrush(Qt.lightGray))
        thisFileItem.setForeground(QBrush(Qt.black))
        thisFileItem.setFont(font)
        self.listWidget.addItem(thisFileItem)
        nonPythonItem = QListWidgetItem(
            QIcon(resources.IMAGES['locate-nonpython']),
                '!\t(Filter only by Non Python Files)')
        self.listWidget.addItem(nonPythonItem)
        nonPythonItem.setSizeHint(QSize(20, 30))
        nonPythonItem.setBackground(QBrush(Qt.lightGray))
        nonPythonItem.setForeground(QBrush(Qt.black))
        nonPythonItem.setFont(font)
