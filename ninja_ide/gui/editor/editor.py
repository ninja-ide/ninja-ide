# -*- coding: utf-8 -*-
from __future__ import absolute_import

import re

from PyQt4.QtGui import QPlainTextEdit
from PyQt4.QtGui import QFontMetricsF
from PyQt4.QtGui import QToolTip
from PyQt4.QtGui import QAction
from PyQt4.QtGui import QTextCharFormat
from PyQt4.QtGui import QTextOption
from PyQt4.QtGui import QTextEdit
from PyQt4.QtGui import QInputDialog
from PyQt4.QtGui import QTextCursor
from PyQt4.QtGui import QTextDocument
from PyQt4.QtGui import QTextFormat
from PyQt4.QtGui import QFont
#from PyQt4.QtGui import QMenu
from PyQt4.QtGui import QPainter
from PyQt4.QtGui import QColor
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QMimeData
from PyQt4.QtCore import Qt

from ninja_ide import resources
from ninja_ide.core import settings
from ninja_ide.core import file_manager
from ninja_ide.tools import styles
from ninja_ide.gui.main_panel import itab_item
from ninja_ide.gui.editor import highlighter
from ninja_ide.gui.editor import helpers
from ninja_ide.gui.editor import pep8_checker
from ninja_ide.gui.editor import errors_checker
from ninja_ide.gui.editor import sidebar_widget


class Editor(QPlainTextEdit, itab_item.ITabItem):

###############################################################################
# EDITOR SIGNALS
###############################################################################
    """
    modificationChanged(bool)
    fileSaved(QPlainTextEdit)
    locateFunction(QString, QString, bool) [functionName, filePath, isVariable]
    openDropFile(QString)
    addBackItemNavigation()
    warningsFound(QPlainTextEdit)
    errorsFound(QPlainTextEdit)
    cleanDocument(QPlainTextEdit)
    findOcurrences(QString)
    cursorPositionChange(int, int)    #row, col
    """
