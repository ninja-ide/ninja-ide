import QtQuick 2.6
import QtQuick.Controls 1.3
import QtQuick.Layouts 1.3

Rectangle {

    width: 512
    height: 512
    color: "white"

    ColumnLayout {
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.topMargin: 48
        anchors.leftMargin: 36

        Rectangle {
            width: 384
            height: 120
            color: "white"

            ColumnLayout {

                Text {
                    text: "Languages"
                    color: "black"
                    font.family: "Segoe UI"
                    font.pixelSize: 20
                }

                Text {
                    topPadding: 24
                    width: 256
                    elide: Text.ElideRight
                    lineHeight: 1.2
                    font.weight: Font.ExtraLight
                    font.family: "Segoe UI"
                    text: "Choose from the languages already installed on your computer below\n" +
                          "or click Add Translation to download other Languages from the community. "
                    font.pixelSize: 12

                }

            }

        }


        ColumnLayout {
            width: 384

            Rectangle {
                width: parent.width
                height: 32
                color: "#fff"

                MouseArea  {
                    anchors.fill: parent
                    hoverEnabled: true

                    onEntered: {
                        parent.color = "#f1f1f1"
                    }

                    onPressed: {
                        parent.color = "#c1c1c1"
                        console.log('open')
                    }

                    onExited: {
                        parent.color = "#fff"
                    }

                }

                Text {
                    anchors.verticalCenter: parent.verticalCenter
                    padding: 8
                    font.bold: false
                    font.weight: Font.Thin
                    font.family: "Segoe UI"
                    text: "Add a Language"
                    font.pixelSize: 16
                }

            }

            ListView {
                width: parent.width
                height: 180

                Component {
                    id: languageDelegate

                    Rectangle {
                        id: listCont
                        width: parent.width
                        height: ListView.isCurrentItem ? 80 : 32
                        color: ListView.isCurrentItem ? "#f1f1f1" : "white"

                        ColumnLayout {

                            width: parent.width
                            height: listCont.ListView.isCurrentItem ? 64 : 32

                            Text {
                                anchors.top: parent.top
                                padding: 8
                                font.weight: Font.ExtraLight
                                font.family: "Segoe UI"
                                text: language + " (" + country + ")"
                                font.pixelSize: 16
                            }

                            LDMButton {
                                visibility: listCont.ListView.isCurrentItem ? true : false
                                btnColor: listCont.ListView.isCurrentItem ? '#c1c1c1' : "#fff"

                                onClick: {
                                    // do something
                                }

                            }

                        }
                    }
                }

                model: LanguageDataModel {}
                delegate: languageDelegate
                focus: true

            }

        }

    }

}
