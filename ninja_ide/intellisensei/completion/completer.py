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

import re
from PyQt5.QtWidgets import (
    QListView
)
from PyQt5.QtCore import (
    QObject,
    Qt,
    QEvent,
    pyqtSlot,
    pyqtSignal,
    QModelIndex,
    QTimer,
    QAbstractListModel
)


class Completer(QObject):

    def __init__(self, neditor):
        super().__init__()
        self._neditor = neditor
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._words = set()
        self.__word_pat = re.compile('\w+')

        self._list_view = None
        # Connections
        self._neditor.textChanged.connect(self.__on_text_changed)
        self._timer.timeout.connect(self._collect_words)

    @property
    def words(self):
        return self._words

    @pyqtSlot()
    def _collect_words(self):
        # FIXME: check performance
        self._words.clear()
        for line_text in self._neditor.text.splitlines():
            for match in self.__word_pat.findall(line_text):
                self._words.add(match)

    @pyqtSlot()
    def __on_text_changed(self):
        """Start collect words"""

        self._timer.start(1000)

    def show_completions(self):
        # Invoke by editor
        if self.words:
            prefix = self._word_before_cursor()
            if prefix:
                if self._list_view is None:
                    model = CompletionListModel(self.words)
                    # model.setData(prefix)
                    self._list_view = CompletionListView(model, self._neditor)
                    self._list_view.keyEscapePressed.connect(
                        self.hide_completer)
                    self._list_view.show()
                else:
                    pass

    def _word_before_cursor(self):
        cursor = self._neditor.textCursor()
        text_before_cursor = cursor.block().text()[:cursor.positionInBlock()]
        w = re.compile('\w+$')
        match = w.search(text_before_cursor)
        return match.group(0)

    def hide_completer(self):
        self._list_view.close()
        self._list_view = None


class CompletionListView(QListView):

    keyEscapePressed = pyqtSignal()

    def __init__(self, model, parent=None):
        super().__init__(parent.viewport())
        self.setModel(model)
        self._neditor = parent
        parent.installEventFilter(self)

        self.setFocusPolicy(Qt.NoFocus)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.update_geometry()
        parent.setFocus()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyRelease:
            if event.key() == Qt.Key_Escape:
                self.keyEscapePressed.emit()
                return True
        return False

    def update_geometry(self):
        cursor_rect = self._neditor.cursorRect()
        width = self.sizeHint().width()
        height = self.sizeHint().height()

        x = cursor_rect.right()
        y = cursor_rect.bottom()

        self.setGeometry(x, y, width, height)


class CompletionListModel(QAbstractListModel):

    def __init__(self, words_set):
        super().__init__()
        self.__completions = [word for word in words_set]

    def data(self, index, role):
        if role == Qt.DisplayRole and index.row() < len(self.__completions):
            text = self.__completions[index.row()]
            return text

    def setData(self, prefix):
        pass

    def columnCount(self, index):
        return 1

    def rowCount(self, index=QModelIndex()):
        return len(self.__completions)



