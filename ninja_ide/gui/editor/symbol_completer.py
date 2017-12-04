from PyQt5.QtGui import QTextCursor
from PyQt5.QtCore import Qt


class SymbolCompleter(object):
    """Automatically complete quotes and parentheses"""

    OPEN_SYMBOLS = '{[('
    CLOSE_SYMBOLS = '}])'
    SYMBOLS = {key: value for (key, value) in zip(OPEN_SYMBOLS, CLOSE_SYMBOLS)}
    QUOTES = {
        '"': '"',
        "'": "'"
    }

    def __init__(self, neditor):
        self._neditor = neditor
        self._neditor.keyPressed.connect(self._on_key_pressed)
        self._neditor.post_key_press.connect(self._on_post_key_press)

    def _on_post_key_press(self, event):
        symbol = event.text()
        cursor = self._neditor.textCursor()
        if symbol and symbol in self.OPEN_SYMBOLS:
            complementary = self.SYMBOLS[symbol]
            cursor.insertText(complementary)
            cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor)
            self._neditor.setTextCursor(cursor)
            event.accept()

    def _on_key_pressed(self, event):
        char = event.text()
        cursor = self._neditor.textCursor()
        if cursor.hasSelection():
            if char in self.QUOTES.keys():
                complementary = self.QUOTES[char]
                cursor.insertText(
                    '%s%s%s' % (char, cursor.selectedText(), complementary)
                )
                # self._neditor.setTextCursor(cursor)
                event.accept()
                # return
        right_char = self._neditor.get_right_character()
        if event.key() == Qt.Key_Backspace:
            cursor = self._neditor.textCursor()
            cursor.movePosition(QTextCursor.Left)
            cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor)
            remove_char = cursor.selectedText()
            if remove_char in self.OPEN_SYMBOLS:
                close_symbol = self.SYMBOLS.get(remove_char, None)
                if close_symbol is not None and close_symbol == right_char:
                    with self._neditor:
                        cursor.movePosition(
                            QTextCursor.Right, QTextCursor.KeepAnchor)
                        cursor.insertText('')
                    event.accept()

        if char in self.CLOSE_SYMBOLS:
            if right_char == char:
                cursor = self._neditor.textCursor()
                cursor.clearSelection()
                cursor.movePosition(
                    QTextCursor.Right, QTextCursor.MoveAnchor)
                self._neditor.setTextCursor(cursor)
                event.accept()
