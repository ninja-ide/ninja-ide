'''from ninja_ide.gui.editor import editor
from ninja_ide.gui.editor import neditable
from ninja_ide.core.file_handling import nfile


def __create_editor(language=None):
    nfile_ref = nfile.NFile()
    neditable_ref = neditable.NEditable(nfile_ref)
    neditable_ref.set_language(language)
    editor_ref = editor.create_editor(neditable_ref)
    return editor_ref


def test_1():
    editor_ref = __create_editor('python')
    editor_ref.text = 'ninja-ide'
    editor_ref.comment()
    assert editor_ref.text == '# ninja-ide'


def test_2():
    editor_ref = __create_editor('python')
    editor_ref.text = 'ninja-ide\nninja-ide'
    editor_ref.selectAll()
    editor_ref.comment()
    assert editor_ref.text == '# ninja-ide\n# ninja-ide'


def test_3():
    editor_ref = __create_editor('python')
    editor_ref.text = 'def foo():\n    lista = [2, 3]\n    return lista'
    editor_ref.comment()
    # assert editor_ref.text == '# def foo():\n#     lista = [2, 3]\n#     return lista'


def test_4():
    editor_ref = __create_editor('python')
    editor_ref.text = '# lalala\n# kkkkk\n print'
    editor_ref.selectAll()
    editor_ref.comment()
    assert editor_ref.text == '# # lalala\n# # kkkkk\n#  print'


def test_5():
    editor_ref = __create_editor('python')
    editor_ref.text = "class A:\n    def foo(self):\n        pass"

    editor_ref.selectAll()
    editor_ref.comment()
    expected = "# class A:\n#     def foo(self):\n#         pass"

    assert editor_ref.text == expected
'''