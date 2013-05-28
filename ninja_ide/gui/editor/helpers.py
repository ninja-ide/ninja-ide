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

from PyQt4.QtGui import QTextCursor
from PyQt4.QtGui import QInputDialog

from ninja_ide.core import settings
from ninja_ide.core import file_manager
from ninja_ide.tools import introspection


patIndent = re.compile('^\s+')
patIsLocalFunction = re.compile('(\s)+self\.(\w)+\(\)')
patClass = re.compile("(\\s)*class.+\\:$")
endCharsForIndent = [':', '{', '(', '[']
closeBraces = {'{': '}', '(': ')', '[': ']'}
#Coding line by language
CODING_LINE = {
    'python': '# -*- coding: utf-8 -*-'
}


def get_leading_spaces(line):
    global patIndent
    space = patIndent.match(line)
    if space is not None:
        return space.group()
    return ''


def get_indentation(line, indent=settings.INDENT, useTabs=settings.USE_TABS):
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


def get_start_end_selection(editorWidget, cursor):
    start = editorWidget.document().findBlock(
        cursor.selectionStart()).firstLineNumber()
    end = editorWidget.document().findBlock(
        cursor.selectionEnd()).firstLineNumber()
    if cursor.blockNumber() == end and cursor.atBlockStart():
        end -= 1
    return start, end


def remove_trailing_spaces(editorWidget):
    cursor = editorWidget.textCursor()
    cursor.beginEditBlock()
    block = editorWidget.document().findBlockByLineNumber(0)
    while block.isValid():
        text = block.text()
        if text.endswith(' '):
            cursor.setPosition(block.position())
            cursor.select(QTextCursor.LineUnderCursor)
            cursor.insertText(text.rstrip())
        block = block.next()
    cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)
    cursor.endEditBlock()


