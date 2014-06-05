import QtQuick 1.1

Rectangle {
    id: button

    signal clicked
    property alias text: btnText.text
    property bool toggledEnagled: true
    property bool toggled: false
    property int textWidth: btnText.width

    height: 30

    gradient: button.toggled ? onn : off

    onToggledChanged: {
        if (button.toggled) {
            button.gradient = onn;
        } else {
            button.gradient = off;
        }
    }

    Gradient {
        id: off
        GradientStop { position: 0.0; color: "#e6e6e6" }
        GradientStop { position: 0.5; color: "#e6e6e6" }
        GradientStop { position: 0.5; color: "#b6b6b6" }
        GradientStop { position: 1.0; color: "#b6b6b6" }
    }

    Gradient {
        id: onn
        GradientStop { position: 0.0; color: "#b0b0b0" }
        GradientStop { position: 0.5; color: "#b0b0b0" }
        GradientStop { position: 0.5; color: "#e6e6e6" }
        GradientStop { position: 1.0; color: "#e6e6e6" }
    }

    Gradient {
        id: hover
        GradientStop { position: 0.0; color: "#fafafa" }
        GradientStop { position: 0.7; color: "#fafafa" }
        GradientStop { position: 0.7; color: "#b6b6b6" }
        GradientStop { position: 1.0; color: "#b6b6b6" }
    }

    Text {
        id: btnText
        anchors.centerIn:parent
        color:"#414141"
        text: "text"
    }

    MouseArea {
            id: mouseArea
            anchors.fill: parent
            hoverEnabled: true
            onClicked: {
                if (button.toggledEnagled) {
                    button.toggled = !button.toggled;
                }
                button.clicked();
            }

            onPressed: {
                button.gradient = onn;
            }

            onReleased: {
                button.gradient = hover;
            }

            onEntered:{
                if (!button.toggled) {
                    button.gradient = hover;
                }
            }

            onCanceled:{
                button.gradient = off;
            }

            onExited: {
                button.gradient = button.toggled ? onn : off;
            }
        }
}