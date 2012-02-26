# -*- coding: utf-8 -*-
from __future__ import absolute_import

import re
import webbrowser

from PyQt4.QtCore import QObject
from PyQt4.QtCore import QSettings
from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QInputDialog
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QShortcut

from ninja_ide.core import file_manager
from ninja_ide.core import settings
from ninja_ide import resources
from ninja_ide.tools import ui_tools
from ninja_ide.tools import locator
from ninja_ide.tools import json_manager
from ninja_ide.gui.editor import editor
from ninja_ide.gui.editor import helpers
from ninja_ide.gui.dialogs import from_import_dialog
from ninja_ide.gui.main_panel import class_diagram
from ninja_ide.gui.main_panel import tab_group


__actionsInstance = None


# Actions Singleton
def Actions(*args, **kw):
    global __actionsInstance
    if __actionsInstance is None:
        __actionsInstance = __Actions(*args, **kw)
    return __actionsInstance


class __Actions(QObject):

    """This class is like the Sauron's Ring:
    One ring to rule them all, One ring to find them,
    One ring to bring them all and in the darkness bind them.

    This Class knows all the containers, and its know by all the containers,
    but the containers don't need to know between each other, in this way we
    can keep a better api without the need to tie the behaviour between
    the widgets, and let them just consume the 'actions' they need."""

    def __init__(self):
        QObject.__init__(self)
        #Definition Locator
        self._locator = locator.Locator()
        self.__codeBack = []
        self.__codeForward = []
        self.__bookmarksFile = ''
        self.__bookmarksPos = -1
        self.__breakpointsFile = ''
        self.__breakpointsPos = -1
        self.__operations = {
            0: self._navigate_code_jumps,
            1: self._navigate_bookmarks,
            2: self._navigate_breakpoints}

    def install_shortcuts(self, ide):
        """Install the shortcuts to the IDE."""
        self.ide = ide
        short = resources.get_shortcut
        self.shortChangeTab = QShortcut(short("Change-Tab"), self.ide)
        self.shortChangeTabReverse = QShortcut(
            short("Change-Tab-Reverse"), self.ide)
        self.shortDuplicate = QShortcut(short("Duplicate"), self.ide)
        self.shortRemove = QShortcut(short("Remove-line"), self.ide)
        self.shortMoveUp = QShortcut(short("Move-up"), self.ide)
        self.shortMoveDown = QShortcut(short("Move-down"), self.ide)
        self.shortCloseTab = QShortcut(short("Close-tab"), self.ide)
        self.shortNew = QShortcut(short("New-file"), self.ide)
        self.shortNewProject = QShortcut(short("New-project"), self.ide)
        self.shortOpen = QShortcut(short("Open-file"), self.ide)
        self.shortOpenProject = QShortcut(short("Open-project"), self.ide)
        self.shortSave = QShortcut(short("Save-file"), self.ide)
        self.shortSaveProject = QShortcut(short("Save-project"), self.ide)
        self.shortPrint = QShortcut(short("Print-file"), self.ide)
        self.shortRedo = QShortcut(short("Redo"), self.ide)
        self.shortAddBookmark = QShortcut(short("Add-Bookmark-or-Breakpoint"),
            self.ide)
        self.shortComment = QShortcut(short("Comment"), self.ide)
        self.shortUncomment = QShortcut(short("Uncomment"), self.ide)
        self.shortHorizontalLine = QShortcut(short("Horizontal-line"),
            self.ide)
        self.shortTitleComment = QShortcut(short("Title-comment"), self.ide)
        self.shortIndentLess = QShortcut(short("Indent-less"), self.ide)
        self.shortHideMisc = QShortcut(short("Hide-misc"), self.ide)
        self.shortHideEditor = QShortcut(short("Hide-editor"), self.ide)
        self.shortHideExplorer = QShortcut(short("Hide-explorer"), self.ide)
        self.shortRunFile = QShortcut(short("Run-file"), self.ide)
        self.shortRunProject = QShortcut(short("Run-project"), self.ide)
        self.shortStopExecution = QShortcut(short("Stop-execution"), self.ide)
        self.shortHideAll = QShortcut(short("Hide-all"), self.ide)
        self.shortFullscreen = QShortcut(short("Full-screen"), self.ide)
        self.shortFind = QShortcut(short("Find"), self.ide)
        self.shortFindReplace = QShortcut(short("Find-replace"), self.ide)
        self.shortFindWithWord = QShortcut(short("Find-with-word"), self.ide)
        self.shortHelp = QShortcut(short("Help"), self.ide)
        self.shortSplitHorizontal = QShortcut(short("Split-horizontal"),
            self.ide)
        self.shortSplitVertical = QShortcut(short("Split-vertical"), self.ide)
        self.shortFollowMode = QShortcut(short("Follow-mode"), self.ide)
        self.shortReloadFile = QShortcut(short("Reload-file"), self.ide)
        self.shortJump = QShortcut(short("Jump"), self.ide)
        self.shortFindInFiles = QShortcut(short("Find-in-files"), self.ide)
        self.shortImport = QShortcut(short("Import"), self.ide)
        self.shortGoToDefinition = QShortcut(short("Go-to-definition"),
            self.ide)
        self.shortCompleteDeclarations = QShortcut(
            short("Complete-Declarations"), self.ide)
        self.shortCodeLocator = QShortcut(short("Code-locator"), self.ide)
        self.shortFileOpener = QShortcut(short("File-Opener"), self.ide)
        self.shortNavigateBack = QShortcut(short("Navigate-back"), self.ide)
        self.shortNavigateForward = QShortcut(short("Navigate-forward"),
            self.ide)
        self.shortOpenLastTabOpened = QShortcut(short("Open-recent-closed"),
            self.ide)
        self.shortShowCodeNav = QShortcut(short("Show-Code-Nav"), self.ide)
        self.shortShowBookmarksNav = QShortcut(short("Show-Bookmarks-Nav"),
            self.ide)
        self.shortShowBreakpointsNav = QShortcut(short("Show-Breakpoints-Nav"),
            self.ide)
        self.shortShowPasteHistory = QShortcut(short("Show-Paste-History"),
            self.ide)
        self.shortPasteHistory = QShortcut(short("History-Paste"), self.ide)
        self.shortCopyHistory = QShortcut(short("History-Copy"), self.ide)
        self.shortHighlightWord = QShortcut(short("Highlight-Word"), self.ide)

        #Connect Shortcuts Signals
        self.connect(self.shortNavigateBack, SIGNAL("activated()"),
            lambda: self.__navigate_with_keyboard(False))
        self.connect(self.shortNavigateForward, SIGNAL("activated()"),
            lambda: self.__navigate_with_keyboard(True))
        self.connect(self.shortCodeLocator, SIGNAL("activated()"),
            self.ide.status.show_locator)
        self.connect(self.shortFileOpener, SIGNAL("activated()"),
            self.ide.status.show_file_opener)
        self.connect(self.shortGoToDefinition, SIGNAL("activated()"),
            self.editor_go_to_definition)
        self.connect(self.shortCompleteDeclarations, SIGNAL("activated()"),
            self.editor_complete_declaration)
        self.connect(self.shortRedo, SIGNAL("activated()"),
            self.editor_redo)
        self.connect(self.shortHorizontalLine, SIGNAL("activated()"),
            self.editor_insert_horizontal_line)
        self.connect(self.shortTitleComment, SIGNAL("activated()"),
            self.editor_insert_title_comment)
        self.connect(self.shortFollowMode, SIGNAL("activated()"),
            self.ide.mainContainer.show_follow_mode)
        self.connect(self.shortReloadFile, SIGNAL("activated()"),
            self.ide.mainContainer.reload_file)
        self.connect(self.shortSplitHorizontal, SIGNAL("activated()"),
            lambda: self.ide.mainContainer.split_tab(True))
        self.connect(self.shortSplitVertical, SIGNAL("activated()"),
            lambda: self.ide.mainContainer.split_tab(False))
        self.connect(self.shortNew, SIGNAL("activated()"),
            self.ide.mainContainer.add_editor)
        self.connect(self.shortNewProject, SIGNAL("activated()"),
            self.ide.explorer.create_new_project)
        self.connect(self.shortHideMisc, SIGNAL("activated()"),
            self.ide.central.change_misc_visibility)
        self.connect(self.shortHideEditor, SIGNAL("activated()"),
            self.ide.central.change_main_visibility)
        self.connect(self.shortHideExplorer, SIGNAL("activated()"),
            self.ide.central.change_explorer_visibility)
        self.connect(self.shortHideAll, SIGNAL("activated()"),
            self.hide_all)
        self.connect(self.shortJump, SIGNAL("activated()"),
            self.ide.mainContainer.editor_jump_to_line)
        self.connect(self.shortFullscreen, SIGNAL("activated()"),
            self.fullscreen_mode)
        self.connect(self.shortOpen, SIGNAL("activated()"),
            self.ide.mainContainer.open_file)
        self.connect(self.shortOpenProject, SIGNAL("activated()"),
            self.open_project)
        self.connect(self.shortCloseTab, SIGNAL("activated()"),
            self.ide.mainContainer.actualTab.close_tab)
        self.connect(self.shortSave, SIGNAL("activated()"),
            self.ide.mainContainer.save_file)
        self.connect(self.shortSaveProject, SIGNAL("activated()"),
            self.save_project)
        self.connect(self.shortPrint, SIGNAL("activated()"),
            self.print_file)
        self.connect(self.shortFind, SIGNAL("activated()"),
            self.ide.status.show)
        self.connect(self.shortFindWithWord, SIGNAL("activated()"),
            self.ide.status.show_with_word)
        self.connect(self.shortFindReplace, SIGNAL("activated()"),
            self.ide.status.show_replace)
        self.connect(self.shortRunFile, SIGNAL("activated()"),
            self.execute_file)
        self.connect(self.shortRunProject, SIGNAL("activated()"),
            self.execute_project)
        self.connect(self.shortStopExecution, SIGNAL("activated()"),
            self.kill_execution)
        self.connect(self.shortIndentLess, SIGNAL("activated()"),
            self.editor_indent_less)
        self.connect(self.shortComment, SIGNAL("activated()"),
            self.editor_comment)
        self.connect(self.shortUncomment, SIGNAL("activated()"),
            self.editor_uncomment)
        self.connect(self.shortHelp, SIGNAL("activated()"),
            self.ide.mainContainer.show_python_doc)
        self.connect(self.shortImport, SIGNAL("activated()"),
            self.import_from_everywhere)
        self.connect(self.shortFindInFiles, SIGNAL("activated()"),
            self.ide.misc.show_find_in_files_widget)
        self.connect(self.shortMoveUp, SIGNAL("activated()"),
            self.editor_move_up)
        self.connect(self.shortMoveDown, SIGNAL("activated()"),
            self.editor_move_down)
        self.connect(self.shortRemove, SIGNAL("activated()"),
            self.editor_remove_line)
        self.connect(self.shortDuplicate, SIGNAL("activated()"),
            self.editor_duplicate)
        self.connect(self.shortOpenLastTabOpened, SIGNAL("activated()"),
            self.reopen_last_tab)
        self.connect(self.shortChangeTab, SIGNAL("activated()"),
            self.ide.mainContainer.actualTab.change_tab)
        self.connect(self.shortChangeTabReverse, SIGNAL("activated()"),
            self.ide.mainContainer.actualTab.change_tab_reverse)
        self.connect(self.shortShowCodeNav, SIGNAL("activated()"),
            self.ide.mainContainer.actualTab.navigator._show_code_nav)
        self.connect(self.shortShowBookmarksNav, SIGNAL("activated()"),
            self.ide.mainContainer.actualTab.navigator._show_bookmarks)
        self.connect(self.shortShowBreakpointsNav, SIGNAL("activated()"),
            self.ide.mainContainer.actualTab.navigator._show_breakpoints)
        self.connect(self.shortAddBookmark, SIGNAL("activated()"),
            self._add_bookmark_breakpoint)
        self.connect(self.shortShowPasteHistory, SIGNAL("activated()"),
            self.ide.central.lateralPanel.combo.showPopup)
        self.connect(self.shortCopyHistory, SIGNAL("activated()"),
            self._copy_history)
        self.connect(self.shortPasteHistory, SIGNAL("activated()"),
            self._paste_history)
        self.connect(self.shortHighlightWord, SIGNAL("activated()"),
            self.editor_highlight_word)

        #Connect SIGNALs from other objects
        self.connect(self.ide.mainContainer._tabMain,
            SIGNAL("runFile()"), self.execute_file)
        self.connect(self.ide.mainContainer._tabSecondary,
            SIGNAL("runFile()"), self.execute_file)
        self.connect(self.ide.mainContainer._tabMain,
            SIGNAL("addToProject(QString)"), self._add_file_to_project)
        self.connect(self.ide.mainContainer._tabSecondary,
            SIGNAL("addToProject(QString)"), self._add_file_to_project)
        self.connect(self.ide.mainContainer,
            SIGNAL("openProject(QString)"), self.open_project)

    def update_shortcuts(self):
        """If the user update the key binded to any shortcut, update them."""
        resources.load_shortcuts()
        short = resources.get_shortcut
        self.shortDuplicate.setKey(short("Duplicate"))
        self.shortRemove.setKey(short("Remove-line"))
        self.shortMoveUp.setKey(short("Move-up"))
        self.shortMoveDown.setKey(short("Move-down"))
        self.shortCloseTab.setKey(short("Close-tab"))
        self.shortNew.setKey(short("New-file"))
        self.shortNewProject.setKey(short("New-project"))
        self.shortOpen.setKey(short("Open-file"))
        self.shortOpenProject.setKey(short("Open-project"))
        self.shortSave.setKey(short("Save-file"))
        self.shortSaveProject.setKey(short("Save-project"))
        self.shortPrint.setKey(short("Print-file"))
        self.shortRedo.setKey(short("Redo"))
        self.shortComment.setKey(short("Comment"))
        self.shortHorizontalLine.setKey(short("Horizontal-line"))
        self.shortTitleComment.setKey(short("Title-comment"))
        self.shortIndentLess.setKey(short("Indent-less"))
        self.shortHideMisc.setKey(short("Hide-misc"))
        self.shortHideEditor.setKey(short("Hide-editor"))
        self.shortHideExplorer.setKey(short("Hide-explorer"))
        self.shortRunFile.setKey(short("Run-file"))
        self.shortRunProject.setKey(short("Run-project"))
        self.shortStopExecution.setKey(short("Stop-execution"))
        self.shortHideAll.setKey(short("Hide-all"))
        self.shortFullscreen.setKey(short("Full-screen"))
        self.shortFind.setKey(short("Find"))
        self.shortFindReplace.setKey(short("Find-replace"))
        self.shortFindWithWord.setKey(short("Find-with-word"))
        self.shortHelp.setKey(short("Help"))
        self.shortSplitHorizontal.setKey(short("Split-horizontal"))
        self.shortSplitVertical.setKey(short("Split-vertical"))
        self.shortFollowMode.setKey(short("Follow-mode"))
        self.shortReloadFile.setKey(short("Reload-file"))
        self.shortJump.setKey(short("Jump"))
        self.shortFindInFiles.setKey(short("Find-in-files"))
        self.shortImport.setKey(short("Import"))
        self.shortGoToDefinition.setKey(short("Go-to-definition"))
        self.shortCodeLocator.setKey(short("Code-locator"))
        self.shortNavigateBack.setKey(short("Navigate-back"))
        self.shortNavigateForward.setKey(short("Navigate-forward"))
        self.shortOpenLastTabOpened.setKey(short("Open-recent-closed"))
        self.shortChangeTab.setKey(short("Change-Tab"))
        self.shortChangeTabReverse.setKey(short("Change-Tab-Reverse"))
        self.shortAddBookmark.setKey(short("Add-Bookmark-or-Breakpoint"))
        self.shortShowCodeNav.setKey(short("Show-Code-Nav"))
        self.shortShowBookmarksNav.setKey(short("Show-Bookmarks-Nav"))
        self.shortShowBreakpointsNav.setKey(short("Show-Breakpoints-Nav"))
        self.shortShowPasteHistory.setKey(short("Show-Paste-History"))

    def _copy_history(self):
        """Copy the selected text into the copy/paste history."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget:
            cursor = editorWidget.textCursor()
            copy = cursor.selectedText()
            self.ide.central.lateralPanel.add_new_copy(copy)

    def _paste_history(self):
        """Paste the text from the copy/paste history."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget:
            cursor = editorWidget.textCursor()
            paste = self.ide.central.lateralPanel.get_paste()
            cursor.insertText(paste)

    def _add_bookmark_breakpoint(self):
        """Add a bookmark or breakpoint to the current file in the editor."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget:
            if self.ide.mainContainer.actualTab.navigator.operation == 1:
                editorWidget._sidebarWidget.set_bookmark(
                    editorWidget.textCursor().blockNumber())
            elif self.ide.mainContainer.actualTab.navigator.operation == 2:
                editorWidget._sidebarWidget.set_breakpoint(
                    editorWidget.textCursor().blockNumber())

    def __navigate_with_keyboard(self, val):
        """Navigate between the positions in the jump history stack."""
        op = self.ide.mainContainer._tabMain.navigator.operation
        self.navigate_code_history(val, op)

    def _add_file_to_project(self, path):
        """Add the file for 'path' in the project the user choose here."""
        pathProject = [self.ide.explorer.get_actual_project()]
        addToProject = ui_tools.AddToProject(pathProject, self.ide)
        addToProject.exec_()
        if not addToProject.pathSelected:
            return
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if not editorWidget.ID:
            name = unicode(QInputDialog.getText(None,
                self.tr("Add File To Project"), self.tr("File Name:"))[0])
            if not name:
                QMessageBox.information(self, self.tr("Invalid Name"),
                    self.tr("The file name is empty, please enter a name"))
                return
        else:
            name = file_manager.get_basename(editorWidget.ID)
        path = file_manager.create_path(
            unicode(addToProject.pathSelected), name)
        try:
            path = file_manager.store_file_content(
                path, editorWidget.get_text(), newFile=True)
            editorWidget.ID = path
            self.ide.explorer.add_existing_file(path)
            self.ide.change_window_title(path)
            name = file_manager.get_basename(path)
            self.ide.mainContainer.actualTab.setTabText(
                self.ide.mainContainer.actualTab.currentIndex(), name)
            editorWidget._file_saved()
        except file_manager.NinjaFileExistsException, ex:
            QMessageBox.information(self, self.tr("File Already Exists"),
                self.tr("Invalid Path: the file '%s' already exists." % \
                    ex.filename))

    def add_project_to_console(self, projectFolder):
        """Add the namespace of the project received into the ninja-console."""
        self.ide.misc._console.load_project_into_console(projectFolder)

    def remove_project_from_console(self, projectFolder):
        """Remove the namespace of the project received from the console."""
        self.ide.misc._console.unload_project_from_console(projectFolder)

    def import_from_everywhere(self):
        """Show the dialog to insert an import from any place in the editor."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget:
            text = unicode(editorWidget.get_text())
            froms = re.findall('^from (.*)', text, re.MULTILINE)
            fromSection = list(set([f.split(' import')[0] for f in froms]))
            dialog = from_import_dialog.FromImportDialog(fromSection,
                editorWidget, self.ide)
            dialog.show()

    def open_project(self, path=''):
        """Open a Project and load the symbols in the Code Locator."""
        self.ide.explorer.open_project_folder(unicode(path))
        self.ide.status.explore_code()

    def create_profile(self):
        """Create a profile binding files and projects to a key."""
        profileInfo = QInputDialog.getText(None,
            self.tr("Create Profile"), self.tr(
                "The Current Files and Projects will "
                "be associated to this profile.\n"
                "Profile Name:"))
        if profileInfo[1]:
            profileName = unicode(profileInfo[0])
            if not profileName or profileName in settings.PROFILES:
                QMessageBox.information(self, self.tr("Profile Name Invalid"),
                    self.tr("The Profile name is invalid or already exists."))
                return
            self.save_profile(profileName)
            return profileName

    def save_profile(self, profileName):
        """Save the updates from a profile."""
        projects_obj = self.ide.explorer.get_opened_projects()
        projects = [p.path for p in projects_obj]
        files = self.ide.mainContainer.get_opened_documents()
        files = files[0] + files[1]
        settings.PROFILES[profileName] = [files, projects]
        qsettings = QSettings()
        qsettings.setValue('ide/profiles', settings.PROFILES)

    def activate_profile(self):
        """Show the Profile Manager dialog."""
        profilesLoader = ui_tools.ProfilesLoader(self._load_profile_data,
            self.create_profile, self.save_profile,
            settings.PROFILES, self.ide)
        profilesLoader.show()

    def deactivate_profile(self):
        """Close the Profile Session."""
        self.ide.Profile = None

    def _load_profile_data(self, key):
        """Activate the selected profile, closing the current files/projects"""
        self.ide.explorer.close_opened_projects()
        self.ide.mainContainer.open_files(settings.PROFILES[key][0])
        self.ide.explorer.open_session_projects(settings.PROFILES[key][1])
        self.ide.status.explore_code()

    def close_files_from_project(self, project):
        """Close the files related to this project."""
        project = unicode(project)
        if project:
            tabMain = self.ide.mainContainer._tabMain
            for tabIndex in reversed(xrange(tabMain.count())):
                if file_manager.belongs_to_folder(
                project, tabMain.widget(tabIndex).ID):
                    tabMain.removeTab(tabIndex)

            tabSecondary = self.ide.mainContainer._tabSecondary
            for tabIndex in reversed(xrange(tabSecondary.count())):
                if file_manager.belongs_to_folder(
                project, tabSecondary.widget(tabIndex).ID):
                    tabSecondary.removeTab(tabIndex)
            self.ide.profile = None

    def count_file_code_lines(self):
        """Count the lines of code in the current file."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget:
            blanks = re.findall('(^\n)|(^(\s+)?#)|(^( +)?($|\n))',
                unicode(editorWidget.get_text()), re.M)
            resume = self.tr("Lines code: %1\n").arg(
                editorWidget.blockCount() - len(blanks))
            resume += self.tr("Blanks and commented lines: %1\n\n").arg(
                len(blanks))
            resume += self.tr("Total lines: %1").arg(editorWidget.blockCount())
            msgBox = QMessageBox(QMessageBox.Information,
                self.tr("Summary of lines"), resume,
                QMessageBox.Ok, editorWidget)
            msgBox.exec_()

    def execute_file(self):
        """Execute the current file."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        #emit a signal for plugin!
        self.emit(SIGNAL("fileExecuted(QString)"), editorWidget.ID)
        if editorWidget:
            if not editorWidget.ID:
                self.ide.mainContainer.save_file()
            ext = file_manager.get_file_extension(editorWidget.ID)
            #TODO: Remove the IF statment with polymorphism using Handler
            if ext == 'py':
                self.ide.misc.run_application(editorWidget.ID)
            elif ext == 'html':
                self.ide.misc.render_web_page(editorWidget.ID)

    def execute_project(self):
        """Execute the project marked as Main Project."""
        mainFile = self.ide.explorer.get_project_main_file()
        if not mainFile and self.ide.explorer._treeProjects and \
          self.ide.explorer._treeProjects._actualProject:
            self.ide.explorer._treeProjects.open_project_properties()
        elif mainFile:
            self.save_project()
            path = self.ide.explorer.get_actual_project()
            #emit a signal for plugin!
            self.emit(SIGNAL("projectExecuted(QString)"), path)
            project = json_manager.read_ninja_project(path)
            venv = project.get('venv', False)
            params = project.get('programParams', '')
            preExec = project.get('preExecScript', '')
            postExec = project.get('postExecScript', '')
            mainFile = file_manager.create_path(path, mainFile)
            self.ide.misc.run_application(mainFile, pythonPath=venv,
                programParams=params, preExec=preExec, postExec=postExec)

    def kill_execution(self):
        """Kill the execution of the current file or project."""
        self.ide.misc.kill_application()

    def fullscreen_mode(self):
        """Change to fullscreen mode."""
        if self.ide.isFullScreen():
            self.ide.showMaximized()
        else:
            self.ide.showFullScreen()

    def editor_redo(self):
        """Execute the redo action in the current editor."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget:
            editorWidget.redo()

    def editor_indent_less(self):
        """Indent 1 position to the left for the current line or selection."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget:
            editorWidget.indent_less()

    def editor_indent_more(self):
        """Indent 1 position to the right for the current line or selection."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget:
            editorWidget.indent_more()

    def editor_comment(self):
        """Mark the current line or selection as a comment."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget:
            helpers.comment(editorWidget)

    def editor_uncomment(self):
        """Uncomment the current line or selection."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget:
            helpers.uncomment(editorWidget)

    def editor_insert_horizontal_line(self):
        """Insert an horizontal lines of comment symbols."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget:
            helpers.insert_horizontal_line(editorWidget)

    def editor_insert_title_comment(self):
        """Insert a Title surrounded by comment symbols."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget:
            helpers.insert_title_comment(editorWidget)

    def editor_remove_trailing_spaces(self):
        """Remove the trailing spaces in the current editor."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget:
            helpers.remove_trailing_spaces(editorWidget)

    def editor_replace_tabs_with_spaces(self):
        """Replace the Tabs with Spaces in the current editor."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget:
            helpers.replace_tabs_with_spaces(editorWidget)

    def editor_move_up(self):
        """Move the current line or selection one position up."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget:
            helpers.move_up(editorWidget)

    def editor_move_down(self):
        """Move the current line or selection one position down."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget:
            helpers.move_down(editorWidget)

    def editor_remove_line(self):
        """Remove the current line or selection."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget:
            helpers.remove_line(editorWidget)

    def editor_duplicate(self):
        """Duplicate the current line or selection."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget:
            helpers.duplicate(editorWidget)

    def editor_go_to_definition(self):
        """Search the definition of the method or variable under the cursor.

        If more than one method or variable is found with the same name,
        shows a table with the results and let the user decide where to go."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget:
            editorWidget.go_to_definition()

    def editor_highlight_word(self):
        """Highlight the occurrences of the current word in the editor."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget:
            editorWidget.highlight_selected_word()

    def editor_complete_declaration(self):
        """Do the opposite action that Complete Declaration expect."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget:
            editorWidget.complete_declaration()

    def editor_go_to_line(self, line):
        """Jump to the specified line in the current editor."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget:
            editorWidget.jump_to_line(line)

    def reset_editor_flags(self):
        """Reset the Flags for all the opened editors."""
        self.ide.mainContainer.reset_editor_flags()

    def preview_in_browser(self):
        """Load the current html file in the default browser."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget:
            if not editorWidget.ID:
                self.ide.mainContainer.save_file()
            ext = file_manager.get_file_extension(editorWidget.ID)
            if ext == 'html':
                webbrowser.open(editorWidget.ID)

    def hide_all(self):
        """Hide/Show all the containers except the editor."""
        if self.ide.menuBar().isVisible():
            self.ide.central.lateralPanel.hide()
            self.ide.misc.hide()
            self.ide.toolbar.hide()
            self.ide.menuBar().hide()
        else:
            self.ide.central.lateralPanel.show()
            self.ide.toolbar.show()
            self.ide.menuBar().show()

    def save_project(self):
        """Save all the opened files that belongs to the actual project."""
        path = self.ide.explorer.get_actual_project()
        if path:
            self.ide.mainContainer.save_project(path)

    def save_all(self):
        """Save all the opened files."""
        self.ide.mainContainer.save_all()

    def print_file(self):
        """Call the print of ui_tool

        Call print of ui_tool depending on the focus of the application"""
        #TODO: Add funtionality for proyect tab and methods tab
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget is not None:
            fileName = "newDocument.pdf"
            if editorWidget.ID:
                fileName = file_manager.get_basename(
                    editorWidget.ID)
                fileName = fileName[:fileName.rfind('.')] + '.pdf'
            ui_tools.print_file(fileName, editorWidget.print_)

    def locate_function(self, function, filePath, isVariable):
        """Move the cursor to the proper position in the navigate stack."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget:
            self.__codeBack.append((editorWidget.ID,
                editorWidget.textCursor().position()))
            self.__codeForward = []
        self._locator.navigate_to(unicode(function),
            unicode(filePath), isVariable)

    def update_explorer(self):
        """Update the symbols in the Symbol Explorer when a file is saved."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget:
            ext = file_manager.get_file_extension(editorWidget.ID)
            #obtain a symbols handler for this file extension
            symbols_handler = settings.get_symbols_handler(ext)
            if symbols_handler:
                source = unicode(editorWidget.toPlainText())
                if editorWidget.encoding is not None:
                    source = source.encode(editorWidget.encoding)
                symbols = symbols_handler.obtain_symbols(source)
                self.ide.explorer.update_symbols(symbols, editorWidget.ID)

            #TODO: Should we change the code below similar to the code above?
            exts = settings.SYNTAX.get('python')['extension']
            if ext in exts or editorWidget.newDocument:
                self.ide.explorer.update_errors(
                    editorWidget.errors, editorWidget.pep8)

    def navigate_code_history(self, val, op):
        """Navigate the code history."""
        self.__operations[op](val)

    def _navigate_code_jumps(self, val):
        """Navigate between the jump points."""
        node = None
        if not val and self.__codeBack:
            node = self.__codeBack.pop()
            editorWidget = self.ide.mainContainer.get_actual_editor()
            if editorWidget:
                self.__codeForward.append((editorWidget.ID,
                    editorWidget.textCursor().position()))
        elif val and self.__codeForward:
            node = self.__codeForward.pop()
            editorWidget = self.ide.mainContainer.get_actual_editor()
            if editorWidget:
                self.__codeBack.append((editorWidget.ID,
                    editorWidget.textCursor().position()))
        if node:
            self.ide.mainContainer.open_file(node[0], node[1])

    def _navigate_breakpoints(self, val):
        """Navigate between the breakpoints."""
        breakList = settings.BREAKPOINTS.keys()
        breakList.sort()
        if not breakList:
            return
        if self.__breakpointsFile not in breakList:
            self.__breakpointsFile = breakList[0]
        index = breakList.index(self.__breakpointsFile)
        breaks = settings.BREAKPOINTS.get(self.__breakpointsFile, [])
        lineNumber = 0
        #val == True: forward
        if val:
            if (len(breaks) - 1) > self.__breakpointsPos:
                self.__breakpointsPos += 1
                lineNumber = breaks[self.__breakpointsPos]
            elif len(breaks) > 0:
                if index < (len(breakList) - 1):
                    self.__breakpointsFile = breakList[index + 1]
                else:
                    self.__breakpointsFile = breakList[0]
                self.__breakpointsPos = 0
                breaks = settings.BREAKPOINTS[self.__breakpointsFile]
                lineNumber = breaks[0]
        else:
            if self.__breakpointsPos > 0:
                self.__breakpointsPos -= 1
                lineNumber = breaks[self.__breakpointsPos]
            elif len(breaks) > 0:
                self.__breakpointsFile = breakList[index - 1]
                breaks = settings.BREAKPOINTS[self.__breakpointsFile]
                self.__breakpointsPos = len(breaks) - 1
                lineNumber = breaks[self.__breakpointsPos]
        if file_manager.file_exists(self.__breakpointsFile):
            self.ide.mainContainer.open_file(self.__breakpointsFile,
                lineNumber, None, True)
        else:
            settings.BREAKPOINTS.pop(self.__breakpointsFile)

    def _navigate_bookmarks(self, val):
        """Navigate between the bookmarks."""
        bookList = settings.BOOKMARKS.keys()
        bookList.sort()
        if not bookList:
            return
        if self.__bookmarksFile not in bookList:
            self.__bookmarksFile = bookList[0]
        index = bookList.index(self.__bookmarksFile)
        bookms = settings.BOOKMARKS.get(self.__bookmarksFile, [])
        lineNumber = 0
        #val == True: forward
        if val:
            if (len(bookms) - 1) > self.__bookmarksPos:
                self.__bookmarksPos += 1
                lineNumber = bookms[self.__bookmarksPos]
            elif len(bookms) > 0:
                if index < (len(bookList) - 1):
                    self.__bookmarksFile = bookList[index + 1]
                else:
                    self.__bookmarksFile = bookList[0]
                self.__bookmarksPos = 0
                bookms = settings.BOOKMARKS[self.__bookmarksFile]
                lineNumber = bookms[0]
        else:
            if self.__bookmarksPos > 0:
                self.__bookmarksPos -= 1
                lineNumber = bookms[self.__bookmarksPos]
            elif len(bookms) > 0:
                self.__bookmarksFile = bookList[index - 1]
                bookms = settings.BOOKMARKS[self.__bookmarksFile]
                self.__bookmarksPos = len(bookms) - 1
                lineNumber = bookms[self.__bookmarksPos]
        if file_manager.file_exists(self.__bookmarksFile):
            self.ide.mainContainer.open_file(self.__bookmarksFile,
                lineNumber, None, True)
        else:
            settings.BOOKMARKS.pop(self.__bookmarksFile)

    def add_back_item_navigation(self):
        """Add an item to the back stack and reset the forward stack."""
        editorWidget = self.ide.mainContainer.get_actual_editor()
        if editorWidget:
            self.__codeBack.append((editorWidget.ID,
                editorWidget.textCursor().position()))
            self.__codeForward = []

    def group_tabs_together(self):
        """Group files that belongs to the same project together."""
        if self.ide.explorer._treeProjects is None:
            return
        projects_obj = self.ide.explorer.get_opened_projects()
        projects = [p.path for p in projects_obj]
        for project in projects:
            projectName = self.ide.explorer.get_project_name(project)
            if not projectName:
                projectName = file_manager.get_basename(project)
            tabGroup = tab_group.TabGroup(project, projectName, self)
            for index in reversed(xrange(
            self.ide.mainContainer._tabMain.count())):
                widget = self.ide.mainContainer._tabMain.widget(index)
                if type(widget) is editor.Editor and \
                file_manager.belongs_to_folder(project, widget.ID):
                    tabGroup.add_widget(widget)
                    self.ide.mainContainer._tabMain.removeTab(index)
            if tabGroup.tabs:
                self.ide.mainContainer._tabMain.add_tab(tabGroup, projectName)

    def deactivate_tabs_groups(self):
        """Deactivate tab grouping based in the project they belong."""
        for index in reversed(xrange(
        self.ide.mainContainer._tabMain.count())):
            widget = self.ide.mainContainer._tabMain.widget(index)
            if type(widget) is tab_group.TabGroup:
                widget.only_expand()

    def reopen_last_tab(self):
        """Reopen the last closed tab."""
        self.ide.mainContainer.actualTab._reopen_last_tab()

    def open_class_diagram(self):
        """Open the Class Diagram Generator."""
        diagram = class_diagram.ClassDiagram(self)
        self.ide.mainContainer.add_tab(diagram, self.tr("Class Diagram v.0.1"))

    def reload_toolbar(self):
        """Reload the Toolbar."""
        self.ide.load_toolbar()
