import QtQuick 1.1

Rectangle {
    id: root

    radius: 10
    smooth: true
    color: "#24262c"

    signal install
    signal close

    property int identifier: 0
    property alias title: txtTitle.text
    property string author: ""
    property string authorEmail: ""
    property string version: ""
    property string homePage: ""
    property string license: ""
    property alias summary: txtSummary.text
    property alias description: txtDescription.text

    function clear() {
        txtTitle.text = "";
        txtSummary.text = "";
        txtDescription.text = "";
        author = "";
        authorEmail = "";
        version = "";
        homePage = "";
        license = "";
    }

    Flickable {
        contentHeight: col.childrenRect.height
        anchors {
            left: parent.left
            right: parent.right
            top: parent.top
            bottom: bottomBar.top
            margins: 10
        }
        clip: true

        Column {
            id: col
            anchors {
                left: parent.left
                right: parent.right
            }
            spacing: 30

            Column {
                spacing: 10
                anchors {
                    left: parent.left
                    right: parent.right
                }

                Text {
                    id: txtTitle
                    color: "white"
                    font.pixelSize: 30
                    anchors {
                        left: parent.left
                        right: parent.right
                    }
                    horizontalAlignment: Text.AlignHCenter
                }
                Text {
                    text: "Author: " + root.author + " (" + root.authorEmail + ")"
                    visible: root.author ? true : false
                    color: "white"
                    anchors {
                        left: parent.left
                        right: parent.right
                    }
                }
                Text {
                    text: "Version: " + root.version
                    visible: root.version ? true : false
                    color: "white"
                    anchors {
                        left: parent.left
                        right: parent.right
                    }
                }
                Text {
                    text: "Home Page: " + root.homePage
                    visible: root.homePage ? true : false
                    color: "white"
                    anchors {
                        left: parent.left
                        right: parent.right
                    }
                }
                Text {
                    text: "License: " + root.license
                    visible: root.license ? true : false
                    color: "white"
                    anchors {
                        left: parent.left
                        right: parent.right
                    }
                }
            }
            Text {
                id: txtSummary
                color: "white"
                wrapMode: Text.WordWrap
                anchors {
                    left: parent.left
                    right: parent.right
                }
            }
            Text {
                id: txtDescription
                color: "white"
                wrapMode: Text.WordWrap
                anchors {
                    left: parent.left
                    right: parent.right
                }
            }
        }
    }

    Rectangle {
        id: bottomBar
        color: "white"
        border.color: "gray"
        border.width: 1
        height: 45
        anchors {
            left: parent.left
            right: parent.right
            bottom: parent.bottom
        }

        ToggleButton {
            id: btnClose
            text: "Close"
            height: 20
            width: 110
            color: "#b8b8b8"
            anchors {
                left: parent.left
                bottom: parent.bottom
                margins: 10
            }
            toggledEnagled: false

            onClicked: {
                root.close();
            }
        }

        ToggleButton {
            id: btnInstall
            text: "Install"
            height: 20
            width: 110
            color: "#b8b8b8"
            anchors {
                right: parent.right
                bottom: parent.bottom
                margins: 10
            }
            toggledEnagled: false

            onClicked: {
                root.install();
            }
        }
    }

}