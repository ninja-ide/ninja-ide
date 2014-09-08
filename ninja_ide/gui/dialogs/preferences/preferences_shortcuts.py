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

from ninja_ide import resources
from ninja_ide.gui import actions
from ninja_ide import translations
from ninja_ide.gui.ide import IDE
from ninja_ide.gui.dialogs.preferences import preferences


class TreeResult(QTreeWidget):
    """Tree Results widget Class"""

    def __init__(self):
        QTreeWidget.__init__(self)
        self.setHeaderLabels((translations.TR_PROJECT_DESCRIPTION,
                              translations.TR_SHORTCUT))
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
        super(ShortcutDialog, self).__init__()
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
        ok_button = QPushButton(translations.TR_ACCEPT)
        cancel_button = QPushButton(translations.TR_CANCEL)
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
        """Save a new Shortcut"""
        self.hide()
        shortcut = QKeySequence(self.line_edit.text())
        self.emit(SIGNAL('shortcutChanged'), shortcut)

    def set_shortcut(self, txt):
        """Setup a shortcut"""
        self.line_edit.setText(txt)

    def eventFilter(self, watched, event):
        """Event Filter handling"""
        if event.type() == QEvent.KeyPress:
            self.keyPressEvent(event)
            return True

        return False

    def keyPressEvent(self, evt):
        """Key Press handling"""
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

    def __init__(self, parent):
        super(ShortcutConfiguration, self).__init__()
        self._preferences = parent
        self.shortcuts_text = {
            "Show-Selector": translations.TR_SHOW_SELECTOR,
            "cut": translations.TR_CUT,
            "Indent-more": translations.TR_INDENT_MORE,
            "expand-file-combo": translations.TR_EXPAND_FILE_COMBO,
            "expand-symbol-combo": translations.TR_EXPAND_SYMBOL_COMBO,
            "undo": translations.TR_UNDO,
            "Close-Split": translations.TR_CLOSE_SPLIT,
            "Split-assistance": translations.TR_SHOW_SPLIT_ASSISTANCE,
            "copy": translations.TR_COPY,
            "paste": translations.TR_PASTE,
            "Duplicate": translations.TR_DUPLICATE_SELECTION,
            "Remove-line": translations.TR_REMOVE_LINE_SELECTION,
            "Move-up": translations.TR_MOVE_LINE_SELECTION_UP,
            "Move-down": translations.TR_MOVE_LINE_SELECTION_DOWN,
            "Close-file": translations.TR_CLOSE_CURRENT_TAB,
            "New-file": translations.TR_NEW_TAB,
            "New-project": translations.TR_NEW_PROJECT,
            "Open-file": translations.TR_OPEN_A_FILE,
            "Open-project": translations.TR_OPEN_PROJECT,
            "Save-file": translations.TR_SAVE_FILE,
            "Save-project": translations.TR_SAVE_OPENED_FILES,
            "Print-file": translations.TR_PRINT_FILE,
            "Redo": translations.TR_REDO,
            "Comment": translations.TR_COMMENT_SELECTION,
            "Uncomment": translations.TR_UNCOMMENT_SELECTION,
            "Horizontal-line": translations.TR_INSERT_HORIZONTAL_LINE,
            "Title-comment": translations.TR_INSERT_TITLE_COMMENT,
            "Indent-less": translations.TR_INDENT_LESS,
            "Hide-misc": translations.TR_HIDE_MISC,
            "Hide-editor": translations.TR_HIDE_EDITOR,
            "Hide-explorer": translations.TR_HIDE_EXPLORER,
            "Toggle-tabs-spaces": translations.TR_TOGGLE_TABS,
            "Run-file": translations.TR_RUN_FILE,
            "Run-project": translations.TR_RUN_PROJECT,
            "Debug": translations.TR_DEBUG,
            "Switch-Focus": translations.TR_SWITCH_FOCUS,
            "Stop-execution": translations.TR_STOP_EXECUTION,
            "Hide-all": translations.TR_HIDE_ALL,
            "Full-screen": translations.TR_FULLSCREEN,
            "Find": translations.TR_FIND,
            "Find-replace": translations.TR_FIND_REPLACE,
            "Find-with-word": translations.TR_FIND_WORD_UNDER_CURSOR,
            "Find-next": translations.TR_FIND_NEXT,
            "Find-previous": translations.TR_FIND_PREVIOUS,
            "Help": translations.TR_SHOW_PYTHON_HELP,
            "Split-vertical": translations.TR_SPLIT_TABS_VERTICAL,
            "Split-horizontal": translations.TR_SPLIT_TABS_HORIZONTAL,
            "Follow-mode": translations.TR_ACTIVATE_FOLLOW_MODE,
            "Reload-file": translations.TR_RELOAD_FILE,
            "Jump": translations.TR_JUMP_TO_LINE,
            "Find-in-files": translations.TR_FIND_IN_FILES,
            "Import": translations.TR_IMPORT_FROM_EVERYWHERE,
            "Go-to-definition": translations.TR_GO_TO_DEFINITION,
            "Complete-Declarations": translations.TR_COMPLETE_DECLARATIONS,
            "Code-locator": translations.TR_SHOW_CODE_LOCATOR,
            "File-Opener": translations.TR_SHOW_FILE_OPENER,
            "Navigate-back": translations.TR_NAVIGATE_BACK,
            "Navigate-forward": translations.TR_NAVIGATE_FORWARD,
            "Open-recent-closed": translations.TR_OPEN_RECENT_CLOSED_FILE,
            "Change-Tab": translations.TR_CHANGE_TO_NEXT_TAB,
            "Change-Tab-Reverse": translations.TR_CHANGE_TO_PREVIOUS_TAB,
            "Move-Tab-to-right": translations.TR_MOVE_TAB_TO_RIGHT,
            "Move-Tab-to-left": translations.TR_MOVE_TAB_TO_LEFT,
            "Show-Code-Nav": translations.TR_ACTIVATE_HISTORY_NAVIGATION,
            "Show-Bookmarks-Nav": translations.TR_ACTIVATE_BOOKMARKS_NAVIGATION,
            "Show-Breakpoints-Nav":
                translations.TR_ACTIVATE_BREAKPOINTS_NAVIGATION,
            "Show-Paste-History": translations.TR_SHOW_COPYPASTE_HISTORY,
            "History-Copy": translations.TR_COPY_TO_HISTORY,
            "History-Paste": translations.TR_PASTE_FROM_HISTORY,
            #"change-split-focus":
                #translations.TR_CHANGE_KEYBOARD_FOCUS_BETWEEN_SPLITS,
            "Add-Bookmark-or-Breakpoint": translations.TR_INSERT_BREAKPOINT,
            "move-tab-to-next-split": translations.TR_MOVE_TAB_TO_NEXT_SPLIT,
            "change-tab-visibility": translations.TR_SHOW_TABS_IN_EDITOR,
            "Highlight-Word": translations.TR_HIGHLIGHT_OCCURRENCES
        }

        self.shortcut_dialog = ShortcutDialog(self)
        #main layout
        main_vbox = QVBoxLayout(self)
        #layout for buttons
        buttons_layout = QVBoxLayout()
        #widgets
        self.result_widget = TreeResult()
        load_defaults_button = QPushButton(translations.TR_LOAD_DEFAULTS)
        #add widgets
        main_vbox.addWidget(self.result_widget)
        buttons_layout.addWidget(load_defaults_button)
        main_vbox.addLayout(buttons_layout)
        main_vbox.addWidget(QLabel(
            translations.TR_SHORTCUTS_ARE_GOING_TO_BE_REFRESH))
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

        self.connect(self._preferences, SIGNAL("savePreferences()"), self.save)

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
                              translations.TR_SHORTCUT_ALREADY_ON_USE,
                              translations.TR_DO_YOU_WANT_TO_REMOVE,
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
        settings = IDE.ninja_settings()
        settings.beginGroup("shortcuts")
        for index in range(self.result_widget.topLevelItemCount()):
            item = self.result_widget.topLevelItem(index)
            shortcut_keys = item.text(1)
            shortcut_name = item.text(2)
            settings.setValue(shortcut_name, shortcut_keys)
        settings.endGroup()

    def _load_shortcuts(self):
        """Method to load all custom shortcuts"""
        for action in resources.CUSTOM_SHORTCUTS:
            shortcut_action = resources.get_shortcut(action)
            #populate the tree widget
            tree_data = [self.shortcuts_text[action],
                shortcut_action.toString(QKeySequence.NativeText), action]
            item = QTreeWidgetItem(self.result_widget, tree_data)
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

    def _load_defaults_shortcuts(self):
        """Method to load the default builtin shortcuts"""
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


preferences.Preferences.register_configuration('GENERAL', ShortcutConfiguration,
    translations.TR_PREFERENCES_SHORTCUTS, weight=2, subsection='SHORTCUTS')