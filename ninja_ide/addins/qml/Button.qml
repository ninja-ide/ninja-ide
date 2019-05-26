import QtQuick 2.6

Rectangle {
    id: button

    property alias text: txtButton.text

    signal clicked

    radius: 3
//    border.color: "gray"
//    border.width: 2
//    gradient: Gradient {
//         GradientStop { id: stop1; position: 0.0; color: "#262626" }
//         GradientStop { id: stop2; position: 1.0; color: "#343434" }
//     }
    color: "#282828"
    Text {
        id: txtButton
        anchors.centerIn: parent

        text: button.text
        color: "white"
    }

    states: [
        State {
            name: "ENTERED"
            PropertyChanges { target: button; color: "#333" }
        },
        State {
            name: "EXITED"
            PropertyChanges { target: button; color: "#282828" }
        },
        State {
            name: "PRESSED"
            PropertyChanges { target: button; color: "#111" }
//            PropertyChanges { target: stop1; color: "#383838" }
        },
        State {
            name: "RELEASED"
            PropertyChanges { target: button; color: "#282828" }
//            PropertyChanges { target: stop2; color: "#343434" }
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
