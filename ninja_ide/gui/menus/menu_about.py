# -*- coding: utf-8 -*-
from __future__ import absolute_import

from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QKeySequence
from PyQt4.QtCore import QObject
from PyQt4.QtCore import SIGNAL

from ninja_ide import resources
from ninja_ide.gui.main_panel import main_container
from ninja_ide.gui.main_panel import browser_widget
from ninja_ide.gui.dialogs import about_ninja


class MenuAbout(QObject):

    def __init__(self, menuAbout):
        QObject.__init__(self)

        startPageAction = menuAbout.addAction(self.tr("Show Start Page"))
        helpAction = menuAbout.addAction(self.tr("Python Help (%1)").arg(
            resources.get_shortcut("Help").toString(QKeySequence.NativeText)))
        menuAbout.addSeparator()
        reportBugAction = menuAbout.addAction(self.tr("Report Bugs!"))
        pluginsDocAction = menuAbout.addAction(
                                        self.tr("Plugins Documentation"))
        menuAbout.addSeparator()

        aboutNinjaAction = menuAbout.addAction(self.tr("About NINJA-IDE"))
        aboutQtAction = menuAbout.addAction(self.tr("About Qt"))

        #Connect Action SIGNALs to proper functions
        self.connect(startPageAction, SIGNAL("triggered()"),
            main_container.MainContainer().show_start_page)

        self.connect(reportBugAction, SIGNAL("triggered()"),
            self.show_report_bugs)
        self.connect(aboutQtAction, SIGNAL("triggered()"),
                            self._show_about_qt)
        self.connect(helpAction, SIGNAL("triggered()"),
            main_container.MainContainer().show_python_doc)
        self.connect(aboutNinjaAction, SIGNAL("triggered()"),
                            self._show_about_ninja)
        self.connect(pluginsDocAction, SIGNAL("triggered()"),
            self.show_plugins_doc)

    def show_report_bugs(self):
        bugsPage = browser_widget.BrowserWidget(resources.BUGS_PAGE,
            parent=main_container.MainContainer())
        main_container.MainContainer().add_tab(
            bugsPage, self.tr("Report Bugs!"))

    def show_plugins_doc(self):
        bugsPage = browser_widget.BrowserWidget(resources.PLUGINS_DOC,
            parent=main_container.MainContainer())
        main_container.MainContainer().add_tab(
            bugsPage, self.tr("How to Write NINJA-IDE plugins"))

    def _show_about_qt(self):
        QMessageBox.aboutQt(main_container.MainContainer(),
            self.tr("About Qt"))

    def _show_about_ninja(self):
        self.about = about_ninja.AboutNinja(main_container.MainContainer())
        self.about.show()
