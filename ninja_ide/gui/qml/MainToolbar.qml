import QtQuick 2.0
import QtQuick.Controls 2.0
import QtQuick.Layouts 1.1

Rectangle {
    id: root

    width: 40
    color: "#232323"
    x: 0
    signal actionClicked(string func)

    Component.onCompleted: {
        var comp = Qt.createComponent("widgets/ButtonToolBar.qml")
        for( var i=0; i<obj.length; i++ ) {
            var iconPath = '../../../img/' + obj[i].icon
            var color = obj[i].color
            var object = comp.createObject(layout, {'btnIcon': iconPath, 'slotName': obj[i].slot, 'colorIcon': color})
            object.clicked.connect(actionClicked)
        }
   }


    Rectangle {
        id: border
        color: "#181818"
        width: 1
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.right: parent.right

    }

    ColumnLayout {
        id: layout

        anchors.top: parent.top
        anchors.topMargin: 30
        anchors.horizontalCenter: parent.horizontalCenter
        spacing: 5
    }

}
