#!/usr/bin/env python
# pep8.py - Check Python source code formatting, according to PEP 8
# Copyright (C) 2006 Johann C. Rocholl <johann@rocholl.net>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

r"""
Check Python source code formatting, according to PEP 8:
http://www.python.org/dev/peps/pep-0008/

For usage and a list of options, try this:
$ python pep8.py -h

This program and its regression test suite live here:
http://github.com/jcrocholl/pep8

Groups of errors and warnings:
E errors
W warnings
100 indentation
200 whitespace
300 blank lines
400 imports
500 line length
600 deprecation
700 statements
900 syntax error

You can add checks to this program by writing plugins. Each plugin is
a simple function that is called for each line of source code, either
physical or logical.

Physical line:
- Raw line of text from the input file.

Logical line:
- Multi-line statements converted to a single line.
- Stripped left and right.
- Contents of strings replaced with 'xxx' of same length.
- Comments removed.

The check function requests physical or logical lines by the name of
the first argument:

def maximum_line_length(physical_line)
def extraneous_whitespace(logical_line)
def blank_lines(logical_line, blank_lines, indent_level, line_number)

The last example above demonstrates how check plugins can request
additional information with extra arguments. All attributes of the
Checker object are available. Some examples:

lines: a list of the raw lines from the input file
tokens: the tokens that contribute to this logical line
line_number: line number in the input file
blank_lines: blank lines before this one
indent_char: first indentation character in this file (' ' or '\t')
indent_level: indentation (with tabs expanded to multiples of 8)
previous_indent_level: indentation on previous line
previous_logical: previous logical line

The docstring of each check function shall be the relevant part of
text from PEP 8. It is printed if the user enables --show-pep8.
Several docstrings contain examples directly from the PEP 8 document.

Okay: spam(ham[1], {eggs: 2})
E201: spam( ham[1], {eggs: 2})

These examples are verified automatically when pep8.py is run with the
--doctest option. You can add examples for your own check functions.
The format is simple: "Okay" or error/warning code followed by colon
and space, the rest of the line is example source code. If you put 'r'
before the docstring, you can use \n for newline, \t for tab and \s
for space.

"""
from __future__ import unicode_literals

__version__ = '1.3.4a0'

import os
import sys
import re
import inspect
import keyword
import tokenize

from ninja_ide import resources

DEFAULT_EXCLUDE = '.svn,CVS,.bzr,.hg,.git'
DEFAULT_IGNORE = 'E24'
if sys.platform == 'win32':
    DEFAULT_CONFIG = os.path.join(resources.HOME_PATH, r'.pep8')
else:
    DEFAULT_CONFIG = os.path.join(os.getenv('XDG_CONFIG_HOME') or
                                  os.path.join(
                                      resources.HOME_PATH, '.config'), 'pep8')
MAX_LINE_LENGTH = 79
REPORT_FORMAT = {
    'default': '%(path)s:%(row)d:%(col)d: %(code)s %(text)s',
    'pylint': '%(path)s:%(row)d: [%(code)s] %(text)s',
}


SINGLETONS = frozenset(['False', 'None', 'True'])
KEYWORDS = frozenset(keyword.kwlist + ['print']) - SINGLETONS
BINARY_OPERATORS = frozenset([
    '**=', '*=', '+=', '-=', '!=', '<>',
    '%=', '^=', '&=', '|=', '==', '/=', '//=', '<=', '>=', '<<=', '>>=',
    '%', '^', '&', '|', '=', '/', '//', '<', '>', '<<'])
UNARY_OPERATORS = frozenset(['>>', '**', '*', '+', '-'])
OPERATORS = BINARY_OPERATORS | UNARY_OPERATORS
WHITESPACE = frozenset(' \t')
SKIP_TOKENS = frozenset([tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE,
                         tokenize.INDENT, tokenize.DEDENT])
BENCHMARK_KEYS = ['directories', 'files', 'logical lines', 'physical lines']

INDENT_REGEX = re.compile(r'([ \t]*)')
RAISE_COMMA_REGEX = re.compile(r'raise\s+\w+\s*(,)')
RERAISE_COMMA_REGEX = re.compile(r'raise\s+\w+\s*,\s*\w+\s*,\s*\w+')
SELFTEST_REGEX = re.compile(r'(Okay|[EW]\d{3}):\s(.*)')
ERRORCODE_REGEX = re.compile(r'[EW]\d{3}')
DOCSTRING_REGEX = re.compile(r'u?r?["\']')
EXTRANEOUS_WHITESPACE_REGEX = re.compile(r'[[({] | []}),;:]')
WHITESPACE_AFTER_COMMA_REGEX = re.compile(r'[,;:]\s*(?:  |\t)')
COMPARE_SINGLETON_REGEX = re.compile(r'([=!]=)\s*(None|False|True)')
COMPARE_TYPE_REGEX = re.compile(r'([=!]=|is|is\s+not)\s*type(?:s\.(\w+)Type'
                                r'|\(\s*(\(\s*\)|[^)]*[^ )])\s*\))')
KEYWORD_REGEX = re.compile(r'(?:[^\s])(\s*)\b(?:%s)\b(\s*)' %
                           r'|'.join(KEYWORDS))
