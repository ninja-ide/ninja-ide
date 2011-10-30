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
        self.execute = self.navigate_code
        self.dirty = False

    def find(self, function, filePath, isVariable):
        self.cancel()
        self._filePath = filePath
        self._cancel = False
        if isVariable:
            function_ = r'(\s)*%s(\s)*=\.*' % function
            class_ = r'(\s)*self.%s(\s)*=\.*' % function
        else:
            function_ = r'(\s)*def(\s)+%s(\s)*\(.*' % function
            class_ = r'(\s)*class(\s)+%s(\s)*\(.*' % function
        self.patFunction = re.compile(function_)
        self.patClass = re.compile(class_)
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

    def navigate_code(self):
        explorerContainer = explorer_container.ExplorerContainer()
        projects_obj = explorerContainer.get_opened_projects()
        projects = [p.path for p in projects_obj]
        project = None
        for p in projects:
            if self._filePath.startswith(p):
                project = p
                break
        #Search in files
        if not project:
            fileName = file_manager.get_basename(self._filePath)
            self._grep_file(self._filePath, fileName)
            return
        queue = Queue.Queue()
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
                ['*.py'], file_filter)
            #process all files in current dir!
            for one_file in current_files:
                if one_file.fileName() != '__init__.py':
                    self._grep_file(one_file.absoluteFilePath(),
                        one_file.fileName())

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
                self._grep_file_locate(one_file.absoluteFilePath(),
                    one_file.fileName())
#        self.convert_map_to_array()
        self.dirty = True

    def locate_file_code(self):
        file_name = file_manager.get_basename(self._file_path)
        self._grep_file_locate(self._file_path, file_name)
        self.dirty = True
        self.execute = self.locate_code

    def get_locations(self):
        if self.dirty:
            self.convert_map_to_array()
            self.dirty = False
        return self.locations

    def get_this_file_locations(self, path):
        global mapping_locations
        thisFileLocations = mapping_locations.get(path, ())
        if thisFileLocations:
            thisFileLocations = thisFileLocations[1:]
        return thisFileLocations

    def convert_map_to_array(self):
        global mapping_locations
        self.locations = [x for location in mapping_locations
            for x in mapping_locations[location] if x[1] != '']

    def _grep_file(self, file_path, file_name):
        file_object = QFile(file_path)
        if not file_object.open(QFile.ReadOnly):
            return

        stream = QTextStream(file_object)
        lines = []
        line_index = 0
        line = stream.readLine()
        while not self._cancel:
            if self.patFunction.match(line) or self.patClass.match(line):
                #fileName - path - lineNumber - lineContent
                lines.append((unicode(file_name), unicode(file_path),
                    line_index, unicode(line)))
            #take the next line!
            line = stream.readLine()
            if line.isNull():
                break
            line_index += 1
        if lines:
            self.results += lines

    def _grep_file_locate(self, file_path, file_name):
        file_object = QFile(file_path)
        if not file_object.open(QFile.ReadOnly):
            return
        #type - file_name - file_path
        global mapping_locations
        if file_manager.get_file_extension(unicode(file_name)) != 'py':
            mapping_locations[unicode(file_path)] = [('!',
                unicode(file_name), unicode(file_path), 0)]
            return
        mapping_locations[unicode(file_path)] = [('@', unicode(file_name),
            unicode(file_path), 0)]

        stream = QTextStream(file_object)
        lines = []
        line_index = 0
        line = stream.readLine()
        while not self._cancel:
            if self.patFunction.match(line):
                line = unicode(line)
                func_name = line[line.find('def') + 3:line.find('(')].strip()
                #type - function name - file_path - lineNumber
                lines.append(('>', func_name, unicode(file_path), line_index))
            elif self.patClass.match(line):
                line = unicode(line)
                if line.find('(') > 0:
                    class_name = line[
                        line.find('class') + 5:line.find('(')].strip()
                else:
                    class_name = line[:line.find(':')].split(
                        'class')[1].strip()
                #type - class name - file_path - lineNumber
                lines.append(('<', class_name, unicode(file_path), line_index))
            #take the next line!
            line = stream.readLine()
            if line.isNull():
                break
            line_index += 1
        if lines:
            mapping_locations[unicode(file_path)] += lines

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

    icons = {'>': resources.IMAGES['function'],
        '@': resources.IMAGES['tree-python'],
        '<': resources.IMAGES['class'],
        '!': resources.IMAGES['tree-code']}

    def __init__(self, data):
        QListWidgetItem.__init__(self, QIcon(self.icons[data[0]]), "\n")
        self._data = data


