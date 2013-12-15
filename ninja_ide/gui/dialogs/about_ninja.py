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

from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QPixmap
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QSize
from PyQt4.QtCore import SIGNAL

from ninja_ide.ui_tools import ScrollLabel

import ninja_ide

LINKS = """
    <a href="{web}" title="{web}" style="{sty}">Website</a>,
    <a href="{cod}" title="{cod}" style="{sty}">Source Code</a>,
    <a href="{plg}" title="{plg}" style="{sty}">Plugins</a>,
    <a href="{sch}" title="{sch}" style="{sty}">Schemes</a>,
    <a href="{twt}" title="{twt}" style="{sty}">Twitter</a>,
    <a href="{plu}" title="{plu}" style="{sty}">Google Plus</a>,
    <a href="{mai}" title="{mai}" style="{sty}">Mailing List</a>,
    <a href="{irc}" title="{irc}" style="{sty}">IRC Channel</a>,
    <a href="{sho}" title="{sho}" style="{sty}">Ninja Store</a>,
    <a href="{trv}" title="{trv}" style="{sty}">Travis CI</a>""".format(
    sty='text-decoration:underline;color:#ff9e21',
    web=ninja_ide.__url__,
    cod=ninja_ide.__source__, plg=ninja_ide.__url__ + '/plugins',
    sch=ninja_ide.__url__ + '/schemes', twt='https://twitter.com/ninja_ide',
    plu='https://plus.google.com/103973182574871451647',
    mai='http://groups.google.com/group/ninja-ide/topics',
    trv='https://travis-ci.org/ninja-ide/ninja-ide',
    sho='http://www.zazzle.com/ninja-ide',
    irc='https://kiwiirc.com/client/chat.freenode.net/?nick=Ninja%7C?&theme=cli#ninja-ide',
).strip()


class AboutNinja(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent, Qt.Dialog)
        self.setWindowTitle(self.tr("About NINJA-IDE"))
        self.setMaximumSize(QSize(0, 0))

        vbox = QVBoxLayout(self)

        #Create an icon for the Dialog
        pixmap = QPixmap(":img/icon")
        self.lblIcon = QLabel()
        self.lblIcon.setPixmap(pixmap)

        hbox = QHBoxLayout()
        hbox.addWidget(self.lblIcon)

        lblTitle = QLabel(
                '<h1>NINJA-IDE</h1>\n<i>Ninja-IDE Is Not Just Another IDE')
        lblTitle.setTextFormat(Qt.RichText)
        lblTitle.setAlignment(Qt.AlignLeft)
        hbox.addWidget(lblTitle)
        vbox.addLayout(hbox)
        #Add description
        vbox.addWidget(QLabel(
self.tr("""NINJA-IDE (from: "Ninja Is Not Just Another IDE"), is a
cross-platform integrated development environment specially designed
to build Python Applications.
NINJA-IDE provides tools to simplify the Python-software development
and handles all kinds of situations thanks to its rich extensibility.""")))
        vbox.addWidget(QLabel(self.tr("Version: %s") % ninja_ide.__version__))
        links = ScrollLabel(LINKS)
        links.setTextInteractionFlags(Qt.LinksAccessibleByMouse)
        links.setOpenExternalLinks(True)
        links.setScrolling(True)
        vbox.addWidget(links)

