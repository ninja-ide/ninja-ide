#-*-coding:utf-8-*-
# based on Python Syntax highlighting from:
# http://diotavelli.net/PyQtWiki/Python%20syntax%20highlighting
from __future__ import absolute_import

from PyQt4.QtGui import QColor
from PyQt4.QtGui import QTextCharFormat
from PyQt4.QtGui import QFont
from PyQt4.QtGui import QSyntaxHighlighter
from PyQt4.QtCore import QRegExp

from ninja_ide import resources
from ninja_ide.core import settings


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


def restyle(scheme):
    STYLES['keyword'] = format(scheme.get('keyword',
        resources.COLOR_SCHEME['keyword']), 'bold')
    STYLES['operator'] = format(scheme.get('operator',
        resources.COLOR_SCHEME['operator']))
    STYLES['brace'] = format(scheme.get('brace',
        resources.COLOR_SCHEME['brace']))
    STYLES['definition'] = format(scheme.get('definition',
        resources.COLOR_SCHEME['definition']), 'bold')
    STYLES['string'] = format(scheme.get('string',
        resources.COLOR_SCHEME['string']))
    STYLES['string2'] = format(scheme.get('string2',
        resources.COLOR_SCHEME['string2']))
    STYLES['comment'] = format(scheme.get('comment',
        resources.COLOR_SCHEME['comment']), 'italic')
    STYLES['properObject'] = format(scheme.get('properObject',
        resources.COLOR_SCHEME['properObject']), 'italic')
    STYLES['numbers'] = format(scheme.get('numbers',
        resources.COLOR_SCHEME['numbers']))
    STYLES['spaces'] = format(scheme.get('spaces',
        resources.COLOR_SCHEME['spaces']))
    STYLES['extras'] = format(scheme.get('extras',
        resources.COLOR_SCHEME['extras']), 'bold')
    STYLES['selectedWord'] = scheme.get('selected-word',
        resources.COLOR_SCHEME['selected-word'])


