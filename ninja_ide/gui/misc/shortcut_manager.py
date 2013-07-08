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

from __future__ import absolute_import

from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QTreeWidget
from PyQt4.QtGui import QTreeWidgetItem
from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QKeySequence
from PyQt4.QtGui import QMessageBox

from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QEvent
from PyQt4.QtCore import QSettings

from ninja_ide import resources
from ninja_ide.gui import actions


class TreeResult(QTreeWidget):

    def __init__(self):
        QTreeWidget.__init__(self)
        self.setHeaderLabels((self.tr('Description'), self.tr('Shortcut')))
        #columns width
        self.setColumnWidth(0, 175)
        self.header().setStretchLastSection(True)
        self.setSortingEnabled(True)
        self.sortByColumn(0, Qt.AscendingOrder)


class ShortcutDialog(QDialog):
    """
    Dialog to set a shortcut for an action
    this class emit the follow signals:
        shortcutChanged(QKeySequence)
    """

    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.keys = 0
        #Keyword modifiers!
        self.keyword_modifiers = (Qt.Key_Control, Qt.Key_Meta, Qt.Key_Shift,
            Qt.Key_Alt, Qt.Key_Menu)
        #main layout
        main_vbox = QVBoxLayout(self)
        self.line_edit = QLineEdit()
        self.line_edit.setReadOnly(True)
        #layout for buttons
        buttons_layout = QHBoxLayout()
        ok_button = QPushButton(self.tr("Accept"))
        cancel_button = QPushButton(self.tr("Cancel"))
        #add widgets
        main_vbox.addWidget(self.line_edit)
        buttons_layout.addWidget(ok_button)
        buttons_layout.addWidget(cancel_button)
        main_vbox.addLayout(buttons_layout)
        self.line_edit.installEventFilter(self)
        #buttons signals
        self.connect(ok_button, SIGNAL("clicked()"), self.save_shortcut)
        self.connect(cancel_button, SIGNAL("clicked()"), self.close)

    def save_shortcut(self):
        self.hide()
        shortcut = QKeySequence(self.line_edit.text())
        self.emit(SIGNAL('shortcutChanged'), shortcut)

    def set_shortcut(self, txt):
        self.line_edit.setText(txt)

    def eventFilter(self, watched, event):
        if event.type() == QEvent.KeyPress:
            self.keyPressEvent(event)
            return True

        return False

    def keyPressEvent(self, evt):
        #modifier can not be used as shortcut
        if evt.key() in self.keyword_modifiers:
            return

        #save the key
        if evt.key() == Qt.Key_Backtab and evt.modifiers() & Qt.ShiftModifier:
            self.keys = Qt.Key_Tab
        else:
            self.keys = evt.key()

        if evt.modifiers() & Qt.ShiftModifier:
            self.keys += Qt.SHIFT
        if evt.modifiers() & Qt.ControlModifier:
            self.keys += Qt.CTRL
        if evt.modifiers() & Qt.AltModifier:
            self.keys += Qt.ALT
        if evt.modifiers() & Qt.MetaModifier:
            self.keys += Qt.META
        #set the keys
        self.set_shortcut(QKeySequence(self.keys).toString())