OPERATOR_REGEX = re.compile(r'(?:[^\s])(\s*)(?:[-+*/|!<=>%&^]+)(\s*)')
LAMBDA_REGEX = re.compile(r'\blambda\b')
HUNK_REGEX = re.compile(r'^@@ -\d+,\d+ \+(\d+),(\d+) @@.*$')

# Work around Python < 2.6 behaviour, which does not generate NL after
# a comment which is on a line by itself.
COMMENT_WITH_NL = tokenize.generate_tokens(['#\n'].pop).send(None)[1] == '#\n'


#Define instance options to set options to be analized
class Options:
    pass


options = Options()
#Set the options to be analized
options.show_source = True
options.repeat = True
options.show_pep8 = False
options.messages = {}
options.select = []
options.ignore = []
options.verbose = 0
options.quiet = 0
options.max_line_length = MAX_LINE_LENGTH
options.ignore_continuation_indentation = True


##############################################################################
# Plugins (check functions) for physical lines
##############################################################################


def tabs_or_spaces(physical_line, indent_char):
    r"""
    Never mix tabs and spaces.

    The most popular way of indenting Python is with spaces only.  The
    second-most popular way is with tabs only.  Code indented with a mixture
    of tabs and spaces should be converted to using spaces exclusively.  When
    invoking the Python command line interpreter with the -t option, it issues
    warnings about code that illegally mixes tabs and spaces.  When using -tt
    these warnings become errors.  These options are highly recommended!

    Okay: if a == 0:\n        a = 1\n        b = 1
    E101: if a == 0:\n        a = 1\n\tb = 1
    """
    indent = INDENT_REGEX.match(physical_line).group(1)
    for offset, char in enumerate(indent):
        if char != indent_char:
            return offset, "E101 indentation contains mixed spaces and tabs"


def tabs_obsolete(physical_line):
    r"""
    For new projects, spaces-only are strongly recommended over tabs.  Most
    editors have features that make this easy to do.

    Okay: if True:\n    return
    W191: if True:\n\treturn
    """
    indent = INDENT_REGEX.match(physical_line).group(1)
    if '\t' in indent:
        return indent.index('\t'), "W191 indentation contains tabs"


def trailing_whitespace(physical_line):
    r"""
    JCR: Trailing whitespace is superfluous.
    FBM: Except when it occurs as part of a blank line (i.e. the line is
         nothing but whitespace). According to Python docs[1] a line with only
         whitespace is considered a blank line, and is to be ignored. However,
         matching a blank line to its indentation level avoids mistakenly
         terminating a multi-line statement (e.g. class declaration) when
         pasting code into the standard Python interpreter.

         [1] http://docs.python.org/reference/lexical_analysis.html#blank-lines

    The warning returned varies on whether the line itself is blank, for easier
    filtering for those who want to indent their blank lines.

    Okay: spam(1)
    W291: spam(1)\s
    W293: class Foo(object):\n    \n    bang = 12
    """
    physical_line = physical_line.rstrip('\n')    # chr(10), newline
    physical_line = physical_line.rstrip('\r')    # chr(13), carriage return
    physical_line = physical_line.rstrip('\x0c')  # chr(12), form feed, ^L
    stripped = physical_line.rstrip(' \t\v')
    if physical_line != stripped:
        if stripped:
            return len(stripped), "W291 trailing whitespace"
        else:
            return 0, "W293 blank line contains whitespace"


def trailing_blank_lines(physical_line, lines, line_number):
    r"""
    JCR: Trailing blank lines are superfluous.

    Okay: spam(1)
    W391: spam(1)\n
    """
    if not physical_line.rstrip() and line_number == len(lines):
        return 0, "W391 blank line at end of file"


def missing_newline(physical_line):
    """
    JCR: The last line should have a newline.

    Reports warning W292.
    """
    if physical_line.rstrip() == physical_line:
        return len(physical_line), "W292 no newline at end of file"


def maximum_line_length(physical_line, max_line_length):
    """
    Limit all lines to a maximum of 79 characters.

    There are still many devices around that are limited to 80 character
    lines; plus, limiting windows to 80 characters makes it possible to have
    several windows side-by-side.  The default wrapping on such devices looks
    ugly.  Therefore, please limit all lines to a maximum of 79 characters.
    For flowing long blocks of text (docstrings or comments), limiting the
    length to 72 characters is recommended.

    Reports error E501.
    """
    line = physical_line.rstrip()
    length = len(line)
    if length > max_line_length:
        if hasattr(line, 'decode'):   # Python 2
            # The line could contain multi-byte characters
            try:
                length = len(line.decode('utf-8'))
            except UnicodeError:
                pass
        if length > max_line_length:
            return (max_line_length, "E501 line too long "
                    "(%d > %d characters)" % (length, max_line_length))


##############################################################################
# Plugins (check functions) for logical lines
##############################################################################


