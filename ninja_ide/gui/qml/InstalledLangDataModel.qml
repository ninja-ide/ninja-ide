import QtQuick 2.4
import QtQuick.Controls 1.3
import QtQuick.Layouts 1.3

ListModel {
        
    ListElement {
        index: 0
        language: "English"
        country: "US"
        status: "Default"
    }

    ListElement {
        index: 1
        language: "German"
        country: "Germany"
        status: "set as Default"
    }
}
