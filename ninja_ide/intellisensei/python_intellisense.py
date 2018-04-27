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

jedi_path = os.path.join(os.path.dirname(__file__))
sys.path.insert(0, jedi_path)
try:
    from ninja_ide.intellisensei import jedi
except ImportError:
    jedi = None
finally:
    sys.path.remove(jedi_path)
from ninja_ide.tools.logger import NinjaLogger

logger = NinjaLogger(__name__)
DEBUG = logger.debug


class JediService(intellisense_registry.IntelliSenseService):

    def __get_script(self, info):
        try:
            script = jedi.Script(
                source=info.get("source"),
                line=info["line"],
                column=info["column"],
                path=info.get("path", ""),
                sys_path=sys.path
            )
        except Exception as reason:
            DEBUG("Jedi error: '%s'" % reason)
        return script

    def get_completions(self, request):
        script = self.__get_script(request)
        completions = []
        for completion in script.completions():
            completions.append({
                "text": completion.name,
                "type": completion.type,
                "detail": completion.docstring()
            })

        return completions

    def get_definitions(self, request):
        script = self.__get_script(request)
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


JediService.register()