def blank_lines(logical_line, blank_lines, indent_level, line_number,
                previous_logical, previous_indent_level):
    r"""
    Separate top-level function and class definitions with two blank lines.

    Method definitions inside a class are separated by a single blank line.

    Extra blank lines may be used (sparingly) to separate groups of related
    functions.  Blank lines may be omitted between a bunch of related
    one-liners (e.g. a set of dummy implementations).

    Use blank lines in functions, sparingly, to indicate logical sections.

    Okay: def a():\n    pass\n\n\ndef b():\n    pass
    Okay: def a():\n    pass\n\n\n# Foo\n# Bar\n\ndef b():\n    pass

    E301: class Foo:\n    b = 0\n    def bar():\n        pass
    E302: def a():\n    pass\n\ndef b(n):\n    pass
    E303: def a():\n    pass\n\n\n\ndef b(n):\n    pass
    E303: def a():\n\n\n\n    pass
    E304: @decorator\n\ndef a():\n    pass
    """
    if line_number == 1:
        return  # Don't expect blank lines before the first line
    if previous_logical.startswith('@'):
        if blank_lines:
            yield 0, "E304 blank lines found after function decorator"
    elif blank_lines > 2 or (indent_level and blank_lines == 2):
        yield 0, "E303 too many blank lines (%d)" % blank_lines
    elif logical_line.startswith(('def ', 'class ', '@')):
        if indent_level:
            if not (blank_lines or previous_indent_level < indent_level or
                    DOCSTRING_REGEX.match(previous_logical)):
                yield 0, "E301 expected 1 blank line, found 0"
        elif blank_lines != 2:
            yield 0, "E302 expected 2 blank lines, found %d" % blank_lines


def extraneous_whitespace(logical_line):
    """
    Avoid extraneous whitespace in the following situations:

    - Immediately inside parentheses, brackets or braces.

    - Immediately before a comma, semicolon, or colon.

    Okay: spam(ham[1], {eggs: 2})
    E201: spam( ham[1], {eggs: 2})
    E201: spam(ham[ 1], {eggs: 2})
    E201: spam(ham[1], { eggs: 2})
    E202: spam(ham[1], {eggs: 2} )
    E202: spam(ham[1 ], {eggs: 2})
    E202: spam(ham[1], {eggs: 2 })

    E203: if x == 4: print x, y; x, y = y , x
    E203: if x == 4: print x, y ; x, y = y, x
    E203: if x == 4 : print x, y; x, y = y, x
    """
    line = logical_line
    for match in EXTRANEOUS_WHITESPACE_REGEX.finditer(line):
        text = match.group()
        char = text.strip()
        found = match.start()
        if text == char + ' ':
            # assert char in '([{'
            yield found + 1, "E201 whitespace after '%s'" % char
        elif line[found - 1] != ',':
            code = ('E202' if char in '}])' else 'E203')  # if char in ',;:'
            yield found, "%s whitespace before '%s'" % (code, char)


def whitespace_around_keywords(logical_line):
    r"""
    Avoid extraneous whitespace around keywords.

    Okay: True and False
    E271: True and  False
    E272: True  and False
    E273: True and\tFalse
    E274: True\tand False
    """
    for match in KEYWORD_REGEX.finditer(logical_line):
        before, after = match.groups()

        if '\t' in before:
            yield match.start(1), "E274 tab before keyword"
        elif len(before) > 1:
            yield match.start(1), "E272 multiple spaces before keyword"

        if '\t' in after:
            yield match.start(2), "E273 tab after keyword"
        elif len(after) > 1:
            yield match.start(2), "E271 multiple spaces after keyword"


def missing_whitespace(logical_line):
    """
    JCR: Each comma, semicolon or colon should be followed by whitespace.

    Okay: [a, b]
    Okay: (3,)
    Okay: a[1:4]
    Okay: a[:4]
    Okay: a[1:]
    Okay: a[1:4:2]
    E231: ['a','b']
    E231: foo(bar,baz)
    """
    line = logical_line
    for index in range(len(line) - 1):
        char = line[index]
        if char in ',;:' and line[index + 1] not in WHITESPACE:
            before = line[:index]
            if char == ':' and before.count('[') > before.count(']'):
                continue  # Slice syntax, no space required
            if char == ',' and line[index + 1] == ')':
                continue  # Allow tuple with only one element: (3,)
            yield index, "E231 missing whitespace after '%s'" % char


def indentation(logical_line, previous_logical, indent_char,
                indent_level, previous_indent_level):
    r"""
    Use 4 spaces per indentation level.

    For really old code that you don't want to mess up, you can continue to
    use 8-space tabs.

    Okay: a = 1
    Okay: if a == 0:\n    a = 1
    E111:   a = 1

    Okay: for item in items:\n    pass
    E112: for item in items:\npass

    Okay: a = 1\nb = 2
    E113: a = 1\n    b = 2
    """
    if indent_char == ' ' and indent_level % 4:
        yield 0, "E111 indentation is not a multiple of four"
    indent_expect = previous_logical.endswith(':')
    if indent_expect and indent_level <= previous_indent_level:
        yield 0, "E112 expected an indented block"
    if indent_level > previous_indent_level and not indent_expect:
        yield 0, "E113 unexpected indentation"


