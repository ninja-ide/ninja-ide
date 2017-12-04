import QtQuick 2.6
import QtQuick.Layouts 1.0

Rectangle {
    id: root
    color: theme.Base

    signal selected(string orientation)

    function signalForIndex(index) {
        if(index === 0) {
            selected("row");
        } else {
            selected("col");
        }
    }

    Component {
        id: col
        ColumnLayout {
            Rectangle {
                width: (root.width / 2) - 15
                height: (root.height / 2) - 10
                color: "#818181"
                opacity: 0.5
            }

            Rectangle {
                width: (root.width / 2) - 15
                height: (root.height / 2) - 10
                color: "#818181"
                opacity: 0.5
            }
        }
    }

    Component {
        id: row
        RowLayout {
            Rectangle {
                width: (300 / 4) - 10
                height: 150 - 15
                color: "#818181"
                opacity: 0.5
            }
            Rectangle {
                width: (300 / 4) - 10
                height: 150 - 15
                color: "#818181"
                opacity: 0.5
            }
        }
    }

    ListView {
        id: list
        anchors.fill: parent
        spacing: 0
        highlightMoveDuration: 150
        model: ListModel {
            ListElement { type: "row" }
            ListElement { type: "col" }
        }
        orientation: ListView.Horizontal
        delegate: Rectangle {
            width: 300 / 2
            height: parent.height
            color: "transparent"
            Loader {
                anchors.centerIn: parent
                sourceComponent: type == "col" ? col : row
            }

            Keys.onLeftPressed: {
                list.currentIndex = 0;
            }
            Keys.onRightPressed: {
                list.currentIndex = 1;
            }

            Keys.onReturnPressed: {
                signalForIndex(list.currentIndex);
            }
        }
        highlight: Rectangle { color: "#383e4a"}
        focus: true


    }
}

/*
Rectangle {
    id: root

    color: theme.LocatorBackground
    //opacity: 0.8
    //radius: 15
    //border.color: "#aae3ef"
    //border.width: 2

    signal selected(string orientation)

    function _signal_for_index(index) {
        if(index === 0) {
            root.selected("row");
        } else {
            root.selected("col");
        }
    }

    Component.onCompleted: {
        list.forceActiveFocus();
    }

    Component {
        id: row
        RowLayout {
            anchors.centerIn: parent
            spacing: 5
            Rectangle {
                width: 50
                height: 105
                color: "orange"
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
        ColumnLayout {
            anchors.centerIn: parent
            spacing: 5
            Rectangle {
                width: 100
                height: 50
                color: "lightblue"
                Text {
                    renderType: Text.NativeRendering
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
        highlight: Rectangle { color: "lightsteelblue" }

        //Keys.onEnterPressed: { root._signal_for_index(list.currentIndex); }
        //Keys.onReturnPressed: { root._signal_for_index(list.currentIndex); }

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
        anchors {
            right: parent.right
            top: parent.top
            margins: 5
        }
        color: "white"
        font.pointSize: 10
    }
}

*/