def insert_horizontal_line(editorWidget):
    editorWidget.moveCursor(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
    text = editorWidget.textCursor().selection().toPlainText()
    editorWidget.moveCursor(QTextCursor.EndOfLine, QTextCursor.MoveAnchor)
    lang = file_manager.get_file_extension(editorWidget.ID)
    key = settings.EXTENSIONS.get(lang, 'python')
    comment_wildcard = settings.SYNTAX[key].get('comment', ['#'])[0]
    comment = comment_wildcard * ((79 - len(text)) / len(comment_wildcard))
    editorWidget.textCursor().insertText(comment)


def insert_title_comment(editorWidget):
    result = str(QInputDialog.getText(editorWidget,
        editorWidget.tr("Title Comment"),
        editorWidget.tr("Enter the Title Name:"))[0])
    if result:
        editorWidget.textCursor().beginEditBlock()
        editorWidget.moveCursor(QTextCursor.StartOfLine,
            QTextCursor.MoveAnchor)
        lang = file_manager.get_file_extension(editorWidget.ID)
        key = settings.EXTENSIONS.get(lang, 'python')
        comment_wildcard = settings.SYNTAX[key].get('comment', ['#'])[0]
        comment = comment_wildcard * (79 / len(comment_wildcard))
        editorWidget.textCursor().insertText(comment)
        editorWidget.textCursor().insertBlock()
        editorWidget.textCursor().insertText(comment_wildcard + ' ' + result)
        editorWidget.textCursor().insertBlock()
        editorWidget.textCursor().insertText(comment)
        editorWidget.textCursor().insertBlock()
        editorWidget.textCursor().endEditBlock()


def insert_coding_line(editorWidget):
    lang = file_manager.get_file_extension(editorWidget.ID)
    key = settings.EXTENSIONS.get(lang)
    coding_line = CODING_LINE.get(key)
    if coding_line:
        editorWidget.textCursor().insertText("%s\n" % coding_line)


def replace_tabs_with_spaces(editorWidget):
    text = editorWidget.toPlainText()
    text = text.replace('\t', ' ' * editorWidget.indent)
    editorWidget.setPlainText(text)


def lint_ignore_line(editorWidget):
    cursor = editorWidget.textCursor()
    if not cursor.hasSelection():
        cursor.movePosition(QTextCursor.EndOfLine)
        cursor.insertText("  # lint:ok")


def lint_ignore_selection(editorWidget):
    cursor = editorWidget.textCursor()
    if cursor.hasSelection():
        cursor.beginEditBlock()
        start, end = get_start_end_selection(editorWidget, cursor)
        position = editorWidget.document().findBlockByLineNumber(
            start).position()
        cursor.setPosition(position)
        indentation = get_indentation(cursor.block().text())
        cursor.movePosition(QTextCursor.StartOfLine)
        cursor.insertText("%s#lint:disable\n" % indentation)
        position = editorWidget.document().findBlockByLineNumber(
            end + 2).position()
        cursor.setPosition(position)
        cursor.movePosition(QTextCursor.StartOfLine)
        cursor.insertText("%s#lint:enable\n" % indentation)
        cursor.endEditBlock()


def insert_debugging_prints(editorWidget):
    cursor = editorWidget.textCursor()
    if cursor.hasSelection():
        result = str(QInputDialog.getText(editorWidget,
            editorWidget.tr("Print Text"),
            editorWidget.tr("Insert a Text to use in the Print or "
                            "leave empty to just print numbers:"))[0])
        print_text = ""
        if result:
            print_text = "%s: " % result
        #begin Undo feature
        cursor.beginEditBlock()
        start, end = get_start_end_selection(editorWidget, cursor)
        lines = end - start
        for i in range(lines):
            position = editorWidget.document().findBlockByLineNumber(
                start + (i * 2)).position()
            cursor.setPosition(position)
            indentation = get_indentation(cursor.block().text())
            cursor.movePosition(QTextCursor.EndOfLine)
            cursor.insertText("\n%sprint('%s%i')" % (
                indentation, print_text, i))
        #end Undo feature
        cursor.endEditBlock()


def insert_pdb(editorWidget):
    """Insert a pdb statement into the current line to debug code."""
    cursor = editorWidget.textCursor()
    indentation = get_indentation(cursor.block().text())
    cursor.insertText("\n%simport pdb; pdb.set_trace()" % indentation)


def move_up(editorWidget):
    cursor = editorWidget.textCursor()
    block_actual = cursor.block()
    if block_actual.blockNumber() > 0:
        #line where indent_more should start and end
        start, end = get_start_end_selection(editorWidget, cursor)
        if cursor.hasSelection() and (start != end):
            #get the position of the line
            startPosition = editorWidget.document().findBlockByLineNumber(
                start).position()
            #select the text to move
            cursor.setPosition(startPosition)
            cursor.movePosition(QTextCursor.StartOfLine)
            cursor.movePosition(QTextCursor.Down, QTextCursor.KeepAnchor,
                end - start)
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
            text_to_move = cursor.selectedText()
            #begin Undo feature
            cursor.beginEditBlock()
            #Remove
            cursor.removeSelectedText()
            cursor.deleteChar()
            #Insert text and breakline
            cursor.movePosition(QTextCursor.Up, QTextCursor.MoveAnchor)
            cursor.movePosition(QTextCursor.StartOfLine,
                QTextCursor.MoveAnchor)
            cursor.insertText(text_to_move + '\n')
            #end Undo feature
            cursor.endEditBlock()
            #Restore the user selection
            startPosition = editorWidget.document().findBlockByLineNumber(
                (start - 1)).position()
            cursor.setPosition(startPosition)
            cursor.movePosition(QTextCursor.StartOfLine)
            cursor.movePosition(QTextCursor.Down, QTextCursor.KeepAnchor,
                end - start)
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
            editorWidget.setTextCursor(cursor)
        else:
            block_previous = block_actual.previous()
            tempLine = block_actual.text()
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.MoveAnchor)
            cursor.movePosition(QTextCursor.StartOfLine,
                QTextCursor.KeepAnchor)
            #begin Undo feature
            cursor.beginEditBlock()
            cursor.insertText(block_previous.text())
            cursor.movePosition(QTextCursor.Up, QTextCursor.MoveAnchor)
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.MoveAnchor)
            cursor.movePosition(QTextCursor.StartOfLine,
                QTextCursor.KeepAnchor)
            cursor.insertText(tempLine)
            #end Undo feature
            cursor.endEditBlock()
            editorWidget.moveCursor(QTextCursor.Up, QTextCursor.MoveAnchor)


def move_down(editorWidget):
    cursor = editorWidget.textCursor()
    block_actual = cursor.block()
    if block_actual.blockNumber() < (editorWidget.blockCount() - 1):
        start, end = get_start_end_selection(editorWidget, cursor)
        if cursor.hasSelection() and (start != end):
            #get the position of the line
            startPosition = editorWidget.document().findBlockByLineNumber(
                start).position()
            #select the text to move
            cursor.setPosition(startPosition)
            cursor.movePosition(QTextCursor.StartOfLine)
            cursor.movePosition(QTextCursor.Down, QTextCursor.KeepAnchor,
                end - start)
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
            text_to_move = cursor.selectedText()
            #begin Undo feature
            cursor.beginEditBlock()
            #Remove
            cursor.removeSelectedText()
            cursor.deleteChar()
            #Insert text and breakline
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.MoveAnchor)
            cursor.insertText('\n' + text_to_move)
            #end Undo feature
            cursor.endEditBlock()
            #Restore the user selection
            startPosition = editorWidget.document().findBlockByLineNumber(
                (start + 1)).position()
            cursor.setPosition(startPosition)
            cursor.movePosition(QTextCursor.StartOfLine)
            cursor.movePosition(QTextCursor.Down, QTextCursor.KeepAnchor,
                end - start)
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
            editorWidget.setTextCursor(cursor)
        else:
            block_next = block_actual.next()
            tempLine = block_actual.text()
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.MoveAnchor)
            cursor.movePosition(QTextCursor.StartOfLine,
                QTextCursor.KeepAnchor)
            #begin Undo feature
            cursor.beginEditBlock()
            cursor.insertText(block_next.text())
            cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor)
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.MoveAnchor)
            cursor.movePosition(QTextCursor.StartOfLine,
                QTextCursor.KeepAnchor)
            cursor.insertText(tempLine)
            #end Undo feature
            cursor.endEditBlock()
            editorWidget.moveCursor(QTextCursor.Down, QTextCursor.MoveAnchor)