def continuation_line_indentation(logical_line, tokens, indent_level, verbose):
    r"""
    Continuation lines should align wrapped elements either vertically using
    Python's implicit line joining inside parentheses, brackets and braces, or
    using a hanging indent.

    When using a hanging indent the following considerations should be applied:

    - there should be no arguments on the first line, and

    - further indentation should be used to clearly distinguish itself as a
      continuation line.

    Okay: a = (\n)
    E123: a = (\n    )

    Okay: a = (\n    42)
    E121: a = (\n   42)
    E122: a = (\n42)
    E123: a = (\n    42\n    )
    E124: a = (24,\n     42\n)
    E125: if (a or\n    b):\n    pass
    E126: a = (\n        42)
    E127: a = (24,\n      42)
    E128: a = (24,\n    42)
    """
    if options.ignore_continuation_indentation:
        return
    first_row = tokens[0][2][0]
    nrows = 1 + tokens[-1][2][0] - first_row
    if nrows == 1:
        return

    # indent_next tells us whether the next block is indented; assuming
    # that it is indented by 4 spaces, then we should not allow 4-space
    # indents on the final continuation line; in turn, some other
    # indents are allowed to have an extra 4 spaces.
    indent_next = logical_line.endswith(':')

    row = depth = 0
    # remember how many brackets were opened on each line
    parens = [0] * nrows
    # relative indents of physical lines
    rel_indent = [0] * nrows
    # visual indents
    indent = [indent_level]
    indent_chances = {}
    last_indent = tokens[0][2]

    for token_type, text, start, end, line in tokens:
        newline = row < start[0] - first_row
        if newline:
            row = start[0] - first_row
            newline = (not last_token_multiline and
                       token_type not in (tokenize.NL, tokenize.NEWLINE))

        if newline:
            # this is the beginning of a continuation line.
            last_indent = start

            # record the initial indent.
            rel_indent[row] = start[1] - indent_level

            if depth:
                # a bracket expression in a continuation line.
                # find the line that it was opened on
                for open_row in range(row - 1, -1, -1):
                    if parens[open_row]:
                        break
            else:
                # an unbracketed continuation line (ie, backslash)
                open_row = 0
            hang = rel_indent[row] - rel_indent[open_row]
            visual_indent = indent_chances.get(start[1])

            if token_type == tokenize.OP and text in ']})':
                # this line starts with a closing bracket
                if indent[depth]:
                    if start[1] != indent[depth]:
                        yield (start, 'E124 closing bracket does not match '
                               'visual indentation')
                elif hang:
                    yield (start, 'E123 closing bracket does not match '
                           'indentation of opening bracket\'s line')
            elif visual_indent is True:
                # visual indent is verified
                if not indent[depth]:
                    indent[depth] = start[1]
            elif visual_indent in (text, str):
                # ignore token lined up with matching one from a previous line
                pass
            elif indent[depth] and start[1] < indent[depth]:
                # visual indent is broken
                yield (start, 'E128 continuation line '
                       'under-indented for visual indent')
            elif hang == 4 or (indent_next and rel_indent[row] == 8):
                # hanging indent is verified
                pass
            else:
                # indent is broken
                if hang <= 0:
                    error = 'E122', 'missing indentation or outdented'
                elif indent[depth]:
                    error = 'E127', 'over-indented for visual indent'
                elif hang % 4:
                    error = 'E121', 'indentation is not a multiple of four'
                else:
                    error = 'E126', 'over-indented for hanging indent'
                yield start, "%s continuation line %s" % error

        # look for visual indenting
        if (parens[row] and token_type not in (tokenize.NL, tokenize.COMMENT)
                and not indent[depth]):
            indent[depth] = start[1]
            indent_chances[start[1]] = True
        # deal with implicit string concatenation
        elif token_type == tokenize.STRING or text in ('u', 'ur', 'b', 'br'):
            indent_chances[start[1]] = str

        # keep track of bracket depth
        if token_type == tokenize.OP:
            if text in '([{':
                depth += 1
                indent.append(0)
                parens[row] += 1
            elif text in ')]}' and depth > 0:
                # parent indents should not be more than this one
                prev_indent = indent.pop() or last_indent[1]
                for d in range(depth):
                    if indent[d] > prev_indent:
                        indent[d] = 0
                for ind in list(indent_chances):
                    if ind >= prev_indent:
                        del indent_chances[ind]
                depth -= 1
                if depth:
                    indent_chances[indent[depth]] = True
                for idx in range(row, -1, -1):
                    if parens[idx]:
                        parens[idx] -= 1
                        break
            assert len(indent) == depth + 1
            if start[1] not in indent_chances:
                # allow to line up tokens
                indent_chances[start[1]] = text

        last_token_multiline = (start[0] != end[0])

    if indent_next and rel_indent[-1] == 4:
        yield (last_indent, "E125 continuation line does not distinguish "
               "itself from next logical line")


def whitespace_before_parameters(logical_line, tokens):
    """
    Avoid extraneous whitespace in the following situations:

    - Immediately before the open parenthesis that starts the argument
      list of a function call.

    - Immediately before the open parenthesis that starts an indexing or
      slicing.

    Okay: spam(1)
    E211: spam (1)

    Okay: dict['key'] = list[index]
    E211: dict ['key'] = list[index]
    E211: dict['key'] = list [index]
    """
    prev_type = tokens[0][0]
    prev_text = tokens[0][1]
    prev_end = tokens[0][3]
    for index in range(1, len(tokens)):
        token_type, text, start, end, line = tokens[index]
        if (token_type == tokenize.OP and
            text in '([' and
            start != prev_end and
            (prev_type == tokenize.NAME or prev_text in '}])') and
            # Syntax "class A (B):" is allowed, but avoid it
            (index < 2 or tokens[index - 2][1] != 'class') and
                # Allow "return (a.foo for a in range(5))"
                not keyword.iskeyword(prev_text)):
            yield prev_end, "E211 whitespace before '%s'" % text
        prev_type = token_type
        prev_text = text
        prev_end = end


