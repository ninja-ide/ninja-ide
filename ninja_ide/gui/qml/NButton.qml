import QtQuick 2.3

Rectangle {
    id: button

    signal clicked
    property alias text: btnText.text

    height: btnText.height + 30
    border.color:"white"
    width: btnText.width + 30

    color: "transparent"

    Text {
        id: btnText
        anchors.centerIn:parent
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true

        onEntered: { button.color = "#313131" }
        onExited: { button.color = "transparent" }
        onClicked: { button.clicked() }
    }

    /*MouseArea {
            id: mouseArea
            anchors.fill: parent
            hoverEnabled: true
            onClicked: {
                button.clicked();
            }

            onPressed: {
                button.color = "#6a6ea9";
                border.color= "#6a6ea9";
            }

            onReleased: {
                button.color = "#323233";
            }

            onEntered:{
                button.color = "#434345";
                border.color= "#6a6ea9";
            }

            onCanceled:{
                button.color = "#323233";
                border.color = "#111";
            }

            onExited: {
                border.color= "#111"
                button.color = "#323233";
            }
        }*/
}
