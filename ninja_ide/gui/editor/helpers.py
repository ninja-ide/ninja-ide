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


def get_indentation(line, indent=None, useTabs=None):
    if indent is None:
        indent = settings.INDENT
    if useTabs is None:
        useTabs = settings.USE_TABS
    global patIndent
    global endCharsForIndent
    indentation = ''
    if len(line) > 0 and line[-1] in endCharsForIndent:
        if useTabs:
            indentation = '\t'
        else:
            indentation = ' ' * indent
    elif len(line) > 0 and line[-1] == ',':
        count = [x for x in endCharsForIndent[1:]
                 if (line.count(x) - line.count(closeBraces[x])) % 2 != 0]
        if count:
            if useTabs:
                indentation = '\t'
            else:
                indentation = ' ' * indent
    space = patIndent.match(line)
    if space is not None:
        return space.group() + indentation
    return indentation


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


#def get_first_keyword(line):
    #word = line.split()[0]
    #keyword = remove_symbols(word)

    #if keyword in settings.SYNTAX.get('python')['keywords']:
        #return keyword

    #return word


#def remove_symbols(word):
    #return patSymbol.sub('', word)


#def clean_line(editorWidget):
    #while editorWidget.textCursor().columnNumber() > 0:
        #editorWidget.textCursor().deletePreviousChar()


def remove_trailing_spaces(editor):
    cursor = editor.textCursor()
    block = editor.document().findBlockByLineNumber(0)
    with editor:
        while block.isValid():
            text = block.text()
            if text.endswith(' '):
                cursor.setPosition(block.position())
                cursor.select(QTextCursor.LineUnderCursor)
                cursor.insertText(text.rstrip())
            block = block.next()


def insert_block_at_end(editor):
    last_line = editor.line_count() - 1
    text = editor.line_text(last_line)
    if text:
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertBlock()


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


def move_up(editorWidget):
    editorWidget.SendScintilla(editorWidget.SCI_MOVESELECTEDLINESUP, 1)


def move_down(editorWidget):
    editorWidget.SendScintilla(editorWidget.SCI_MOVESELECTEDLINESDOWN, 1)


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


def duplicate(editorWidget):
    if editorWidget.hasSelectedText():
        lstart, istart, lend, iend = editorWidget.getSelection()
        length = editorWidget.lineLength(lend)
        editorWidget.setSelection(lstart, 0, lend, length)
        text = editorWidget.selectedText()
        editorWidget.SendScintilla(editorWidget.SCI_BEGINUNDOACTION, 1)
        editorWidget.insertAt("%s" % text, lend, length)
        editorWidget.SendScintilla(editorWidget.SCI_ENDUNDOACTION, 1)
    else:
        editorWidget.SendScintilla(editorWidget.SCI_LINEDUPLICATE, 1)


def comment_or_uncomment(editor):
    cursor = editor.textCursor()
    doc = editor.document()
    block_start = doc.findBlock(cursor.selectionStart())
    block_end = doc.findBlock(cursor.selectionEnd()).next()
    key = editor.neditable.language()
    card = settings.SYNTAX[key].get("comment", [])[0]
    has_selection = editor.has_selection()
    lines_commented = 0
    lines_without_comment = 0
    with editor:
        # Save blocks for use later
        temp_start, temp_end = block_start, block_end
        min_indent = sys.maxsize
        comment = True
        card_lenght = len(card)
        # Get operation (comment/uncomment) and the minimum indent
        # of selected lines
        while temp_start != temp_end:
            block_number = temp_start.blockNumber()
            indent = editor.line_indent(block_number)
            block_text = temp_start.text().lstrip()
            if not block_text:
                temp_start = temp_start.next()
                continue
            min_indent = min(indent, min_indent)
            if block_text.startswith(card):
                lines_commented += 1
                comment = False
            elif block_text.startswith(card.strip()):
                lines_commented += 1
                comment = False
                card_lenght -= 1
            else:
                lines_without_comment += 1
                comment = True
            temp_start = temp_start.next()

        total_lines = lines_commented + lines_without_comment
        if lines_commented > 0 and lines_commented != total_lines:
            comment = True
        # Comment/uncomment blocks
        while block_start != block_end:
            cursor.setPosition(block_start.position())
            cursor.movePosition(QTextCursor.StartOfLine)
            cursor.movePosition(QTextCursor.Right,
                                QTextCursor.MoveAnchor, min_indent)
            if block_start.text().lstrip():
                if comment:
                    cursor.insertText(card)
                else:
                    cursor.movePosition(QTextCursor.Right,
                                        QTextCursor.KeepAnchor,
                                        card_lenght)
                    cursor.removeSelectedText()
            block_start = block_start.next()

        if not has_selection:
            cursor.movePosition(QTextCursor.Down)
            editor.setTextCursor(cursor)


