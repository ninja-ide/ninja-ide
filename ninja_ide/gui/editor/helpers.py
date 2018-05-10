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

import re
import sys

from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtGui import QTextCursor

from ninja_ide.core import settings
from ninja_ide.core.file_handling import file_manager
from ninja_ide.tools import introspection


patIndent = re.compile('^\s+')
pat_word = re.compile(r"^[\t ]*$|[^\s]+")
patSymbol = re.compile(r'[^\w]')
patIsLocalFunction = re.compile('(\s)+self\.(\w)+\(\)')
patClass = re.compile("(\\s)*class.+\\:$")
endCharsForIndent = [':', '{', '(', '[']
closeBraces = {'{': '}', '(': ')', '[': ']'}
# Coding line by language
CODING_LINE = {
    'python': '# -*- coding: utf-8 -*-'
}


def get_leading_spaces(line):
    global patIndent
    space = patIndent.match(line)
    if space is not None:
        return space.group()
    return ''


def get_range(editor, line, col=-1):

        lineno = line
        line_text = editor.line_text(lineno)
        col_end = len(line_text)
        col_start = col if col > -1 else 0
        if col > -1:
            match = pat_word.match(line_text[col:])
            if match:
                col_end = col_start + match.end()
        else:
            col_start = editor.line_indent(lineno)

        return col_start, col_end


def add_line_increment(lines, lineModified, diference, atLineStart=False):
    """Increment the line number of the list content when needed."""
    def _inner_increment(line):
        if (not atLineStart and line <= lineModified) or (
                lineModified == line + diference):
            return line
        return line + diference
    return list(map(_inner_increment, lines))


def add_line_increment_for_dict(data, lineModified, diference,
                                atLineStart=False):
    """Increment the line number of the dict content when needed."""
    def _inner_increment(line):
        if (not atLineStart and line <= lineModified) or (
                lineModified == line + diference):
            return line
        newLine = line + diference
        summary = data.pop(line)
        data[newLine] = summary
        return newLine
    list(map(_inner_increment, list(data.keys())))
    return data


def insert_horizontal_line(editorWidget):
    line, index = editorWidget.getCursorPosition()
    lang = file_manager.get_file_extension(editorWidget.file_path)
    key = settings.EXTENSIONS.get(lang, 'python')
    comment_wildcard = settings.SYNTAX[key].get('comment', ['#'])[0]
    comment = comment_wildcard * (
        (80 - editorWidget.lineLength(line) / len(comment_wildcard)))
    editorWidget.insertAt(comment, line, index)


def insert_title_comment(editorWidget):
    result = str(QInputDialog.getText(editorWidget,
                 editorWidget.tr("Title Comment"),
                 editorWidget.tr("Enter the Title Name:"))[0])
    if result:
        line, index = editorWidget.getCursorPosition()
        lang = file_manager.get_file_extension(editorWidget.file_path)
        key = settings.EXTENSIONS.get(lang, 'python')
        comment_wildcard = settings.SYNTAX[key].get('comment', ['#'])[0]
        comment = comment_wildcard * (80 / len(comment_wildcard))
        editorWidget.SendScintilla(editorWidget.SCI_BEGINUNDOACTION, 1)
        editorWidget.insertAt(comment, line, index)
        text = "%s %s\n" % (comment_wildcard, result)
        editorWidget.insertAt(text, line + 1, 0)
        editorWidget.insertAt("\n", line + 2, 0)
        editorWidget.insertAt(comment, line + 2, index)
        editorWidget.SendScintilla(editorWidget.SCI_ENDUNDOACTION, 1)


def insert_coding_line(editorWidget):
    key = settings.EXTENSIONS.get(editorWidget.nfile.file_ext)
    coding_line = CODING_LINE.get(key)
    if coding_line:
        editorWidget.insert("%s\n" % coding_line)


def replace_tabs_with_spaces(editorWidget):
    text = editorWidget.text()
    text = text.replace('\t', ' ' * editorWidget._indent)
    editorWidget.selectAll(True)
    editorWidget.replaceSelectedText(text)


def lint_ignore_line(editorWidget):
    if not editorWidget.hasSelectedText():
        line, index = editorWidget.getCursorPosition()
        index = editorWidget.lineLength(line)
        editorWidget.insertAt("  # lint:ok", line, index)


