from projects_data import PROJECT_TYPES
from ide_settings_variables import TOOLBAR_ITEMS_PLUGINS
from editor_settings_variables import USE_PLATFORM_END_OF_LINE


###############################################################################
# FUNCTIONS
###############################################################################


def set_project_type_handler(project_type, project_type_handler):
    """Set a project type handler for the given project_type."""
    global PROJECT_TYPES
    PROJECT_TYPES[project_type] = project_type_handler


def get_project_type_handler(project_type):
    """Returns the handler for the given project_type."""
    global PROJECT_TYPES
    return PROJECT_TYPES.get(project_type)


def get_all_project_types():
    """Returns the availables project types."""
    global PROJECT_TYPES
    return list(PROJECT_TYPES.keys())


def add_toolbar_item_for_plugins(toolbar_action):
    """Add a toolbar action set from some plugin."""
    global TOOLBAR_ITEMS_PLUGINS
    TOOLBAR_ITEMS_PLUGINS.append(toolbar_action)


def get_toolbar_item_for_plugins():
    """Returns the toolbar actions set by plugins."""
    global TOOLBAR_ITEMS_PLUGINS
    return TOOLBAR_ITEMS_PLUGINS


def use_platform_specific_eol():
    """Returns the USE_PLATFORM_END_OF_LINE."""
    global USE_PLATFORM_END_OF_LINE
    return USE_PLATFORM_END_OF_LINE