def whitespace_around_operator(logical_line):
    r"""
    Avoid extraneous whitespace in the following situations:

    - More than one space around an assignment (or other) operator to
      align it with another.

    Okay: a = 12 + 3
    E221: a = 4  + 5
    E222: a = 4 +  5
    E223: a = 4\t+ 5
    E224: a = 4 +\t5
    """
    for match in OPERATOR_REGEX.finditer(logical_line):
        before, after = match.groups()

        if '\t' in before:
            yield match.start(1), "E223 tab before operator"
        elif len(before) > 1:
            yield match.start(1), "E221 multiple spaces before operator"

        if '\t' in after:
            yield match.start(2), "E224 tab after operator"
        elif len(after) > 1:
            yield match.start(2), "E222 multiple spaces after operator"


def missing_whitespace_around_operator(logical_line, tokens):
    r"""
    - Always surround these binary operators with a single space on
      either side: assignment (=), augmented assignment (+=, -= etc.),
      comparisons (==, <, >, !=, <>, <=, >=, in, not in, is, is not),
      Booleans (and, or, not).

    - Use spaces around arithmetic operators.

    Okay: i = i + 1
    Okay: submitted += 1
    Okay: x = x * 2 - 1
    Okay: hypot2 = x * x + y * y
    Okay: c = (a + b) * (a - b)
    Okay: foo(bar, key='word', *args, **kwargs)
    Okay: baz(**kwargs)
    Okay: negative = -1
    Okay: spam(-1)
    Okay: alpha[:-i]
    Okay: if not -5 < x < +5:\n    pass
    Okay: lambda *args, **kw: (args, kw)

    E225: i=i+1
    E225: submitted +=1
    E225: x = x*2 - 1
    E225: hypot2 = x*x + y*y
    E225: c = (a+b) * (a-b)
    E225: c = alpha -4
    E225: z = x **y
    """
    parens = 0
    need_space = False
    prev_type = tokenize.OP
    prev_text = prev_end = None
    for token_type, text, start, end, line in tokens:
        if token_type in (tokenize.NL, tokenize.NEWLINE, tokenize.ERRORTOKEN):
            # ERRORTOKEN is triggered by backticks in Python 3000
            continue
        if text in ('(', 'lambda'):
            parens += 1
        elif text == ')':
            parens -= 1
        if need_space:
            if start != prev_end:
                need_space = False
            elif text == '>' and prev_text in ('<', '-'):
                # Tolerate the "<>" operator, even if running Python 3
                # Deal with Python 3's annotated return value "->"
                pass
            else:
                yield prev_end, "E225 missing whitespace around operator"
                need_space = False
        elif token_type == tokenize.OP and prev_end is not None:
            if text == '=' and parens:
                # Allow keyword args or defaults: foo(bar=None).
                pass
            elif text in BINARY_OPERATORS:
                need_space = True
            elif text in UNARY_OPERATORS:
                # Allow unary operators: -123, -x, +1.
                # Allow argument unpacking: foo(*args, **kwargs).
                if prev_type == tokenize.OP:
                    if prev_text in '}])':
                        need_space = True
                elif prev_type == tokenize.NAME:
                    if prev_text not in KEYWORDS:
                        need_space = True
                elif prev_type not in SKIP_TOKENS:
                    need_space = True
            if need_space and start == prev_end:
                yield prev_end, "E225 missing whitespace around operator"
                need_space = False
        prev_type = token_type
        prev_text = text
        prev_end = end


def whitespace_around_comma(logical_line):
    r"""
    Avoid extraneous whitespace in the following situations:

    - More than one space around an assignment (or other) operator to
      align it with another.

    Note: these checks are disabled by default

    Okay: a = (1, 2)
    E241: a = (1,  2)
    E242: a = (1,\t2)
    """
    line = logical_line
    for m in WHITESPACE_AFTER_COMMA_REGEX.finditer(line):
        found = m.start() + 1
        if '\t' in m.group():
            yield found, "E242 tab after '%s'" % m.group()[0]
        else:
            yield found, "E241 multiple spaces after '%s'" % m.group()[0]


def whitespace_around_named_parameter_equals(logical_line, tokens):
    """
    Don't use spaces around the '=' sign when used to indicate a
    keyword argument or a default parameter value.

    Okay: def complex(real, imag=0.0):
    Okay: return magic(r=real, i=imag)
    Okay: boolean(a == b)
    Okay: boolean(a != b)
    Okay: boolean(a <= b)
    Okay: boolean(a >= b)

    E251: def complex(real, imag = 0.0):
    E251: return magic(r = real, i = imag)
    """
    parens = 0
    no_space = False
    prev_end = None
    for token_type, text, start, end, line in tokens:
        if no_space:
            no_space = False
            if start != prev_end:
                yield (prev_end,
                       "E251 no spaces around keyword / parameter equals")
        elif token_type == tokenize.OP:
            if text == '(':
                parens += 1
            elif text == ')':
                parens -= 1
            elif parens and text == '=':
                no_space = True
                if start != prev_end:
                    yield (prev_end,
                           "E251 no spaces around keyword / parameter equals")
        prev_end = end