def remove_line(editorWidget):
    cursor = editorWidget.textCursor()
    cursor.beginEditBlock()

    if cursor.hasSelection():
        start, end = get_start_end_selection(editorWidget, cursor)

        if start == end:  # same block selection
            cursor.movePosition(QTextCursor.StartOfLine)
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
            cursor.deleteChar()
        else:  # multiple blocks selection
            selection_start = cursor.selectionStart()
            selection_end = cursor.selectionEnd()

            cursor.setPosition(selection_end)
            if cursor.atBlockStart():
                end = end - 1

            cursor.setPosition(selection_start)
            cursor.movePosition(QTextCursor.StartOfLine)
            cursor.movePosition(QTextCursor.Down, QTextCursor.KeepAnchor,
                end - start)
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)

            cursor.removeSelectedText()
            cursor.deleteChar()
    else:
        cursor.select(QTextCursor.LineUnderCursor)
        cursor.removeSelectedText()
        cursor.deleteChar()
    cursor.endEditBlock()


def duplicate(editorWidget):
    cursor = editorWidget.textCursor()
    cursor.beginEditBlock()
    if cursor.hasSelection():
        start, end = get_start_end_selection(editorWidget, cursor)
        #get the position of the line
        startPosition = editorWidget.document().findBlockByLineNumber(
            start).position()
        #select the text to move
        cursor.setPosition(startPosition)
        cursor.movePosition(QTextCursor.StartOfLine)
        cursor.movePosition(QTextCursor.Down, QTextCursor.KeepAnchor,
            end - start)
        cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
        text_to_move = cursor.selectedText()
        #Insert text and breakline
        cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.MoveAnchor)
        cursor.insertText('\n' + text_to_move)
    else:
        block = cursor.block()
        cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.MoveAnchor)
        cursor.insertBlock()
        cursor.insertText(block.text())
    cursor.endEditBlock()


def uncomment(editorWidget):
    #cursor is a COPY all changes do not affect the QPlainTextEdit's cursor!!!
    cursor = editorWidget.textCursor()
    block_start = editorWidget.document().findBlock(
        cursor.selectionStart())
    block_end = editorWidget.document().findBlock(
        cursor.selectionEnd()).next()
    lang = file_manager.get_file_extension(editorWidget.ID)
    key = settings.EXTENSIONS.get(lang, 'python')
    same_line = (block_start == block_end.previous())
    funcs = {'comment': uncomment_single_line,
        'multiline_comment': uncomment_multiple_lines}
    comment_line_wildcard = settings.SYNTAX[key].get('comment', [])
    comment_multi_wildcard = settings.SYNTAX[key].get('multiline_comment', {})
    option = 'multiline_comment'
    comment_wildcard = comment_multi_wildcard
    if ((same_line and comment_line_wildcard) or
        not (same_line or comment_multi_wildcard)):
        option = 'comment'
        comment_wildcard = comment_line_wildcard
    f = funcs[option]
    f(cursor, block_start, block_end, comment_wildcard)


def uncomment_single_line(cursor, block_start, block_end, comment_wildcard):
    """Uncoment one or more lines when one line symbol is supported"""
    comment_wildcard = comment_wildcard[0]
    # Start block undo
    cursor.beginEditBlock()
    while (block_start != block_end):
        # Find the position of the comment in the line
        comment_position = block_start.text().find(
            comment_wildcard[0])
        if block_start.text().startswith(
           " " * comment_position + comment_wildcard[0]) or (
           settings.USE_TABS and block_start.text().startswith(
           "\t" * comment_position + comment_wildcard[0])):
            cursor.setPosition(block_start.position() + comment_position)
            cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor,
                len(comment_wildcard))
            cursor.removeSelectedText()
        block_start = block_start.next()
    cursor.endEditBlock()