class LocateWidget(QLabel):

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
        self.filterPrefix = re.compile(r'^(@|<|>|!|\.)(\s)*')
        self.locations = []
        self.tempLocations = []
        self.setMinimumWidth(700)

        self.connect(self, SIGNAL("textChanged(QString)"),
            self.set_prefix)

    def set_prefix(self, prefix):
        self.__prefix = unicode(prefix.toLower())
        if self.__prefix != '':
            self.frame.hide_help()
        self._refresh_filter()

    def complete(self):
        self.frame.reload(self.filter())
        self.frame.setFixedWidth(self.width())
        point = self._parent.mapToGlobal(self.pos())
        self.frame.show()
        self.frame.move(point.x(), point.y() - self.frame.height())

    def _create_list_items(self):
        if self._parent._thread.dirty:
            self.locations = [(LocateItem(x), LocateWidget(x)) \
                for x in self._parent._thread.get_locations()]
        return self.locations

    def filter(self):
        self.tempLocations = self._create_list_items()
        if self.filterPrefix.match(self.__prefix):
            filterOption = self.__prefix[:1]
            if filterOption == '.':
                editorWidget = \
                    main_container.MainContainer().get_actual_editor()
                self.tempLocations = \
                    self._parent._thread.get_this_file_locations(
                        editorWidget.ID)
                self.__prefix = unicode(self.__prefix)[1:].lstrip()
                self.tempLocations = [(LocateItem(x), LocateWidget(x)) \
                    for x in self.tempLocations \
                    if x[1].lower().find(self.__prefix) > -1]
                return self.tempLocations
            self.tempLocations = [x for x in self.tempLocations
                if x[0]._data[0] == filterOption]
            self.__prefix = unicode(self.__prefix)[1:].lstrip()
        if self.__prefix:
            self.tempLocations = [x for x in self.tempLocations \
                if x[0]._data[1].lower().find(self.__prefix) > -1]
        else:
            self.tempLocations = [x for x in self.tempLocations]
        return self.tempLocations

    def _refresh_filter(self):
        self.frame.refresh(self.filter())

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            currentText = unicode(self.frame.listWidget.currentItem().text())
            currentText = currentText.split(' (')[0]
            self.setText(currentText)
            return

        QLineEdit.keyPressEvent(self, event)
        if event.key() == Qt.Key_Down:
            if self.frame.listWidget.currentRow() == \
              self.frame.listWidget.count() - 3:
                self.frame.fetch_more(self.tempLocations)
            elif self.frame.listWidget.currentRow() != \
              self.frame.listWidget.count() - 1:
                self.frame.listWidget.setCurrentRow(
                    self.frame.listWidget.currentRow() + 1)
            else:
                self.frame.fetch_more(self.tempLocations)
        elif event.key() == Qt.Key_Up:
            if self.frame.listWidget.currentRow() > 0:
                self.frame.listWidget.setCurrentRow(
                    self.frame.listWidget.currentRow() - 1)
        elif event.key() in (Qt.Key_Tab, Qt.Key_Return, Qt.Key_Enter):
            item = self.frame.listWidget.currentItem()
            if type(item) is LocateItem:
                print item._data
                self._open_item(item._data)
            self._parent.statusBar.hide_status()

    def focusOutEvent(self, event):
        self._parent.statusBar.hide_status()
        QLineEdit.focusOutEvent(self, event)

    def _open_item(self, data):
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
        self.fetch = 10
        self.listWidget = QListWidget()
        self.listWidget.setAutoScroll(True)
        self.listWidget.setVerticalScrollMode(self.listWidget.ScrollPerItem)
        self.listWidget.setMinimumHeight(250)
        vbox.addWidget(self.listWidget)
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

    def reload(self, model):
        for index in xrange(self.listWidget.count()):
            self.listWidget.setRowHidden(index, True)
        self.show_help()
        for i, item in enumerate(model):
            if i > self.fetch:
                break
            if self.listWidget.indexFromItem(item[0]).isValid():
                item[0].setHidden(False)
            else:
                self.listWidget.addItem(item[0])
                self.listWidget.setItemWidget(item[0], item[1])
        if len(model) != self.listWidget.count():
            moreItems = QListWidgetItem('Load more...')
            self.listWidget.addItem(moreItems)
        self.listWidget.setCurrentRow(5)

    def hide_help(self):
        for i in xrange(5):
            self.listWidget.setRowHidden(i, True)

    def show_help(self):
        for i in xrange(5):
            self.listWidget.setRowHidden(i, False)

    def refresh(self, model):
        for index in xrange(self.listWidget.count()):
            self.listWidget.setRowHidden(index, True)
        for i, item in enumerate(model):
            if i > self.fetch:
                break
            if self.listWidget.indexFromItem(item[0]).isValid():
                item[0].setHidden(False)
            else:
                self.listWidget.addItem(item[0])
                self.listWidget.setItemWidget(item[0], item[1])
        for index in xrange(self.listWidget.count()):
            if not self.listWidget.item(index).isHidden():
                break
        self.listWidget.setCurrentRow(index)
        self.listWidget.scrollToTop()

    def fetch_more(self, model):
        fromFetch = self.fetch + 1
        self.fetch = min(self.fetch + 10, len(model))
        if self.fetch > fromFetch:
            self.listWidget.takeItem(self.listWidget.count() - 1)
        for i in xrange(self.fetch - fromFetch):
            self.listWidget.addItem(model[fromFetch + i][0])
            self.listWidget.setItemWidget(model[fromFetch + i][0],
                model[fromFetch + i][1])
        self.listWidget.setCurrentRow(
            self.listWidget.currentRow() + 1)
        if len(model) != self.fetch:
            moreItems = QListWidgetItem('Load more...')
            self.listWidget.addItem(moreItems)
