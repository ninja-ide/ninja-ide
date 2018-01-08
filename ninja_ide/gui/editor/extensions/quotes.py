from PyQt5.QtGui import QTextCursor
from PyQt5.QtCore import Qt
from ninja_ide.gui.editor.extensions import base


class AutocompleteQuotes(base.Extension):

    QUOTES = {
        Qt.Key_QuoteDbl: '"',
        Qt.Key_Apostrophe: "'"
    }

    def install(self):
        self._neditor.keyPressed.connect(self._on_key_pressed)

    def shutdown(self):
        self._neditor.keyPressed.disconnect(self._on_key_pressed)

    def _on_key_pressed(self, event):
        if event.isAccepted():
            return
        key = event.key()
        if key in self.QUOTES.keys():
            self._autocomplete_quotes(key)
            event.accept()

    def get_left_chars(self, nchars=1):
        cursor = self.text_cursor()
        chars = None
        for i in range(nchars):
            if not cursor.atBlockStart():
                cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor)
                chars = cursor.selectedText()
        return chars

    def _autocomplete_quotes(self, key):
        char = self.QUOTES[key]
        cursor = self._neditor.textCursor()
        two = self.get_left_chars(2)
        three = self.get_left_chars(3)
        if self._neditor.has_selection():
            text = self._neditor.selected_text()
            cursor.insertText("{0}{1}{0}".format(char, text))
            # Keep selection
            cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor)
            cursor.movePosition(
                QTextCursor.Left, QTextCursor.KeepAnchor, len(text))
        elif self._neditor.get_right_character() == char:
            cursor.movePosition(
                QTextCursor.NextCharacter, QTextCursor.KeepAnchor)
            cursor.clearSelection()
        elif three == char * 3:
            cursor.insertText(char * 3)
            cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, 3)
        elif two == char * 2:
            cursor.insertText(char)
        else:
            cursor.insertText(char * 2)
            cursor.movePosition(QTextCursor.PreviousCharacter)
        self._neditor.setTextCursor(cursor)
