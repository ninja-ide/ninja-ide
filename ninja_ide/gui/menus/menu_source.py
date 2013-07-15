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

from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QKeySequence
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QObject
from PyQt4.QtCore import Qt

from ninja_ide import resources
from ninja_ide.core import settings
from ninja_ide.gui.ide import IDE


class MenuSource(QObject):

    def install_menu(self, menuSource):
        countCodeLinesAction = menuSource.addAction(
            self.trUtf8("Count Code Lines"))
        menuSource.addSeparator()
        menu_debugging = menuSource.addMenu(self.trUtf8("Debugging Tricks"))
        insertPrints = menu_debugging.addAction(
            self.trUtf8("Insert Prints per selected line."))
        insertPdb = menu_debugging.addAction(
            self.trUtf8("Insert pdb.set_trace()"))

        menuSource.addSeparator()
        removeTrailingSpaces = menuSource.addAction(
            self.trUtf8("&Remove Trailing Spaces"))
        replaceTabsSpaces = menuSource.addAction(
            self.trUtf8("Replace Tabs With &Spaces"))



        self.connect(goToDefinitionAction, SIGNAL("triggered()"),
            self.editor_go_to_definition)
        self.connect(countCodeLinesAction, SIGNAL("triggered()"),
            self.count_lines_in_file)
        self.connect(insertImport, SIGNAL("triggered()"),
            self.import_from_everywhere)
        self.connect(indentMoreAction, SIGNAL("triggered()"),
            self.editor_indent_more)
        self.connect(indentLessAction, SIGNAL("triggered()"),
            self.editor_indent_less)
        self.connect(commentAction, SIGNAL("triggered()"),
            self.editor_comment)
        self.connect(unCommentAction, SIGNAL("triggered()"),
            self.editor_uncomment)
        self.connect(horizontalLineAction, SIGNAL("triggered()"),
            self.editor_insert_horizontal_line)
        self.connect(titleCommentAction, SIGNAL("triggered()"),
            self.editor_insert_title_comment)
#        QObject.connect(removeUnusedImportsAction, SIGNAL("triggered()"),
#        lambda: self._main._central.obtain_editor().remove_unused_imports())
##        QObject.connect(addMissingImportsAction, SIGNAL("triggered()"),
#        lambda: self._main._central.obtain_editor().add_missing_imports())
#        QObject.connect(organizeImportsAction, SIGNAL("triggered()"),
#        lambda: self._main._central.obtain_editor().organize_imports())
#        QObject.connect(extractMethodAction, SIGNAL("triggered()"),
#        lambda: self._main._central.obtain_editor().extract_method())
        self.connect(moveUp, SIGNAL("triggered()"),
            self.editor_move_up)
        self.connect(moveDown, SIGNAL("triggered()"),
            self.editor_move_down)
        self.connect(duplicate, SIGNAL("triggered()"),
            self.editor_duplicate)
        self.connect(replaceTabsSpaces, SIGNAL("triggered()"),
            self.editor_replace_tabs_with_spaces)
        self.connect(removeTrailingSpaces, SIGNAL("triggered()"),
            self.editor_remove_trailing_spaces)
        self.connect(remove, SIGNAL("triggered()"),
            self.editor_remove_line)
        self.connect(insertPrints, SIGNAL("triggered()"),
            self.editor_insert_debugging_prints)
        self.connect(insertPdb, SIGNAL("triggered()"),
            self.editor_insert_pdb)

    def count_lines_in_file(self):
        main_container = IDE.get_service('main_container')
        if main_container:
            main_container.count_file_code_lines()

    def editor_go_to_definition(self):
        main_container = IDE.get_service('main_container')
        if main_container:
            main_container.editor_go_to_definition()

    def editor_redo(self):
        main_container = IDE.get_service('main_container')
        if main_container:
            main_container.editor_redo()

    def editor_indent_less(self):
        main_container = IDE.get_service('main_container')
        if main_container:
            main_container.editor_indent_less()

    def editor_indent_more(self):
        main_container = IDE.get_service('main_container')
        if main_container:
            main_container.editor_indent_more()

    def editor_insert_debugging_prints(self):
        main_container = IDE.get_service('main_container')
        if main_container:
            main_container.editor_insert_debugging_prints()

    def editor_insert_pdb(self):
        main_container = IDE.get_service('main_container')
        if main_container:
            main_container.editor_insert_pdb()

    def editor_comment(self):
        main_container = IDE.get_service('main_container')
        if main_container:
            main_container.editor_comment()

    def editor_uncomment(self):
        main_container = IDE.get_service('main_container')
        if main_container:
            main_container.editor_uncomment()

    def editor_insert_horizontal_line(self):
        main_container = IDE.get_service('main_container')
        if main_container:
            main_container.editor_insert_horizontal_line()

    def editor_insert_title_comment(self):
        main_container = IDE.get_service('main_container')
        if main_container:
            main_container.editor_insert_title_comment()

    def editor_remove_trailing_spaces(self):
        main_container = IDE.get_service('main_container')
        if main_container:
            main_container.editor_remove_trailing_spaces()

    def editor_replace_tabs_with_spaces(self):
        main_container = IDE.get_service('main_container')
        if main_container:
            main_container.editor_replace_tabs_with_spaces()

    def editor_move_up(self):
        main_container = IDE.get_service('main_container')
        if main_container:
            main_container.editor_move_up()

    def editor_move_down(self):
        main_container = IDE.get_service('main_container')
        if main_container:
            main_container.editor_move_down()

    def editor_remove_line(self):
        main_container = IDE.get_service('main_container')
        if main_container:
            main_container.editor_remove_line()

    def editor_duplicate(self):
        main_container = IDE.get_service('main_container')
        if main_container:
            main_container.editor_duplicate()

    def import_from_everywhere(self):
        main_container = IDE.get_service('main_container')
        if main_container:
            main_container.import_from_everywhere()