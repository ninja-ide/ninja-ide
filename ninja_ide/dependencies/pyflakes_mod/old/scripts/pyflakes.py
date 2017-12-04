"""
Implementation of the command-line I{pyflakes} tool.
"""
from __future__ import absolute_import

# For backward compatibility
from ninja_ide.dependencies.pyflakes_mod.api import (
    check, checkPath, checkRecursive, iterSourceCode, main)
