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

import os
import sys

from ninja_ide.intellisensei import intellisense_registry
from ninja_ide.tools.logger import NinjaLogger

jedi_path = os.path.join(os.path.dirname(__file__))
sys.path.insert(0, jedi_path)
try:
    from ninja_ide.intellisensei import jedi
except ImportError:
    jedi = None
finally:
    sys.path.remove(jedi_path)

logger = NinjaLogger(__name__)


class PythonProvider(intellisense_registry.Provider):

    def load(self):
        jedi.settings.case_insensitive_completion = False
        for module in ("PyQt4", "PyQt5", "numpy"):
            jedi.preload_module(module)

    def __get_script(self):
        info = self._code_info
        try:
            script = jedi.Script(
                source=info.source,
                line=info.line,
                column=info.col,
                path=info.path,
                sys_path=sys.path
            )
        except Exception as reason:
            logger.debug("Jedi error: '%s'" % reason)
        return script

    def completions(self):
        script = self.__get_script()
        completions = []
        append = completions.append
        for completion in script.completions():
            append({
                "text": completion.name,
                "type": completion.type,
                "detail": completion.docstring()
            })

        return completions

    def definitions(self):
        script = self.__get_script()
        func = getattr(script, "goto_assignments", None)
        _definitions = []
        if func is not None:
            definitions = func()
            for definition in definitions:
                if definition.type == "import":
                    definition = self._get_top_definitions(definition)
                _definitions.append({
                    "text": definition.name,
                    "filename": definition.module_path,
                    "line": definition.line,
                    "column": definition.column,
                })
        return _definitions

    def __get_top_definitions(self, definition):
        for _def in definition.goto_assignments():
            if _def == definition:
                continue
            if _def.type == "import":
                return self.__get_top_definitions(_def)
            return _def
        return definition

    def calltips(self):
        script = self.__get_script()
        signatures = script.call_signatures()
        results = {}
        for signature in signatures:
            name = signature.name
            if not name:
                continue
            results["signature.name"] = name
            results["signature.params"] = self._get_params(signature.params)
            results["signature.index"] = signature.index
        return results

    def _get_params(self, params):
        params_list = []
        for pos, param in enumerate(params):
            name = param.full_name
            if not name:
                continue
            if name == "self" and pos == 0:
                continue
            if not name.startswith("..."):
                name = name.split(".")[-1]
            params_list.append(name)
        return params_list


PythonProvider.register()

# class JediService(intellisense_registry.IntelliSenseService):

#     def __get_script(self):
#         info = self._code_info
#         try:
#             script = jedi.Script(
#                 source=info.get("source"),
#                 line=info["line"],
#                 column=info["column"],
#                 path=info.get("path", ""),
#                 sys_path=sys.path
#             )
#         except Exception as reason:
#             DEBUG("Jedi error: '%s'" % reason)
#         return script

#     def get_completions(self):
#         script = self.__get_script()
#         completions = []
#         for completion in script.completions():
#             completions.append({
#                 "text": completion.name,
#                 "type": completion.type,
#                 "detail": completion.docstring()
#             })

#         return completions

#     def get_signatures(self):
#         script = self.__get_script()
#         signatures = script.call_signatures()
#         results = {}
#         for signature in signatures:
#             name = signature.name
#             if not name:
#                 continue
#             results["signature.name"] = name
#             results["signature.params"] = self._get_params(signature.params)
#             results["signature.index"] = signature.index
#         return results

#     def _get_params(self, params):
#         params_list = []
#         for pos, param in enumerate(params):
#             name = param.full_name
#             if not name:
#                 continue
#             if name == "self" and pos == 0:
#                 continue
#             if not name.startswith("..."):
#                 name = name.split(".")[-1]
#             params_list.append(name)
#         return params_list

#     def get_definitions(self):
#         script = self.__get_script()
#         func = getattr(script, "goto_assignments", None)
#         _definitions = []
#         if func is not None:
#             definitions = func()
#             for definition in definitions:
#                 if definition.type == "import":
#                     definition = self._get_top_definitions(definition)

#                 _definitions.append({
#                     "text": definition.name,
#                     "filename": definition.module_path,
#                     "line": definition.line,
#                     "column": definition.column,
#                 })
#         return _definitions

#     def __get_top_definitions(self, definition):
#         for _def in definition.goto_assignments():
#             if _def == definition:
#                 continue
#             if _def.type == "import":
#                 return self.__get_top_definitions(_def)
#             return _def
#         return definition


# JediService.register()
