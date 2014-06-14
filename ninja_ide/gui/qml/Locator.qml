import QtQuick 1.1

Rectangle {
    id: root
    width: 500
    height: 400
    color: "#202123"

    property string filterVerbose: "<font color='#8f8f8f'>@Filename &lt;Class &gt;Function -Attribute .Current /Opened :Line !NoPython</font>"
    property string filterComposite: ""

    signal textChanged(string text)
    signal open(string path, int lineno)
    signal fetchMore

    function activateInput() {
        input.forceActiveFocus();
    }

    function setFilterComposite(filter) {
        root.filterComposite = filter;
    }

    function loadItem(type, name, lineno, path, color) {
        itemsModel.append({"type": type, "name": name, "lineno": lineno,
                           "path": path, "colorType": color});
    }

    function clear() {
        itemsModel.clear();
    }

    function cleanText() {
        input.text = "";
    }

    function currentItem() {
        if (listResults.currentIndex > -1) {
            var item = itemsModel.get(listResults.currentIndex);
            return [item.type, item.name, item.path, item.lineno];
        }
    }

    function openCurrent() {
        if (listResults.currentIndex > -1) {
            var item = itemsModel.get(listResults.currentIndex);
            root.open(item.path, item.lineno);
        }
    }

    ListModel {
        id: itemsModel
        ListElement {
            type: ""
            name: ""
            lineno: ""
            path: ""
            colorType: ""
        }
    }

    Component.onCompleted: {
        itemsModel.clear();
    }

    Column {
        id: filtersCol
        anchors {
            right: parent.right
            top: flipableArea.top
            bottom: parent.bottom
            margins: 10
        }
        width: 10
        spacing: 10

        Text {
            text: "@"
            color: "white"
            font.pixelSize: 16
            font.bold: true
            horizontalAlignment: Text.AlignHCenter
            anchors {
                left: parent.left
                right: parent.right
            }
            MouseArea {
                anchors.fill: parent
                onClicked: {
                    input.text += parent.text;
                }
            }
        }
        Text {
            text: "<"
            color: "#18ff6a"
            font.pixelSize: 16
            font.bold: true
            horizontalAlignment: Text.AlignHCenter
            anchors {
                left: parent.left
                right: parent.right
            }
            MouseArea {
                anchors.fill: parent
                onClicked: {
                    input.text += parent.text;
                }
            }
        }
        Text {
            text: ">"
            color: "red"
            font.pixelSize: 16
            font.bold: true
            horizontalAlignment: Text.AlignHCenter
            anchors {
                left: parent.left
                right: parent.right
            }
            MouseArea {
                anchors.fill: parent
                onClicked: {
                    input.text += parent.text;
                }
            }
        }
        Text {
            text: "-"
            color: "#18e1ff"
            font.pixelSize: 16
            font.bold: true
            horizontalAlignment: Text.AlignHCenter
            anchors {
                left: parent.left
                right: parent.right
            }
            MouseArea {
                anchors.fill: parent
                onClicked: {
                    input.text += parent.text;
                }
            }
        }
        Text {
            text: "."
            color: "#f118ff"
            font.pixelSize: 16
            font.bold: true
            horizontalAlignment: Text.AlignHCenter
            anchors {
                left: parent.left
                right: parent.right
            }
            MouseArea {
                anchors.fill: parent
                onClicked: {
                    input.text += parent.text;
                }
            }
        }
        Text {
            text: "/"
            color: "#fff118"
            font.pixelSize: 16
            font.bold: true
            horizontalAlignment: Text.AlignHCenter
            anchors {
                left: parent.left
                right: parent.right
            }
            MouseArea {
                anchors.fill: parent
                onClicked: {
                    input.text += parent.text;
                }
            }
        }
        Text {
            text: ":"
            color: "#18ffd6"
            font.pixelSize: 16
            font.bold: true
            horizontalAlignment: Text.AlignHCenter
            anchors {
                left: parent.left
                right: parent.right
            }
            MouseArea {
                anchors.fill: parent
                onClicked: {
                    input.text += parent.text;
                }
            }
        }
        Text {
            text: "!"
            color: "#ffa018"
            font.pixelSize: 16
            font.bold: true
            horizontalAlignment: Text.AlignHCenter
            anchors {
                left: parent.left
                right: parent.right
            }
            MouseArea {
                anchors.fill: parent
                onClicked: {
                    input.text += parent.text;
                }
            }
        }
    }

    Rectangle {
        id: inputArea
        radius: 2
        color: "#2d2f31"
        height: 30
        anchors {
            left: parent.left
            right: filtersCol.left
            top: parent.top
            margins: 10
        }
        border.color: "black"
        border.width: 1
        smooth: true

        TextInput {
            id: input
            anchors {
                fill: parent
                margins: 4
            }
            focus: true
            clip: true
            color: "white"
            font.pixelSize: 18

            onTextChanged: {
                root.textChanged(input.text);
            }

            Keys.onDownPressed: {
                listResults.incrementCurrentIndex();
                if (listResults.currentIndex == (listResults.count - 2)) {
                    root.fetchMore();
                }
            }
            Keys.onUpPressed: {
                listResults.decrementCurrentIndex();
            }
            Keys.onEnterPressed: {
                root.openCurrent();
            }
            Keys.onReturnPressed: {
                root.openCurrent();
            }
        }
    }

    Flipable {
        id: flipableArea
        anchors {
            left: parent.left
            right: filtersCol.left
            bottom: filtersText.top
            top: inputArea.bottom
            margins: 10
            bottomMargin: 5
        }

        property bool flipped: false

        transform: Rotation {
            id: rotation
            origin.x: flipableArea.width/2
            origin.y: flipableArea.height/2
            axis.x: 0; axis.y: 1; axis.z: 0     // set axis.y to 1 to rotate around y-axis
            angle: 0    // the default angle
        }

        states: State {
            name: "back"
            PropertyChanges { target: rotation; angle: 180 }
            when: flipableArea.flipped
        }

        transitions: Transition {
            NumberAnimation { target: rotation; property: "angle"; duration: 700 }
        }

        front: ListView {
            id: listResults
            anchors.fill: parent
            clip: true
            spacing: 2
            model: itemsModel
            delegate: Rectangle {
                id: listItem
                anchors {
                    left: parent.left
                    right: parent.right
                }
                height: 70
                property bool current: ListView.isCurrentItem
                color: listItem.current ? "#4182c4" : "#27292b"

                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        listResults.currentIndex = index;
                        root.openCurrent();
                    }
                }

                Item {
                    anchors.fill: parent

                    Text {
                        id: fileType
                        anchors {
                            left: parent.left
                            right: colFileInfo.left
                            top: parent.top
                            bottom: parent.bottom
                        }
                        text: "<font color='" + colorType + "'>" + type + "</font>"
                        font.bold: true
                        font.pixelSize: 30
                        verticalAlignment: Text.AlignVCenter
                        horizontalAlignment: Text.AlignHCenter
                    }

                    Column {
                        id: colFileInfo
                        anchors {
                            fill: parent
                            topMargin: 15
                            leftMargin: 45
                            rightMargin: 10
                        }
                        spacing: 10

                        Item {
                            anchors {
                                left: parent.left
                                right: parent.right
                            }
                            height: filenameText.height

                            Text {
                                id: filenameText
                                anchors {
                                    left: parent.left
                                    right: lineText.left
                                    rightMargin: 5
                                }
                                text: name
                                color: listItem.current ? "white" : "#aaaaaa"
                                font.pixelSize: 13
                                font.bold: true
                                elide: Text.ElideRight
                            }
                            Text {
                                id: lineText
                                anchors {
                                    right: parent.right
                                }
                                text: "[Line: " + (lineno + 1) + "]"
                                visible: lineno > -1 ? true : false
                                color: listItem.current ? "#aaaaaa" : "#555555"
                                font.pixelSize: 10
                                font.bold: true
                            }
                        }
                        Text {
                            id: pathText
                            anchors {
                                left: parent.left
                                right: parent.right
                            }
                            text: path
                            color: listItem.current ? "#aaaaaa" : "#555555"
                            font.bold: true
                            elide: Text.ElideLeft
                        }
                    }
                }
            }
        }

        back: Flickable {
            anchors.fill: parent
            clip: true
            contentHeight: colHelp.childrenRect.height

            Column {
                id: colHelp
                anchors {
                    left: parent.left
                    right: parent.right
                }
                spacing: 10
                Text {
                    text: "The Code Locator provides you an easy way to access any file, class, function, attribute with a few keystrokes."
                    font.pixelSize: 14
                    anchors {
                        left: parent.left
                        right: parent.right
                    }
                    color: "white"
                    wrapMode: Text.WordWrap
                }
                Text {
                    text: "You can just enter your search and you will see the results being filtered. You can search for any part of the word, for example:"
                    font.pixelSize: 14
                    anchors {
                        left: parent.left
                        right: parent.right
                    }
                    color: "white"
                    wrapMode: Text.WordWrap
                }
                Text {
                    text: "If you want to obtain: EDITOR\nSearching for: ITO\nIs a valid search and it will contain EDITOR among the possible results."
                    font.pixelSize: 14
                    anchors {
                        left: parent.left
                        right: parent.right
                    }
                    color: "white"
                    wrapMode: Text.WordWrap
                }
                Text {
                    text: "You can also use any of the filters to specialize your query and even combine them to specialize it even more."
                    font.pixelSize: 14
                    anchors {
                        left: parent.left
                        right: parent.right
                    }
                    color: "white"
                    wrapMode: Text.WordWrap
                }
                Text {
                    text: "@ Python Files"
                    color: "white"
                    font.pixelSize: 16
                    font.bold: true
                    horizontalAlignment: Text.AlignHCenter
                    anchors {
                        left: parent.left
                        right: parent.right
                    }
                }
                Text {
                    text: "< Classes"
                    color: "#18ff6a"
                    font.pixelSize: 16
                    font.bold: true
                    horizontalAlignment: Text.AlignHCenter
                    anchors {
                        left: parent.left
                        right: parent.right
                    }
                }
                Text {
                    text: "> Functions"
                    color: "red"
                    font.pixelSize: 16
                    font.bold: true
                    horizontalAlignment: Text.AlignHCenter
                    anchors {
                        left: parent.left
                        right: parent.right
                    }
                }
                Text {
                    text: "- Attributes"
                    color: "#18e1ff"
                    font.pixelSize: 16
                    font.bold: true
                    horizontalAlignment: Text.AlignHCenter
                    anchors {
                        left: parent.left
                        right: parent.right
                    }
                }
                Text {
                    text: ". Current File"
                    color: "#f118ff"
                    font.pixelSize: 16
                    font.bold: true
                    horizontalAlignment: Text.AlignHCenter
                    anchors {
                        left: parent.left
                        right: parent.right
                    }
                }
                Text {
                    text: "/ Opened Files"
                    color: "#fff118"
                    font.pixelSize: 16
                    font.bold: true
                    horizontalAlignment: Text.AlignHCenter
                    anchors {
                        left: parent.left
                        right: parent.right
                    }
                }
                Text {
                    text: ": Line number"
                    color: "#18ffd6"
                    font.pixelSize: 16
                    font.bold: true
                    horizontalAlignment: Text.AlignHCenter
                    anchors {
                        left: parent.left
                        right: parent.right
                    }
                }
                Text {
                    text: "! Non Python Files"
                    color: "#ffa018"
                    font.pixelSize: 16
                    font.bold: true
                    horizontalAlignment: Text.AlignHCenter
                    anchors {
                        left: parent.left
                        right: parent.right
                    }
                }
                Text {
                    text: "Combining them:"
                    font.pixelSize: 14
                    anchors {
                        left: parent.left
                        right: parent.right
                    }
                    font.bold: true
                    color: "white"
                    wrapMode: Text.WordWrap
                }
                Text {
                    text: "Search for files containing \"edi\" in the name, check out the classes of the current result, and check out the Functions that contains the word \"key\" in the name for the selected Class."
                    font.pixelSize: 14
                    anchors {
                        left: parent.left
                        right: parent.right
                    }
                    color: "white"
                    wrapMode: Text.WordWrap
                }
                Image {
                    anchors {
                        left: parent.left
                        right: parent.right
                    }
                    source: "qrc:/help/locator"
                    fillMode: Image.PreserveAspectFit
                }
                Text {
                    text: "When you combine the filters, for example, to list the classes of an specific file, the second filter will take as input the current selected element in the results list.\nCheck out at the bottom of the screen which filters are being used, they will be highlighted."
                    font.pixelSize: 14
                    anchors {
                        left: parent.left
                        right: parent.right
                    }
                    color: "white"
                    wrapMode: Text.WordWrap
                }
            }
        }
    }

    Text {
        id: filtersText
        text: "Filters: "
        color: "#8f8f8f"
        font.pixelSize: 10
        font.bold: true
        anchors {
            left: parent.left
            bottom: parent.bottom
            margins: 5
        }
    }
    Text {
        id: filtersExplainedText
        text: root.filterComposite ? root.filterComposite : root.filterVerbose
        color: "white"
        font.pixelSize: 10
        font.bold: true
        anchors {
            left: parent.left
            right: parent.right
            bottom: parent.bottom
            margins: 5
        }
        horizontalAlignment: Text.AlignHCenter
    }

    Rectangle {
        id: help
        anchors {
            right: parent.right
            bottom: parent.bottom
            margins: 5
            rightMargin: 5
        }
        width: 20
        height: 20
        radius: width / 2
        color: "transparent"
        border.width: 1
        border.color: "white"
        smooth: true

        Text {
            text: "?"
            color: "white"
            font.pixelSize: 12
            font.bold: true
            anchors.centerIn: help
        }

        MouseArea {
            anchors.fill: parent
            onClicked: flipableArea.flipped = !flipableArea.flipped
        }
    }
}