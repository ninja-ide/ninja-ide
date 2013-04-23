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

import webbrowser
from copy import copy
from distutils import version

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QFormLayout
from PyQt4.QtGui import QFileDialog
from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QTextBrowser
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QTableWidget
from PyQt4.QtGui import QTabWidget
from PyQt4.QtGui import QPlainTextEdit
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QSpacerItem
from PyQt4.QtGui import QSizePolicy
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QIcon
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QThread

from ninja_ide import resources
from ninja_ide.core import plugin_manager
from ninja_ide.core import file_manager
from ninja_ide.tools import ui_tools

from ninja_ide.tools.logger import NinjaLogger

logger = NinjaLogger('ninja_ide.gui.dialogs.plugin_manager')

HTML_STYLE = """
<html>
<body>
    <h2>{name}</h2>
    <p><i>Version: {version}</i></p>
    <h3>{description}</h3>
    <br><p><b>Author:</b> {author}</p>
    <p>More info about the Plugin: <a href='{link}'>Website</a></p>
</body>
</html>
"""


def _get_plugin(plugin_name, plugin_list):
    plugin = None
    for plug in plugin_list:
        if plug["name"] == plugin_name:
            plugin = plug
            break
    return plugin


def _format_for_table(plugins):
    return [[data["name"], data["version"], data["description"],
        data["authors"], data["home"]] for data in plugins]


