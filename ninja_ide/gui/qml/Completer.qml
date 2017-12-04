import QtQuick 2.7
import QtQuick.Layouts 1.1
import QtQuick.Controls 2.1

Rectangle {
    id: root
    color: theme.CompleterBackground
    property int itemHeight: 35  // Height of each item
    property int visibleItems: 6  // Number of items to be seen on the list
    signal insertCompletion;

    ListModel {
        id: itemsModel

        ListElement {
            type: ""
            item: ""
            itemColor: ""
        }
    }
    Component {
        id: delegate
        Rectangle {
            id: listItem
            anchors {
                left: parent.left
                right: parent.right
            }
            height: itemHeight
            property bool current: ListView.isCurrentItem
            color: listItem.current ? Qt.lighter(theme.CompleterCurrentItem, 0.9) : root.color

            MouseArea {
                anchors.fill: parent

                onClicked: {
                    proposalsList.currentIndex = index;
                }

                onDoubleClicked: {
                    insertCompletion();
                }
            }

            Item {
                anchors.fill: parent
                RowLayout {
                    spacing: 15
                    Rectangle {
                        anchors {
                            left: parent.left
                            right: item.left
                        }
                        height: itemHeight
                        width: 40  // Calculate this
                        color: itemColor ? itemColor : ""
                        Text {
                            id: completionType
                            anchors.centerIn: parent
                            anchors.leftMargin: 5
                            font.bold: true
                            font.pixelSize: 12
                            color: "white"
                            text: type
                        }

                    }
                    Text {
                        text: item
                        color: theme.CompleterText
                        renderType: Text.NativeRendering
                        font.pixelSize: 16
                        font.letterSpacing: 2
                        font.bold: true
                        //font.family: fontFamily  // Root context
                    }
                }
            }
        }
    }
    ListView {
        id: proposalsList
        anchors.fill: parent
        model: itemsModel
        delegate: delegate
        ScrollBar.vertical: ScrollBar {}
    }

    function addItem(type, name, itemColor) {
        itemsModel.append({"type": type, "item": name, "itemColor": itemColor});
    }

    function clear() {
        itemsModel.clear();
    }

    function nextItem() {
        var index = proposalsList.currentIndex;
        if (index == itemsModel.count - 1) {
            proposalsList.positionViewAtBeginning();
            proposalsList.currentIndex = 0
        } else {
            proposalsList.incrementCurrentIndex();
        }
    }

    function previousItem() {
        var index = proposalsList.currentIndex;
        if (index == 0) {
            proposalsList.positionViewAtEnd();
            proposalsList.currentIndex = itemsModel.count - 1;
        } else {
            proposalsList.decrementCurrentIndex();
        }
    }

    function currentItem() {
        return itemsModel.get(proposalsList.currentIndex).item;
    }

    function getHeight() {
        var hei = itemHeight * itemsModel.count;
        var height = visibleItems * itemHeight;
        if(hei < height)
            return hei;
        return height;
    }
}
