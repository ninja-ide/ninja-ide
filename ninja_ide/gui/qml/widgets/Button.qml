import QtQuick 2.1
import QtQuick.Controls 1.0
import QtQuick.Controls.Styles 1.0

Button {
    id: button
    style: ButtonStyle {
        padding.left: 14
        background: Item {
            anchors.fill: parent
            implicitWidth: 160
            implicitHeight: 30

            Rectangle {
                id: rect
                anchors.fill: parent
                color: (button.checked || button.pressed)
                       ? "#6a6ea9": (button.hovered ? "#434345": "#323232")
                border.width: 1
                border.color: "#434345"

                Behavior on color {
                    ColorAnimation { duration: 150 }
                }

            }

        }

        label: Text {
            id: text
            renderType: Text.NativeRendering
            verticalAlignment: Text.AlignVCenter
            text: button.text
            font.pixelSize: 16
            font.bold: false
            smooth: true
            color: "white"
        }
    }

}