'''import re
import time
from PyQt5.QtWidgets import QListView
from PyQt5.QtCore import (
    QObject,
    QAbstractListModel,
    pyqtSlot,
    pyqtSignal,
    QModelIndex,
    QTimer,
    QEvent,
    Qt
)
from PyQt5.QtGui import QColor
word_pat = re.compile("\w+")


class WordSetTimer(object):

    def __init__(self):
        self.__timer = QTimer()
        self.__timer.setSingleShot(True)
        self.__timer.timeout.connect(self.__on_timeout)
        self.__scheduled_methods = []

    def __on_timeout(self):
        func = self.__scheduled_methods.pop()
        func()
        if self.__scheduled_methods:
            self.__timer.start(1000)

    def schedule(self, func):
        if func not in self.__scheduled_methods:
            self.__scheduled_methods.append(func)
        self.__timer.start(1000)


class Completer(QObject):

    def __init__(self, neditor):
        QObject.__init__(self, neditor)
        self._neditor = neditor
        self._neditor.textChanged.connect(self.__on_text_changed)
        self._timer = WordSetTimer()
        self._words = None
        self._list_view = None

    @pyqtSlot()
    def __on_text_changed(self):
        self._timer.schedule(self._update_words)

    def _update_words(self):
        self._words = set()
        start = time.time()
        for line in self._neditor.text.splitlines():
            for match in word_pat.findall(line):
                self._words.add(match)
            if time.time() - start > 0.4:
                break

    def show_completion(self):
        if self._words is not None:
            if self._list_view is None:
                model = CompletionModel(self._words)
                listview = CompletionWidget(self._neditor, model)
                listview.closeMe.connect(self.hide_completer)
                listview.show()
            else:
                self._list_view.show()

    def hide_completer(self):
        self._list_view.close()
        self._list_view = None


class CompletionModel(QAbstractListModel):

    def __init__(self, words):
        super().__init__()
        self.__words = [word for word in words]

    @property
    def completions(self):
        return self.__words

    def rowCount(self, index=QModelIndex()):
        return len(self.__words)

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self.__words[index.row()]


class CompletionWidget(QListView):

    closeMe = pyqtSignal()

    def __init__(self, neditor, model):
        super().__init__(neditor.viewport())
        pal = self.palette()
        pal.setColor(pal.Base, QColor('#313640'))
        self.setPalette(pal)
        self._neditor = neditor
        self.setModel(model)
        self.setFocusPolicy(Qt.NoFocus)

        self._selected_index = -1

        self._neditor.installEventFilter(self)
        self.updateGeometry()
        self._neditor.setFocus()

    def updateGeometry(self):
        width = self.sizeHint().width()
        height = self.sizeHint().height()
        cr = self._neditor.cursorRect()
        ypos = cr.bottom()
        xpos = max(3, cr.top() - height)
        self.setGeometry(xpos, ypos, width, height)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Escape:
                self.closeMe.emit()
                return True
            elif event.key() == Qt.Key_Down:
                if self._selected_index + 1 < self.model().rowCount():
                    self._select_item(self._selected_index + 1)
                return True
            elif event.key() == Qt.Key_Up:
                if self._selected_index - 1 >= 0:
                    self._select_item(self._selected_index - 1)
                return True
            elif event.key() in (Qt.Key_Return, Qt.Key_Enter):

                return True
        return False
    def __show_completion(self):
        index = self.currentIndex().row()
        model = self.model()
        selected = model.completions[index]
        self._neditor.textCursor().insertText(selected)
        self.hide()
    def _select_item(self, index):
        self._selected_index = index
        self.setCurrentIndex(self.model().createIndex(index, 0))

'''
"""from __future__ import absolute_import

import sys
import types
#import inspect
try:
    import StringIO
except:
    import io as StringIO  # lint:ok
from ninja_ide.tools.logger import NinjaLogger

logger = NinjaLogger('ninja_ide.tools.completion.completer')

_HELPOUT = StringIO.StringIO
_STDOUT = sys.stdout


def get_completions_per_type(object_dir):
    '''Return info about function parameters'''

    if not object_dir:
        return {}
    result = {'attributes': [], 'modules': [], 'functions': [], 'classes': []}
    type_assign = {types.ClassType: 'classes',
                   types.FunctionType: 'functions',
                   types.MethodType: 'functions',
                   types.ModuleType: 'modules',
                   types.LambdaType: 'functions'}

    for attr in object_dir:
        obj = None
        sig = ""
        try:
            obj = _load_symbol(attr, globals(), locals())
        except Exception as ex:
            logger.error('Could not load symbol: %r', ex)
            return {}

        if type(obj) in (types.ClassType, types.TypeType):
            # Look for the highest __init__ in the class chain.
            obj = _find_constructor(obj)
        elif isinstance(obj, types.MethodType):
            # bit of a hack for methods - turn it into a function
            # but we drop the "self" param.
            obj = obj.im_func

        # Not Show functions args, but we will use this for showing doc
#        if type(obj) in [types.FunctionType, types.LambdaType]:
#            (args, varargs, varkw, defaults) = inspect.getargspec(obj)
#            sig = ('%s%s' % (obj.__name__,
#                               inspect.formatargspec(args, varargs, varkw,
#                                                     defaults)))
        if not sig:
            sig = attr[attr.rfind('.') + 1:]
        result[type_assign.get(type(obj), 'attributes')].append(sig)
    return result


def _load_symbol(s, dglobals, dlocals):
    sym = None
    dots = s.split('.')
    if not s or len(dots) == 1:
        sym = eval(s, dglobals, dlocals)
    else:
        for i in range(1, len(dots) + 1):
            s = '.'.join(dots[:i])
            if not s:
                continue
            try:
                sym = eval(s, dglobals, dlocals)
            except NameError:
                try:
                    sym = __import__(s, dglobals, dlocals, [])
                    dglobals[s] = sym
                except ImportError:
                    pass
            except AttributeError:
                try:
                    sym = __import__(s, dglobals, dlocals, [])
                except ImportError:
                    pass
    return sym


def _import_modules(imports, dglobals):
    '''If given, execute import statements'''
    if imports is not None:
        for stmt in imports:
            try:
                exec(stmt, dglobals)
            except TypeError:
                raise TypeError('invalid type: %s' % stmt)
            except Exception:
                continue


def get_all_completions(s, imports=None):
    '''Return contextual completion of s (string of >= zero chars)'''
    dlocals = {}
    #FIXXXXXXXXXXXXXXXX
    #return {}

    _import_modules(imports, globals())

    dots = s.rsplit('.', 1)

    sym = None
    for i in range(1, len(dots)):
        s = '.'.join(dots[:i])
        if not s:
            continue
        try:
            try:
                if s.startswith('PyQt4.') and s.endswith(')'):
                    s = s[:s.rindex('(')]
                sym = eval(s, globals(), dlocals)
            except NameError:
                try:
                    sym = __import__(s, globals(), dlocals, [])
                except ImportError:
                    if s.find('(') != -1 and s[-1] == ')':
                        s = s[:s.index('(')]
                    sym = eval(s, globals(), dlocals)
                except AttributeError:
                    try:
                        sym = __import__(s, globals(), dlocals, [])
                    except ImportError:
                        pass
        except (AttributeError, NameError, TypeError, SyntaxError):
            return {}
    if sym is not None:
        var = s
        s = dots[-1]
        return get_completions_per_type(["%s.%s" % (var, k) for k in
            dir(sym) if k.startswith(s)])
    return {}


def _find_constructor(class_ob):
    # Given a class object, return a function object used for the
    # constructor (ie, __init__() ) or None if we can't find one.
    try:
        return class_ob.__init__.im_func
    except AttributeError:
        for base in class_ob.__bases__:
            rc = _find_constructor(base)
            if rc is not None:
                return rc
    return None
"""