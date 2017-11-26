import QtQuick 2.4
import QtQuick.Controls 1.4
import QtQuick.Window 2.2 as WIN
import QtQuick.Layouts 1.2

WIN.Window {
    id: win
    modality: Qt.ApplicationModal
    //visibility: Window.Windowed
    visible: true
    width: 135
    height: 40
    color: "white"
    //flags: Qt.Popup

    ColumnLayout{
        id: columnLayout1
        spacing: 2
        anchors.fill: parent
        Rectangle{
            id: rectangle1
            anchors.right: parent.right
            anchors.rightMargin: 0
            anchors.top: parent.top
            anchors.topMargin: 0
            anchors.bottom: sep.top
            Layout.fillWidth: true
            Text{
                id: t1
                Layout.fillHeight: true
                anchors.leftMargin: 5
                anchors.left: parent.left
                anchors.right: parent.right
                height: parent.height
                text: "Incert File in..."
                verticalAlignment: Text.AlignVCenter
                font.pointSize: 11
            }
            MouseArea {
                anchors.fill: parent
                onClicked: print("onClicked1")//win.close()
            }
        }

        Rectangle{
            id: sep
            height: 2
            Layout.fillWidth: true
            Layout.maximumHeight: 2
            anchors.verticalCenter: parent.verticalCenter
            color: "gray"
        }

        Rectangle{
            id: rectangle2
            anchors.right: parent.rights
            anchors.bottom: parent.bottom
            anchors.top: sep.bottom
            Layout.fillWidth: true
            Text{
                id: t2
                Layout.fillHeight: true
                anchors.leftMargin: 5
                anchors.left: parent.left
                anchors.right: parent.right
                height: parent.height
                text: "Incert All Files in..."
                verticalAlignment: Text.AlignVCenter
                font.pointSize: 11
            }
            MouseArea {
                anchors.fill: parent
                onClicked: print("onClicked2")//win.close()
            }
        }
    }
    // Component.onCompleted: win.show()
}
