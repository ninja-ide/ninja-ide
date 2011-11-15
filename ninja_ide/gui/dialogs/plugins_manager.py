# *-* coding: utf-8 *-*
from __future__ import absolute_import

from copy import copy

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QLabel
#from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QTableWidget
from PyQt4.QtGui import QTabWidget
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QMessageBox
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QThread

from ninja_ide.core import plugin_manager
from ninja_ide.core import file_manager
from ninja_ide.tools import ui_tools


def _get_plugin(plugin_name, plugin_list):
    plugin = None
    for plug in plugin_list:
        if unicode(plug["name"]) == unicode(plugin_name):
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
        self.setModal(True)
        self.resize(700, 500)

        vbox = QVBoxLayout(self)
        self._tabs = QTabWidget()
        vbox.addWidget(self._tabs)
        btnReload = QPushButton(self.tr("Reload"))
        btnReload.setMaximumWidth(100)
        vbox.addWidget(btnReload)
        self.overlay = ui_tools.Overlay(self)
        self.overlay.hide()

        self._oficial_available = []
        self._community_available = []
        self._locals = []
        self._updates = []
        self._loading = True

        self.connect(btnReload, SIGNAL("clicked()"), self._reload_plugins)
        self.thread = ThreadLoadPlugins(self)
        self.connect(self.thread, SIGNAL("finished()"),
            self._load_plugins_data)
        self.connect(self.thread, SIGNAL("plugin_downloaded(PyQt_PyObject)"),
            self._after_download_plugin)
        self.connect(self.thread, SIGNAL("plugin_uninstalled(PyQt_PyObject)"),
            self._after_uninstall_plugin)
        self.overlay.show()
        self._reload_plugins()

    def _reload_plugins(self):
        self.overlay.show()
        self._loading = True
        self.thread.runnable = self.thread.collect_data_thread
        self.thread.start()

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
            self._loading = False
        self.overlay.hide()

    def download_plugins(self, plugs):
        """
        Install
        """
        self.overlay.show()
        self.thread.plug = plugs
        #set the function to run in the thread
        self.thread.runnable = self.thread.download_plugins_thread
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
        self._table = QTableWidget(1, 5)
        self._table.removeRow(0)
        self._headers = ('Name', 'Version', 'Description', 'Authors', 'Web')
        vbox.addWidget(self._table)
        ui_tools.load_table(self._table, self._headers,
            _format_for_table(updates))
        self._table.setColumnWidth(0, 200)
        btnUpdate = QPushButton(self.tr("Update"))
        btnUpdate.setMaximumWidth(100)
        vbox.addWidget(btnUpdate)

        self.connect(btnUpdate, SIGNAL("clicked()"), self._update_plugins)

    def _update_plugins(self):
        data = _format_for_table(self._updates)
        plugins = ui_tools.remove_get_selected_items(self._table, data)
        #get the download link of each plugin
        for p_row in plugins:
            #search the plugin
            for p_dict in self._updates:
                if unicode(p_dict["name"]) == unicode(p_row[0]):
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
        self._table = QTableWidget(1, 5)
        self._table.removeRow(0)
        vbox.addWidget(self._table)
        self._headers = ('Name', 'Version', 'Description', "Authors", "Web")
        ui_tools.load_table(self._table, self._headers,
            _format_for_table(available))
        self._table.setColumnWidth(0, 200)
        hbox = QHBoxLayout()
        btnInstall = QPushButton('Install')
        btnInstall.setMaximumWidth(100)
        hbox.addWidget(btnInstall)
        hbox.addWidget(QLabel(self.tr("NINJA needs to be restarted for " \
            "changes to take effect.")))
        vbox.addLayout(hbox)

#        hbox = QHBoxLayout()
#        hbox.addWidget(QLabel(
#            self.tr("Add an external Plugin. URL Zip File:")))
#        self._link = QLineEdit()
#        hbox.addWidget(self._link)
#        btnAdd = QPushButton(self.tr("Add"))
#        hbox.addWidget(btnAdd)
#        vbox.addLayout(hbox)
#        lblExternalPlugin = QLabel(
#            self.tr("(Write the URL of the Plugin and press 'Add')"))
#        lblExternalPlugin.setAlignment(Qt.AlignRight)
#        vbox.addWidget(lblExternalPlugin)

        self.connect(btnInstall, SIGNAL("clicked()"), self._install_plugins)
#        self.connect(btnAdd, SIGNAL("clicked()"), self._install_external)

    def _install_plugins(self):
        data = _format_for_table(self._available)
        plugins = ui_tools.remove_get_selected_items(self._table, data)
        #get the download link of each plugin
        for p_row in plugins:
            #search the plugin
            for p_dict in self._available:
                if unicode(p_dict["name"]) == unicode(p_row[0]):
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
        ui_tools.load_table(self._table, self._headers, data)


class InstalledWidget(QWidget):
    """
    This widget show the installed plugins
    """

    def __init__(self, parent, installed):
        QWidget.__init__(self, parent)
        self._parent = parent
        self._installed = installed
        vbox = QVBoxLayout(self)
        self._table = QTableWidget(1, 5)
        self._table.removeRow(0)
        self._headers = ('Name', 'Version', 'Description', "Authors", "Web")
        vbox.addWidget(self._table)
        ui_tools.load_table(self._table, self._headers,
            _format_for_table(installed))
        self._table.setColumnWidth(0, 200)
        btnUninstall = QPushButton(self.tr("Uninstall"))
        btnUninstall.setMaximumWidth(100)
        vbox.addWidget(btnUninstall)

        self.connect(btnUninstall, SIGNAL("clicked()"),
            self._uninstall_plugins)

    def remove_item(self, plugin_name):
        plugin = _get_plugin(plugin_name, self._installed)
        self._installed.remove(plugin)

    def add_table_items(self, plugs):
        self._installed += plugs
        data = _format_for_table(self._installed)
        ui_tools.load_table(self._table, self._headers, data)

    def _uninstall_plugins(self):
        data = _format_for_table(self._installed)
        plugins = ui_tools.remove_get_selected_items(self._table, data)
        self._parent.mark_as_available(plugins)

    def reset_table(self, installed):
        self._installed = installed
        while self._table.rowCount() > 0:
            self._table.removeRow(0)
        ui_tools.load_table(self._table, self._headers, self._installed)


class ThreadLoadPlugins(QThread):
    """
    This thread makes the HEAVY work!
    """

    def __init__(self, manager):
        QThread.__init__(self)
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
                        if unicode(p["name"]) != unicode(local_data["name"])]
            elif plug_community:
                ava = plug_community
                community_available = [p for p in community_available
                        if unicode(p["name"]) != unicode(local_data["name"])]
            #check versions
            if ava and float(ava["version"]) > float(local_data["version"]):
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
            plugin_manager.download_plugin(p[5])
            plugin_manager.update_local_plugin_descriptor((p, ))
            self.emit(SIGNAL("plugin_downloaded(PyQt_PyObject)"), p)

    def uninstall_plugins_thread(self):
        for p in self.plug:
            plugin_manager.uninstall_plugin(p)
            self.emit(SIGNAL("plugin_uninstalled(PyQt_PyObject)"), p)

    def update_plugin_thread(self):
        """
        Updates some plugins
        """
        for p in self.plug:
            plugin_manager.uninstall_plugin(p)
            plugin_manager.download_plugin(p[5])
            plugin_manager.update_local_plugin_descriptor([p])
            self._manager.reset_installed_plugins()
