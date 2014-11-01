# -*- coding: utf-8 -*-


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


"""Settings for Ninja-IDE."""


# imports
import datetime
import os

from ninja_ide import resources

from ide_settings_variables import LAST_CLEAN_LOCATOR


###############################################################################
# Locator Knowledge
###############################################################################


def should_clean_locator_knowledge():
    """Method to know if we should clean the knowledge or not."""
    value = None
    if LAST_CLEAN_LOCATOR is not None:
        delta = datetime.date.today() - LAST_CLEAN_LOCATOR
        if delta.days >= 10:
            value = datetime.date.today()
    elif LAST_CLEAN_LOCATOR is None:
        value = datetime.date.today()
    return value


def clean_locator_db(qsettings):
    """Clean Locator Knowledge."""
    last_clean = should_clean_locator_knowledge()
    if last_clean is not None:
        file_path = os.path.join(resources.NINJA_KNOWLEDGE_PATH, 'locator.db')
        if os.path.isfile(file_path):
            os.remove(file_path)
        qsettings.setValue("preferences/general/cleanLocator", last_clean)
