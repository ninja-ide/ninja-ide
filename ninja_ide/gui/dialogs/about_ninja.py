# *-* coding: utf-8 *-*
from __future__ import absolute_import

from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QPixmap
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QSize
from PyQt4.QtCore import QEvent

import ninja_ide
from ninja_ide import resources
from ninja_ide.gui.main_panel import main_container
from ninja_ide.gui.menus.lib.tetrisgame import TetrisMainWindow


class AboutNinja(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent, Qt.Dialog)
        self.setModal(True)
        self.setWindowTitle(self.tr("About NINJA-IDE"))
        self.setMaximumSize(QSize(0, 0))

        vbox = QVBoxLayout(self)

        #Create an icon for the Dialog
        pixmap = QPixmap(resources.IMAGES['icon'])
        self.lblIcon = QLabel()
        self.lblIcon.setPixmap(pixmap)

        hbox = QHBoxLayout()
        hbox.addWidget(self.lblIcon)

        lblTitle = QLabel(
                '<h1>NINJA-IDE</h1>\n<i>Ninja-IDE Is Not Just Another IDE<i>')
        lblTitle.setTextFormat(Qt.RichText)
        lblTitle.setAlignment(Qt.AlignLeft)
        hbox.addWidget(lblTitle)
        vbox.addLayout(hbox)
        #Add description
        vbox.addWidget(QLabel(
self.tr("""NINJA-IDE (from: "Ninja Is Not Just Another IDE"), is a
cross-platform integrated development environment specially design
to build Python Applications.
NINJA-IDE provides tools to simplify the Python-software development
and handles all kinds of situations thanks to its rich extensibility.""")))
        vbox.addWidget(QLabel(self.tr("Version: %1").arg(
                ninja_ide.__version__)))
        vbox.addWidget(QLabel(
            self.tr("Website: %1").arg(ninja_ide.__url__)))
        vbox.addWidget(QLabel(
            self.tr("Source Code: %1").arg(ninja_ide.__source__)))

        self.lblIcon.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj == self.lblIcon and event.type() == QEvent.MouseButtonPress:
            self.show_retsae()
        return False

    def show_retsae(self):
        height = main_container.MainContainer().size().height()
        width = main_container.MainContainer().size().width()
        tetris = TetrisMainWindow(width, height)
        main_container.MainContainer().add_tab(tetris, 'Tetris')
        self.close()
