from ninja_ide.gui.editor import editor
from ninja_ide.gui.editor import neditable
from ninja_ide.core.file_handling import nfile


def create_editor(language=None):
    nfile_ref = nfile.NFile()
    neditable_ref = neditable.NEditable(nfile_ref)
    neditable_ref.set_language(language)
    editor_ref = editor.create_editor(neditable_ref)
    return editor_ref
