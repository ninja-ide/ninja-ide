import QtQuick 1.1

Rectangle {
    id: button

    property alias text: txtButton.text

    signal clicked

    radius: 10
    border.color: "gray"
    border.width: 2
    gradient: Gradient {
         GradientStop { id: stop1; position: 0.0; color: "#570000" }
         GradientStop { id: stop2; position: 1.0; color: "#881f1f" }
     }

    Text {
        id: txtButton
        anchors.centerIn: parent

        text: button.text
        color: "white"
    }

    states: [
        State {
            name: "ENTERED"
            PropertyChanges { target: stop1; color: "gray" }
        },
        State {
            name: "EXITED"
            PropertyChanges { target: stop1; color: "#570000" }
        },
        State {
            name: "PRESSED"
            PropertyChanges { target: stop2; color: "#3d0000" }
            PropertyChanges { target: stop1; color: "#631717" }
        },
        State {
            name: "RELEASED"
            PropertyChanges { target: stop1; color: "#570000" }
            PropertyChanges { target: stop2; color: "#881f1f" }
        }
     ]

    MouseArea {
        anchors.fill: parent
        hoverEnabled: true

        onEntered: button.state = "ENTERED";
        onExited: button.state = "EXITED";
        onClicked: button.clicked();
        onPressed: button.state = "PRESSED";
        onReleased: button.state = "RELEASED";
    }
}
