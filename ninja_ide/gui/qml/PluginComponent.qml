import QtQuick 1.1

Rectangle {
    id: root

    radius: 10
    smooth: true
    color: "#24262c"

    signal install
    signal downloadFinished
    signal selection(bool value)
    property bool selected: false

    states: [
        State {
            name: "NOT_INSTALLED"
            PropertyChanges { target: btnInstall; visible: true }
            PropertyChanges { target: progress; visible: false }
        },
        State {
            name: "INSTALLING"
            PropertyChanges { target: btnInstall; visible: false }
            PropertyChanges { target: progress; visible: true }
        }
    ]

    state: "NOT_INSTALLED"

    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        onEntered:{
            root.color = "#32353d";
        }

        onCanceled:{
            root.color = "#24262c";
        }

        onExited: {
            root.color = "#24262c";
        }
    }

    Column {
        anchors.fill: parent
        anchors.margins: 5
        spacing: 15

        Column {
            anchors {
                left: parent.left
                right: parent.right
            }
            spacing: 2
            Text {
                text: "Django"
                color: "#ededed"
                anchors {
                    left: parent.left
                    right: parent.right
                }
                horizontalAlignment: Text.AlignHCenter
            }
            Text {
                text: "Version: 0.1"
                color: "#ededed"
                font.pixelSize: 10
                anchors {
                    left: parent.left
                    right: parent.right
                }
                horizontalAlignment: Text.AlignHCenter
            }
            Text {
                text: "Diego Sarmentero"
                color: "#ededed"
                font.pixelSize: 10
                anchors {
                    left: parent.left
                    right: parent.right
                }
                horizontalAlignment: Text.AlignHCenter
            }
        }

        ToggleButton {
            id: btnInstall
            height: 20
            text: "Install"
            toggledEnagled: false
            anchors {
                left: parent.left
                right: parent.right
            }

            onClicked: {
                root.state = "INSTALLING";
                progress.start()
            }
        }

        Rectangle {
            id: progress
            height: 20
            color: "#ededed"
            anchors {
                left: parent.left
                right: parent.right
            }

            function start() {
                timer.start();
            }

            Rectangle {
                id: bar
                property int percentage: 0
                visible: progress.visible
                gradient: Gradient {
                    GradientStop { position: 0.0; color: "lightsteelblue" }
                    GradientStop { position: 0.5; color: "lightsteelblue" }
                    GradientStop { position: 0.5; color: "steelblue" }
                    GradientStop { position: 1.0; color: "steelblue" }
                }
                anchors {
                    top: parent.top
                    bottom: parent.bottom
                }
                width: (bar.percentage * progress.width / 100)

                Timer {
                    id: timer
                    interval: 200
                    running: false
                    repeat: true
                    onTriggered: {
                        bar.percentage += 10;
                        if (bar.percentage == 100) {
                            timer.stop();
                            root.downloadFinished();
                        }
                    }
                }
            }
        }
    }

    Rectangle {
        id: btnSelected
        height: 15
        width: 15
        radius: width / 2
        color: root.selected ? "lightgreen" : "white"
        anchors {
            left: parent.left
            bottom: parent.bottom
            margins: 10
        }

        MouseArea {
            anchors.fill: parent
            onClicked: {
                root.selection(!root.selected);
            }
        }
    }

    Row {
        spacing: 2
        anchors {
            bottom: parent.bottom
            right: parent.right
            margins: 10
        }

        Image {
            source: "img/download.png"
            width: 12
            height: 12
            fillMode: Image.PreserveAspectFit
        }
        Text {
            text: "252"
            color: "#d6d6d6"
            font.pixelSize: 10
        }
    }
}