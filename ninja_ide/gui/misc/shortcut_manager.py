# -*- coding: utf-8 -*-

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
from PyQt4.QtCore import QString
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
        self.set_shortcut(QString(QKeySequence(self.keys)))


class ShortcutConfiguration(QWidget):
    """
    Dialog to manage ALL shortcuts
    """
    def __init__(self):
        QWidget.__init__(self)
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
            self.tr("The Shortcut's Text in the Menus are " \
            "going to be refreshed on restart.")))
        #load data!
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
            self.result_widget.currentItem().setText(1, QString(keysequence))

    def __validate_shortcut(self, keysequence):
        """
        Validate a shortcut
        """
        if keysequence.isEmpty():
            return True

        keyname = unicode(self.result_widget.currentItem().text(0))
        keystr = unicode(QString(keysequence))

        for top_index in xrange(self.result_widget.topLevelItemCount()):
            top_item = self.result_widget.topLevelItem(top_index)

            if unicode(top_item.text(0)) != keyname:
                itmseq = unicode(top_item.text(1))
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

        self.shortcut_dialog.set_shortcut(QString(QKeySequence(item.text(1))))
        self.shortcut_dialog.exec_()

    def save(self):
        """
        Save all shortcuts to settings
        """
        settings = QSettings()
        settings.beginGroup("shortcuts")
        for index in xrange(self.result_widget.topLevelItemCount()):
            item = self.result_widget.topLevelItem(index)
            shortcut_name = item.text(0)
            shortcut_keys = item.text(1)
            settings.setValue(shortcut_name, shortcut_keys)
        settings.endGroup()
        actions.Actions().update_shortcuts()

    def _load_shortcuts(self):
        for action in resources.CUSTOM_SHORTCUTS:
            shortcut_action = resources.get_shortcut(action)
            #populate the tree widget
            tree_data = [self.tr(action),
                shortcut_action.toString(QKeySequence.NativeText)]
            item = QTreeWidgetItem(self.result_widget, tree_data)
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

    def _load_defaults_shortcuts(self):
        self.result_widget.clear()
        for name, action in resources.SHORTCUTS.iteritems():
            shortcut_action = action
            #populate the tree widget
            tree_data = [self.tr(name),
                shortcut_action.toString(QKeySequence.NativeText)]
            item = QTreeWidgetItem(self.result_widget, tree_data)
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
