import QtQuick 1.1

Rectangle {
    id: root
    width: 500
    height: 400
    color: "#202123"

    property string filterVerbose: "<font color='#8f8f8f'>@Filename &lt;Classes &gt;Methods -Attribute .Current /Opened :Lines !NoPython</font>"

    signal textChanged(string text)

    function activateInput() {
        input.forceActiveFocus();
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
            style: Text.Raised
            styleColor: "black"
            font.bold: true
            horizontalAlignment: Text.AlignHCenter
            anchors {
                left: parent.left
                right: parent.right
            }
        }
        Text {
            text: "<"
            color: "#18ff6a"
            font.pixelSize: 16
            style: Text.Raised
            styleColor: "black"
            font.bold: true
            horizontalAlignment: Text.AlignHCenter
            anchors {
                left: parent.left
                right: parent.right
            }
        }
        Text {
            text: ">"
            color: "red"
            font.pixelSize: 16
            style: Text.Raised
            styleColor: "black"
            font.bold: true
            horizontalAlignment: Text.AlignHCenter
            anchors {
                left: parent.left
                right: parent.right
            }
        }
        Text {
            text: "-"
            color: "#18e1ff"
            font.pixelSize: 16
            style: Text.Raised
            styleColor: "black"
            font.bold: true
            horizontalAlignment: Text.AlignHCenter
            anchors {
                left: parent.left
                right: parent.right
            }
        }
        Text {
            text: "."
            color: "#f118ff"
            font.pixelSize: 16
            style: Text.Raised
            styleColor: "black"
            font.bold: true
            horizontalAlignment: Text.AlignHCenter
            anchors {
                left: parent.left
                right: parent.right
            }
        }
        Text {
            text: "/"
            color: "#fff118"
            font.pixelSize: 16
            style: Text.Raised
            styleColor: "black"
            font.bold: true
            horizontalAlignment: Text.AlignHCenter
            anchors {
                left: parent.left
                right: parent.right
            }
        }
        Text {
            text: ":"
            color: "#18ffd6"
            font.pixelSize: 16
            style: Text.Raised
            styleColor: "black"
            font.bold: true
            horizontalAlignment: Text.AlignHCenter
            anchors {
                left: parent.left
                right: parent.right
            }
        }
        Text {
            text: "!"
            color: "#ffa018"
            font.pixelSize: 16
            style: Text.Raised
            styleColor: "black"
            font.bold: true
            horizontalAlignment: Text.AlignHCenter
            anchors {
                left: parent.left
                right: parent.right
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
            }
            Keys.onUpPressed: {
                listResults.decrementCurrentIndex();
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
                        smooth: true
                        style: Text.Raised
                        styleColor: "black"
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
                                    right: lineText.right
                                }
                                text: name
                                color: listItem.current ? "white" : "#aaaaaa"
                                font.pixelSize: 13
                                font.bold: true
                                smooth: true
                                style: Text.Raised
                                styleColor: "black"
                                elide: Text.ElideLeft
                            }
                            Text {
                                id: lineText
                                anchors {
                                    right: parent.right
                                }
                                text: "[Line: " + lineno + "]"
                                visible: lineno > -1 ? true : false
                                color: listItem.current ? "#aaaaaa" : "#555555"
                                font.pixelSize: 10
                                font.bold: true
                                smooth: true
                                style: Text.Raised
                                styleColor: "black"
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
                            font.pixelSize: 12
                            smooth: true
                            style: Text.Raised
                            styleColor: "black"
                            elide: Text.ElideLeft
                        }
                    }
                }
            }
        }

        back: Flickable {
            anchors.fill: parent

            Column {
                anchors.fill: parent
                spacing: 20
                Text {
                    anchors {
                        left: parent.left
                        right: parent.left
                    }
                    text: "<font color='#18e1ff'>@</font>"
                    font.bold: true
                    font.pixelSize: 30
                    smooth: true
                    style: Text.Raised
                    styleColor: "black"
                }

                Text {
                    anchors {
                        left: parent.left
                        right: parent.left
                    }
                    text: "<font color='#18e1ff'>@</font>"
                    font.bold: true
                    font.pixelSize: 30
                    smooth: true
                    style: Text.Raised
                    styleColor: "black"
                }

                Text {
                    anchors {
                        left: parent.left
                        right: parent.left
                    }
                    text: "<font color='#18e1ff'>@</font>"
                    font.bold: true
                    font.pixelSize: 30
                    smooth: true
                    style: Text.Raised
                    styleColor: "black"
                }
            }
        }
    }

    Text {
        id: filtersText
        text: "Filters: "
        color: "#8f8f8f"
        font.pixelSize: 10
        style: Text.Raised
        styleColor: "black"
        font.bold: true
        anchors {
            left: parent.left
            bottom: parent.bottom
            margins: 5
        }
    }
    Text {
        id: filtersExplainedText
        text: root.filterVerbose
        color: "white"
        font.pixelSize: 10
        style: Text.Raised
        styleColor: "black"
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