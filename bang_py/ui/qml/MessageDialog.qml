import QtQuick 2.15
import QtQuick.Controls 2.15

Dialog {
    id: root
    modal: true
    property string titleText: qsTr("Message")
    property string message: ""
    property bool error: false
    title: titleText
    standardButtons: Dialog.Ok

    contentItem: Column {
        spacing: 8
        Label {
            text: root.message
            wrapMode: Text.Wrap
            color: root.error ? "red" : "black"
        }
    }
}
