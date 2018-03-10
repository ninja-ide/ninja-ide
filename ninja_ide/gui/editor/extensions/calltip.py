from PyQt5.QtWidgets import QToolTip

from PyQt5.QtCore import Qt

from ninja_ide.gui.editor.extensions import base


class CallTips(base.Extension):

    def install(self):
        self._neditor.keyReleased.connect(self._on_key_released)

    def _on_key_released(self, event):
        if event.key() in (Qt.Key_ParenLeft, Qt.Key_Comma):
            self._neditor._intellisense.process("signatures")

        elif event.key() in (
                Qt.Key_ParenRight,
                Qt.Key_Return,
                Qt.Key_Left,
                Qt.Key_Right,
                Qt.Key_Down,
                Qt.Key_Up,
                Qt.Key_Backspace,
                Qt.Key_Escape):
            QToolTip.hideText()
