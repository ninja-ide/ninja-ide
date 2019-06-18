#!/usr/bin/env python3
# -*-coding:utf-8-*-

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

# import sys
import os
# import shutil

from distutils.command.install import install
from setuptools import setup, find_packages

import ninja_ide


class CustomInstall(install):
    """
    Custom installation class on package files.

    It copies all the files into the "PREFIX/share/ninja-ide" dir.
    """

    def run(self):
        install.run(self)

        for script in self.distribution.scripts:

            script_path = os.path.join(self.install_scripts,
                                       os.path.basename(script))

            with open(script_path, 'r') as f:
                content = f.read()
            content = content.replace('@ INSTALLED_BASE_DIR @',
                                      self._custom_data_dir)
            with open(script_path, 'w') as f:
                f.write(content)

            src_desktop = self.distribution.get_name() + '.desktop'
            src_desktop = src_desktop.lower()

            if not os.path.exists(self._custom_apps_dir):
                os.makedirs(self._custom_apps_dir)
            dst_desktop = os.path.join(self._custom_apps_dir, src_desktop)
            with open(src_desktop, 'r') as f:
                content = f.read()
            icon = os.path.join(self._custom_data_dir, "ninja_ide", "img", "icon.png")
            content = content.replace('@ INSTALLED_ICON @', icon)
            with open(dst_desktop, 'w') as f:
                f.write(content)

            # Man dir
            # if not os.path.exists(self._custom_man_dir):
            #     os.makedirs(self._custom_man_dir)
            # shutil.copy("man/ninja-ide.1", self._custom_man_dir)

    def finalize_options(self):
        """ Alter the installation path """

        install.finalize_options(self)

        data_dir = os.path.join(self.prefix, "share",
                                self.distribution.get_name())
        apps_dir = os.path.join(self.prefix, "share", "applications")
        # man_dir = os.path.join(self.prefix, "share", "man", "man1")

        if self.root is None:
            build_dir = data_dir
        else:

            build_dir = os.path.join(self.root, data_dir[1:])
            apps_dir = os.path.join(self.root, apps_dir[1:])
            # man_dir = os.path.join(self.root, man_dir[1:])

        self.install_lib = build_dir

        self._custom_data_dir = data_dir
        self._custom_apps_dir = apps_dir
        # self._custom_man_dir = man_dir


###############################################################################
# SETUP
###############################################################################

setup(
    name=ninja_ide.__prj__,
    version=ninja_ide.__version__,
    description=ninja_ide.__doc__,
    author=ninja_ide.__author__,
    author_email=ninja_ide.__mail__,
    url=ninja_ide.__url__,
    license=ninja_ide.__license__,
    keywords="ide python ninja development",
    classifiers=[
        "Development Status :: Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3"
    ],
    package_data={
        "ninja_ide": [
            "addins/lang/*",
            "addins/qml/*",
            "addins/qml/img/*",
            "addins/syntax/*",
            "addins/theme/*",
            "img/*"
        ]
    },
    packages=find_packages(exclude=["ninja_tests", "debian"]),
    scripts=["ninja-ide"],
    cmdclass={"install": CustomInstall}
)


###############################################################################
# MAIN
###############################################################################

if __name__ == '__main__':
    print(__doc__)
