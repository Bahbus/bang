import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Dialog {
    id: root
    modal: true
    property string titleText: qsTr("Confirm")
    property string message: ""
    title: titleText
    standardButtons: Dialog.Ok | Dialog.Cancel

    contentItem: ColumnLayout {
        spacing: 8
        Label {
            Layout.fillWidth: true
            text: root.message
            wrapMode: Text.Wrap
        }
    }
}
