import QtQuick 2.5

Rectangle {
    id: root
    color: theme.FileFolderBackground
    height: 80

    property bool fileDialog: true
    signal create(string path)

    Column {
        id: col
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10
        Text {
            id: headerText
            text: root.fileDialog ? qsTr("+ Enter the path for the new file") :
                                    qsTr("+ Enter the path for the new folder")
            color: theme.FileFolderText
            font.bold: true
        }
        Rectangle {
            id: inputArea
            color: theme.FileFolderLineEdit
            height: 30
            border.width: 2
            border.color: theme.RectangleBorder
            width: parent.width

            TextInput {
                color: theme.FileFolderText
                anchors {
                    fill: parent
                    margins: 5
                }

                id: input
                focus: true
                clip: true

                Keys.onEnterPressed: {
                    root.create(input.text);
                }

                Keys.onReturnPressed: {
                    root.create(input.text);
                }
            }
        }
    }

    function setBasePath(path) {
        input.text = path;
    }

    function setDialogType(isFile) {
        fileDialog = isFile;
    }
}
