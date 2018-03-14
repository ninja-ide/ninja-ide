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

from PyQt5.QtGui import QSyntaxHighlighter
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QTextCharFormat
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QBrush
from PyQt5.QtGui import QTextFormat

from ninja_ide.core import settings
from ninja_ide import resources
from ninja_ide.gui.ide import IDE


class TextCharFormat(QTextCharFormat):
    NAME = QTextFormat.UserProperty + 1


class Format(object):

    __slots__ = ("name", "tcf")

    def __init__(self, name, color=None,
                 bold=None, italic=None, base_format=None):
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
            raise HighlighterError("{0}: {1} {2}".format(exc, name, end))


class PartitionScanner(object):
    # The idea to partition the source into different
    # contexts comes from Eclipse.
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
                assert isinstance(
                    p, Partition), "Partition expected, got %r" % p
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
    __slots__ = ("tokens", "search")

    def __init__(self, tokens):
        self.tokens = []
        groups = []
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
            groups.append(p)
            self.tokens.append(t)
        pat = "|".join(groups)
        self.search = re.compile(pat).search

    def scan(self, s):
        search = self.search
        last_pos = 0
        # loop yields (token, start_pos, end_pos)
        while True:
            found = search(s, last_pos)
            if found:
                lg = found.lastgroup
                start, last_pos = found.span(lg)
                yield lg, start, last_pos
            else:
                break


class SyntaxHighlighter(QSyntaxHighlighter):

    def __init__(self, parent, partition_scanner,
                 scanner, formats, default_font=None):
        """
        :param parent: QDocument or QTextEdit/QPlainTextEdit instance
        'partition_scanner:
            PartitionScanner instance
        :param scanner:
            dictionary of token scanners for each partition
            The key is the name of the partition,
            the value is a Scanner instance
            The default scanner has the key None
        :formats:
            list of tuples consisting of a name and a format definition
            The name is the name of a partition or token
        """
        super(SyntaxHighlighter, self).__init__(parent)
        if default_font:
            parent.setDefaultFont(default_font)

        if isinstance(partition_scanner, (list, tuple)):
            partition_scanner = PartitionScanner(partition_scanner)
        else:
            assert isinstance(
                partition_scanner,
                PartitionScanner), ("PartitionScanner expected, "
                                    "got {!r}".format(partition_scanner))
        self.partition_scanner = partition_scanner

        self.scanner = scanner
        for inside_part, inside_scanner in list(scanner.items()):
            if isinstance(inside_scanner, (list, tuple)):
                inside_scanner = Scanner(inside_scanner)
                self.scanner[inside_part] = inside_scanner
            else:
                assert isinstance(
                    inside_scanner, Scanner), ("Scanner expected, "
                                               "got {!r}".format(
                                                    inside_scanner))

        self.formats = {}
        for f in formats:
            if isinstance(f, tuple):
                fname, f = f
            else:
                assert isinstance(
                    f, (Format, dict)), "Format expected, got %r" % f
            if isinstance(f, str):
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

    def highlightBlock(self, text):
        """automatically called by Qt"""

        text = str(text) + "\n"
        previous_state = self.previousBlockState()
        new_state = previous_state
        # speed-up name-lookups
        get_format = self.get_format
        set_format = self.setFormat
        get_scanner = self.get_scanner

        for start, end, partition, new_state, is_inside in \
                self.scan_partitions(previous_state, text):
            f = get_format(partition, None)
            if f:
                set_format(start, end - start, f)
            if is_inside:
                scan = get_scanner(partition)
                if scan:
                    for token, token_pos, token_end in scan(text[start:end]):
                        f = get_format(token)
                        if f:
                            set_format(
                                start + token_pos, token_end - token_pos, f)

        self.setCurrentBlockState(new_state)


class Syntax(object):
    __slots__ = ("partition_scanner", "scanners", "context")

    def __init__(self, part_scanner, scanners):
        self.partition_scanner = part_scanner
        self.scanners = scanners
        self.context = []

    def build_context(self):
        for color in resources.COLOR_SCHEME.get("colors"):
            scope = color.get("scope")
            colors = color.get("settings")
            self.context.append((scope, colors))


def build_highlighter(language, force=False):
    syntax_registry = IDE.get_service("syntax_registry")
    syntax = syntax_registry.get_syntax_for(language)
    if syntax is None:
        syntax_structure = settings.SYNTAX.get(language)
        if syntax_structure is None:
            print("Error")
            return None
        part_scanner = PartitionScanner(syntax_structure.get("partitions"))
        scanners = {}
        for scanner in syntax_structure.get("scanner"):
            name = scanner.get("partition_name")
            scanners[name] = Scanner(scanner.get("tokens"))
        syntax = Syntax(part_scanner, scanners)
        syntax.build_context()
        syntax_registry.register_syntax(language, syntax)

    return syntax
