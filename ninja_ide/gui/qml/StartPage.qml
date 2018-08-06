import QtQuick 2.5
//import QtQuick.Layouts 1.1
//import QtQuick.Controls 2.1

Rectangle {
    id: root

    signal onDrop(string files);
    signal openProject(string path)
    signal newFile
    color: theme.StartPageBackground;

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
                }
            }

            Column {
                id: features
                spacing: 0
                Row {
                    Text {
                        text: "Open a Project with "
                        color: theme.StartPageText
                        renderType: Text.NativeRendering
                        font.family: "monospace"
                    }
                    Rectangle {
                        width: shor.width + 10
                        height: shor.height
                        Text {
                            id: shor
                            anchors.centerIn: parent
                            text: shortcuts.openproject
                            color: theme.StartPageText
                            renderType: Text.NativeRendering
                            font.bold: true
                        }
                        color: "#333"
                        radius: 3
                    }
                }
                Row {
                    Text {
                        text: "Locates anything in the project with "
                        color: theme.StartPageText
                        renderType: Text.NativeRendering
                        font.family: "monospace"
                    }
                    Rectangle {
                        width: shor2.width + 10
                        height: shor2.height
                        Text {
                            id: shor2
                            anchors.centerIn: parent
                            text: shortcuts.locator
                            color: theme.StartPageText
                            renderType: Text.NativeRendering
                            font.bold: true
                        }
                        color: "#333"
                        radius: 3
                    }
                }
                Text {
                    text: "Drag and drop files here!"
                    color: theme.StartPageText
                    renderType: Text.NativeRendering
                    font.family: "monospace"
                }
            }

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
}
