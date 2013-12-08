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

from __future__ import absolute_import
from __future__ import unicode_literals

from PyQt4.QtCore import QObject
#from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import pyqtSignal

from ninja_ide.core import settings
from ninja_ide.core.file_handling import file_manager
from ninja_ide.core import plugin_util
from ninja_ide.gui.main_panel import itab_item
#from ninja_ide.gui.main_panel import main_container
#from ninja_ide.gui import actions
#from ninja_ide.gui.explorer import explorer_container


###############################################################################
# PLUGINS SERVICES
###############################################################################


class MainService(QObject):
    """
    Main Interact whith NINJA-IDE
    """
    # SIGNALS
    editorKeyPressEvent = pyqtSignal("QEvent")
    beforeFileSaved = pyqtSignal("QString")
    fileSaved = pyqtSignal("QString")
    currentTabChanged = pyqtSignal("QString")
    fileExecuted = pyqtSignal("QString")
    fileOpened = pyqtSignal("QString")

    def __init__(self):
        QObject.__init__(self)
        #self._main = main_container.MainContainer()
        #self._action = actions.Actions()
        #self._explorer = explorer_container.ExplorerContainer()
        #Connect signals
        #self.connect(self._main, SIGNAL("editorKeyPressEvent(QEvent)"),
            #self._keyPressEvent)
        #self.connect(self._main, SIGNAL("beforeFileSaved(QString)"),
            #self._beforeFileSaved)
        #self.connect(self._main, SIGNAL("fileSaved(QString)"),
            #self._fileSaved)
        #self.connect(self._main, SIGNAL("currentTabChanged(QString)"),
            #self._currentTabChanged)
        #self.connect(self._action, SIGNAL("fileExecuted(QString)"),
            #self._fileExecuted)
        #self.connect(self._main, SIGNAL("fileOpened(QString)"),
            #self._fileOpened)

###############################################################################
# Get main GUI Objects
###############################################################################

    def get_tab_manager(self):
        """
        Returns the TabWidget (ninja_ide.gui.main_panel.tab_widget.TabWidget)
        subclass of QTabWidget
        """
        return self._main.actualTab

