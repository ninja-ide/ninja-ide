# -*- coding: utf-8 *-*

import time
import threading

from ninja_ide.tools.completion import model


__completion_daemon_instance = None
MODULES = {}
WAITING_BEFORE_START = 5


def CompletionDaemon():
    global __completion_daemon_instance
    if __completion_daemon_instance is None:
        __completion_daemon_instance = __CompletionDaemon()
        __completion_daemon_instance.start()
    __completion_daemon_instance.reference_counter += 1
    return __completion_daemon_instance


class __CompletionDaemon(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.lock = threading.Lock()
        self.event = threading.Event()
        self.unresolved_modules = {}
        self.keep_alive = True
        self.reference_counter = 0

    def run(self):
        global MODULES
        global WAITING_BEFORE_START
        time.sleep(WAITING_BEFORE_START)
        while self.keep_alive:
            if not self.unresolved_modules:
                self.event.wait()
            self.lock.acquire()
            for path in self.unresolved_modules:
                module = self.unresolved_modules[path]
                if module.need_resolution():
                    self._resolve_module(module)
                MODULES[path] = module
            self.unresolved_modules = {}
            self.lock.release()

    def _resolve_module(self, module):
        for attr in module.attributes:
            attribute = module.attributes[attr]
            for d in attribute.data:
                if d.data_type == model.late_resolution:
                    self._resolve_assign(attribute, module)

    def _resolve_assign(self, assign, module):
        self._resolve_with_imports(assign, module)

    def _resolve_with_imports(self, assign, module):
        for data in assign.data:
            line = data.line_content
            value = line.split('=')[1].strip().split('.')
            if value[0] in module.imports:
                value[0] = module.imports[value[0]].data_type
                resolve = '.'.join(value)
                data.data_type = resolve

    def inspect_module(self, path, module):
        self.lock.acquire()
        self.unresolved_modules[path] = module
        self.event.set()
        self.lock.release()

    def stop(self):
        self.reference_counter -= 1
        if self.reference_counter == 0:
            self.keep_alive = False
            if self.is_alive():
                self.join()

    def force_stop(self):
        self.keep_alive = False
        if self.is_alive():
            self.join()


def shutdown_daemon():
    daemon = CompletionDaemon()
    daemon.force_stop()
    global __completion_daemon_instance
    __completion_daemon_instance = None
