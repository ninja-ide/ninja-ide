import QtQuick 2.6
import QtQuick.Controls 1.5
import QtQuick.Layouts 1.3

Rectangle {

    property int boundWidth: 512
    property int boundHeight: 512
    property string placeHolder: "Type a language name to search"

    width: boundWidth
    height: boundHeight
    color: "white"

    ColumnLayout {
        width: boundWidth

        // The Navigation
        Rectangle {
            id: navbar
            width: boundWidth
            height: 36
            anchors.top: parent.top

            Rectangle {
                width: 48
                height: 36
                color: "dodgerblue"

                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true

                    onEntered: {
                        parent.color = "lightblue"
                    }

                    onPressed: {
                        // Not available yet but will be available in the stackView
                        stack.pop()
                    }

                    onExited: {
                        parent.color = "dodgerblue"
                    }

                }

                Text {
                    anchors.centerIn: parent
                    textFormat: Text.RichText
                    text: "<h2>&larr;</h2>"
                    color: "white"
                }

            }

        }

        // The main Page
        ColumnLayout {
            width: parent.width
            height: boundHeight - 36
            anchors.top: navbar.bottom
            anchors.left: parent.left
            anchors.leftMargin: 12

            // Header
            Rectangle {
                id: header
                width: parent.width
                height: 84
                color: "white"
                anchors.top: parent.top
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
                id: searchBar
                width: 280
                height: 32
                color: "white"
                anchors.top: header.bottom
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

            Rectangle {
                id: scrollCont
                width: boundWidth
                height: parent.height - 128
                anchors.top: searchBar.bottom
                anchors.bottom: parent.bottom

                ScrollView {
                    id: sv
                    width: parent.width
                    height: parent.height - 8
                    anchors.top: parent.top
                    anchors.topMargin: 8

                    // The Items View, I think this is self-explanatory
                    GridView {
                        id: downloadView
                        z: -1
                        width: scrollCont.width - 24
                        height: parent.height
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
                                    spacing: 0
                                    // This is sort of padding within the component box
                                    anchors.top: parent.top
                                    anchors.topMargin: 8
                                    anchors.left: parent.left
                                    anchors.leftMargin: 12

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
                                            stack.languageName = language
                                            parentClass.start_download(language, country)
                                            stack.push(downloadPage)
                                        }

                                        onExited: {
                                            deleRect.border.width = 0
                                        }
                                    }

                                    Text {
                                        id: lang
                                        anchors.top: parent.top
                                        font.bold: false
                                        font.weight: Font.Thin
                                        font.family: "Segoe UI"
                                        text: language
                                        color: "orangered"
                                        font.pixelSize: 22
                                    }

                                    Text {
                                        anchors.top: lang.bottom
                                        font.bold: false
                                        font.weight: Font.Thin
                                        font.family: "Segoe UI"
                                        text: country
                                        font.pixelSize: 16
                                    }
                                }

                            }

                        }

                        // The model is located in qml/AvailableLangDataModel.qml
                        model: AvailableLangDataModel {}
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

        }



    }

}
