import QtQuick 2.6
import QtQuick.Layouts 1.1


Rectangle {
    id: root
    opacity: 0
    color: "#434343"

    function start() {
        animation.start();
    }

    NumberAnimation { id: animation; target: root; property: "opacity"; to: 1; duration: 200 }

    GridView {
        id: view
        anchors.fill: parent
        anchors.margins: 20
        clip: true
        model: ListModel {}
        interactive: true
        cellWidth: 900; cellHeight: 500
        highlight: Rectangle { color: "blue" }
        focus: true
        delegate: Item {
            width: 300; height: 200
            Image {
                id: preview
                anchors.fill: parent
                fillMode: Image.PreserveAspectFit
                source: Qt.resolvedUrl(image_path)
                smooth: true
            }
            Keys.onRightPressed: {
                view.moveCurrentIndexRight();
            }
            Keys.onLeftPressed: {
                view.moveCurrentIndexLeft();
            }
        }
        highlightMoveDuration: 120
    }


    function add_widget(path) {
        view.model.append({"image_path": path});
    }
}
