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
import webbrowser

from PyQt4.QtCore import QObject
from PyQt4.QtGui import QMessageBox

from ninja_ide.core.file_handling import file_manager
from ninja_ide.core import settings
from ninja_ide.gui.editor import editor
from ninja_ide.gui.main_panel import tab_group


class Actions(QObject):

    def count_file_code_lines(self):
        """Count the lines of code in the current file."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget:
            block_count = editorWidget.blockCount()
            blanks = re.findall('(^\n)|(^(\s+)?#)|(^( +)?($|\n))',
                editorWidget.get_text(), re.M)
            blanks_count = len(blanks)
            resume = self.tr("Lines code: %s\n") % (block_count - blanks_count)
            resume += (self.tr("Blanks and commented lines: %s\n\n") %
                blanks_count)
            resume += self.tr("Total lines: %s") % block_count
            msgBox = QMessageBox(QMessageBox.Information,
                self.tr("Summary of lines"), resume,
                QMessageBox.Ok, editorWidget)
            msgBox.exec_()

    def reset_editor_flags(self):
        """Reset the Flags for all the opened editors."""
        self.ide.mainContainer.reset_editor_flags()

    def call_editors_function(self, call_function, *args, **kwargs):
        self.ide.mainContainer.call_editors_function(
            call_function, args, kwargs)

    def preview_in_browser(self):
        """Load the current html file in the default browser."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget:
            if not editorWidget.ID:
                self.ide.mainContainer.save_file()
            ext = file_manager.get_file_extension(editorWidget.ID)
            if ext == 'html':
                webbrowser.open(editorWidget.ID)

    def save_all(self):
        """Save all the opened files."""
        self.ide.mainContainer.save_all()

    def locate_function(self, function, filePath, isVariable):
        """Move the cursor to the proper position in the navigate stack."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget:
            self.__codeBack.append((editorWidget.ID,
                editorWidget.textCursor().position()))
            self.__codeForward = []
        #self._locator.navigate_to(function,
            #filePath, isVariable)

    def update_explorer(self):
        """Update the symbols in the Symbol Explorer when a file is saved."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget:
            ext = file_manager.get_file_extension(editorWidget.ID)
            #obtain a symbols handler for this file extension
            symbols_handler = settings.get_symbols_handler(ext)
            if symbols_handler:
                source = editorWidget.toPlainText()
                if editorWidget.encoding is not None:
                    source = source.encode(editorWidget.encoding)
                if ext == 'py':
                    args = (source, True)
                else:
                    args = (source,)
                symbols = symbols_handler.obtain_symbols(*args)
                self.ide.explorer.update_symbols(symbols, editorWidget.ID)

            #TODO: Should we change the code below similar to the code above?
            exts = settings.SYNTAX.get('python')['extension']
            if ext in exts or editorWidget.newDocument:
                self.ide.explorer.update_errors(
                    editorWidget.errors, editorWidget.pep8)

    def add_back_item_navigation(self):
        """Add an item to the back stack and reset the forward stack."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget:
            self.__codeBack.append((editorWidget.ID,
                editorWidget.textCursor().position()))
            self.__codeForward = []

    def group_tabs_together(self):
        """Group files that belongs to the same project together."""
        if self.ide.explorer._treeProjects is None:
            return
        projects_obj = self.ide.explorer.get_opened_projects()
        projects = [p.path for p in projects_obj]
        for project in projects:
            projectName = self.ide.explorer.get_project_name(project)
            if not projectName:
                projectName = file_manager.get_basename(project)
            tabGroup = tab_group.TabGroup(project, projectName, self)
            for index in reversed(list(range(
            self.ide.mainContainer._tabMain.count()))):
                widget = self.ide.mainContainer._tabMain.widget(index)
                if type(widget) is editor.Editor and \
                file_manager.belongs_to_folder(project, widget.ID):
                    tabGroup.add_widget(widget)
                    self.ide.mainContainer._tabMain.removeTab(index)
            if tabGroup.tabs:
                self.ide.mainContainer._tabMain.add_tab(tabGroup, projectName)

    def deactivate_tabs_groups(self):
        """Deactivate tab grouping based in the project they belong."""
        for index in reversed(list(range(
        self.ide.mainContainer._tabMain.count()))):
            widget = self.ide.mainContainer._tabMain.widget(index)
            if type(widget) is tab_group.TabGroup:
                widget.only_expand()

    def reload_toolbar(self):
        """Reload the Toolbar."""
        self.ide.load_toolbar()
