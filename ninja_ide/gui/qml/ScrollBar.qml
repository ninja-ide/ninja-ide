/* Scrollbar for a flickable elements */

import QtQuick 2.5

Item {
    id: scrollBar

    property real position
    property real pageSize
    property int orientation : Qt.Vertical

    Rectangle {
        x: orientation == Qt.Vertical ? 1 : (scrollBar.position * (scrollBar.width-2) + 1)
        y: orientation == Qt.Vertical ? (scrollBar.position * (scrollBar.height-2) + 1) : 1
        width: orientation == Qt.Vertical ? (parent.width-2) : (scrollBar.pageSize * (scrollBar.width-2))
        height: orientation == Qt.Vertical ? (scrollBar.pageSize * (scrollBar.height-2)) : (parent.height-2)
        color: "gray"
        opacity: 0.7
    }
}
