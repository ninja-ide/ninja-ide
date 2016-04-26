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
from __future__ import unicode_literals

import os
import re
import uuid
from collections import namedtuple

from ninja_ide.tools.logger import NinjaLogger
logger = NinjaLogger(__name__)

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QJsonValue
from PyQt5.QtCore import pyqtProperty
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QUrl
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import QObject
from PyQt5.QtQuickWidgets import QQuickWidget
from PyQt5.QtQuick import QQuickView

from ninja_ide.gui.ide import IDE
from ninja_ide.tools import ui_tools
from ninja_ide.tools.locator import locator



class raww(QObject):
    def __init__(self, parent=None):
        super(raww, self).__init__(parent)
    @pyqtSlot()
    def view_WinFlags(self):
        items = QApplication.instance().topLevelWidgets()
        print("view_WinFlags", self.parent().windowFlags(),
            bool(self.parent().windowFlags() & Qt.WindowStaysOnTopHint),\
            bool(self.parent().windowFlags() & Qt.WA_KeyboardFocusChange))
        print("items", items, self.parent(), len(items),\
            QApplication.instance().activePopupWidget(),\
            QApplication.instance().activeModalWidget(),\
                QApplication.instance().activeWindow(),\
                self.parent().isVisibleTo(self.parent().comboParent),\
                self.parent().visibleRegion() )


