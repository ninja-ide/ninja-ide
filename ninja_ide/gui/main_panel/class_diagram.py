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

from PyQt4.QtCore import Qt
from PyQt4.QtCore import QRectF
from PyQt4.QtGui import QGraphicsItem
from PyQt4.QtGui import QRadialGradient
from PyQt4.QtGui import QGraphicsTextItem
from PyQt4.QtGui import QStyle
from PyQt4.QtGui import QColor
from PyQt4.QtGui import QPen
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QGraphicsView
from PyQt4.QtGui import QGraphicsScene
from PyQt4.QtGui import QVBoxLayout

from ninja_ide.gui.main_panel import itab_item
from ninja_ide.tools import introspection
from ninja_ide.core import file_manager


class ClassDiagram(QWidget, itab_item.ITabItem):

    def __init__(self, actions, parent=None):
        QWidget.__init__(self, parent)
        itab_item.ITabItem.__init__(self)
        self.actions = actions
        self.graphicView = QGraphicsView(self)
        self.scene = QGraphicsScene()
        self.graphicView.setScene(self.scene)
        self.graphicView.setViewportUpdateMode(
            QGraphicsView.BoundingRectViewportUpdate)

        vLayout = QVBoxLayout(self)
        self.setLayout(vLayout)
        vLayout.addWidget(self.graphicView)
        self.scene.setItemIndexMethod(QGraphicsScene.NoIndex)
        self.scene.setSceneRect(-200, -200, 400, 400)
        self.graphicView.setMinimumSize(400, 400)
        actualProject = self.actions.ide.explorer.get_actual_project()
        arrClasses = self.actions._locator.get_classes_from_project(
            actualProject)
        #FIXME:dirty need to fix
        self.mX = -400
        self.mY = -320
        self.hightestY = self.mY
        filesList = []
        for elem in arrClasses:
            #loking for paths
            filesList.append(elem[2])
        for path in set(filesList):
            self.create_class(path)

    def create_class(self, path):
        content = file_manager.read_file_content(path)
        items = introspection.obtain_symbols(content)
        mYPadding = 10
        mXPadding = 10
        for classname, classdetail in list(items["classes"].items()):
            cl = ClassModel(self.graphicView, self.scene)
            cl.set_class_name(classname)
            self.fill_clases(cl, classdetail[1])
            self.scene.addItem(cl)
            cl.setPos(self.mX, self.mY)
            self.mX += cl._get_width() + mXPadding
            if self.hightestY < self.mY + cl.get_height():
                self.hightestY = self.mY + cl.get_height()
            if self.mX > 2000:
                self.mX = -400
                self.mY += self.hightestY + mYPadding

    def fill_clases(self, classComponent, classContent):
        funct = classContent['functions']
        classComponent.set_functions_list(funct)
        attr = classContent['attributes']
        classComponent.set_attributes_list(attr)

    def scale_view(self, scaleFactor):
            factor = self.graphicView.transform().scale(
                scaleFactor, scaleFactor).mapRect(QRectF(0, 0, 1, 1)).width()

            if factor > 0.05 and factor < 15:
                self.graphicView.scale(scaleFactor, scaleFactor)

    def keyPressEvent(self, event):

        taskList = {
                  Qt.Key_Plus: lambda: self.scaleView(1.2),
                  Qt.Key_Minus: lambda: self.scaleView(1 / 1.2)}
        if(event.key() in taskList):
            taskList[event.key()]()
        else:
            QWidget.keyPressEvent(self, event)