class Highlighter (QSyntaxHighlighter):

    # braces
    braces = ['\\(', '\\)', '\\{', '\\}', '\\[', '\\]']

    def __init__(self, document, lang=None, scheme=None,
      errors=None, pep8=None):
        QSyntaxHighlighter.__init__(self, document)
        self.errors = errors
        self.pep8 = pep8
        if lang is not None:
            self.apply_highlight(lang, scheme)

    def sanitize(self, word):
        return word.replace('\\', '\\\\')

    def apply_highlight(self, lang, scheme=None, syntax=None):
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
        rules += [(r'\b%s\b' % w, 0, STYLES['keyword'])
            for w in keywords]
        rules += [(r'%s' % o, 0, STYLES['operator'])
            for o in operators]
        rules += [(r'%s' % b, 0, STYLES['brace'])
            for b in Highlighter.braces]
        rules += [(r'^((.* )|(.*=)){0,1}(%s)((\(.*)|( .*)){0,1}$' % e,
             4, STYLES['extras'])
            for e in extras]

        # All other rules
        proper = langSyntax.get('properObject', None)
        if proper is not None:
            proper = r'\b%s\b' % str(proper[0])
            rules += [(proper, 0, STYLES['properObject'])]

        rules.append((r'__\w+__', 0, STYLES['properObject']))

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

        stringChar = langSyntax.get('string', [])
        for sc in stringChar:
            expr = r'"[^"\\]*(\\.[^"\\]*)*"' if sc == '"' \
                else r"'[^'\\]*(\\.[^'\\]*)*'"
            rules.append((expr, 0, STYLES['string']))

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
            self.multi_start = (QRegExp(multi['open']), STYLES['comment'])
            self.multi_end = (QRegExp(multi['close']), STYLES['comment'])
        else:
            self.multi_start = None

        # Build a QRegExp for each pattern
        self.rules = [(QRegExp(pat), index, fmt)
            for (pat, index, fmt) in rules]
        self.selected_word_pattern = None
        #Apply Highlight to the document... (when colors change)
        self.rehighlight()

    def set_selected_word(self, word):
        """Set the word to highlight."""
        if len(word) > 2:
            self.selected_word_pattern = QRegExp(
                r'\b%s\b' % self.sanitize(word))
        else:
            self.selected_word_pattern = None

    def __highlight_pep8(self, format):
        """Highlight the lines with errors."""
        format = format.toCharFormat()
        format.setUnderlineColor(QColor(
            resources.CUSTOM_SCHEME.get('pep8-underline',
                resources.COLOR_SCHEME['pep8-underline'])))
        format.setUnderlineStyle(
            QTextCharFormat.WaveUnderline)
        return format

    def __highlight_lint(self, format):
        """Highlight the lines with errors."""
        format = format.toCharFormat()
        format.setUnderlineColor(QColor(
            resources.CUSTOM_SCHEME.get('error-underline',
                resources.COLOR_SCHEME['error-underline'])))
        format.setUnderlineStyle(
            QTextCharFormat.WaveUnderline)
        return format

    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text."""
        hls = []
        block = self.currentBlock()
        block_number = self.currentBlock().blockNumber()
        highlight_errors = lambda x: x
        if self.errors and (block_number in self.errors.errorsSummary):
            highlight_errors = self.__highlight_lint
        elif self.pep8 and (block_number in self.pep8.pep8checks):
            highlight_errors = self.__highlight_pep8

        format = block.charFormat()
        format = highlight_errors(format)
        self.setFormat(0, len(block.text()), format)

        for expression, nth, format in self.rules:
            index = expression.indexIn(text, 0)

            while index >= 0:
                # We actually want the index of the nth match
                index = expression.pos(nth)
                length = expression.cap(nth).length()
                format = highlight_errors(format)

                if (self.format(index) != STYLES['string']):
                    self.setFormat(index, length, format)
                    if format == STYLES['string']:
                        hls.append((index, index + length))
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)
        if not self.multi_start:
            # Do multi-line strings
            in_multiline = self.match_multiline(text, *self.tri_single,
                hls=hls, highlight_errors=highlight_errors)
            if not in_multiline:
                in_multiline = self.match_multiline(text, *self.tri_double,
                    hls=hls, highlight_errors=highlight_errors)
        else:
            # Do multi-line comment
            self.comment_multiline(text, self.multi_end[0], *self.multi_start)

        #Highlight selected word
        if self.selected_word_pattern is not None:
            index = self.selected_word_pattern.indexIn(text, 0)

            while index >= 0:
                index = self.selected_word_pattern.pos(0)
                length = self.selected_word_pattern.cap(0).length()
                format = self.format(index)
                color = QColor()
                color.setNamedColor(STYLES['selectedWord'])
                color.setAlpha(100)
                format.setBackground(color)
                self.setFormat(index, length, format)
                index = self.selected_word_pattern.indexIn(
                    text, index + length)

        #Spaces
        expression = QRegExp('\s+')
        index = expression.indexIn(text, 0)
        while index >= 0:
            index = expression.pos(0)
            length = expression.cap(0).length()
            format = STYLES['spaces']
            format = highlight_errors(format)
            self.setFormat(index, length, format)
            index = expression.indexIn(text, index + length)

    def match_multiline(self, text, delimiter, in_state, style,
        hls=[], highlight_errors=lambda x: x):
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
                length = text.length() - start + add

            st_fmt = self.format(start)
            start_collides = [pos for pos in hls if pos[0] < start < pos[1]]

            # Apply formatting
            if ((st_fmt != STYLES['comment']) or \
               ((st_fmt == STYLES['comment']) and
               (self.previousBlockState() != 0))) and \
                (len(start_collides) == 0):
                style = highlight_errors(style)
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
        startIndex = 0
        if self.previousBlockState() != 1:
            startIndex = delimiter_start.indexIn(text)
        while startIndex >= 0:
            endIndex = delimiter_end.indexIn(text, startIndex)
            commentLength = 0
            if endIndex == -1:
                self.setCurrentBlockState(1)
                commentLength = text.length() - startIndex
            else:
                commentLength = endIndex - startIndex + \
                    delimiter_end.matchedLength()

            self.setFormat(startIndex, commentLength, style)
            startIndex = delimiter_start.indexIn(text,
                startIndex + commentLength)


class EmptyHighlighter (QSyntaxHighlighter):

    def __init__(self, document):
        QSyntaxHighlighter.__init__(self, document)

    def highlightBlock(self, text):
        pass
