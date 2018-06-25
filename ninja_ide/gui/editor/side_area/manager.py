# -*- coding: utf-8 -*-
#
# This file is part of NINJA-IDE (http://ninja-ide.org).
#
# NINJA-IDE is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.
#
# NINJA-IDE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NINJA-IDE; If not, see <http://www.gnu.org/licenses/>.

from collections import OrderedDict


class SideWidgetManager(object):
    """Manages side widgets"""

    def __init__(self, neditor):
        self.__widgets = OrderedDict()
        self._neditor = neditor
        self.__width = 0

        neditor.blockCountChanged.connect(self.update_viewport)
        neditor.updateRequest.connect(self._update)

    def add(self, Widget):
        """Installs a widget on left area of the editor"""

        widget_obj = Widget()
        self.__widgets[widget_obj.object_name] = widget_obj
        widget_obj.register(self._neditor)
        self.update_viewport()
        return widget_obj

    def get(self, object_name):
        """Returns a side widget instance"""

        return self.__widgets.get(object_name)

    def remove(self, object_name):
        widget = self.get(object_name)
        del self.__widgets[object_name]
        # widget.hide()
        widget.setParent(None)
        widget.deleteLater()

    def _update(self):
        for widget in self:
            widget.update()

    def __iter__(self):
        return iter(self.__widgets.values())

    def __len__(self):
        return len(self.__widgets.values())

    def update_viewport(self):
        """Recalculates geometry for all the side widgets"""

        total_width = 0
        for widget in self:
            if not widget.isVisible():
                continue
            total_width += widget.sizeHint().width()
        self._neditor.setViewportMargins(total_width, 0, 0, 0)

    def resize(self):
        """Resize all side widgets"""

        cr = self._neditor.contentsRect()
        current_x = cr.left()
        top = cr.top()
        height = cr.height()
        left = 0
        for widget in self:
            size_hint = widget.sizeHint()
            width = size_hint.width()
            widget.setGeometry(current_x + left, top, width, height)
            left += size_hint.width()
        self.__width = left

    @property
    def width(self):
        return self.__width