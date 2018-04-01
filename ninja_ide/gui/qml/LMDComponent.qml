import QtQuick 2.6
import QtQuick.Controls 1.5
import QtQuick.Layouts 1.3

Rectangle {
    width: 1024
    height: 512

    property string placeHolder: "Type a language name to search"

    ColumnLayout {
        width: parent.width
        anchors.left: parent.left
        anchors.leftMargin: 12

        // Header
        Rectangle {
            width: parent.width
            height: 84
            anchors.left: parent.left
            anchors.leftMargin: 12

            Text {
                anchors.verticalCenter: parent.verticalCenter
                text: "Choose Language to Start Downloading"
                color: "black"
                font.family: "Segoe UI"
                font.pixelSize: 24
                font.weight: Font.ExtraLight

            }
        }

        Rectangle {
            width: 280
            height: 32
            color: "white"
            anchors.left: parent.left
            anchors.leftMargin: 12

            Rectangle {
                width: 280
                height: 32
                border.width: 2
                border.color: "orangered"



                RowLayout {
                    width: parent.width
                    height: parent.height

                    MouseArea {
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.IBeamCursor

                        onPressed: {
                            if(search.text == placeHolder) {
                                search.text = ''
                            } else {
                            }
                        }
                    }

                    focus: true
                    Keys.onPressed: {
                        if(event.key == Qt.Key_Backspace) {
                            var length = search.text.length - 1
                            search.text = search.text.slice(0, length)
                        } else {
                        search.text += event.text
                        }
                    }

                    Text {
                        id: search
                        anchors.left: parent.left
                        anchors.leftMargin: 8
                        anchors.verticalCenter: parent.verticalCenter
                        width: parent.width - 50
                        elide: Text.ElideRight
                        maximumLineCount: 12
                        text: placeHolder
                        font.pixelSize: 14
                        color: "#ccc"
                    }

                    Image {
                        anchors.right: parent.right
                        anchors.rightMargin: 8
                        width: 32; height: 32;
                        source: "img/delete-project.png"
                    }

                }

            }

        }

        // The Items View, I think this is self-explanatory
        GridView {
            id: downloadView
            width: parent.width - 24
            height: 384
            anchors.top: parent.children[1].bottom
            anchors.topMargin: 12
            cellWidth: 284
            cellHeight: 72

            // The component for displayed for each item in the view
            Component {
                id: downloadDelegate

                // I put the whole thing still in a rectangle, actually you can change it.
                Rectangle {
                    id: deleRect
                    width: downloadView.cellWidth
                    height: downloadView.cellHeight
                    color: "transparent"

                    ColumnLayout {
                        width: downloadView.cellWidth
                        //height: parent.height
                        spacing: 0
                        // This is sort of padding within the component box
                        anchors.top: parent.top
                        anchors.topMargin: 8
                        anchors.left: parent.left
                        anchors.leftMargin: 12
                        //height: downloadView.cellHeight

                        // To handle to hover and clicks from a mouse
                        MouseArea {
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                            hoverEnabled: true

                            onEntered: {
                                deleRect.border.width = 2
                                deleRect.border.color = "#e1e1e1"
                                downloadView.highlightItem.border.width = 0
                            }

                            // prefered over onClicked
                            onPressed: {
                                deleRect.border.color = "#c1c1c1"
                            }

                            onExited: {
                                deleRect.border.width = 0
                            }
                        }

                        Text {
                            font.bold: false
                            font.weight: Font.Thin
                            font.family: "Segoe UI"
                            text: language
                            color: "orangered"
                            font.pixelSize: 22
                        }

                        Text {
                            font.bold: false
                            font.weight: Font.Thin
                            font.family: "Segoe UI"
                            text: country
                            font.pixelSize: 16
                        }

                        /*
                        Rectangle {
                            width: parent.width
                            height: 42
                            color: 'transparent'
                            border.width: 2
                            anchors.top: parent.top
                            anchors.topMargin: 0
                            anchors.left: parent.left
                            anchors.leftMargin: 12
                            Text {
                                font.bold: false
                                font.weight: Font.Thin
                                font.family: "Segoe UI"
                                text: language
                                color: "orangered"
                                font.pixelSize: 22
                            }

                        }

                        Rectangle {
                            width: parent.width
                            height: 32
                            border.width: 2
                            color: 'transparent'
                            anchors.left: parent.left
                            anchors.leftMargin: 1
                            Text {
                                font.bold: false
                                font.weight: Font.Thin
                                font.family: "Segoe UI"
                                text: country
                                font.pixelSize: 16
                            }

                        }*/
                    }

                }

            }

            // The model is located in qml/LMDModel.qml
            model: LMDModel {}
            delegate: downloadDelegate
            highlight: Rectangle {
                id: highRect
                border.width: 2
                border.color: "#e1e1e1"
            }
            // This could be removed in the future
            focus: true

        }


    }

}
