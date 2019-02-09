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

import pytest

from PyQt5.QtGui import QTextCursor

from ninja_ide.gui.editor import base


@pytest.fixture
def editor_fixture():
    editor = base.BaseTextEditor()
    return editor


@pytest.fixture
def editor_with_text(editor_fixture):
    editor_fixture.setPlainText("this\nis\an\nexample")
    editor_fixture.moveCursor(QTextCursor.Start)
    return editor_fixture


def test_selected_text(editor_with_text):
    cursor = editor_with_text.textCursor()
    cursor.movePosition(cursor.Right, cursor.KeepAnchor, 4)
    editor_with_text.setTextCursor(cursor)
    assert editor_with_text.has_selection()
    assert editor_with_text.selected_text() == 'this'


def test_selection_range(editor_with_text):
    cursor = editor_with_text.textCursor()
    cursor.movePosition(QTextCursor.Down, QTextCursor.KeepAnchor, 2)
    editor_with_text.setTextCursor(cursor)
    assert editor_with_text.selection_range() == (0, 1)
    cursor.movePosition(QTextCursor.Right, QTextCursor. KeepAnchor)
    editor_with_text.setTextCursor(cursor)
    assert editor_with_text.selection_range() == (0, 2)


@pytest.mark.parametrize(
    'text, lineno, expected',
    [
        ('ninja\nIDE\n\nis awesome!', 2, ''),
        ('ninja\nIDE\n\nis awesome!', 0, 'ninja'),
        ('ninja\nIDE\n\nis awesome!', 3, 'is awesome!'),
        ('ninja\nIDE\n\nis awesome!', -1, 'ninja')
    ]
)
def test_line_text(editor_fixture, text, lineno, expected):
    editor_fixture.text = text
    editor_fixture.cursor_position = lineno, 0
    assert editor_fixture.line_text(lineno) == expected

@pytest.mark.parametrize(
    'text, expected',
    [
        ('asd ldsaj lkaskdj hakjshdkjh asd', 1),
        ('as\n\n\nd ld\nsaj l\nkaskdj hakjshdkjh asd', 6),
        ('asd ldsaj lkaskdj ha\nkj\nshdkjh asd', 3)
    ]
)
def test_line_count(editor_fixture, text, expected):
    editor_fixture.text = text
    assert editor_fixture.line_count() == expected


def test_insert_text(editor_fixture):
    assert editor_fixture.text == ''
    editor_fixture.insert_text("inserting text")
    assert editor_fixture.text == 'inserting text'
    editor_fixture.setReadOnly(True)
    editor_fixture.insert_text("INSERTING TEXt")
    assert editor_fixture.text == 'inserting text'


@pytest.mark.parametrize(
    'text, position, expected',
    [
        ('hola como estas', (0, 0), 'hola'),
        ('hola\n como \nestas', (2, 3), 'estas'),
        ('hola\n aaa ssss wwww como estas', (1, 17), 'como')
    ]
)
def test_get_right_word(editor_fixture, text, position, expected):
    editor_fixture.text = text
    editor_fixture.cursor_position = position
    assert editor_fixture.cursor_position == position


@pytest.mark.parametrize(
    'text, position, expected',
    [
        ('hola como estas', (0, 0), 'h'),
        ('hola\n como \nestas', (2, 3), 'a'),
        ('hola\n aaa ssss wwww como estas', (1, 17), 'm')
    ]
)
def test_get_right_character(editor_fixture, text, position, expected):
    editor_fixture.text = text
    editor_fixture.cursor_position = position
    assert editor_fixture.get_right_character() == expected


@pytest.mark.parametrize(
    'text, lineno, up, expected',
    [
        ('ninja\nIDE\n\nis awesome!!!\n!', 0, False,
         'IDE\nninja\n\nis awesome!!!\n!'),
        ('ninja\nIDE\n\nis awesome!!!\n!', 3, True,
         'ninja\nIDE\nis awesome!!!\n\n!')
    ]
)
def test_move_up_down(editor_fixture, text, lineno, up, expected):
    editor_fixture.text = text
    editor_fixture.cursor_position = lineno, 0
    editor_fixture.move_up_down(up)
    assert editor_fixture.text == expected


@pytest.mark.parametrize(
    'text, range_, up, expected',
    [
        ('ninja is not just\nanother\nide\nprint', (0, 1), False,
         'ide\nninja is not just\nanother\nprint'),
        ('ninja is not just\nanother\nide\nprint', (2, 1), True,
         'another\nide\nninja is not just\nprint')
    ]
)
def test_move_up_down_selection(editor_fixture, text, range_, up, expected):
    editor_fixture.text = text
    start, end = range_
    editor_fixture.cursor_position = start, 0
    cursor = editor_fixture.textCursor()
    if up:
        cursor.movePosition(QTextCursor.EndOfLine)
        cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
        cursor.movePosition(QTextCursor.Up, QTextCursor.KeepAnchor, abs(end - start))
    else:
        cursor.movePosition(QTextCursor.Down, QTextCursor.KeepAnchor, end - start)
        cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
    editor_fixture.setTextCursor(cursor)
    editor_fixture.move_up_down(up)
    assert editor_fixture.text == expected



@pytest.mark.parametrize(
    'text, lineno, n, expected',
    [
        ('example\ntext', 0, 1, 'example\nexample\ntext'),
        ('example\ntext', 1, 1, 'example\ntext\ntext'),
        ('example\ntext', 1, 3, 'example\ntext\ntext\ntext\ntext')
    ]
)
def test_duplicate_line(editor_fixture, text, lineno, n, expected):
    editor_fixture.text = text
    editor_fixture.cursor_position = lineno, 0
    for i in range(n):
        editor_fixture.duplicate_line()
    assert editor_fixture.text == expected


@pytest.mark.parametrize(
    'text, _range, n, expected',
    [
        ('exa\nmple\ntext\n!!', (0, 1), 1, 'exa\nmple\nexa\nmple\ntext\n!!'),
        ('exa\nmple\ntext\n!!', (0, 1), 4, 'exa\nmple\nexa\nmple\nexa\nmple\nexa\nmple\nexa\nmple\ntext\n!!'),  # noqa
    ]
)
def test_duplicate_line_selection(editor_fixture, text, _range, n, expected):
    editor_fixture.text = text
    cursor = editor_fixture.textCursor()
    start, end = _range
    editor_fixture.cursor_position = start, 0
    cursor.movePosition(QTextCursor.Down, QTextCursor.KeepAnchor, end - start)
    cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
    editor_fixture.setTextCursor(cursor)
    for i in range(n):
        editor_fixture.duplicate_line()
    assert editor_fixture.text == expected


@pytest.mark.parametrize(
    'text, position, expected',
    [
        ('hola\ncomo\nestas\n  ', (0, 4), 'hola'),
        ('hola\ncomo\nestas\n  ', (2, 1), 'estas'),
        ('hola\ncomo\nestas\n  ', (0, 1), 'hola'),
        ('hola\ncomo\nestas\n  ', (1, 3), 'como'),
        ('hola\ncomo\nestas\n  ', (3, 2), '')
    ]
)
def test_word_under_cursor(editor_fixture, text, position, expected):
    editor_fixture.text = text
    editor_fixture.cursor_position = position
    cursor = editor_fixture.word_under_cursor()
    assert not cursor.isNull()
    assert cursor.selectedText() == expected
