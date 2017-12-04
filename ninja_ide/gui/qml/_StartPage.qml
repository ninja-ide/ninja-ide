import QtQuick 2.3
import "widgets"

Rectangle {
    id: root

    property bool compressed: false

    signal markAsFavorite(string pat, bool value)
    signal newFile
    signal openProject(string path)
    signal removeProject(string path)
    signal openPreferences

    color: "#252526"

    onWidthChanged: {
        if(root.width < 850){
            compressed = true;
        }else{
            compressed = false;
        }
    }

    Rectangle {
        id: mainArea
        color: "#252526"
        anchors.fill: parent
        anchors.margins: parent.height / 14
        smooth: true
        // Flickable {
            /*
            anchors.fill: parent
            contentHeight: colLeft.height + 30
            clip: true*/

        Column {
            id: colLeft
            spacing: 10
            anchors {
                top: parent.top
                left: parent.left
                margins: 20
            }
            width: root.compressed ? parent.width - 40 : parent.width / 2 - 20

            Image {
                id: logo
                source: "img/logo.png"
                mipmap: true
                fillMode: Image.PreserveAspectFit
                anchors.left: parent.left
                anchors.right: parent.right
                smooth: true
            }

            Text {
                id: txtWelcome
                anchors.left: parent.left
                anchors.right: parent.right
                horizontalAlignment: Text.AlignHCenter
                color: "#eeeeec"
                text: qsTr("Welcome!")
                renderType: Text.NativeRendering
                font.bold: true
                font.pointSize: 45
            }

            Text {
                id: txtDescription
                renderType: Text.NativeRendering
                anchors.left: parent.left
                anchors.right: parent.right
                horizontalAlignment: Text.AlignHCenter
                text: qsTr("NINJA-IDE (from: \"Ninja-IDE Is Not Just Another IDE\"), is a cross-platform integrated development environment specifically designed to build Python Applications. NINJA-IDE provides the tools necessary to simplify the Python software development process and handles all kinds of situations thanks to its rich extensibility.")
                wrapMode: Text.WordWrap
                color: "#eeeeec"
            }

            Column {
                id: colButtons
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.leftMargin: 20
                spacing: 10

                property int buttonWidth: colLeft.width / 2 - 30
                Row {
                    spacing: 10
                    Button {
                        width: colButtons.buttonWidth
                        height: 35
                        text: qsTr("New File")
                        onClicked: root.newFile();
                    }
                    /*Button {
                        width: colButtons.buttonWidth
                        height: 35
                        text: "New Project"
                        onClicked: root.newFile();
                    }*/
                }
                Row {
                    spacing: 10
                    Button {
                        width: colButtons.buttonWidth
                        height: 35
                        text: qsTr("Chat with us!")
                        onClicked: Qt.openUrlExternally("https://kiwiirc.com/client/chat.freenode.net/?nick=Ninja|?&theme=cli#ninja-ide")
                    }
                    Button {
                        width: colButtons.buttonWidth
                        height: 35
                        text: qsTr("Preferences")
                        onClicked: openPreferences();
                    }
                }
            }
        }

        Column {
            id: colRight
            spacing: 10
            anchors {
                top: parent.top
                right: parent.right
                bottom: parent.bottom
                margins: 20
            }
            width: parent.width / 2 - 20
            visible: !root.compressed

            ProjectList {
                id: projectList
                anchors.left: parent.left
                anchors.right: parent.right

                onMarkAsFavorite: root.markAsFavorite(path, value);
                onOpenProject: root.openProject(path);
                onRemoveProject: root.removeProject(path);
            }
        }
    }

    Row {
        spacing: 10
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 5
        anchors.rightMargin: parent.height / 14
        visible: !root.compressed

        Text {
            text: "Powered by:"
            color: "#eeeeec"
            // style: Text.Raised
            renderType: Text.NativeRendering
            //styleColor: "black"
            height: logoPy.height
            verticalAlignment: Text.AlignVCenter
        }
        Image {
            id: logoPy
            source: "img/python-logo.png"
        }
        Image {
            id: logoQt
            source: "img/bwqt.png"
        }
    }

    Text {
        id: copyright
        renderType: Text.NativeRendering
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.leftMargin: parent.height / 14
        anchors.bottomMargin: 10
        font.pixelSize: 12
        color: "#eeeeec"
        text: "Copyright © 2010-" + new Date().getFullYear() + " NINJA-IDE is distributed under the terms of the GNU GPLv3+ copyleft license"
    }

    function add_project(name, path, favorite){
        projectList.add_project(name, path, favorite);
    }
}
