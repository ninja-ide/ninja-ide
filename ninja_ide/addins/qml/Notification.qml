import QtQuick 1.1

Rectangle {
    id: frame
    width: 400
    height: 40
    color: "black"
    opacity: 0
    radius: 15
    border.color: "#aae3ef"
    border.width: 2

    property int interval: 3000
    signal close

    function setText(message){
        textArea.text = message;
    }

    function start(interval) {
        frame.interval = interval;
        showFrame.start();
    }

    SequentialAnimation {
        id: showFrame
        running: false
        NumberAnimation { target: frame; property: "opacity"; to: 1; duration: (frame.interval / 2); easing.type: Easing.InOutQuad }
        NumberAnimation { target: frame; property: "opacity"; to: 0; duration: (frame.interval / 2); easing.type: Easing.InOutQuad }
    }

    onOpacityChanged: {
        if(frame.opacity == 0){
            frame.close();
        }
    }

    Text{
        id: textArea
        text: ""
        wrapMode: Text.WordWrap
        font.pixelSize: 16
        font.bold: true
        anchors.fill: parent
        anchors.margins: 10
        color: "white"
        width: frame.width
        elide: Text.ElideRight
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
    }

    states: [
         State {
             name: "entered";
             when: mouseArea.containsMouse
             PropertyChanges { target: frame; opacity: 1 }
         },
         State {
             name: "";
             when: !mouseArea.containsMouse
             PropertyChanges { target: frame; opacity: 0.5 }
         }
     ]

    transitions: Transition {
        reversible: true
        from: ""
        to: "entered"
        NumberAnimation { target: parent; properties: "opacity"; duration: 500 }
    }

}
