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


mapping_locations = {}


#@ FILES
#< CLASSES
#> FUNCTIONS
#- MODULE ATTRIBUTES
#! NO PYTHON FILES
#. SYMBOLS IN THIS FILE


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
            if item[0] == '<']
        return classes


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
        file_filter = QDir.Files | QDir.NoDotAndDotDot | QDir.Readable
        dir_filter = QDir.Dirs | QDir.NoDotAndDotDot | QDir.Readable
        while not self._cancel and not queue.empty():
            current_dir = QDir(queue.get())
            #Skip not readable dirs!
            if not current_dir.isReadable():
                continue

            #Collect all sub dirs!
            current_sub_dirs = current_dir.entryInfoList(dir_filter)
            for one_dir in current_sub_dirs:
                queue.put(one_dir.absoluteFilePath())

            current_sub_dirs = current_dir.entryInfoList(dir_filter)
            #all files in sub_dir first apply the filters
            current_files = current_dir.entryInfoList(
                ['*{0}'.format(x) for x in settings.SUPPORTED_EXTENSIONS],
                file_filter)
            #process all files in current dir!
            for one_file in current_files:
                self._grep_file_locate(unicode(one_file.absoluteFilePath()),
                    one_file.fileName())
        self.dirty = True
        self.get_locations()

    def locate_file_code(self):
        file_name = file_manager.get_basename(self._file_path)
        self._grep_file_locate(self._file_path, file_name)
        self.dirty = True
        self.execute = self.locate_code

    def go_to_definition(self):
        self.dirty = True
        self.results = []
        locations = self.get_locations()
        #fileName - path - lineNumber - lineContent
        #type - class name - file_path - lineNumber
        if self._isVariable:
            preResults = [[file_manager.get_basename(x[2]), x[2], x[3], ''] \
                for x in locations \
                if x[0] == '-' and x[1] == self._search]
        else:
            preResults = [[file_manager.get_basename(x[2]), x[2], x[3], ''] \
                for x in locations \
                if (x[0] == '>' or x[0] == '<') and x[1] == self._search]
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
        thisFileLocations = thisFileLocations[1:]
        return thisFileLocations

    def convert_map_to_array(self):
        global mapping_locations
        self.locations = [x for location in mapping_locations
            for x in mapping_locations[location]]

    def _grep_file_locate(self, file_path, file_name):
        #type - file_name - file_path
        global mapping_locations
        if file_manager.get_file_extension(unicode(file_name)) != 'py':
            mapping_locations[unicode(file_path)] = [('!',
                unicode(file_name), unicode(file_path), 0)]
            return
        mapping_locations[unicode(file_path)] = [('@', unicode(file_name),
            unicode(file_path), 0)]

        lines = []
        with open(file_path) as f:
            content = f.read()
            ext = file_manager.get_file_extension(file_path)
            #obtain a symbols handler for this file extension
            symbols_handler = settings.get_symbols_handler(ext)
            symbols = symbols_handler.obtain_symbols(content)
            if "classes" in symbols:
                for claz in symbols['classes']:
                    clazz = symbols['classes'][claz]
                    #type - class name - file_path - lineNumber
                    lines.append(('<', claz, unicode(file_path),
                        clazz[0] - 1))
                    if 'attributes' in clazz[1]:
                        for attr in clazz[1]['attributes']:
                            #type - attribute name - file_path - lineNumber
                            lines.append(('-', attr, unicode(file_path),
                                clazz[1]['attributes'][attr] - 1))
                    if 'functions' in clazz[1]:
                        for func in clazz[1]['functions']:
                            #type - function name - file_path - lineNumber
                            lines.append(('>', func, unicode(file_path),
                                clazz[1]['functions'][func] - 1))
            if 'attributes' in symbols:
                for attr in symbols['attributes']:
                    #type - attribute name - file_path - lineNumber
                    lines.append(('-', attr, unicode(file_path),
                        symbols['attributes'][attr] - 1))
            if 'functions' in symbols:
                for func in symbols['functions']:
                    #type - function name - file_path - lineNumber
                    lines.append(('>', func, unicode(file_path),
                        symbols['functions'][func] - 1))
        if lines:
            mapping_locations[unicode(file_path)] += lines

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
                    #type - class name - file_path - lineNumber
                    lines.append(('<', claz, unicode(file_path),
                        clazz[0] - 1))
                    if 'attributes' in clazz[1]:
                        for attr in clazz[1]['attributes']:
                            #type - attribute name - file_path - lineNumber
                            lines.append(('-', attr, unicode(file_path),
                                clazz[1]['attributes'][attr] - 1))
                    if 'functions' in clazz[1]:
                        for func in clazz[1]['functions']:
                            #type - function name - file_path - lineNumber
                            lines.append(('>', func, unicode(file_path),
                                clazz[1]['functions'][func] - 1))
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

    icons = {'>': resources.IMAGES['function'],
        '@': resources.IMAGES['tree-python'],
        '<': resources.IMAGES['class'],
        '!': resources.IMAGES['tree-code'],
        '-': resources.IMAGES['attribute']}

    def __init__(self, data):
        QListWidgetItem.__init__(self, QIcon(self.icons[data[0]]), "\n")
        self._data = data


