import QtQuick 2.3

Rectangle {
    id: button

    signal clicked
    property alias text: btnText.text

    height: 50
    border.color:"#111"
    radius: 2

    color: "#323233"

    Text {
        id: btnText
        anchors.centerIn:parent
        color:"white"
        text: "text"
    }

    MouseArea {
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
        }
}
