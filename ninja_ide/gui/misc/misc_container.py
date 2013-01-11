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

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QToolBar
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QStyle
from PyQt4.QtGui import QStackedWidget
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QSpacerItem
from PyQt4.QtGui import QSizePolicy
from PyQt4.QtCore import SIGNAL
from PyQt4.QtWebKit import QWebPage

from ninja_ide import resources
from ninja_ide .core import settings
from ninja_ide.gui.explorer import explorer_container
from ninja_ide.gui.misc import console_widget
from ninja_ide.gui.misc import run_widget
from ninja_ide.gui.misc import web_render
from ninja_ide.gui.misc import find_in_files
from ninja_ide.gui.misc import results
from ninja_ide.tools import ui_tools


__miscContainerInstance = None


def MiscContainer(*args, **kw):
    global __miscContainerInstance
    if __miscContainerInstance is None:
        __miscContainerInstance = __MiscContainer(*args, **kw)
    return __miscContainerInstance


class __MiscContainer(QWidget):
    """From Miscellaneous, contains all the widgets in the bottom area."""
    #Miscellaneous was to long and dificult to write :P

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)

        self.__toolbar = QToolBar()
        self.__toolbar.setObjectName('custom')
        hbox = QHBoxLayout()
        vbox.addLayout(hbox)

        self.stack = StackedWidget()
        vbox.addWidget(self.stack)

        self._console = console_widget.ConsoleWidget()
        self.stack.addWidget(self._console)

        self._runWidget = run_widget.RunWidget()
        self.stack.addWidget(self._runWidget)

        self._web = web_render.WebRender()
        self.stack.addWidget(self._web)

        self._findInFilesWidget = find_in_files.FindInFilesWidget(
            self.parent())
        self.stack.addWidget(self._findInFilesWidget)

        #Last Element in the Stacked widget
        self._results = results.Results(self)
        self.stack.addWidget(self._results)

        self._btnConsole = QPushButton(QIcon(resources.IMAGES['console']), '')
        self._btnConsole.setToolTip(self.tr("Console"))
        self._btnRun = QPushButton(QIcon(resources.IMAGES['play']), '')
        self._btnRun.setToolTip(self.tr("Output"))
        self._btnWeb = QPushButton(QIcon(resources.IMAGES['web']), '')
        self._btnWeb.setToolTip(self.tr("Web Preview"))
        self._btnFind = QPushButton(QIcon(resources.IMAGES['find']), '')
        self._btnFind.setToolTip(self.tr("Find in Files"))
        #Toolbar
        hbox.addWidget(self.__toolbar)
        self.__toolbar.addWidget(self._btnConsole)
        self.__toolbar.addWidget(self._btnRun)
        self.__toolbar.addWidget(self._btnWeb)
        self.__toolbar.addWidget(self._btnFind)
        self.__toolbar.addSeparator()
        hbox.addSpacerItem(QSpacerItem(1, 0, QSizePolicy.Expanding))
        btn_close = QPushButton(
            self.style().standardIcon(QStyle.SP_DialogCloseButton), '')
        btn_close.setObjectName('navigation_button')
        btn_close.setToolTip(self.tr('F4: Show/Hide'))
        hbox.addWidget(btn_close)

        self.connect(self._btnConsole, SIGNAL("clicked()"),
            lambda: self._item_changed(0))
        self.connect(self._btnRun, SIGNAL("clicked()"),
            lambda: self._item_changed(1))
        self.connect(self._btnWeb, SIGNAL("clicked()"),
            lambda: self._item_changed(2))
        self.connect(self._btnFind, SIGNAL("clicked()"),
            lambda: self._item_changed(3))
        self.connect(btn_close, SIGNAL('clicked()'), self.hide)

    def gain_focus(self):
        self._console.setFocus()

    def _item_changed(self, val):
        if not self.isVisible():
            self.show()
        self.stack.show_display(val)

    def show_find_in_files_widget(self):
        index_of = self.stack.indexOf(self._findInFilesWidget)
        self._item_changed(index_of)
        self._findInFilesWidget.open()

    def show_find_occurrences(self, word):
        index_of = self.stack.indexOf(self._findInFilesWidget)
        self._item_changed(index_of)
        self._findInFilesWidget.find_occurrences(word)

    def load_toolbar(self, toolbar):
        toolbar.addWidget(self._combo)
        toolbar.addSeparator()

    def run_application(self, fileName, pythonPath=False, PYTHONPATH=None,
            programParams='', preExec='', postExec=''):
        self._item_changed(1)
        self.show()
        self._runWidget.start_process(fileName, pythonPath, PYTHONPATH,
            programParams, preExec, postExec)
        self._runWidget.input.setFocus()

    def show_results(self, items):
        self._item_changed(4)
        self.show()
        self._results.update_result(items)
        self._results._tree.setFocus()

    def kill_application(self):
        self._runWidget.kill_process()

    def render_web_page(self, url):
        self._item_changed(2)
        self.show()
        self._web.render_page(url)
        if settings.SHOW_WEB_INSPECTOR:
            explorer_container.ExplorerContainer().set_inspection_page(
            self._web.webFrame.page())
            self._web.webFrame.triggerPageAction(
                QWebPage.InspectElement, True)
            explorer_container.ExplorerContainer().refresh_inspector()

    def add_to_stack(self, widget, icon_path, description):
        """
        Add a widget to the container and an button(with icon))to the toolbar
        to show the widget
        """
        #add the widget
        self.stack.addWidget(widget)
        #create a button in the toolbar to show the widget
        button = QPushButton(QIcon(icon_path), '')
        button.setToolTip(description)
        index = self.stack.count() - 1
        func = lambda: self._item_changed(index)
        self.connect(button, SIGNAL("clicked()"), func)
        self.__toolbar.addWidget(button)


class StackedWidget(QStackedWidget):

    def __init__(self):
        QStackedWidget.__init__(self)

    def setCurrentIndex(self, index):
        self.fader_widget = ui_tools.FaderWidget(self.currentWidget(),
            self.widget(index))
        QStackedWidget.setCurrentIndex(self, index)

    def show_display(self, index):
        self.setCurrentIndex(index)
