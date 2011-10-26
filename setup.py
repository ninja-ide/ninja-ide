#!/usr/bin/env python
#-*-coding:utf-8-*-

# Copyright (C) - 2011 Matías Herranz <matiasherranzgmail.com>

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


#===============================================================================
# DOCS
#===============================================================================

"""Setup for NinjaIDE"""


#===============================================================================
# IMPORTS
#===============================================================================

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

import ninja_ide


#===============================================================================
# SETUP
#===============================================================================

# download_url =

setup(name=ninja_ide.__name__,
      version=ninja_ide.__version__,
      description=ninja_ide.__doc__,
      author=ninja_ide.__author__,
      author_email=ninja_ide.__mail__,
      url=ninja_ide.__url__,
      # download_url=download_url,
      license=ninja_ide.__license__,
      keywords="ninja_ide ide",
      classifiers=[
                   "Topic :: Python IDE",
                   # something like:
                   # "License :: OSI Approved :: GNU LGeneral Public License (GPL)",
                   # for the license
                   "Programming Language :: Python :: 2",
                   ],
      packages = find_packages(),
      include_package_data = True,
      scripts = ['ninja-ide.py'],

      install_requires=["PyQt4",]
)


#===============================================================================
# MAIN
#===============================================================================

if __name__ == '__main__':
    print(__doc__)
