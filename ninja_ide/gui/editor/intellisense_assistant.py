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

from PyQt5.QtCore import QObject
from PyQt5.QtCore import Qt

from ninja_ide import translations
from ninja_ide.gui.editor import proposal_widget
from ninja_ide.gui.ide import IDE
from ninja_ide.tools.logger import NinjaLogger

logger = NinjaLogger(__name__)


class IntelliSenseAssistant(QObject):

    def __init__(self, editor):
        QObject.__init__(self)
        self._editor = editor
        # Proposal widget
        self._proposal_widget = None
        self.__kind = "completions"

        self.__handlers = {
            "completions": self._handle_completions,
            "calltips": self._handle_calltips,
            "definitions": self._handle_definitions
        }

        self._intellisense = IDE.get_service("intellisense")
        self._provider = self._intellisense.provider(
            editor.neditable.language())

        # Connections
        self._editor.postKeyPressed.connect(self._on_post_key_pressed)
        self._editor.keyReleased.connect(self._on_key_released)
        self._editor.destroyed.connect(self.deleteLater)

    def _on_key_released(self, event):
        key = event.key()
        if key in (Qt.Key_ParenLeft, Qt.Key_Comma):
            self.invoke("calltips")
        elif key in (
                Qt.Key_ParenRight,
                Qt.Key_Return,
                Qt.Key_Left,
                Qt.Key_Right,
                Qt.Key_Down,
                Qt.Key_Up,
                Qt.Key_Backspace,
                Qt.Key_Escape):
            self._editor.hide_tooltip()

    def _on_post_key_pressed(self, key_event):
        if key_event.key() == Qt.Key_Escape:
            self._editor.hide_tooltip()

        key = key_event.text()
        if not key:
            return

        # TODO: shortcut
        if key in self._provider.triggers and not \
                self._editor.inside_string_or_comment():
            self.invoke("completions")

    def invoke(self, kind):
        self.__kind = kind
        self._intellisense.resultAvailable.connect(self._on_result_available)
        if kind == "completions":
            if self._proposal_widget is not None:
                self._proposal_widget.abort()
        self._intellisense.process(kind, self._editor)

    def _on_result_available(self, result):
        self._intellisense.resultAvailable.disconnect(
            self._on_result_available)
        try:
            handler = self.__handlers[self.__kind]
            handler(result)
        except KeyError as reason:
            logger.error(reason)

    def _handle_calltips(self, signatures: list):
        if not signatures:
            return
        calltip = "<p style='white-space:pre'>{0}(".format(
            signatures.get("signature.name"))
        params = signatures.get("signature.params")
        for i, param in enumerate(params):
            if i == signatures.get("signature.index"):
                calltip += "<b><u>"
            calltip += param
            if i == signatures.get("signature.index"):
                calltip += "</u></b>"
            if i < len(params) - 1:
                calltip += ", "
        calltip += ")"
        font = self._editor.default_font
        crect = self._editor.cursorRect()
        crect.setX(crect.x() + self._editor.viewport().x())
        position = self._editor.mapToGlobal(crect.topLeft())
        position.setY(position.y() + font.pointSize() + 1)
        self._editor.show_tooltip(calltip, position)

    def _handle_completions(self, completions: list):
        if not completions:
            return
        _completions = []
        append = _completions.append
        for completion in completions:
            item = proposal_widget.ProposalItem(completion["text"])
            completion_type = completion["type"]
            item.type = completion_type
            item.detail = completion["detail"]
            item.set_icon(completion_type)
            append(item)
        self._create_view(_completions)

    def _handle_definitions(self, defs):
        if defs:
            defs = defs[0]
            if defs["line"] is not None:
                line = defs["line"] - 1
                column = defs["column"]
                fname = defs["filename"]
                if fname == self._editor.file_path:
                    self._editor.go_to_line(line, column)
                else:
                    main_container = IDE.get_service("main_container")
                    main_container.open_file(fname, line, column)
                return

        ide = IDE.get_service("ide")
        ide.show_message(translations.TR_DEFINITION_NOT_FOUND)

    def _create_view(self, completions):
        """Create proposal widget to show completions"""

        self._proposal_widget = proposal_widget.ProposalWidget(self._editor)
        self._proposal_widget.destroyed.connect(self.finalize)
        self._proposal_widget.proposalItemActivated.connect(
            self._process_proposal_item)
        model = proposal_widget.ProposalModel(self._proposal_widget)
        model.set_items(completions)
        self._proposal_widget.set_model(model)
        self._proposal_widget.show_proposal()

    def finalize(self):
        del self._proposal_widget
        self._proposal_widget = None

    def _process_proposal_item(self, item):
        prefix = self._editor.word_under_cursor().selectedText()
        to_insert = item.text[len(prefix):]
        prefix_inserted = item.text[:len(prefix)]
        if prefix_inserted != prefix:
            # If the item to be inserted is different from what
            # we are writing, then we fix that
            # e.g. str.CAPIT  --> str.capitalize instead of str.CAPITalize
            cursor = self._editor.textCursor()
            cursor.movePosition(
                cursor.Left, cursor.KeepAnchor, len(prefix_inserted))
            cursor.removeSelectedText()
            self._editor.textCursor().insertText(prefix_inserted)
        self._editor.textCursor().insertText(to_insert)

        if item.type == "function":
            self._editor.textCursor().insertText("()")
