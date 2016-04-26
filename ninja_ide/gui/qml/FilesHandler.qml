import QtQuick 2.4
import QtQuick.Controls 1.4

Rectangle {
    id: root

    width: 400
    height: 400

    radius: 5
    color: "#202123"
    border.width: 1
    border.color: "gray"

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

    function activateInput() {
        input.text = "";
        input.forceActiveFocus();
        input.selectAll();
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

    function add_File(item) {
        print("add_File", item)
        listFiles.model.append(
            {"name": item[i][0],
            "path": item[i][1],
            "checkers": item[i][2],
            "modified": item[i][3],
            "tempFile": item[i][4],
            "project": "",
            "itemVisible": true});
    }

    function remove_File(file_path) {
        print("remove_File", file_path)
        listFiles.currentIndex = 0;
        for(var i = 0; i < listFiles.model.length; i++) {
            if (listFiles.model[i]["path"] === file_path) {
                listFiles.model.remove(i)
            }
        }
    }
/*
    function sort_model() 
        for(var i = 0; i < listFiles.model.length; i++) {
            if (listFiles.model[i]["path"] === file_path) {
                listFiles.model.remove(i)
            }
        }        
    }*/

    function set_model(model) {
        // print("set_model", model)
        listFiles.currentIndex = 0;
        for(var i = 0; i < model.length; i++) {
            listFiles.model.append(
                {"name": model[i][0],
                "path": model[i][1],
                "checkers": model[i][2],
                "modified": model[i][3],
                "tempFile": model[i][4],
                "project": model[i][5],
                "itemVisible": model[i][6]});
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
        print("next_item\n")
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
        objectName: "--Rectangle--"
        radius: 2
        color: "#2d2f31"
        height: 30
        
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.margins: 10
        
        border.color: "black"
        border.width: 1
        smooth: true

        TextInput {
            id: input
            objectName: "--TextInput--"
            
            anchors.fill: parent
            anchors.margins: 4
            
            focus: true
            //clip: true
            color: "orange"
            selectionColor: "red"
            selectByMouse: true
            font.pixelSize: 18
            activeFocusOnPress: true

            Image {
                id: imag
                anchors.right: parent.right
                anchors.rightMargin: 0
                anchors.verticalCenter: parent.verticalCenter
                height: 20
                width: 20
                source: "img/delete-project_rojo.png"
                fillMode: Image.PreserveAspectFit

                Behavior on width {
                    NumberAnimation { easing.type: Easing.InOutBack; duration: 100 }
                }
                Behavior on height {
                    NumberAnimation { easing.type: Easing.InOutBack; duration: 100 }
                }
                Behavior on anchors.rightMargin {
                    NumberAnimation { easing.type: Easing.InOutBack; duration: 100 }
                }

                states: [
                    State {
                        name: "zoomIn"
                        PropertyChanges { target: imag; width: 20; }
                        PropertyChanges { target: imag; height: 20;  }
                        PropertyChanges { target: imag; anchors.rightMargin: 0; }
                    },
                    State {
                        name: "zoomOut"
                        PropertyChanges { target: imag; width: 15; }
                        PropertyChanges { target: imag; height: 15; }
                        PropertyChanges { target: imag; anchors.rightMargin: 2.5; }
                    }
                ]

                MouseArea{
                    id: but
                    anchors.fill: parent
                    onPressed:{
                        imag.state = "zoomOut"
                    }

                    onReleased:{
                        imag.state = "zoomIn"
                    }

                    onClicked: input.text= ""
                }
            }

            Keys.onEscapePressed: {
                print("Keys.onEscapePressed")
                Qt.quit();
            }
            Keys.onDownPressed: {
                print("Keys.onDownPressed")
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
            /*Keys.onDigit8Pressed: {
                rawObj.view_WinFlags();
            }*/

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

        }

    }

    Text {
        id: fuzzyText
        color: "white"
        font.pixelSize: 10
        font.bold: true
        
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: inputArea.bottom
        anchors.margins: 5
        
        horizontalAlignment: Text.AlignHCenter
    }

    Component {
        id: tabDelegate
        Rectangle {
            id: item
            visible: itemVisible
            width: parent.width
            property int defaultValues: checkers ? 70 : 60
            height: itemVisible ? defaultValues : 0
            property bool current: ListView.isCurrentItem
            color: item.current ? "#4182c4" : "#27292b"

            property string mainTextColor: item.current ? "white" : "#aaaaaa"
            property string mainTextModifiedColor: item.current ? "lightgreen" : "green"

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
                color: "white"
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
                        //FIXME: when index == 0 then start removing the wrong items
                        if(index == 0) {
                            root.hide();
                        }
                        root.close(path, tempFile);
                        listFiles.model.remove(index);
                    }
                }
            }

            Column {
                id: col
                
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.margins: 10
                
                Text {

                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.rightMargin: imgClose.width
                    
                    color: modified ? mainTextModifiedColor : mainTextColor
                    font.pixelSize: 18
                    font.bold: true
                    text: name
                    elide: Text.ElideRight
                    font.italic: modified
                }
                Text {

                    anchors.left: parent.left
                    anchors.right: parent.right
                    
                    color: item.current ? "#aaaaaa" : "#555555"
                    elide: Text.ElideLeft
                    text: path
                }
            }
            Row {

                anchors.right: parent.right
                anchors.top: col.bottom
                anchors.margins: 5
                
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

        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.top: inputArea.bottom
        anchors.margins: 5
        
        spacing: 2

        //focus: true
        model: ListModel {}
        delegate: tabDelegate
        highlightMoveDuration: 200
    }

    ListView {
        id: listFuzzyFiles

        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.top: fuzzyText.bottom
        anchors.margins: 5
        
        visible: !listFiles.visible
        spacing: 2

        //focus: true
        model: ListModel {}
        delegate: tabDelegate
        highlightMoveDuration: 200
    }
}
