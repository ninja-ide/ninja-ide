import QtQuick 1.1

Rectangle {
    id: frame
    width: 400
    height: 60
    color: "black"
    opacity: 0.5
    radius: 15
    border.color: "#aae3ef"
    border.width: 2

    function set_text(message){
        text.text = message;
    }

    Text{
        id: text
        text: "Esta es una notification del sistema."
        wrapMode: Text.WordWrap
        font.pixelSize: 18
        font.bold: true
        anchors.fill: parent
        anchors.topMargin: 20
        anchors.leftMargin: 20
        anchors.rightMargin: 20
        anchors.bottomMargin: 20
        color: "white"
    }

    // Animation
    Behavior on y { PropertyAnimation {duration: 1000} }
    NumberAnimation { id: show; target: parent; properties: "opacity"; from: 0.5; to: 1; duration: 2000 }
    NumberAnimation { id: hide; target: parent; properties: "opacity";from: 1; to: 0.5; duration: 2000 }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        onEntered: { show.running = true; }
        onExited: { hide.running = true; }
    }

    states: State {
         name: "entered"; when: mouseArea.containsMouse
         PropertyChanges { target: frame; opacity: 1 }
     }

    transitions: Transition {
        reversible: true

    }

}
