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
#lint:disable
try:
    from urllib.request import urlopen
    from urllib.error import URLError
except ImportError:
    from urllib2 import urlopen
    from urllib2 import URLError
#lint:enable
import threading

from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QSpacerItem
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QDialog
from PyQt5.QtQuickWidgets import QQuickWidget
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from ninja_ide import resources
from ninja_ide.core.file_handling import file_manager
from ninja_ide.tools import ui_tools
from ninja_ide.tools import json_manager


# Every space of this block is important, edit with care
old_default_lang_text = 'ListElement {\
\n        language: "LANGUAGE NAME HERE"\
\n        country: "COUNTRY NAME HERE"\
\n        status: "Default"\
\n    }'

old_curr_langs_text = 'ListElement {\
\n        language: "LANGUAGE NAME HERE"\
\n        country: "COUNTRY NAME HERE"\
\n        status: "set as Default"\
\n    }'

repl_old_default_lang_text = 'ListElement {\
\n        language: "LANGUAGE NAME HERE"\
\n        country: "COUNTRY NAME HERE"\
\n        status: "set as Default"\
\n    }'

repl_old_curr_langs_text = 'ListElement {\
\n        language: "LANGUAGE NAME HERE"\
\n        country: "COUNTRY NAME HERE"\
\n        status: "Default"\
\n    }'

# Available lang replacement
old_avail_lang_text = 'ListElement {\
\n        language: "LANGUAGE NAME HERE"\
\n        country: "COUNTRY NAME HERE"\
\n    }'

# Adding to Installed Lang replacement
installed_lang_text = '    }\
\n\
\n    ListElement {\
\n        language: "LANGUAGE NAME HERE"\
\n        country: "COUNTRY NAME HERE"\
\n        status: "set as Default"\
\n    }\
\n}'


# install to replace
installed_to_find = '    }\
\n}'

