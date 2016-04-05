import QtQuick 2.3

Rectangle {
    id: root
    color: "#33363b"

    width: 100
    height: 100

    signal open(int index)
    signal ready()
    signal animationCompleted()
    signal closePreviewer()

    property int duration: 300
    property int indexSelected: 0
    property int currentIndex: 0
    property variant removed: new Array()

    //property var image_path: null

    function get_removed() {
        return root.removed;
    }

    function select_item(index) {
        print("select_item", index)
        preview.visible = true;
        var image_of_path = repeater.model.get(index).image__path;
        var obj_index = repeater.model.get(index).obj_index;
        imagePreview.source = Qt.resolvedUrl(image_of_path);
        root.indexSelected = obj_index;
        animationSelected.start();
    }

    function close_item(index) {
        var obj_index = repeater.model.get(index).obj_index;
        var array = root.removed
        array.push(obj_index)
        root.removed = array;
        repeater.model.remove(index);
    }

    ParallelAnimation {
        id: animation
        running: false
        NumberAnimation { target: preview; property: "x"; to: 25; duration: root.duration }
        NumberAnimation { target: preview; property: "y"; to: 25; duration: root.duration }
        NumberAnimation { target: preview; property: "width"; to: 200; duration: root.duration}
        NumberAnimation { target: preview; property: "height"; to: 200; duration: root.duration}
        NumberAnimation { target: preview; property: "opacity"; to: 0; duration: root.duration}

        onStarted: {
            preview.visible = false
        }

        Component.onCompleted: {
            preview.visible = false;
            root.animationCompleted();
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

        onStarted: {
            preview.visible = true
        }

        Component.onCompleted: {
            root.open(root.indexSelected);
            imagePreview.source = "";
            repeater.model.clear();
        }
    }

    Image {
        id: imag
        source: "img/delete-project_rojo.png"
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.margins: 7//margenes
        visible: !preview.visible
        z:2
        fillMode: Image.PreserveAspectFit
        //property double margenes: 7

        Behavior on width {
            NumberAnimation { easing.type: Easing.InOutBack; duration: 300 }
        }
        Behavior on height {
            NumberAnimation { easing.type: Easing.InOutBack; duration: 300 }
        }
        Behavior on anchors.margins {
            NumberAnimation { easing.type: Easing.InOutBack; duration: 300 }
        }

        states: [
            State {
                name: "zoomIn"
                PropertyChanges { target: imag; width: 1.8*sourceSize.width }
                PropertyChanges { target: imag; height: 1.8*sourceSize.height }
                PropertyChanges { target: imag; anchors.margins: 1 }
            },
            State {
                name: "zoomOut"
                PropertyChanges { target: imag; width: 0.8*sourceSize.width }
                PropertyChanges { target: imag; height: 0.8*sourceSize.height }
                PropertyChanges { target: imag; anchors.margins: 7 }
        }]


        MouseArea {
            anchors.fill: parent
            hoverEnabled: true

            onEntered: {
                //print("onEntered")
                imag.state = "zoomIn"
            }
            onExited: {
                //print("onExited")
                imag.state = "zoomOut"
            }

            onClicked: {
                //print("closePreviewer")
                closePreviewer()
            }
        }
    }

    Flickable {
        id: flip
        anchors.fill: parent
        contentHeight: grid.height
        visible: !preview.visible

        Grid {
            id: grid
            columns: root.width > 700 ? 3 : 2
            spacing: 20
            
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.right: parent.right
            anchors.margins: 20
            

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

                    property alias mouse: mouseArea

                    Image {
                        id: image
                        cache: false
                        width: grid.width / grid.columns - grid.spacing - 5
                        anchors.centerIn: parent
                        asynchronous: true
                        source: Qt.resolvedUrl(image__path)
                        fillMode: Image.PreserveAspectFit
                        smooth: true
                        //Component.onCompleted: print("source",source, "\n")
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
                            select_item(index);
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

                    Rectangle {
                        anchors.fill: imgClose
                        anchors.margins: 2
                        radius: width / 2
                        color: "white"
                        visible: closable
                    }

                    Image {
                        id: imgClose
                        source: "img/delete-project.png"
                        anchors.right: parent.right
                        anchors.top: parent.top
                        anchors.margins: 7
                        visible: closable

                        MouseArea {
                            anchors.fill: parent

                            onClicked: {
                                close_item(index);
                            }
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
            smooth: true
            asynchronous: true
            // source: Qt.resolvedUrl(root.image_path)//agragado
            // Component.onCompleted: print("Image", root.image_path)

            onStatusChanged: {
                print("Image222222", source)
                if (imagePreview.status == Image.Ready) {
                    root.ready();
                }
            }
            Image {
                source: "img/delete-project_rojo.png"
                anchors.right: parent.right
                anchors.top: parent.top
                //anchors.margins: 5
                fillMode: Image.PreserveAspectFit
                width: 1.3*sourceSize.width
                height: 1.3*sourceSize.height

                MouseArea {
                    anchors.fill: parent

                    onClicked: {
                        start_animation()
                    }
                }
            }
        }
    }

    function add_preview(index, path) {
        print("add_preview", index)
        //print("Qt.resolvedUrl(path)", Qt.resolvedUrl(path), path, Qt.resolvedUrl(path))
        imagePreview.source = Qt.resolvedUrl(path);//Qt.resolvedUrl(path);
        root.indexSelected = index;
    }

    function add_widget(index, path, closable) {
        //print("add_widget", index, path, closable)
        /*if (!root.image_path) {
            root.image_path = path
        }*/
        repeater.model.append({"obj_index": index, "image__path": path, "closable": closable});
    }

    function start_animation() {
        animation.start();
    }

    function showPreview() {
        preview.visible = true;
        animationSelected.start();
    }

    function close_selector() {
        preview.visible = true;
        animationSelected.start();
    }

    function clean_removed() {
        var array = new Array();
        root.removed = array;
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
