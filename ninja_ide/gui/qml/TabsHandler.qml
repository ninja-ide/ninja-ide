import QtQuick 1.1

Rectangle {
    id: root

    radius: 10

    gradient: Gradient {
        GradientStop { position: 0.0; color: "#dfdfdf" }
        GradientStop { position: 0.6; color: "#a0a0a0" }
    }

    PropertyAnimation {
        id: showAnim
        target: root
        properties: "opacity"
        easing.type: Easing.InOutQuad
        to: 1
        duration: 300
    }

    signal open(string path)

    function show_animation() {
        root.opacity = 0;
        showAnim.running = true;
    }

    function open_item() {
        var path = listFiles.model.get(listFiles.currentIndex).path;
        root.open(path);
    }

    function set_model(model) {
        listFiles.model.clear();
        listFiles.currentIndex = 0;
        for(var i = 0; i < model.length; i++) {
            listFiles.model.append(
                {"name": model[i][0],
                "path": model[i][1],
                "checkers": model[i][2],
                "modified": model[i][3]});
        }
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
            property string _name: name
            property string _path: path

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