#WA_AlwaysStackOnTop
#WA_ShowWithoutActivating
class FilesHandler(QFrame):
#Qt.WindowStaysOnTopHint | 
    _changedForJava = pyqtSignal()
    def __init__(self, combofiles, Force_Free=False):#SplashScreen
        super(FilesHandler, self).__init__(None, Qt.SplashScreen)#, Qt.Popup | Qt.FramelessWindowHint
        # self.setAttribute(Qt.WA_TranslucentBackground)
        # self.setStyleSheet("background:transparent;")
        #self.setStyleSheet("background-color: rgb(25, 255, 60);")
        self.setWindowState(Qt.WindowActive)# | Qt.SplashScreen
        self.setAttribute(Qt.WA_AlwaysStackOnTop, False)
        # Create the QML user interface.
        self._main_container = combofiles.container#IDE.get_service('main_container')
        self.comboParent = combofiles
        self.Force_Free = combofiles.undocked or Force_Free
        # self.rawObj = raww(self)

        self.view = QQuickWidget()
        self.view.setResizeMode(QQuickWidget.SizeRootObjectToView)
        self.view.engine().quit.connect(self.hide)
        # self.view.rootContext().setContextProperty("rawObj", self.rawObj)
        self.view.setSource(ui_tools.get_qml_resource("FilesHandler.qml"))
        self._root = self.view.rootObject()
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        vbox.addWidget(self.view)

                # {"name": model[i][0],
                # "path": model[i][1],
                # "checkers": model[i][2],
                # "modified": model[i][3],
                # "tempFile": model[i][4],
                # "project": "",
                # "itemVisible": true});

        self._ntup = ("name", "path", "checkers", "modified", "tempFile", "project", "itemVisible")
        # self._Ndtup = namedtuple("_Ndtup", self._ntup)

        self._filePathPosition = {}
        self._filesModel = []
        self._temp_files = {}
        self._max_index = 0
        print("\n\nFilesHandler", self)


        # QApplication.instance().focusChanged["QWidget*", "QWidget*"].connect(\
        #     lambda w1, w2: print("\n\n:focusChanged:", w1, w1.geometry() if w1\
        #     else "_No es un widget",  w2, w2.geometry() if w2 else "_No es un widget"))

        QApplication.instance().focusChanged["QWidget*", "QWidget*"].connect(\
            lambda w1, w2, this=self: this.hide() if w1 == this.view else None)

        self._root.open.connect(self._open)
        self._root.close.connect(self._close)
        self._root.hide.connect(self.hide)
        self._root.fuzzySearch.connect(self._fuzzy_search)
        #QTimer.singleShot(15000, lambda: print("QTimer::", self.show()))

        # self._root.setVisible(True)

    def _open(self, path, temp, project):
        print("\n\n_open", path, "|", temp, "|", project, "|", self)
        if project:
            path = os.path.join(os.path.split(project)[0], path)
            self._main_container.open_file(path)
        elif temp:
            nfile = self._temp_files[temp]
            ninjaide = IDE.getInstance()
            neditable = ninjaide.get_or_create_editable(nfile=nfile)
            print("nfile", nfile, neditable, self._temp_files, temp)
            self._main_container.current_comboEditor.set_current(neditable)
        else:
            # self._main_container.open_file(path)
            # self._main_container.open_file_from_nEditable(self.comboParent.get_editable_fromPath(path),\
                # self.comboParent.ParentalComboEditor)
            self.comboParent.ParentalComboEditor.set_current(\
                self.comboParent.get_editable_fromPath(path) )

            index = self._filePathPosition[path]
            self._max_index = max(self._max_index, index) + 1
            self._filePathPosition[path] = self._max_index
        self.hide()

    def _close(self, path, temp):
        if temp:
            nfile = self._temp_files.get(temp, None)
        else:
            ninjaide = IDE.getInstance()
            nfile = ninjaide.get_or_create_nfile(path)
        if nfile is not None:
            nfile.close()

    def _fuzzy_search(self, search):
        search = '.+'.join(re.escape(search).split('\\ '))
        pattern = re.compile(search, re.IGNORECASE)

        model = []
        for project_path in locator.files_paths:
            files_in_project = locator.files_paths[project_path]
            base_project = os.path.basename(project_path)
            for file_path in files_in_project:
                file_path = os.path.join(
                    base_project, os.path.relpath(file_path, project_path))
                if pattern.search(file_path):
                    model.append([os.path.basename(file_path), file_path,
                                  project_path])
        self._root.set_fuzzy_model(model)

    def getNewIndex(self):
        self._max_index += 1
        return self._max_index-1

    def currentEditable(self):
        return self.comboParent.get_editable()

    def removeFile(self, nedit):
        self.removeFilePath(nedit.file_path)

    def removeFilePath(self, path):
        # del self._filesModel[self._filePathPosition[path]]
        del self._filePathPosition[path]
        self._changedForJava.emit()

    @pyqtProperty(QJsonValue, notify= _changedForJava)
    def fileModel(self):
        return self._filesModel

    def add_Data(self, dat):
        self._filesModel.append(dict( zip(self._tup, dat) ))
        # sort by Path
        model = sorted(self._filesModel,\
            key=lambda x: self._filePathPosition.get(x[1], False), reverse=True)

        self._filesModel = model
        self._changedForJava.emit()


    def addFile(self, neditable):
        nfile = neditable.nfile
        current_editor = ninjaide.getCurrentEditor()

        current_path = current_editor.file_path if current_editor else ""
        model = []
        if nfile.file_path not in self._filePathPosition and nfile.file_path is not None:
            self._filePathPosition[nfile.file_path] = 0# default position for NEW FILE

        checkers = neditable.sorted_checkers
        checks = []
        for items in checkers:
            checker, color, _ = items
            if checker.dirty:
                # Colors needs to be reversed for QML
                color = "#%s" % color[::-1]
                checks.append(
                    {"checker_text": checker.dirty_text,
                     "checker_color": color})
                
        modified = neditable.editor.is_modified
        temp_file = str(uuid.uuid4()) if nfile.file_path is None else ""
        filepath = nfile.file_path if nfile.file_path is not None else ""

        if temp_file:
            self._temp_files[temp_file] = nfile

        self.add_Data( (nfile.file_name, filepath, checks, modified, temp_file,\
            "", current_path and current_path != nfile.file_path) )



    def _add_model(self):
        # print("_add_model:_add_model")
        ninjaide = IDE.getInstance()
        #files = ninjaide.opened_files# list<neditable>
        # if True:#self.Force_Free:
        #     files = self.comboParent.opened_files
        # else:
        #     files = ninjaide.opened_files

        files = self.comboParent.opened_files
        print("_add_model::", len(files))
        past = set(self._filePathPosition.keys())
        now = set([neditable.file_path for neditable in files])
        old = past - now
        # print("\n_model:past:", past)
        # print("\n_model:now:", now)
        # print("\n_model:old:", old)

        # Update model
        for item in old:
            # print("\n to Delete", item)
            del self._filePathPosition[item]

        current_editor = ninjaide.getCurrentEditor()
        # if current_editor.neditable != self.currentEditable():
        #     QMessageBox.critical(None, "current_editor", "el QSCiEditor que la aplicación dice que es el actual\n"\
        #         "NO coincide con el Editor de éste FilesHandler()")
        
        current_path = current_editor.file_path if current_editor else ""
        model = []
        # print("len(files)", len(files), [nfile.file_path for nfile in files], "\n\n")
        for neditable in files:
            nfile = neditable.nfile

            if nfile.file_path not in self._filePathPosition and nfile.file_path is not None:
                self._filePathPosition[nfile.file_path] = self.getNewIndex()

            # print("\n_add_model->", not self.Force_Free, type(nfile))
            # if not self.Force_Free:
            #     neditable = ninjaide.get_or_create_editable_EXTERNAL(nfile=nfile)

            # print("\n_add_model->->", neditable, self._filePathPosition, neditable.editor)

            checkers = neditable.sorted_checkers
            checks = []
            for items in checkers:
                checker, color, _ = items
                if checker.dirty:
                    # Colors needs to be reversed for QML
                    color = "#%s" % color[::-1]
                    checks.append(
                        {"checker_text": checker.dirty_text,
                         "checker_color": color})

            modified = neditable.editor.is_modified
            temp_file = str(uuid.uuid4()) if nfile.file_path is None else ""
            filepath = nfile.file_path if nfile.file_path is not None else ""
            model.append([nfile.file_name, filepath, checks, modified,
                          temp_file, "", current_path and current_path != nfile.file_path])
            if temp_file:
                self._temp_files[temp_file] = nfile

        # if current_path:
        #     index = self._filePathPosition[current_path]
        #     self._max_index = max(self._max_index, index) + 1
        #     self._filePathPosition[current_path] = self._max_index

        # print("\n\nmodel:1:", self._filePathPosition, "\n///", model)
        # sort by Path
        model = sorted(model, key=lambda x: self._filePathPosition.get(x[1], False),
                       reverse=True)
        # print("\n\nmodel:2:", model)
        self._root.set_model(model)

    def showEvent(self, event):
        print("\nshowEvent:::showEvent", self.isVisible(), self.view.isVisible())
        self._add_model()
        widget = self.comboParent.ParentalComboEditor.currentEditor()
        if widget is None:
            widget = self._main_container
        
        if self._main_container.splitter.count() < 2:
            width = max(widget.width() / 2, 500)
            height = max(widget.height() / 2, 400)
        else:
            width = widget.width()
            height = widget.height()
        self.view.setFixedWidth(width)
        self.view.setFixedHeight(height)

        super(FilesHandler, self).showEvent(event)
        self._root.show_animation()
        point = widget.mapToGlobal(self.view.pos())
        self.move(point.x(), point.y())
        self.view.setFocus()
        self._root.activateInput()
        # QTimer.singleShot(5000, lambda item=self._root.childItems()[0].childItems()[0]:\
        #     print("QTimer::", item, item.hasActiveFocus(), item.scopedFocusItem(),\
        #         item.hasFocus(), item.isFocusScope() ))

    def hideEvent(self, event):
        print("\nhideEvent:::", self.isVisible(), self.view.isVisible())
        super(FilesHandler, self).hideEvent(event)
        self._temp_files = {}
        self._root.clear_model()

    def next_item(self):
        print("next_item()", self)
        if not self.isVisible():
            self.show()
        self._root.next_item()

    def previous_item(self):
        print("previous_item()", self)
        if not self.isVisible():
            self.show()
        self._root.previous_item()

    def keyPressEvent(self, event):
        print("keyPressEvent()", event.key(), event.key() == Qt.Key_Escape)
        if event.key() == Qt.Key_Escape:
            self.hide()
        elif (event.modifiers() == Qt.ControlModifier and
                event.key() == Qt.Key_PageDown) or event.key() == Qt.Key_Down:
            self._root.next_item()
        elif (event.modifiers() == Qt.ControlModifier and
                event.key() == Qt.Key_PageUp) or event.key() == Qt.Key_Up:
            self._root.previous_item()
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self._root.open_item()
        # elif event.key() == Qt.Key_Asterisk):
        #     print("keyPressEvent()", self,self.isVisible())
        super(FilesHandler, self).keyPressEvent(event)

    def mousePressEvent(self, event):
        print("\n\nFILESHANDLER.mousePressEvent", QApplication.instance().widgetAt( self.mapToGlobal(event.pos()) ))
        if QApplication.instance().widgetAt( self.mapToGlobal(event.pos()) ) == self.comboParent:
            print("TRUE!!!")
            # event.ignore()
            self.comboParent.hidePopup()
            return
        super(FilesHandler, self).mousePressEvent(event)

