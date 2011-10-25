# -*- coding: utf-8 -*-
from __future__ import absolute_import


class ITabItem(object):

    EXTRA_MENU = {}

    def __init__(self):
        self._id = ""    # Should be unique
        self.wasModified = False

        self._parentTab = None

    def get_id(self):
        return self._id

    def set_id(self, id_):
        self._id = id_
        if id_:
            self.newDocument = False

    ID = property(lambda self: self.get_id(), lambda self,
        fileName: self.set_id(fileName))

    def __eq__(self, path):
        """Compares if the path (str) received is equal to the id"""
        return self._id == path

    @classmethod
    def add_extra_menu(cls, menu, lang="py"):
        if not lang in cls.EXTRA_MENU:
            cls.EXTRA_MENU[lang] = []

        cls.EXTRA_MENU[lang].append(menu)
