import pytest

from PyQt5.QtGui import QTextCursor

from ninja_ide.gui.editor.base import CodeEditor


@pytest.fixture
def code_editor():
    editor = CodeEditor()
    editor.text = "NINJA-IDE is not just another IDE"
    return editor


def test_find_match(code_editor):
    assert code_editor.find_match('IDE') is True
    _, col = code_editor.cursor_position
    assert col == 9


def test_find_match_cs(code_editor):
    assert code_editor.find_match('JUST', True) is False


def test_find_match_wo(code_editor):
    assert code_editor.find_match('ju', whole_word=True) is False


def test_replace_match(code_editor):
    code_editor.find_match('just')
    code_editor.replace_match(
        word_old='just',
        word_new='JUST'
    )
    assert code_editor.text == 'NINJA-IDE is not JUST another IDE'


def test_replace_all(code_editor):
    code_editor.replace_all(
        word_old='IDE',
        word_new='Integrated Development Environment'
    )
    assert code_editor.text == (
        'NINJA-Integrated Development Environment is not just another '
        'Integrated Development Environment')
