from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor
from ninja_ide.gui.editor.extensions import base


class AutocompleteBraces(base.Extension):
    """Automatically complete braces"""

    OPENED_BRACES = "[{("
    CLOSED_BRACES = "]})"
    ALL_BRACES = {
        "(": ")",
        "[": "]",
        "{": "}"
    }

    def install(self):
        self._neditor.postKeyPressed.connect(self._on_post_key_pressed)
        self._neditor.keyPressed.connect(self._on_key_pressed)

    def shutdown(self):
        self._neditor.postKeyPressed.disconnect(self._on_post_key_pressed)
        self._neditor.keyPressed.disconnect(self._on_key_pressed)

    def _on_key_pressed(self, event):
        right = self._neditor.get_right_character()
        current_text = event.text()
        if current_text in self.CLOSED_BRACES and right == current_text:
            # Move cursor to right if same symbol is typing
            cursor = self.text_cursor()
            cursor.movePosition(QTextCursor.NextCharacter,
                                QTextCursor.MoveAnchor)
            self._neditor.setTextCursor(cursor)
            event.accept()
        elif event.key() == Qt.Key_Backspace:
            # Remove automatically closed symbol if opened symbol is removed
            cursor = self.text_cursor()
            cursor.movePosition(QTextCursor.Left)
            cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor)
            to_remove = cursor.selectedText()
            if to_remove in self.ALL_BRACES.keys():  # Opened braces
                complementary = self.ALL_BRACES.get(to_remove)
                if complementary is not None and complementary == right:
                    cursor.movePosition(
                        QTextCursor.Right, QTextCursor.KeepAnchor)
                    cursor.insertText('')
                    event.accept()

    def _on_post_key_pressed(self, event):
        # Insert complementary symbol
        char = event.text()
        if not char:
            return
        right = self._neditor.get_right_character()
        cursor = self.text_cursor()
        if char in self.OPENED_BRACES:
            to_insert = self.ALL_BRACES[char]
            if not right or right in self.CLOSED_BRACES or right.isspace():
                cursor.insertText(to_insert)
                cursor.movePosition(QTextCursor.PreviousCharacter)
                self._neditor.setTextCursor(cursor)
