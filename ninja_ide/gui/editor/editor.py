# -*- coding: utf-8 -*-
from __future__ import absolute_import

import re
import logging

from tokenize import generate_tokens, TokenError
import token as tkn
from StringIO import StringIO

from PyQt4.QtGui import QPlainTextEdit
from PyQt4.QtGui import QFontMetricsF
from PyQt4.QtGui import QToolTip
from PyQt4.QtGui import QAction
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
from ninja_ide.gui.editor import minimap
from ninja_ide.gui.editor import pep8_checker
from ninja_ide.gui.editor import errors_checker
from ninja_ide.gui.editor import sidebar_widget

BRACE_DICT = {')': '(', ']': '[', '}': '{', '(': ')', '[': ']', '{': '}'}
logger = logging.getLogger('ninja_ide.gui.editor.editor')


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
        self.extraSelections = []
        self.wordSelection = []
        self._patIsWord = re.compile('\w+')
        #Brace matching
        self._braces = None
        self._mtime = None
        self.__encoding = None
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
            Qt.Key_ParenRight: self.__brace_completion,
            Qt.Key_Apostrophe: self.__quot_completion,
            Qt.Key_QuoteDbl: self.__quot_completion}

        self.postKeyPress = {
            Qt.Key_Enter: self.__auto_indent,
            Qt.Key_Return: self.__auto_indent,
            Qt.Key_BracketLeft: self.__complete_braces,
            Qt.Key_BraceLeft: self.__complete_braces,
            Qt.Key_ParenLeft: self.__complete_braces,
            Qt.Key_Apostrophe: self.__complete_quotes,
            Qt.Key_QuoteDbl: self.__complete_quotes}

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

        self._mini = None
        if settings.SHOW_MINIMAP:
            self._mini = minimap.MiniMap(self)
            self._mini.show()
            self.connect(self, SIGNAL("updateRequest(const QRect&, int)"),
                self._mini.update_visible_area)

        #Context Menu Options
        self.__actionFindOccurrences = QAction(
            self.tr("Find Usages"), self)
        self.connect(self.__actionFindOccurrences, SIGNAL("triggered()"),
            self._find_occurrences)

    def __get_encoding(self):
        """Get the current encoding of 'utf-8' otherwise."""
        if self.__encoding is not None:
            return self.__encoding
        return 'utf-8'

    def __set_encoding(self, encoding):
        """Set the current encoding."""
        self.__encoding = encoding

    encoding = property(__get_encoding, __set_encoding)

    def set_flags(self):
        if settings.ALLOW_WORD_WRAP:
            self.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        else:
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
        if self._mini:
            self._mini.set_code(self.toPlainText())
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

    def _add_line_increment_for_dict(self, data, blockModified, diference):
        def _inner_increment(line):
            if line < blockModified:
                return line
            newLine = line + diference
            summary = data.pop(line)
            data[newLine] = summary
            return newLine
        map(_inner_increment, data.keys())
        return data

    def _update_file_metadata(self, val):
        """Update the info of bookmarks, breakpoint, pep8 and static errors."""
        if self.pep8.pep8checks or self.errors.errorsSummary or \
        self._sidebarWidget._bookmarks or self._sidebarWidget._breakpoints:
            cursor = self.textCursor()
            if self.__lines_count:
                diference = val - self.__lines_count
            else:
                diference = 0
            blockNumber = cursor.blockNumber() - diference
            if self.pep8.pep8checks:
                self.pep8.pep8checks = self._add_line_increment_for_dict(
                    self.pep8.pep8checks, blockNumber, diference)
                self._sidebarWidget._pep8Lines = self.pep8.pep8checks.keys()
            if self.errors.errorsSummary:
                self.errors.errorsSummary = self._add_line_increment_for_dict(
                    self.errors.errorsSummary, blockNumber, diference)
                self._sidebarWidget._errorsLines = \
                    self.errors.errorsSummary.keys()
            if self._sidebarWidget._breakpoints and self.ID:
                self._sidebarWidget._breakpoints = self._add_line_increment(
                    self._sidebarWidget._breakpoints, blockNumber, diference)
                settings.BREAKPOINTS[self.ID] = \
                    self._sidebarWidget._breakpoints
            if self._sidebarWidget._bookmarks and self.ID:
                self._sidebarWidget._bookmarks = self._add_line_increment(
                    self._sidebarWidget._bookmarks, blockNumber, diference)
                settings.BOOKMARKS[self.ID] = self._sidebarWidget._bookmarks
        self.__lines_count = val
        self.highlight_current_line()

    def show_pep8_errors(self):
        self._sidebarWidget.pep8_check_lines(self.pep8.pep8checks.keys())
        if self.syncDocErrorsSignal:
            self._sync_tab_icon_notification_signal()
        else:
            self.syncDocErrorsSignal = True

    def show_static_errors(self):
        self._sidebarWidget.static_errors_lines(
            self.errors.errorsSummary.keys())
        if self.syncDocErrorsSignal:
            self._sync_tab_icon_notification_signal()
        else:
            self.syncDocErrorsSignal = True

    def _sync_tab_icon_notification_signal(self):
        self.syncDocErrorsSignal = False
        if self.errors.errorsSummary:
            self.emit(SIGNAL("errorsFound(QPlainTextEdit)"), self)
        elif self.pep8.pep8checks:
            self.emit(SIGNAL("warningsFound(QPlainTextEdit)"), self)
        else:
            self.emit(SIGNAL("cleanDocument(QPlainTextEdit)"), self)
        self.highlighter.rehighlight()

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
                None, resources.CUSTOM_SCHEME, self.errors, self.pep8)
        if not syntaxLang:
            ext = file_manager.get_file_extension(self.ID)
            self.highlighter.apply_highlight(
                settings.EXTENSIONS.get(ext, 'python'),
                resources.CUSTOM_SCHEME)
            if self._mini:
                self._mini.highlighter.apply_highlight(
                    settings.EXTENSIONS.get(ext, 'python'),
                    resources.CUSTOM_SCHEME)
        else:
            self.highlighter.apply_highlight(
                str(syntaxLang), resources.CUSTOM_SCHEME)
            if self._mini:
                self._mini.highlighter.apply_highlight(
                    str(syntaxLang), resources.CUSTOM_SCHEME)

    def _file_saved(self, undoAvailable=False):
        if not undoAvailable:
            self.emit(SIGNAL("fileSaved(QPlainTextEdit)"), self)
            self.newDocument = False
            self.textModified = False
            self.document().setModified(self.textModified)

    def register_syntax(self, lang='', syntax=None):
        self.lang = settings.EXTENSIONS.get(lang, 'python')
        if lang in settings.EXTENSIONS:
            self.highlighter = highlighter.Highlighter(self.document(),
                self.lang, resources.CUSTOM_SCHEME, self.errors, self.pep8)
            if self._mini:
                self._mini.highlighter = highlighter.Highlighter(
                    self._mini.document(),
                    self.lang, resources.CUSTOM_SCHEME)
        elif syntax is not None:
            self.highlighter = highlighter.Highlighter(self.document(),
                None, resources.CUSTOM_SCHEME)
            self.highlighter.apply_highlight(lang, resources.CUSTOM_SCHEME,
                syntax)
            if self._mini:
                self._mini.highlighter = highlighter.Highlighter(
                    self.document(), None, resources.CUSTOM_SCHEME)
                self._mini.highlighter.apply_highlight(lang,
                    resources.CUSTOM_SCHEME, syntax)

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
        #line where indent_more should start and end
        block = self.document().findBlock(
            cursor.selectionStart())
        end = self.document().findBlock(
            cursor.selectionEnd()).next()

        #Start a undo block
        cursor.beginEditBlock()

        #Move the COPY cursor
        cursor.setPosition(block.position())
        while block != end:
            cursor.setPosition(block.position())
            cursor.insertText(' ' * settings.INDENT)
            block = block.next()

        #End a undo block
        cursor.endEditBlock()

    def indent_less(self):
        #cursor is a COPY all changes do not affect the QPlainTextEdit's cursor
        cursor = self.textCursor()
        if not cursor.hasSelection():
            cursor.movePosition(QTextCursor.EndOfLine)
        #line where indent_less should start and end
        block = self.document().findBlock(
            cursor.selectionStart())
        end = self.document().findBlock(
            cursor.selectionEnd()).next()

        #Start a undo block
        cursor.beginEditBlock()

        cursor.setPosition(block.position())
        while block != end:
            cursor.setPosition(block.position())
            #Select Settings.indent chars from the current line
            cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor,
                settings.INDENT)
            text = cursor.selectedText()
            if text == ' ' * settings.INDENT:
                cursor.removeSelectedText()
            block = block.next()

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
        """Find if searched text exists and replace it with new one.
        If there is a selection just doit inside it and exit.
        """
        tc = self.textCursor()
        if tc.hasSelection():
            start, end = tc.selectionStart(), tc.selectionEnd()
            text = tc.selectedText()
            old_len = len(text)
            max_replace = (not all) and 1 or -1
            text = unicode(text).replace(wordOld, wordNew, max_replace)
            new_len = len(text)
            tc.insertText(text)
            offset = new_len - old_len
            self.__set_selection_from_pair(start, end + offset)
            return

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

    def resizeEvent(self, event):
        QPlainTextEdit.resizeEvent(self, event)
        self._sidebarWidget.setFixedHeight(self.height())
        if self._mini:
            self._mini.adjust_to_parent()

    def __insert_indentation(self, event):
        if self.textCursor().hasSelection():
            self.indent_more()
        elif settings.ALLOW_TABS_NON_PYTHON and self.lang != 'python':
            return False
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
        if event.modifiers() == Qt.ControlModifier:
            return False
        elif event.modifiers() == Qt.ShiftModifier:
            move = QTextCursor.KeepAnchor
        else:
            move = QTextCursor.MoveAnchor
        if self.textCursor().atBlockStart():
            self.moveCursor(QTextCursor.WordRight, move)
            return True

    def __ignore_extended_line(self, event):
        if event.modifiers() == Qt.ShiftModifier:
            return True

    def __set_selection_from_pair(self, begin, end):
        """Set the current editor cursor with a selection from a given pair of
        positions"""
        cursor = self.textCursor()
        cursor.setPosition(begin)
        cursor.setPosition(end, QTextCursor.KeepAnchor)
        self.setTextCursor(cursor)

    def __reverse_select_text_portion_from_offset(self, begin, end):
        """Backwards select text, go from current+begin to current - end
        possition, returns text"""
        cursor = self.textCursor()
        cursor_position = cursor.position()
        cursor.setPosition(cursor_position + begin)
        #QT silently fails on invalid position, ergo breaks when EOF < begin
        while (cursor.position() == cursor_position) and begin > 0:
            begin -= 1
            cursor.setPosition(cursor_position + begin)
        cursor.setPosition(cursor_position - end, QTextCursor.KeepAnchor)
        selected_text = unicode(cursor.selectedText())
        return selected_text

    def __quot_completion(self, event):
        """Indicate if this is some sort of quote that needs to be completed
        This is a very simple boolean table, given that quotes are a
        simmetrical symbol, is a little more cumbersome guessing the completion
        table.
        """
        text = unicode(event.text())
        PENTA_Q = 5 * text
        TETRA_Q = 4 * text
        TRIPLE_Q = 3 * text
        DOUBLE_Q = 2 * text
        supress_echo = False
        pre_context = self.__reverse_select_text_portion_from_offset(0, 3)
        pos_context = self.__reverse_select_text_portion_from_offset(3, 0)
        if pre_context == pos_context == TRIPLE_Q:
            supress_echo = True
        elif pos_context[:2] == DOUBLE_Q:
            pre_context = self.__reverse_select_text_portion_from_offset(0, 4)
            if pre_context == TETRA_Q:
                supress_echo = True
        elif pos_context[:1] == text:
            pre_context = self.__reverse_select_text_portion_from_offset(0, 5)
            if pre_context == PENTA_Q:
                supress_echo = True
            elif pre_context[-1] == text:
                supress_echo = True
        if supress_echo:
            self.moveCursor(QTextCursor.Right)
        return supress_echo

    def __brace_completion(self, event):
        """Indicate if this symbol is part of a given pair and needs to be
        completed.
        """
        text = unicode(event.text())
        if text in settings.BRACES.values():
            portion = self.__reverse_select_text_portion_from_offset(1, 1)
            brace_open = portion[0]
            brace_close = (len(portion) > 1) and portion[1] or None
            balance = BRACE_DICT.get(brace_open, None) == text == brace_close
            if balance:
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
        elif settings.COMPLETE_DECLARATIONS:
            helpers.check_for_assistance_completion(self, text)

    def complete_declaration(self):
        settings.COMPLETE_DECLARATIONS = not settings.COMPLETE_DECLARATIONS
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.EndOfLine)
        if cursor.atEnd():
            cursor.insertBlock()
        self.moveCursor(QTextCursor.Down)
        self.__auto_indent(None)
        settings.COMPLETE_DECLARATIONS = not settings.COMPLETE_DECLARATIONS

    def __complete_braces(self, event):
        """Complete () [] and {} using a mild inteligence to see if corresponds
        and also do some more magic such as complete in classes and functions"""
        brace = unicode(event.text())
        if brace not in settings.BRACES:
            # Thou shalt not waste cpu cycles if this brace compleion dissabled
            return
        text = self.textCursor().block().text()
        complementary_brace = BRACE_DICT.get(brace)
        token_buffer = []
        _, tokens = self.__tokenize_text(text)
        is_unbalance = 0
        for tkn_type, tkn_rep, tkn_begin, tkn_end in tokens:
            if tkn_rep == brace:
                is_unbalance += 1
            elif tkn_rep == complementary_brace:
                is_unbalance -= 1
            if tkn_rep.strip() != "":
                token_buffer.append((tkn_rep, tkn_end[1]))
            is_unbalance = (is_unbalance >= 0) and is_unbalance or 0

        if (self.lang == "python") and (len(token_buffer) == 3) and \
                (token_buffer[2][0] == brace) and (token_buffer[0][0] in
                                                        ("def", "class")):
            #are we in presence of a function?
            self.textCursor().insertText("):")
            self.__fancyMoveCursor(QTextCursor.Left, 2)
            self.textCursor().insertText(self.selected_text)
        elif token_buffer and (not is_unbalance) and \
           self.selected_text:
            self.textCursor().insertText(self.selected_text)
        elif is_unbalance:
            self.textCursor().insertText(complementary_brace)
            self.moveCursor(QTextCursor.Left)
            self.textCursor().insertText(self.selected_text)

    def __complete_quotes(self, event):
        """
        Completion for single and double quotes, which since are simmetrical
        symbols used for different things can not be balanced as easily as
        braces or equivalent.
        """
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.StartOfLine,
            QTextCursor.KeepAnchor)
        symbol = unicode(event.text())
        if symbol in settings.QUOTES:
            pre_context = self.__reverse_select_text_portion_from_offset(0, 3)
            if pre_context == 3 * symbol:
                self.textCursor().insertText(3 * symbol)
                self.__fancyMoveCursor(QTextCursor.Left, 3)
            else:
                self.textCursor().insertText(symbol)
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
        if settings.ERRORS_HIGHLIGHT_LINE and \
        (block.blockNumber()) in self.errors.errorsSummary:
            message = '\n'.join(
                self.errors.errorsSummary[block.blockNumber()])
            QToolTip.showText(self.mapToGlobal(position),
                message, self)
        elif settings.CHECK_HIGHLIGHT_LINE and \
        (block.blockNumber()) in self.pep8.pep8checks:
            message = '\n'.join(
                self.pep8.pep8checks[block.blockNumber()])
            QToolTip.showText(self.mapToGlobal(position), message, self)
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
        text = cursor.selection().toPlainText()

        return unicode(text)

    def __get_abs_position_on_text(self, text, position):
        """tokens give us position of char in a given line, we need
        such position relative to the beginning of the text, also we need
        to add the number of lines, since our split removes the newlines
        which are counted as a character in the editor"""
        line, relative_position = position
        insplit_line = line - 1
        full_lenght = 0
        for each_line in text.splitlines()[:insplit_line]:
            full_lenght += len(each_line)
        return full_lenght + insplit_line + relative_position

    def __fancyMoveCursor(self, operation, repeat=1,
                                            moveMode=QTextCursor.MoveAnchor):
        """Move the cursor a given number of times (with or without
        anchoring), just a helper given the less than practical way qt
        has for such a common operation"""
        cursor = self.textCursor()
        cursor.movePosition(operation, moveMode, repeat)
        self.setTextCursor(cursor)

    def __tokenize_text(self, text):
        invalid_syntax = False
        token_buffer = []
        try:
            for tkn_type, tkn_rep, tkn_begin, tkn_end, _ in \
                            generate_tokens(StringIO(text).readline):
                token_buffer.append((tkn_type, tkn_rep, tkn_begin, tkn_end))
        except (TokenError, IndentationError, SyntaxError):
            invalid_syntax = True
        return (invalid_syntax, token_buffer)

    def _match_braces(self, position, brace, forward):
        """Return the position to hilight of the matching brace"""
        braceMatch = BRACE_DICT[brace]
        if forward:
            text = self.get_selection(position, QTextCursor.End)
        else:
            text = self.get_selection(QTextCursor.Start, position)
        brace_stack = []
        brace_buffer = []
        invalid_syntax, tokens = self.__tokenize_text(text)
        for tkn_type, tkn_rep, tkn_begin, tkn_end in tokens:
            if (tkn_type == tkn.OP) and (tkn_rep in BRACE_DICT):
                tkn_pos = forward and tkn_begin or tkn_end
                brace_buffer.append((tkn_rep, tkn_pos))
        if not forward:
            brace_buffer.reverse()
        if not ((not forward) and invalid_syntax):
            #Exclude the brace that triggered all this
            brace_buffer = brace_buffer[1:]

        for tkn_rep, tkn_position in brace_buffer:
            if (tkn_rep == braceMatch) and not brace_stack:
                hl_position = \
                self.__get_abs_position_on_text(text, tkn_position)
                return forward and hl_position + position or hl_position
            elif brace_stack and \
                (BRACE_DICT.get(tkn_rep, '') == brace_stack[-1]):
                brace_stack.pop(-1)
            else:
                brace_stack.append(tkn_rep)

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
        if text in (")", "]", "}"):
            pos2 = self._match_braces(pos1, text, forward=False)
        elif text in ("(", "[", "{"):
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
            self.highlighter.set_selected_word(word)
        self.highlighter.rehighlight()


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
