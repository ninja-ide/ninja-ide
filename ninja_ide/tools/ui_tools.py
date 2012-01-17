# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os
import math

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QAction
from PyQt4.QtGui import QCompleter
from PyQt4.QtGui import QKeyEvent
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QSizePolicy
from PyQt4.QtGui import QListWidget
from PyQt4.QtGui import QLinearGradient
from PyQt4.QtGui import QTableWidgetItem
from PyQt4.QtGui import QAbstractItemView
from PyQt4.QtGui import QPrinter
from PyQt4.QtGui import QPrintDialog
from PyQt4.QtGui import QPalette
from PyQt4.QtGui import QPainter
from PyQt4.QtGui import QBrush
from PyQt4.QtGui import QPixmap
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QPen
from PyQt4.QtGui import QColor
from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QTreeWidget
from PyQt4.QtGui import QTreeWidgetItem
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QPushButton
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QObject
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QThread
from PyQt4.QtCore import QEvent
from PyQt4.QtCore import QTimeLine

from ninja_ide import resources
from ninja_ide.core import file_manager


def load_table(table, headers, data, checkFirstColumn=True):
    table.setHorizontalHeaderLabels(headers)
    table.horizontalHeader().setStretchLastSection(True)
    table.setSelectionBehavior(QAbstractItemView.SelectRows)
    for i in xrange(table.rowCount()):
        table.removeRow(0)
    for r, row in enumerate(data):
        table.insertRow(r)
        for index, colItem in enumerate(row):
            item = QTableWidgetItem(colItem)
            table.setItem(r, index, item)
            if index == 0 and checkFirstColumn:
                item.setCheckState(Qt.Unchecked)
            else:
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)


def remove_get_selected_items(table, data):
    rows = table.rowCount()
    pos = rows - 1
    selected = []
    for i in xrange(rows):
        if table.item(pos - i, 0) is not None and \
        table.item(pos - i, 0).checkState() == Qt.Checked:
            selected.append(data.pop(pos - i))
            table.removeRow(pos - i)
    return selected


###############################################################################
# Thread with Callback
###############################################################################


class ThreadCallback(QThread):

    def __init__(self, functionInit=None):
        QThread.__init__(self)
        self.execute = functionInit

    def run(self):
        if self.execute:
            self.execute()


###############################################################################
# LOADING ANIMATION OVER THE WIDGET
###############################################################################


