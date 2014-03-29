import QtQuick 1.1

Rectangle {
    id: root
    color: "#616161"

    signal inflatePlugin(int identifier)
    property int currentDownloads: 0

    ListModel {
        id: pluginsModel

        ListElement {
            identifier: 0
            mname: ""
            mversion: ""
            mauthor: ""
            msummary: ""
            mdownloads: ""
            mdownload_url: ""
            mselected: false
            minstalled: false
        }
    }

    function showGrid() {
        imgLoading.visible = false;
        btnName.visible = true;
        btnTags.visible = true;
        btnAuthor.visible = true;
        btnInstalled.visible = true;
        searchComponent.visible = true;
        grid.visible = true;
    }

    function addPlugin(identifier, name, summary, version) {
        pluginsModel.append({"identifier": identifier, "mname": name,
            "msummary": summary, "mversion": version,
            "mauthor": "", "mdownloads": 0, "mdownload_url": "", "mselected": false,
            "minstalled": false});
    }

    function updatePlugin(identifier, author) {
        for (var i = 0; i < pluginsModel.count; i++) {
            var plugin = pluginsModel.get(i)
            if (plugin.identifier == identifier) {
                plugin.mauthor = author;
                break;
            }
        }
    }

    Component.onCompleted: {
        pluginsModel.clear();
    }

    Row {
        anchors {
            left: parent.left
            top: parent.top
            leftMargin: 10
            topMargin: 10
        }
        spacing: 1

        ToggleButton {
            id: btnName
            text: "By Name"
            height: 20
            width: 70
            color: "#b8b8b8"
            toggled: true
            visible: false

            onClicked: {
                btnAuthor.toggled = false;
                btnTags.toggled = false;
                btnInstalled.toggled = false;
                btnName.toggled = true;
            }
        }
        ToggleButton {
            id: btnTags
            text: "By Tags"
            height: 20
            width: 70
            visible: false

            onClicked: {
                btnName.toggled = false;
                btnAuthor.toggled = false;
                btnInstalled.toggled = false;
                btnTags.toggled = true;
            }
        }
        ToggleButton {
            id: btnAuthor
            text: "By Author"
            height: 20
            width: 70
            visible: false

            onClicked: {
                btnName.toggled = false;
                btnTags.toggled = false;
                btnInstalled.toggled = false;
                btnAuthor.toggled = true;
            }
        }
        ToggleButton {
            id: btnInstalled
            text: "Installed"
            height: 20
            width: 70
            visible: false

            onClicked: {
                btnName.toggled = false;
                btnTags.toggled = false;
                btnAuthor.toggled = false;
                btnInstalled.toggled = true;
            }
        }
    }

    Image {
        id: img
        source: "img/spinner.png"
        anchors.top: parent.top
        anchors.topMargin: 5
        anchors.horizontalCenter: parent.horizontalCenter
        height: 30
        width: 30
        visible: root.currentDownloads > 0 ? true : false
        smooth: true

        Timer {
            interval: 100
            running: img.visible
            repeat: true
            onTriggered: img.rotation = img.rotation + 20
        }
    }

    Text {
        id: textDownloads
        text: root.currentDownloads
        color: "white"
        anchors.centerIn: img
        visible: img.visible
    }

    Rectangle {
        id: searchComponent
        height: 20
        width: 250
        color: "white"
        radius: 5
        smooth: true
        visible: false
        anchors {
            right: parent.right
            top: parent.top
            margins: 10
        }

        TextInput {
            id: text
            color: "gray"
            smooth: true
            anchors.fill: parent
            anchors.margins: 2
            anchors.rightMargin: 20
        }

        Image {
            source: "img/find.png"
            width: 10
            height: 10
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.margins: 5
        }
    }

    GridView {
        id: grid
        cellWidth: 190
        cellHeight: 150
        clip: true
        visible: false

        anchors {
            left: parent.left
            right: parent.right
            bottom: parent.bottom
            top: img.bottom
            margins: (root.width - parseInt(root.width / grid.cellWidth) * grid.cellWidth) / 2
        }

        model: pluginsModel

        delegate: PluginComponent {
            width: 180
            height: 140
            title: mname
            version: mversion
            summary: msummary
            selected: mselected

            onShowPlugin: {
                root.inflatePlugin(identifier);
            }

            onDownloadFinished: {
                pluginsModel.remove(index);
            }

            onSelection: {
                pluginsModel.setProperty(index, "mselected", value);
            }
        }
    }

    Item {
        anchors.fill: parent
        Image {
            id: imgLoading
            source: "img/spinner.png"
            anchors.centerIn: parent
            height: 80
            width: 80
            smooth: true

            Timer {
                interval: 100
                running: imgLoading.visible
                repeat: true
                onTriggered: imgLoading.rotation = imgLoading.rotation + 20
            }
        }

        Text {
            id: textLoading
            text: "Loading"
            font.pixelSize: 15
            color: "white"
            anchors.centerIn: imgLoading
            visible: imgLoading.visible
        }
    }
}