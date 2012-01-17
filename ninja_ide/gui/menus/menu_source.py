# *-* coding: utf-8 *-*
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
            self.tr("Indent More (%1)").arg(
                QKeySequence(Qt.Key_Tab).toString(QKeySequence.NativeText)))
        indentLessAction = menuSource.addAction(
            QIcon(resources.IMAGES['indent-less']),
            self.tr("Indent Less (%1)").arg(
                resources.get_shortcut("Indent-less").toString(
                    QKeySequence.NativeText)))
        menuSource.addSeparator()
        commentAction = menuSource.addAction(
            QIcon(resources.IMAGES['comment-code']),
            self.tr("Comment (%1)").arg(
                resources.get_shortcut("Comment").toString(
                    QKeySequence.NativeText)))
        unCommentAction = menuSource.addAction(
            QIcon(resources.IMAGES['uncomment-code']),
            self.tr("Uncomment (%1)").arg(
                resources.get_shortcut("Uncomment").toString(
                    QKeySequence.NativeText)))
        horizontalLineAction = menuSource.addAction(
            self.tr("Insert Horizontal Line (%1)").arg(
                resources.get_shortcut("Horizontal-line").toString(
                    QKeySequence.NativeText)))
        titleCommentAction = menuSource.addAction(
            self.tr("Insert Title Comment (%1)").arg(
                resources.get_shortcut("Title-comment").toString(
                    QKeySequence.NativeText)))
        countCodeLinesAction = menuSource.addAction(
            self.tr("Count Code Lines"))
        menuSource.addSeparator()
        tellTaleAction = menuSource.addAction(
            self.tr("Tell me a Tale of Code"))
        tellTaleAction.setEnabled(False)
        goToDefinitionAction = menuSource.addAction(
            QIcon(resources.IMAGES['go-to-definition']),
            self.tr("Go To Definition (%1 or %2+Click)").arg(
                resources.get_shortcut("Go-to-definition").toString(
                    QKeySequence.NativeText),
                settings.OS_KEY))
        insertImport = menuSource.addAction(
            QIcon(resources.IMAGES['insert-import']),
            self.tr("Insert &Import (%1)").arg(
                resources.get_shortcut("Import").toString(
                    QKeySequence.NativeText)))
#        organizeImportsAction = menuSource.addAction(
#            self.tr("&Organize Imports"))
#        removeUnusedImportsAction = menuSource.addAction(
#            self.tr("Remove Unused &Imports"))
#        extractMethodAction = menuSource.addAction(
#            self.tr("Extract selected &code as Method"))
        menuSource.addSeparator()
        removeTrailingSpaces = menuSource.addAction(
            self.tr("&Remove Trailing Spaces"))
        replaceTabsSpaces = menuSource.addAction(
            self.tr("Replace Tabs With &Spaces"))
        moveUp = menuSource.addAction(self.tr("Move &Up (%1)").arg(
            resources.get_shortcut("Move-up").toString(
                QKeySequence.NativeText)))
        moveDown = menuSource.addAction(self.tr("Move &Down (%1)").arg(
            resources.get_shortcut("Move-down").toString(
                QKeySequence.NativeText)))
        duplicate = menuSource.addAction(
            self.tr("Duplica&te (%1)").arg(
                resources.get_shortcut("Duplicate").toString(
                    QKeySequence.NativeText)))
        remove = menuSource.addAction(
            self.tr("&Remove Line (%1)").arg(
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