###############################################################################

    def __init__(self, filename, project):
        QPlainTextEdit.__init__(self)
        itab_item.ITabItem.__init__(self)
        #Config Editor
        self.set_flags()
        self.__lines_count = None

        self._sidebarWidget = sidebar_widget.SidebarWidget(self)
        if filename in settings.BREAKPOINTS:
            self._sidebarWidget._breakpoints = settings.BREAKPOINTS[filename]
        if filename in settings.BOOKMARKS:
            self._sidebarWidget._bookmarks = settings.BOOKMARKS[filename]
        self.pep8 = pep8_checker.Pep8Checker(self)
        self.errors = errors_checker.ErrorsChecker(self)

        self.textModified = False
        self.newDocument = True
        self.highlighter = None
        self.syncDocErrorsSignal = False
        #Set editor style
        styles.set_editor_style(self, resources.CUSTOM_SCHEME)
        self.set_font(settings.FONT_FAMILY, settings.FONT_SIZE)
        #For Highlighting in document
        self._patIsWord = re.compile('\w+')
        #Brace matching
        self._braces = None
        self._mtime = None
        self.encoding = None
        #Flag to dont bug the user when answer *the modification dialog*
        self.ask_if_externally_modified = True
        #Dict functions for KeyPress
        self.preKeyPress = {
            Qt.Key_Tab: self.__insert_indentation,
            Qt.Key_Backspace: self.__backspace,
            Qt.Key_Home: self.__home_pressed,
            Qt.Key_Enter: self.__ignore_extended_line,
            Qt.Key_Return: self.__ignore_extended_line,
            Qt.Key_BracketRight: self.__brace_completion,
            Qt.Key_BraceRight: self.__brace_completion,
            Qt.Key_ParenRight: self.__brace_completion}

        self.postKeyPress = {
            Qt.Key_Enter: self.__auto_indent,
            Qt.Key_Return: self.__auto_indent,
            Qt.Key_BracketLeft: self.__complete_braces,
            Qt.Key_BraceLeft: self.__complete_braces,
            Qt.Key_ParenLeft: self.__complete_braces,
            Qt.Key_Apostrophe: self.__complete_braces,
            Qt.Key_QuoteDbl: self.__complete_braces}

        self.connect(self, SIGNAL("updateRequest(const QRect&, int)"),
            self._sidebarWidget.update_area)
        self.connect(self, SIGNAL("undoAvailable(bool)"), self._file_saved)
        self.connect(self, SIGNAL("cursorPositionChanged()"),
            self.highlight_current_line)
        self.connect(self.pep8, SIGNAL("finished()"), self.show_pep8_errors)
        self.connect(self.errors, SIGNAL("finished()"),
            self.show_static_errors)
        self.connect(self, SIGNAL("blockCountChanged(int)"),
            self._update_file_metadata)

        #Context Menu Options
        self.__actionFindOccurrences = QAction(
            self.tr("Find Usages"), self)
        self.connect(self.__actionFindOccurrences, SIGNAL("triggered()"),
            self._find_occurrences)

    def set_flags(self):
        self.setWordWrapMode(QTextOption.NoWrap)
        self.setMouseTracking(True)
        doc = self.document()
        option = QTextOption()
        if settings.SHOW_TABS_AND_SPACES:
            option.setFlags(QTextOption.ShowTabsAndSpaces)
        doc.setDefaultTextOption(option)
        self.setDocument(doc)
        self.setCenterOnScroll(settings.CENTER_ON_SCROLL)

    def set_id(self, id_):
        super(Editor, self).set_id(id_)
        self._mtime = file_manager.get_last_modification(id_)
        if settings.CHECK_STYLE:
            self.pep8.check_style()
        if settings.FIND_ERRORS:
            self.errors.check_errors()

    def _add_line_increment(self, lines, blockModified, diference):
        def _inner_increment(line):
            if line < blockModified:
                return line
            return line + diference
        return map(_inner_increment, lines)

    def _add_line_increment_for_error(self, lines, blockModified, diference):
        def _inner_increment(line):
            if line < blockModified:
                return line
            newLine = line + diference
            summary = self.errors.errorsSummary.pop(line)
            self.errors.errorsSummary[newLine] = summary
            return newLine
        return map(_inner_increment, lines)

    def _update_file_metadata(self, val):
        """Update the info of bookmarks, breakpoint, pep8 and static errors."""
        if self.pep8.pep8lines or self.errors.errorsLines or \
        self._sidebarWidget._bookmarks or self._sidebarWidget._breakpoints:
            cursor = self.textCursor()
            if self.__lines_count:
                diference = val - self.__lines_count
            else:
                diference = 0
            blockNumber = cursor.blockNumber() - diference
            if self.pep8.pep8lines:
                self.pep8.pep8lines = self._add_line_increment(
                    self.pep8.pep8lines, blockNumber, diference)
                self._sidebarWidget._pep8Lines = self.pep8.pep8lines
            if self.errors.errorsLines:
                self.errors.errorsLines = self._add_line_increment_for_error(
                    self.errors.errorsLines, blockNumber, diference)
                self._sidebarWidget._errorsLines = self.errors.errorsLines
            if self._sidebarWidget._breakpoints:
                self._sidebarWidget._breakpoints = self._add_line_increment(
                    self._sidebarWidget._breakpoints, blockNumber, diference)
                settings.BREAKPOINTS[self.ID] = \
                    self._sidebarWidget._breakpoints
            if self._sidebarWidget._bookmarks:
                self._sidebarWidget._bookmarks = self._add_line_increment(
                    self._sidebarWidget._bookmarks, blockNumber, diference)
                settings.BOOKMARKS[self.ID] = self._sidebarWidget._bookmarks
        self.__lines_count = val
        self.highlight_current_line()

    def show_pep8_errors(self):
        self._sidebarWidget.pep8_check_lines(self.pep8.pep8lines)
        if self.syncDocErrorsSignal:
            self._sync_tab_icon_notification_signal()
        else:
            self.syncDocErrorsSignal = True

    def show_static_errors(self):
        self._sidebarWidget.static_errors_lines(self.errors.errorsLines)
        if self.syncDocErrorsSignal:
            self._sync_tab_icon_notification_signal()
        else:
            self.syncDocErrorsSignal = True

    def _sync_tab_icon_notification_signal(self):
        self.syncDocErrorsSignal = False
        if self.errors.errorsLines:
            self.emit(SIGNAL("errorsFound(QPlainTextEdit)"), self)
        elif self.pep8.pep8lines:
            self.emit(SIGNAL("warningsFound(QPlainTextEdit)"), self)
        else:
            self.emit(SIGNAL("cleanDocument(QPlainTextEdit)"), self)

    def check_external_modification(self):
        if self.newDocument:
            return False
        #Saved document we can ask for modification!
        return file_manager.check_for_external_modification(
            self.get_id(), self._mtime)

    def has_write_permission(self):
        if self.newDocument:
            return True
        return file_manager.has_write_permission(self.ID)

    def restyle(self, syntaxLang=None):
        styles.set_editor_style(self, resources.CUSTOM_SCHEME)
        if self.highlighter is None:
            self.highlighter = highlighter.Highlighter(self.document(),
                None, resources.CUSTOM_SCHEME)
        if not syntaxLang:
            ext = file_manager.get_file_extension(self.ID)
            self.highlighter.apply_highlight(
                settings.EXTENSIONS.get(ext, 'python'),
                resources.CUSTOM_SCHEME)
        else:
            self.highlighter.apply_highlight(
                str(syntaxLang), resources.CUSTOM_SCHEME)

    def _file_saved(self, undoAvailable=False):
        if not undoAvailable:
            self.emit(SIGNAL("fileSaved(QPlainTextEdit)"), self)
            self.newDocument = False
            self.textModified = False
            self.document().setModified(self.textModified)

    def register_syntax(self, lang='', syntax=None):
        if lang in settings.EXTENSIONS:
            self.highlighter = highlighter.Highlighter(self.document(),
                settings.EXTENSIONS.get(lang, 'python'),
                    resources.CUSTOM_SCHEME)
        elif syntax is not None:
            self.highlighter = highlighter.Highlighter(self.document(),
                None, resources.CUSTOM_SCHEME)
            self.highlighter.apply_highlight(lang, resources.CUSTOM_SCHEME,
                syntax)

    def get_text(self):
        """
        Returns all the plain text of the editor
        """
        return self.toPlainText()

    def get_lines_count(self):
        """
        Returns the count of lines in the editor
        """
        return self.textCursor().document().lineCount()

    def set_font(self, family=settings.FONT_FAMILY, size=settings.FONT_SIZE):
        font = QFont(family, size)
        self.document().setDefaultFont(font)
        # Fix for older version of Qt which doens't has ForceIntegerMetrics
        if "ForceIntegerMetrics" in dir(QFont):
            self.document().defaultFont().setStyleStrategy(
                QFont.ForceIntegerMetrics)

    def jump_to_line(self, lineno=None):
        """
        Jump to a specific line number or ask to the user for the line
        """
        """
        try:
            lineno = int(lineno)
            self.emit(SIGNAL("addBackItemNavigation()"))
            self.go_to_line(lineno)
            return
        except ValueError:
            #ask the line and go!
        """
        if lineno is not None:
            self.emit(SIGNAL("addBackItemNavigation()"))
            self.go_to_line(lineno)
            return

        max = self.blockCount()
        line = QInputDialog.getInt(self, self.tr("Jump to Line"),
            self.tr("Line:"), 1, 1, max, 1)
        if line[1]:
            self.emit(SIGNAL("addBackItemNavigation()"))
            self.go_to_line(line[0] - 1)

    def _find_occurrences(self):
        word = self._text_under_cursor()
        self.emit(SIGNAL("findOcurrences(QString)"), word)

    def go_to_line(self, lineno):
        """
        Go to an specific line
        """
        cursor = self.textCursor()
        cursor.setPosition(self.document().findBlockByLineNumber(
            lineno).position())
        self.setTextCursor(cursor)

    def zoom_in(self):
        font = self.document().defaultFont()
        size = font.pointSize()
        if size < settings.FONT_MAX_SIZE:
            size += 2
            font.setPointSize(size)
        self.setFont(font)

    def zoom_out(self):
        font = self.document().defaultFont()
        size = font.pointSize()
        if size > settings.FONT_MIN_SIZE:
            size -= 2
            font.setPointSize(size)
        self.setFont(font)

    def get_parent_project(self):
        return ''

    def get_cursor_position(self):
        return self.textCursor().position()

    def set_cursor_position(self, pos):
        cursor = self.textCursor()
        cursor.setPosition(pos)
        self.setTextCursor(cursor)

    def indent_more(self):
        #cursor is a COPY all changes do not affect the QPlainTextEdit's cursor
        cursor = self.textCursor()
        selectionStart = cursor.selectionStart()
        selectionEnd = cursor.selectionEnd()
        #line where indent_more should start and end
        start = self.document().findBlock(
            cursor.selectionStart()).firstLineNumber()
        end = self.document().findBlock(
            cursor.selectionEnd()).firstLineNumber()
        startPosition = self.document().findBlockByLineNumber(start).position()

        #Start a undo block
        cursor.beginEditBlock()

        #Decide which lines will be indented
        cursor.setPosition(selectionEnd)
        self.setTextCursor(cursor)
        #Select one char at left
        #If there is a newline \u2029 (\n) then skip it
        self.moveCursor(QTextCursor.Left, QTextCursor.KeepAnchor)
        if u'\u2029' in self.textCursor().selectedText():
            end -= 1

        cursor.setPosition(selectionStart)
        self.setTextCursor(cursor)
        self.moveCursor(QTextCursor.StartOfLine)
        #Indent loop; line by line
        for i in xrange(start, end + 1):
            self.textCursor().insertText(' ' * settings.INDENT)
            self.moveCursor(QTextCursor.Down, QTextCursor.MoveAnchor)

        #Restore the user selection
        cursor.setPosition(startPosition)
        selectionEnd = selectionEnd + \
            (settings.INDENT * (end - start + 1))
        cursor.setPosition(selectionEnd, QTextCursor.KeepAnchor)
        self.setTextCursor(cursor)
        #End a undo block
        cursor.endEditBlock()

    def indent_less(self):
        #save the total of movements made after indent_less
        totalIndent = 0
        #cursor is a COPY all changes do not affect the QPlainTextEdit's cursor
        cursor = self.textCursor()
        if not cursor.hasSelection():
            cursor.movePosition(QTextCursor.EndOfLine)
        selectionEnd = cursor.selectionEnd()
        #line where indent_less should start and end
        start = self.document().findBlock(
            cursor.selectionStart()).firstLineNumber()
        end = self.document().findBlock(
            cursor.selectionEnd()).firstLineNumber()
        startPosition = self.document().findBlockByLineNumber(start).position()

        #Start a undo block
        cursor.beginEditBlock()

        #Decide which lines will be indented_less
        cursor.setPosition(selectionEnd)
        self.setTextCursor(cursor)
        #Select one char at left
        self.moveCursor(QTextCursor.Left, QTextCursor.KeepAnchor)
        #If there is a newline \u2029 (\n) then dont indent this line; skip it!
        if u'\u2029' in self.textCursor().selectedText():
            end -= 1

        cursor.setPosition(startPosition)
        self.setTextCursor(cursor)
        self.moveCursor(QTextCursor.StartOfLine)
        #Indent_less loop; line by line
        for i in xrange(start, end + 1):
            #Select Settings.indent chars from the current line
            for j in xrange(settings.INDENT):
                self.moveCursor(QTextCursor.Right, QTextCursor.KeepAnchor)

            text = self.textCursor().selectedText()
            if text == ' ' * settings.INDENT:
                self.textCursor().removeSelectedText()
                totalIndent += settings.INDENT
            elif u'\u2029' in text:
                #\u2029 is the unicode char for \n
                #if there is a newline, rollback the selection made above.
                for j in xrange(settings.INDENT):
                    self.moveCursor(QTextCursor.Left, QTextCursor.KeepAnchor)

            #Go Down to the next line!
            self.moveCursor(QTextCursor.Down)
        #Restore the user selection
        cursor.setPosition(startPosition)
        cursor.setPosition(selectionEnd - totalIndent, QTextCursor.KeepAnchor)
        self.setTextCursor(cursor)
        #End a undo block
        cursor.endEditBlock()

    def find_match(self, word, flags, findNext=False):
        flags = QTextDocument.FindFlags(flags)
        if findNext:
            self.moveCursor(QTextCursor.NoMove, QTextCursor.KeepAnchor)
        else:
            self.moveCursor(QTextCursor.StartOfWord, QTextCursor.KeepAnchor)
        found = self.find(word, flags)
        if not found:
            cursor = self.textCursor()
            self.moveCursor(QTextCursor.Start)
            found = self.find(word, flags)
            if not found:
                self.setTextCursor(cursor)

    def replace_match(self, wordOld, wordNew, flags, all=False):
        flags = QTextDocument.FindFlags(flags)
        self.moveCursor(QTextCursor.NoMove, QTextCursor.KeepAnchor)

        cursor = self.textCursor()
        cursor.beginEditBlock()

        self.moveCursor(QTextCursor.Start)
        replace = True
        while (replace or all):
            result = False
            result = self.find(wordOld, flags)

            if result:
                tc = self.textCursor()
                if tc.hasSelection():
                    tc.insertText(wordNew)
            else:
                break
            replace = False

        cursor.endEditBlock()

    def focusInEvent(self, event):
        super(Editor, self).focusInEvent(event)
        #use parent().parent() to Access QTabWidget
        #First parent() = QStackedWidget, Second parent() = TabWidget
        self.parent().parent().focusInEvent(event)
        #Check for modifications

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Control:
            self.highlight_current_line()
            self.highlight_selected_word()
        QPlainTextEdit.keyReleaseEvent(self, event)

    def resizeEvent(self, event):
        QPlainTextEdit.resizeEvent(self, event)
        self._sidebarWidget.setFixedHeight(self.height())

    def __insert_indentation(self, event):
        if self.textCursor().hasSelection():
            self.indent_more()
        else:
            self.textCursor().insertText(' ' * settings.INDENT)
        return True

    def __backspace(self, event):
        if self.textCursor().hasSelection():
            return False
        for i in xrange(settings.INDENT):
            self.moveCursor(QTextCursor.Left, QTextCursor.KeepAnchor)
        text = self.textCursor().selection()
        if unicode(text.toPlainText()) == ' ' * settings.INDENT:
            self.textCursor().removeSelectedText()
            return True
        else:
            for i in xrange(text.toPlainText().size()):
                self.moveCursor(QTextCursor.Right)

    def __home_pressed(self, event):
        if event.modifiers() == Qt.ShiftModifier:
            move = QTextCursor.KeepAnchor
        else:
            move = QTextCursor.MoveAnchor
        if self.textCursor().atBlockStart():
            self.moveCursor(QTextCursor.WordRight, move)
            return True

    def __ignore_extended_line(self, event):
        if event.modifiers() == Qt.ShiftModifier:
            return True

    def __brace_completion(self, event):
        if unicode(event.text()) in \
        (set(settings.BRACES.values()) - set(["'", '"'])):
            cursor = self.textCursor()
            cursor.setPosition(cursor.position() + 1)
            cursor.setPosition(cursor.position() - 2, QTextCursor.KeepAnchor)
            brace = unicode(cursor.selectedText())
            if brace == ('%s%s' % (brace[0],
            settings.BRACES.get(brace[0], ''))) and brace[1] == event.text():
                self.moveCursor(QTextCursor.Right)
                return True

    def __auto_indent(self, event):
        text = unicode(self.textCursor().block().previous().text())
        spaces = helpers.get_indentation(text)
        self.textCursor().insertText(spaces)
        if text != '' and text == ' ' * len(text):
            self.moveCursor(QTextCursor.Up)
            self.moveCursor(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
            self.textCursor().removeSelectedText()
            self.moveCursor(QTextCursor.Down)
        else:
            helpers.check_for_assistance_completion(self, text)

    def __complete_braces(self, event):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.StartOfLine,
            QTextCursor.KeepAnchor)
