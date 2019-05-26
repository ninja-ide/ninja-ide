import QtQuick 2.6

Rectangle {
    id: root

    property int _padding: (mainArea.width / 4)
    property bool compressed: true
    signal markAsFavorite(string pat, bool value)
    signal openProject(string path)
    signal removeProject(string path)
    signal openPreferences
    color: "#1e1e1e"
//    gradient: Gradient {
//         GradientStop { position: 0.0; color: "#1e1e1e" }
//         GradientStop { position: 1.0; color: "#a4a4a4" }
//     }

    onWidthChanged: {
        if(root.width < 500){
            compressed = true;
            root._padding = (mainArea.width / 2);
            logo.width = 300;
            txtProjects.visible = false;
            projectList.visible = false;
        }else{
            compressed = false;
            root._padding = (mainArea.width / 4);
            logo.width = logo.sourceSize.width;
            txtProjects.visible = true;
            projectList.visible = true;
        }
    }

    Rectangle {
        id: mainArea
        color: "#1e1e1e"
        anchors.fill: parent
        smooth: true
        anchors.margins: 60
        Image {
            id: logo
            source: "img/logo_black.png"
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.leftMargin: root.compressed ? 10 : root.get_padding(logo);
            anchors.topMargin: 10
            fillMode: Image.PreserveAspectFit
        }

        Text {
            id: txtWelcome
            anchors.left: parent.left
            anchors.top: logo.bottom
            anchors.leftMargin: root.compressed ? 10 : root.get_padding(txtWelcome);
            anchors.topMargin: 15
            color: "#ffffff"
            text: "Welcome!"
            font.bold: true
            font.pointSize: 45
            style: Text.Raised
            styleColor: "black"
        }

        Text {
            id: txtDescription
            width: compressed ? parent.width - 20 : root._padding * 1.5
            anchors.left: parent.left
            anchors.top: txtWelcome.bottom
            anchors.leftMargin: root.compressed ? 10 : root.get_padding(txtDescription);
            anchors.topMargin: 10
            color: "#ffffff"
            text: "NINJA-IDE (from: \"Ninja-IDE Is Not Just Another IDE\"), is a cross-platform integrated development environment specially designed to build Python Applications. NINJA-IDE provides tools to simplify the Python-software development and handles all kinds of situations thanks to its rich extensibility."
            wrapMode: Text.WordWrap
            renderType: Text.NativeRendering
        }

        Column {
            id: colButtons
            anchors.top: txtDescription.bottom
            anchors.left: parent.left
            anchors.leftMargin: root.compressed ? 10 : root.get_padding(colButtons);
            anchors.topMargin: root.compressed ? 10 : 50

            property int buttonWidth: compressed ? (mainArea.width / 2) - 20 : (mainArea.width / 4) - 50
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

        Text {
            id: txtProjects
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.rightMargin: root.get_padding(txtProjects);
            anchors.topMargin: 30
            color: "#ffffff"
            text: "Recent Projects:"
            font.bold: true
            font.pointSize: 30
            style: Text.Raised
            styleColor: "black"
        }

        ProjectList {
            id: projectList
            width: (parent.width / 2) - 20
            height: parent.height - txtProjects.height - 70
            anchors.right: parent.right
            anchors.top: txtProjects.bottom
            anchors.rightMargin: root.get_padding(projectList)
            anchors.topMargin: 10

            onMarkAsFavorite: root.markAsFavorite(path, value);
            onOpenProject: root.openProject(path);
            onRemoveProject: root.removeProject(path);
        }
    }

    Text {
        anchors {
            bottom: parent.bottom
            left: parent.left
            bottomMargin: 15
            leftMargin: 10
        }

        color: "#ffffff"
        text: "Copyright © 2011-2013 NINJA-IDE under GPLv3 License agreements"
        renderType: Text.NativeRendering
    }

    Row {
        spacing: 10
        anchors.bottom: parent.bottom
        anchors.right: parent.right
        anchors.margins: 10
        Text {
            text: "Powered by:"
            color: "white"
            verticalAlignment: Text.AlignVCenter
            height: python.height
        }
        Image {
            id: python
            source: "img/python-logo.png"
        }
        Image {
            id: bwqt
            source: "img/bwqt.png"
        }
    }

    function get_padding(item){
        var newPadding = (root._padding - (item.width / 2)) - 10;
        return newPadding;
    }

    function add_project(name, path, favorite){
        projectList.add_project(name, path, favorite);
    }

}
