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

import time

from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSlot

from ninja_ide.gui.editor import proposal_widget
from ninja_ide.gui.ide import IDE


class IntelliSenseAssistant(QObject):
    """
    Proxy to communicate the editor with the intellisense.

    This object processes the editor request, communicates with the
    intellisense through signals/slots and processes the results
    by applying them to the editor.
    """
    def __init__(self, editor):
        super().__init__(editor)
        self._editor = editor
        self._view = None

        self._operations = {
            "completions": self._handle_completions,
            "definitions": self._handle_definitions
        }
        self._intellisense = IDE.get_service("intellisense")

    def _handle_completions(self, completions):
        _completions = []
        append = _completions.append
        t0 = time.time()
        for completion in completions:
            item = proposal_widget.ProposalItem(completion["text"])
            item.type = completion["type"]
            item.detail = completion["detail"]
            append(item)
        self._create_view(_completions)
        print("VIEW: %.1f" % (time.time() - t0))

    def _handle_definitions(self, definitions):
        main = IDE.get_service("main_container")
        result = definitions[0]
        main.open_file(
            result["filename"], result["line"] - 1, result["column"])

    @pyqtSlot("PyQt_PyObject", "QString")
    def _on_finished(self, result, kind):
        self._operations[kind](result)
        # Disconnect
        self._intellisense.resultAvailable.disconnect(self._on_finished)

    def _get_code_info(self):
        cursor = self._editor.textCursor()
        cursor.setPosition(cursor.position() - 1)
        word = self.__word_before_cursor(cursor)
        if not word:
            return
        line, col = self._editor.cursor_position
        request_data = {
            "source": self._editor.text,
            "line": line + 1,
            "column": col,
            "path": self._editor.file_path,
        }
        return request_data

    def _process_completions(self):
        request_data = self._get_code_info()
        if self._view is not None:
            self._view.abort()
        self._intellisense.get(
            "completions", request_data, self._editor)

    def _process_definitions(self):
        request_data = self._get_code_info()
        self._intellisense.get("definitions", request_data, self._editor)

    def process(self, kind):
        self._intellisense.resultAvailable.connect(self._on_finished)
        handle = getattr(self, "_process_" + kind)
        handle()

    def _create_view(self, completions):
        self._view = proposal_widget.ProposalWidget(self._editor)
        self._view.destroyed.connect(self.finalize)
        self._view.proposalItemActivated.connect(self.process_proposal_item)

        model = proposal_widget.ProposalModel(self._view)
        model.set_items(completions)
        self._view.set_model(model)
        self._view.show_proposal()

    def process_proposal_item(self, item):
        """Handle proposal item from completions/snippets"""
        prefix = self.__word_before_cursor()
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
            # If completion inserted is a function, we will add the parentheses
            self._editor.textCursor().insertText("()")

    def finalize(self):
        del self._view
        self._view = None

    def __word_before_cursor(self, cursor=None):
        return self._editor.word_under_cursor(cursor).selectedText()
