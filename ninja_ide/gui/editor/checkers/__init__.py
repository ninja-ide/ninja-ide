# -*- coding: utf-8 -*-

from ninja_ide import resources
from ninja_ide.gui.editor.checkers import (
    errors_checker,
    migration_2to3,
    pep8_checker,
)


NOTIFICATIONS_CHECKERS = {}


def register_checker(lang='python', checker=None, color=None):
    """Register a Checker (Like PEP8, Lint, etc) for some language."""
    global NOTIFICATIONS_CHECKERS
    checkers = NOTIFICATIONS_CHECKERS.get(lang, [])
    checkers.append((checker, color))
    NOTIFICATIONS_CHECKERS[lang] = checkers


def get_checker_for(lang='python'):
    """Get a registered checker for some language."""
    global NOTIFICATIONS_CHECKERS
    return NOTIFICATIONS_CHECKERS.get(lang, [])


register_checker(checker=errors_checker.ErrorsChecker,
    resources.CUSTOM_SCHEME.get('error-underline',
    resources.COLOR_SCHEME['error-underline']))
register_checker(checker=migration_2to3.MigrationTo3,
    resources.CUSTOM_SCHEME.get('migration-underline',
    resources.COLOR_SCHEME['migration-underline']))
register_checker(checker=pep8_checker.Pep8Checker,
    resources.CUSTOM_SCHEME.get('pep8-underline',
    resources.COLOR_SCHEME['pep8-underline']))