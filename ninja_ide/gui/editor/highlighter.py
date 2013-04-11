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
# based on Python Syntax highlighting from:
# http://diotavelli.net/PyQtWiki/Python%20syntax%20highlighting
from __future__ import absolute_import
from __future__ import unicode_literals

import re

from PyQt4.QtGui import QColor
from PyQt4.QtGui import QTextCharFormat
from PyQt4.QtGui import QFont
from PyQt4.QtGui import QSyntaxHighlighter
from PyQt4.QtCore import QThread
from PyQt4.QtCore import QRegExp
from PyQt4.QtCore import SIGNAL

from ninja_ide import resources
from ninja_ide.core import settings
from ninja_ide.gui.editor import syntax_highlighter


def format(color, style=''):
    """Return a QTextCharFormat with the given attributes."""
    _color = QColor()
    _color.setNamedColor(color)

    _format = QTextCharFormat()
    _format.setFontFamily(settings.FONT_FAMILY)
    _format.setForeground(_color)
    if 'bold' in style:
        _format.setFontWeight(QFont.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)

    return _format


# Syntax styles that can be shared by all languages
STYLES = {}
SDEFAULTS = (
    ("keyword", "keyword", "bold"),
    ("operator", "operator", None),
    ("brace", "brace", None),
    ("definition", "definition", "bold"),
    ("string", "string", None),
    ("string2", "string2", None),
    ("comment", "comment", "italic"),
    ("properObject", "properObject", None),
    ("numbers", "numbers", None),
    ("spaces", "spaces", None),
    ("extras", "extras", "bold"),
    ("selectedWord", "selected-word", None),
)


def restyle(scheme):
    """Reset the style for each highlighting item when the scheme change."""
    rescs = resources.COLOR_SCHEME
    global STYLES

    for stkw, srkw, default in SDEFAULTS:
        if default:
            STYLES[stkw] = format(scheme.get(srkw, rescs[srkw]), default)
        else:
            STYLES[stkw] = format(scheme.get(srkw, rescs[srkw]))