def uncomment(editorWidget):
    lstart, istart, lend, iend = editorWidget.getSelection()
    lang = file_manager.get_file_extension(editorWidget.file_path)
    key = settings.EXTENSIONS.get(lang, 'python')
    same_line = (lstart == lend)
    comment_line_wildcard = settings.SYNTAX[key].get('comment', [])
    comment_multi_wildcard = settings.SYNTAX[key].get('multiline_comment', {})
    comment_wildcard = comment_multi_wildcard
    if (same_line and comment_line_wildcard):
        comment_wildcard = comment_line_wildcard
    elif comment_line_wildcard:
        comment_wildcard = comment_line_wildcard

    is_multi = comment_wildcard == comment_multi_wildcard
    if is_multi:
        wildopen = comment_wildcard["open"]
        wildclose = comment_wildcard["close"]
    else:
        wildopen = comment_wildcard[0]

    if same_line:
        lstart, _ = editorWidget.getCursorPosition()
        lines = 1
    else:
        lines = (lend - lstart) + 1

    editorWidget.SendScintilla(editorWidget.SCI_BEGINUNDOACTION, 1)
    for l in range(lines):
        index = len(get_indentation(editorWidget.text(lstart + l)))
        editorWidget.setSelection(lstart + l, index, lstart + l,
                                  index + len(wildopen))
        if editorWidget.selectedText() == wildopen:
            editorWidget.removeSelectedText()
        if is_multi:
            length = editorWidget.lineLength(lstart + l)
            editorWidget.setSelection(lstart + l, length,
                                      lstart + l, index - len(wildclose))
            if editorWidget.selectedText() == wildopen:
                editorWidget.removeSelectedText()
    editorWidget.SendScintilla(editorWidget.SCI_ENDUNDOACTION, 1)


def comment(editorWidget):
    """ This method comment one or more lines of code """
    lstart, istart, lend, iend = editorWidget.getSelection()
    lang = file_manager.get_file_extension(editorWidget.file_path)
    key = settings.EXTENSIONS.get(lang, 'python')
    same_line = (lstart == lend)
    comment_line_wildcard = settings.SYNTAX[key].get('comment', [])
    comment_multi_wildcard = settings.SYNTAX[key].get('multiline_comment', {})
    comment_wildcard = comment_multi_wildcard

    if (same_line and comment_line_wildcard):
        comment_wildcard = comment_line_wildcard
    elif comment_line_wildcard:
        comment_wildcard = comment_line_wildcard

    is_multi = comment_wildcard == comment_multi_wildcard
    if is_multi:
        wildopen = comment_wildcard["open"]
        wildclose = comment_wildcard["close"]
    else:
        wildopen = comment_wildcard[0]

    if same_line:
        lstart, _ = editorWidget.getCursorPosition()
        lines = 1
    else:
        lines = (lend - lstart) + 1

    editorWidget.SendScintilla(editorWidget.SCI_BEGINUNDOACTION, 1)
    for l in range(lines):
        index = len(get_indentation(editorWidget.text(lstart + l)))
        editorWidget.insertAt(wildopen, lstart + l, index)
        if is_multi:
            length = editorWidget.lineLength(lstart + l)
            editorWidget.insertAt(wildclose, lstart + l, length)
    editorWidget.SendScintilla(editorWidget.SCI_ENDUNDOACTION, 1)


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
