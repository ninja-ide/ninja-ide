# -*- coding: utf-8 -*-


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