class PluginsManagerWidget(QDialog):

    def __init__(self, parent):
        QDialog.__init__(self, parent, Qt.Dialog)
        self.setWindowTitle(self.tr("Plugins Manager"))
        self.resize(700, 600)

        vbox = QVBoxLayout(self)
        self._tabs = QTabWidget()
        vbox.addWidget(self._tabs)
        self._txt_data = QTextBrowser()
        self._txt_data.setOpenLinks(False)
        vbox.addWidget(QLabel(self.tr("Description:")))
        vbox.addWidget(self._txt_data)
        # Footer
        hbox = QHBoxLayout()
        btn_close = QPushButton(self.tr('Close'))
        btnReload = QPushButton(self.tr("Reload"))
        hbox.addWidget(btn_close)
        hbox.addSpacerItem(QSpacerItem(1, 0, QSizePolicy.Expanding))
        hbox.addWidget(btnReload)
        vbox.addLayout(hbox)
        self.overlay = ui_tools.Overlay(self)
        self.overlay.hide()

        self._oficial_available = []
        self._community_available = []
        self._locals = []
        self._updates = []
        self._loading = True
        self._requirements = {}

        self.connect(btnReload, SIGNAL("clicked()"), self._reload_plugins)
        self.thread = ThreadLoadPlugins(self)
        self.connect(self.thread, SIGNAL("finished()"),
            self._load_plugins_data)
        self.connect(self.thread, SIGNAL("plugin_downloaded(PyQt_PyObject)"),
            self._after_download_plugin)
        self.connect(self.thread,
            SIGNAL("plugin_manually_installed(PyQt_PyObject)"),
            self._after_manual_install_plugin)
        self.connect(self.thread, SIGNAL("plugin_uninstalled(PyQt_PyObject)"),
            self._after_uninstall_plugin)
        self.connect(self._txt_data, SIGNAL("anchorClicked(const QUrl&)"),
            self._open_link)
        self.connect(btn_close, SIGNAL('clicked()'), self.close)
        self.overlay.show()
        self._reload_plugins()

    def show_plugin_info(self, data):
        plugin_description = data[2].replace('\n', '<br>')
        html = HTML_STYLE.format(name=data[0],
            version=data[1], description=plugin_description,
            author=data[3], link=data[4])
        self._txt_data.setHtml(html)

    def _open_link(self, url):
        link = url.toString()
        if link.startswith('/plugins/'):
            link = 'http://ninja-ide.org' + link
        webbrowser.open(link)

    def _reload_plugins(self):
        self.overlay.show()
        self._loading = True
        self.thread.runnable = self.thread.collect_data_thread
        self.thread.start()

    def _after_manual_install_plugin(self, plugin):
        data = {}
        data['name'] = plugin[0]
        data['version'] = plugin[1]
        data['description'] = ''
        data['authors'] = ''
        data['home'] = ''
        self._installedWidget.add_table_items([data])

    def _after_download_plugin(self, plugin):
        oficial_plugin = _get_plugin(plugin[0], self._oficial_available)
        community_plugin = _get_plugin(plugin[0], self._community_available)
        if oficial_plugin:
            self._installedWidget.add_table_items([oficial_plugin])
            self._availableOficialWidget.remove_item(plugin[0])
        elif community_plugin:
            self._installedWidget.add_table_items([community_plugin])
            self._availableCommunityWidget.remove_item(plugin[0])

    def _after_uninstall_plugin(self, plugin):
        #make available the plugin corresponding to the type
        oficial_plugin = _get_plugin(plugin[0], self._oficial_available)
        community_plugin = _get_plugin(plugin[0], self._community_available)
        if oficial_plugin:
            self._availableOficialWidget.add_table_items([oficial_plugin])
            self._installedWidget.remove_item(plugin[0])
        elif community_plugin:
            self._availableCommunityWidget.add_table_items([community_plugin])
            self._installedWidget.remove_item(plugin[0])

    def _load_plugins_data(self):
        if self._loading:
            self._tabs.clear()
            self._updatesWidget = UpdatesWidget(self, copy(self._updates))
            self._availableOficialWidget = AvailableWidget(self,
                copy(self._oficial_available))
            self._availableCommunityWidget = AvailableWidget(self,
                copy(self._community_available))
            self._installedWidget = InstalledWidget(self, copy(self._locals))
            self._tabs.addTab(self._availableOficialWidget,
                self.tr("Official Available"))
            self._tabs.addTab(self._availableCommunityWidget,
                self.tr("Community Available"))
            self._tabs.addTab(self._updatesWidget, self.tr("Updates"))
            self._tabs.addTab(self._installedWidget, self.tr("Installed"))
            self._manualWidget = ManualInstallWidget(self)
            self._tabs.addTab(self._manualWidget, self.tr("Manual Install"))
            self._loading = False
        self.overlay.hide()
        self.thread.wait()

    def download_plugins(self, plugs):
        """
        Install
        """
        self.overlay.show()
        self.thread.plug = plugs
        #set the function to run in the thread
        self.thread.runnable = self.thread.download_plugins_thread
        self.thread.start()

    def install_plugins_manually(self, plug):
        """Install plugin from local zip."""
        self.overlay.show()
        self.thread.plug = plug
        #set the function to run in the thread
        self.thread.runnable = self.thread.manual_install_plugins_thread
        self.thread.start()

    def mark_as_available(self, plugs):
        """
        Uninstall
        """
        self.overlay.show()
        self.thread.plug = plugs
        #set the function to run in the thread
        self.thread.runnable = self.thread.uninstall_plugins_thread
        self.thread.start()

    def update_plugin(self, plugs):
        """
        Update
        """
        self.overlay.show()
        self.thread.plug = plugs
        #set the function to run in the thread
        self.thread.runnable = self.thread.update_plugin_thread
        self.thread.start()

    def reset_installed_plugins(self):
        local_plugins = plugin_manager.local_plugins()
        plugins = _format_for_table(local_plugins)
        self._installedWidget.reset_table(plugins)

    def resizeEvent(self, event):
        self.overlay.resize(event.size())
        event.accept()


