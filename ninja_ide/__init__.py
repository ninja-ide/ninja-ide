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


###############################################################################
# METADATA
###############################################################################

__prj__ = "NINJA-IDE"
__author__ = "The NINJA-IDE Team"
__mail__ = "ninja-ide at googlegroups dot com"
__url__ = "http://www.ninja-ide.org"
__source__ = "https://github.com/ninja-ide/ninja-ide"
__version__ = "3.0-alpha"
__license__ = "GPL3"

###############################################################################
# DOC
###############################################################################

"""NINJA-IDE is a cross-platform integrated development environment (IDE).
NINJA-IDE runs on Linux/X11, Mac OS X and Windows desktop operating systems,
and allows developers to create applications for several purposes using all the
tools and utilities of NINJA-IDE, making the task of writing software easier
and more enjoyable.
"""

###############################################################################
# SET PYQT API 2
###############################################################################

# import sip
# API_NAMES = ["QDate", "QDateTime", "QString", "QTime", "QUrl", "QTextStream",
#             "QVariant"]
# API_VERSION = 2
# for name in API_NAMES:
#    sip.setapi(name, API_VERSION)

###############################################################################
# START
###############################################################################


def setup_and_run():
    """Load the Core module and trigger the execution."""
    # import only on run
    # Dont import always this, setup.py will fail
    from ninja_ide import core
    from ninja_ide import nresources  # noqa
    from multiprocessing import freeze_support

    # Used to support multiprocessing on windows packages
    freeze_support()

    # Run NINJA-IDE
    core.run_ninja()
