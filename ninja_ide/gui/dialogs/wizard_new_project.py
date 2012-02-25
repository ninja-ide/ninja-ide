# *-* coding: utf-8 *-*
from __future__ import absolute_import

import os
import sys
import logging

from PyQt4.QtGui import QWizard
from PyQt4.QtGui import QWizardPage
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QComboBox
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QPlainTextEdit
from PyQt4.QtGui import QGridLayout
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QFileDialog
from PyQt4.QtGui import QListWidget
from PyQt4.QtGui import QPixmap
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL

from ninja_ide import resources
from ninja_ide.core import settings
from ninja_ide.core import plugin_interfaces
from ninja_ide.core import file_manager
from ninja_ide.tools import json_manager


logger = logging.getLogger('ninja_ide.gui.dialogs.wizard_new_project')


###############################################################################
# Wizard handler and Python Project handler
###############################################################################

class WizardNewProject(QWizard):
    """
    Wizard to create a new project (of any kind), it implements the base
    behavior. Also, it set two special projects type handler
    (PythonProjectHandler, ImportFromSourcesProjectHandler)
    """
    def __init__(self, parent):
        QWizard.__init__(self, parent)
        self.__explorer = parent
        self.setWindowTitle(self.tr("NINJA - New Project Wizard"))
        self.setPixmap(QWizard.LogoPixmap, QPixmap(resources.IMAGES['icon']))

        self.option = 'Python'
        #Add a project type handler for Python
        settings.set_project_type_handler(self.option,
            PythonProjectHandler(self.__explorer))
        #Add a project type handler for Import from existing sources
        settings.set_project_type_handler('Import from sources',
            ImportFromSourcesProjectHandler(self.__explorer))

        self.projectTypePage = PageProjectType(self)
        self.addPage(self.projectTypePage)
        self.addPage(PageProjectProperties())

    def add_project_pages(self, option='Python'):
        self.option = option
        pages = settings.get_project_type_handler(option).get_pages()
        listIds = self.pageIds()
        listIds.pop(listIds.index(0))
        for page in pages:
            self.addPage(page)
        #this page is always needed by a project!
        self.addPage(PageProjectProperties())
        for i in listIds:
            self.removePage(i)

    def next(self):
        if self.currentPage() == self.projectTypePage:
            self.add_project_pages(
                unicode(self.projectTypePage.listWidget.currentItem().text()))
        super(WizardNewProject, self).next()

    def done(self, result):
        if result == 1:
            page = self.currentPage()
            if type(page) == PageProjectProperties:
                venv = unicode(page.vtxtPlace.text())
                if venv:
                    if sys.platform == 'win32':
                        venv = os.path.join(venv, 'Scripts', 'python.exe')
                    else:
                        venv = os.path.join(venv, 'bin', 'python')
                    #check if venv folder exists
                    if  not os.path.exists(venv):
                        btnPressed = QMessageBox.information(self,
                            self.tr("Virtualenv Folder"),
                            self.tr("Folder don't exists or this is not a " \
                                "valid Folder.\n If you want to set " \
                                "or modify, go to project properties"),
                            self.tr("Back"),
                            self.tr("Continue"))
                        if btnPressed == QMessageBox.NoButton:
                            return
                        else:
                            self.currentPage().vtxtPlace.setText("")
                page.vtxtPlace.setText(venv)
            settings.get_project_type_handler(self.option)\
                .on_wizard_finish(self)
        super(WizardNewProject, self).done(result)

    def _load_project(self, path):
        """
        Open Project based on path into Explorer
        """
        self.__explorer.open_project_folder(path)

    def _load_project_with_extensions(self, path, extensions):
        """Open Project based on path into Explorer with extensions"""
#        self._main._properties._treeProjects.load_project(
#            self._main.open_project_with_extensions(path), path)
        pass


###############################################################################
# Python Project Handler
###############################################################################


class PythonProjectHandler(plugin_interfaces.IProjectTypeHandler):
    """
    Handler for Python projects
    """
    def __init__(self, explorer):
        self.__explorer = explorer

    def get_pages(self):
        """
        Get extra pages for new Python projects
        """
        return ()

    def get_context_menus(self):
        """
        Get a special menu for new Python projects
        """
        return ()

    def on_wizard_finish(self, wizard):
        """
        Create the ninja_porject (.nja file), create the main __init__.py
        and open the project
        """
        ids = wizard.pageIds()
        page = wizard.page(ids[1])
        path = unicode(page.txtPlace.text())
        if not path:
            QMessageBox.critical(self, self.tr("Incorrect Location"),
                self.tr("The project couldn\'t be create"))
            return
        project = {}
        name = unicode(page.txtName.text())
        project['name'] = name
        project['description'] = unicode(page.txtDescription.toPlainText())
        project['license'] = unicode(page.cboLicense.currentText())
        project['venv'] = unicode(page.vtxtPlace.text())
        json_manager.create_ninja_project(path, name, project)
        try:
            file_manager.create_init_file(path)
        except:
            logger.debug("The __init__ file already exists - Import Sources.")
        wizard._load_project(path)


###############################################################################
# Import project from existing sources
###############################################################################


