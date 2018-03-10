import QtQuick 2.5

Rectangle {
    id: root

    color: theme.FilesHandlerBackground
    focus: true
    property bool simple: false
    PropertyAnimation {
        id: showAnim
        target: root
        properties: "opacity"
        easing.type: Easing.InOutQuad
        to: 1
        duration: 300
    }

    signal open(string path, string tempFile, string project)
    signal close(string path, string tempFile)
    signal hide
    signal fuzzySearch(string search)

    function setMode(mode) {
        root.simple = mode;
    }

    function activateInput() {
        input.text = "";
        input.forceActiveFocus();
    }

    function show_animation() {
        root.opacity = 0;
        showAnim.running = true;
    }

    function open_item() {
        var item;
        if (listFiles.visible) {
            item = listFiles.model.get(listFiles.currentIndex);
        } else {
            item = listFuzzyFiles.model.get(listFuzzyFiles.currentIndex);
        }
        var path = item.path;
        var tempFile = item.tempFile;
        var project = item.project;
        root.open(path, tempFile, project);
    }

    function set_model(model) {
        listFiles.currentIndex = 0;
        for(var i = 0; i < model.length; i++) {
            listFiles.model.append(
                {"name": model[i][0],
                "path": model[i][1],
                "checkers": model[i][2],
                "modified": model[i][3],
                "tempFile": model[i][4],
                "project": "",
                "itemVisible": true});
        }
    }

    function set_fuzzy_model(model) {
        listFuzzyFiles.model.clear();
        listFuzzyFiles.currentIndex = 0;
        for(var i = 0; i < model.length; i++) {
            listFuzzyFiles.model.append(
                {"name": model[i][0],
                "path": model[i][1],
                "project": model[i][2],
                "checkers": "",
                "modified": "",
                "tempFile": "",
                "itemVisible": true});
        }
    }

    function clear_model() {
        listFiles.model.clear();
        listFuzzyFiles.model.clear();
    }

    function next_item() {
        if (listFiles.visible) {
            for (var i = 0; i < listFiles.model.count; i++) {
                if (listFiles.currentIndex == (listFiles.count - 1)) {
                    listFiles.currentIndex = 0;
                } else {
                    listFiles.incrementCurrentIndex();
                }
                if (listFiles.model.get(listFiles.currentIndex).itemVisible) {
                    break
                }
            }
        } else {
            if (listFuzzyFiles.currentIndex == (listFuzzyFiles.count - 1)) {
                listFuzzyFiles.currentIndex = 0;
            } else {
                listFuzzyFiles.incrementCurrentIndex();
            }
        }
    }

    function previous_item() {
        if (listFiles.visible) {
            for (var i = 0; i < listFiles.model.count; i++) {
                if (listFiles.currentIndex == 0) {
                    listFiles.currentIndex = (listFiles.count - 1);
                } else {
                    listFiles.decrementCurrentIndex();
                }
                if (listFiles.model.get(listFiles.currentIndex).itemVisible) {
                    break
                }
            }
        } else {
            if (listFuzzyFiles.currentIndex == 0) {
                listFuzzyFiles.currentIndex = (listFuzzyFiles.count - 1);
            } else {
                listFuzzyFiles.decrementCurrentIndex();
            }
        }
    }

    Rectangle {
        id: inputArea
        //radius: 2
        color: theme.FilesHandlerInput
        height: 30
        anchors {
            left: parent.left
            right: parent.right
            top: parent.top
            margins: 5
        }
        border.color: theme.RectangleBorder
        border.width: 2

        TextInput {
            id: input
            anchors {
                fill: parent
                margins: 4
            }

            clip: true
            focus: true
            smooth: true
            color: theme.FilesHandlerText
            font.pixelSize: 18
            onTextChanged: {
                var firstValidItem = -1;
                for (var i = 0; i < listFiles.model.count; i++) {
                    var item = listFiles.model.get(i);
                    if (item.name.indexOf(input.text) == -1) {
                        item.itemVisible = false;
                    } else {
                        if (firstValidItem == -1) firstValidItem = i;
                        item.itemVisible = true;
                    }
                }
                listFiles.currentIndex = firstValidItem;
                if (firstValidItem == -1) {
                    listFiles.visible = false;
                    fuzzySearch(input.text);
                } else {
                    listFiles.visible = true;
                }
            }

            Keys.onDownPressed: {
                root.next_item();
            }
            Keys.onUpPressed: {
                root.previous_item();
            }
            Keys.onEnterPressed: {
                root.open_item();
            }
            Keys.onReturnPressed: {
                root.open_item();
            }
        }
    }

    Text {
        id: fuzzyText
        color: "white"
        font.pixelSize: 10
        font.bold: true
        anchors {
            left: parent.left
            right: parent.right
            top: inputArea.bottom
            margins: 5
        }
        horizontalAlignment: Text.AlignHCenter
    }

    Component {
        id: tabDelegate
        Rectangle {
            id: item
            visible: itemVisible
            width: parent.width
            property int defaultValues: checkers && (!root.simple) ? 70 : (listFuzzyFiles.visible && root.simple) ? 40: 60
            height: itemVisible ? defaultValues : 0
            property bool current: ListView.isCurrentItem
            color: item.current ? theme.FilesHandlerCurrentItem : theme.FilesHandlerListView

            property string mainTextColor: item.current ? theme.FilesHandlerText : "red"
            property string mainTextModifiedColor: item.current ? theme.FilesHandlerText : "green"

            SequentialAnimation {
                id: closeAnimation
                PropertyAction { target: item; property: "ListView.delayRemove"; value: true }
                NumberAnimation { target: item; property: "scale"; to: 0; duration: 250; easing.type: Easing.InOutQuad }
                PropertyAction { target: item; property: "ListView.delayRemove"; value: false }
            }

            MouseArea {
                anchors.fill: parent

                onClicked: {
                    if (listFiles.visible) {
                        listFiles.currentIndex = index;
                    } else {
                        listFuzzyFiles.currentIndex = index;
                    }
                    root.open_item();
                }
            }

            Rectangle {
                anchors.fill: imgClose
                anchors.margins: 2
                radius: width / 2
                color: "black"
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
                        var path = listFiles.model.get(index).path;
                        var tempFile = listFiles.model.get(index).tempFile;
                        root.close(path, tempFile);
                        listFiles.model.remove(index);
                        if(listFiles.model.count === 0) {
                            root.hide()
                        }
                        closeAnimation.start();
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
                        rightMargin: imgClose.width
                    }
                    color: modified ? mainTextModifiedColor : theme.FilesHandlerText
                    font.pixelSize: 18
                    font.bold: true
                    text: name
                    elide: Text.ElideRight
                    font.italic: modified
                }
                Text {
                    anchors {
                        left: parent.left
                        right: parent.right
                    }
                    visible: !root.simple
                    color: item.current ? theme.FilesHandlerText : theme.FilesHandlerAlternativeText
                    elide: Text.ElideLeft
                    text: path
                }
            }
            Row {
                anchors {
                    right: parent.right
                    top: col.bottom
                    margins: 3
                }
                visible: !root.simple
                spacing: 10
                Repeater {
                    model: checkers
                    Text {
                        renderType: Text.NativeRendering
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
        anchors {
            left: parent.left
            right: parent.right
            bottom: parent.bottom
            top: inputArea.bottom
            margins: 5
        }
        spacing: 2

        clip: true
        model: ListModel {}
        delegate: tabDelegate
        highlightMoveDuration: 200
    }

    ListView {
        id: listFuzzyFiles
        anchors {
            left: parent.left
            right: parent.right
            bottom: parent.bottom
            top: inputArea.bottom
            margins: 5
        }
        visible: !listFiles.visible
        spacing: 2

        clip: true
        model: ListModel {}
        delegate: tabDelegate
        highlightMoveDuration: 200
    }
}