###############################################################################
# END main GUI Objects
###############################################################################

    def add_menu(self, menu, lang=".py"):
        """
        Add an *extra context menu* to the editor context menu
        """
        itab_item.ITabItem.add_extra_menu(menu, lang=lang)

    def get_opened_documents(self):
        """
        Returns the opened documents
        """
        documents_data = self._main.get_opened_documents()
        #returns ONLY names!
        return [doc_data[0] for doc_list in documents_data
                    for doc_data in doc_list]

    def get_project_owner(self, editorWidget=None):
        """
        Return the project where this file belongs, or an empty string.
        """
        #if not editor try to get the current
        if editorWidget is None:
            editorWidget = self._main.get_current_editor()
        belongs = ''
        if editorWidget is None:
            return belongs
        #get the opened projects
        opened_projects_obj = self._explorer.get_opened_projects()
        for project in opened_projects_obj:
            if file_manager.belongs_to_folder(project.path, editorWidget.ID):
                belongs = project.path
                break
        return belongs

    def get_file_syntax(self, editorWidget=None):
        """Return the syntax for this file -> {}."""
        if editorWidget is None:
            editorWidget = self._main.get_current_editor()

        if editorWidget is not None:
            ext = file_manager.get_file_extension(editorWidget.ID)
            lang = settings.EXTENSIONS.get(ext, '')
            syntax = settings.SYNTAX.get(lang, {})
            return syntax
        return {}

    def add_editor(self, fileName="", content=None, syntax=None):
        """
        Create a new editor
        """
        editor = self._main.add_editor(fileName=fileName, syntax=syntax)
        if content:
            editor.setPlainText(content)
        return editor

    def get_editor(self):
        """
        Returns the actual editor (instance of ninja_ide.gui.editor.Editor)
        This method could return None
        """
        return self._main.get_current_editor()

    def get_editor_path(self):
        """
        Returns the actual editor path
        This method could return None if there is not an editor
        """
        editor = self._main.get_current_editor()
        if editor:
            return editor.ID
        return None

    def get_editor_encoding(self, editorWidget=None):
        """
        Returns the editor encoding
        """
        if editorWidget is None:
            editorWidget = self._main.get_current_editor()

        if editorWidget is not None:
            return editorWidget.encoding
        return None

    def get_text(self):
        """
        Returns the plain text of the current editor
        or None if thre is not an editor.
        """
        editor = self._main.get_current_editor()
        if editor:
            return editor.get_text()
        return

    def get_selected_text(self):
        """
        Returns the selected text of and editor.
        This method could return None
        """
        editor = self._main.get_current_editor()
        if editor:
            return editor.textCursor().selectedText()
        return None

    def insert_text(self, text):
        """
        Insert text in the current cursor position
        @text: string
        """
        editor = self._main.get_current_editor()
        if editor:
            editor.insertPlainText(text)

    def jump_to_line(self, lineno):
        """
        Jump to a specific line in the current editor
        """
        self._main.editor_jump_to_line(lineno=lineno)

    def get_lines_count(self):
        """
        Returns the count of lines in the current editor
        """
        editor = self._main.get_current_editor()
        if editor:
            return editor.get_lines_count()
        return None

    def save_file(self):
        """
        Save the actual file
        """
        self._main.save_file()

    def open_files(self, files, mainTab=True):
        """
        Open many files
        """
        self._main.open_files(self, files, mainTab=mainTab)

    def open_file(self, fileName='', cursorPosition=0,
                    positionIsLineNumber=False):
        """
        Open a single file, if the file is already open it get focus
        """
        self._main.open_file(filename=fileName, cursorPosition=cursorPosition,
                                positionIsLineNumber=positionIsLineNumber)

    def open_image(self, filename):
        """
        Open a single image
        """
        self._main.open_image(filename)

    def get_actual_tab(self):
        """
        Returns the actual widget
        """
        return self._main.get_actual_widget()

    # SIGNALS
    def _keyPressEvent(self, qEvent):
        """
        Emit the signal when a key is pressed
        @event: QEvent
        """
        self.editorKeyPressEvent.emit(qEvent)

    def _beforeFileSaved(self, fileName):
        """
        Signal emitted before save a file
        """
        self.beforeFileSaved.emit(fileName)

    def _fileSaved(self, fileName):
        """
        Signal emitted after save a file
        """
        fileName = fileName.split(":")[-1].strip()
        self.fileSaved.emit(fileName)

    def _currentTabChanged(self, fileName):
        """
        Signal emitted when the current tab changes
        """
        self.currentTabChanged.emit(fileName)

    def _fileExecuted(self, fileName):
        """
        Signal emitted when the file is executed
        """
        self.fileExecuted.emit(fileName)

    def _fileOpened(self, fileName):
        """
        Signal emitted when the file is opened
        """
        self.fileOpened.emit(fileName)


class ToolbarService(QObject):
    """
    Interact with the Toolbar
    """
    def __init__(self, toolbar):
        QObject.__init__(self)
        self._toolbar = toolbar

    def add_action(self, action):
        """
        Add an action to the Toolbar
        @action: Should be an instance(or subclass) of QAction
        """
        settings.add_toolbar_item_for_plugins(action)
        self._toolbar.addAction(action)


class MenuAppService(QObject):
    """
    Interact with the Plugins Menu
    """
    def __init__(self, plugins_menu):
        QObject.__init__(self)
        self._plugins_menu = plugins_menu

    def add_menu(self, menu):
        """
        Add an extra menu to the Plugin Menu of NINJA
        """
        self._plugins_menu.addMenu(menu)

    def add_action(self, action):
        """
        Add an action to the Plugin Menu of NINJA
        """
        self._plugins_menu.addAction(action)


#class ProjectTypeService(QObject):
#    """
#    Interact with the New Project Wizard
#    """
#    def __init__(self):
#        QObject.__init__(self)
#
#    def set_project_type_handler(self, project_type, project_type_handler):
#        """
#        Add a new Project Type and the handler for it
#        example:
#            foo_project_handler = FooProjectHandler(...)
#            set_project_type_handler('Foo Project', foo_project_handler)
#        Then 'Foo Project' will appear in the New Project wizard
#            and foo_project_handler instance controls the wizard
#
#        Note: project_type_handler SHOULD have a special interface see
#        ninja_ide.core.plugin_interfaces
#        """
#        settings.set_project_type_handler(project_type, project_type_handler)
#
#
#class TreeSymbolsService(QObject):
#    """
#    Interact with the symbols tree
#    """
#    def __init__(self):
#        QObject.__init__(self)
#
#    def set_symbols_handler(self, file_extension, symbols_handler):
#        """
#        Add a new Symbol's handler for the given file extension
#        example:
#            cpp_symbols_handler = CppSymbolHandler(...)
#            set_symbols_handler('cpp', cpp_symbols_handler)
#        Then all symbols in .cpp files will be handle by cpp_symbols_handler
#
#        Note: symbols_handler SHOULD have a special interface see
#        ninja_ide.core.plugin_interfaces
#        """
#        settings.set_symbols_handler(file_extension, symbols_handler)


