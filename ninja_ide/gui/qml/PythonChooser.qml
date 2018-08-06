import QtQuick 2.6

Rectangle {
    id: root
    color: "black"
    radius: 3
    focus: true

    signal pythonSelected(string path)

    function setModel(model) {
        for( var i = 0; i < model.length; i++ ) {
            pythonList.model.append({
                "name": model[i][0],
                "path": model[i][1],
                "pexec": model[i][2]
            })
        }
        forceActiveFocus();
    }

    function clearModel() {
        pythonList.model.clear();
    }

    Keys.onDownPressed: {
        pythonList.incrementCurrentIndex();
    }

    Keys.onUpPressed: {
        pythonList.decrementCurrentIndex();
    }

    ListView {
        id: pythonList
        anchors.fill: parent
        anchors.margins: 5
        spacing: 2
        boundsBehavior: Flickable.StopAtBounds
        clip: true
        model: ListModel {}
        delegate: Rectangle {
            id: item
            anchors.left: parent.left
            anchors.right: parent.right
            height: 40
            property bool current: ListView.isCurrentItem
            color: item.current ? "#ed8200" : "black"
            Column {
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.margins: 3
                Text {
                    text: name;
                    color: "white"
                    font.bold: true
                    font.pixelSize: 16
                    renderType: Text.NativeRendering
                }
                Text {
                    text: path;
                    color: "white"
                    renderType: Text.NativeRendering
                }
            }

            MouseArea {
                anchors.fill: parent
                onClicked: {
                    pythonList.currentIndex = index;
                    root.pythonSelected(pexec);
                }
            }
        }

        states: State {
            name: "showScroll"
            when: pythonList.movingVertically
            PropertyChanges { target: scrollbar; opacity: 1 }
        }

        transitions: Transition {
            NumberAnimation { properties: "opacity"; duration: 300 }
        }
    }

    ScrollBar {
        id: scrollbar
        width: 5; height: pythonList.height
        anchors.right: pythonList.right
        opacity: 0
        orientation: Qt.Vertical
        position: pythonList.visibleArea.yPosition
        pageSize: pythonList.visibleArea.heightRatio
    }
}
