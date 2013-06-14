#!/usr/bin/env python
#-*-coding:utf-8-*-

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


###############################################################################
# DOCS
###############################################################################

"""Setup for Ninja-ide (http://www.ninja-ide.org)

NINJA-IDE is a cross-platform integrated development environment (IDE).
NINJA-IDE runs on Linux/X11, Mac OS X and Windows desktop operating systems,
and allows developers to create applications for several purposes using all the
tools and utilities of NINJA-IDE, making the task of writing software easier
and more enjoyable.
"""


###############################################################################
# IMPORTS
###############################################################################

import sys

from setuptools import setup, find_packages

import ninja_ide

###############################################################################
# VALIDATE THE NEEDED MODULES
###############################################################################

# This modules can't be easy installed
# Syntax: [(module, url of the tutorial)...]
if sys.platform == 'win32':
    NEEDED_MODULES = [("PyQt4",
        "http://www.riverbankcomputing.co.uk/software/pyqt/intro"),
        ('win32con', "http://sourceforge.net/projects/pywin32/files/pywin32/")]
else:
    NEEDED_MODULES = [("PyQt4",
        "http://www.riverbankcomputing.co.uk/software/pyqt/intro"), ]


for mn, urlm in NEEDED_MODULES:
    try:
        __import__(mn)
    except ImportError:
        print("Module '%s' not found. For more details: '%s'.\n" % (mn, urlm))
        sys.exit(1)


dependencies = []
if sys.platform == 'darwin':
    dependencies.append("macfsevents")
elif sys.platform == 'linux2':
    dependencies.append("pyinotify")


###############################################################################
# PRE-SETUP
###############################################################################

# Common
params = {
    "name": ninja_ide.__prj__,
    "version": ninja_ide.__version__,
    "description": ninja_ide.__doc__,
    "author": ninja_ide.__author__,
    "author_email": ninja_ide.__mail__,
    "url": ninja_ide.__url__,
    "license": ninja_ide.__license__,
    "keywords": "ide python ninja development",
    "classifiers": ["Development Status :: Development Status :: 4 - Beta",
               "Topic :: Utilities",
               "License :: OSI Approved :: GNU General Public License (GPL)",
               "Natural Language :: English",
               "Operating System :: OS Independent",
               "Programming Language :: Python :: 2"],

    # Ninja need:
    "install_requires": dependencies,

    # include all resources
    "include_package_data": True,
    "package_data": {'': ['*.png', '*.gif', '*.jpg', '*.json', '*.qss',
        '*.js', '*.html', '*.css', '*.qm', '*.qml']},

    # include ninja pkg and setup the run script
    "packages": find_packages() + [
        'ninja_ide/addins',
        'ninja_ide/addins/lang',
        'ninja_ide/addins/qml',
        'ninja_ide/addins/qml/img',
        'ninja_ide/addins/syntax',
        'ninja_ide/addins/theme',
        'ninja_ide/img'],

    #auto create scripts
    "entry_points": {
        'console_scripts': [
            'ninja-ide = ninja_ide:setup_and_run',
        ],
        'gui_scripts': [
            'ninja-ide = ninja_ide:setup_and_run',
        ]
    }
}


###############################################################################
# SETUP
###############################################################################

setup(**params)


###############################################################################
# MAIN
###############################################################################

if __name__ == '__main__':
    print(__doc__)
