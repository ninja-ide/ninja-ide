import QtQuick 2.6
import QtQuick.Controls 1.3
import QtQuick.Layouts 1.3

Rectangle {
    id: cont
    width: 512
    height: 512
    color: "white"

    property string languageNames: "Chinese (China)"
    property string status: "Downloading"
    property string currDownPer: "45%"
    property int progressWidth: 1

    ColumnLayout {

        // The Navigation
        Rectangle {
            width: cont.width
            height: 36

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

        // The main body
        ColumnLayout {

            anchors.top: parent.children[0].bottom
            anchors.left: parent.left
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.topMargin: 20
            anchors.leftMargin: 36

            Rectangle {
                width: 384
                height: 48
                color: "white"

                    Text {
                        text: languageNames
                        color: "black"
                        font.family: "Segoe UI"
                        font.pixelSize: 28
                    }



            }


            Rectangle {
                width: cont.width
                height: 48
                anchors.top: parent.children[0].bottom
                anchors.topMargin: 20
                Text {
                    topPadding: 2
                    width: 256
                    elide: Text.ElideRight
                    lineHeight: 1.2
                    font.weight: Font.ExtraLight
                    font.family: "Segoe UI"
                    text: status
                    font.pixelSize: 20

                }

            }


            Rectangle {
                width: cont.width
                height: 28
                anchors.top: parent.children[1].bottom

                Text {
                    topPadding: 2
                    width: 256
                    elide: Text.ElideRight
                    lineHeight: 1.2
                    font.weight: Font.ExtraLight
                    font.family: "Segoe UI"
                    text: "Downloaded " + currDownPer + "..."
                    font.pixelSize: 16

                }

            }


            Rectangle {
                width: cont.width - 120
                height: 48
                anchors.top: parent.children[2].bottom

                Rectangle {
                    width: parent.width / 100 * progressWidth
                    height: 8
                    color: '#e1e1e1'
                }

            }

        }



    }

}
