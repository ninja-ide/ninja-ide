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

import re
import bisect

from tokenize import generate_tokens, TokenError
#lint:disable
try:
    from StringIO import StringIO
except:
    from io import StringIO
#lint:enable

#from PyQt4.QtGui import QToolTip
from PyQt4.QtGui import QAction
from PyQt4.QtGui import QInputDialog
from PyQt4.QtGui import QMenu
from PyQt4.QtGui import QColor
from PyQt4.QtGui import QKeySequence
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QMimeData
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QTimer

from ninja_ide import resources
from ninja_ide.core import settings
#from ninja_ide.core.file_handling import file_manager
##from ninja_ide.tools.completion import completer_widget
from ninja_ide.gui.ide import IDE
from ninja_ide.gui.editor import highlighter
from ninja_ide.gui.editor import helpers
from ninja_ide.gui.editor import minimap
from ninja_ide.gui.editor import document_map
from ninja_ide.extensions import handlers

from PyQt4.Qsci import QsciScintilla  # , QsciCommand

from ninja_ide.tools.logger import NinjaLogger
logger = NinjaLogger('ninja_ide.gui.editor.editor')

BRACE_DICT = {')': '(', ']': '[', '}': '{', '(': ')', '[': ']', '{': '}'}


class Editor(QsciScintilla):

###############################################################################
# EDITOR SIGNALS
###############################################################################
    """
    modificationChanged(bool)
    fileSaved(QPlainTextEdit)
    locateFunction(QString, QString, bool) [functionName, filePath, isVariable]
    openDropFile(QString)
    addBackItemNavigation()
    findOcurrences(QString)
    cursorPositionChange(int, int)    #row, col
    migrationAnalyzed()
    currentLineChanged(int)
    """