def uncomment_multiple_lines(cursor, block_start, block_end, comment_wildcard):
    """Uncomment one or more lines when multiple lines symbols is supported"""
    #begin Undo feature
    cursor.beginEditBlock()
    #Remove start symbol comment if correspond
    if block_start.previous().text().startswith(comment_wildcard['open']):
        block_start = block_start.previous()
        delete_lines_selected(cursor, block_start)
    if block_start.text().startswith(comment_wildcard['open']):
        delete_lines_selected(cursor, block_start)
    #Remove end symbol comment if correspond
    if block_end.previous().text().startswith(comment_wildcard['close']):
        block_end = block_end.previous()
        delete_lines_selected(cursor, block_end)
    if block_end.text().startswith(comment_wildcard['close']):
        delete_lines_selected(cursor, block_end)
    cursor.endEditBlock()


def delete_lines_selected(cursor, block_actual):
    cursor.setPosition(block_actual.position())
    cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
    cursor.removeSelectedText()
    cursor.deleteChar()


def comment(editorWidget):
    """ This method comment one or more lines of code """
    #cursor is a COPY all changes do not affect the QPlainTextEdit's cursor!!!
    cursor = editorWidget.textCursor()
    block_start = editorWidget.document().findBlock(
        cursor.selectionStart())
    block_end = editorWidget.document().findBlock(
        cursor.selectionEnd()).next()
    lang = file_manager.get_file_extension(editorWidget.ID)
    key = settings.EXTENSIONS.get(lang, 'python')
    same_line = (block_start == block_end.previous())
    funcs = {'comment': comment_single_line,
        'multiline_comment': comment_multiple_lines}
    comment_line_wildcard = settings.SYNTAX[key].get('comment', [])
    comment_multi_wildcard = settings.SYNTAX[key].get('multiline_comment', {})
    option = 'multiline_comment'
    comment_wildcard = comment_multi_wildcard
    if ((same_line and comment_line_wildcard) or
        not (same_line or comment_multi_wildcard)):
        option = 'comment'
        comment_wildcard = comment_line_wildcard
    f = funcs[option]
    f(cursor, block_start, block_end, comment_wildcard)


def comment_single_line(cursor, block_start, block_end, comment_wildcard):
    """Comment one or more lines with single comment symbol"""
    #Start a undo block
    cursor.beginEditBlock()
    #Move the COPY cursor
    while block_start != block_end:
        cursor.setPosition(block_start.position())
        block_number = block_start.blockNumber()
        cursor.select(QTextCursor.WordUnderCursor)
        word = cursor.selectedText()
        cursor.movePosition(QTextCursor.StartOfBlock)
        if not word:
            cursor.movePosition(QTextCursor.WordRight)
        if block_number == cursor.blockNumber():
            cursor.insertText(comment_wildcard[0])
        block_start = block_start.next()
    #End a undo block
    cursor.endEditBlock()


def comment_multiple_lines(cursor, block_start, block_end, comment_wildcard):
    """Comment one or more lines with multiple comment symbol"""
    #select the text to comment
    cursor.setPosition(block_start.position())
    cursor.movePosition(QTextCursor.StartOfLine)
    cursor.movePosition(QTextCursor.Down, QTextCursor.KeepAnchor,
        block_end.previous().firstLineNumber() - block_start.firstLineNumber())
    cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
    text_to_comment = cursor.selectedText()
    #begin Undo feature
    cursor.beginEditBlock()
    #Remove
    cursor.removeSelectedText()
    cursor.insertText(comment_wildcard['open'])
    cursor.insertText('\n' + text_to_comment)
    cursor.insertText('\n' + comment_wildcard['close'])
    #End a undo block
    cursor.endEditBlock()


def check_for_assistance_completion(editorWidget, line):
    #This will be possible when code completion is working
    global patClass
    if patClass.match(line) and editorWidget.lang == 'python':
        source = editorWidget.toPlainText()
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
        editorWidget.textCursor().insertText('\n')
        indent = get_indentation(
            line, editorWidget.indent, editorWidget.useTabs)
        editorWidget.textCursor().insertText(indent + 'def __init__(self):\n')
        if editorWidget.useTabs:
            indent += '\t'
        else:
            indent += ' ' * editorWidget.indent
        if line.find('(') != -1:
            classes = line.split('(')
            parents = []
            if len(classes) > 1:
                parents += classes[1].split(',')
            if len(parents) > 0 and 'object):' not in parents:
                editorWidget.textCursor().insertText(
                    indent + "super({0}, self).__init__()\n".format(clazzName))
                editorWidget.textCursor().insertText(indent)
            else:
                editorWidget.textCursor().insertText(indent)
        else:
            editorWidget.textCursor().insertText(indent)