class ExplorerService(QObject):
    # SIGNALS
    projectOpened = pyqtSignal("QString")
    projectExecuted = pyqtSignal("QString")

    def __init__(self):
        QObject.__init__(self)
        #self._explorer = explorer_container.ExplorerContainer()
        #self._action = actions.Actions()
        #self.connect(self._explorer, SIGNAL("projectOpened(QString)"),
            #self._projectOpened)
        #self.connect(self._action, SIGNAL("projectExecuted(QString)"),
            #self._projectExecuted)

    def get_tree_projects(self):
        """
        Returns the projects tree
        """
        return self._explorer._treeProjects

    def get_item(self, path):
        if self._explorer._treeProjects:
            return self._explorer._treeProjects.get_item_for_path(path)

    def get_current_project_item(self):
        """
        Returns the current item of the tree projects
        this method is a shortcut of self.get_tree_projects().currentItem()
        """
        if self._explorer._treeProjects:
            return self._explorer._treeProjects.currentItem()
        return None

    def get_project_item_by_name(self, projectName):
        """
        Return a ProjectItem that has the name provided.
        """
        if self._explorer._treeProjects:
            return self._explorer._treeProjects.get_project_by_name(
                projectName)
        return None

    def get_tree_symbols(self):
        """
        Returns the symbols tree
        """
        return self._explorer._treeSymbols

    def set_symbols_handler(self, file_extension, symbols_handler):
        """
        Add a new Symbol's handler for the given file extension
        example:
            cpp_symbols_handler = CppSymbolHandler(...)
            set_symbols_handler('cpp', cpp_symbols_handler)
        Then all symbols in .cpp files will be handle by cpp_symbols_handler

        Note: symbols_handler SHOULD have a special interface see
        ninja_ide.core.plugin_interfaces
        """
        settings.set_symbols_handler(file_extension, symbols_handler)

    def set_project_type_handler(self, project_type, project_type_handler):
        """
        Add a new Project Type and the handler for it
        example:
            foo_project_handler = FooProjectHandler(...)
            set_project_type_handler('Foo Project', foo_project_handler)
        Then 'Foo Project' will appear in the New Project wizard
            and foo_project_handler instance controls the wizard

        Note: project_type_handler SHOULD have a special interface see
        ninja_ide.core.plugin_interfaces
        """
        settings.set_project_type_handler(project_type, project_type_handler)

    def add_tab(self, tab, title):
        """
        Add a tab with the given title
        @tab: Should be an instance (or subclass )of QTabWidget
        @title: Name of the tab string
        """
        self._explorer.addTab(tab, title)

    def get_actual_project(self):
        """
        Returns the path of the opened projects
        """
        return self._explorer.get_actual_project()

    def get_opened_projects(self):
        """
        Return the opened projects in the Tree Project Explorer.
        list of <ninja_ide.gui.explorer.tree_projects_widget.ProjectTree>
        """
        opened_projects = self._explorer.get_opened_projects()
        return opened_projects

    def add_project_menu(self, menu, lang='all'):
        """
        Add an extra menu to the project explorer for the files
        with the given extension.
        @lang: String with file extension format (py, php, json)
        """
        if self._explorer._treeProjects:
            self._explorer._treeProjects.add_extra_menu(menu, lang=lang)

    def add_project_menu_by_scope(self, menu, scope=None):
        """
        Add an extra menu to the project explorer to the specific scope
        @scope: String with the menu scope (all, project, folder, file)
        """
        if scope is None:
            #default behavior show ALL
            scope = plugin_util.ContextMenuScope(project=True, folder=True,
                files=True)
        if self._explorer._treeProjects:
            self._explorer._treeProjects.add_extra_menu_by_scope(menu, scope)

    # SIGNALS
    def _projectOpened(self, projectPath):
        """
        Signal emitted when the project is opened
        """
        self.projectOpened.emit(projectPath)

    def _projectExecuted(self, projectPath):
        """
        Signal emitted when the project is executed
        """
        self.projectExecuted.emit(projectPath)
