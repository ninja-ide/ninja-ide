import QtQuick 2.3


Rectangle {
    id: root
    width: 400
    height: 500

    color: "green"

    MouseArea { id: mouseArea2; anchors.fill: parent }

    states: State {
        name: "brighter2"; when: mouseArea2.pressed
        PropertyChanges { target: rect; color: "cyan" }
        PropertyChanges { target: root; color: "magenta" }
    }

    transitions: Transition {
        ColorAnimation { duration: 500 }
    }


    Rectangle {
        id: rect
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 200
        width: 200
        color: "red"

        MouseArea { id: mouseArea; anchors.fill: parent }

        states: State {
            name: "brighter"; when: mouseArea.pressed
            PropertyChanges { target: rect; color: "yellow" }
        }

        transitions: Transition {
            //SequentialAnimation{
                ColorAnimation { /*to: "yellow";*/ duration: 1000 }
                /*ColorAnimation { to: "red"; duration: 1000 }
            }*/
        }
    }

    Rectangle {
        id: window
        //visible: false
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        height: 200
        color: "black"

        Rectangle { id: myRect1; width: 50; height: 50; color: "red" }
        Rectangle { id: myRect2; width: 50; height: 50; color: "blue"; x: window.width/2 -width/2; y: window.height/2 -height/2 }

        states: [
            State {
                name: "reanchored1"

                AnchorChanges {
                    target: myRect1
                    anchors.top: window.top
                    anchors.bottom: window.bottom
                }
                PropertyChanges {
                    target: myRect1
                    anchors.topMargin: 10
                    anchors.bottomMargin: 10
                    width: 20
                    height: 20
                }

                AnchorChanges {
                    target: myRect2
                    anchors.left: window.left
                    anchors.right: window.right
                    anchors.top: undefined
                    anchors.bottom: undefined
                }
                PropertyChanges {
                    target: myRect2
                    anchors.rightMargin: 10
                    anchors.leftMargin: 10
                    height: 20
                }
            }, 
            State {
                name: "reanchored2"

                AnchorChanges {
                    target: myRect1
                    anchors.left: window.left
                    anchors.right: window.right
                }
                PropertyChanges {
                    target: myRect1
                    anchors.topMargin: 50
                    anchors.bottomMargin: 50
                    width: 20
                    height: 20
                }

                AnchorChanges {
                    target: myRect2
                    anchors.top: window.top
                    anchors.bottom: window.bottom
                    anchors.left: undefined
                    anchors.right: undefined
                }
                PropertyChanges {
                    target: myRect2
                    anchors.topMargin: 10
                    anchors.bottomMargin: 10
                    width: 20
                }
        }]

        transitions: Transition {
            AnchorAnimation { targets: [myRect1]; duration: 700}
            AnchorAnimation { targets: [myRect2]; duration: 200}
        }

        MouseArea {
            anchors.fill: parent;
            onClicked: {
                window.state === "reanchored2" ? window.state = "reanchored1": window.state = "reanchored2"
            }
        }
    }
}