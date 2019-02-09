import QtQuick 2.6

Rectangle {
    id: frame
    opacity: 0
    property int duration: 3000
    property int interval: 500
    signal close

    function setText(message){
        textArea.text = message;
    }

    function updateText(message) {
        timer.restart();
        textArea.text = message;
    }

    function setColor(background_color, foreground_color){
        frame.color = background_color;
        textArea.color = foreground_color;
    }

    function start(duration) {
        frame.duration = duration;
        showFrame.start();
    }


    NumberAnimation {
        id: showFrame
        target: frame
        property: "opacity"
        to: 1
        duration: interval
        easing.type: Easing.InOutQuad

        onStopped: timer.start()
    }


    NumberAnimation {
        id: hideFrame
        target: frame
        property: "opacity"
        to: 0
        duration: interval
        easing.type: Easing.InOutQuad
    }
    Timer {
        id: timer
        interval: duration; running: false
        onTriggered: hideFrame.start()
    }

    onOpacityChanged: {
        if(frame.opacity == 0){
            frame.close();
        }
    }

    Text{
        id: textArea
        text: ""
//        wrapMode: Text.WordWrap
//        font.pixelSize: 16
        font.bold: true
        anchors.verticalCenter: parent.verticalCenter
        anchors.left: parent.left
        anchors.leftMargin: 10
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