def whitespace_before_inline_comment(logical_line, tokens):
    """
    Separate inline comments by at least two spaces.

    An inline comment is a comment on the same line as a statement.  Inline
    comments should be separated by at least two spaces from the statement.
    They should start with a # and a single space.

    Okay: x = x + 1  # Increment x
    Okay: x = x + 1    # Increment x
    E261: x = x + 1 # Increment x
    E262: x = x + 1  #Increment x
    E262: x = x + 1  #  Increment x
    """
    prev_end = (0, 0)
    for token_type, text, start, end, line in tokens:
        if token_type == tokenize.COMMENT:
            if not line[:start[1]].strip():
                continue
            if prev_end[0] == start[0] and start[1] < prev_end[1] + 2:
                yield (prev_end,
                       "E261 at least two spaces before inline comment")
            if text.startswith('#  ') or not text.startswith('# '):
                yield start, "E262 inline comment should start with '# '"
        elif token_type != tokenize.NL:
            prev_end = end


def imports_on_separate_lines(logical_line):
    r"""
    Imports should usually be on separate lines.

    Okay: import os\nimport sys
    E401: import sys, os

    Okay: from subprocess import Popen, PIPE
    Okay: from myclas import MyClass
    Okay: from foo.bar.yourclass import YourClass
    Okay: import myclass
    Okay: import foo.bar.yourclass
    """
    line = logical_line
    if line.startswith('import '):
        found = line.find(',')
        if -1 < found and ';' not in line[:found]:
            yield found, "E401 multiple imports on one line"


def compound_statements(logical_line):
    r"""
    Compound statements (multiple statements on the same line) are
    generally discouraged.

    While sometimes it's okay to put an if/for/while with a small body
    on the same line, never do this for multi-clause statements. Also
    avoid folding such long lines!

    Okay: if foo == 'blah':\n    do_blah_thing()
    Okay: do_one()
    Okay: do_two()
    Okay: do_three()

    E701: if foo == 'blah': do_blah_thing()
    E701: for x in lst: total += x
    E701: while t < 10: t = delay()
    E701: if foo == 'blah': do_blah_thing()
    E701: else: do_non_blah_thing()
    E701: try: something()
    E701: finally: cleanup()
    E701: if foo == 'blah': one(); two(); three()

    E702: do_one(); do_two(); do_three()
    """
    line = logical_line
    found = line.find(':')
    if -1 < found < len(line) - 1:
        before = line[:found]
        if (before.count('{') <= before.count('}') and  # {'a': 1} (dict)
            before.count('[') <= before.count(']') and  # [1:2] (slice)
            before.count('(') <= before.count(')') and  # (Python 3 annotation)
                not LAMBDA_REGEX.search(before)):       # lambda x: x
            yield found, "E701 multiple statements on one line (colon)"
    found = line.find(';')
    if -1 < found:
        yield found, "E702 multiple statements on one line (semicolon)"


def explicit_line_join(logical_line, tokens):
    r"""
    Avoid explicit line join between brackets.

    The preferred way of wrapping long lines is by using Python's implied line
    continuation inside parentheses, brackets and braces.  Long lines can be
    broken over multiple lines by wrapping expressions in parentheses.  These
    should be used in preference to using a backslash for line continuation.

    E502: aaa = [123, \\n       123]
    E502: aaa = ("bbb " \\n       "ccc")

    Okay: aaa = [123,\n       123]
    Okay: aaa = ("bbb "\n       "ccc")
    Okay: aaa = "bbb " \\n    "ccc"
    """
    prev_start = prev_end = parens = 0
    for token_type, text, start, end, line in tokens:
        if start[0] != prev_start and parens and backslash:
            yield backslash, "E502 the backslash is redundant between brackets"
        if end[0] != prev_end:
            if line.rstrip('\r\n').endswith('\\'):
                backslash = (end[0], len(line.splitlines()[-1]) - 1)
            else:
                backslash = None
            prev_start = prev_end = end[0]
        else:
            prev_start = start[0]
        if token_type == tokenize.OP:
            if text in '([{':
                parens += 1
            elif text in ')]}':
                parens -= 1


def comparison_to_singleton(logical_line):
    """
    Comparisons to singletons like None should always be done
    with "is" or "is not", never the equality operators.

    Okay: if arg is not None:
    E711: if arg != None:
    E712: if arg == True:

    Also, beware of writing if x when you really mean if x is not None --
    e.g. when testing whether a variable or argument that defaults to None was
    set to some other value.  The other value might have a type (such as a
    container) that could be false in a boolean context!
    """
    match = COMPARE_SINGLETON_REGEX.search(logical_line)
    if match:
        same = (match.group(1) == '==')
        singleton = match.group(2)
        msg = "'if cond is %s:'" % (('' if same else 'not ') + singleton)
        if singleton in ('None',):
            code = 'E711'
        else:
            code = 'E712'
            nonzero = ((singleton == 'True' and same) or
                       (singleton == 'False' and not same))
            msg += " or 'if %scond:'" % ('' if nonzero else 'not ')
        yield match.start(1), ("%s comparison to %s should be %s" %
                               (code, singleton, msg))


def comparison_type(logical_line):
    """
    Object type comparisons should always use isinstance() instead of
    comparing types directly.

    Okay: if isinstance(obj, int):
    E721: if type(obj) is type(1):

    When checking if an object is a string, keep in mind that it might be a
    unicode string too! In Python 2.3, str and unicode have a common base
    class, basestring, so you can do:

    Okay: if isinstance(obj, basestring):
    Okay: if type(a1) is type(b1):
    """
    match = COMPARE_TYPE_REGEX.search(logical_line)
    if match:
        inst = match.group(3)
        if inst and isidentifier(inst) and inst not in SINGLETONS:
            return  # Allow comparison for types which are not obvious
        yield match.start(1), "E721 do not compare types, use 'isinstance()'"


