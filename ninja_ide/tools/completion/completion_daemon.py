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
                # Don't die whatever happend
                message = 'Daemon Fail with: %r', reason
                print(message)

    def _resolve_module(self, module):
        self._resolve_attributes(module, module)
        self._resolve_functions(module, module)
        for cla in module.classes:
            clazz = module.classes[cla]
            self._resolve_attributes(clazz, module)
            self._resolve_functions(clazz, module)

    def _resolve_functions(self, structure, module):
        for func in structure.functions:
            function = structure.functions[func]
            self._resolve_attributes(function, module)
            self._resolve_functions(function, module)

    def _resolve_attributes(self, structure, module):
        for attr in structure.attributes:
            attribute = structure.attributes[attr]
            for d in attribute.data:
                if d.data_type == model.late_resolution:
                    self._resolve_assign(attribute, module)

    def _resolve_assign(self, assign, module):
        if self.first_iteration:
            self._resolve_with_imports(assign, module)
            self._resolve_with_local_names(assign, module)
        else:
            self._resolve_with_local_vars(assign, module)

    def _resolve_with_imports(self, assign, module):
        for data in assign.data:
            line = data.line_content
            value = line.split('=')[1].strip().split('.')
            name = value[0]
            extra = ''
            if name.find('(') != -1:
                extra = name[name.index('('):]
                name = name[:name.index('(')]
            if name in module.imports:
                value[0] = module.imports[name].data_type
                resolve = "%s%s" % ('.'.join(value), extra)
                data.data_type = resolve

    def _resolve_with_local_names(self, assign, module):
        #TODO: resolve with functions returns
        for data in assign.data:
            line = data.line_content
            value = line.split('=')[1].split('(')[0].strip()
            if value in module.classes:
                clazz = module.classes[value]
                data.data_type = clazz

    def _resolve_with_local_vars(self, assign, module):
        for data in assign.data:
            line = data.line_content
            value = line.split('=')[1].split('(')[0].strip()
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
                self._get_scope(assign, scope)
                scope.pop(0)
                scope.reverse()
                result = module.get_type(main_attr, child_attr, scope)
                data_type = model.late_resolution
                if isinstance(result[1], basestring):
                    if child_attr:
                        data_type = "%s.%s" % (result[1], child_attr)
                    else:
                        data_type = result[1]
                elif result[1] is not None:
                    data_type = result[1]

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
