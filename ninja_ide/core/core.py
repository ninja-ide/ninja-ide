# -*- coding: utf-8 -*-
from __future__ import absolute_import

from ninja_ide import resources
from ninja_ide.core import cliparser


def run_ninja():
    """First obtain the execution args and create the resources folder."""
    filenames, projects_path, extra_plugins = cliparser.parse()
    # Create NINJA-IDE user folder structure for plugins, themes, etc
    resources.create_home_dir_structure()

    # Start the UI
    from ninja_ide.gui import ide
    ide.start(filenames, projects_path, extra_plugins)
