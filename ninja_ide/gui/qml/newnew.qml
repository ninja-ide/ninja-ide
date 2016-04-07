import QtQuick 2.5

ToggleButton {
    id: btnClose
    text: "Close"
    height: 20
    width: 50
    visible: true
    toggledEnagled: false
    anchors.right: parent.right
    anchors.top: parent.top
    anchors.margins: 10
    
    onClicked: {
        print("toClose...")
        root.close();
    }
}