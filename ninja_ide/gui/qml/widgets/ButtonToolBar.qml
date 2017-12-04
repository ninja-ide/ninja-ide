import QtQuick 2.8
import QtGraphicalEffects 1.0

Rectangle {
    id: back
    color: "#232323"
    width: 38; height: 38
    property string btnIcon
    property string slotName
    property string colorIcon
    signal clicked(string slot)

    Image {
        id: icon
        source: back.btnIcon
        fillMode: Image.PreserveAspectFit
        anchors.centerIn: parent
        sourceSize: Qt.size(22, 22)

    }

    MouseArea {
        id: ma
        anchors.fill: parent
        hoverEnabled: true
        onClicked: back.clicked(back.slotName)

        onEntered: {
            back.color = "#434343"
        }
        onExited: {
            back.color = "#232323"
        }
        onPressed: {
            back.color = "#6a6ea9"
        }
        onReleased: {
            back.color = "#232323"
        }
        onCanceled: {
            back.color = "#232323"
        }
    }

    Behavior on color {
        ColorAnimation { duration: 130 }
    }

    DropShadow {
        anchors.fill: icon
        source: icon
        color: Qt.rgba(0, 0, 0, 80)
        horizontalOffset: 1
        verticalOffset: 1
        radius: 5.0
        samples: 20
    }

    ColorOverlay {
        anchors.fill: icon
        source: icon
        color: colorIcon ? colorIcon : "#ddd"
    }
}

/*Button {
    id: btn
    text: ""
    Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
    property string source
    background: Rectangle {
        implicitWidth: 49
        implicitHeight: 48
        opacity: enabled ? 1 : 0.3
        color: btn.down ? "black" : "#232323"
    }

    Image {
        id: img
        fillMode: Image.PreserveAspectFit
        anchors.centerIn: parent
        sourceSize.height: btn.background.height - 6
        height: sourceSize.height
        source: "../../img/file-text.png"
    }

    ColorOverlay {
        anchors.fill: img
        source: img
        color: "#ddd"
    }
}*/
