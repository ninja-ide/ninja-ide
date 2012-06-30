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

import time
from threading import Thread, Lock
from multiprocessing import Process, Queue

from ninja_ide.tools.completion import model
from ninja_ide.tools.completion import completer


__completion_daemon_instance = None
WAITING_BEFORE_START = 5


def CompletionDaemon():
    global __completion_daemon_instance
    if __completion_daemon_instance is None:
        __completion_daemon_instance = __CompletionDaemon()
        __completion_daemon_instance.start()
    return __completion_daemon_instance


class __CompletionDaemon(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.modules = {}
        self.reference_counter = 0
        self.keep_alive = True
        self.lock = Lock()
        self.queue_receive = Queue()
        self.queue_send = Queue()
        self.daemon = _DaemonProcess(self.queue_send, self.queue_receive)
        self.daemon.start()

    def run(self):
        global WAITING_BEFORE_START
        time.sleep(WAITING_BEFORE_START)
        while self.keep_alive:
            path_id, module, resolve = self.queue_receive.get()
            if path_id is None:
                continue
            self.lock.acquire()
            self.modules[path_id] = module
            self.lock.release()

    def _resolve_with_other_modules(self, module):
        pass

    def inspect_module(self, path_id, module):
        self.lock.acquire()
        self.modules[path_id] = module
        self.lock.release()
        self.queue_send.put((path_id, module))

    def get_module(self, path_id):
        return self.modules.get(path_id, None)

    def _shutdown_process(self):
        self.queue_send.put((None, None))
        self.daemon.terminate()
        self.queue_receive.put((None, None, None))

    def force_stop(self):
        self.keep_alive = False
        self._shutdown_process()
        if self.is_alive():
            self.join()


class _DaemonProcess(Process):

    def __init__(self, queue_receive, queue_send):
        super(_DaemonProcess, self).__init__()
        self.queue_receive = queue_receive
        self.queue_send = queue_send
        self.first_iteration = True

    def run(self):
        while True:
            self.first_iteration = True
            path_id, module = self.queue_receive.get()
            if path_id is None and module is None:
                break

            try:
                if module.need_resolution():
                    self._resolve_module(module)
                    self.first_iteration = False
                    self._resolve_module(module)
                else:
                    continue
                if module.need_resolution():
                    self.queue_send.put((path_id, module, 1))
                else:
                    self.queue_send.put((path_id, module, 0))
            except Exception, reason:
                # Try to not die whatever happend
                message = 'Daemon Fail with: %r', reason
                print(message)

    def _resolve_module(self, module):
        self._resolve_attributes(module, module)
        self._resolve_functions(module, module)
        for cla in module.classes:
            clazz = module.classes[cla]
            self._resolve_inheritance(clazz, module)
            self._resolve_attributes(clazz, module)
            self._resolve_functions(clazz, module)

    def _resolve_inheritance(self, clazz, module):
        for base in clazz.bases:
            name = base.split('.', 1)
            main_attr = name[0]
            child_attrs = ''
            if len(name) == 2:
                child_attrs = name[1]
            result = module.get_type(main_attr, child_attrs)
            data = model.late_resolution
            if result.get('found', True):
                data_type = module.imports[main_attr].get_data_type()
                if child_attrs:
                    child_attrs = '.%s' % child_attrs
                name = '%s%s().' % (data_type, child_attrs)
                imports = module.get_imports()
                imports = [imp.split('.')[0] for imp in imports]
                data = completer.get_all_completions(name, imports)
                data = (name, data)
            elif result.get('object', False).__class__ is model.Clazz:
                data = result['object']
            clazz.bases[base] = data
        clazz.update_with_parent_data()

    def _resolve_functions(self, structure, module):
        if structure.__class__ is model.Assign:
            return
        for func in structure.functions:
            function = structure.functions[func]
            self._resolve_attributes(function, module)
            self._resolve_functions(function, module)
            self._resolve_returns(function, module)

    def _resolve_returns(self, structure, module):
        if structure.__class__ is model.Assign:
            return
        self._resolve_types(structure.return_type, module, structure, 'return')

    def _resolve_attributes(self, structure, module):
        if structure.__class__ is model.Assign:
            return
        for attr in structure.attributes:
            assign = structure.attributes[attr]
            self._resolve_types(assign.data, module, assign)

    def _resolve_types(self, types, module, structure=None, split_by='='):
        if self.first_iteration:
            self._resolve_with_imports(types, module, split_by)
            self._resolve_with_local_names(types, module, split_by)
        else:
            self._resolve_with_local_vars(types, module, split_by, structure)

    def _resolve_with_imports(self, types, module, splitby):
        for data in types:
            if data.data_type != model.late_resolution:
                continue
            line = data.line_content
            value = line.split(splitby)[1].strip().split('.')
            name = value[0]
            extra = ''
            if name.find('(') != -1:
                extra = name[name.index('('):]
                name = name[:name.index('(')]
            if name in module.imports:
                value[0] = module.imports[name].data_type
                resolve = "%s%s" % ('.'.join(value), extra)
                data.data_type = resolve

    def _resolve_with_local_names(self, types, module, splitby):
        #TODO: resolve with functions returns
        for data in types:
            if data.data_type != model.late_resolution:
                continue
            line = data.line_content
            value = line.split(splitby)[1].split('(')[0].strip()
            if value in module.classes:
                clazz = module.classes[value]
                data.data_type = clazz

    def _resolve_with_local_vars(self, types, module, splitby, structure=None):
        for data in types:
            if data.data_type != model.late_resolution:
                continue
            line = data.line_content
            value = line.split(splitby)[1].split('(')[0].strip()
            sym = value.split('.')
            if len(sym) != 0:
                main_attr = sym[0]
                if len(sym) > 2:
                    child_attr = '.'.join(sym[1:])
                elif len(sym) == 2:
                    child_attr = sym[1]
                else:
                    child_attr = ''
                scope = []
                self._get_scope(structure, scope)
                if structure.__class__ is model.Assign:
                    scope.pop(0)
                scope.reverse()
                result = module.get_type(main_attr, child_attr, scope)
                data_type = model.late_resolution
                if isinstance(result['type'], basestring) and len(result) < 3:
                    if child_attr and \
                       structure.__class__ is not model.Function:
                        data_type = "%s.%s" % (result['type'], child_attr)
                    else:
                        data_type = result['type']
                elif result.get('object', False):
                    data_type = result['object']

                if data is not None:
                    data.data_type = data_type

    def _get_scope(self, structure, scope):
        if structure.__class__ not in (None, model.Module):
            scope.append(structure.name)
            self._get_scope(structure.parent, scope)


def shutdown_daemon():
    daemon = CompletionDaemon()
    daemon.force_stop()
    global __completion_daemon_instance
    __completion_daemon_instance = None