###############################################################################

    __indicator_word = 0
    __indicator_folded = 2
    __indicator_navigation = 3

    def _configure_qscintilla(self):
        self._first_visible_line = 0
        self.patFold = re.compile(
            r"(\s)*\"\"\"|(\s)*def |(\s)*class |(\s)*if |(\s)*while |"
            "(\s)*else:|(\s)*elif |(\s)*for |"
            "(\s)*try:|(\s)*except:|(\s)*except |(.)*\($")
        self.setAutoIndent(True)
        self.setBackspaceUnindents(True)
        self.setCaretLineVisible(True)
        line_color = QColor(
            resources.CUSTOM_SCHEME.get(
                'CurrentLine',
                resources.COLOR_SCHEME['CurrentLine']))
        caretColor = QColor(
            resources.CUSTOM_SCHEME.get(
                'Caret',
                resources.COLOR_SCHEME['Caret']))
        self.setCaretLineBackgroundColor(line_color)
        self.setCaretForegroundColor(caretColor)
        self.setBraceMatching(QsciScintilla.StrictBraceMatch)
        self.SendScintilla(QsciScintilla.SCI_SETBUFFEREDDRAW, 0)
        self.SendScintilla(QsciScintilla.SCI_SETHSCROLLBAR, 0)
        self.setMatchedBraceBackgroundColor(QColor(
            resources.CUSTOM_SCHEME.get(
                'BraceBackground',
                resources.COLOR_SCHEME.get('BraceBackground'))))
        self.setMatchedBraceForegroundColor(QColor(
            resources.CUSTOM_SCHEME.get(
                'BraceForeground',
                resources.COLOR_SCHEME.get('BraceForeground'))))

        self.SendScintilla(QsciScintilla.SCI_INDICSETFORE,
                           self.__indicator_word,
                           int(resources.get_color_hex("SelectedWord"), 16))
        self.SendScintilla(QsciScintilla.SCI_INDICSETSTYLE,
                           self.__indicator_word, 6)
        self.SendScintilla(QsciScintilla.SCI_INDICSETFORE,
                           self.__indicator_folded, int("ffffff", 16))
        self.SendScintilla(QsciScintilla.SCI_INDICSETSTYLE,
                           self.__indicator_folded, 0)
        self._navigation_highlight_active = False
        self.SendScintilla(QsciScintilla.SCI_INDICSETFORE,
                           self.__indicator_navigation,
                           int(resources.get_color_hex("LinkNavigate"), 16))
        self.SendScintilla(QsciScintilla.SCI_INDICSETSTYLE,
                           self.__indicator_navigation, 8)
        self.SendScintilla(QsciScintilla.SCI_INDICSETALPHA,
                           self.__indicator_navigation, 40)

        # Sets QScintilla into unicode mode
        self.SendScintilla(QsciScintilla.SCI_SETCODEPAGE, 65001)
        # Enable multiple selection
        self.SendScintilla(QsciScintilla.SCI_SETMULTIPLESELECTION, 1)
        self.SendScintilla(QsciScintilla.SCI_SETADDITIONALSELECTIONTYPING, 1)

    def __init__(self, neditable):
        super(Editor, self).__init__()
        self._neditable = neditable
        # QScintilla Configuration
        self._configure_qscintilla()

        # Markers
        self.foldable_lines = []
        self.breakpoints = []
        self.bookmarks = []
        self.search_lines = []
        self._fold_expanded_marker = 1
        self._fold_collapsed_marker = 2
        self._bookmark_marker = 3
        self._breakpoint_marker = 4
        self.setMarginSensitivity(1, True)
        self.connect(
            self,
            SIGNAL('marginClicked(int, int, Qt::KeyboardModifiers)'),
            self.on_margin_clicked)
        color_fore = resources.get_color("FoldArea")
        # Marker Fold Expanded
        self.markerDefine(QsciScintilla.DownTriangle,
                          self._fold_expanded_marker)
        color = resources.get_color("FoldArrowExpanded")
        self.setMarkerBackgroundColor(QColor(color), self._fold_expanded_marker)
        self.setMarkerForegroundColor(QColor(color_fore),
                                      self._fold_expanded_marker)
        # Marker Fold Collapsed
        self.markerDefine(QsciScintilla.RightTriangle,
                          self._fold_collapsed_marker)
        color = resources.get_color("FoldArrowCollapsed")
        self.setMarkerBackgroundColor(QColor(color),
                                      self._fold_collapsed_marker)
        self.setMarkerForegroundColor(QColor(color_fore),
                                      self._fold_collapsed_marker)
        # Marker Breakpoint
        self.markerDefine(QsciScintilla.Circle,
                          self._breakpoint_marker)
        self.setMarkerBackgroundColor(QColor(255, 11, 11),
                                      self._breakpoint_marker)
        self.setMarkerForegroundColor(QColor(color_fore),
                                      self._breakpoint_marker)
        # Marker Bookmark
        self.markerDefine(QsciScintilla.SmallRectangle,
                          self._bookmark_marker)
        self.setMarkerBackgroundColor(QColor(10, 158, 227),
                                      self._bookmark_marker)
        self.setMarkerForegroundColor(QColor(color_fore),
                                      self._bookmark_marker)
        # Configure key bindings
        self._configure_keybindings()

        self.lexer = highlighter.get_lexer(self._neditable.extension())

        if self.lexer is not None:
            self.setLexer(self.lexer)

        #Config Editor
        self._mini = None
        if settings.SHOW_MINIMAP:
            self._load_minimap(settings.SHOW_MINIMAP)
        self._docmap = None
        if settings.SHOW_DOCMAP:
            self._load_docmap(settings.SHOW_DOCMAP)
            self.cursorPositionChanged.connect(self._docmap.update)

        self._last_block_position = 0
        self.set_flags()
        #FIXME this lang should be guessed in the same form as lexer.
        self.lang = highlighter.get_lang(self._neditable.extension())
        self._cursor_line = self._cursor_index = -1
        self.__lines_count = 0
        self.pos_margin = 0
        self._indentation_guide = 0
        self._indent = 0
        self.__font = None
        self.__encoding = None
        self.__positions = []  # Caret positions
        self.SCN_CHARADDED.connect(self._on_char_added)

        #FIXME these should be language bound
        self.allows_less_indentation = ['else', 'elif', 'finally', 'except']
        self.set_font(settings.FONT)
        self._selected_word = ''
        self._patIsWord = re.compile('\w+')
        #Completer
        #self.completer = completer_widget.CodeCompletionWidget(self)
        #Dict functions for KeyPress
        self.preKeyPress = {
            Qt.Key_Backspace: self.__backspace,
            Qt.Key_Enter: self.__ignore_extended_line,
            Qt.Key_Return: self.__ignore_extended_line,
            #Qt.Key_Colon: self.__retreat_to_keywords,
            Qt.Key_BracketRight: self.__brace_completion,
            Qt.Key_BraceRight: self.__brace_completion,
            Qt.Key_ParenRight: self.__brace_completion,
            Qt.Key_Apostrophe: self.__quot_completion,
            Qt.Key_QuoteDbl: self.__quot_completion}

        self.postKeyPress = {
            Qt.Key_Enter: self.__auto_indent,
            Qt.Key_Return: self.__auto_indent,
            Qt.Key_BracketLeft: self.__complete_braces,
            Qt.Key_BraceLeft: self.__complete_braces,
            Qt.Key_ParenLeft: self.__complete_braces,
            Qt.Key_Apostrophe: self.__complete_quotes,
            Qt.Key_QuoteDbl: self.__complete_quotes}

        # Highlight word timer
        self._highlight_word_timer = QTimer()
        self._highlight_word_timer.setSingleShot(True)
        self._highlight_word_timer.timeout.connect(self.highlight_selected_word)
        # Highlight the words under cursor after 500 msec, starting when
        # the cursor changes position
        self.cursorPositionChanged.connect(
            lambda: self._highlight_word_timer.start(500))

        self.connect(self, SIGNAL("linesChanged()"), self._update_sidebar)
        self.connect(self, SIGNAL("blockCountChanged(int)"),
                     self._update_file_metadata)

        self.load_project_config()
        #Context Menu Options
        self.__actionFindOccurrences = QAction(self.tr("Find Usages"), self)
        self.connect(self.__actionFindOccurrences, SIGNAL("triggered()"),
                     self._find_occurrences)

        ninjaide = IDE.get_service('ide')
        self.connect(
            ninjaide,
            SIGNAL("ns_preferences_editor_font(PyQt_PyObject)"),
            self.set_font)
        self.connect(
            ninjaide,
            SIGNAL("ns_preferences_editor_showTabsAndSpaces(PyQt_PyObject)"),
            self.set_flags)
        self.connect(
            ninjaide,
            SIGNAL("ns_preferences_editor_showIndentationGuide(PyQt_PyObject)"),
            self.set_flags)
        #TODO: figure it out it doesn´t work if gets shown after init
        self.connect(ninjaide,
            SIGNAL("ns_preferences_editor_minimapShow(PyQt_PyObject)"),
            self._load_minimap)
        self.connect(ninjaide,
            SIGNAL("ns_preferences_editor_docmapShow(PyQt_PyObject)"),
            self._load_docmap)
        self.connect(
            ninjaide,
            SIGNAL("ns_preferences_editor_indent(PyQt_PyObject)"),
            self.load_project_config)
        self.connect(
            ninjaide,
            SIGNAL("ns_preferences_editor_marginLine(PyQt_PyObject)"),
            self._set_margin_line)
        self.connect(
            ninjaide,
            SIGNAL("ns_preferences_editor_showLineNumbers(PyQt_PyObject)"),
            self._show_line_numbers)
        self.connect(ninjaide,
                     SIGNAL(
            "ns_preferences_editor_errorsUnderlineBackground(PyQt_PyObject)"),
                self._change_indicator_style)
        #self.connect(
            #ninjaide,
            #SIGNAL("ns_preferences_editor_scheme(PyQt_PyObject)"),
            #self.restyle)
        #self.connect(
            #ninjaide,
            #SIGNAL("ns_preferences_editor_scheme(PyQt_PyObject)"),
            #lambda: self.restyle())

        self.additional_builtins = None
        # Set the editor after initialization
        if self._neditable.editor:
            self.setDocument(self._neditable.document)
        else:
            self._neditable.set_editor(self)

        if self._neditable.file_path in settings.BREAKPOINTS:
            self.breakpoints = settings.BREAKPOINTS[self._neditable.file_path]
        if self._neditable.file_path in settings.BOOKMARKS:
            self.bookmarks = settings.BOOKMARKS[self._neditable.file_path]
        # Add breakpoints
        for line in self.breakpoints:
            self.markerAdd(line, self._breakpoint_marker)
        # Add bookmarks
        for line in self.bookmarks:
            self.markerAdd(line, self._bookmark_marker)

        self.connect(
            self._neditable,
            SIGNAL("checkersUpdated(PyQt_PyObject)"),
            self._highlight_checkers)

    @property
    def display_name(self):
        self._neditable.display_name

    @property
    def nfile(self):
        return self._neditable.nfile

    @property
    def neditable(self):
        return self._neditable

    @property
    def file_path(self):
        return self._neditable.file_path

    @property
    def is_modified(self):
        return self.isModified()

    def _configure_keybindings(self):
        #commands = self.standardCommands()
        #command = commands.find(QsciCommand.LineDuplicate)
        #command.setKey()
        #command.setAlternateKey(0)
        #print dir(QsciScintilla)
        self.SendScintilla(QsciScintilla.SCI_ASSIGNCMDKEY,
                           QsciScintilla.SCI_HOMEDISPLAY, Qt.Key_Home)

    def on_margin_clicked(self, nmargin, nline, modifiers):
        position = self.positionFromLineIndex(nline, 0)
        length = self.lineLength(nline)

        if nline in self.contractedFolds():
            self.SendScintilla(QsciScintilla.SCI_SETINDICATORCURRENT,
                               self.__indicator_folded)
            self.SendScintilla(QsciScintilla.SCI_INDICATORCLEARRANGE,
                               position, length)
            self.markerDelete(nline, self._fold_collapsed_marker)
            self.markerAdd(nline, self._fold_expanded_marker)
            self.foldLine(nline)
            if self._mini:
                self._mini.fold(nline)
        elif nline in self.foldable_lines:
            self.SendScintilla(QsciScintilla.SCI_SETINDICATORCURRENT,
                               self.__indicator_folded)
            self.SendScintilla(QsciScintilla.SCI_INDICATORFILLRANGE,
                               position, length)
            self.markerDelete(nline, self._fold_expanded_marker)
            self.markerAdd(nline, self._fold_collapsed_marker)
            self.foldLine(nline)
            if self._mini:
                self._mini.fold(nline)
        else:
            self.handle_bookmarks_breakpoints(nline, modifiers)

    def handle_bookmarks_breakpoints(self, line, modifiers):
        # Breakpoints Default
        marker = self._breakpoint_marker
        list_markers = self.breakpoints
        if modifiers == Qt.ControlModifier:
            # Bookmarks
            marker = self._bookmark_marker
            list_markers = self.bookmarks

        if self.markersAtLine(line) != 0:
            self.markerDelete(line, marker)
            list_markers.remove(line)
        else:
            self.markerAdd(line, marker)
            list_markers.append(line)

        self._save_breakpoints_bookmarks()

    def _change_indicator_style(self, underline):
        ncheckers = len(self._neditable.sorted_checkers)
        indicator_style = QsciScintilla.INDIC_SQUIGGLE
        if not underline:
            indicator_style = QsciScintilla.INDIC_STRAIGHTBOX
        indicator_index = 4
        for i in range(ncheckers):
            self.SendScintilla(QsciScintilla.SCI_INDICSETSTYLE,
                               indicator_index, indicator_style)
            indicator_index += 1

    def _save_breakpoints_bookmarks(self):
        if self.bookmarks and not self._neditable.new_document:
            settings.BOOKMARKS[self._neditable.file_path] = self.bookmarks
        elif self._neditable.file_path in settings.BOOKMARKS:
            settings.BOOKMARKS.pop(self._neditable.file_path)

        if self.breakpoints and not self._neditable.new_document:
            settings.BREAKPOINTS[self._neditable.file_path] = self.breakpoints
        elif self._neditable.file_path in settings.BREAKPOINTS:
            settings.BREAKPOINTS.pop(self._neditable.file_path)

    def _highlight_checkers(self, checkers):
        checkers = self._neditable.sorted_checkers
        indicator_index = 4  # Start from 4 (valid), before numbers are used
        painted_lines = []
        for items in checkers:
            checker, color, _ = items
            lines = list(checker.checks.keys())
            # Set current
            self.SendScintilla(QsciScintilla.SCI_SETINDICATORCURRENT,
                               indicator_index)
            # Clear
            self.SendScintilla(QsciScintilla.SCI_INDICATORCLEARRANGE,
                               0, len(self.text()))
            # Set Color
            color = color.replace("#", "")
            self.SendScintilla(QsciScintilla.SCI_INDICSETFORE,
                               indicator_index, int(color, 16))
            # Set Style
            indicator_style = QsciScintilla.INDIC_SQUIGGLE
            if not settings.UNDERLINE_NOT_BACKGROUND:
                indicator_style = QsciScintilla.INDIC_STRAIGHTBOX
            self.SendScintilla(QsciScintilla.SCI_INDICSETSTYLE,
                               indicator_index, indicator_style)
            # Paint Lines
            for line in lines:
                if line in painted_lines:
                    continue
                position = self.positionFromLineIndex(line, 0)
                length = self.lineLength(line)
                self.SendScintilla(QsciScintilla.SCI_INDICATORFILLRANGE,
                                   position, length)
                painted_lines.append(line)
            indicator_index += 1

    def cursor_before_focus_lost(self):
        return self._cursor_line, self._cursor_index

    def load_project_config(self):
        ninjaide = IDE.get_service('ide')
        project = ninjaide.get_project_for_file(self._neditable.file_path)
        if project is not None:
            self._indent = project.indentation
            self.useTabs = project.use_tabs
            self.connect(project, SIGNAL("projectPropertiesUpdated()"),
                         self.load_project_config)
            self.additional_builtins = project.additional_builtins
        else:
            self._indent = settings.INDENT
            self.useTabs = settings.USE_TABS
            self.additional_builtins = None
        self.setIndentationsUseTabs(self.useTabs)
        self.setIndentationWidth(self._indent)
        if self._mini:
            self._mini.setIndentationsUseTabs(self.useTabs)
            self._mini.setIndentationWidth(self._indent)
        self._set_margin_line(settings.MARGIN_LINE)

    def _update_sidebar(self):
        # Margin 0 is used for line numbers
        if settings.SHOW_LINE_NUMBERS:
            self.setMarginWidth(0, '0' * (len(str(self.lines())) + 1))
        else:
            self.setMarginWidth(0, 0)

        # Fold
        self.foldable_lines = []
        lines = self.lines()
        for line in range(lines):
            text = self.text(line)
            if self.patFold.match(text):
                self.foldable_lines.append(line)
                if line in self.contractedFolds():
                    self.markerDelete(line, self._fold_collapsed_marker)
                    self.markerDelete(line, self._fold_expanded_marker)
                    self.markerAdd(line, self._fold_collapsed_marker)
                else:
                    self.markerDelete(line, self._fold_collapsed_marker)
                    self.markerDelete(line, self._fold_expanded_marker)
                    self.markerAdd(line, self._fold_expanded_marker)

    def _load_minimap(self, show):
        if show:
            if self._mini is None:
                self._mini = minimap.MiniMap(self)
                # Signals
                self.SCN_UPDATEUI.connect(self._mini.scroll_map)
                self.SCN_ZOOM.connect(self._mini.slider.update_position)
                self._mini.setDocument(self.document())
                self._mini.setLexer(self.lexer)
                #FIXME: register syntax
                self._mini.show()
            self._mini.adjust_to_parent()
        elif self._mini is not None:
            #FIXME: lost doc pointer?
            self._mini.shutdown()
            self._mini.deleteLater()
            self._mini = None

    def _load_docmap(self, show):
        if show:
            if self._docmap is None:
                self._docmap = document_map.DocumentMap(self)
            self._docmap.initialize()
        elif self._docmap is not None:
            self._docmap.deleteLater()
            self._docmap = None
    #def __retreat_to_keywords(self, event):
        #"""Unindent some kind of blocks if needed."""
        #previous_text = unicode(self.textCursor().block().previous().text())
        #current_text = unicode(self.textCursor().block().text())
        #previous_spaces = helpers.get_indentation(previous_text)
        #current_spaces = helpers.get_indentation(current_text)

        #if len(previous_spaces) < len(current_spaces):
            #last_word = helpers.get_first_keyword(current_text)

            #if last_word in self.allows_less_indentation:
                #helpers.clean_line(self)

                #spaces_diff = len(current_spaces) - len(previous_spaces)
                #self.textCursor().insertText(current_text[spaces_diff:])

    def __get_encoding(self):
        """Get the current encoding of 'utf-8' otherwise."""
        if self.__encoding is not None:
            return self.__encoding
        return 'utf-8'

    def __set_encoding(self, encoding):
        """Set the current encoding."""
        self.__encoding = encoding

    encoding = property(__get_encoding, __set_encoding)

    def set_flags(self):
        """Set some configuration flags for the Editor."""
        if settings.ALLOW_WORD_WRAP:
            self.setWrapMode(QsciScintilla.WrapWord)
        else:
            self.setWrapMode(QsciScintilla.WrapNone)
        self.setMouseTracking(True)
        if settings.SHOW_TABS_AND_SPACES:
            self.setWhitespaceVisibility(QsciScintilla.WsVisible)
        else:
            self.setWhitespaceVisibility(QsciScintilla.WsInvisible)
        self.setIndentationGuides(settings.SHOW_INDENTATION_GUIDE)
        self.setEolVisibility(settings.USE_PLATFORM_END_OF_LINE)
        self.SendScintilla(QsciScintilla.SCI_SETENDATLASTLINE,
                           settings.END_AT_LAST_LINE)

    def _update_file_metadata(self):
        """Update the info of bookmarks, breakpoint and checkers."""
        new_count = self.lines()
        if (self.bookmarks or self.breakpoints):
            line, index = self.getCursorPosition()
            diference = new_count - self.__lines_count
            lineNumber = line - abs(diference)
            contains_text = self.lineLength(line) != 0
            self._update_sidebar_marks(lineNumber, diference, contains_text)
        self.__lines_count = new_count

    def _update_sidebar_marks(self, lineNumber, diference, atLineStart=False):
        if self.breakpoints:
            self.breakpoints = helpers.add_line_increment(
                self.breakpoints, lineNumber, diference, atLineStart)
            if not self._neditable.new_document:
                settings.BREAKPOINTS[self._neditable.file_path] = \
                    self._breakpoints
        if self.bookmarks:
            self.bookmarks = helpers.add_line_increment(
                self.bookmarks, lineNumber, diference, atLineStart)
            if not self._neditable.new_document:
                settings.BOOKMARKS[self._neditable.file_path] = self._bookmarks

    #def restyle(self, syntaxLang=None):
        #self.apply_editor_style()
        #if self.lang == 'python':
            #parts_scanner, code_scanner, formats = \
                #syntax_highlighter.load_syntax(python_syntax.syntax)
            #self.highlighter = syntax_highlighter.SyntaxHighlighter(
                #self.document(),
                #parts_scanner, code_scanner, formats, self._neditable)
            #if self._mini:
                #self._mini.highlighter = syntax_highlighter.SyntaxHighlighter(
                    #self._mini.document(), parts_scanner,
                    #code_scanner, formats)
            #return
        #if self.highlighter is None or isinstance(self.highlighter,
           #highlighter.EmpyHighlighter):
            #self.highlighter = highlighter.Highlighter(
                #self.document(),
                #None, resources.CUSTOM_SCHEME, self.errors, self.pep8,
                #self.migration)
        #if not syntaxLang:
            #ext = file_manager.get_file_extension(self.file_path)
            #self.highlighter.apply_highlight(
                #settings.EXTENSIONS.get(ext, 'python'),
                #resources.CUSTOM_SCHEME)
            #if self._mini:
                #self._mini.highlighter.apply_highlight(
                    #settings.EXTENSIONS.get(ext, 'python'),
                    #resources.CUSTOM_SCHEME)
        #else:
            #self.highlighter.apply_highlight(
                #syntaxLang, resources.CUSTOM_SCHEME)
            #if self._mini:
                #self._mini.highlighter.apply_highlight(
                    #syntaxLang, resources.CUSTOM_SCHEME)
        #self._sidebarWidget.repaint()

    #def register_syntax(self, lang='', syntax=None):
        #self.lang = settings.EXTENSIONS.get(lang, 'python')
        #sr = IDE.get_service("syntax_registry")
        #this_syntax = sr.get_syntax_for(self.lang)

        #if this_syntax is not None:
            #parts_scanner, code_scanner, formats = \
                #syntax_highlighter.load_syntax(this_syntax)
            #self.highlighter = syntax_highlighter.SyntaxHighlighter(
                #self.document(),
                #parts_scanner, code_scanner, formats, self._neditable)
            #if self._mini:
                #self._mini.highlighter = syntax_highlighter.SyntaxHighlighter(
                    #self._mini.document(), parts_scanner,
                    #code_scanner, formats, self._neditable)

    def _show_line_numbers(self):
        self.setMarginsFont(self.__font)
        # Margin 0 is used for line numbers
        self.setMarginLineNumbers(0, settings.SHOW_LINE_NUMBERS)
        self._update_sidebar()

    def set_font(self, font):
        self.__font = font
        self.lexer.setFont(font)
        self._show_line_numbers()
        background = resources.CUSTOM_SCHEME.get(
            'SidebarBackground',
            resources.COLOR_SCHEME['SidebarBackground'])
        foreground = resources.CUSTOM_SCHEME.get(
            'SidebarForeground',
            resources.COLOR_SCHEME['SidebarForeground'])
        self.setMarginsBackgroundColor(QColor(background))
        self.setMarginsForegroundColor(QColor(foreground))

    def jump_to_line(self, lineno=None):
        """
        Jump to a specific line number or ask to the user for the line
        """
        if lineno is not None:
            self.emit(SIGNAL("addBackItemNavigation()"))
            self._cursor_line = self._cursor_index = -1
            self.go_to_line(lineno)
            return

        maximum = self.lines()
        line = QInputDialog.getInt(self, self.tr("Jump to Line"),
                                   self.tr("Line:"), 1, 1, maximum, 1)
        if line[1]:
            self.emit(SIGNAL("addBackItemNavigation()"))
            self.go_to_line(line[0] - 1)

    def _find_occurrences(self):
        if self.hasSelectedText():
            word = self.selectedText()
        else:
            word = self._text_under_cursor()
        self.emit(SIGNAL("findOcurrences(QString)"), word)

    def go_to_line(self, lineno):
        """
        Go to an specific line
        """
        if self.lines() >= lineno:
            self.setCursorPosition(lineno, 0)

    def zoom_in(self):
        self.zoomIn()

    def zoom_out(self):
        self.zoomOut()

    def _set_margin_line(self, margin=None):
        color_margin = QColor(resources.CUSTOM_SCHEME.get(
            "MarginLine", resources.COLOR_SCHEME["MarginLine"]))
        self.setEdgeMode(QsciScintilla.EdgeLine)
        self.setEdgeColumn(margin)
        self.setEdgeColor(color_margin)

    def set_cursor_position(self, line, index=0):
        if self.lines() >= line:
            self._first_visible_line = line
            self._cursor_line = self._cursor_index = -1
            self.setCursorPosition(line, index)

    def add_caret(self):
        """ Adds additional caret in current position """

        cur_pos = self.SendScintilla(QsciScintilla.SCI_GETCURRENTPOS)
        if cur_pos not in self.__positions:
            self.__positions.append(cur_pos)

        # Same position arguments is use for just adding carets
        # rather than selections.
        for e, pos in enumerate(self.__positions):
            if e == 0:
                # The first selection should be added with SCI_SETSELECTION
                # and later selections added with SCI_ADDSELECTION
                self.SendScintilla(QsciScintilla.SCI_CLEARSELECTIONS)
                self.SendScintilla(QsciScintilla.SCI_SETSELECTION, pos, pos)
            else:
                self.SendScintilla(QsciScintilla.SCI_ADDSELECTION, pos, pos)

    def _on_char_added(self):
        """
        When char is added, cursors change position. This function obtains
        new positions and adds them to the list of positions.
        """

        # For rectangular selection
        if not self.__positions:
            return
        selections = self.SendScintilla(QsciScintilla.SCI_GETSELECTIONS)
        if selections > 1:
            for sel in range(selections):
                new_pos = self.SendScintilla(
                    QsciScintilla.SCI_GETSELECTIONNCARET, sel)
                self.__positions[sel] = new_pos

    def indent_less(self):
        if self.hasSelectedText():
            self.SendScintilla(QsciScintilla.SCI_BEGINUNDOACTION, 1)
            line_from, _, line_to, _ = self.getSelection()
            for i in range(line_from, line_to):
                self.unindent(i)
            self.SendScintilla(QsciScintilla.SCI_ENDUNDOACTION, 1)
        else:
            line, _ = self.getCursorPosition()
            self.unindent(line)

    def indent_more(self):
        if self.hasSelectedText():
            self.SendScintilla(QsciScintilla.SCI_BEGINUNDOACTION, 1)
            line_from, _, line_to, _ = self.getSelection()
            for i in range(line_from, line_to):
                self.indent(i)
            self.SendScintilla(QsciScintilla.SCI_ENDUNDOACTION, 1)
        else:
            line, _ = self.getCursorPosition()
            self.indent(line)

    def find_match(self, expr, reg, cs, wo, wrap=True, forward=True, line=-1,
                   index=-1):
        if self.hasSelectedText():
            line, index, lto, ito = self.getSelection()
            index += 1
        elif line < 0 or index < 0:
            line, index = self._cursor_line, self._cursor_index
        found = self.findFirst(expr, reg, cs, wo, wrap, forward, line, index)
        if found:
            self.highlight_selected_word(expr, case_sensitive=cs)
            return self._get_find_index_result(expr, cs, wo)
        else:
            return 0, 0

    def _get_find_index_result(self, expr, cs, wo):
        text = self.text()
        hasSearch = len(expr) > 0
        current_index = 0
        if wo:
            pattern = r'\b%s\b' % expr
            temp_text = ' '.join(re.findall(pattern, text, re.IGNORECASE))
            text = temp_text if temp_text != '' else text

        if cs:
            search = expr
            totalMatches = text.count(expr)
        else:
            text = text.lower()
            search = expr.lower()
            totalMatches = text.count(search)
        if hasSearch and totalMatches > 0:
            line, index, lto, ito = self.getSelection()
            position = self.positionFromLineIndex(line, index)

            current_index = text[:position].count(search)
            if current_index <= totalMatches:
                index = current_index
            else:
                index = text.count(search) + 1
        else:
            index = 0
            totalMatches = 0
        return current_index + 1, totalMatches

    def replace_match(self, wordOld, wordNew, allwords=False, selection=False):
        """Find if searched text exists and replace it with new one.
        If there is a selection just do it inside it and exit.
        """
        if selection and self.hasSelectedText():
            lstart, istart, lend, iend = self.getSelection()
            text = self.selectedText()
            max_replace = -1  # all
            text = text.replace(wordOld, wordNew, max_replace)
            self.replaceSelectedText(text)
            return

        self.SendScintilla(QsciScintilla.SCI_BEGINUNDOACTION, 1)
        line, index, lto, ito = self.getSelection()
        self.replace(wordNew)

        while allwords:
            result = self.findNext()

            if result:
                self.replace(wordNew)
            else:
                break

        if allwords:
            self.setCursorPosition(line, index)
        self.SendScintilla(QsciScintilla.SCI_ENDUNDOACTION, 1)

    def focusInEvent(self, event):
        super(Editor, self).focusInEvent(event)
        self.emit(SIGNAL("editorFocusObtained()"))
        selected = False
        if self.hasSelectedText():
            selected = True
            line, index, lto, ito = self.getSelection()
        else:
            line, index = self._cursor_line, self._cursor_index
        if line != -1:
            self.setCursorPosition(line, index)
        if selected:
            self.setSelection(line, index, lto, ito)
        self.SendScintilla(QsciScintilla.SCI_SETFIRSTVISIBLELINE,
                           self._first_visible_line)

    def focusOutEvent(self, event):
        """Hide Popup on focus lost."""
        #self.completer.hide_completer()
        self._first_visible_line = int(
            self.SendScintilla(QsciScintilla.SCI_GETFIRSTVISIBLELINE))
        self._cursor_line, self._cursor_index = self.getCursorPosition()
        super(Editor, self).focusOutEvent(event)

    def resizeEvent(self, event):
        super(Editor, self).resizeEvent(event)
        if self._mini:
            self._mini.adjust_to_parent()
        if self._docmap:
            self._docmap.adjust()

    def __backspace(self, event):
        if self.hasSelectedText():
            return False
        line, index = self.getCursorPosition()
        text = self.text(line)
        if index < len(text):
            char = text[index - 1]
            next_char = text[index]

            if (char in settings.BRACES and
                    next_char in settings.BRACES.values()) \
                    or (char in settings.QUOTES and
                        next_char in settings.QUOTES.values()):
                self.setSelection(line, index - 1, line, index)
                self.removeSelectedText()

    def __ignore_extended_line(self, event):
        if event.modifiers() == Qt.ShiftModifier:
            return True

    def __reverse_select_text_portion_from_offset(self, begin, end):
        """Backwards select text, go from current+begin to current - end
        possition, returns text"""
        line, index = self.getCursorPosition()
        text = self.text(line)
        cursor_position = index
        #QT silently fails on invalid position, ergo breaks when EOF < begin
        while ((index + begin) == index) and begin > 0:
            begin -= 1
            index = cursor_position + begin
        return text[index:cursor_position - end]

    def __quot_completion(self, event):
        """Indicate if this is some sort of quote that needs to be completed
        This is a very simple boolean table, given that quotes are a
        simmetrical symbol, is a little more cumbersome guessing the completion
        table.
        """
        text = event.text()
        line, index = self.getCursorPosition()
        PENTA_Q = 5 * text
        TETRA_Q = 4 * text
        TRIPLE_Q = 3 * text
        DOUBLE_Q = 2 * text
        supress_echo = False
        pre_context = self.__reverse_select_text_portion_from_offset(0, 3)
        pos_context = self.__reverse_select_text_portion_from_offset(3, 0)
        if pre_context == pos_context == TRIPLE_Q:
            supress_echo = True
        elif pos_context[:2] == DOUBLE_Q:
            pre_context = self.__reverse_select_text_portion_from_offset(0, 4)
            if pre_context == TETRA_Q:
                supress_echo = True
        elif pos_context[:1] == text:
            pre_context = self.__reverse_select_text_portion_from_offset(0, 5)
            if pre_context == PENTA_Q:
                supress_echo = True
            elif pre_context[-1] == text:
                supress_echo = True
        if supress_echo:
            line, index = self.getCursorPosition()
            self.setCursorPosition(line, index + 1)
        return supress_echo

    def __brace_completion(self, event):
        """Indicate if this symbol is part of a given pair and needs to be
        completed.
        """
        text = event.text()
        if text in list(settings.BRACES.values()):
            line, index = self.getCursorPosition()
            line_text = self.text(line)
            portion = line_text[index - 1:index + 1]
            brace_open = portion[0]
            brace_close = (len(portion) > 1) and portion[1] or None
            balance = BRACE_DICT.get(brace_open, None) == text == brace_close
            if balance:
                self.setCursorPosition(line, index + 1)
                return True

    def __auto_indent(self, event):
        line, index = self.getCursorPosition()
        text = self.text(line - 1).strip()
        symbols_to_look = tuple(settings.BRACES.keys()) + (",",)
        if text and text[-1] in symbols_to_look:
            symbol = " " * self._indent
            if self.useTabs:
                symbol = "\t"
            self.insertAt(symbol, line, index)
            self.setCursorPosition(line, index + self._indent)
        if settings.COMPLETE_DECLARATIONS and text and text[-1] == ":":
            helpers.check_for_assistance_completion(self, text)

    def complete_declaration(self):
        settings.COMPLETE_DECLARATIONS = not settings.COMPLETE_DECLARATIONS
        self.insert_new_line()
        settings.COMPLETE_DECLARATIONS = not settings.COMPLETE_DECLARATIONS

    def insert_new_line(self):
        line, index = self.getCursorPosition()
        length = self.lineLength(line) - 1
        at_block_end = index == length
        self.insertAt("\n", line, length)
        if not at_block_end:
            length = self.lineLength(line + 1)
            self.setCursorPosition(line + 1, length)
        self.__auto_indent(None)

    def __complete_braces(self, event):
        """Complete () [] and {} using a mild inteligence to see if corresponds
        and also do some more magic such as complete in classes and functions.
        """
        brace = event.text()
        if brace not in settings.BRACES:
            # Thou shalt not waste cpu cycles if this brace compleion dissabled
            return
        line, index = self.getCursorPosition()
        text = self.text(line)
        complementary_brace = BRACE_DICT.get(brace)
        token_buffer = []
        _, tokens = self.__tokenize_text(text)
        is_unbalance = 0
        for tkn_type, tkn_rep, tkn_begin, tkn_end in tokens:
            if tkn_rep == brace:
                is_unbalance += 1
            elif tkn_rep == complementary_brace:
                is_unbalance -= 1
            if tkn_rep.strip() != "":
                token_buffer.append((tkn_rep, tkn_end[1]))
            is_unbalance = (is_unbalance >= 0) and is_unbalance or 0

        if (self.lang == "python") and (len(token_buffer) == 3) and \
                (token_buffer[2][0] == brace) and (token_buffer[0][0] in
                                                   ("def", "class")):
            self.insertAt("):", line, index)
            #are we in presence of a function?
            #TODO: IMPROVE THIS AND GENERALIZE IT WITH INTELLISENSEI
            if token_buffer[0][0] == "def":
                symbols_handler = handlers.get_symbols_handler('py')
                split_source = self.text().split("\n")
                indent = re.match('^\s+', str(split_source[line]))
                indentation = (indent.group() + " " * self._indent
                               if indent is not None else " " * self._indent)
                new_line = "%s%s" % (indentation, 'pass')
                split_source.insert(line + 1, new_line)
                source = '\n'.join(split_source)
                source = source.encode(self.encoding)
                _, symbols_simplified = symbols_handler.obtain_symbols(
                    source, simple=True, only_simple=True)
                symbols_index = sorted(symbols_simplified.keys())
                symbols_simplified = sorted(
                    list(symbols_simplified.items()), key=lambda x: x[0])
                index_symbol = bisect.bisect(symbols_index, line)
                if (index_symbol >= len(symbols_index) or
                        symbols_index[index_symbol] > (line + 1)):
                    index -= 1
                belongs_to_class = symbols_simplified[index_symbol][1][2]
                if belongs_to_class:
                    self.insertAt("self", line, index)
                    index += 4
                    if self.selected_text != "":
                        self.insertAt(", ", line, index)
                        index += 2
            self.insertAt(self.selected_text, line, index)
            self.setCursorPosition(line, index)
        elif (token_buffer and (not is_unbalance) and
              self.selected_text):
            self.insertAt(self.selected_text, line, index)
        elif is_unbalance:
            next_char = text[index:index + 1].strip()
            if self.selected_text or next_char == "":
                self.insertAt(complementary_brace, line, index)
                self.insertAt(self.selected_text, line, index)

    def __complete_quotes(self, event):
        """
        Completion for single and double quotes, which since are simmetrical
        symbols used for different things can not be balanced as easily as
        braces or equivalent.
        """
        line, index = self.getCursorPosition()
        symbol = event.text()
        if symbol in settings.QUOTES:
            pre_context = self.__reverse_select_text_portion_from_offset(0, 3)
            if pre_context == 3 * symbol:
                self.insertAt(3 * symbol, line, index)
            else:
                self.insertAt(symbol, line, index)
            self.insertAt(self.selected_text, line, index)

    def clear_additional_carets(self):
        reset_pos = self.SendScintilla(QsciScintilla.SCI_GETCURRENTPOS)
        self.__positions = []
        self.SendScintilla(QsciScintilla.SCI_CLEARSELECTIONS)
        self.SendScintilla(QsciScintilla.SCI_SETSELECTION,
                           reset_pos, reset_pos)

    def keyPressEvent(self, event):
        #Completer pre key event
        #if self.completer.process_pre_key_event(event):
            #return
        #On Return == True stop the execution of this method
        if self.preKeyPress.get(event.key(), lambda x: False)(event):
            #emit a signal so that plugins can do their thing
            self.emit(SIGNAL("keyPressEvent(QEvent)"), event)
            return
        self.selected_text = self.selectedText()

        self._check_auto_copy_cut(event)
        # Clear additional carets if undo
        undo = event.matches(QKeySequence.Undo)
        if undo and self.__positions:
            self.clear_additional_carets()

        super(Editor, self).keyPressEvent(event)
        if event.key() == Qt.Key_Escape:
            self.clear_additional_carets()
        elif event.key() in (Qt.Key_Left, Qt.Key_Right,
                             Qt.Key_Up, Qt.Key_Down):
            if self.__positions:
                self.clear_additional_carets()

        if event.modifiers() == Qt.AltModifier:
            cur_pos = self.SendScintilla(QsciScintilla.SCI_GETCURRENTPOS)
            if not self.__positions:
                self.__positions = [cur_pos]

        self.postKeyPress.get(event.key(), lambda x: False)(event)

        #Completer post key event
        #self.completer.process_post_key_event(event)

        #emit a signal so that plugins can do their thing
        self.emit(SIGNAL("keyPressEvent(QEvent)"), event)

    def keyReleaseEvent(self, event):
        super(Editor, self).keyReleaseEvent(event)
        line, _ = self.getCursorPosition()
        if line != self._last_block_position:
            self._last_block_position = line
            self.emit(SIGNAL("currentLineChanged(int)"), line)

    def _check_auto_copy_cut(self, event):
        """Convenience method, when the user hits Ctrl+C or
        Ctrl+X with no text selected, we automatically select
        the entire line under the cursor."""
        copyOrCut = event.matches(QKeySequence.Copy) or \
            event.matches(QKeySequence.Cut)
        if copyOrCut and not self.hasSelectedText():
            line, index = self.getCursorPosition()
            length = self.lineLength(line)
            self.setSelection(line, 0, line, length)

    def _text_under_cursor(self):
        line, index = self.getCursorPosition()
        word = self.wordAtLineIndex(line, index)
        result = self._patIsWord.findall(word)
        word = result[0] if result else ''
        return word

    def wheelEvent(self, event, forward=True):
        if event.modifiers() == Qt.ControlModifier:
            if event.delta() > 0:
                self.zoom_in()
            elif event.delta() < 0:
                self.zoom_out()
            event.ignore()
        super(Editor, self).wheelEvent(event)

    def contextMenuEvent(self, event):
        popup_menu = self.createStandardContextMenu()

        menu_lint = QMenu(self.tr("Ignore Lint"))
        ignoreLineAction = menu_lint.addAction(
            self.tr("Ignore This Line"))
        ignoreSelectedAction = menu_lint.addAction(
            self.tr("Ignore Selected Area"))
        self.connect(ignoreLineAction, SIGNAL("triggered()"),
                     lambda: helpers.lint_ignore_line(self))
        self.connect(ignoreSelectedAction, SIGNAL("triggered()"),
                     lambda: helpers.lint_ignore_selection(self))
        popup_menu.insertSeparator(popup_menu.actions()[0])
        popup_menu.insertMenu(popup_menu.actions()[0], menu_lint)
        popup_menu.insertAction(popup_menu.actions()[0],
                                self.__actionFindOccurrences)
        #add extra menus (from Plugins)
        #lang = file_manager.get_file_extension(self.file_path)
        #extra_menus = self.EXTRA_MENU.get(lang, None)
        #if extra_menus:
            #popup_menu.addSeparator()
            # for menu in extra_menus:
                #popup_menu.addMenu(menu)
        # show menu
        popup_menu.exec_(event.globalPos())

    def mouseMoveEvent(self, event):
        position = event.pos()
        line = self.lineAt(position)
        checkers = self._neditable.sorted_checkers
        for items in checkers:
            checker, color, _ = items
            message = checker.message(line)
            if message:
                QToolTip.showText(self.mapToGlobal(position), message, self)
        if event.modifiers() == Qt.ControlModifier:
            self._navigation_highlight_active = True
            word = self.wordAtPoint(position)

            self.SendScintilla(QsciScintilla.SCI_SETINDICATORCURRENT,
                               self.__indicator_navigation)
            self.SendScintilla(QsciScintilla.SCI_INDICATORCLEARRANGE,
                               0, len(self.text()))
            text = self.text()
            word_length = len(word)
            index = text.find(word)
            while index != -1:
                self.SendScintilla(QsciScintilla.SCI_INDICATORFILLRANGE,
                                   index, word_length)
                index = text.find(word, index + 1)
        elif self._navigation_highlight_active:
            self._navigation_highlight_active = False
            self.SendScintilla(QsciScintilla.SCI_SETINDICATORCURRENT,
                               self.__indicator_navigation)
            self.SendScintilla(QsciScintilla.SCI_INDICATORCLEARRANGE,
                               0, len(self.text()))
        super(Editor, self).mouseMoveEvent(event)

    def mousePressEvent(self, event):
        #if self.completer.isVisible():
            #self.completer.hide_completer()
        super(Editor, self).mousePressEvent(event)
        if event.modifiers() == Qt.ControlModifier:
            self.go_to_definition()
        elif event.modifiers() == Qt.AltModifier:
            self.add_caret()
        else:
            self.clear_additional_carets()

        line, _ = self.getCursorPosition()
        if line != self._last_block_position:
            self._last_block_position = line
            self.emit(SIGNAL("currentLineChanged(int)"), line)

    # def mouseReleaseEvent(self, event):
        # super(Editor, self).mouseReleaseEvent(event)
        # if event.button() == Qt.LeftButton:
        #    self.highlight_selected_word()

    def dropEvent(self, event):
        if len(event.mimeData().urls()) > 0:
            path = event.mimeData().urls()[0].path()
            self.emit(SIGNAL("openDropFile(QString)"), path)
            event.ignore()
            event.mimeData = QMimeData()
        super(Editor, self).dropEvent(event)
        self.undo()

    def go_to_definition(self):
        line, index = self.getCursorPosition()
        word = self.wordAtLineIndex(line, index)
        text = self.text(line)
        brace_pos = text.find("(", index)
        back_text = text[:index]
        dot_pos = back_text.rfind(".")
        prop_pos = back_text.rfind("@")
        is_function = (brace_pos != -1 and
                       text[index:brace_pos + 1] in ("%s(" % word))
        is_attribute = (dot_pos != -1 and
                        text[dot_pos:index] in (".%s" % word))
        is_property = (prop_pos != -1 and
                       text[prop_pos:index] in ("@%s" % word))
        if is_function or is_property:
            self.emit(SIGNAL("locateFunction(QString, QString, bool)"),
                      word, self.file_path, False)
        elif is_attribute:
            self.emit(SIGNAL("locateFunction(QString, QString, bool)"),
                      word, self.file_path, True)

    def __tokenize_text(self, text):
        invalid_syntax = False
        token_buffer = []
        try:
            for tkn_type, tkn_rep, tkn_begin, tkn_end, _ in \
                    generate_tokens(StringIO(text).readline):
                token_buffer.append((tkn_type, tkn_rep, tkn_begin, tkn_end))
        except (TokenError, IndentationError, SyntaxError):
            invalid_syntax = True
        return (invalid_syntax, token_buffer)

    def highlight_selected_word(self, word_find=None, case_sensitive=True,
                                reset=False):
        """Highlight selected variable"""
        self.SendScintilla(QsciScintilla.SCI_SETINDICATORCURRENT,
                           self.__indicator_word)
        word = self._text_under_cursor()
        if word_find is not None:
            word = word_find

        if word != self._selected_word and not reset:
            self.SendScintilla(QsciScintilla.SCI_INDICATORCLEARRANGE, 0,
                               len(self.text()))
            self._selected_word = word
            word_length = len(self._selected_word)
            text = self.text()
            search = self._selected_word
            if not case_sensitive:
                search = search.lower()
                text = text.lower()
            index = text.find(search)
            self.search_lines = []  # Restore search lines
            appendLine = self.search_lines.append
            while index != -1 and word:
                line = self.SendScintilla(QsciScintilla.SCI_LINEFROMPOSITION,
                                          index)
                if line not in self.search_lines:
                    appendLine(line)
                self.SendScintilla(QsciScintilla.SCI_INDICATORFILLRANGE,
                                   index, word_length)
                index = text.find(search, index + 1)
            # FIXME:
            if self._docmap is not None:
                self._docmap.update()
        elif ((word == self._selected_word) and (word_find is None)) or reset:
            self.SendScintilla(QsciScintilla.SCI_INDICATORCLEARRANGE, 0,
                               len(self.text()))
            self._selected_word = None

    def to_upper(self):
        self.SendScintilla(QsciScintilla.SCI_BEGINUNDOACTION, 1)
        if self.hasSelectedText():
            text = self.selectedText().upper()
            self.replaceSelectedText(text)
        self.SendScintilla(QsciScintilla.SCI_ENDUNDOACTION, 1)

    def to_lower(self):
        self.SendScintilla(QsciScintilla.SCI_BEGINUNDOACTION, 1)
        if self.hasSelectedText():
            text = self.selectedText().lower()
            self.replaceSelectedText(text)
        self.SendScintilla(QsciScintilla.SCI_ENDUNDOACTION, 1)

    def to_title(self):
        self.SendScintilla(QsciScintilla.SCI_BEGINUNDOACTION, 1)
        if self.hasSelectedText():
            text = self.selectedText().title()
            self.replaceSelectedText(text)
        self.SendScintilla(QsciScintilla.SCI_ENDUNDOACTION, 1)


def create_editor(neditable):
    # has_editor = neditable.editor is not None
    editor = Editor(neditable)
    # ext = neditable.nfile.file_ext()
    # if not has_editor or syntax:
    #    editor.register_syntax(ext, syntax)
    # else:
    #    editor.highlighter = neditable.editor.highlighter

    return editor