class LocateWidget(QLabel):

    """Create a styled QLabel that will show the info."""

    def __init__(self, data):
        QLabel.__init__(self)
        self.setText(u"{0}<br>"
            "<span style='font-size: 12px; color: grey;'>({1})</span>".format(
                data[1], data[2]))


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
            if '@' in (filterOptions[1], filterOptions[2]):
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
            if filterOption == '.':
                inCurrentFile = True
                main = main_container.MainContainer()
                editorWidget = main.get_actual_editor()
                if editorWidget:
                    self.tempLocations = \
                        self._parent._thread.get_this_file_locations(
                            editorWidget.ID)
                    self.__prefix = unicode(self.__prefix)[1:].lstrip()
                    self.tempLocations = [x for x in self.tempLocations \
                        if x[1].lower().find(self.__prefix) > -1]
            else:
                #Is not "." filter by the other options
                self.tempLocations = [
                    x for x in self._parent._thread.get_locations()
                    if x[0] == filterOption]
                #Obtain the user input without the filter prefix
                self.__prefix = unicode(self.__prefix)[1:].lstrip()
        else:
            self.tempLocations = self._parent._thread.get_locations()

        if self.__prefix and not inCurrentFile:
            #if prefix (user search now) is not empty, filter words that1
            #contain the user input
            self.tempLocations = [x for x in self.tempLocations \
                if x[1].lower().find(self.__prefix) > -1]

        return self._create_list_widget_items(self.tempLocations)

    def _advanced_filter(self, filterOptions):
        if filterOptions[0] == '.':
            filterOptions[0] = '@'
            main = main_container.MainContainer()
            editorWidget = main.get_actual_editor()
            if editorWidget:
                filterOptions.insert(1, editorWidget.ID)
        elif filterOptions[0] in ('<', '@'):
            currentItem = self.frame.listWidget.currentItem()
            if type(currentItem) is LocateItem:
                if currentItem._data[0] in ('@', '<'):
                    self._filterData = currentItem._data
            if filterOptions[0] == '<':
                filterOptions.insert(0, '@')
                filterOptions.insert(1, self._filterData[2])
            else:
                filterOptions[1] = self._filterData[2]
        global mapping_locations
        filePath = filterOptions[1]

        moveIndex = 0
        if len(filterOptions) > 4 and filterOptions[2] == '<':
            moveIndex = 2
            if self._filterData[0] == '<':
                self._classFilter = self._filterData[1]
            symbols = self._parent._thread.get_symbols_for_class(filePath,
                self._classFilter)
            self.tempLocations = [x for x in symbols \
                if x[0] == filterOptions[4]]
        else:
            self.tempLocations = [
                x for x in mapping_locations.get(filePath, []) \
                if x[0] == filterOptions[2]]
        if filterOptions[3 + moveIndex]:
            self.tempLocations = [x for x in self.tempLocations \
                if x[1].lower().find(filterOptions[3 + moveIndex]) > -1]

    def _advanced_filter_by_file(self, filterOptions):
        if filterOptions[1] == '@':
            index = 2
        else:
            index = 3
        self.tempLocations = [x for x in self.tempLocations \
            if file_manager.get_basename(x[2]).lower().find(
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
        if file_manager.get_file_extension(data[2]) in ('jpg', 'png'):
            main_container.MainContainer().open_image(data[2])
        else:
            main_container.MainContainer().open_file(
                data[2], data[3], None, True)


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
