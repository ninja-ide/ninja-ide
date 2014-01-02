import QtQuick 1.1

Rectangle {
    id: root

    radius: 10
    color: "#d7d7d7"

    PropertyAnimation {
        id: showAnim
        target: root
        properties: "opacity"
        easing.type: Easing.InOutQuad
        to: 1
        duration: 300
    }

    signal open(string path)
    signal close(string path)

    function show_animation() {
        root.opacity = 0;
        showAnim.running = true;
    }

    function open_item() {
        var path = listFiles.model.get(listFiles.currentIndex).path;
        root.open(path);
    }

    function set_model(model) {
        listFiles.currentIndex = 0;
        for(var i = 0; i < model.length; i++) {
            listFiles.model.append(
                {"name": model[i][0],
                "path": model[i][1],
                "checkers": model[i][2],
                "modified": model[i][3]});
        }
    }

    function clear_model() {
        listFiles.model.clear();
    }

    function next_item() {
        var index = listFiles.currentIndex + 1;
        if(index < listFiles.count) {
            listFiles.currentIndex = index;
        } else {
            listFiles.currentIndex = 0;
        }
    }

    function previous_item() {
        var index = listFiles.currentIndex - 1;
        if(index >= 0) {
            listFiles.currentIndex = index;
        } else {
            listFiles.currentIndex = listFiles.count - 1;
        }
    }

    Component {
        id: tabDelegate
        Item {
            id: item
            width: root.width;
            height: checkers ? 70 : 60

            ListView.onRemove: SequentialAnimation {
                PropertyAction { target: item; property: "ListView.delayRemove"; value: true }
                NumberAnimation { target: item; property: "scale"; to: 0; duration: 400; easing.type: Easing.InOutQuad }
                PropertyAction { target: item; property: "ListView.delayRemove"; value: false }
            }

            MouseArea {
                anchors.fill: parent

                onClicked: {
                    var coord = mapToItem(listFiles, mouseX, mouseY)
                    var index = listFiles.indexAt(coord.x, coord.y);
                    var path = listFiles.model.get(index).path;
                    root.open(path);
                }
            }

            Image {
                id: imgClose
                source: "img/delete-project.png"
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.margins: 7

                MouseArea {
                    anchors.fill: parent

                    onClicked: {
                        var coord = mapToItem(listFiles, mouseX, mouseY)
                        var index = listFiles.indexAt(coord.x, coord.y);
                        //FIXME: when index == 0 then start removing the wrong items
                        var path = listFiles.model.get(index).path;
                        listFiles.model.remove(index);
                        root.close(path);
                    }
                }
            }

            Column {
                id: col
                anchors {
                    top: parent.top
                    left: parent.left
                    right: parent.right
                    margins: 10
                }
                Text {
                    anchors {
                        left: parent.left
                        right: parent.right
                    }
                    color: modified ? "green" : "black"
                    font.pixelSize: 18
                    font.bold: true
                    text: name
                    font.italic: modified
                }
                Text {
                    anchors {
                        left: parent.left
                        right: parent.right
                    }
                    color: "gray"
                    elide: Text.ElideLeft
                    text: path
                }
            }
            Row {
                anchors {
                    right: parent.right
                    top: col.bottom
                    margins: 5
                }
                spacing: 10
                Repeater {
                    model: checkers
                    Text {
                        color: checker_color
                        text: checker_text
                        visible: checker_text.length > 0 ? true : false
                        font.pixelSize: 12
                    }
                }
            }
        }
    }

    ListView {
        id: listFiles
        anchors.fill: parent

        focus: true
        model: ListModel {}
        delegate: tabDelegate
        highlight: Rectangle { color: "lightsteelblue"; radius: 10; width: root.width }
        highlightMoveDuration: 200
    }
}
