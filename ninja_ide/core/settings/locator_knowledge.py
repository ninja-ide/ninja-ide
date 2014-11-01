import datetime
import os

from ninja_ide import resources

from ide_settings_variables import LAST_CLEAN_LOCATOR


###############################################################################
# Locator Knowledge
###############################################################################


def should_clean_locator_knowledge():
    value = None
    if LAST_CLEAN_LOCATOR is not None:
        delta = datetime.date.today() - LAST_CLEAN_LOCATOR
        if delta.days >= 10:
            value = datetime.date.today()
    elif LAST_CLEAN_LOCATOR is None:
        value = datetime.date.today()
    return value


# Clean Locator Knowledge
def clean_locator_db(qsettings):
    last_clean = should_clean_locator_knowledge()
    if last_clean is not None:
        file_path = os.path.join(resources.NINJA_KNOWLEDGE_PATH, 'locator.db')
        if os.path.isfile(file_path):
            os.remove(file_path)
        qsettings.setValue("preferences/general/cleanLocator", last_clean)
