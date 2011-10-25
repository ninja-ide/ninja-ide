# -*- coding: utf-8 -*-
from __future__ import absolute_import

from ninja_ide.core import cliparser
from ninja_ide.gui import ide


def run_ninja():
    filenames, projects_path, extra_plugins = cliparser.parse()
    ide.start(filenames, projects_path, extra_plugins)
