import QtQuick 1.1

Rectangle {
    id: root
    color: "#33363b"

    signal open(int index)
    signal ready

    property int duration: 300
    property int indexSelected: 0
    property int currentIndex: 0

    ParallelAnimation {
        id: animation
        running: false
        NumberAnimation { target: preview; property: "x"; to: 25; duration: root.duration }
        NumberAnimation { target: preview; property: "y"; to: 25; duration: root.duration }
        NumberAnimation { target: preview; property: "width"; to: 200; duration: root.duration}
        NumberAnimation { target: preview; property: "height"; to: 200; duration: root.duration}
        NumberAnimation { target: preview; property: "opacity"; to: 0; duration: root.duration}

        onCompleted: {
            preview.visible = false;
        }
    }

    ParallelAnimation {
        id: animationSelected
        running: false
        NumberAnimation { target: preview; property: "x"; to: 0; duration: root.duration }
        NumberAnimation { target: preview; property: "y"; to: 0; duration: root.duration }
        NumberAnimation { target: preview; property: "width"; to: root.width; duration: root.duration}
        NumberAnimation { target: preview; property: "height"; to: root.height; duration: root.duration}
        NumberAnimation { target: preview; property: "opacity"; to: 1; duration: root.duration}

        onCompleted: {
            root.open(root.indexSelected);
            imagePreview.source = "";
        }
    }

    Flickable {
        anchors.fill: parent
        contentHeight: grid.height

        Grid {
            id: grid
            columns: root.width > 700 ? 3 : 2
            spacing: 20
            anchors {
                left: parent.left
                top: parent.top
                right: parent.right
                margins: 20
            }

            Repeater {
                id: repeater
                model: ListModel {}

                Rectangle {
                    id: tile
                    color: "#24262c"
                    border.color: tile.focus ? "white" : "lightblue"
                    radius: 5
                    width: grid.width / grid.columns - grid.spacing
                    height: image.height + 5
                    focus: index == root.currentIndex ? true : false

                    property int widgetIndex: obj_index
                    property alias mouse: mouseArea

                    Image {
                        id: image
                        cache: false
                        width: grid.width / grid.columns - grid.spacing - 5
                        anchors.centerIn: parent
                        asynchronous: true
                        source: Qt.resolvedUrl(image_path)
                        fillMode: Image.PreserveAspectFit
                    }

                    Rectangle {
                        id: hover
                        anchors.fill: parent
                        opacity: tile.focus ? 0.2 : 0
                        color: "white"
                    }

                    MouseArea {
                        id: mouseArea
                        anchors.fill: parent
                        hoverEnabled: true
                        onClicked: {
                            preview.visible = true;
                            imagePreview.source = Qt.resolvedUrl(image_path);
                            root.indexSelected = widgetIndex;
                            animationSelected.start();
                        }

                        onEntered: {
                            tile.focus = true;
                            root.currentIndex = index;
                        }

                        onExited: {
                            tile.focus = false;
                            root.currentIndex = 0;
                        }
                    }
                }
            }
        }

    }

    Rectangle {
        id: preview
        x: 0
        y: 0
        width: parent.width
        height: parent.height
        color: "#33363b"

        Image {
            id: imagePreview
            anchors.fill: parent
            cache: false
            fillMode: Image.PreserveAspectFit

            onStatusChanged: {
                if (imagePreview.status == Image.Ready) {
                    root.ready();
                }
            }
        }
    }

    function add_preview(index, image_path) {
        imagePreview.source = Qt.resolvedUrl(image_path);
        root.indexSelected = index;
    }

    function add_widget(index, path){
        repeater.model.append({"obj_index": index, "image_path": path});
    }

    function start_animation() {
        animation.start();
    }

    function clear_model() {
        repeater.model.clear();
    }

    function close_selector() {
        preview.visible = true;
        animationSelected.start();
    }

    function calculate_index(key) {
        var columns = grid.columns;
        if (key == Qt.Key_Right) {
            var index = root.currentIndex + 1;
            if (index < repeater.count) {
                root.currentIndex = index;
            }
        } else if (key == Qt.Key_Left) {
            var index = root.currentIndex - 1;
            if (index >= 0) {
                root.currentIndex = index;
            }
        } else if (key == Qt.Key_Down) {
            var index = root.currentIndex + columns;
            if (index < repeater.count) {
                root.currentIndex = index;
            }
        } else if (key == Qt.Key_Up) {
            var index = root.currentIndex - columns;
            if (index >= 0) {
                root.currentIndex = index;
            }
        }
    }

    Keys.onPressed: {
        root.calculate_index(event.key);
        var item = repeater.itemAt(root.currentIndex);
        item.focus = true;
        if (event.key == Qt.Key_Return || event.key == Qt.Key_Enter) {
            item.mouse.clicked(null);
        }

        event.accepted = true;
    }

}
