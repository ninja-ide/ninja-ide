import QtQuick 2.6
import QtQuick.Controls 1.3
import QtQuick.Layouts 1.3

Component {

    Rectangle {
        width: parent.width
        height: 32
        color: "#fff"

        MouseArea  {
            anchors.fill: parent
            hoverEnabled: true

            onEntered: {
                parent.color = "#f1f1f1"
            }

            onPressed: {
                parent.color = "#c1c1c1"
                stack.push(browseLang)
            }

            onExited: {
                parent.color = "#fff"
            }

        }

        Text {
            anchors.verticalCenter: parent.verticalCenter
            padding: 8
            font.bold: false
            font.weight: Font.Thin
            font.family: "Segoe UI"
            text: "Add a Language"
            font.pixelSize: 16
        }

    }

}
