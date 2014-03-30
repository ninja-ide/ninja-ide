import QtQuick 1.1

Rectangle {
    id: root

    radius: 10
    smooth: true
    color: "#24262c"

    signal install
    signal selection(bool value)
    signal showPlugin
    property bool selected: false
    property alias title: txtTitle.text
    property alias summary: txtSummary.text
    property string version: "0"

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
        onClicked: {
            root.showPlugin();
        }

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

    Rectangle {
        id: btnSelected
        height: 15
        width: 15
        color: root.selected ? "lightgreen" : "white"
        anchors {
            left: parent.left
            top: parent.top
            margins: 10
        }

        MouseArea {
            anchors.fill: parent
            onClicked: {
                root.selection(!root.selected);
            }
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
            spacing: 5
            Text {
                id: txtTitle
                color: "#ededed"
                anchors {
                    left: parent.left
                    leftMargin: 25
                    right: parent.right
                    rightMargin: 25
                }
                elide: Text.ElideRight
                horizontalAlignment: Text.AlignHCenter
            }
            Text {
                text: "Version: " + root.version
                color: "#ededed"
                font.pixelSize: 10
                anchors {
                    left: parent.left
                    leftMargin: 25
                    right: parent.right
                    rightMargin: 25
                }
                elide: Text.ElideRight
                horizontalAlignment: Text.AlignHCenter
            }
            Text {
                id: txtSummary
                color: "#ededed"
                font.pixelSize: 10
                anchors {
                    left: parent.left
                    right: parent.right
                }
                maximumLineCount: 5
                wrapMode: Text.WordWrap
                horizontalAlignment: Text.AlignHCenter
            }
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
            bottom: parent.bottom
            margins: 10
        }

        onClicked: {
            root.state = "INSTALLING";
            root.install();
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
            bottom: parent.bottom
            margins: 10
        }

        function start() {
            bar.x = bar.end;
        }

        Rectangle {
            id: bar
            visible: progress.visible
            property int end: (progress.width - bar.width)
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
            width: 50
            x: parent.x

            Behavior on x { PropertyAnimation {duration: 800} }

            onXChanged: {
                if (bar.x == 0) {
                    bar.x = bar.end;
                } else if (bar.x == bar.end) {
                    bar.x = 0;
                }
            }
        }
    }
}