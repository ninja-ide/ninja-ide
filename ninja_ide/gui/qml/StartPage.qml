import QtQuick 2.5
//import QtQuick.Layouts 1.1
//import QtQuick.Controls 2.1

Rectangle {
    id: root

    property bool compressed: false
    signal onDrop(string files);
    signal openProject(string path)
    signal newFile
    color: theme.StartPageBackground;

    NumberAnimation {
        id: animationEnd
        running: false
        target: listContainer
        property: "opacity"
        to: 0;
        duration: 150
        onStopped:  {
            listContainer.visible = false
        }
    }

    ParallelAnimation {
        id: animation
        running: false
        NumberAnimation {
            target: features; property: "opacity"; to: 0; duration: 150
        }
        NumberAnimation {
            target: logo; property: "opacity"; to: 0; duration: 150
        }

        onStopped: {
            features.visible = false;
            logo.visible = false;
            listContainer.visible = true;
            //ani.start();
        }
    }

    NumberAnimation {
        id: ani
        target: listContainer; property: "opacity"; to: 1; duration: 150
    }

    ParallelAnimation {
        id: aniEnd
        NumberAnimation { target: features; property: "opacity"; to: 1; duration: 150 }
        NumberAnimation { target: logo; property: "opacity"; to: 1; duration: 150 }
    }


    DropArea {
        anchors.fill: parent
        onDropped: { onDrop(drop.urls); }

        Column {
            spacing: 40
            anchors.centerIn: parent

            Image { id: logo; source: "img/logo_black.png" }

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: "Ninja IDE Is Not Just Another IDE"
                renderType: Text.NativeRendering
                font.pointSize: 12
                color: theme.StartPageAlternativeText
                font.family: "monospace"
            }
            Rectangle {
                id: listContainer
                width: parent.width * 2
                border.width: 1
                border.color: "#282c34"
                color: "#21252b"
                height: 400
                visible: false
                opacity: 0

                ListView {
                    id: listProjects
                    //width: parent.width
                    anchors.fill: parent
                    anchors.margins: 5
                    height: 300
                    focus: true
                    clip: true
                    smooth: true
                    model: ListModel {}

                    delegate: Rectangle {
                        id: listItem
                        anchors {
                            left: parent.left
                            right: parent.right
                        }
                        height: 70
                        property bool current: ListView.isCurrentItem
                        color: listItem.current ? theme.LocatorCurrentItem : "#21252b"
                        Column {
                            id: col
                            spacing: 3
                            anchors.fill: parent
                            anchors.leftMargin: 10
                            Text {
                                id: projectName
                                text: name
                                color: theme.LocatorText
                                font.pixelSize: 22
                                font.bold: true
                            }
                            Text {
                                id: projectPath
                                text: path
                                color: listItem.current ? theme.LocatorText : theme.LocatorAlternativeText
                                font.pixelSize: 16
                            }
                        }

                        MouseArea {
                            anchors.fill: parent
                            onClicked: {
                                listProjects.currentIndex = index;
                            }
                            onDoubleClicked: {
                                root.openProject(listProjects.model.get(listProjects.currentIndex).path);
                            }
                        }
                    }
                    onVisibleChanged: {
                        if(visible) {
                            ani.start();
                        } else {
                            logo.visible = true;
                            if(features != null)
                                features.visible = true;
                            aniEnd.start();
                        }
                    }
                }
            }

            Column {
                id: features
                spacing: 0
                Text {
                    text: "• Open a Project with <%1>".arg(shortcuts.openproject)
                    color: theme.StartPageText
                    renderType: Text.NativeRendering
                    font.family: "monospace"
                }
                Text {
                    text: "• Locates anything in the project with <%1>".arg(shortcuts.locator)
                    color: theme.StartPageText
                    renderType: Text.NativeRendering
                    font.family: "monospace"
                }
                Text {
                    text: "• Drag and drop files here!"
                    color: theme.StartPageText
                    renderType: Text.NativeRendering
                    font.family: "monospace"
                }
            }

            /*Button {
                id: control
                text: listProjects.visible ? "Back" : "Open a Recent Project"
                anchors.horizontalCenter: parent.horizontalCenter
                property bool clicked: false
                contentItem: Text {
                    text: control.text
                    renderType: Text.NativeRendering
                    color: theme.WelcomeAlternativeTextColor
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }

                background: Rectangle {
                    implicitHeight: 40
                    implicitWidth: 100
                    radius: 2
                    opacity: enabled ? 1 : 0.3
                    color: control.down ? theme.WelcomeButtonSelected : theme.WelcomeButton
                }
                onClicked: {
                    if(control.clicked) {
                        control.clicked = false
                        animationEnd.start();
                    } else {
                        control.clicked = true;
                        animation.start();
                    }
                }
            }*/

            /*RowLayout {
                anchors.horizontalCenter: parent.horizontalCenter
                NButton {
                    text: "Open a Recent Project"
                    color: "red"
                }
                NButton {
                    text: "New File"
                }*/

                /*NButton {
                    id: control
                    text: listProjects.visible ? "Back" : "Open a Recent Project"
                    //anchors.horizontalCenter: parent.horizontalCenter
                    property bool clicked: false
                    /*contentItem: Text {
                        text: control.text
                        renderType: Text.NativeRendering
                        color: theme.WelcomeAlternativeTextColor
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }

                    /*background: Rectangle {
                        implicitHeight: 40
                        implicitWidth: 100
                        radius: 2
                        opacity: enabled ? 1 : 0.3
                        color: control.down ? theme.WelcomeButtonSelected : theme.WelcomeButton
                    }
                    onClicked: {
                        if(control.clicked) {
                            control.clicked = false
                            animationEnd.start();
                        } else {
                            control.clicked = true;
                            animation.start();
                        }
                    }
                }*/

               /* Button {
                    id: control2
                    visible: !listProjects.visible
                    text: "New File"
                    //anchors.horizontalCenter: parent.horizontalCenter
                    property bool clicked: false
                    contentItem: Text {
                        text: control2.text
                        renderType: Text.NativeRendering
                        color: theme.WelcomeAlternativeTextColor
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }

                    background: Rectangle {
                        implicitHeight: 40
                        implicitWidth: 100
                        radius: 2
                        opacity: enabled ? 1 : 0.3
                        color: control2.down ? theme.WelcomeButtonSelected : theme.WelcomeButton
                    }
                    onClicked: root.newFile();
                }*/
        //}

            Text {
                id: link
                anchors.horizontalCenter: parent.horizontalCenter
                text: "ninja-ide.org"
                color: theme.StartPageLink
                font.family: "monospace"
                font.pointSize: 8
                renderType: Text.NativeRendering
                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: containsMouse ? Qt.PointingHandCursor : Qt.ArrowCursor;
                    onHoveredChanged: {
                        if(link.font.underline) {
                            link.font.underline = false
                        } else {
                            link.font.underline = true;
                        }
                    }
                    onClicked: Qt.openUrlExternally("http://ninja-ide.org");
                }
            }
        }
    }

    Image {
        source: "img/bwqute.png"
        anchors {
            right: parent.right
            bottom: parent.bottom
            rightMargin: 10
            bottomMargin: 10
        }
    }

    function addProject(name, path, lastOpen) {
        listProjects.model.append({"name": name, "path": path, "lastOpen": lastOpen});
    }
}