class UpdatesWidget(QWidget):
    """
    This widget show the availables plugins to update
    """

    def __init__(self, parent, updates):
        QWidget.__init__(self, parent)
        self._parent = parent
        self._updates = updates
        vbox = QVBoxLayout(self)
        self._table = QTableWidget(1, 2)
        self._table.removeRow(0)
        self._table.setSelectionMode(QTableWidget.SingleSelection)
        self._table.setColumnWidth(0, 500)
        vbox.addWidget(self._table)
        ui_tools.load_table(self._table, (self.tr('Name'), self.tr('Version')),
            _format_for_table(updates))
        btnUpdate = QPushButton(self.tr("Update"))
        btnUpdate.setMaximumWidth(100)
        vbox.addWidget(btnUpdate)

        self.connect(btnUpdate, SIGNAL("clicked()"), self._update_plugins)
        self.connect(self._table, SIGNAL("itemSelectionChanged()"),
            self._show_item_description)

    def _show_item_description(self):
        item = self._table.currentItem()
        if item is not None:
            data = list(item.data(Qt.UserRole))
            self._parent.show_plugin_info(data)

    def _update_plugins(self):
        data = _format_for_table(self._updates)
        plugins = ui_tools.remove_get_selected_items(self._table, data)
        #get the download link of each plugin
        for p_row in plugins:
            #search the plugin
            for p_dict in self._updates:
                if p_dict["name"] == p_row[0]:
                    p_data = p_dict
                    break
            #append the downlod link
            p_row.append(p_data["download"])
        self._parent.update_plugin(plugins)


class AvailableWidget(QWidget):

    def __init__(self, parent, available):
        QWidget.__init__(self, parent)
        self._parent = parent
        self._available = available
        vbox = QVBoxLayout(self)
        self._table = QTableWidget(1, 2)
        self._table.setSelectionMode(QTableWidget.SingleSelection)
        self._table.removeRow(0)
        vbox.addWidget(self._table)
        ui_tools.load_table(self._table, (self.tr('Name'), self.tr('Version')),
            _format_for_table(available))
        self._table.setColumnWidth(0, 500)
        hbox = QHBoxLayout()
        btnInstall = QPushButton(self.tr('Install'))
        btnInstall.setMaximumWidth(100)
        hbox.addWidget(btnInstall)
        hbox.addWidget(QLabel(self.tr("NINJA needs to be restarted for "
            "changes to take effect.")))
        vbox.addLayout(hbox)

        self.connect(btnInstall, SIGNAL("clicked()"), self._install_plugins)
        self.connect(self._table, SIGNAL("itemSelectionChanged()"),
            self._show_item_description)

    def _show_item_description(self):
        item = self._table.currentItem()
        if item is not None:
            data = list(item.data(Qt.UserRole))
            self._parent.show_plugin_info(data)

    def _install_plugins(self):
        data = _format_for_table(self._available)
        plugins = ui_tools.remove_get_selected_items(self._table, data)
        #get the download link of each plugin
        for p_row in plugins:
            #search the plugin
            for p_dict in self._available:
                if p_dict["name"] == p_row[0]:
                    p_data = p_dict
                    break
            #append the downlod link
            p_row.append(p_data["download"])
        #download
        self._parent.download_plugins(plugins)

    def remove_item(self, plugin_name):
        plugin = _get_plugin(plugin_name, self._available)
        self._available.remove(plugin)

    def _install_external(self):
        if self._link.text().isEmpty():
            QMessageBox.information(self, self.tr("External Plugins"),
                self.tr("URL from Plugin missing..."))
            return
        plug = [
            file_manager.get_module_name(str(self._link.text())),
            'External Plugin',
            '1.0',
            str(self._link.text())]
        self.parent().download_plugins(plug)
        self._link.setText('')

    def add_table_items(self, plugs):
        self._available += plugs
        data = _format_for_table(self._available)
        ui_tools.load_table(self._table, (self.tr('Name'), self.tr('Version')),
            data)


