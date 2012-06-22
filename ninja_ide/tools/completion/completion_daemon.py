# -*- coding: utf-8 *-*

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
        __completion_daemon_instance.reference_counter += 1
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
            package, module, resolve = self.queue_receive.get()
            if package is None:
                continue
            self.lock.acquire()
            self.modules[package] = module
            self.lock.release()

    def _resolve_with_other_modules(self, module):
        pass

    def inspect_module(self, package, module):
        self.lock.acquire()
        self.modules[package] = module
        self.lock.release()
        self.queue_send.put((package, module))

    def get_module(self, package):
        return self.modules.get(package, None)

    def stop(self):
        self.reference_counter -= 1
        if self.reference_counter == 0:
            self.keep_alive = False
            self._shutdown_process()
            if self.is_alive():
                self.join()

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
            package, module = self.queue_receive.get()
            if package is None and module is None:
                break

            if module.need_resolution():
                self._resolve_module(module)
                self.first_iteration = False
                self._resolve_module(module)
            if module.need_resolution():
                self.queue_send.put((package, module, 1))
            else:
                self.queue_send.put((package, module, 0))

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
            if value[0] in module.imports:
                value[0] = module.imports[value[0]].data_type
                resolve = '.'.join(value)
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
        pass


def shutdown_daemon():
    daemon = CompletionDaemon()
    daemon.force_stop()
    global __completion_daemon_instance
    __completion_daemon_instance = None
