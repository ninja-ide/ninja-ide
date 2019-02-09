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

import re

from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QShortcut

from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt
from PyQt5.QtQuickWidgets import QQuickWidget

# from ninja_ide.utils import
from ninja_ide import resources
from ninja_ide.core import settings
from ninja_ide.core.file_handling import file_manager
from ninja_ide.tools import ui_tools
from ninja_ide.tools import utils
from ninja_ide.gui.ide import IDE
from ninja_ide.tools.locator import locator
from ninja_ide.tools.logger import NinjaLogger

logger = NinjaLogger(__name__)
DEBUG = logger.debug


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
        view = QQuickWidget()
        view.rootContext().setContextProperty("theme", resources.QML_COLORS)
        view.setResizeMode(QQuickWidget.SizeRootObjectToView)
        view.setSource(ui_tools.get_qml_resource("Locator.qml"))
        self._root = view.rootObject()
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        vbox.addWidget(view)

        self.locate_symbols = locator.LocateSymbolsThread()
        self.locate_symbols.finished.connect(self._cleanup)
        # FIXME: invalid signal
        # self.locate_symbols.terminated.connect(self._cleanup)
        # Hide locator with Escape key
        shortEscMisc = QShortcut(QKeySequence(Qt.Key_Escape), self)
        shortEscMisc.activated.connect(self.hide)

        # Locator things
        self.filterPrefix = re.compile(r'(@|<|>|-|!|\.|/|:)')
        self.page_items_step = 10
        self._colors = {
            "@": "#5dade2",
            "<": "#4becc9",
            ">": "#ff555a",
            "-": "#66ff99",
            ".": "#a591c6",
            "/": "#f9d170",
            ":": "#18ffd6",
            "!": "#ff884d"}
        self._filters_list = [
            ("@", "Filename"),
            ("<", "Class"),
            (">", "Function"),
            ("-", "Attribute"),
            (".", "Current"),
            ("/", "Opened"),
            (":", "Line"),
            ("!", "NoPython")
        ]
        self._replace_symbol_type = {"<": "&lt;", ">": "&gt;"}
        self.reset_values()

        self._filter_actions = {
            '.': self._filter_this_file,
            '/': self._filter_tabs,
            ':': self._filter_lines
        }
        self._root.textChanged['QString'].connect(self.set_prefix)
        self._root.open['QString', int].connect(self._open_item)
        self._root.fetchMore.connect(self._fetch_more)

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
        super(LocatorWidget, self).showEvent(event)
        self._root.activateInput()
        self._refresh_filter()

    def _cleanup(self):
        self.locate_symbols.wait()

    def explore_code(self):
        self.locate_symbols.find_code_location()

    def explore_file_code(self, path):
        self.locate_symbols.find_file_code_location(path)

    def set_prefix(self, prefix):
        """Set the prefix for the completer."""
        self.__prefix = prefix.lower()
        if not self._avoid_refresh:
            self._refresh_filter()

    def set_text(self, text):
        self._root.setText(text)

    def _refresh_filter(self):
        items = self.filter()
        self._root.clear()
        self._load_items(items)
        filter_composite = ""
        for symbol, text in self._filters_list:
            typeIcon = self._replace_symbol_type.get(symbol, symbol)
            if symbol in self.__prefix:
                composite = "<font color='{0}'>{1}{2}</font> ".format(
                    self._colors.get(symbol, "#8f8f8f"), typeIcon, text)
                filter_composite += composite
            else:
                composite = "<font color='#8f8f8f'>{0}{1}</font> ".format(
                    typeIcon, text)
                filter_composite += composite
        self._root.setFilterComposite(filter_composite)

    def _load_items(self, items):
        for item in items:
            typeIcon = self._replace_symbol_type.get(item.type, item.type)
            if settings.IS_WINDOWS:
                display_path = item.path
            else:
                display_path = utils.path_with_tilde_homepath(item.path)
            self._root.loadItem(typeIcon, item.name, item.lineno,
                                item.path, display_path, self._colors[item.type])

    def _fetch_more(self):
        locations = self._create_list_items(self.tempLocations)
        self._load_items(locations)

    def _create_list_items(self, locations):
        """Create a list of items (using pages for results to speed up)."""
        # The list is regenerated when the locate metadata is updated
        # for example: open project, etc.
        # Create the list items
        begin = self.items_in_page
        self.items_in_page += self.page_items_step
        locations_view = [x for x in locations[begin:self.items_in_page]]
        return locations_view

    def filter(self):
        self._line_jump = -1
        self.items_in_page = 0

        filterOptions = self.filterPrefix.split(self.__prefix.lstrip())
        if not filterOptions[0]:
            del filterOptions[0]

        if len(filterOptions) == 0:
            self.tempLocations = self.locate_symbols.get_locations()
        elif len(filterOptions) == 1:
            self.tempLocations = [
                x for x in self.locate_symbols.get_locations()
                if x.comparison.lower().find(filterOptions[0].lower()) > -1]
        else:
            index = 0
            if not self.tempLocations and (self.__pre_filters == filterOptions):
                self.tempLocations = self.__pre_results
                return self._create_list_items(self.tempLocations)
            while index < len(filterOptions):
                filter_action = self._filter_actions.get(
                    filterOptions[index], self._filter_generic)
                if filter_action is None:
                    break
                index = filter_action(filterOptions, index)
            if self.tempLocations:
                self.__pre_filters = filterOptions
                self.__pre_results = self.tempLocations
        return self._create_list_items(self.tempLocations)

    def _filter_generic(self, filterOptions, index):
        at_start = (index == 0)
        if at_start:
            self.tempLocations = [
                x for x in self.locate_symbols.get_locations()
                if x.type == filterOptions[0] and
                x.comparison.lower().find(filterOptions[1].lower()) > -1]
        else:
            currentItem = self._root.currentItem()
            if currentItem is not None:
                currentItem = currentItem.toVariant()
                if (filterOptions[index - 2] == locator.FILTERS['classes'] and
                        currentItem):
                    symbols = self.locate_symbols.get_symbols_for_class(
                        currentItem[2], currentItem[1])
                    self.tempLocations = symbols
                elif currentItem:
                    global mapping_symbols
                    self.tempLocations = locator.mapping_symbols.get(
                        currentItem[2], [])
                self.tempLocations = [x for x in self.tempLocations
                                      if x.type == filterOptions[index] and
                                      x.comparison.lower().find(
                                        filterOptions[index + 1].lower()) > -1]
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
                    filterOptions.insert(0, locator.FILTERS['files'])
                else:
                    filterOptions.insert(0, locator.FILTERS['non-python'])
                filterOptions.insert(1, editorWidget.file_path)
                self.tempLocations = \
                    self.locate_symbols.get_this_file_symbols(
                        editorWidget.file_path)
                search = filterOptions[index + 1].lstrip().lower()
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
            self.tempLocations = [
                locator.ResultItem(
                    locator.FILTERS['files'],
                    opened[f].file_name, opened[f].file_path) for f in opened]
            search = filterOptions[index + 1].lstrip().lower()
            self.tempLocations = [
                x for x in self.tempLocations
                if x.comparison.lower().find(search) > -1]
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
                    filterOptions.insert(0, locator.FILTERS['files'])
                else:
                    filterOptions.insert(0, locator.FILTERS['non-python'])
                filterOptions.insert(1, editorWidget.file_path)
            self.tempLocations = [
                x for x in self.locate_symbols.get_locations()
                if x.type == filterOptions[0] and
                x.path == filterOptions[1]]
        else:
            currentItem = self._root.currentItem()
            if currentItem is not None:
                currentItem = currentItem.toVariant()
                self.tempLocations = [
                    x for x in self.locate_symbols.get_locations()
                    if x.type == currentItem[0] and
                    x.path == currentItem[2]]
        if filterOptions[index + 1].isdigit():
            self._line_jump = int(filterOptions[index + 1]) - 1
        return index + 2

    def _open_item(self, path, lineno):
        """Open the item received."""
        main_container = IDE.get_service('main_container')
        if not main_container:
            return
        jump = lineno if self._line_jump == -1 else self._line_jump
        main_container.open_file(path, jump)
        self.hide()

    def hideEvent(self, event):
        super(LocatorWidget, self).hideEvent(event)
        # clean
        self._avoid_refresh = True
        self._root.cleanText()
        self._root.clear()
        self.reset_values()
