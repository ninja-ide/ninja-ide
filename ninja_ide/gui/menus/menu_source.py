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
from ninja_ide.gui import actions


class MenuSource(QObject):

    def __init__(self, menuSource):
        QObject.__init__(self)

        indentMoreAction = menuSource.addAction(
            QIcon(resources.IMAGES['indent-more']),
            (self.trUtf8("Indent More (%s)") %
                QKeySequence(Qt.Key_Tab).toString(QKeySequence.NativeText)))
        indentLessAction = menuSource.addAction(
            QIcon(resources.IMAGES['indent-less']),
            (self.trUtf8("Indent Less (%s)") %
                resources.get_shortcut("Indent-less").toString(
                    QKeySequence.NativeText)))
        menuSource.addSeparator()
        commentAction = menuSource.addAction(
            QIcon(resources.IMAGES['comment-code']),
            (self.trUtf8("Comment (%s)") %
                resources.get_shortcut("Comment").toString(
                    QKeySequence.NativeText)))
        unCommentAction = menuSource.addAction(
            QIcon(resources.IMAGES['uncomment-code']),
            (self.trUtf8("Uncomment (%s)") %
                resources.get_shortcut("Uncomment").toString(
                    QKeySequence.NativeText)))
        horizontalLineAction = menuSource.addAction(
            (self.trUtf8("Insert Horizontal Line (%s)") %
                resources.get_shortcut("Horizontal-line").toString(
                    QKeySequence.NativeText)))
        titleCommentAction = menuSource.addAction(
            (self.trUtf8("Insert Title Comment (%s)") %
                resources.get_shortcut("Title-comment").toString(
                    QKeySequence.NativeText)))
        countCodeLinesAction = menuSource.addAction(
            self.trUtf8("Count Code Lines"))
        menuSource.addSeparator()
#        tellTaleAction = menuSource.addAction(
#            self.trUtf8("Tell me a Tale of Code"))
#        tellTaleAction.setEnabled(False)
        goToDefinitionAction = menuSource.addAction(
            QIcon(resources.IMAGES['go-to-definition']),
            (self.trUtf8("Go To Definition (%s or %s+Click)") %
                (resources.get_shortcut("Go-to-definition").toString(
                    QKeySequence.NativeText),
                settings.OS_KEY)))
        insertImport = menuSource.addAction(
            QIcon(resources.IMAGES['insert-import']),
            (self.trUtf8("Insert &Import (%s)") %
                resources.get_shortcut("Import").toString(
                    QKeySequence.NativeText)))
        menu_debugging = menuSource.addMenu(self.trUtf8("Debugging Tricks"))
        insertPrints = menu_debugging.addAction(
            self.trUtf8("Insert Prints per selected line."))
        insertPdb = menu_debugging.addAction(
            self.trUtf8("Insert pdb.set_trace()"))
#        organizeImportsAction = menuSource.addAction(
#            self.trUtf8("&Organize Imports"))
#        removeUnusedImportsAction = menuSource.addAction(
#            self.trUtf8("Remove Unused &Imports"))
#        extractMethodAction = menuSource.addAction(
#            self.trUtf8("Extract selected &code as Method"))
        menuSource.addSeparator()
        removeTrailingSpaces = menuSource.addAction(
            self.trUtf8("&Remove Trailing Spaces"))
        replaceTabsSpaces = menuSource.addAction(
            self.trUtf8("Replace Tabs With &Spaces"))
        moveUp = menuSource.addAction((self.trUtf8("Move &Up (%s)") %
            resources.get_shortcut("Move-up").toString(
                QKeySequence.NativeText)))
        moveDown = menuSource.addAction((self.trUtf8("Move &Down (%s)") %
            resources.get_shortcut("Move-down").toString(
                QKeySequence.NativeText)))
        duplicate = menuSource.addAction(
            (self.trUtf8("Duplica&te (%s)") %
                resources.get_shortcut("Duplicate").toString(
                    QKeySequence.NativeText)))
        remove = menuSource.addAction(
            (self.trUtf8("&Remove Line (%s)") %
                resources.get_shortcut("Remove-line").toString(
                    QKeySequence.NativeText)))

        self.toolbar_items = {
            'indent-more': indentMoreAction,
            'indent-less': indentLessAction,
            'comment': commentAction,
            'uncomment': unCommentAction,
            'go-to-definition': goToDefinitionAction,
            'insert-import': insertImport}

        self.connect(goToDefinitionAction, SIGNAL("triggered()"),
            actions.Actions().editor_go_to_definition)
        self.connect(countCodeLinesAction, SIGNAL("triggered()"),
            actions.Actions().count_file_code_lines)
        self.connect(insertImport, SIGNAL("triggered()"),
            actions.Actions().import_from_everywhere)
        self.connect(indentMoreAction, SIGNAL("triggered()"),
            actions.Actions().editor_indent_more)
        self.connect(indentLessAction, SIGNAL("triggered()"),
            actions.Actions().editor_indent_less)
        self.connect(commentAction, SIGNAL("triggered()"),
            actions.Actions().editor_comment)
        self.connect(unCommentAction, SIGNAL("triggered()"),
            actions.Actions().editor_uncomment)
        self.connect(horizontalLineAction, SIGNAL("triggered()"),
            actions.Actions().editor_insert_horizontal_line)
        self.connect(titleCommentAction, SIGNAL("triggered()"),
            actions.Actions().editor_insert_title_comment)
#        QObject.connect(removeUnusedImportsAction, SIGNAL("triggered()"),
#        lambda: self._main._central.obtain_editor().remove_unused_imports())
##        QObject.connect(addMissingImportsAction, SIGNAL("triggered()"),
#        lambda: self._main._central.obtain_editor().add_missing_imports())
#        QObject.connect(organizeImportsAction, SIGNAL("triggered()"),
#        lambda: self._main._central.obtain_editor().organize_imports())
#        QObject.connect(extractMethodAction, SIGNAL("triggered()"),
#        lambda: self._main._central.obtain_editor().extract_method())
        self.connect(moveUp, SIGNAL("triggered()"),
            actions.Actions().editor_move_up)
        self.connect(moveDown, SIGNAL("triggered()"),
            actions.Actions().editor_move_down)
        self.connect(duplicate, SIGNAL("triggered()"),
            actions.Actions().editor_duplicate)
        self.connect(replaceTabsSpaces, SIGNAL("triggered()"),
            actions.Actions().editor_replace_tabs_with_spaces)
        self.connect(removeTrailingSpaces, SIGNAL("triggered()"),
            actions.Actions().editor_remove_trailing_spaces)
        self.connect(remove, SIGNAL("triggered()"),
            actions.Actions().editor_remove_line)
        self.connect(insertPrints, SIGNAL("triggered()"),
            actions.Actions().editor_insert_debugging_prints)
        self.connect(insertPdb, SIGNAL("triggered()"),
            actions.Actions().editor_insert_pdb)
