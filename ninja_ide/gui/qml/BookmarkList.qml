import QtQuick 2.5

Rectangle {
    id: root

    color: theme.FilesHandlerBackground
    focus: true

    signal menuRequested(int x, int y, int index);
    signal openBookmark(string fname, int line);

    MouseArea {
        anchors.fill: parent
        acceptedButtons: Qt.LeftButton | Qt.RightButton
        onClicked: {
            if (mouse.button & Qt.RightButton) {
                var index = listBookmarks.indexAt(mouseX, mouseY)
                root.menuRequested(mouseX, mouseY, index);
            }
        }
    }
    Component {
        id: bookDelegate

        Rectangle {
            id: item
            width: parent.width
            height: 55
            property bool current: ListView.isCurrentItem
            color:item.current ? theme.FilesHandlerCurrentItem : theme.FilesHandlerListView

            MouseArea {
                anchors.fill: parent
                onClicked: {
                    listBookmarks.currentIndex = index;
                    root.openBookmark(filename, lineno);
                }
            }

            Text {
                id: fnameText
                anchors.left: parent.left
                anchors.top: parent.top
                anchors.right: linenoText.left
                anchors.margins: 5
                color: item.current ? "#8080ff" : theme.FilesHandlerText
                elide: Text.ElideRight
                font.pixelSize: 16
                font.bold: true
                text: displayname
            }
            Text {
                id: linenoText
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.margins: 5
                color: item.current ? "#8080ff" : theme.FilesHandlerText
                text: lineno + 1
            }
            Text {
                id: lineText
                anchors.bottom: parent.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.margins: 5
                color: theme.FilesHandlerAlternativeText
                elide: Text.ElideRight
                text: note != "" ? note : linetext
            }
        }
    }

    ListView {
        id: listBookmarks
        anchors.fill: parent
        anchors.margins: 5
        spacing: 2
        model: bookmarkModel
        delegate: bookDelegate
    }
}