def lint_ignore_selection(editorWidget):
    if editorWidget.hasSelectedText():
        editorWidget.SendScintilla(editorWidget.SCI_BEGINUNDOACTION, 1)
        lstart, istart, lend, iend = editorWidget.getSelection()
        iend = editorWidget.lineLength(lend)
        indentation = get_indentation(editorWidget.text(lstart))
        editorWidget.insertAt("%s#lint:disable\n" % indentation, lstart, 0)
        editorWidget.insertAt("\n%s#lint:enable\n" % indentation, lend, iend)
        editorWidget.SendScintilla(editorWidget.SCI_ENDUNDOACTION, 1)


def insert_debugging_prints(editorWidget):
    if editorWidget.hasSelectedText():
        result = str(QInputDialog.getText(editorWidget,
                     editorWidget.tr("Print Text"),
                     editorWidget.tr("Insert a Text to use in the Print or "
                                     "leave empty to just print numbers:"))[0])
        print_text = ""
        if result:
            print_text = "%s: " % result
        #begin Undo feature
        editorWidget.SendScintilla(editorWidget.SCI_BEGINUNDOACTION, 1)
        lstart, istart, lend, iend = editorWidget.getSelection()
        lines = lend - lstart
        for i in range(lines):
            pos = lstart + (i * 2)
            indentation = get_indentation(editorWidget.text(pos))
            editorWidget.insertAt("%sprint('%s%i')\n" % (
                indentation, print_text, i), pos, 0)
        #end Undo feature
        editorWidget.SendScintilla(editorWidget.SCI_ENDUNDOACTION, 1)


def insert_pdb(editorWidget):
    """Insert a pdb statement into the current line to debug code."""
    line, index = editorWidget.getCursorPosition()
    indentation = get_indentation(editorWidget.text(line))
    editorWidget.insertAt("%simport pdb; pdb.set_trace()\n" % indentation,
                          line, 0)


def remove_line(editorWidget):
    if editorWidget.hasSelectedText():
        lstart, istart, lend, iend = editorWidget.getSelection()
        lines = (lend - lstart) + 1
        editorWidget.SendScintilla(editorWidget.SCI_BEGINUNDOACTION, 1)
        editorWidget.setCursorPosition(lstart, istart)
        for l in range(lines):
            editorWidget.SendScintilla(editorWidget.SCI_LINEDELETE, 1)
        editorWidget.SendScintilla(editorWidget.SCI_ENDUNDOACTION, 1)
    else:
        editorWidget.SendScintilla(editorWidget.SCI_LINEDELETE, 1)


def check_for_assistance_completion(editorWidget, line):
    global patClass
    if patClass.match(line) and editorWidget.lang == 'python':
        source = editorWidget.text()
        source = source.encode(editorWidget.encoding)
        symbols = introspection.obtain_symbols(source)
        clazzName = [name for name in
                     re.split("(\\s)*class(\\s)+|:|\(", line)
                     if name is not None and name.strip()][0]
        clazz_key = [item for item in symbols.get('classes', [])
                     if item.startswith(clazzName)]
        if clazz_key:
            clazz = symbols['classes'][clazz_key['lineno']]
            if [init for init in clazz['members']['functions']
               if init.startswith('__init__')]:
                return
        lnumber, index = editorWidget.getCursorPosition()
        indent = get_indentation(
            line, editorWidget._indent, editorWidget.useTabs)
        init_def = 'def __init__(self):'
        definition = "\n%s%s\n%s" % (indent, init_def, indent * 2)

        super_include = ''
        if line.find('(') != -1:
            classes = line.split('(')
            parents = []
            if len(classes) > 1:
                parents += classes[1].split(',')
            if len(parents) > 0 and 'object):' not in parents:
                super_include = "super({0}, self).__init__()".format(clazzName)
                definition = "\n%s%s\n%s%s\n%s" % (
                    indent, init_def, indent * 2, super_include, indent * 2)

        editorWidget.insertAt(definition, lnumber, index)
        lines = definition.count("\n") + 1
        line_pos = lnumber + lines
        editorWidget.setCursorPosition(
            line_pos, editorWidget.lineLength(line_pos))
