import QtQuick 2.6

Rectangle {

    property color btnColor: "#fff"
    property bool visibility: true
    signal click()

    anchors.top: parent.children[0].bottom
    anchors.right: parent.right
    anchors.rightMargin: 8
    visible: visibility
    width: 120
    height: 32
    color: btnColor

    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor

        onEntered: {
            parent.border.color = "#7a7a7a"
            parent.border.width = 2
        }

        onExited: {
            parent.border.width = 0
        }

        onClicked: click()

    }

    Text {
        anchors.centerIn: parent
        padding: 8
        font.weight: Font.Thin
        font.family: "Segoe UI"
        text: "set as Default"
        font.pixelSize: 16
    }
}
