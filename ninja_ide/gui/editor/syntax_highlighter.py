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

# Based on: https://bitbucket.org/henning/syntaxhighlighter
"""
Partition-based syntax highlighter
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import re

from PyQt4.QtGui import (
    QSyntaxHighlighter,
    QColor, QTextCharFormat, QTextBlockUserData, QFont, QBrush, QTextFormat)

from ninja_ide import resources
from ninja_ide.core import settings


try:
    unicode
except NameError:
    # Python 3
    basestring = unicode = str  # lint:ok


def get_user_data(block):
    user_data = block.userData()
    if user_data is None or not isinstance(user_data, SyntaxUserData):
        user_data = SyntaxUserData()

    return user_data


class SyntaxUserData(QTextBlockUserData):
    """Store the information of the errors, str and comments for each block."""

    def __init__(self, error=False):
        super(SyntaxUserData, self).__init__()
        self.error = error
        self.str_groups = []
        self.comment_start = -1

    def clear_data(self):
        """Clear the data stored for the current block."""
        self.error = False
        self.str_groups = []
        self.comment_start = -1

    def add_str_group(self, start, end):
        """Add a pair of values setting the beggining and end of a string."""
        self.str_groups.append((start, end + 1))

    def comment_start_at(self, pos):
        """Set the position in the line where the comment starts."""
        self.comment_start = pos


class TextCharFormat(QTextCharFormat):
    NAME = QTextFormat.UserProperty + 1


class Format(object):

    __slots__ = ("name", "tcf")

    def __init__(self, name, color=None, bold=None, italic=None,
        base_format=None, background=None):
        self.name = name
        tcf = TextCharFormat()
        if base_format is not None:
            if isinstance(base_format, Format):
                base_format = base_format.tcf
            tcf.merge(base_format)
            tcf.setFont(base_format.font())
        if color is not None:
            if not isinstance(color, QColor):
                color = QColor(color)
            tcf.setForeground(QBrush(color))
        if bold is not None:
            if bold:
                tcf.setFontWeight(QFont.Bold)
            else:
                tcf.setFontWeight(QFont.Normal)
        if italic is not None:
            tcf.setFontItalic(italic)
        if background is not None:
            color = QColor(background)
            tcf.setBackground(color)
        tcf.setProperty(TextCharFormat.NAME, name)
        self.tcf = tcf


class HighlighterError(Exception):
    pass


class Partition(object):
    # every partition maps to a specific state in QSyntaxHighlighter

    __slots__ = ("name", "start", "end", "is_multiline", "search_end")

    def __init__(self, name, start, end, is_multiline=False):
        self.name = name
        self.start = start
        self.end = end
        self.is_multiline = is_multiline
        try:
            self.search_end = re.compile(end, re.M | re.S).search
        except Exception as exc:
            raise HighlighterError("%s: %s %s" % (exc, name, end))


class PartitionScanner(object):
    # The idea to partition the source into different contexts comes
    # from Eclipse.
    # http://wiki.eclipse.org/FAQ_What_is_a_document_partition%3F

    def __init__(self, partitions):
        start_groups = []
        self.partitions = []
        for i, p in enumerate(partitions):
            if isinstance(p, (tuple, list)):
                p = Partition(*p)
            elif isinstance(p, dict):
                p = Partition(**p)
            else:
                assert isinstance(p, Partition), \
                    "Partition expected, got %r" % p
            self.partitions.append(p)
            start_groups.append("(?P<g%s_%s>%s)" % (i, p.name, p.start))
        start_pat = "|".join(start_groups)
        try:
            self.search_start = re.compile(start_pat, re.M | re.S).search
        except Exception as exc:
            raise HighlighterError("%s: %s" % (exc, start_pat))

    def scan(self, current_state, text):
        last_pos = 0
        length = len(text)
        parts = self.partitions
        search_start = self.search_start
        # loop yields (start, end, partition, new_state, is_inside)
        while last_pos < length:
            if current_state == -1:
                found = search_start(text, last_pos)
                if found:
                    start, end = found.span()
                    yield last_pos, start, None, -1, True
                    current_state = found.lastindex - 1
                    p = parts[current_state]
                    yield start, end, p.name, current_state, False
                    last_pos = end
                else:
                    current_state = -1
                    yield last_pos, length, None, -1, True
                    break
            else:
                p = parts[current_state]
                found = p.search_end(text, last_pos)
                if found:
                    start, end = found.span()
                    yield last_pos, start, p.name, current_state, True
                    yield start, end, p.name, current_state, False
                    last_pos = end
                    current_state = -1
                else:
                    yield last_pos, length, p.name, current_state, True
                    break
        if current_state != -1:
            p = parts[current_state]
            if not p.is_multiline:
                current_state = -1
        yield length, length, None, current_state, False


class Token(object):
    __slots__ = ("name", "pattern", "prefix", "suffix")

    def __init__(self, name, pattern, prefix="", suffix=""):
        self.name = name
        if isinstance(pattern, list):
            pattern = "|".join(pattern)
        self.pattern = pattern
        self.prefix = prefix
        self.suffix = suffix


class Scanner(object):
    __slots__ = ("groups", "tokens", "search")

    def __init__(self, tokens):
        self.tokens = []
        self.groups = []
        for t in tokens:
            if isinstance(t, (list, tuple)):
                t = Token(*t)
            elif isinstance(t, dict):
                t = Token(**t)
            else:
                assert isinstance(t, Token), "Token expected, got %r" % t
            gdef = "?P<%s>" % t.name
            if gdef in t.pattern:
                p = t.pattern
            else:
                p = ("(%s%s)" % (gdef, t.pattern))
            p = t.prefix + p + t.suffix
            self.groups.append(p)
            self.tokens.append(t)
        pat = "|".join(self.groups)
        self.search = re.compile(pat).search

    def add_token(self, token):
        self.__clean_highlight()
        tpattern = token[1]
        if tpattern != "":
            t = Token(*token)
            gdef = "?P<%s>" % t.name
            if gdef in t.pattern:
                p = t.pattern
            else:
                p = ("(%s%s)" % (gdef, t.pattern))
            p = t.prefix + p + t.suffix
            self.groups.append(p)
            self.tokens.append(t)
        pat = "|".join(self.groups)
        self.search = re.compile(pat).search

    def __clean_highlight(self):
        for group in self.groups:
            if group.startswith('(?P<highlight_word>'):
                self.groups.remove(group)
                break
        for token in self.tokens:
            if token.name == "highlight_word":
                self.tokens.remove(token)
                break

    def scan(self, s):
        search = self.search
        #length = len(s)
        last_pos = 0
        # loop yields (token, start_pos, end_pos)
        while 1:
            found = search(s, last_pos)
            if found:
                lg = found.lastgroup
                start, last_pos = found.span(lg)
                yield lg, start, last_pos
            else:
                break


class SyntaxHighlighter(QSyntaxHighlighter):

    def __init__(self, parent, partition_scanner, scanner, formats,
        errors=None, pep8=None, migration=None):
        """
        :param parent: QDocument or QTextEdit/QPlainTextEdit instance
        'partition_scanner:
            PartitionScanner instance
        :param scanner:
            dictionary of token scanners for each partition
            The key is the name of the partition, the value is a Scanner
                instance
            The default scanner has the key None
        :formats:
            list of tuples consisting of a name and a format definition
            The name is the name of a partition or token
        """
        super(SyntaxHighlighter, self).__init__(parent)
        self.errors = errors
        self.pep8 = pep8
        self.migration = migration

        if isinstance(partition_scanner, (list, tuple)):
            partition_scanner = PartitionScanner(partition_scanner)
        else:
            assert isinstance(partition_scanner, PartitionScanner), \
                "PartitionScanner expected, got %r" % partition_scanner
        self.partition_scanner = partition_scanner

        self.scanner = scanner
        for inside_part, inside_scanner in list(scanner.items()):
            if isinstance(inside_scanner, (list, tuple)):
                inside_scanner = Scanner(inside_scanner)
                self.scanner[inside_part] = inside_scanner
            else:
                assert isinstance(inside_scanner, Scanner), \
                    "Scanner expected"

        self.formats = {}
        for f in formats:
            if isinstance(f, tuple):
                fname, f = f
            else:
                assert isinstance(f, (Format, dict)), \
                    "Format expected, got %r" % f
            if isinstance(f, basestring):
                f = (f,)  # only color specified
            if isinstance(f, (tuple, list)):
                f = Format(*((fname,) + f))
            elif isinstance(f, dict):
                f = Format(**dict(name=fname, **f))
            else:
                assert isinstance(f, Format), "Format expected, got %r" % f
            f.tcf.setFontFamily(parent.defaultFont().family())
            self.formats[f.name] = f.tcf

        # reduce name look-ups for better speed
        scan_inside = {}
        for inside_part, inside_scanner in list(self.scanner.items()):
            scan_inside[inside_part] = inside_scanner.scan
        self.get_scanner = scan_inside.get
        self.scan_partitions = partition_scanner.scan
        self.get_format = self.formats.get

    def __apply_proper_style(self, char_format, color):
        if settings.UNDERLINE_NOT_BACKGROUND:
            char_format.setUnderlineColor(color)
            char_format.setUnderlineStyle(QTextCharFormat.WaveUnderline)
        else:
            color.setAlpha(60)
            char_format.setBackground(color)

    def __highlight_pep8(self, char_format, user_data=None):
        """Highlight the lines with pep8 errors."""
        user_data.error = True
        color = QColor(
            resources.CUSTOM_SCHEME.get('pep8-underline',
            resources.COLOR_SCHEME['pep8-underline']))
        self.__apply_proper_style(char_format, color)
        return char_format

    def __highlight_lint(self, char_format, user_data):
        """Highlight the lines with lint errors."""
        user_data.error = True
        color = QColor(
            resources.CUSTOM_SCHEME.get('error-underline',
            resources.COLOR_SCHEME['error-underline']))
        self.__apply_proper_style(char_format, color)
        return char_format

    def __highlight_migration(self, char_format, user_data):
        """Highlight the lines with lint errors."""
        user_data.error = True
        color = QColor(
            resources.CUSTOM_SCHEME.get('migration-underline',
            resources.COLOR_SCHEME['migration-underline']))
        self.__apply_proper_style(char_format, color)
        return char_format

    def __remove_error_highlight(self, char_format, user_data):
        user_data.error = False
        char_format.setUnderlineStyle(QTextCharFormat.NoUnderline)
        char_format.clearBackground()
        return char_format

    def highlightBlock(self, text):
        """automatically called by Qt"""
        text += "\n"
        previous_state = self.previousBlockState()
        new_state = previous_state
        # User data and errors
        block = self.currentBlock()
        user_data = get_user_data(block)
        user_data.clear_data()
        valid_error_line, highlight_errors = self.get_error_highlighter(block)
        # speed-up name-lookups
        get_format = self.get_format
        set_format = self.setFormat
        get_scanner = self.get_scanner

        for start, end, partition, new_state, is_inside in \
          self.scan_partitions(previous_state, text):
            f = get_format(partition, None)
            if f:
                f = highlight_errors(f, user_data)
                set_format(start, end - start, f)
            elif valid_error_line:
                f = TextCharFormat()
                f = highlight_errors(f, user_data)
                set_format(start, end - start, f)
            if is_inside:
                scan = get_scanner(partition)
                if scan:
                    for token, token_pos, token_end in scan(text[start:end]):
                        f = get_format(token)
                        if f:
                            f = highlight_errors(f, user_data)
                            set_format(start + token_pos,
                                token_end - token_pos, f)
            if partition and partition == "string":
                user_data.add_str_group(start, end)

        block.setUserData(user_data)
        self.setCurrentBlockState(new_state)

    def get_error_highlighter(self, block):
        block_number = block.blockNumber()
        highlight_errors = self.__remove_error_highlight
        valid_error_line = False
        if self.errors and (block_number in self.errors.errorsSummary):
            highlight_errors = self.__highlight_lint
            valid_error_line = True
        elif self.pep8 and (block_number in self.pep8.pep8checks):
            highlight_errors = self.__highlight_pep8
            valid_error_line = True
        elif self.migration and (
             block_number in self.migration.migration_data):
            highlight_errors = self.__highlight_migration
            valid_error_line = True
        return valid_error_line, highlight_errors

    def set_selected_word(self, word, partial=False):
        """Set the word to highlight."""
        if len(word) > 2:
            suffix = "(?![A-Za-z_\d])"
            prefix = "(?<![A-Za-z_\d])"
            word = re.escape(word)
            if not partial:
                word = "%s%s%s" % (prefix, word, suffix)
            self.scanner[None].add_token(('highlight_word', word))
        else:
            self.scanner[None].add_token(('highlight_word', ""))
        self.rehighlight()

    def _rehighlight_lines(self, lines):
        """If the document is valid, highlight the list of lines received."""
        if self.document() is None:
            return
        for line in lines:
            block = self.document().findBlockByNumber(line)
            self.document().markContentsDirty(block.position(),
                block.position() + block.length())
            self.rehighlightBlock(block)

    def _get_errors_lines(self):
        """Return the number of lines that contains errors to highlight."""
        errors_lines = []
        block = self.document().begin()
        while block.isValid():
            user_data = get_user_data(block)
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
            refresh_lines = set(lines)
        self._rehighlight_lines(refresh_lines)


def _create_scheme():
    scheme = {
      "syntax_comment": dict(color=resources.CUSTOM_SCHEME.get(
          "comment", resources.COLOR_SCHEME["comment"]), italic=True),
      "syntax_string": resources.CUSTOM_SCHEME.get(
          "string", resources.COLOR_SCHEME["string"]),
      "syntax_builtin": resources.CUSTOM_SCHEME.get(
          "extras", resources.COLOR_SCHEME["extras"]),
      "syntax_keyword": (resources.CUSTOM_SCHEME.get(
          "keyword", resources.COLOR_SCHEME["keyword"]), True),
      "syntax_definition": (resources.CUSTOM_SCHEME.get(
          "definition", resources.COLOR_SCHEME["definition"]), True),
      "syntax_braces": resources.CUSTOM_SCHEME.get(
          "brace", resources.COLOR_SCHEME["brace"]),
      "syntax_number": resources.CUSTOM_SCHEME.get(
          "numbers", resources.COLOR_SCHEME["numbers"]),
      "syntax_proper_object": resources.CUSTOM_SCHEME.get(
          "properObject", resources.COLOR_SCHEME["properObject"]),
      "syntax_operators": resources.CUSTOM_SCHEME.get(
          "operator", resources.COLOR_SCHEME["operator"]),
      "syntax_highlight_word": dict(color=resources.CUSTOM_SCHEME.get(
          "selected-word", resources.COLOR_SCHEME["selected-word"]),
          background=resources.CUSTOM_SCHEME.get(
          "selected-word-background",
          resources.COLOR_SCHEME["selected-word-background"])),
      "syntax_pending": resources.COLOR_SCHEME["pending"],
    }

    return scheme


def load_syntax(syntax):
    context = _create_scheme() or {}

    partition_scanner = PartitionScanner(syntax.get("partitions", []))

    scanners = {}
    for part_name, part_scanner in list(syntax.get("scanner", {}).items()):
        scanners[part_name] = Scanner(part_scanner)

    formats = []
    for fname, fstyle in list(syntax.get("formats", {}).items()):
        if isinstance(fstyle, basestring):
            if fstyle.startswith("%(") and fstyle.endswith(")s"):
                key = fstyle[2:-2]
                fstyle = context[key]
            else:
                fstyle = fstyle % context
        formats.append((fname, fstyle))

    return partition_scanner, scanners, formats
