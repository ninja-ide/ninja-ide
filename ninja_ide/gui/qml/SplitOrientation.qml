import QtQuick 2.5

Rectangle {
    id: root

    color: "black"
    opacity: 0.8
    radius: 15
    border.color: "#aae3ef"
    border.width: 2

    signal selected(string orientation)

    function _signal_for_index(index) {
        if(index == 0) {
            root.selected("row");
        } else {
            root.selected("col");
        }
    }

    Component {
        id: row
        Row {
            anchors.centerIn: parent
            spacing: 5
            Rectangle {
                width: 50
                height: 105
                color: "orange"
                radius: 5
                Column {
                    anchors.fill: parent
                    anchors.topMargin: 5
                    anchors.leftMargin: 2
                    spacing: 2
                    Text {
                        text: "class MyClass(object):"
                        color: "white"
                        font.bold: true
                        font.pixelSize: 9
                        width: parent.width
                        elide: Text.ElideRight
                    }
                    Text {
                        text: "  def __init__(self):"
                        color: "white"
                        font.bold: true
                        font.pixelSize: 9
                        width: parent.width
                        elide: Text.ElideRight
                    }
                }
            }
            Rectangle {
                width: 50
                height: 105
                color: "orange"
                radius: 5
                Column {
                    anchors.fill: parent
                    anchors.topMargin: 5
                    anchors.leftMargin: 2
                    spacing: 2
                    Text {
                        text: "def func():"
                        color: "white"
                        font.bold: true
                        font.pixelSize: 9
                        width: parent.width
                        elide: Text.ElideRight
                    }
                    Text {
                        text: "  print 'NINJA-IDE'"
                        color: "white"
                        font.bold: true
                        font.pixelSize: 9
                        width: parent.width
                        elide: Text.ElideRight
                    }
                }
            }
        }
    }

    Component {
        id: col
        Column {
            anchors.centerIn: parent
            spacing: 5
            Rectangle {
                width: 100
                height: 50
                color: "lightblue"
                radius: 5
                Text {
                    anchors.top: parent.top
                    anchors.left: parent.left
                    anchors.topMargin: 5
                    anchors.leftMargin: 2
                    text: "class MyClass(object):\n  def __init__(self):"
                    font.bold: true
                    color: "white"
                    font.pixelSize: 9
                    width: parent.width
                    elide: Text.ElideRight
                }
            }
            Rectangle {
                width: 100
                height: 50
                color: "lightblue"
                radius: 5
                Text {
                    anchors.top: parent.top
                    anchors.left: parent.left
                    anchors.topMargin: 5
                    anchors.leftMargin: 2
                    text: "def func():\n  print 'NINJA-IDE'"
                    color: "white"
                    font.bold: true
                    font.pixelSize: 9
                    width: parent.width
                    elide: Text.ElideRight
                }
            }
        }
    }

    ListView {
        id: list
        anchors.fill: parent
        anchors.margins: 20
        spacing: 10
        orientation: ListView.Horizontal
        highlight: Rectangle { color: "lightsteelblue"; radius: 5 }
        focus: true
        highlightMoveDuration: 150

        model: ListModel {
            ListElement { type: "row" }
            ListElement { type: "col" }
        }

        delegate: Rectangle {
            width: 120
            height: 120
            color: "transparent"
            Loader {
                anchors.centerIn: parent
                sourceComponent: type == "col" ? col : row
            }
        }

        Keys.onEnterPressed: { root._signal_for_index(list.currentIndex); }
        Keys.onReturnPressed: { root._signal_for_index(list.currentIndex); }

        MouseArea {
            anchors.fill: parent
            onClicked: {
                var index = list.indexAt(mouseX, mouseY);
                list.currentIndex = index;
                root._signal_for_index(index);
            }
        }
    }

    Text {
        text: "Esc to exit"
        
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.margins: 5
        
        color: "white"
        font.pointSize: 10
    }
}
