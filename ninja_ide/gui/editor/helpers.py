# -*- coding: utf-8 -*-
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
patInit = re.compile("(\\s)*def __init__\(self,.+\\:$")
endCharsForIndent = [':', '{', '(', '[', ',']


def get_leading_spaces(line):
    global patIndent
    space = patIndent.match(line)
    if space is not None:
        return space.group()
    return ''


def get_indentation(line):
    global patIndent
    global endCharsForIndent
    indentation = ''
    if len(line) > 0 and line[-1] in endCharsForIndent:
        indentation = ' ' * settings.INDENT
    space = patIndent.match(line)
    if space is not None:
        return space.group() + indentation
    return indentation


def remove_trailing_spaces(editorWidget):
    cursor = editorWidget.textCursor()
    cursor.setPosition(0)
    cursor.beginEditBlock()
    pat = re.compile('.*\\s$')
    block = editorWidget.document().findBlockByLineNumber(0)
    while block.isValid():
        if pat.match(block.text()):
            cursor.select(QTextCursor.LineUnderCursor)
            cursor.insertText(unicode(block.text()).rstrip())
        cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor)
        block = block.next()
    cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)
    if not cursor.block().text().isEmpty():
        cursor.insertText('\n')
    cursor.endEditBlock()


def insert_horizontal_line(editorWidget):
    editorWidget.moveCursor(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
    text = unicode(editorWidget.textCursor().selection().toPlainText())
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


def replace_tabs_with_spaces(editorWidget):
    text = editorWidget.toPlainText()
    text = text.replace('\t', ' ' * settings.INDENT)
    editorWidget.setPlainText(text)


def move_up(editorWidget):
    cursor = editorWidget.textCursor()
    block_actual = cursor.block()
    if block_actual.blockNumber() > 0:
        #line where indent_more should start and end
        start = editorWidget.document().findBlock(
            cursor.selectionStart()).firstLineNumber()
        end = editorWidget.document().findBlock(
            cursor.selectionEnd()).firstLineNumber()
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
            tempLine = unicode(block_actual.text())
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
        start = editorWidget.document().findBlock(
            cursor.selectionStart()).firstLineNumber()
        end = editorWidget.document().findBlock(
            cursor.selectionEnd()).firstLineNumber()
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
            tempLine = unicode(block_actual.text())
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
        block_start = editorWidget.document().findBlock(
            cursor.selectionStart()).firstLineNumber()
        block_end = editorWidget.document().findBlock(
            cursor.selectionEnd()).firstLineNumber()

        if block_start == block_end:  # same block selection
            cursor.movePosition(QTextCursor.StartOfLine)
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
            cursor.deleteChar()
        else:  # multiple blocks selection
            selection_start = cursor.selectionStart()
            selection_end = cursor.selectionEnd()

            cursor.setPosition(selection_end)
            if cursor.atBlockStart():
                block_end = block_end - 1

            cursor.setPosition(selection_start)
            cursor.movePosition(QTextCursor.StartOfLine)
            cursor.movePosition(QTextCursor.Down, QTextCursor.KeepAnchor,
                block_end - block_start)
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
        start = editorWidget.document().findBlock(
            cursor.selectionStart()).firstLineNumber()
        end = editorWidget.document().findBlock(
            cursor.selectionEnd()).firstLineNumber()
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


def uncomment(editorWidget, start=-1, end=-1, startPosition=-1):
    lang = file_manager.get_file_extension(editorWidget.ID)
    key = settings.EXTENSIONS.get(lang, 'python')
    comment_wildcard = settings.SYNTAX[key].get('comment', ['#'])[0]

    #cursor is a COPY all changes do not affect the QPlainTextEdit's cursor!!!
    cursor = editorWidget.textCursor()
    if start == -1 and end == -1 and startPosition == -1:
        start = editorWidget.document().findBlock(
            cursor.selectionStart()).firstLineNumber()
        end = editorWidget.document().findBlock(
            cursor.selectionEnd()).firstLineNumber()
        startPosition = editorWidget.document().findBlockByLineNumber(
            start).position()

    #Start a undo block
    cursor.beginEditBlock()

    #Move the COPY cursor
    cursor.setPosition(startPosition)
    #Move the QPlainTextEdit Cursor where the COPY cursor IS!
    editorWidget.setTextCursor(cursor)
    editorWidget.moveCursor(QTextCursor.StartOfLine)
    for i in xrange(start, end + 1):
        editorWidget.moveCursor(QTextCursor.Right, QTextCursor.KeepAnchor)
        text = editorWidget.textCursor().selectedText()
        if text == comment_wildcard:
            editorWidget.textCursor().removeSelectedText()
        elif u'\u2029' in text:
            #\u2029 is the unicode char for \n
            #if there is a newline, rollback the selection made above.
            editorWidget.moveCursor(QTextCursor.Left, QTextCursor.KeepAnchor)

        editorWidget.moveCursor(QTextCursor.Down)
        editorWidget.moveCursor(QTextCursor.StartOfLine)

    #End a undo block
    cursor.endEditBlock()


def comment(editorWidget):
    lang = file_manager.get_file_extension(editorWidget.ID)
    key = settings.EXTENSIONS.get(lang, 'python')
    comment_wildcard = settings.SYNTAX[key].get('comment', ['#'])[0]

    #cursor is a COPY all changes do not affect the QPlainTextEdit's cursor!!!
    cursor = editorWidget.textCursor()
    start = editorWidget.document().findBlock(
        cursor.selectionStart()).firstLineNumber()
    end = editorWidget.document().findBlock(
        cursor.selectionEnd()).firstLineNumber()
    startPosition = editorWidget.document().findBlockByLineNumber(
        start).position()

    #Start a undo block
    cursor.beginEditBlock()

    #Move the COPY cursor
    cursor.setPosition(startPosition)
    #Move the QPlainTextEdit Cursor where the COPY cursor IS!
    editorWidget.setTextCursor(cursor)
    editorWidget.moveCursor(QTextCursor.StartOfLine)
    editorWidget.moveCursor(QTextCursor.Right, QTextCursor.KeepAnchor)
    text = editorWidget.textCursor().selectedText()
    if text == comment_wildcard:
        cursor.endEditBlock()
        uncomment(editorWidget, start, end, startPosition)
        return
    else:
        editorWidget.moveCursor(QTextCursor.StartOfLine)
    for i in xrange(start, end + 1):
        editorWidget.textCursor().insertText(comment_wildcard)
        editorWidget.moveCursor(QTextCursor.Down)
        editorWidget.moveCursor(QTextCursor.StartOfLine)

    #End a undo block
    cursor.endEditBlock()


def check_for_assistance_completion(editorWidget, line):
    #This will be possible when code completion is working
    global patClass
    global patInit
    if patClass.match(line):
        source = unicode(editorWidget.toPlainText())
        source = source.encode(editorWidget.encoding)
        symbols = introspection.obtain_symbols(source)
        clazzName = [name for name in
            re.split("(\\s)*class(\\s)+|:|\(", line) \
            if name is not None and name.strip()][0]
        if 'classes' in symbols and clazzName in symbols['classes']:
            clazz = symbols['classes'][clazzName]
            if '__init__' in clazz[1]['functions']:
                return
        editorWidget.textCursor().insertText('\n')
        spaces = get_leading_spaces(line)
        indent = ' ' * 4
        if spaces:
            indent += ' ' * (len(spaces) - 1)
        editorWidget.textCursor().insertText(indent + 'def __init__(self):\n')
        indent += ' ' * 4
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
    if patInit.match(line):
        pass
