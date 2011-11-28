# *-* coding: utf-8 *-*
from __future__ import absolute_import

from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QTextCursor
from PyQt4.QtGui import QKeySequence
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QObject

from ninja_ide import resources
from ninja_ide.core import settings
from ninja_ide.gui.main_panel import main_container
from ninja_ide.gui.misc import misc_container
from ninja_ide.gui import status_bar
from ninja_ide.gui.dialogs import preferences


class MenuEdit(QObject):

    def __init__(self, menuEdit, toolbar):
        QObject.__init__(self)

        undoAction = menuEdit.addAction(QIcon(resources.IMAGES['undo']),
            self.tr("Undo (%1+Z)").arg(settings.OS_KEY))
        redoAction = menuEdit.addAction(QIcon(resources.IMAGES['redo']),
            self.tr("Redo (%1)").arg(
                resources.get_shortcut("Redo").toString(
                    QKeySequence.NativeText)))
        cutAction = menuEdit.addAction(QIcon(resources.IMAGES['cut']),
            self.tr("&Cut (%1+X)").arg(settings.OS_KEY))
        copyAction = menuEdit.addAction(QIcon(resources.IMAGES['copy']),
            self.tr("&Copy (%1+C)").arg(settings.OS_KEY))
        pasteAction = menuEdit.addAction(QIcon(resources.IMAGES['paste']),
            self.tr("&Paste (%1+V)").arg(settings.OS_KEY))
        menuEdit.addSeparator()
        findAction = menuEdit.addAction(QIcon(resources.IMAGES['find']),
            self.tr("Find (%1)").arg(
                resources.get_shortcut("Find").toString(
                    QKeySequence.NativeText)))
        findReplaceAction = menuEdit.addAction(
            QIcon(resources.IMAGES['findReplace']),
            self.tr("Find/Replace (%1)").arg(
                resources.get_shortcut("Find-replace").toString(
                    QKeySequence.NativeText)))
        findWithWordAction = menuEdit.addAction(
            self.tr("Find using word under cursor (%1)").arg(
                resources.get_shortcut("Find-with-word").toString(
                    QKeySequence.NativeText)))
        findInFilesAction = menuEdit.addAction(QIcon(resources.IMAGES['find']),
            self.tr("Find in Files (%1)").arg(
                resources.get_shortcut("Find-in-files").toString(
                    QKeySequence.NativeText)))
        jumpAction = menuEdit.addAction(
            self.tr("Jump to Line (%1)").arg(
                resources.get_shortcut("Jump").toString(
                    QKeySequence.NativeText)))
        locatorAction = menuEdit.addAction(QIcon(resources.IMAGES['locator']),
            self.tr("Code Locator (%1)").arg(
                resources.get_shortcut("Code-locator").toString(
                    QKeySequence.NativeText)))
        menuEdit.addSeparator()
        upperAction = menuEdit.addAction(
            self.tr("Convert selected Text to: UPPER"))
        lowerAction = menuEdit.addAction(
            self.tr("Convert selected Text to: lower"))
        titleAction = menuEdit.addAction(
            self.tr("Convert selected Text to: Title Word"))
        menuEdit.addSeparator()
        prefAction = menuEdit.addAction(QIcon(resources.IMAGES['pref']),
            self.tr("Preference&s"))

        self.toolbar_items = {
            'undo': undoAction,
            'redo': redoAction,
            'cut': cutAction,
            'copy': copyAction,
            'paste': pasteAction,
            'find': findAction,
            'find-replace': findReplaceAction,
            'find-files': findInFilesAction,
            'code-locator': locatorAction}

        self.connect(cutAction, SIGNAL("triggered()"), self._editor_cut)
        self.connect(copyAction, SIGNAL("triggered()"), self._editor_copy)
        self.connect(pasteAction, SIGNAL("triggered()"), self._editor_paste)
        self.connect(redoAction, SIGNAL("triggered()"), self._editor_redo)
        self.connect(undoAction, SIGNAL("triggered()"), self._editor_undo)
        self.connect(upperAction, SIGNAL("triggered()"), self._editor_upper)
        self.connect(lowerAction, SIGNAL("triggered()"), self._editor_lower)
        self.connect(titleAction, SIGNAL("triggered()"), self._editor_title)
        self.connect(findAction, SIGNAL("triggered()"),
            status_bar.StatusBar().show)
        self.connect(findWithWordAction, SIGNAL("triggered()"),
            status_bar.StatusBar().show_with_word)
        self.connect(jumpAction, SIGNAL("triggered()"),
            lambda: self.jump_to_editor_line())
        self.connect(findReplaceAction, SIGNAL("triggered()"),
            status_bar.StatusBar().show_replace)
        self.connect(findInFilesAction, SIGNAL("triggered()"),
            self._show_find_in_files)
        self.connect(locatorAction, SIGNAL("triggered()"),
            status_bar.StatusBar().show_locator)
        self.connect(prefAction, SIGNAL("triggered()"), self._show_preferences)

    def _editor_upper(self):
        editorWidget = main_container.MainContainer().get_actual_editor()
        if editorWidget:
            editorWidget.textCursor().beginEditBlock()
            if editorWidget.textCursor().hasSelection():
                text = unicode(
                    editorWidget.textCursor().selectedText()).upper()
            else:
                text = unicode(editorWidget._text_under_cursor()).upper()
                editorWidget.moveCursor(QTextCursor.StartOfWord)
                editorWidget.moveCursor(QTextCursor.EndOfWord,
                    QTextCursor.KeepAnchor)
            editorWidget.textCursor().insertText(text)
            editorWidget.textCursor().endEditBlock()

    def _editor_lower(self):
        editorWidget = main_container.MainContainer().get_actual_editor()
        if editorWidget:
            editorWidget.textCursor().beginEditBlock()
            if editorWidget.textCursor().hasSelection():
                text = unicode(
                    editorWidget.textCursor().selectedText()).lower()
            else:
                text = unicode(editorWidget._text_under_cursor()).lower()
                editorWidget.moveCursor(QTextCursor.StartOfWord)
                editorWidget.moveCursor(QTextCursor.EndOfWord,
                    QTextCursor.KeepAnchor)
            editorWidget.textCursor().insertText(text)
            editorWidget.textCursor().endEditBlock()

    def _editor_title(self):
        editorWidget = main_container.MainContainer().get_actual_editor()
        if editorWidget:
            editorWidget.textCursor().beginEditBlock()
            if editorWidget.textCursor().hasSelection():
                text = unicode(
                    editorWidget.textCursor().selectedText()).title()
            else:
                text = unicode(editorWidget._text_under_cursor()).title()
                editorWidget.moveCursor(QTextCursor.StartOfWord)
                editorWidget.moveCursor(QTextCursor.EndOfWord,
                    QTextCursor.KeepAnchor)
            editorWidget.textCursor().insertText(text)
            editorWidget.textCursor().endEditBlock()

    def _editor_cut(self):
        editorWidget = main_container.MainContainer().get_actual_editor()
        if editorWidget:
            editorWidget.cut()

    def _editor_copy(self):
        editorWidget = main_container.MainContainer().get_actual_editor()
        if editorWidget:
            editorWidget.copy()

    def _editor_paste(self):
        editorWidget = main_container.MainContainer().get_actual_editor()
        if editorWidget:
            editorWidget.paste()

    def _editor_redo(self):
        editorWidget = main_container.MainContainer().get_actual_editor()
        if editorWidget:
            editorWidget.redo()

    def _editor_undo(self):
        editorWidget = main_container.MainContainer().get_actual_editor()
        if editorWidget:
            editorWidget.undo()

    def jump_to_editor_line(self):
        editor = main_container.MainContainer().get_actual_editor()
        if editor:
            editor.jump_to_line()

    def _show_preferences(self):
        pref = preferences.PreferencesWidget(main_container.MainContainer())
        pref.show()

    def _show_find_in_files(self):
        misc_container.MiscContainer().show_find_in_files_widget()