class ClassModel(QGraphicsItem):

    def __init__(self, parent=None, graphicView=None, graphicScene=None):
        QGraphicsItem.__init__(self)
        self.set_default_data()
        self.className = QGraphicsTextItem(self)
        self.functionsItem = FunctionsContainerModel(self)
        self.className.setPlainText(self.defaultClassName)
        self.setFlag(self.ItemIsMovable)
        self.setFlag(self.ItemSendsGeometryChanges)
        self.functionsItem.setPos(0, self.__get_title_height())
        self.attributesItem = FunctionsContainerModel(self)
        self.attributesItem.setPos(0, self.functionsItem.get_height())

    def set_default_data(self):
        self.maxWidth = 100
        self.defaultClassNameHeight = 30
        self.defaultClassName = "No name"

    def set_functions_list(self, functionsList):
        self.functionsItem.set_functions_list(functionsList, "*", "()")
        self.update_positions()

    def set_attributes_list(self, attributesList):
        self.attributesItem.set_functions_list(attributesList)
        self.update_positions()

    def set_class_name(self, className):
        self.className.setPlainText(className)

    def _get_width(self):
        self.__calc_max_width()
        return self.maxWidth

    def __get_title_height(self):
        titleHeight = self.defaultClassNameHeight
        if titleHeight == self.className.document().size().height():
            titleHeight = self.className.document().size().height()
        return titleHeight

    def get_height(self):
        summary = self.defaultClassNameHeight
        summary += self.functionsItem.get_height()
        summary += self.attributesItem.get_height()
        return summary

    def __calc_max_width(self):
        if self.maxWidth < self.className.document().size().width():
            self.maxWidth = self.className.document().size().width()
        if hasattr(self, "functionsItem"):
            if self.maxWidth < self.functionsItem.get_width():
                self.maxWidth = self.functionsItem.get_width()
        if hasattr(self, "attributesItem"):
            if self.maxWidth < self.attributesItem.get_width():
                self.maxWidth = self.attributesItem.get_width()

    def set_bg_color(self, qColor):
        self.backgroundColor = qColor

    def set_method_list(self, itemList):
        self.methodList = itemList

    def update_positions(self):
        self.functionsItem.setPos(0, self.__get_title_height())
        self.attributesItem.setPos(
            0, self.functionsItem.y() + self.functionsItem.get_height())

    def paint(self, painter, option, widget):
        gradient = QRadialGradient(-3, -3, 10)
        if option.state & QStyle.State_Sunken:
            gradient.setCenter(3, 3)
            gradient.setFocalPoint(3, 3)
            gradient.setColorAt(0, QColor(Qt.yellow).light(120))
        else:
            gradient.setColorAt(0, QColor(Qt.yellow).light(120))
        painter.setBrush(gradient)
        painter.setPen(QPen(Qt.black, 0))
        painter.drawRoundedRect(self.boundingRect(), 3, 3)

    def boundingRect(self):
        return QRectF(0, 0, self._get_width(), self.get_height())

    def add_edge(self, edge):
        self.myEdge = edge
        edge.adjust()


class FunctionsContainerModel(QGraphicsItem):

    def __init__(self, parent=None):
        QGraphicsItem.__init__(self, parent)
        self.parent = parent
        self.maxWidth = self.parent._get_width()
        self.maxHeight = 0

    def paint(self, painter, option, widget):
        painter.drawLine(
            self.boundingRect().topLeft(), self.boundingRect().topRight())

    def set_functions_list(self, functionsList, prefix="", sufix=""):
        self.funtionsList = functionsList
        self.funtionsListItems = []
        self.maxHeight = 0
        tempHeight = 0
        for element in functionsList:
            tempElement = QGraphicsTextItem(self)
            tempElement.setPlainText(prefix + element + sufix)
            tempElement.setPos(0, tempHeight)
            tempHeight += tempElement.document().size().height()
            if self.maxWidth < tempElement.document().size().width():
                self.maxWidth = tempElement.document().size().width()
            self.funtionsListItems.append(tempElement)
        self.maxHeight = tempHeight

    def get_height(self):
        return self.maxHeight

    def get_width(self):
        if self.parent.maxWidth < self.maxWidth:
            return self.maxWidth
        else:
            return self.parent.maxWidth

    def boundingRect(self):
        return QRectF(0, 0, self.get_width(), self.get_height())