#        if not settings.ENABLE_COMPLETION_IN_COMMENTS and \
#        cursor.selectedText().contains("#"):
#            return
        self.textCursor().insertText(settings.BRACES[unicode(event.text())])
        self.moveCursor(QTextCursor.Left)
        self.textCursor().insertText(self.selected_text)

    def keyPressEvent(self, event):
        #On Return == True stop the execution of this method
        if self.preKeyPress.get(event.key(), lambda x: False)(event):
            #emit a signal then plugings can do something
            self.emit(SIGNAL("keyPressEvent(QEvent)"), event)
            return
        self.selected_text = self.textCursor().selectedText()

        QPlainTextEdit.keyPressEvent(self, event)

        self.postKeyPress.get(event.key(), lambda x: False)(event)

        #emit a signal then plugings can do something
        self.emit(SIGNAL("keyPressEvent(QEvent)"), event)

    def _text_under_cursor(self):
        tc = self.textCursor()
        tc.select(QTextCursor.WordUnderCursor)
        return tc.selectedText()

    def paintEvent(self, event):
        super(Editor, self).paintEvent(event)
        if settings.SHOW_MARGIN_LINE:
            painter = QPainter()
            painter.begin(self.viewport())
            painter.setPen(QColor('#FE9E9A'))
            posX = QFontMetricsF(self.document().defaultFont()).width(' ') \
                                        * settings.MARGIN_LINE
            offset = self.contentOffset()
            painter.drawLine(posX + offset.x(), 0, \
                posX + offset.x(), self.viewport().height())
            painter.end()

    def wheelEvent(self, event, forward=True):
        if event.modifiers() == Qt.ControlModifier:
            if event.delta() == 120:
                self.zoom_in()
            elif event.delta() == -120:
                self.zoom_out()
            event.ignore()
        QPlainTextEdit.wheelEvent(self, event)

    def contextMenuEvent(self, event):
        popup_menu = self.createStandardContextMenu()