def python_3000_has_key(logical_line):
    r"""
    The {}.has_key() method will be removed in the future version of
    Python. Use the 'in' operation instead.

    Okay: if "alph" in d:\n    print d["alph"]
    W601: assert d.has_key('alph')
    """
    pos = logical_line.find('.has_key(')
    if pos > -1:
        yield pos, "W601 .has_key() is deprecated, use 'in'"


def python_3000_raise_comma(logical_line):
    """
    When raising an exception, use "raise ValueError('message')"
    instead of the older form "raise ValueError, 'message'".

    The paren-using form is preferred because when the exception arguments
    are long or include string formatting, you don't need to use line
    continuation characters thanks to the containing parentheses.  The older
    form will be removed in Python 3000.

    Okay: raise DummyError("Message")
    W602: raise DummyError, "Message"
    """
    match = RAISE_COMMA_REGEX.match(logical_line)
    if match and not RERAISE_COMMA_REGEX.match(logical_line):
        yield match.start(1), "W602 deprecated form of raising exception"


def python_3000_not_equal(logical_line):
    """
    != can also be written <>, but this is an obsolete usage kept for
    backwards compatibility only. New code should always use !=.
    The older syntax is removed in Python 3000.

    Okay: if a != 'no':
    W603: if a <> 'no':
    """
    pos = logical_line.find('<>')
    if pos > -1:
        yield pos, "W603 '<>' is deprecated, use '!='"


def python_3000_backticks(logical_line):
    """
    Backticks are removed in Python 3000.
    Use repr() instead.

    Okay: val = repr(1 + 2)
    W604: val = `1 + 2`
    """
    pos = logical_line.find('`')
    if pos > -1:
        yield pos, "W604 backticks are deprecated, use 'repr()'"


##############################################################################
# Helper functions
##############################################################################

if '' == ''.encode():
    # Python 2: implicit encoding.
    isidentifier = re.compile(r'[a-zA-Z_]\w*').match
else:
    # Python 3
    isidentifier = str.isidentifier


def expand_indent(line):
    r"""
    Return the amount of indentation.
    Tabs are expanded to the next multiple of 8.

    >>> expand_indent('    ')
    4
    >>> expand_indent('\t')
    8
    >>> expand_indent('    \t')
    8
    >>> expand_indent('       \t')
    8
    >>> expand_indent('        \t')
    16
    """
    if '\t' not in line:
        return len(line) - len(line.lstrip())
    result = 0
    for char in line:
        if char == '\t':
            result = result // 8 * 8 + 8
        elif char == ' ':
            result += 1
        else:
            break
    return result


def mute_string(text):
    """
    Replace contents with 'xxx' to prevent syntax matching.

    >>> mute_string('"abc"')
    '"xxx"'
    >>> mute_string("'''abc'''")
    "'''xxx'''"
    >>> mute_string("r'abc'")
    "r'xxx'"
    """
    # String modifiers (e.g. u or r)
    start = text.index(text[-1]) + 1
    end = len(text) - 1
    # Triple quotes
    if text[-3:] in ('"""', "'''"):  # '''
        start += 2
        end -= 2
    return text[:start] + 'x' * (end - start) + text[end:]


##############################################################################
# Framework to run all checks
##############################################################################


def find_checks(argument_name):
    """
    Find all globally visible functions where the first argument name
    starts with argument_name.
    """
    checks = []
    for name, function in list(globals().items()):
        if not inspect.isfunction(function):
            continue
        args = inspect.getargspec(function)[0]
        if args and args[0].startswith(argument_name):
            codes = ERRORCODE_REGEX.findall(function.__doc__ or '')
#            yield name, codes, function, args
            for code in codes or ['']:
                    if not code or not ignore_code(code):
                        checks.append((name, function, args))
                        break
    checks.sort()
    return checks


def ignore_code(code):
    """
    Check if options.ignore contains a prefix of the error code.
    If options.select contains a prefix of the error code, do not ignore it.
    """
    for select in options.select:
        if code.startswith(select):
            return False
    for ignore in options.ignore:
        if code.startswith(ignore):
            return True


#Set Physical and Logical check functions
options.physical_checks = find_checks('physical_line')
options.logical_checks = find_checks('logical_line')


def refresh_checks():
    #Refresh the Physical and Logical check functions
    options.physical_checks = find_checks('physical_line')
    options.logical_checks = find_checks('logical_line')


