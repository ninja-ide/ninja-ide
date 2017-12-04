from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor
from ninja_ide.gui.editor.extensions import Extension


class AutocompleteBraces(Extension):
    """Automatically complete braces"""

    def install(self):
        self._neditor.postKeyPressed.connect(self._on_post_key_pressed)
        self._neditor.keyPressed.connect(self._on_key_pressed)

    def _on_key_pressed(self, event):
        """Remove automatically right brace"""
        right = self._neditor.get_right_character()
        if event.key() == Qt.Key_Backspace:
            cursor = self.text_cursor()
            cursor.movePosition(QTextCursor.Left)
            cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor)
            to_remove = cursor.selectedText()
            if to_remove in '([{':
                complementary = {'{': '}', '[': ']', '(': ')'}.get(to_remove)
                if complementary is not None and complementary == right:
                    cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor)
                    cursor.insertText('')
                    event.accept()

    def _on_post_key_pressed(self, event):
        key = event.key()
        cursor = self.text_cursor()
        operations = {
            Qt.Key_ParenLeft: ')',
            Qt.Key_BraceLeft: '}',
            Qt.Key_BracketLeft: ']'
        }
        if key in operations.keys():
            cursor.insertText(operations[key])
            cursor.movePosition(QTextCursor.PreviousCharacter)
        elif key in (Qt.Key_ParenRight, Qt.Key_BraceRight, Qt.Key_BracketRight):
            cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
        self._neditor.setTextCursor(cursor)
