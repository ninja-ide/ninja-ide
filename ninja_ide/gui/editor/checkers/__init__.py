# -*- coding: utf-8 -*-

from ninja_ide import resources
from ninja_ide.core import settings
from ninja_ide.gui.editor.checkers import (
    errors_checker,
    migration_2to3,
    pep8_checker,
)


NOTIFICATIONS_CHECKERS = {}


def register_checker(lang='python', checker=None, color=None, priority=1):
    """Register a Checker (Like PEP8, Lint, etc) for some language.
    @lang: language that the checker apply.
    @checker: Class to be instantiated.
    @color: the color that this checker will use.
    @priority: the priority of this checker (1=LOW, >1 = HIGH...)"""
    global NOTIFICATIONS_CHECKERS
    checkers = NOTIFICATIONS_CHECKERS.get(lang, [])
    checkers.append((checker, color, priority))
    NOTIFICATIONS_CHECKERS[lang] = checkers


def get_checkers_for(lang='python'):
    """Get a registered checker for some language."""
    global NOTIFICATIONS_CHECKERS
    return NOTIFICATIONS_CHECKERS.get(lang, [])


if settings.FIND_ERRORS:
    register_checker(checker=errors_checker.ErrorsChecker,
        color=resources.CUSTOM_SCHEME.get('error-underline',
        resources.COLOR_SCHEME['error-underline']), priority=10)
if settings.SHOW_MIGRATION_TIPS:
    register_checker(checker=migration_2to3.MigrationTo3,
        color=resources.CUSTOM_SCHEME.get('migration-underline',
        resources.COLOR_SCHEME['migration-underline']))
if settings.CHECK_STYLE:
    register_checker(checker=pep8_checker.Pep8Checker,
        color=resources.CUSTOM_SCHEME.get('pep8-underline',
        resources.COLOR_SCHEME['pep8-underline']), priority=2)


def remove_pep8_checker():
    checker = (pep8_checker.Pep8Checker,
        resources.CUSTOM_SCHEME.get('pep8-underline',
        resources.COLOR_SCHEME['pep8-underline']), 2)
    global NOTIFICATIONS_CHECKERS
    checkers = NOTIFICATIONS_CHECKERS.get('python', [])
    if checker in checkers:
        checkers.remove(checker)
        NOTIFICATIONS_CHECKERS['python'] = checkers


def remove_error_checker():
    checker = (errors_checker.ErrorsChecker,
        resources.CUSTOM_SCHEME.get('error-underline',
        resources.COLOR_SCHEME['error-underline']), 10)
    global NOTIFICATIONS_CHECKERS
    checkers = NOTIFICATIONS_CHECKERS.get('python', [])
    if checker in checkers:
        checkers.remove(checker)
        NOTIFICATIONS_CHECKERS['python'] = checkers


def remove_migration_checker():
    checker = (migration_2to3.MigrationTo3,
        resources.CUSTOM_SCHEME.get('migration-underline',
        resources.COLOR_SCHEME['migration-underline']), 1)
    global NOTIFICATIONS_CHECKERS
    checkers = NOTIFICATIONS_CHECKERS.get('python', [])
    if checker in checkers:
        checkers.remove(checker)
        NOTIFICATIONS_CHECKERS['python'] = checkers