import QtQuick 1.1

Rectangle {
    id: root

    property bool compressed: false

    signal markAsFavorite(string pat, bool value)
    signal newFile
    signal openProject(string path)
    signal removeProject(string path)
    signal openPreferences

    gradient: Gradient {
        GradientStop { position: 0.0; color: "#2f2f2f" }
        GradientStop { position: 0.5; color: "#2f2f2f" }
        GradientStop { position: 0.5; color: "#454545" }
        GradientStop { position: 1.0; color: "#454545" }
    }

    onWidthChanged: {
        if(root.width < 650){
            compressed = true;
        }else{
            compressed = false;
        }
    }

    Rectangle {
        id: mainArea
        color: "white"
        border.color: "gray"
        anchors.fill: parent
        radius: 15
        anchors.margins: parent.height / 14
        smooth: true

        Flickable {
            anchors.fill: parent
            contentHeight: colLeft.height + 30
            clip: true

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
                    source: "img/ninja-ide.png"
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
                    color: "#2f2d2d"
                    text: "Welcome!"
                    font.bold: true
                    font.pointSize: 45
                }

                Text {
                    id: txtDescription
                    anchors.left: parent.left
                    anchors.right: parent.right
                    horizontalAlignment: Text.AlignHCenter
                    text: "NINJA-IDE (from: \"Ninja-IDE Is Not Just Another IDE\"), is a cross-platform integrated development environment specifically designed to build Python Applications. NINJA-IDE provides the tools necessary to simplify the Python software development process and handles all kinds of situations thanks to its rich extensibility."
                    wrapMode: Text.WordWrap
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
                            text: "New File"
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
                            text: "Chat with us!"
                            onClicked: Qt.openUrlExternally("https://kiwiirc.com/client/chat.freenode.net/?nick=Ninja|?&theme=cli#ninja-ide")
                        }
                        Button {
                            width: colButtons.buttonWidth
                            height: 35
                            text: "Preferences"
                            onClicked: openPreferences();
                        }
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
        anchors.bottomMargin: 15
        anchors.rightMargin: parent.height / 14
        visible: !root.compressed

        Text {
            text: "Powered by:"
            color: "white"
            style: Text.Raised
            styleColor: "black"
            height: logoPy.height
            verticalAlignment: Text.AlignVCenter
        }
        Image {
            id: logoPy
            source: "img/powered_py.png"
        }
        Image {
            id: logoQt
            source: "img/powered_qt.png"
        }
    }

    Text {
        id: copyright
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.leftMargin: parent.height / 14
        anchors.bottomMargin: 10
        font.pixelSize: 12
        color: "white"
    }

    function add_project(name, path, favorite){
        projectList.add_project(name, path, favorite);
    }

    function set_year(year){
        copyright.text = "Copyright © 2010-" + year + " NINJA-IDE is distributed under the terms of the GNU GPLv3+ copyleft license";
    }

}