#        menuRefactor = QMenu(self.tr("Refactor"))
#        extractMethodAction = menuRefactor.addAction(
#            self.tr("Extract as Method"))
#        organizeImportsAction = menuRefactor.addAction(
#            self.tr("Organize Imports"))
#        removeUnusedAction = menuRefactor.addAction(
#            self.tr("Remove Unused Imports"))
        #TODO
#        self.connect(organizeImportsAction, SIGNAL("triggered()"),
#            self.organize_imports)
#        self.connect(removeUnusedAction, SIGNAL("triggered()"),
#            self.remove_unused_imports)
#        self.connect(extractMethodAction, SIGNAL("triggered()"),
#            self.extract_method)
        popup_menu.insertSeparator(popup_menu.actions()[0])
#        popup_menu.insertMenu(popup_menu.actions()[0], menuRefactor)
        popup_menu.insertAction(popup_menu.actions()[0],
            self.__actionFindOccurrences)
        #add extra menus (from Plugins)
        lang = file_manager.get_file_extension(self.ID)
        extra_menus = self.EXTRA_MENU.get(lang, None)
        if extra_menus:
            popup_menu.addSeparator()
            for menu in extra_menus:
                popup_menu.addMenu(menu)
        #show menu
        popup_menu.exec_(event.globalPos())

    def mouseMoveEvent(self, event):
        position = event.pos()
        cursor = self.cursorForPosition(position)
        block = cursor.block()
        if (block.blockNumber() + 1) in self.errors.errorsLines:
            QToolTip.showText(self.mapToGlobal(position),
                self.errors.errorsSummary[(block.blockNumber() + 1)], self)
        elif (block.blockNumber() + 1) in self.pep8.pep8lines:
            index = self.pep8.pep8lines.index(block.blockNumber() + 1)
            QToolTip.showText(self.mapToGlobal(position),
                self.pep8.pep8checks[index], self)
        if event.modifiers() == Qt.ControlModifier:
            cursor.select(QTextCursor.WordUnderCursor)
            cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor)
            if cursor.selectedText().endsWith('(') or \
            cursor.selectedText().endsWith('.'):
                cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor)
                self.extraSelections = []
                selection = QTextEdit.ExtraSelection()
                lineColor = QColor(resources.CUSTOM_SCHEME.get('linkNavigate',
                            resources.COLOR_SCHEME['linkNavigate']))
                selection.format.setForeground(lineColor)
                selection.format.setFontUnderline(True)
                selection.cursor = cursor
                self.extraSelections.append(selection)
                self.setExtraSelections(self.extraSelections)
            else:
                self.extraSelections = []
                self.setExtraSelections(self.extraSelections)
        QPlainTextEdit.mouseMoveEvent(self, event)

    def mousePressEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            cursor = self.cursorForPosition(event.pos())
            self.setTextCursor(cursor)
            self.go_to_definition(cursor)
        elif event.button() == Qt.RightButton and \
        not self.textCursor().hasSelection():
            cursor = self.cursorForPosition(event.pos())
            self.setTextCursor(cursor)
        QPlainTextEdit.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        QPlainTextEdit.mouseReleaseEvent(self, event)
        if event.button() == Qt.LeftButton:
            self.highlight_selected_word()

    def dropEvent(self, event):
        if len(event.mimeData().urls()) > 0:
            path = event.mimeData().urls()[0].path()
            self.emit(SIGNAL("openDropFile(QString)"), path)
            event.ignore()
            event.mimeData = QMimeData()
        QPlainTextEdit.dropEvent(self, event)
        self.undo()

    def go_to_definition(self, cursor=None):
        if not cursor:
            cursor = self.textCursor()
        cursor.select(QTextCursor.WordUnderCursor)
        cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor)
        if cursor.selectedText().endsWith('('):
            cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor)
            self.emit(SIGNAL("locateFunction(QString, QString, bool)"),
                cursor.selectedText(), self.ID, False)
        elif cursor.selectedText().endsWith('.'):
            cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor)
            self.emit(SIGNAL("locateFunction(QString, QString, bool)"),
                cursor.selectedText(), self.ID, True)

    def get_selection(self, posStart, posEnd):
        cursor = self.textCursor()
        cursor.setPosition(posStart)
        cursor2 = self.textCursor()
        if posEnd == QTextCursor.End:
            cursor2.movePosition(posEnd)
            cursor.setPosition(cursor2.position(), QTextCursor.KeepAnchor)
        else:
            cursor.setPosition(posEnd, QTextCursor.KeepAnchor)
        text = cursor.selectedText()
        return unicode(text)

    def _match_braces(self, position, brace, forward):
        """based on: http://gitorious.org/khteditor"""
        if forward:
            braceMatch = {'(': ')', '[': ']', '{': '}'}
            text = self.get_selection(position, QTextCursor.End)
            braceOpen, braceClose = 1, 1
        else:
            braceMatch = {')': '(', ']': '[', '}': '{'}
            text = self.get_selection(QTextCursor.Start, position)
            braceOpen, braceClose = len(text) - 1, len(text) - 1
        while True:
            if forward:
                posClose = text.find(braceMatch[brace], braceClose)
            else:
                posClose = text.rfind(braceMatch[brace], 0, braceClose + 1)
            if posClose > -1:
                if forward:
                    braceClose = posClose + 1
                    posOpen = text.find(brace, braceOpen, posClose)
                else:
                    braceClose = posClose - 1
                    posOpen = text.rfind(brace, posClose, braceOpen + 1)
                if posOpen > -1:
                    if forward:
                        braceOpen = posOpen + 1
                    else:
                        braceOpen = posOpen - 1
                else:
                    if forward:
                        return position + posClose
                    else:
                        return position - (len(text) - posClose)
            else:
                return

    def highlight_current_line(self):
        self.emit(SIGNAL("cursorPositionChange(int, int)"),
            self.textCursor().blockNumber() + 1,
            self.textCursor().columnNumber())
        self.extraSelections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            lineColor = QColor(resources.CUSTOM_SCHEME.get('current-line',
                        resources.COLOR_SCHEME['current-line']))
            lineColor.setAlpha(20)
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            self.extraSelections.append(selection)
        self.setExtraSelections(self.extraSelections)

        #Find Errors
        if settings.ERRORS_HIGHLIGHT_LINE and \
        len(self.errors.errorsLines) < settings.MAX_HIGHLIGHT_ERRORS:
            cursor = self.textCursor()
            for lineno in self.errors.errorsLines:
                block = self.document().findBlockByLineNumber(lineno - 1)
                if not block.isValid():
                    continue
                cursor.setPosition(block.position())
                selection = QTextEdit.ExtraSelection()
                selection.format.setUnderlineColor(QColor(
                    resources.CUSTOM_SCHEME.get('error-underline',
                    resources.COLOR_SCHEME['error-underline'])))
                selection.format.setUnderlineStyle(
                    QTextCharFormat.WaveUnderline)
                selection.cursor = cursor
                selection.cursor.movePosition(QTextCursor.EndOfBlock,
                    QTextCursor.KeepAnchor)
                self.extraSelections.append(selection)
            if self.errors.errorsLines:
                self.setExtraSelections(self.extraSelections)

        #Check Style
        if settings.CHECK_HIGHLIGHT_LINE and \
        len(self.pep8.pep8lines) < settings.MAX_HIGHLIGHT_ERRORS:
            cursor = self.textCursor()
            for xline, line in enumerate(self.pep8.pep8lines):
                block = self.document().findBlockByLineNumber(line - 1)
                if not block.isValid():
                    continue
                cursor.setPosition(block.position())
                selection = QTextEdit.ExtraSelection()
                selection.format.setToolTip(self.pep8.pep8checks[xline])
                selection.format.setUnderlineColor(QColor(
                    resources.CUSTOM_SCHEME.get('pep8-underline',
                    resources.COLOR_SCHEME['pep8-underline'])))
                selection.format.setUnderlineStyle(
                    QTextCharFormat.WaveUnderline)
                selection.cursor = cursor
                selection.cursor.movePosition(QTextCursor.EndOfBlock,
                    QTextCursor.KeepAnchor)
                self.extraSelections.append(selection)
            if self.pep8.pep8lines:
                self.setExtraSelections(self.extraSelections)

        #Re-position tooltip to allow text editing in the line of the error
        if QToolTip.isVisible():
            QToolTip.hideText()

        if self._braces is not None:
            self._braces = None
        cursor = self.textCursor()
        if cursor.position() == 0:
            self.setExtraSelections(self.extraSelections)
            return
        cursor.movePosition(QTextCursor.PreviousCharacter,
                             QTextCursor.KeepAnchor)
        text = unicode(cursor.selectedText())
        pos1 = cursor.position()
        if text in (')', ']', '}'):
            pos2 = self._match_braces(pos1, text, forward=False)
        elif text in ('(', '[', '{'):
            pos2 = self._match_braces(pos1, text, forward=True)
        else:
            self.setExtraSelections(self.extraSelections)
            return
        if pos2 is not None:
            self._braces = (pos1, pos2)
            selection = QTextEdit.ExtraSelection()
            selection.format.setForeground(QColor(
                resources.CUSTOM_SCHEME.get('brace-foreground',
                resources.COLOR_SCHEME.get('brace-foreground'))))
            selection.format.setBackground(QColor(
                resources.CUSTOM_SCHEME.get('brace-background',
                resources.COLOR_SCHEME.get('brace-background'))))
            selection.cursor = cursor
            self.extraSelections.append(selection)
            selection = QTextEdit.ExtraSelection()
            selection.format.setForeground(QColor(
                resources.CUSTOM_SCHEME.get('brace-foreground',
                resources.COLOR_SCHEME.get('brace-foreground'))))
            selection.format.setBackground(QColor(
                resources.CUSTOM_SCHEME.get('brace-background',
                resources.COLOR_SCHEME.get('brace-background'))))
            selection.cursor = self.textCursor()
            selection.cursor.setPosition(pos2)
            selection.cursor.movePosition(QTextCursor.NextCharacter,
                             QTextCursor.KeepAnchor)
            self.extraSelections.append(selection)
        else:
            self._braces = (pos1,)
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(QColor(
                resources.CUSTOM_SCHEME.get('brace-background',
                resources.COLOR_SCHEME.get('brace-background'))))
            selection.format.setForeground(QColor(
                resources.CUSTOM_SCHEME.get('brace-foreground',
                resources.COLOR_SCHEME.get('brace-foreground'))))
            selection.cursor = cursor
            self.extraSelections.append(selection)
        self.setExtraSelections(self.extraSelections)

    def highlight_selected_word(self):
        #Highlight selected variable
        if not self.isReadOnly() and not self.textCursor().hasSelection():
            word = self._text_under_cursor()
            if self._patIsWord.match(word):
                lineColor = QColor(
                    resources.CUSTOM_SCHEME.get('selected-word',
                        resources.COLOR_SCHEME['selected-word']))
                lineColor.setAlpha(100)
                block = self.document().findBlock(0)
                cursor = self.document().find(word, block.position(),
                    QTextDocument.FindCaseSensitively or \
                    QTextDocument.FindWholeWords)
                while block.isValid() and \
                  block.blockNumber() <= self._sidebarWidget.highest_line \
                  and cursor.position() != -1:
                    selection = QTextEdit.ExtraSelection()
                    selection.format.setBackground(lineColor)
                    selection.cursor = cursor
                    self.extraSelections.append(selection)
                    cursor = self.document().find(word, cursor.position(),
                        QTextDocument.FindCaseSensitively or \
                        QTextDocument.FindWholeWords)
                    block = block.next()
        self.setExtraSelections(self.extraSelections)


def create_editor(fileName='', project=None, syntax=None):
    editor = Editor(fileName, project)
    #if syntax is specified, use it
    if syntax:
        editor.register_syntax(syntax)
    else:
        #try to set a syntax based on the file extension
        ext = file_manager.get_file_extension(fileName)
        if ext not in settings.EXTENSIONS and fileName == '':
            #by default use python syntax
            editor.register_syntax('py')
        else:
            editor.register_syntax(ext)
    return editor
