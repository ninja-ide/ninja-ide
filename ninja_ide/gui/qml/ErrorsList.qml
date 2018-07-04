import QtQuick 2.5

Rectangle {
    id: root

    color: theme.FilesHandlerBackground
    focus: true

    signal open(int row)

    property var pep8Model: []
    property var errorModel: []

    function open_item() {
        var item;
        item = listFiles.model.get(listFiles.currentIndex);
        root.open(item.row);
    }

    function set_pep8_model(model) {
        listFiles.currentIndex = 0;
        pep8Model = model;
        refresh_model();
    }

    function set_error_model(model) {
        listFiles.currentIndex = 0;
        errorModel = model;
        refresh_model();
    }

    function refresh_model() {
        clear_model();
        for(var i = 0; i < pep8Model.length; i++) {
            listFiles.model.append(
                {"name": pep8Model[i][0],
                "codeLine": pep8Model[i][1],
                "row": pep8Model[i][2],
                "column": pep8Model[i][3],
                "bug": false,
                "expanded": false});
        }

        for(i = 0; i < errorModel.length; i++) {
            listFiles.model.append(
                {"name": errorModel[i][0],
                "codeLine": errorModel[i][1],
                "row": errorModel[i][2],
                "column": errorModel[i][3],
                "bug": true,
                "expanded": false});
        }
    }

    function clear_model() {
        listFiles.model.clear();
    }

    function next_item() {
        for (var i = 0; i < listFiles.model.count; i++) {
            if (listFiles.currentIndex == (listFiles.count - 1)) {
                listFiles.currentIndex = 0;
            } else {
                listFiles.incrementCurrentIndex();
            }
        }
    }

    function previous_item() {
        for (var i = 0; i < listFiles.model.count; i++) {
            if (listFiles.currentIndex == 0) {
                listFiles.currentIndex = (listFiles.count - 1);
            } else {
                listFiles.decrementCurrentIndex();
            }
        }
    }

    Component {
        id: tabDelegate

        Rectangle {
            id: item
            width: parent.width
            height: expanded ? 100 : 55;
            property bool current: ListView.isCurrentItem
            color: item.current ? theme.FilesHandlerCurrentItem : theme.FilesHandlerListView

            Behavior on height {
                NumberAnimation {
                    id: heightAnim
                    duration: 150
                    onRunningChanged: {
                        if(!heightAnim.running){
                            root.open_item();
                        }
                    }
                }
            }

            MouseArea {
                anchors.fill: parent

                onClicked: {
                    listFiles.model.get(listFiles.currentIndex).expanded = false;
                    listFiles.currentIndex = index;
                    listFiles.model.get(listFiles.currentIndex).expanded = true;
                }
            }

            Keys.onDownPressed: {
                root.next_item();
            }
            Keys.onUpPressed: {
                root.previous_item();
            }
            Keys.onEnterPressed: {
                listFiles.model.get(listFiles.currentIndex).expanded = false;
                listFiles.currentIndex = index;
                listFiles.model.get(listFiles.currentIndex).expanded = true;
            }
            Keys.onReturnPressed: {
                listFiles.model.get(listFiles.currentIndex).expanded = false;
                listFiles.currentIndex = index;
                listFiles.model.get(listFiles.currentIndex).expanded = true;
            }

            Image {
                id: imgType
                source: bug ? "img/bug.png" : "img/warning.png"
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.margins: 7
                sourceSize.width: 24
                sourceSize.height: 24
            }

            Column {
                id: colItem
                anchors {
                    top: parent.top
                    left: parent.left
                    right: parent.right
                    margins: 10
                }
                spacing: 5

                Text {
                    id: errorType
                    anchors {
                        left: parent.left
                        right: parent.right
                        rightMargin: imgType.width
                    }
                    property string message: "%1"
                    color: bug ? colors.bug : colors.warning
                    font.pixelSize: expanded ? 16 : 12
                    font.bold: true
                    text: message.arg(name)
                    elide: expanded ? Text.ElideNone : Text.ElideRight
                    wrapMode: expanded ? Text.WordWrap : Text.NoWrap
                    height: expanded ? 60 : 13

                    Behavior on font.pixelSize {
                        NumberAnimation { duration: 150 }
                    }
                }
                Row {
                    anchors {
                        left: parent.left
                        right: parent.right
                        rightMargin: 5
                    }
                    Text {
                        id: rowColText
                        property string message: "(%1, %2) - "
                        color: item.current ? theme.FilesHandlerText : theme.FilesHandlerAlternativeText
                        elide: Text.ElideLeft
                        text: message.arg(row + 1).arg(column)
                    }
                    Text {
                        color: item.current ? theme.FilesHandlerText : theme.FilesHandlerAlternativeText
                        elide: Text.ElideRight
                        text: codeLine
                        width: parent.width - rowColText.width
                    }
                }
            }
        }
    }

    ListView {
        id: listFiles
        anchors {
            fill: parent
            margins: 5
        }

        spacing: 2
        model: ListModel {}
        delegate: tabDelegate
        highlightMoveDuration: 200

        onActiveFocusChanged: console.log("focus")

        states: State {
            name: "showScroll"
            when: listFiles.movingVertically
            PropertyChanges { target: verticalScrollbar; opacity: 1}
        }

        transitions: Transition {
            NumberAnimation { properties: "opacity"; duration: 300 }
        }
    }

    ScrollBar {
        id: verticalScrollbar
        width: 8; height: listFiles.height
        anchors.right: listFiles.right
        opacity: 0
        orientation: Qt.Vertical
        position: listFiles.visibleArea.yPosition
        pageSize: listFiles.visibleArea.heightRatio
    }
}
