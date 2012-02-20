# -*- coding: utf-8 -*-

from __future__ import absolute_import

from ninja_ide.resources import COLOR_SCHEME


QSS_STYLES = {
    'editor': """QPlainTextEdit {
            font-family: monospace;
            font-size: 10;
            color: black;
            background-color: white;
            selection-color: white;
            selection-background-color: #437DCD;
        }""",
    'toolbar-default': """QToolBar::separator {
            border-radius: 10px;
            background: gray;
            width: 2px; /* when vertical */
            height: 2px; /* when horizontal */
        }""",
    'recent-project': """WebPluginList {
            padding-top: 5px;
            color: black;
            background-color: white;
            selection-color: blue;
            border-radius: 10px;
            selection-background-color: #437DCD;
        }
        WebPluginList:Item:hover {
            color: black;
            border-radius: 10px;
            border-style: solid;
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 #FAFBFE, stop: 1 #6181E0);
        }""",
    'recent-project-list': """QPushButton, QLineEdit {
            background:transparent;
            border:none;
            border-radius: 10px;
            color: black;
        }""",
    'tab-navigator': """QPushButton{
            border:none;
        }
        QPushButton:hover{
            border-radius: 5px;
            border-style: solid;
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 #0a0b0b, stop: 1 #606161);
        }
        QPushButton:pressed{
            border-radius: 5px;
            border-style: solid;
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                stop: 0 #606161, stop: 1 #0a0b0b);
        }
        """,
    'toolbar-customization': """QToolBar{
            border-radius: 5px;
            border-width: 1px;
            border-color:gray;
            border-style: solid;
        }""",
     'minimap': """QPlainTextEdit {
             border: none;
             border-left: 1px solid grey;
             border-top: 1px solid grey;
             border-bottom: 1px solid grey;
             margin-right: 5px;
         }"""}


def set_style(widget, sty):
    widget.setStyleSheet(QSS_STYLES.get(sty, ''))


def set_editor_style(widget, scheme):
    css = 'QPlainTextEdit {color: %s; background-color: %s;' \
        'selection-color: %s; selection-background-color: %s;}' \
        % (scheme.get('editor-text', COLOR_SCHEME['editor-text']),
        scheme.get('editor-background',
            COLOR_SCHEME['editor-background']),
        scheme.get('editor-selection-color',
            COLOR_SCHEME['editor-selection-color']),
        scheme.get('editor-selection-background',
            COLOR_SCHEME['editor-selection-background']))
    widget.setStyleSheet(css)