class InstalledWidget(QWidget):
    """
    This widget show the installed plugins
    """

    def __init__(self, parent, installed):
        QWidget.__init__(self, parent)
        self._parent = parent
        self._installed = installed
        vbox = QVBoxLayout(self)
        self._table = QTableWidget(1, 2)
        self._table.setSelectionMode(QTableWidget.SingleSelection)
        self._table.removeRow(0)
        vbox.addWidget(self._table)
        ui_tools.load_table(self._table, (self.tr('Name'), self.tr('Version')),
            _format_for_table(installed))
        self._table.setColumnWidth(0, 500)
        btnUninstall = QPushButton(self.tr("Uninstall"))
        btnUninstall.setMaximumWidth(100)
        vbox.addWidget(btnUninstall)

        self.connect(btnUninstall, SIGNAL("clicked()"),
            self._uninstall_plugins)
        self.connect(self._table, SIGNAL("itemSelectionChanged()"),
            self._show_item_description)

    def _show_item_description(self):
        item = self._table.currentItem()
        if item is not None:
            data = list(item.data(Qt.UserRole))
            self._parent.show_plugin_info(data)

    def remove_item(self, plugin_name):
        plugin = _get_plugin(plugin_name, self._installed)
        self._installed.remove(plugin)

    def add_table_items(self, plugs):
        self._installed += plugs
        data = _format_for_table(self._installed)
        ui_tools.load_table(self._table, (self.tr('Name'), self.tr('Version')),
            data)

    def _uninstall_plugins(self):
        data = _format_for_table(self._installed)
        plugins = ui_tools.remove_get_selected_items(self._table, data)
        self._parent.mark_as_available(plugins)

    def reset_table(self, installed):
        self._installed = installed
        while self._table.rowCount() > 0:
            self._table.removeRow(0)
        ui_tools.load_table(self._table, (self.tr('Name'), self.tr('Version')),
            self._installed)


class ManualInstallWidget(QWidget):

    def __init__(self, parent):
        super(ManualInstallWidget, self).__init__()
        self._parent = parent
        vbox = QVBoxLayout(self)
        form = QFormLayout()
        self._txtName = QLineEdit()
        self._txtVersion = QLineEdit()
        form.addRow(self.tr("Plugin Name:"), self._txtName)
        form.addRow(self.tr("Plugin Version:"), self._txtVersion)
        vbox.addLayout(form)
        hPath = QHBoxLayout()
        self._txtFilePath = QLineEdit()
        self._btnFilePath = QPushButton(QIcon(resources.IMAGES['open']), '')
        hPath.addWidget(QLabel(self.tr("Plugin File:")))
        hPath.addWidget(self._txtFilePath)
        hPath.addWidget(self._btnFilePath)
        vbox.addLayout(hPath)
        vbox.addSpacerItem(QSpacerItem(0, 1, QSizePolicy.Expanding,
            QSizePolicy.Expanding))

        hbox = QHBoxLayout()
        hbox.addSpacerItem(QSpacerItem(1, 0, QSizePolicy.Expanding))
        self._btnInstall = QPushButton(self.tr("Install"))
        hbox.addWidget(self._btnInstall)
        vbox.addLayout(hbox)

        #Signals
        self.connect(self._btnFilePath,
            SIGNAL("clicked()"), self._load_plugin_path)
        self.connect(self._btnInstall, SIGNAL("clicked()"),
            self.install_plugin)

    def _load_plugin_path(self):
        path = QFileDialog.getOpenFileName(self, self.tr("Select Plugin Path"))
        if path:
            self._txtFilePath.setText(path)

    def install_plugin(self):
        if self._txtFilePath.text() and self._txtName.text():
            plug = []
            plug.append(self._txtName.text())
            plug.append(self._txtVersion.text())
            plug.append('')
            plug.append('')
            plug.append('')
            plug.append(self._txtFilePath.text())
            self._parent.install_plugins_manually([plug])