class Checker(object):
    """
    Load a Python source file, tokenize it, check coding style.
    """

    def __init__(self, filename, lines=None):
        self._physical_checks = options.physical_checks
        self._logical_checks = options.logical_checks
        self.max_line_length = options.max_line_length
        self.verbose = options.verbose
        self.filename = filename
        self.lines = lines
        self.results = []

    def readline(self):
        """
        Get the next line from the input buffer.
        """
        self.line_number += 1
        if self.line_number > len(self.lines):
            return ''
        return self.lines[self.line_number - 1]

    def readline_check_physical(self):
        """
        Check and return the next physical line. This method can be
        used to feed tokenize.generate_tokens.
        """
        line = self.readline()
        if line:
            self.check_physical(line)
        return line

    def run_check(self, check, argument_names):
        """
        Run a check plugin.
        """
        arguments = []
        for name in argument_names:
            arguments.append(getattr(self, name))
        return check(*arguments)

    def check_physical(self, line):
        """
        Run all physical checks on a raw input line.
        """
        self.physical_line = line
        if self.indent_char is None and line[:1] in WHITESPACE:
            self.indent_char = line[0]
        for name, check, argument_names in self._physical_checks:
            result = self.run_check(check, argument_names)
            if result is not None:
                offset, text = result
                self.report_error(self.line_number, offset, text, check)

    def build_tokens_line(self):
        """
        Build a logical line from tokens.
        """
        self.mapping = []
        logical = []
        length = 0
        previous = None
        for token in self.tokens:
            token_type, text = token[0:2]
            if token_type in SKIP_TOKENS:
                continue
            if token_type == tokenize.STRING:
                text = mute_string(text)
            if previous:
                end_row, end = previous[3]
                start_row, start = token[2]
                if end_row != start_row:    # different row
                    prev_text = self.lines[end_row - 1][end - 1]
                    if prev_text == ',' or (prev_text not in '{[('
                                            and text not in '}])'):
                        logical.append(' ')
                        length += 1
                elif end != start:  # different column
                    fill = self.lines[end_row - 1][end:start]
                    logical.append(fill)
                    length += len(fill)
            self.mapping.append((length, token))
            logical.append(text)
            length += len(text)
            previous = token
        self.logical_line = ''.join(logical)
        assert self.logical_line.strip() == self.logical_line

    def check_logical(self):
        """
        Build a line from tokens and run all logical checks on it.
        """
        self.build_tokens_line()
        first_line = self.lines[self.mapping[0][1][2][0] - 1]
        indent = first_line[:self.mapping[0][1][2][1]]
        self.previous_indent_level = self.indent_level
        self.indent_level = expand_indent(indent)
        for name, check, argument_names in self._logical_checks:
            for result in self.run_check(check, argument_names):
                offset, text = result
                if isinstance(offset, tuple):
                    orig_number, orig_offset = offset
                else:
                    for token_offset, token in self.mapping:
                        if offset >= token_offset:
                            orig_number = token[2][0]
                            orig_offset = (token[2][1] + offset - token_offset)
                self.report_error(orig_number, orig_offset, text, check)
        self.previous_logical = self.logical_line

    def generate_tokens(self):
        tokengen = tokenize.generate_tokens(self.readline_check_physical)
        try:
            for token in tokengen:
                yield token
        except (SyntaxError, tokenize.TokenError):
            exc_type, exc = sys.exc_info()[:2]
            offset = exc.args[1]
            if len(offset) > 2:
                offset = offset[1:3]
            self.report_error(offset[0], offset[1],
                              'E901 %s: %s' % (exc_type.__name__, exc.args[0]),
                              self.generate_tokens)
    generate_tokens.__doc__ = "    Check if the syntax is valid."

    def check_all(self, expected=None, line_offset=0):
        """
        Run all checks on the input file.
        """
        self.line_number = 0
        self.line_offset = line_offset
        self.indent_char = None
        self.indent_level = 0
        self.previous_logical = ''
        self.tokens = []
        self.blank_lines = blank_lines_before_comment = 0
        parens = 0
        for token in self.generate_tokens():
            self.tokens.append(token)
            token_type, text = token[0:2]
            if self.verbose >= 3:
                if token[2][0] == token[3][0]:
                    pos = '[%s:%s]' % (token[2][1] or '', token[3][1])
                else:
                    pos = 'l.%s' % token[3][0]
            if token_type == tokenize.OP:
                if text in '([{':
                    parens += 1
                elif text in '}])':
                    parens -= 1
            elif not parens:
                if token_type == tokenize.NEWLINE:
                    if self.blank_lines < blank_lines_before_comment:
                        self.blank_lines = blank_lines_before_comment
                    self.check_logical()
                    self.tokens = []
                    self.blank_lines = blank_lines_before_comment = 0
                elif token_type == tokenize.NL:
                    if len(self.tokens) == 1:
                        # The physical line contains only this token.
                        self.blank_lines += 1
                    self.tokens = []
                elif token_type == tokenize.COMMENT and len(self.tokens) == 1:
                    if blank_lines_before_comment < self.blank_lines:
                        blank_lines_before_comment = self.blank_lines
                    self.blank_lines = 0
                    if COMMENT_WITH_NL:
                        # The comment also ends a physical line
                        self.tokens = []
        return self.results

    def report_error(self, line_number, offset, text, check):
        """
        Report an error, according to options.
        """
        if options.repeat:
            self.results.append("%s:%s:%d: %s" %
                    (self.filename, self.line_offset + line_number,
                     offset + 1, text))
            if options.show_source and len(self.lines) >= line_number:
                line = self.lines[line_number - 1]
                self.results.append(line.rstrip())
                self.results.append(' ' * offset + '^')
            if options.show_pep8:
                self.results.append(check.__doc__.lstrip('\n').rstrip())


def run_check(fileName, source):
    """
    Parse options and run checks on Python source.
    """
    try:
        lines = ['%s\n' % line for line in source.splitlines()]
        return Checker(fileName, lines).check_all()
    except Exception as reason:
        print(('pep8mod couldn\'t parse file: {0}'.format(fileName)))
        print(reason)
        raise
    return []