class ShortcutConfiguration(QWidget):
    """
    Dialog to manage ALL shortcuts
    """

    def __init__(self):
        QWidget.__init__(self)

        self.shortcuts_text = {
            "Duplicate": self.tr("Duplicate the line/selection"),
            "Remove-line": self.tr("Remove the line/selection"),
            "Move-up": self.tr("Move the line/selection up"),
            "Move-down": self.tr("Move the line/selection down"),
            "Close-tab": self.tr("Close the current tab"),
            "New-file": self.tr("Create a New tab"),
            "New-project": self.tr("Create a new Project"),
            "Open-file": self.tr("Open a File"),
            "Open-project": self.tr("Open a Project"),
            "Save-file": self.tr("Save the current file"),
            "Save-project": self.tr("Save the current project opened files"),
            "Print-file": self.tr("Print current file"),
            "Redo": self.tr("Redo"),
            "Comment": self.tr("Comment line/selection"),
            "Uncomment": self.tr("Uncomment line/selection"),
            "Horizontal-line": self.tr("Insert Horizontal line"),
            "Title-comment": self.tr("Insert comment Title"),
            "Indent-less": self.tr("Indent less"),
            "Hide-misc": self.tr("Hide Misc Container"),
            "Hide-editor": self.tr("Hide Editor Area"),
            "Hide-explorer": self.tr("Hide Explorer"),
            "Run-file": self.tr("Execute current file"),
            "Run-project": self.tr("Execute current project"),
            "Debug": self.tr("Debug"),
            "Switch-Focus": self.tr("Switch keyboard focus"),
            "Stop-execution": self.tr("Stop Execution"),
            "Hide-all": self.tr("Hide all (Except Editor)"),
            "Full-screen": self.tr("Full Screen"),
            "Find": self.tr("Find"),
            "Find-replace": self.tr("Find & Replace"),
            "Find-with-word": self.tr("Find word under cursor"),
            "Find-next": self.tr("Find Next"),
            "Find-previous": self.tr("Find Previous"),
            "Help": self.tr("Show Python Help"),
            "Split-vertical": self.tr("Split Tabs Vertically"),
            "Split-horizontal": self.tr("Split Tabs Horizontally"),
            "Follow-mode": self.tr("Activate/Deactivate Follow Mode"),
            "Reload-file": self.tr("Reload File"),
            "Jump": self.tr("Jump to line"),
            "Find-in-files": self.tr("Find in Files"),
            "Import": self.tr("Import from everywhere"),
            "Go-to-definition": self.tr("Go to definition"),
            "Complete-Declarations": self.tr("Complete Declarations"),
            "Code-locator": self.tr("Show Code Locator"),
            "File-Opener": self.tr("Show File Opener"),
            "Navigate-back": self.tr("Navigate Back"),
            "Navigate-forward": self.tr("Navigate Forward"),
            "Open-recent-closed": self.tr("Open recent closed file"),
            "Change-Tab": self.tr("Change to the next Tab"),
            "Change-Tab-Reverse": self.tr("Change to the previous Tab"),
            "Move-Tab-to-right": self.tr("Move tab to right"),
            "Move-Tab-to-left": self.tr("Move tab to left"),
            "Show-Code-Nav": self.tr("Activate History Navigation"),
            "Show-Bookmarks-Nav": self.tr("Activate Bookmarks Navigation"),
            "Show-Breakpoints-Nav": self.tr("Activate Breakpoints Navigation"),
            "Show-Paste-History": self.tr("Show copy/paste history"),
            "History-Copy": self.tr("Copy into copy/paste history"),
            "History-Paste": self.tr("Paste from copy/paste history"),
            "change-split-focus": self.tr(
                "Change the keyboard focus between the current splits"),
            "Add-Bookmark-or-Breakpoint": self.tr(
                "Insert Bookmark/Breakpoint"),
            "move-tab-to-next-split": self.tr(
                "Move the current Tab to the next split."),
            "change-tab-visibility": self.tr(
                "Show/Hide the Tabs in the Editor Area."),
            "Highlight-Word": self.tr(
                "Highlight occurrences for word under cursor")
        }

        self.shortcut_dialog = ShortcutDialog(self)
        #main layout
        main_vbox = QVBoxLayout(self)
        #layout for buttons
        buttons_layout = QVBoxLayout()
        #widgets
        self.result_widget = TreeResult()
        load_defaults_button = QPushButton(self.tr("Load defaults"))
        #add widgets
        main_vbox.addWidget(self.result_widget)
        buttons_layout.addWidget(load_defaults_button)
        main_vbox.addLayout(buttons_layout)
        main_vbox.addWidget(QLabel(
            self.tr("The Shortcut's Text in the Menus are "
            "going to be refreshed on restart.")))
        #load data!
        self.result_widget.setColumnWidth(0, 400)
        self._load_shortcuts()
        #signals
        #open the set shortcut dialog
        self.connect(self.result_widget,
            SIGNAL("itemDoubleClicked(QTreeWidgetItem*, int)"),
                self._open_shortcut_dialog)
        #load defaults shortcuts
        self.connect(load_defaults_button, SIGNAL("clicked()"),
            self._load_defaults_shortcuts)
        #one shortcut has changed
        self.connect(self.shortcut_dialog, SIGNAL('shortcutChanged'),
                     self._shortcut_changed)

    def _shortcut_changed(self, keysequence):
        """
        Validate and set a new shortcut
        """
        if self.__validate_shortcut(keysequence):
            self.result_widget.currentItem().setText(1, keysequence.toString())

    def __validate_shortcut(self, keysequence):
        """
        Validate a shortcut
        """
        if keysequence.isEmpty():
            return True

        keyname = self.result_widget.currentItem().text(0)
        keystr = keysequence

        for top_index in range(self.result_widget.topLevelItemCount()):
            top_item = self.result_widget.topLevelItem(top_index)

            if top_item.text(0) != keyname:
                itmseq = top_item.text(1)
                if keystr == itmseq:
                    val = QMessageBox.warning(self,
                            self.tr('Shortcut is already in use'),
                            self.tr("Do you want to remove it?"),
                            QMessageBox.Yes, QMessageBox.No)
                    if val == QMessageBox.Yes:
                        top_item.setText(1, "")
                        return True
                    else:
                        return False
                if not itmseq:
                    continue

        return True

    def _open_shortcut_dialog(self, item, column):
        """
        Open the dialog to set a shortcut
        """
        if item.childCount():
            return

        self.shortcut_dialog.set_shortcut(
            QKeySequence(item.text(1)).toString())
        self.shortcut_dialog.exec_()

    def save(self):
        """
        Save all shortcuts to settings
        """
        settings = QSettings(resources.SETTINGS_PATH, QSettings.IniFormat)
        settings.beginGroup("shortcuts")
        for index in range(self.result_widget.topLevelItemCount()):
            item = self.result_widget.topLevelItem(index)
            shortcut_keys = item.text(1)
            shortcut_name = item.text(2)
            settings.setValue(shortcut_name, shortcut_keys)
        settings.endGroup()
        actions.Actions().update_shortcuts()

    def _load_shortcuts(self):
        for action in resources.CUSTOM_SHORTCUTS:
            shortcut_action = resources.get_shortcut(action)
            #populate the tree widget
            tree_data = [self.shortcuts_text[action],
                shortcut_action.toString(QKeySequence.NativeText), action]
            item = QTreeWidgetItem(self.result_widget, tree_data)
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

    def _load_defaults_shortcuts(self):
        #clean custom shortcuts and UI widget
        resources.clean_custom_shortcuts()
        self.result_widget.clear()
        for name, action in list(resources.SHORTCUTS.items()):
            shortcut_action = action
            #populate the tree widget
            tree_data = [self.shortcuts_text[name],
                shortcut_action.toString(QKeySequence.NativeText), name]
            item = QTreeWidgetItem(self.result_widget, tree_data)
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