class ImportFromSourcesProjectHandler(plugin_interfaces.IProjectTypeHandler):
    """
    Handler for Import from existing sources project
    """
    def __init__(self, explorer):
        self.__explorer = explorer

    def get_pages(self):
        """
        Get extra pages for Import from sources projects
        """
        return ()

    def get_context_menus(self):
        """
        Get a special menu for Import from sources projects
        """
        return ()

    def on_wizard_finish(self, wizard):
        """
        Create the ninja_porject (.nja file) and open the project
        """
        ids = wizard.pageIds()
        page = wizard.page(ids[1])
        path = unicode(page.txtPlace.text())
        if not path:
            QMessageBox.critical(self, self.tr("Incorrect Location"),
                self.tr("The project couldn\'t be create"))
            return
        project = {}
        name = unicode(page.txtName.text())
        project['name'] = name
        project['description'] = unicode(page.txtDescription.toPlainText())
        project['license'] = unicode(page.cboLicense.currentText())
        project['venv'] = unicode(page.vtxtPlace.text())
        json_manager.create_ninja_project(path, name, project)
        wizard._load_project(path)


###############################################################################
# WIZARD FIRST PAGE
###############################################################################


class PageProjectType(QWizardPage):

    def __init__(self, wizard):
        QWizardPage.__init__(self)
        self.setTitle(self.tr("Project Type"))
        self.setSubTitle(self.tr("Choose the Project Type"))
        self._wizard = wizard

        vbox = QVBoxLayout(self)
        self.listWidget = QListWidget()
        vbox.addWidget(self.listWidget)
        types = settings.get_all_project_types()
        types.sort()
        index = types.index('Python')
        types.insert(0, types.pop(index))
        self.listWidget.addItems(types)
        self.listWidget.setCurrentRow(0)


###############################################################################
# WIZARD LAST PAGE
###############################################################################


class PageProjectProperties(QWizardPage):

    def __init__(self):
        QWizardPage.__init__(self)
        self.setTitle(self.tr("New Project Data"))
        self.setSubTitle(self.tr(
            "Complete the following fields to create the Project Structure"))

        gbox = QGridLayout(self)
        #Names of the fields to complete
        self.lblName = QLabel(self.tr("New Project Name (*):"))
        self.lblPlace = QLabel(self.tr("Project Location (*):"))
        self.lblDescription = QLabel(self.tr("Project Description:"))
        self.lblLicense = QLabel(self.tr("Project License:"))
        self.lblVenvFolder = QLabel(self.tr("Virtualenv Folder:"))
        gbox.addWidget(self.lblName, 0, 0, Qt.AlignRight)
        gbox.addWidget(self.lblPlace, 1, 0, Qt.AlignRight)
        gbox.addWidget(self.lblDescription, 2, 0, Qt.AlignTop)
        gbox.addWidget(self.lblLicense, 3, 0, Qt.AlignRight)
        gbox.addWidget(self.lblVenvFolder, 4, 0, Qt.AlignRight)

        #Fields on de right of the grid
        #Name
        self.txtName = QLineEdit()
        self.registerField('PageProjectProperties_projectName*', self.txtName)
        #Location
        hPlace = QHBoxLayout()
        self.txtPlace = QLineEdit()
        self.txtPlace.setReadOnly(True)
        self.registerField('PageProjectProperties_place*', self.txtPlace)
        self.btnExamine = QPushButton(self.tr("Examine..."))
        hPlace.addWidget(self.txtPlace)
        hPlace.addWidget(self.btnExamine)
        #Virtualenv
        vPlace = QHBoxLayout()
        self.vtxtPlace = QLineEdit()
        self.vtxtPlace.setReadOnly(True)
        self.registerField('PageProjectProperties_vplace', self.vtxtPlace)
        self.vbtnExamine = QPushButton(self.tr("Examine..."))
        vPlace.addWidget(self.vtxtPlace)
        vPlace.addWidget(self.vbtnExamine)
        #Project Description
        self.txtDescription = QPlainTextEdit()
        #Project License
        self.cboLicense = QComboBox()
        self.cboLicense.setFixedWidth(250)
        self.cboLicense.addItem('Apache License 2.0')
        self.cboLicense.addItem('Artistic License/GPL')
        self.cboLicense.addItem('Eclipse Public License 1.0')
        self.cboLicense.addItem('GNU General Public License v2')
        self.cboLicense.addItem('GNU General Public License v3')
        self.cboLicense.addItem('GNU Lesser General Public License')
        self.cboLicense.addItem('MIT License')
        self.cboLicense.addItem('Mozilla Public License 1.1')
        self.cboLicense.addItem('New BSD License')
        self.cboLicense.addItem('Other Open Source')
        self.cboLicense.addItem('Other')
        self.cboLicense.setCurrentIndex(4)
        #Add to Grid
        gbox.addWidget(self.txtName, 0, 1)
        gbox.addLayout(hPlace, 1, 1)
        gbox.addWidget(self.txtDescription, 2, 1)
        gbox.addWidget(self.cboLicense, 3, 1)
        gbox.addLayout(vPlace, 4, 1)
        #Signal
        self.connect(self.btnExamine, SIGNAL('clicked()'), self.load_folder)
        self.connect(self.vbtnExamine, SIGNAL('clicked()'),
            self.load_folder_venv)

    def load_folder(self):
        self.txtPlace.setText(unicode(QFileDialog.getExistingDirectory(
            self, self.tr("New Project Folder"))))

    def load_folder_venv(self):
        self.vtxtPlace.setText(unicode(QFileDialog.getExistingDirectory(
            self, self.tr("Select Virtualenv Folder"))))
