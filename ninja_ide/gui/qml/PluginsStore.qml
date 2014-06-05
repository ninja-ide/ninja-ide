import QtQuick 1.1

Rectangle {
    id: root
    color: "#616161"

    signal showPluginDetails(int identifier)
    signal loadPluginsGrid
    signal loadTagsGrid
    signal loadAuthorGrid
    signal loadPluginsForCategory(string tag)
    signal search(string key)
    signal close
    property int currentDownloads: 0
    property int pluginsSelected: 0
    property int categoryCounter: 0

    ListModel {
        id: pluginsModel

        ListElement {
            identifier: 0
            shallow: true
            mname: ""
            mversion: ""
            mauthor: ""
            mauthorEmail: ""
            mhomePage: ""
            mlicense: ""
            mdescription: ""
            msummary: ""
            mdownloadUrl: ""
            mselected: false
            minstalled: false
        }

        function getPlugin(identifier) {
            for (var i = 0; i < pluginsModel.count; i++) {
                var plugin = pluginsModel.get(i)
                if (plugin.identifier == identifier) {
                    return plugin;
                    break;
                }
            }
        }
    }

    ListModel {
        id: categoryModel

        ListElement {
            mcolor: "white"
            name: ""
        }
    }

    function updateCategoryCounter(value) {
        root.categoryCounter = value;
    }

    function showGridPlugins() {
        pluginsModel.clear();
        gridCategories.opacity = 0;
        loadingArea.visible = false;
        btnName.visible = true;
        btnTags.visible = true;
        btnAuthor.visible = true;
        btnInstalled.visible = true;
        searchComponent.visible = true;
        gridPlugins.opacity = 1;
    }

    function showDetails(identifier) {
        details.clear();
        details.opacity = 1;
        loadingArea.visible = true;
        var plugin = pluginsModel.getPlugin(identifier);
        if (plugin && !plugin.shallow) {
            root.displayDetails(plugin.identifier);
        } else {
            root.showPluginDetails(identifier);
        }
    }

    function displayDetails(identifier) {
        var plugin = pluginsModel.getPlugin(identifier);
        if (plugin) {
            details.identifier = plugin.identifier;
            details.title = plugin.mname;
            details.author = plugin.mauthor;
            details.authorEmail = plugin.mauthorEmail;
            details.version = plugin.mversion;
            details.homePage = plugin.mhomePage;
            details.license = plugin.mlicense;
            details.summary = plugin.msummary;
            details.description = plugin.mdescription;
        }
        loadingArea.visible = false;
    }

    function addPlugin(identifier, name, summary, version) {
        pluginsModel.append({"identifier": identifier, "mname": name,
            "msummary": summary, "mversion": version,
            "mauthor": "", "mdownloadUrl": "", "mselected": false,
            "minstalled": false, "mauthorEmail": "", "mhomePage": "", "mlicense": "",
            "mdescription": "", "shallow": true});
    }

    function addCategory(color, name) {
        categoryModel.append({"mcolor": color, "name": name})
    }

    function showTagsGrid() {
        categoryModel.clear();
        gridPlugins.opacity = 0;
        gridCategories.opacity = 1;
        loadingArea.visible = true;
        root.loadTagsGrid();
    }

    function showAuthorGrid() {
        categoryModel.clear();
        gridPlugins.opacity = 0;
        gridCategories.opacity = 1;
        loadingArea.visible = true;
        root.loadAuthorGrid();
    }

    function loadingComplete() {
        loadingArea.visible = false;
    }

    function updatePlugin(identifier, author, authorEmail, description, downloadUrl, homePage, license) {
        var plugin = pluginsModel.getPlugin(identifier);
        if (plugin) {
            plugin.mauthor = author;
            plugin.mauthorEmail = authorEmail;
            plugin.mdescription = description;
            plugin.mdownloadUrl = downloadUrl;
            plugin.mhomePage = homePage;
            plugin.mlicense = license;
            plugin.shallow = false;
        }
    }

    Component.onCompleted: {
        pluginsModel.clear();
        categoryModel.clear();
    }

    Row {
        id: rowButtons
        anchors {
            left: parent.left
            top: parent.top
            leftMargin: 10
            topMargin: 10
        }
        spacing: 1

        property int buttonsPadding: 20

        ToggleButton {
            id: btnName
            text: "By Name"
            height: 20
            width: btnName.textWidth + rowButtons.buttonsPadding
            color: "#b8b8b8"
            toggled: true
            visible: false

            onClicked: {
                btnAuthor.toggled = false;
                btnTags.toggled = false;
                btnInstalled.toggled = false;
                btnSearch.visible = false;
                btnName.toggled = true;
                btnSelection.visible = false;
                root.loadPluginsGrid();
            }
        }
        ToggleButton {
            id: btnTags
            text: "By Tags"
            height: 20
            width: btnName.textWidth + rowButtons.buttonsPadding
            visible: false

            onClicked: {
                btnName.toggled = false;
                btnAuthor.toggled = false;
                btnInstalled.toggled = false;
                btnSearch.visible = false;
                btnTags.toggled = true;
                btnSelection.visible = false;
                root.showTagsGrid();
            }
        }
        ToggleButton {
            id: btnAuthor
            text: "By Author"
            height: 20
            width: btnName.textWidth + rowButtons.buttonsPadding
            visible: false

            onClicked: {
                btnName.toggled = false;
                btnTags.toggled = false;
                btnInstalled.toggled = false;
                btnSearch.visible = false;
                btnAuthor.toggled = true;
                btnSelection.visible = false;
                root.showAuthorGrid();
            }
        }
        ToggleButton {
            id: btnInstalled
            text: "Installed"
            height: 20
            width: btnName.textWidth + rowButtons.buttonsPadding
            visible: false

            onClicked: {
                btnName.toggled = false;
                btnTags.toggled = false;
                btnAuthor.toggled = false;
                btnSearch.visible = false;
                btnSelection.visible = false;
                btnInstalled.toggled = true;
            }
        }
        ToggleButton {
            id: btnSearch
            text: "Search"
            height: 20
            width: btnName.textWidth + rowButtons.buttonsPadding
            toggled: true
            visible: false

            onVisibleChanged: {
                if (btnSearch.visible) {
                    btnName.toggled = false;
                    btnTags.toggled = false;
                    btnAuthor.toggled = false;
                    btnInstalled.toggled = false;
                    btnSelection.visible = false;
                }
            }
        }
    }

    ToggleButton {
            id: btnSelection
            text: "Selection"
            height: 20
            width: 354
            color: "#b8b8b8"
            toggled: true
            visible: false
            anchors {
                left: rowButtons.left
                top: rowButtons.bottom
                topMargin: 3
            }

            onVisibleChanged: {
                if (btnSelection.visible) {
                    btnName.toggled = false;
                    btnTags.toggled = false;
                    btnAuthor.toggled = false;
                    btnInstalled.toggled = false;
                }
            }
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
            right: btnClose.left
            top: parent.top
            margins: 10
        }

        TextInput {
            id: textInput
            color: "gray"
            smooth: true
            anchors.fill: parent
            anchors.margins: 2
            anchors.rightMargin: 20

            onAccepted: {
                pluginsModel.clear();
                loadingArea.visible = true;
                gridCategories.opacity = 0;
                gridPlugins.opacity = 1;
                btnSearch.visible = true;
                root.search(textInput.text);
            }
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

    ToggleButton {
        id: btnClose
        text: "Close"
        height: 20
        width: 50
        visible: true
        toggledEnagled: false
        anchors {
            right: parent.right
            top: parent.top
            margins: 10
        }

        onClicked: {
            root.close();
        }
    }

    GridView {
        id: gridPlugins
        cellWidth: 190
        cellHeight: 150
        clip: true
        opacity: 0

        anchors {
            left: parent.left
            right: parent.right
            bottom: bottomBar.visible ? bottomBar.top : parent.bottom
            top: btnSelection.visible ? btnSelection.bottom : searchComponent.bottom
            margins: (root.width - parseInt(root.width / gridPlugins.cellWidth) * gridPlugins.cellWidth) / 2
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
                root.showDetails(identifier);
            }

/*
            onDownloadFinished: {
                pluginsModel.remove(index);
            }
*/

            onSelection: {
                pluginsModel.setProperty(index, "mselected", value);
                if (value) {
                    root.pluginsSelected += 1;
                } else {
                    root.pluginsSelected -= 1;
                }
            }
        }

        Behavior on opacity {PropertyAnimation{duration: 300}}
    }

    GridView {
        id: gridCategories
        cellWidth: 190
        cellHeight: 70
        clip: true
        opacity: 0

        anchors {
            left: parent.left
            right: parent.right
            bottom: bottomBar.visible ? bottomBar.top : parent.bottom
            top: btnSelection.visible ? btnSelection.bottom : searchComponent.bottom
            margins: (root.width - parseInt(root.width / gridCategories.cellWidth) * gridCategories.cellWidth) / 2
        }

        model: categoryModel

        delegate: Rectangle {
            width: 180
            height: 60
            radius: 10
            smooth: true
            color: mcolor

            Text {
                text: name
                color: "black"
                font.pixelSize: 14
                anchors.fill: parent
                wrapMode: Text.WordWrap
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }

            MouseArea {
                anchors.fill: parent
                hoverEnabled: true
                onClicked: {
                    btnSelection.text = name;
                    btnSelection.visible = true;
                    root.loadPluginsForCategory(name);
                }

                onEntered:{
                    parent.color = "white";
                }

                onCanceled:{
                    parent.color = mcolor;
                }

                onExited: {
                    parent.color = mcolor;
                }
            }
        }

        Behavior on opacity {PropertyAnimation{duration: 300}}
    }

    PluginDetails {
        id: details
        anchors.fill: gridPlugins
        opacity: 0

        Behavior on opacity { PropertyAnimation { duration: 300 } }

        onClose: {
            details.opacity = 0;
        }
    }

    Rectangle {
        id: loadingArea
        anchors.fill: parent
        color: "transparent"
        Image {
            id: imgLoading
            source: "img/spinner.png"
            anchors.centerIn: parent
            height: 80
            width: 80
            smooth: true
            visible: loadingArea.visible

            Timer {
                interval: 100
                running: imgLoading.visible
                repeat: true
                onTriggered: imgLoading.rotation = imgLoading.rotation + 20
            }
        }

        Text {
            id: textLoading
            text: root.categoryCounter > 0 ? root.categoryCounter : "Loading"
            font.pixelSize: 15
            color: "white"
            anchors.centerIn: imgLoading
            visible: imgLoading.visible
        }

        MouseArea {
            anchors.fill: parent
        }
    }

    Rectangle {
        id: bottomBar
        color: "white"
        border.color: "gray"
        border.width: 1
        height: 45
        visible: (root.currentDownloads > 0 || root.pluginsSelected > 0) ? true : false
        anchors {
            left: parent.left
            right: parent.right
            bottom: parent.bottom
        }
        Text {
            id: txtInstalling
            text: "Installing..."
            color: "black"
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.leftMargin: 10
            verticalAlignment: Text.AlignVCenter
            visible: imgSpinner.visible
        }

        Image {
            id: imgSpinner
            source: "img/spinner.png"
            height: 30
            width: 30
            anchors.centerIn: parent
            visible: root.currentDownloads > 0 ? true : false
            smooth: true

            Timer {
                interval: 100
                running: imgSpinner.visible
                repeat: true
                onTriggered: imgSpinner.rotation = imgSpinner.rotation + 20
            }
        }

        Text {
            id: textDownloads
            text: root.currentDownloads
            color: "black"
            anchors.centerIn: imgSpinner
            visible: imgSpinner.visible
        }

        ToggleButton {
            id: btnInstallSelected
            text: "Install Selected"
            height: 20
            width: 110
            color: "#b8b8b8"
            visible: root.pluginsSelected > 0 ? true : false
            anchors {
                right: parent.right
                bottom: parent.bottom
                margins: 10
            }

            onClicked: {
                //call func
            }
        }
    }
}