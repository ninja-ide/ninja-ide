
from PyQt5.QtCore import QUrl, Qt, QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QFrame, QVBoxLayout, QComboBox
from PyQt5.QtQuick import QQuickView, QQuickItem
from PyQt5.QtQuickWidgets import QQuickWidget




class FilesHandler(QFrame):
#
    def __init__(self, parent=None):
        self.wid = QWidget()
        self.comboParent = QComboBox(self.wid)
        super(FilesHandler, self).__init__(None, Qt.Popup)#, Qt.Popup | Qt.FramelessWindowHint
        self.view = QQuickWidget()
        self.view.setResizeMode(QQuickWidget.SizeRootObjectToView)
        self.view.setSource(QUrl.fromLocalFile("G:/miguel 2/Peluqueria/instaladores/nuevo/ninja/ninja-ide-master/ninja_ide/gui/qml/FilesHandler.qml"))
#
        self._model = {}
        self._temp_files = {}
        self._max_index = 0
#
#
        self.setStyleSheet("background-color: rgb(25, 255, 60);")
        self.vbox = QVBoxLayout(self)
#
        self.vbox.setContentsMargins(0, 0, 0, 0)
        self.vbox.setSpacing(0)
        self.vbox.addWidget(self.view)
#
        self._root = self.view.rootObject()
#
        self.resize(400,400)
        self.move(200, 200)
#
#
    def showEvent(self, event):
        print("\nshowEvent:::showEvent")
#
        super(FilesHandler, self).showEvent(event)
        self._root.show_animation()
        point = self.comboParent.mapToGlobal(self.view.pos())
        self.move(point.x(), point.y())
        # self.setFocus()
        self.view.setFocus()
        self._root.activateInput()
        QTimer.singleShot(5000, lambda item=self._root.childItems()[0].childItems()[0]:\
            print("QTimer::", item, item.hasActiveFocus(), item.scopedFocusItem(),\
                item.hasFocus(), item.isFocusScope() ))
#
    def hideEvent(self, event):
        print("\nhideEvent:::")
        super(FilesHandler, self).hideEvent(event)
        self._temp_files = {}
        self._root.clear_model()
#
    def next_item(self):
        print("next_item()", self)
        if not self.isVisible():
            self.show()
        self._root.next_item()
#
    def previous_item(self):
        print("previous_item()", self)
        if not self.isVisible():
            self.show()
        self._root.previous_item()
#
    def keyPressEvent(self, event):
        print("keyPressEvent()", event.key(), event.key() == Qt.Key_Escape)
        if event.key() == Qt.Key_Escape:
            self.hide()
        elif (event.modifiers() == Qt.ControlModifier and
                event.key() == Qt.Key_PageDown) or event.key() == Qt.Key_Down:
            self._root.next_item()
        elif (event.modifiers() == Qt.ControlModifier and
                event.key() == Qt.Key_PageUp) or event.key() == Qt.Key_Up:
            self._root.previous_item()
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self._root.open_item()
        super(FilesHandler, self).keyPressEvent(event)
#
    def mousePressEvent(self, event):
        if QApplication.instance().widgetAt( self.mapToGlobal(event.pos()) ) == self.comboParent:
            event.ignore()
            print("mousePressEvent()::event.ignore()")
            #self.comboParent.hidePopup()
            return
        super(FilesHandler, self).mousePressEvent(event)





app = QApplication([])

engine = QQuickWidget()
engine.setResizeMode(QQuickWidget.SizeRootObjectToView)
engine.setSource(QUrl.fromLocalFile("G:/miguel 2/Peluqueria/instaladores/nuevo/ninja/ninja-ide-master/ninja_ide/gui/qml/FilesHandler.qml"))


wid = QWidget()
frm = QFrame(wid, Qt.Popup | Qt.FramelessWindowHint)
frm.setStyleSheet("background-color: rgb(25, 255, 60);")
vbox = QVBoxLayout(frm)

vbox.setContentsMargins(0, 0, 0, 0)
vbox.setSpacing(0)
vbox.addWidget(engine)

obj = engine.rootObject()

frm.resize(400,400)
frm.move(200, 200)

frm.show()
engine.setFocus()
obj.show_animation()
obj.activateInput()

app.exec_()