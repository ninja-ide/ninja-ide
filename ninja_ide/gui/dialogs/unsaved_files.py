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

from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QListWidget
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtWidgets import QDialogButtonBox
from PyQt5.QtWidgets import QLabel

from PyQt5.QtCore import Qt

from ninja_ide import translations
from ninja_ide.tools.logger import NinjaLogger

logger = NinjaLogger(__name__)


class UnsavedFilesDialog(QDialog):

    def __init__(self, unsaved_files, parent=None):
        super().__init__(parent)
        self._ninja = parent
        self.setWindowTitle(translations.TR_IDE_CONFIRM_EXIT_TITLE)
        vbox = QVBoxLayout(self)

        self._unsave_files_list = QListWidget()
        self._unsave_files_list.setSelectionMode(QListWidget.ExtendedSelection)
        vbox.addWidget(QLabel(translations.TR_IDE_CONFIRM_EXIT_BODY))
        vbox.addWidget(self._unsave_files_list)
        button_box = QDialogButtonBox(self)

        standard_icon = self.style().standardIcon

        btn = button_box.addButton(
            translations.TR_CANCEL, QDialogButtonBox.RejectRole)
        btn.setIcon(standard_icon(self.style().SP_DialogCloseButton))
        self._btn_save_selected = button_box.addButton(
            translations.TR_SAVE_SELECTED, QDialogButtonBox.AcceptRole)
        self._btn_save_selected.setIcon(
            standard_icon(self.style().SP_DialogSaveButton))
        btn_save_all = button_box.addButton(
            translations.TR_SAVE_ALL, QDialogButtonBox.AcceptRole)
        btn_save_all.setIcon(standard_icon(self.style().SP_DialogApplyButton))
        btn_donot_save = button_box.addButton(
            translations.TR_DONOT_SAVE, QDialogButtonBox.DestructiveRole)
        btn_donot_save.setIcon(standard_icon(self.style().SP_DialogNoButton))

        vbox.addWidget(button_box)

        for nfile in unsaved_files:
            item = QListWidgetItem(nfile.display_name)
            item.setData(Qt.UserRole, nfile)
            item.setToolTip(nfile.file_path)
            self._unsave_files_list.addItem(item)

        # Connections
        button_box.rejected.connect(self.reject)
        button_box.accepted.connect(self._save_selected)
        btn_donot_save.clicked.connect(self._discard)
        btn_save_all.clicked.connect(self._save_all)
        self._unsave_files_list.itemSelectionChanged.connect(
            self._on_selection_changed)

        self._unsave_files_list.selectAll()

    def _on_selection_changed(self):
        value = True
        if not self._unsave_files_list.selectedItems():
            value = False
        self._btn_save_selected.setEnabled(value)

    def _save_selected(self):
        logger.debug("Saving selected unsaved files")
        self.__save()

    def __save(self):
        """Collect all selected items and save"""

        items_to_save = []
        for item in self._unsave_files_list.selectedItems():
            nfile = item.data(Qt.UserRole)
            items_to_save.append(nfile)
        self._ninja._save_unsaved_files(items_to_save)
        self.accept()

    def _save_all(self):
        """Select all items in the list and save"""
        logger.debug("Saving all unsaved files")
        for index in range(self._unsave_files_list.count()):
            item = self._unsave_files_list.item(index)
            item.setSelected(True)
        self.__save()

    def _discard(self):
        logger.debug("Discarding all unsaved files")
        self.accept()
