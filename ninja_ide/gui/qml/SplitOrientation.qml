import QtQuick 2.6
import QtQuick.Layouts 1.0

Rectangle {
    id: root
    color: theme.SplitAssistantBackground
    radius: 3
    opacity: 0.9
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
        Column {
            spacing: 5
            Rectangle {
                width: 100
                height: 50
                color: "lightblue"
                radius: 3

                Text {
                    anchors.centerIn: parent
                    text: "class MyClass(object):\n  def __init__(self):"
                    font.bold: true
                    color: theme.SplitAssistantText
                    font.pixelSize: 7
                }
            }
            Rectangle {
                width: 100
                height: 50
                color: "lightblue"
                radius: 3
                Text {
                    anchors.centerIn: parent
                    text: "def func():\n  print('NINJA-IDE')"
                    color: theme.SplitAssistantText
                    font.bold: true
                    font.pixelSize: 7
                }
            }
        }
    }

    Component {
        id: row
        Row {
            spacing: 5
            anchors.centerIn: parent
            Rectangle {
                width: 50; height: 105
                color: "orange"
                radius: 3
                Text {
                    anchors.centerIn: parent
                    text: ("def func():
    pass")
                    color: theme.SplitAssistantText
                    font.bold: true
                    font.pixelSize: 7
                }
            }
            Rectangle {
                width: 50
                height: 105
                color: "orange"
                radius: 3
                Text {
                    anchors.centerIn: parent
                    text: ("def func():
    pass")
                    color: theme.SplitAssistantText
                    font.bold: true
                    font.pixelSize: 7
                }

            }
        }
    }

    ListView {
        id: list
        anchors.fill: parent
        spacing: 10
        anchors.margins: 20
        highlightMoveDuration: 150
        model: ListModel {
            ListElement { type: "row" }
            ListElement { type: "col" }
        }
        orientation: ListView.Horizontal
        delegate: Rectangle {
            width: 120
            height: 120
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
        highlight: Rectangle { color: theme.SplitAssistantHighlight; radius: 3 }
        focus: true


    }
    Text {
        text: "Esc to exit"
        anchors {
            right: parent.right
            top: parent.top
            rightMargin: 10
            topMargin: 3
        }
        color: theme.SplitAssistantText
        font.pointSize: 8
    }
}
