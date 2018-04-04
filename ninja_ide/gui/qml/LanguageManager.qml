import QtQuick 2.6
import QtQuick.Controls 1.3
import QtQuick.Layouts 1.3

Rectangle {
    id: langRect

    width: 512
    height: 512
    color: "white"
    visible: true

    property string statusComment: ""
    property int total: 0
    property int downloaded: 0
    property int progressMeter: 2
    property string percentString: ""

    StackView {
        width: parent.width
        height: parent.height
        id: stack
        initialItem: selectLang
        property string languageName: ""
        property string curr_lang: "Undefined"
        property string curr_lang_cc: "Undefined"

        Component {
            id: selectLang

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

                    ListView {
                        id: listView
                        width: parent.width
                        height: 180

                        Component {
                            id: languageDelegate

                            Rectangle {
                                id: listCont
                                width: parent.width
                                height: 36
                                color: "white"

                                MouseArea {
                                    anchors.fill: parent
                                    cursorShape: Qt.PointingHandCursor
                                    hoverEnabled: true

                                    onEntered: {
                                        //listCont.height = 80
                                        listCont.color = "#f1f1f1"
                                    }

                                    onPressed: {
                                        if(status !== 'Default') {
                                            console.log(stack.curr_lang, stack.curr_lang_cc,
                                                        language, country);
                                            parentClass.set_as_default(stack.curr_lang, stack.curr_lang_cc,
                                                                       language, country)
                                        }
                                    }

                                    onExited: {
                                            listCont.color = "white"
                                    }

                                }

                                RowLayout {
                                    id: listLay

                                    width: parent.width
                                    height: 36

                                    Text {
                                        anchors.top: parent.top
                                        padding: 8
                                        font.weight: Font.ExtraLight
                                        font.family: "Segoe UI"
                                        text: language + " (" + country + ")"
                                        font.pixelSize: 16
                                    }

                                    Text {
                                        anchors.top: parent.top
                                        anchors.right: parent.right
                                        anchors.rightMargin: 8
                                        padding: 8
                                        font.weight: Font.ExtraLight
                                        font.family: "Segoe UI"
                                        text: status
                                        color: {
                                            if(status == 'Default' &&
                                                    (stack.curr_lang = language) &&
                                                    (stack.curr_lang_cc = country)) {
                                                'dodgerblue'
                                            } else {
                                                "#3a3a3a"
                                            }
                                        }
                                        font.pixelSize: 12
                                    }

                                }
                            }
                        }

                        model: InstalledLangDataModel {}
                        header: HeaderItem {}
                        delegate: languageDelegate
                        spacing: 12
                        focus: true

                    }

                }

            }

        } // selectLang

        Component {
            id: browseLang

            LMDComponent {
                boundWidth: stack.parent.width
                boundHeight: stack.parent.height
            }

        } // browseLang

        Component {
            id: downloadPage

            LMDPage {
                languageNames: stack.languageName
                status: statusComment
                currDownPer: percentString
                progressWidth: progressMeter
            }

        }

    }

    Connections {
        target: parentClass

        onStatus: {
            statusComment = pinging
        }

        onDownloading: {
            downloaded = downloading_lang
            percentString = downloaded + "%"
            progressMeter = downloaded / 10
        }

        onDownloadFinish: {
            statusComment = finishUp
            console.log(statusComment)
            for(var x=0; x < stack.depth; x++){
                stack.pop()
            }
        }

    }

}

