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

from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL
from PyQt4.QtDeclarative import QDeclarativeView

from ninja_ide.tools import ui_tools
from ninja_ide.tools.locator import locator


class LocatorWidget(QDialog):
    """LocatorWidget class with the Logic for the QML UI"""

    def __init__(self, parent=None):
        super(LocatorWidget, self).__init__(
            parent, Qt.Dialog | Qt.FramelessWindowHint)
        self._parent = parent
        self.setModal(True)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background:transparent;")
        self.setFixedHeight(400)
        self.setFixedWidth(500)
        # Create the QML user interface.
        view = QDeclarativeView()
        view.setResizeMode(QDeclarativeView.SizeRootObjectToView)
        view.setSource(ui_tools.get_qml_resource("Locator.qml"))
        self._root = view.rootObject()
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        vbox.addWidget(view)

        self.locate_symbols = locator.LocateSymbolsThread()
        #self.connect(self.locate_symbols, SIGNAL("finished()"), self._cleanup)
        #self.connect(self.locate_symbols, SIGNAL("terminated()"),
                     #self._cleanup)

        # Locator things
        self._avoid_refresh = False
        self.__prefix = ''
        self.__pre_filters = []
        self.__pre_results = []
        self.filterPrefix = re.compile(r'(@|<|>|-|!|\.|/|:)')
        self.tempLocations = []
        self.items_in_page = 0
        self.page_items_step = 10
        self._line_jump = -1
        self._colors = {
            "@": "white",
            "<": "#18ff6a",
            ">": "red",
            "-": "#18e1ff",
            ".": "#f118ff",
            "/": "#fff118",
            ":": "#18ffd6",
            "!": "#ffa018"}

        #self._filter_actions = {
            #'.': self._filter_this_file,
            #'/': self._filter_tabs,
            #':': self._filter_lines
        #}

        self.connect(self._root, SIGNAL("textChanged(QString)"),
                     self.set_prefix)

        #self.connect(self.popup.listWidget,
                     #SIGNAL("itemPressed(QListWidgetItem*)"),
                     #self._go_to_location)

    def reset_values(self):
        self._avoid_refresh = False
        self.__prefix = ''
        self.__pre_filters = []
        self.__pre_results = []
        self.tempLocations = []
        self.items_in_page = 0
        self._line_jump = -1

    def showEvent(self, event):
        """Method takes an event to show the Notification"""
        # Load POPUP
        #TODO
        self.locate_symbols.find_code_location()
        super(LocatorWidget, self).showEvent(event)
        #width, pgeo = self._parent.width() / 2, self._parent.geometry()
        #conditional_vertical = settings.NOTIFICATION_POSITION in (0, 1)
        #conditional_horizont = settings.NOTIFICATION_POSITION in (0, 2)
        #x = pgeo.left() if conditional_horizont else pgeo.right()
        #y = pgeo.bottom() if conditional_vertical else pgeo.top() - self._height
        #self.setFixedWidth(width)
        x = (self._parent.width() / 2) - (self.width() / 2)
        y = 0
        #y = self._parent.y() + self._main_container.combo_header_size
        self.setGeometry(x, y, self.width(), self.height())
        self._root.activateInput()
        #background_color = str(settings.NOTIFICATION_COLOR)
        #foreground_color = str(settings.NOTIFICATION_COLOR).lower().translate(
            #maketrans('0123456789abcdef', 'fedcba9876543210'))
        #self._root.setColor(background_color, foreground_color)
        #self._root.start(self._duration)

    #def _cleanup(self):
        #self.locate_symbols.wait()

    #def explore_code(self):
        #self.locate_symbols.find_code_location()

    #def explore_file_code(self, path):
        #self.locate_symbols.find_file_code_location(path)

    def set_prefix(self, prefix):
        """Set the prefix for the completer."""
        if not self._avoid_refresh:
            self.__prefix = prefix.lower()
            self._refresh_filter()

    def _create_list_items(self, locations):
        """Create a list of items (using pages for results to speed up)."""
        #The list is regenerated when the locate metadata is updated
        #for example: open project, etc.
        #Create the list items
        begin = self.items_in_page
        self.items_in_page += self.page_items_step
        locations_view = [x for x in locations[begin:self.items_in_page]]
        return locations_view

    #def filter(self):
        #self._line_jump = -1
        #self.items_in_page = 0

        #filterOptions = self.filterPrefix.split(self.__prefix.lstrip())
        #if filterOptions[0] == '':
            #del filterOptions[0]

        #if len(filterOptions) == 0:
            #self.tempLocations = self._parent.locate_symbols.get_locations()
        #elif len(filterOptions) == 1:
            #self.tempLocations = [
                #x for x in self._parent.locate_symbols.get_locations()
                #if x.comparison.lower().find(filterOptions[0].lower()) > -1]
        #else:
            #index = 0
            #if not self.tempLocations and (self.__pre_filters == filterOptions):
                #self.tempLocations = self.__pre_results
                #return self._create_list_widget_items(self.tempLocations)
            #while index < len(filterOptions):
                #filter_action = self._filter_actions.get(
                    #filterOptions[index], self._filter_generic)
                #if filter_action is None:
                    #break
                #index = filter_action(filterOptions, index)
            #if self.tempLocations:
                #self.__pre_filters = filterOptions
                #self.__pre_results = self.tempLocations
        #return self._create_list_widget_items(self.tempLocations)

    #def _filter_generic(self, filterOptions, index):
        #at_start = (index == 0)
        #if at_start:
            #self.tempLocations = [
                #x for x in self._parent.locate_symbols.get_locations()
                #if x.type == filterOptions[0] and
                #x.comparison.lower().find(filterOptions[1].lower()) > -1]
        #else:
            #currentItem = self.popup.listWidget.currentItem()
            #filter_data = None
            #if type(currentItem) is LocateItem:
                #filter_data = currentItem.data
            #if filterOptions[index - 2] == FILTERS['classes'] and filter_data:
                #symbols = self._parent.locate_symbols.get_symbols_for_class(
                    #filter_data.path, filter_data.name)
                #self.tempLocations = symbols
            #elif filter_data:
                #global mapping_symbols
                #self.tempLocations = mapping_symbols.get(filter_data.path, [])
            #self.tempLocations = [x for x in self.tempLocations
                                  #if x.type == filterOptions[index] and
                                  #x.comparison.lower().find(
                                      #filterOptions[index + 1].lower()) > -1]
        #return index + 2

    #def _filter_this_file(self, filterOptions, index):
        #at_start = (index == 0)
        #if at_start:
            #main_container = IDE.get_service('main_container')
            #editorWidget = None
            #if main_container:
                #editorWidget = main_container.get_current_editor()
            #index += 2
            #if editorWidget:
                #exts = settings.SYNTAX.get('python')['extension']
                #file_ext = file_manager.get_file_extension(
                    #editorWidget.file_path)
                #if file_ext in exts:
                    #filterOptions.insert(0, FILTERS['files'])
                #else:
                    #filterOptions.insert(0, FILTERS['non-python'])
                #filterOptions.insert(1, editorWidget.file_path)
                #self.tempLocations = \
                    #self._parent.locate_symbols.get_this_file_symbols(
                        #editorWidget.file_path)
                #search = filterOptions[index + 1].lstrip().lower()
                #self.tempLocations = [x for x in self.tempLocations
                                      #if x.comparison.lower().find(search) > -1]
        #else:
            #del filterOptions[index + 1]
            #del filterOptions[index]
        #return index

    #def _filter_tabs(self, filterOptions, index):
        #at_start = (index == 0)
        #if at_start:
            #ninjaide = IDE.get_service('ide')
            #opened = ninjaide.filesystem.get_files()
            #self.tempLocations = [
                #ResultItem(
                    #FILTERS['files'],
                    #opened[f].file_name, opened[f].file_path) for f in opened]
            #search = filterOptions[index + 1].lstrip().lower()
            #self.tempLocations = [
                #x for x in self.tempLocations
                #if x.comparison.lower().find(search) > -1]
            #index += 2
        #else:
            #del filterOptions[index + 1]
            #del filterOptions[index]
        #return index

    #def _filter_lines(self, filterOptions, index):
        #at_start = (index == 0)
        #if at_start:
            #main_container = IDE.get_service('main_container')
            #editorWidget = None
            #if main_container:
                #editorWidget = main_container.get_current_editor()
            #index = 2
            #if editorWidget:
                #exts = settings.SYNTAX.get('python')['extension']
                #file_ext = file_manager.get_file_extension(
                    #editorWidget.file_path)
                #if file_ext in exts:
                    #filterOptions.insert(0, FILTERS['files'])
                #else:
                    #filterOptions.insert(0, FILTERS['non-python'])
                #filterOptions.insert(1, editorWidget.file_path)
            #self.tempLocations = [
                #x for x in self._parent.locate_symbols.get_locations()
                #if x.type == filterOptions[0] and
                #x.path == filterOptions[1]]
        #if filterOptions[index + 1].isdigit():
            #self._line_jump = int(filterOptions[index + 1]) - 1
        #return index + 2

    def _refresh_filter(self):
        #has_text = len(self.text()) != 0
        locations = self.locate_symbols.get_locations()
        l = self._create_list_items(locations)
        for item in l:
            self._root.loadItem(item.type, item.name, item.lineno,
                                item.path, self._colors[item.type])
        #self.popup.refresh(self.filter(), has_text)

    #def keyPressEvent(self, event):
        #if event.key() == Qt.Key_Space:
            #item = self.popup.listWidget.currentItem()
            #self.setText(item.data.comparison)
            #return

        #super(LocatorCompleter, self).keyPressEvent(event)
        #currentRow = self.popup.listWidget.currentRow()
        #if event.key() == Qt.Key_Down:
            #count = self.popup.listWidget.count()
            ##If the current position is greater than the amount of items in
            ##the list - 6, then try to fetch more items in the list.
            #if currentRow >= (count - 6):
                #locations = self._create_list_widget_items(self.tempLocations)
                #self.popup.fetch_more(locations)
            ##While the current position is lower that the list size go to next
            #if currentRow != count - 1:
                #self.popup.listWidget.setCurrentRow(
                    #self.popup.listWidget.currentRow() + 1)
        #elif event.key() == Qt.Key_Up:
            ##while the current position is greater than 0, go to previous
            #if currentRow > 0:
                #self.popup.listWidget.setCurrentRow(
                    #self.popup.listWidget.currentRow() - 1)
        #elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            ##If the user press enter, go to the item selected
            #item = self.popup.listWidget.currentItem()
            #self._go_to_location(item)

    #def _go_to_location(self, item):
        #if type(item) is LocateItem:
            #self._open_item(item.data)
        #self.emit(SIGNAL("hidden()"))

    #def focusOutEvent(self, event):
        #"""Hide Popup on focus lost."""
        #self.emit(SIGNAL("hidden()"))
        #super(LocatorCompleter, self).focusOutEvent(event)

    #def _open_item(self, data):
        #"""Open the item received."""
        #main_container = IDE.get_service('main_container')
        #if not main_container:
            #return
        #jump = data.lineno if self._line_jump == -1 else self._line_jump
        #main_container.open_file(data.path, jump, None, True)

    #def hideEvent(self, event):
        #self.tempLocations = []
        #self.__pre_filters = []
        #self.__pre_results = []
        #super(LocatorCompleter, self).hideEvent(event)

    def hideEvent(self, event):
        super(LocatorWidget, self).hideEvent(event)
        # clean
        self._avoid_refresh = True
        self._root.cleanText()
        self._root.clear()
        self.reset_values()