class Overlay(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        palette = QPalette(self.palette())
        palette.setColor(palette.Background, Qt.transparent)
        self.setPalette(palette)

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(event.rect(), QBrush(QColor(255, 255, 255, 127)))
        painter.setPen(QPen(Qt.NoPen))

        for i in xrange(6):
            x_pos = self.width() / 2 + 30 * \
                math.cos(2 * math.pi * i / 6.0) - 10
            y_pos = self.height() / 2 + 30 * \
                math.sin(2 * math.pi * i / 6.0) - 10
            if (self.counter / 5) % 6 == i:
                linear_gradient = QLinearGradient(
                    x_pos + 10, x_pos, y_pos + 10, y_pos)
                linear_gradient.setColorAt(0, QColor(135, 206, 250))
                linear_gradient.setColorAt(1, QColor(0, 0, 128))
                painter.setBrush(QBrush(linear_gradient))
            else:
                linear_gradient = QLinearGradient(
                    x_pos - 10, x_pos, y_pos + 10, y_pos)
                linear_gradient.setColorAt(0, QColor(105, 105, 105))
                linear_gradient.setColorAt(1, QColor(0, 0, 0))
                painter.setBrush(QBrush(linear_gradient))
            painter.drawEllipse(
                x_pos,
                y_pos,
                20, 20)

        painter.end()

    def showEvent(self, event):
        self.timer = self.startTimer(50)
        self.counter = 0

    def timerEvent(self, event):
        self.counter += 1
        self.update()


###############################################################################
# PRINT FILE
###############################################################################


def print_file(fileName, printFunction):
    """This method print a file

    This method print a file, fileName is the default fileName,
    and printFunction is a funcion that takes a QPrinter
    object and print the file,
    the print method
    More info on:http://doc.qt.nokia.com/latest/printing.html"""
    #TODO: Make that the option it's taken from settings. maybe
    #this should be a class to manage all cases?

    printer = QPrinter(QPrinter.HighResolution)
    printer.setPageSize(QPrinter.A4)
    printer.setOutputFileName(fileName)
    printer.setDocName(fileName)
#PRINT PREVIEW OPTIONS
#TODO: the follow imp. dipatch an error on execution time we need to review
#if the error belongs to qt
#    preview = QPrintPreviewDialog(printer)
#    preview.paintRequested[QPrinter].connect(printFunction)
#    preview.exec_()
    dialog = QPrintDialog(printer)
    if dialog.exec_():
        printFunction(printer)

###############################################################################
# FADING ANIMATION
###############################################################################


class FaderWidget(QWidget):

    def __init__(self, old_widget, new_widget):
        QWidget.__init__(self, new_widget)

        self.old_pixmap = QPixmap(new_widget.size())
        old_widget.render(self.old_pixmap)
        self.pixmap_opacity = 1.0

        self.timeline = QTimeLine()
        self.timeline.valueChanged.connect(self.animate)
        self.timeline.finished.connect(self.close)
        self.timeline.setDuration(500)
        self.timeline.start()

        self.resize(new_widget.size())
        self.show()

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setOpacity(self.pixmap_opacity)
        painter.drawPixmap(0, 0, self.old_pixmap)
        painter.end()

    def animate(self, value):
        self.pixmap_opacity = 1.0 - value
        self.repaint()


###############################################################################
# ADD TO PROJECT
###############################################################################


class AddToProject(QDialog):

    def __init__(self, pathProjects, parent=None):
        #pathProjects must be a list
        QDialog.__init__(self, parent)
        self.setWindowTitle(self.tr("Add File to Project"))
        self.pathSelected = ''
        vbox = QVBoxLayout(self)

        self._tree = QTreeWidget()
        self._tree.header().setHidden(True)
        self._tree.setSelectionMode(QTreeWidget.SingleSelection)
        self._tree.setAnimated(True)
        vbox.addWidget(self._tree)
        hbox = QHBoxLayout()
        btnAdd = QPushButton(self.tr("Add here!"))
        btnCancel = QPushButton(self.tr("Cancel"))
        hbox.addWidget(btnCancel)
        hbox.addWidget(btnAdd)
        vbox.addLayout(hbox)
        #load folders
        self._root = None
        for pathProject in pathProjects:
            folderStructure = file_manager.open_project(pathProject)
            self._load_project(folderStructure, pathProject)

        self.connect(btnCancel, SIGNAL("clicked()"), self.close)
        self.connect(btnAdd, SIGNAL("clicked()"), self._select_path)

    def _select_path(self):
        item = self._tree.currentItem()
        if item:
            self.pathSelected = unicode(item.toolTip(0))
            self.close()

    def _load_project(self, folderStructure, folder):
        if not folder:
            return

        name = file_manager.get_basename(folder)
        item = QTreeWidgetItem(self._tree)
        item.setText(0, name)
        item.setToolTip(0, folder)
        item.setIcon(0, QIcon(resources.IMAGES['tree-folder']))
        if folderStructure[folder][1] is not None:
            folderStructure[folder][1].sort()
        self._load_folder(folderStructure, folder, item)
        item.setExpanded(True)
        self._root = item

    def _load_folder(self, folderStructure, folder, parentItem):
        items = folderStructure[folder]

        if items[1] is not None:
            items[1].sort()
        for _file in items[1]:
            if _file.startswith('.'):
                continue
            subfolder = QTreeWidgetItem(parentItem)
            subfolder.setText(0, _file)
            subfolder.setToolTip(0, os.path.join(folder, _file))
            subfolder.setIcon(0, QIcon(resources.IMAGES['tree-folder']))
            self._load_folder(folderStructure,
                os.path.join(folder, _file), subfolder)


###############################################################################
# PROFILE WIDGET
###############################################################################

class ProfilesLoader(QDialog):

    def __init__(self, load_func, create_func, save_func,
    profiles, parent=None):
        QDialog.__init__(self, parent, Qt.Dialog)
        self.setWindowTitle(self.tr("Profile Manager"))
        self.setMinimumWidth(400)
        self._profiles = profiles
        self.load_function = load_func
        self.create_function = create_func
        self.save_function = save_func
        self.ide = parent
        vbox = QVBoxLayout(self)
        vbox.addWidget(QLabel(self.tr("Save your opened files and projects "
                        "into a profile and change really quick\n"
                        "between projects and files sessions.\n"
                        "This allows you to save your working environment, "
                        "keep working in another\nproject and then go back "
                        "exactly where you left.")))
        self.profileList = QListWidget()
        self.profileList.addItems([key for key in profiles])
        self.profileList.setCurrentRow(0)
        self.contentList = QListWidget()
        self.btnDelete = QPushButton(self.tr("Delete Profile"))
        self.btnDelete.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.btnUpdate = QPushButton(self.tr("Update Profile"))
        self.btnUpdate.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.btnCreate = QPushButton(self.tr("Create New Profile"))
        self.btnCreate.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.btnOpen = QPushButton(self.tr("Open Profile"))
        self.btnOpen.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.btnOpen.setDefault(True)
        hbox = QHBoxLayout()
        hbox.addWidget(self.btnDelete)
        hbox.addWidget(self.btnUpdate)
        hbox.addWidget(self.btnCreate)
        hbox.addWidget(self.btnOpen)

        vbox.addWidget(self.profileList)
        vbox.addWidget(self.contentList)
        vbox.addLayout(hbox)

        self.connect(self.profileList, SIGNAL("itemSelectionChanged()"),
            self.load_profile_content)
        self.connect(self.btnOpen, SIGNAL("clicked()"), self.open_profile)
        self.connect(self.btnUpdate, SIGNAL("clicked()"), self.save_profile)
        self.connect(self.btnCreate, SIGNAL("clicked()"), self.create_profile)
        self.connect(self.btnDelete, SIGNAL("clicked()"), self.delete_profile)

    def load_profile_content(self):
        item = self.profileList.currentItem()
        self.contentList.clear()
        if item is not None:
            key = unicode(item.text())
            files = [self.tr('Files:')] + \
                [file[0] for file in self._profiles[key][0]]
            projects = [self.tr('Projects:')] + self._profiles[key][1]
            content = files + projects
            self.contentList.addItems(content)

    def create_profile(self):
        profileName = self.create_function()
        self.ide.Profile = profileName
        self.close()

    def save_profile(self):
        if self.profileList.currentItem():
            profileName = unicode(self.profileList.currentItem().text())
            self.save_function(profileName)
            self.ide.show_status_message(self.tr("Profile %1 Updated!").arg(
                profileName))
            self.load_profile_content()

    def open_profile(self):
        if self.profileList.currentItem():
            key = unicode(self.profileList.currentItem().text())
            self.load_function(key)
            self.ide.Profile = key
            self.close()

    def delete_profile(self):
        if self.profileList.currentItem():
            key = unicode(self.profileList.currentItem().text())
            self._profiles.pop(key)
            self.profileList.takeItem(self.profileList.currentRow())
            self.contentList.clear()


###############################################################################
# Enhanced UI Widgets
###############################################################################

class LineEditButton(object):

    def __init__(self, lineEdit, operation, icon=None):
        hbox = QHBoxLayout(lineEdit)
        hbox.setMargin(0)
        lineEdit.setLayout(hbox)
        hbox.addStretch()
        btnOperation = QPushButton(lineEdit)
        if icon:
            btnOperation.setIcon(QIcon(icon))
        hbox.addWidget(btnOperation)
        btnOperation.clicked.connect(operation)


class ComboBoxButton(object):

    def __init__(self, combo, operation, icon=None):
        hbox = QHBoxLayout(combo)
        hbox.setDirection(hbox.RightToLeft)
        hbox.setMargin(0)
        combo.setLayout(hbox)
        hbox.addStretch()
        btnOperation = QPushButton(combo)
        btnOperation.setStyleSheet("border: none;")
        if icon:
            btnOperation.setIcon(QIcon(icon))
        hbox.addWidget(btnOperation)
        btnOperation.clicked.connect(operation)


class LineEditCount(QObject):

    def __init__(self, lineEdit):
        QObject.__init__(self)
        hbox = QHBoxLayout(lineEdit)
        hbox.setMargin(0)
        lineEdit.setLayout(hbox)
        hbox.addStretch()
        self.counter = QLabel(lineEdit)
        hbox.addWidget(self.counter)
        lineEdit.setStyleSheet("padding-right: 2px;")
        lineEdit.setTextMargins(0, 0, 60, 0)

    def update_count(self, index, total, hasSearch=False):
        message = self.tr("%1 of %2").arg(index).arg(total)
        self.counter.setText(message)
        self.counter.setStyleSheet("background: none;color: gray;")
        if index == 0 and total == 0 and hasSearch:
            self.counter.setStyleSheet(
                "background: #e73e3e;color: white;border-radius: 5px;")


class LineEditTabCompleter(QLineEdit):

    def __init__(self, completer, type=QCompleter.PopupCompletion):
        QLineEdit.__init__(self)
        self.completer = completer
        self.setTextMargins(0, 0, 5, 0)
        self.completionType = type
        self.completer.setCompletionMode(self.completionType)

    def event(self, event):
        if (event.type() == QEvent.KeyPress) and (event.key() == Qt.Key_Tab):
            if self.completionType == QCompleter.InlineCompletion:
                eventTab = QKeyEvent(QEvent.KeyPress,
                    Qt.Key_End, Qt.NoModifier)
                super(LineEditTabCompleter, self).event(eventTab)
            else:
                completion = self.completer.currentCompletion()
                completion += os.path.sep
                self.selectAll()
                self.insert(completion)
                self.completer.popup().hide()
            return True
        return super(LineEditTabCompleter, self).event(event)

    def contextMenuEvent(self, event):
        popup_menu = self.createStandardContextMenu()

        if self.completionType == QCompleter.InlineCompletion:
            actionCompletion = QAction(
                self.tr("Set completion type to: Popup Completion"), self)
        else:
            actionCompletion = QAction(
                self.tr("Set completion type to: Inline Completion"), self)
        self.connect(actionCompletion, SIGNAL("triggered()"),
            self.change_completion_type)
        popup_menu.insertSeparator(popup_menu.actions()[0])
        popup_menu.insertAction(popup_menu.actions()[0], actionCompletion)

        #show menu
        popup_menu.exec_(event.globalPos())

    def change_completion_type(self):
        if self.completionType == QCompleter.InlineCompletion:
            self.completionType = QCompleter.PopupCompletion
        else:
            self.completionType = QCompleter.InlineCompletion
        self.completer.setCompletionMode(self.completionType)
        self.setFocus()
