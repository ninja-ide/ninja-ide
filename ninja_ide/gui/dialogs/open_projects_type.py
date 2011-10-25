

#class OpenProjectType(QDialog, ProjectWizard):
#
#    def __init__(self, main):
#        QDialog.__init__(self)
#        ProjectWizard.__init__(self)
#        self._main = main
#        self.setModal(True)
#        vbox = QVBoxLayout(self)
#        vbox.addWidget(QLabel(self.tr("Select the Type of Project:")))
#        self.listWidget = QListWidget()
#        projectTypes = self.types.keys()
#        projectTypes.sort()
#        self.listWidget.addItems(projectTypes)
#        vbox.addWidget(self.listWidget)
#        btnNext = QPushButton(self.tr("Next"))
#        vbox.addWidget(btnNext)
#        if len(projectTypes) > 0:
#            self.listWidget.setCurrentRow(0)
#        else:
#            btnNext.setEnabled(False)
#
#        self.connect(btnNext, SIGNAL("clicked()"), self._open_project)
#
#    def _open_project(self):
#        type_ = str(self.listWidget.currentItem().text())
#        extensions = self.types[type_].projectFiles()
#        if extensions is None:
#            self._main.open_project_folder()
#        else:
#            self._main.open_project_type(extensions)