class Highlighter(QSyntaxHighlighter):
    """Syntax Highlighter for NINJA-IDE."""

    # braces
    braces = ['\\(', '\\)', '\\{', '\\}', '\\[', '\\]']

    def __init__(self, document, lang=None, scheme=None,
      errors=None, pep8=None, migration=None):
        QSyntaxHighlighter.__init__(self, document)
        self.highlight_function = self.realtime_highlight
        self.errors = errors
        self.pep8 = pep8
        self.migration = migration
        self._old_search = None
        self.selected_word_lines = []
        self.visible_limits = (0, 50)
        self._styles = {}
        if lang is not None:
            self.apply_highlight(lang, scheme)

    def sanitize(self, word):
        """Sanitize the string to avoid problems with the regex."""
        return word.replace('\\', '\\\\')

    def apply_highlight(self, lang, scheme=None, syntax=None):
        """Set the rules that will decide what to highlight and how."""
        if syntax is None:
            langSyntax = settings.SYNTAX.get(lang, {})
        else:
            langSyntax = syntax
        if scheme is not None:
            restyle(scheme)

        keywords = langSyntax.get('keywords', [])
        operators = langSyntax.get('operators', [])
        extras = langSyntax.get('extras', [])

        rules = []

        # Keyword, operator, brace and extras rules
        keyword_pattern = '(^|[^\w\.]{1})(%s)([^\w]{1}|$)'
        rules += [(keyword_pattern % w, 2, STYLES['keyword'])
            for w in keywords]
        rules += [(r'%s' % o, 0, STYLES['operator'])
            for o in operators]
        rules += [(r'%s' % b, 0, STYLES['brace'])
            for b in Highlighter.braces]
        rules += [(keyword_pattern % e, 2, STYLES['extras'])
            for e in extras]

        # All other rules
        proper = langSyntax.get('properObject', None)
        if proper is not None:
            proper = r'\b%s\b' % str(proper[0])
            rules += [(proper, 0, STYLES['properObject'])]

        rules.append((r'__\w+__', 0, STYLES['properObject']))

        # Classes and functions
        definition = langSyntax.get('definition', [])
        for de in definition:
            expr = r'\b%s\b\s*(\w+)' % de
            rules.append((expr, 1, STYLES['definition']))

        # Numeric literals
        rules += [
            (r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0,
            STYLES['numbers']),
        ]

        # Regular expressions
        regex = langSyntax.get('regex', [])
        for reg in regex:
            expr = reg[0]
            color = resources.COLOR_SCHEME['extras']
            style = ''
            if len(reg) > 1:
                if reg[1] in resources.CUSTOM_SCHEME:
                    color = resources.CUSTOM_SCHEME[reg[1]]
                elif reg[1] in resources.COLOR_SCHEME:
                    color = resources.COLOR_SCHEME[reg[1]]
            if len(reg) > 2:
                style = reg[2]
            rules.append((expr, 0, format(color, style)))

        # Strings
        stringChar = langSyntax.get('string', [])
        for sc in stringChar:
            expr = r'"[^"\\]*(\\.[^"\\]*)*"' if sc == '"' \
                else r"'[^'\\]*(\\.[^'\\]*)*'"
            rules.append((expr, 0, STYLES['string']))

        # Comments
        comments = langSyntax.get('comment', [])
        for co in comments:
            expr = co + '[^\\n]*'
            rules.append((expr, 0, STYLES['comment']))

        # Multi-line strings (expression, flag, style)
        # FIXME: The triple-quotes in these two lines will mess up the
        # syntax highlighting from this point onward
        self.tri_single = (QRegExp("'''"), 1, STYLES["string2"])
        self.tri_double = (QRegExp('"""'), 2, STYLES['string2'])

        multi = langSyntax.get('multiline_comment', [])
        if multi:
            self.multi_start = (QRegExp(
                re.escape(multi['open'])), STYLES['comment'])
            self.multi_end = (QRegExp(
                re.escape(multi['close'])), STYLES['comment'])
        else:
            self.multi_start = None

        # Build a QRegExp for each pattern
        self.rules = [(QRegExp(pat), index, fmt)
            for (pat, index, fmt) in rules]
        self.selected_word_pattern = None
        #Apply Highlight to the document... (when colors change)
        self.rehighlight()

    def set_selected_word(self, word, partial=True):
        """Set the word to highlight."""
        # partial = True for new highlighter compatibility
        hl_worthy = len(word) > 2
        if hl_worthy:
            self.selected_word_pattern = QRegExp(
                r'\b%s\b' % self.sanitize(word))
        else:
            self.selected_word_pattern = None

        suffix = "(?![A-Za-z_\d])"
        prefix = "(?<![A-Za-z_\d])"
        word = re.escape(word)
        if not partial:
            word = "%s%s%s" % (prefix, word, suffix)
        lines = []
        pat_find = re.compile(word)
        document = self.document()
        for lineno, text in enumerate(document.toPlainText().splitlines()):
            if hl_worthy and pat_find.search(text):
                lines.append(lineno)
            elif self._old_search and self._old_search.search(text):
                lines.append(lineno)
        # Ask perrito if i don't know what the next line does:
        self._old_search = hl_worthy and pat_find
        self.rehighlight_lines(lines)

    def __highlight_pep8(self, char_format, user_data):
        """Highlight the lines with pep8 errors."""
        user_data.error = True
        char_format = char_format.toCharFormat()
        char_format.setUnderlineColor(QColor(
            resources.CUSTOM_SCHEME.get('pep8-underline',
                resources.COLOR_SCHEME['pep8-underline'])))
        char_format.setUnderlineStyle(
            QTextCharFormat.WaveUnderline)
        return char_format

    def __highlight_lint(self, char_format, user_data):
        """Highlight the lines with lint errors."""
        user_data.error = True
        char_format = char_format.toCharFormat()
        char_format.setUnderlineColor(QColor(
            resources.CUSTOM_SCHEME.get('error-underline',
                resources.COLOR_SCHEME['error-underline'])))
        char_format.setUnderlineStyle(
            QTextCharFormat.WaveUnderline)
        return char_format

    def __highlight_migration(self, char_format, user_data):
        """Highlight the lines with lint errors."""
        user_data.error = True
        char_format = char_format.toCharFormat()
        char_format.setUnderlineColor(QColor(
            resources.CUSTOM_SCHEME.get('migration-underline',
                resources.COLOR_SCHEME['migration-underline'])))
        char_format.setUnderlineStyle(
            QTextCharFormat.WaveUnderline)
        return char_format

    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text."""
        self.highlight_function(text)

    def set_open_visible_area(self, is_line, position):
        """Set the range of lines that should be highlighted on open."""
        if is_line:
            self.visible_limits = (position - 50, position + 50)

    def open_highlight(self, text):
        """Only highlight the lines inside the accepted range."""
        if self.visible_limits[0] <= self.currentBlock().blockNumber() <= \
           self.visible_limits[1]:
            self.realtime_highlight(text)
        else:
            self.setCurrentBlockState(0)

    def async_highlight(self):
        """Execute a thread to collect the info of the things to highlight.

        The thread will collect the data from where to where to highlight,
        and which kind of highlight to use for those sections, and return
        that info to the main thread after it process all the file."""
        self.thread_highlight = HighlightParserThread(self)
        self.connect(self.thread_highlight,
            SIGNAL("highlightingDetected(PyQt_PyObject)"),
            self._execute_threaded_highlight)
        self.thread_highlight.start()

    def _execute_threaded_highlight(self, styles=None):
        """Function called with the info collected when the thread ends."""
        self.highlight_function = self.threaded_highlight
        if styles:
            self._styles = styles
            lines = list(set(styles.keys()) -
                set(range(self.visible_limits[0], self.visible_limits[1])))
            # Highlight the rest of the lines that weren't highlighted on open
            self.rehighlight_lines(lines, False)
        else:
            self._styles = {}
        self.highlight_function = self.realtime_highlight
        self.thread_highlight.wait()

    def threaded_highlight(self, text):
        """Highlight each line using the info collected by the thread.

        This function doesn't need to execute the regular expressions to see
        where the highlighting starts and end for each rule, it just take
        the start and end point, and the proper highlighting style from the
        info returned from the thread and applied that to the document."""
        hls = []
        block = self.currentBlock()
        user_data = syntax_highlighter.get_user_data(block)
        user_data.clear_data()
        block_number = block.blockNumber()
        highlight_errors = lambda cf, ud: cf
        if self.errors and (block_number in self.errors.errorsSummary):
            highlight_errors = self.__highlight_lint
        elif self.pep8 and (block_number in self.pep8.pep8checks):
            highlight_errors = self.__highlight_pep8
        elif self.migration and (
             block_number in self.migration.migration_data):
            highlight_errors = self.__highlight_migration

        char_format = block.charFormat()
        char_format = highlight_errors(char_format, user_data)
        self.setFormat(0, len(block.text()), char_format)

        block_styles = self._styles.get(block.blockNumber(), ())
        for index, length, char_format in block_styles:
            char_format = highlight_errors(char_format, user_data)
            if (self.format(index) != STYLES['string']):
                self.setFormat(index, length, char_format)
                if char_format == STYLES['string']:
                    hls.append((index, index + length))
                    user_data.add_str_group(index, index + length)
                elif char_format == STYLES['comment']:
                    user_data.comment_start_at(index)

        self.setCurrentBlockState(0)
        if not self.multi_start:
            # Do multi-line strings
            in_multiline = self.match_multiline(text, *self.tri_single,
                hls=hls, highlight_errors=highlight_errors,
                user_data=user_data)
            if not in_multiline:
                in_multiline = self.match_multiline(text, *self.tri_double,
                    hls=hls, highlight_errors=highlight_errors,
                    user_data=user_data)
        else:
            # Do multi-line comment
            self.comment_multiline(text, self.multi_end[0], *self.multi_start)

        block.setUserData(user_data)

    def realtime_highlight(self, text):
        """Highlight each line while it is being edited.

        This function apply the proper highlight to the line being edited
        by the user, this is a really fast process for each line once you
        already have the document highlighted, but slow to do it the first
        time to highlight all the lines together."""
        hls = []
        block = self.currentBlock()
        user_data = syntax_highlighter.get_user_data(block)
        user_data.clear_data()
        block_number = block.blockNumber()
        highlight_errors = lambda cf, ud: cf
        if self.errors and (block_number in self.errors.errorsSummary):
            highlight_errors = self.__highlight_lint
        elif self.pep8 and (block_number in self.pep8.pep8checks):
            highlight_errors = self.__highlight_pep8
        elif self.migration and (
             block_number in self.migration.migration_data):
            highlight_errors = self.__highlight_migration

        char_format = block.charFormat()
        char_format = highlight_errors(char_format, user_data)
        self.setFormat(0, len(block.text()), char_format)

        for expression, nth, char_format in self.rules:
            index = expression.indexIn(text, 0)

            while index >= 0:
                # We actually want the index of the nth match
                index = expression.pos(nth)
                length = len(expression.cap(nth))
                char_format = highlight_errors(char_format, user_data)

                if (self.format(index) != STYLES['string']):
                    self.setFormat(index, length, char_format)
                    if char_format == STYLES['string']:
                        hls.append((index, index + length))
                        user_data.add_str_group(index, index + length)
                    elif char_format == STYLES['comment']:
                        user_data.comment_start_at(index)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)
        if not self.multi_start:
            # Do multi-line strings
            in_multiline = self.match_multiline(text, *self.tri_single,
                hls=hls, highlight_errors=highlight_errors,
                user_data=user_data)
            if not in_multiline:
                in_multiline = self.match_multiline(text, *self.tri_double,
                    hls=hls, highlight_errors=highlight_errors,
                    user_data=user_data)
        else:
            # Do multi-line comment
            self.comment_multiline(text, self.multi_end[0], *self.multi_start)

        #Highlight selected word
        if self.selected_word_pattern is not None:
            index = self.selected_word_pattern.indexIn(text, 0)

            while index >= 0:
                index = self.selected_word_pattern.pos(0)
                length = len(self.selected_word_pattern.cap(0))
                char_format = self.format(index)
                color = STYLES['selectedWord'].foreground().color()
                color.setAlpha(100)
                char_format.setBackground(color)
                self.setFormat(index, length, char_format)
                index = self.selected_word_pattern.indexIn(
                    text, index + length)

        #Spaces
        expression = QRegExp('\s+')
        index = expression.indexIn(text, 0)
        while index >= 0:
            index = expression.pos(0)
            length = len(expression.cap(0))
            char_format = STYLES['spaces']
            char_format = highlight_errors(char_format, user_data)
            self.setFormat(index, length, char_format)
            index = expression.indexIn(text, index + length)

        block.setUserData(user_data)

    def _rehighlight_lines(self, lines):
        """If the document is valid, highlight the list of lines received."""
        if self.document() is None:
            return
        for line in lines:
            block = self.document().findBlockByNumber(line)
            self.rehighlightBlock(block)

    def _get_errors_lines(self):
        """Return the number of lines that contains errors to highlight."""
        errors_lines = []
        block = self.document().begin()
        while block.isValid():
            user_data = syntax_highlighter.get_user_data(block)
            if user_data.error:
                errors_lines.append(block.blockNumber())
            block = block.next()
        return errors_lines

    def rehighlight_lines(self, lines, errors=True):
        """Rehighlight the lines for errors or selected words."""
        if errors:
            errors_lines = self._get_errors_lines()
            refresh_lines = set(lines + errors_lines)
        else:
            refresh_lines = set(lines + self.selected_word_lines)
            self.selected_word_lines = lines
        self._rehighlight_lines(refresh_lines)

    def match_multiline(self, text, delimiter, in_state, style,
        hls=[], highlight_errors=lambda x: x, user_data=None):
        """Do highlighting of multi-line strings. ``delimiter`` should be a
        ``QRegExp`` for triple-single-quotes or triple-double-quotes, and
        ``in_state`` should be a unique integer to represent the corresponding
        state changes when inside those strings. Returns True if we're still
        inside a multi-line string when this function is finished.
        """
        # If inside triple-single quotes, start at 0
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        # Otherwise, look for the delimiter on this line
        else:
            start = delimiter.indexIn(text)
            # Move past this match
            add = delimiter.matchedLength()

        # As long as there's a delimiter match on this line...
        while start >= 0:
            # Look for the ending delimiter
            end = delimiter.indexIn(text, start + add)
            # Ending delimiter on this line?
            if end >= add:
                length = end - start + add + delimiter.matchedLength()
                self.setCurrentBlockState(0)
            # No; multi-line string
            else:
                self.setCurrentBlockState(in_state)
                length = len(text) - start + add

            st_fmt = self.format(start)
            start_collides = [pos for pos in hls if pos[0] < start < pos[1]]

            # Apply formatting
            if ((st_fmt != STYLES['comment']) or
               ((st_fmt == STYLES['comment']) and
               (self.previousBlockState() != 0))) and \
                (len(start_collides) == 0):
                style = highlight_errors(style, user_data)
                self.setFormat(start, length, style)
            else:
                self.setCurrentBlockState(0)
            # Look for the next match
            start = delimiter.indexIn(text, start + length)

        # Return True if still inside a multi-line string, False otherwise
        if self.currentBlockState() == in_state:
            return True
        else:
            return False

    def comment_multiline(self, text, delimiter_end, delimiter_start, style):
        """Process the beggining and end of a multiline comment."""
        startIndex = 0
        if self.previousBlockState() != 1:
            startIndex = delimiter_start.indexIn(text)
        while startIndex >= 0:
            endIndex = delimiter_end.indexIn(text, startIndex)
            commentLength = 0
            if endIndex == -1:
                self.setCurrentBlockState(1)
                commentLength = len(text) - startIndex
            else:
                commentLength = endIndex - startIndex + \
                    delimiter_end.matchedLength()

            self.setFormat(startIndex, commentLength, style)
            startIndex = delimiter_start.indexIn(text,
                startIndex + commentLength)


class HighlightParserThread(QThread):
    """Thread that collect the highlighting info to the current file."""

    def __init__(self, highlighter):
        super(HighlightParserThread, self).__init__()
        self._highlighter = highlighter

    def run(self):
        """Execute this rules in another thread to avoid blocking the ui."""
        styles = {}
        self.msleep(300)
        block = self._highlighter.document().begin()
        while block.blockNumber() != -1:
            text = block.text()
            formats = []

            for expression, nth, char_format in self._highlighter.rules:
                index = expression.indexIn(text, 0)

                while index >= 0:
                    # We actually want the index of the nth match
                    index = expression.pos(nth)
                    length = len(expression.cap(nth))

                    formats.append((index, length, char_format))
                    index = expression.indexIn(text, index + length)

            #Spaces
            expression = QRegExp('\s+')
            index = expression.indexIn(text, 0)
            while index >= 0:
                index = expression.pos(0)
                length = len(expression.cap(0))
                formats.append((index, length, STYLES['spaces']))
                index = expression.indexIn(text, index + length)

            styles[block.blockNumber()] = formats
            block = block.next()
        self.emit(SIGNAL("highlightingDetected(PyQt_PyObject)"), styles)


class EmpyHighlighter(QSyntaxHighlighter):
    """Dummy highlighter to be used when the current file is not recognized."""

    def __init__(self, document):
        super(EmpyHighlighter, self).__init__(document)
        self.highlight_function = lambda x: None

    def apply_highlight(self, *args, **kwargs):
        pass

    def set_selected_word(self, *args, **kwargs):
        pass

    def realtime_highlight(self, *args, **kwargs):
        pass

    def set_open_visible_area(self, *args, **kwargs):
        pass

    def open_highlight(self, *args, **kwargs):
        pass

    def async_highlight(self, *args, **kwargs):
        pass

    def highlightBlock(self, text):
        pass

    def rehighlight_lines(self, lines, errors=True):
        pass