class ThreadLoadPlugins(QThread):
    """
    This thread makes the HEAVY work!
    """

    def __init__(self, manager):
        super(ThreadLoadPlugins, self).__init__()
        self._manager = manager
        #runnable hold a function to call!
        self.runnable = self.collect_data_thread
        #this attribute contains the plugins to download/update
        self.plug = None

    def run(self):
        self.runnable()
        self.plug = None

    def collect_data_thread(self):
        """
        Collects plugins info from NINJA-IDE webservice interface
        """
        #get availables OFICIAL plugins
        oficial_available = plugin_manager.available_oficial_plugins()
        #get availables COMMUNITIES plugins
        community_available = plugin_manager.available_community_plugins()
        #get locals plugins
        local_plugins = plugin_manager.local_plugins()
        updates = []
        #Check por update the already installed plugin
        for local_data in local_plugins:
            ava = None
            plug_oficial = _get_plugin(local_data["name"], oficial_available)
            plug_community = _get_plugin(local_data["name"],
                community_available)
            if plug_oficial:
                ava = plug_oficial
                oficial_available = [p for p in oficial_available
                        if p["name"] != local_data["name"]]
            elif plug_community:
                ava = plug_community
                community_available = [p for p in community_available
                        if p["name"] != local_data["name"]]
            #check versions
            if ava:
                available_version = version.LooseVersion(str(ava["version"]))
            else:
                available_version = version.LooseVersion('0.0')
            local_version = version.LooseVersion(str(local_data["version"]))
            if available_version > local_version:
                #this plugin has an update
                updates.append(ava)
        #set manager attributes
        self._manager._oficial_available = oficial_available
        self._manager._community_available = community_available
        self._manager._locals = local_plugins
        self._manager._updates = updates

    def download_plugins_thread(self):
        """
        Downloads some plugins
        """
        for p in self.plug:
            try:
                name = plugin_manager.download_plugin(p[5])
                p.append(name)
                plugin_manager.update_local_plugin_descriptor((p, ))
                req_command = plugin_manager.has_dependencies(p)
                if req_command[0]:
                    self._manager._requirements[p[0]] = req_command[1]
                self.emit(SIGNAL("plugin_downloaded(PyQt_PyObject)"), p)
            except Exception as e:
                logger.warning("Impossible to install (%s): %s", p[0], e)

    def manual_install_plugins_thread(self):
        """
        Install a plugin from the a file.
        """
        for p in self.plug:
            try:
                name = plugin_manager.manual_install(p[5])
                p.append(name)
                plugin_manager.update_local_plugin_descriptor((p, ))
                req_command = plugin_manager.has_dependencies(p)
                if req_command[0]:
                    self._manager._requirements[p[0]] = req_command[1]
                self.emit(
                    SIGNAL("plugin_manually_installed(PyQt_PyObject)"), p)
            except Exception as e:
                logger.warning("Impossible to install (%s): %s", p[0], e)

    def uninstall_plugins_thread(self):
        for p in self.plug:
            try:
                plugin_manager.uninstall_plugin(p)
                self.emit(SIGNAL("plugin_uninstalled(PyQt_PyObject)"), p)
            except Exception as e:
                logger.warning("Impossible to uninstall (%s): %s", p[0], e)

    def update_plugin_thread(self):
        """
        Updates some plugins
        """
        for p in self.plug:
            try:
                plugin_manager.uninstall_plugin(p)
                name = plugin_manager.download_plugin(p[5])
                p.append(name)
                plugin_manager.update_local_plugin_descriptor([p])
                self._manager.reset_installed_plugins()
            except Exception as e:
                logger.warning("Impossible to update (%s): %s", p[0], e)


class DependenciesHelpDialog(QDialog):
    def __init__(self, requirements_dict):
        super(DependenciesHelpDialog, self).__init__()
        self.setWindowTitle(self.tr("Plugin requirements"))
        self.resize(525, 400)
        vbox = QVBoxLayout(self)
        label = QLabel(self.tr("""It seems that some plugins needs some
            dependencies to be solved to work properly, you should install them
            as follows using a Terminal"""))
        vbox.addWidget(label)
        self._editor = QPlainTextEdit()
        self._editor.setReadOnly(True)
        vbox.addWidget(self._editor)
        hbox = QHBoxLayout()
        btnAccept = QPushButton(self.tr("Accept"))
        btnAccept.setMaximumWidth(100)
        hbox.addWidget(btnAccept)
        vbox.addLayout(hbox)
        #signals
        self.connect(btnAccept, SIGNAL("clicked()"), self.close)

        command_tmpl = "<%s>:\n%s\n"
        for name, description in list(requirements_dict.items()):
            self._editor.insertPlainText(command_tmpl % (name, description))