class LanguagesManagerWidget(QDialog):

    def __init__(self, parent):
        QDialog.__init__(self, parent, Qt.Dialog)
        self.setWindowTitle(self.tr("Language Manager"))
        self.resize(700, 500)

        self.vbox = QVBoxLayout(self)
        self.q = QQuickWidget()

        self.q.rootContext().setContextProperty(
            "theme", resources.QML_COLORS)
        self.q.rootContext().setContextProperty(
            "resources", resources)
        self.q.rootContext().setContextProperty(
            "parentClass", self)
        self.q.setMinimumWidth(400)
        self.q.setResizeMode(QQuickWidget.SizeRootObjectToView)
        self.q.setSource(ui_tools.get_qml_resource("LanguageManager.qml"))
        self.root = self.q.rootObject()
        self.overlay = ui_tools.Overlay(self)

        self.vbox.addWidget(self.q)

        self.language = ''
        self.country = ''

        """/*
        self._tabs = QTabWidget()
        vbox.addWidget(self._tabs)
        # Footer
        hbox = QHBoxLayout()
        btn_close = QPushButton(self.tr('Close'))
        btnReload = QPushButton(self.tr("Reload"))
        hbox.addWidget(btn_close)
        hbox.addSpacerItem(QSpacerItem(1, 0, QSizePolicy.Expanding))
        hbox.addWidget(btnReload)
        vbox.addLayout(hbox)
        self.overlay = ui_tools.Overlay(self)
        self.overlay.show()

        self._languages = []
        self._loading = True
        self.downloadItems = []

        #Load Themes with Thread
        btnReload.clicked.connect(self._reload_languages)
        self._thread = ui_tools.ThreadExecution(self.execute_thread)
        self._thread.finished.connect(self.load_languages_data)
        btn_close.clicked.connect(self.close)
        self._reload_languages()
        */"""
    status = pyqtSignal(str, arguments=["pinging"])
    downloading = pyqtSignal(int, arguments=["downloading_lang"])
    downloadFinish = pyqtSignal(str, arguments=["finishUp"])

    @pyqtSlot(str, str, str, str)
    def set_as_default(self, c_language, c_lang_coun, language, lang_coun):

        print(c_language, c_lang_coun, language, lang_coun)

        # get current language
        curr_lang_filename = c_language + "_translations.py"
        curr_lang_path = os.path.join(resources.LANGS, curr_lang_filename)

        # set current language as default
        lang_filename = language + "_translations.py"
        old_path = os.path.join(resources.LANGS,  lang_filename)
        translation_default = "translations.py"
        new_path = os.path.join(resources.LANGS,  translation_default)
        os.rename(old_path, new_path)
        c_tr_file = os.path.join(resources.PRJ_PATH, 'translations.py')
        # copy back to languages folder
        os.rename(c_tr_file, curr_lang_path)
        # now copy the users preferred language here instead
        os.rename(new_path, c_tr_file)
        self._rebuild_model(c_language, c_lang_coun, language, lang_coun)


    def _rebuild_model(self, c_language, c_lang_coun, language, lang_coun):
        # get statements
        variables = self._replace_langs(c_language, c_lang_coun, language,
                                        lang_coun)

        old_def, repl_old_def, new_lang, new_def = variables

        model = os.path.join(resources.QML_FILES, "InstalledLangDataModel.qml")

        # read the file
        with open(model, encoding='utf-8', mode='r') as model_file:
            data = model_file.read()

        final = self._replaces(data, old_def, repl_old_def, new_lang, new_def)

        # Now re write the file
        with open(model, encoding='utf-8', mode='w') as model_file:
            model_file.write(final)

    def _replace_langs(self, old_default, old_default_cc, new_default,
                        new_default_cc) :
        # Here we are replacing the sort of vars with thw translation langs.
        fixed0 = old_default_lang_text.replace('LANGUAGE NAME HERE',
                                                old_default )
        fixed01 = fixed0.replace('COUNTRY NAME HERE', old_default_cc)
        fixed2 = repl_old_default_lang_text.replace('COUNTRY NAME HERE',
                                                     old_default_cc )
        fixed21 = fixed2.replace('LANGUAGE NAME HERE', old_default)

        fixed3 = old_curr_langs_text.replace('LANGUAGE NAME HERE', new_default)
        fixed31 = fixed3.replace('COUNTRY NAME HERE', new_default_cc)
        fixed4 = repl_old_curr_langs_text.replace('COUNTRY NAME HERE',
                                                  new_default_cc)
        fixed41 = fixed4.replace('LANGUAGE NAME HERE', new_default)
        return fixed01, fixed21, fixed31, fixed41

    def _replaces(self, data, old_def, repl_old_def, new_lang, new_def):
        replace1 = data.replace(old_def, repl_old_def)
        replace2 = replace1.replace(new_lang, new_def)
        return replace2

    def downloading_lang(self):
        language_url = resources.LANGUAGES_URL + '/' \
        + self.language + "_translations.py"
        try:
            req = urlopen('http://localhost/translations/German_translations.py')
            resp = req.read()
            data = resp.decode('utf-8')
            
            if data:
                self.downloading.emit(100)
                self.finishUp(data)
        except:
            print('Exception one')

    def finishUp(self, data):
        print('finish UP')
        local_lang_file = self.language + "_translations.py"
        local_path = os.path.join(resources.LANGS, local_lang_file)

        # Save the Translation.py
        with open(local_path, mode='w') as file:
            file.write(data)
        print('data up')
        # replace old available langs
        available_file = os.path.join(resources.QML_FILES,
                                      'AvailableLangDataModel.qml')
        with open(available_file, mode='r', encoding='utf-8') as avail:
            read = avail.read()
        print('avaial gotten')
        avai1 = old_avail_lang_text.replace('LANGUAGE NAME HERE', self.language)
        avail_lang_text = avai1.replace('COUNTRY NAME HERE', self.country)
        fixed = read.replace(avail_lang_text, '')
        print('fixed up')
        with open(available_file, mode='w', encoding='utf-8') as available:
            available.write(fixed)

        print('avail written')
        # replace install langs
        installed_file = os.path.join(resources.QML_FILES,
                                      'InstalledLangDataModel.qml')
        with open(installed_file, mode='r', encoding='utf-8') as inst:
            install_read = inst.read()
        print('inst read')
        ins1 = installed_lang_text.replace('LANGUAGE NAME HERE', self.language)
        print(ins1)
        inst_lang_text = ins1.replace('COUNTRY NAME HERE', self.country)
        # There was a problem here
        fixed1 = install_read.replace(installed_to_find, inst_lang_text)
        with open(installed_file, mode='w', encoding='utf-8') as installed:
            installed.write(fixed1)
        print('inst write')

        self.downloadFinish.emit('Success')

    @pyqtSlot(str, str)
    def start_download(self, lang, cc):
        print('start_download')
        self.language = lang
        self.country = cc
        download_thread = threading.Thread(target=self.pinging)
        download_thread.start()

    def pinging(self):
        print('pinging')
        status_comment = "Connecting to http://www.ninja-ide.org..."
        self.status.emit(status_comment)

        # open
        try:
            req = urlopen('http://localhost/translations/German_translations.py')
            status_comment = "Connected to http://www.ninja-ide.org..."
            self.status.emit(status_comment)
            self.downloading_lang()
        except:
            pass

    def _reload_languages(self):
        self.overlay.show()
        self._loading = True
        self._thread.execute = self.execute_thread
        self._thread.start()

    def load_languages_data(self):
        if self._loading:
            self._tabs.clear()
            self._languageWidget = LanguageWidget(self, self._languages)
            self._tabs.addTab(self._languageWidget,
                self.tr("Languages"))
            self._loading = False
        self.overlay.hide()
        self._thread.wait()

    def download_language(self, language):
        self.overlay.show()
        self.downloadItems = language
        self._thread.execute = self._download_language_thread
        self._thread.start()

    def resizeEvent(self, event):
        self.overlay.resize(event.size())
        event.accept()

    def execute_thread(self):
        try:
            descriptor_languages = urlopen(resources.LANGUAGES_URL)
            languages = json_manager.parse(descriptor_languages)
            languages = [[name, languages[name]] for name in languages]
            local_languages = self.get_local_languages()
            languages = [languages[i] for i in range(len(languages)) if
                os.path.basename(languages[i][1]) not in local_languages]
            self._languages = languages
        except URLError:
            self._languages = []

    def get_local_languages(self):
        if not file_manager.folder_exists(resources.LANGS_DOWNLOAD):
            file_manager.create_tree_folders(resources.LANGS_DOWNLOAD)
        languages = os.listdir(resources.LANGS_DOWNLOAD) + \
            os.listdir(resources.LANGS)
        languages = [s for s in languages if s.lower().endswith('.qm')]
        return languages

    def _download_language_thread(self):
        for d in self.downloadItems:
            self.download(d[1], resources.LANGS_DOWNLOAD)

    def download(self, url, folder):
        fileName = os.path.join(folder, os.path.basename(url))
        try:
            content = urlopen(url)
            with open(fileName, 'wb') as f:
                f.write(content.read())
        except URLError:
            return


class LanguageWidget(QWidget):

    def __init__(self, parent, languages):
        QWidget.__init__(self, parent)
        self._parent = parent
        self._languages = languages
        vbox = QVBoxLayout(self)
        self._table = ui_tools.CheckableHeaderTable(1, 2)
        self._table.removeRow(0)
        vbox.addWidget(self._table)
        ui_tools.load_table(self._table,
            [self.tr('Language'), self.tr('URL')], self._languages)
        btnUninstall = QPushButton(self.tr('Download'))
        btnUninstall.setMaximumWidth(100)
        vbox.addWidget(btnUninstall)
        self._table.setColumnWidth(0, 200)
        self._table.setSortingEnabled(True)
        self._table.setAlternatingRowColors(True)
        btnUninstall.clicked.connect(self._download_language)

    def _download_language(self):
        languages = ui_tools.remove_get_selected_items(self._table,
            self._languages)
        self._parent.download_language(languages)
