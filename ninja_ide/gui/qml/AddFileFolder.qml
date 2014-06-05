import QtQuick 1.1

Rectangle {
    id: root
    color: "#202123"

    property bool fileDialog: true

    signal create(string path)

    function setDialogType(isFile) {
        fileDialog = isFile;
    }

    function setBasePath(path) {
        input.text = path;
    }

    function activateInput() {
        input.forceActiveFocus();
    }

    function cleanText() {
        input.text = "";
    }

    Text {
        id: headerText
        text: root.fileDialog ? "+ Enter the path for the new file" : "+ Enter the path for the new folder"
        color: "white"
        font.pixelSize: 14
        font.bold: true
        anchors {
            left: parent.left
            right: parent.right
            top: parent.top
            margins: 5
        }
    }

    Rectangle {
        id: inputArea
        radius: 2
        color: "#2d2f31"
        height: 30
        anchors {
            left: parent.left
            right: parent.right
            top: headerText.bottom
            margins: 5
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

            Keys.onEnterPressed: {
                root.create(input.text);
            }
            Keys.onReturnPressed: {
                root.create(input.text);
            }
        }
    }
}