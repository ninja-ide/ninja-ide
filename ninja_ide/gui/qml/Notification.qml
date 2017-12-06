import QtQuick 2.5

Rectangle {
    id: frame
    //width: 400
    //height: 40
    // color: "black"
    opacity: 0
    // radius: 15
    border.color: "gray"
    //border.width: 2
    property int interval: 2500
    signal close

    function setText(message){
        textArea.text = message;
    }

    function setColor(background_color, foreground_color){
        frame.color = background_color;
        textArea.color = foreground_color;
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
        //renderType: Text.NativeRendering
        font.pixelSize: 16
        font.bold: true
        // anchors.fill: parent
        anchors.verticalCenter: parent.verticalCenter
        anchors.left: parent.left
        anchors.leftMargin: 10
        // anchors.margins: 10
        //color: "white"
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
