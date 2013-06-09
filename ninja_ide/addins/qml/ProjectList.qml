import QtQuick 1.1

Rectangle {
    id: root

    property alias _projects: listProjects

    signal markAsFavorite(string path, bool value)
    signal openProject(string path)
    signal removeProject(string path)

    Component {
    id: contactDelegate
        Item {
            id: item
            width: root.width; height: 50
            property string _name: name
            property string _path: path

            ListView.onRemove: SequentialAnimation {
                PropertyAction { target: item; property: "ListView.delayRemove"; value: true }
                NumberAnimation { target: item; property: "scale"; to: 0; duration: 400; easing.type: Easing.InOutQuad }
                PropertyAction { target: item; property: "ListView.delayRemove"; value: false }
            }

            Image {
                id: imgFavorite
                property bool _favorite: favorite

                source: _favorite ? "img/favorite-project.png" : "img/unfavorite-project.png"
                anchors.left: parent.left
                anchors.top: parent.top
                anchors.leftMargin: 10
                anchors.topMargin: (parent.height / 2) - (imgFavorite.height / 2)

                MouseArea {
                    anchors.fill: parent

                    onClicked: {
                        if(imgFavorite._favorite){
                            imgFavorite.source = "img/unfavorite-project.png";
                            imgFavorite._favorite = false;
                        }else{
                            imgFavorite.source = "img/favorite-project.png";
                            imgFavorite._favorite = true;
                        }
                        root.markAsFavorite(item._path, imgFavorite._favorite);
                    }
                }
            }

            Rectangle {
                id: texts
                color: "transparent"
                height: item.height
                width: item.width - imgFavorite.width - imgDelete.width - 60
                anchors.left: imgFavorite.right
                anchors.leftMargin: 10
                anchors.top: parent.top
                anchors.topMargin: 5
                Column {
                    id: col
                    anchors.fill: parent
                    Text { text: 'NAME: ' + name; width: texts.width; elide: Text.ElideMiddle }
                    Text { text: 'PATH: ' + path; width: texts.width; elide: Text.ElideMiddle }
                }

                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        var coord = mapToItem(_projects, mouseX, mouseY)
                        var index = _projects.indexAt(coord.x, coord.y);
                        _projects.currentIndex = index;
                        root.openProject(item._path);
                    }
                }
            }

            Image {
                id: imgDelete
                source: "img/delete-project.png"
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.rightMargin: 20
                anchors.topMargin: (parent.height / 2) - (imgFavorite.height / 2)

                MouseArea {
                    anchors.fill: parent

                    onClicked: {
                        var coord = mapToItem(_projects, mouseX, mouseY)
                        var index = _projects.indexAt(coord.x, coord.y);
                        _projects.model.remove(index);
                        root.removeProject(item._path);
                    }
                }
            }
        }
    }

    ListView {
        id: listProjects
        width: root.width
        height: root.height

        focus: true
        model: ListModel {}
        delegate: contactDelegate
        highlight: Rectangle { color: "lightsteelblue"; radius: 5; width: (root.width - 10) }

        Keys.onReturnPressed: {
            var path = listProjects.model.get(listProjects.currentIndex).path;
            root.openProject(path);
        }
    }

    function add_project(name, path, favorite){
        listProjects.model.append({"name": name, "path": path, "favorite": favorite});
    }
}
