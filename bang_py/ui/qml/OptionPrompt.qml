import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Dialog {
    id: root
    modal: true
    property string titleText: qsTr("Choose")
    property var options: []
    property int selectedIndex: -1
    title: titleText
    standardButtons: Dialog.Ok | Dialog.Cancel
    signal acceptedIndex(int index)

    contentItem: ColumnLayout {
        spacing: 8
        ListView {
            id: optionList
            Layout.fillWidth: true
            Layout.preferredHeight: Math.min(contentHeight, 200)
            model: root.options
            delegate: ItemDelegate {
                text: modelData
                width: optionList.width
                onClicked: root.selectedIndex = index
                highlighted: root.selectedIndex === index
            }
        }
        Label {
            Layout.fillWidth: true
            text: qsTr("Please select an option")
            color: "red"
            visible: root.selectedIndex === -1
        }
    }

    onAccepted: {
        if (selectedIndex === -1) {
            root.open()
            return
        }
        acceptedIndex(selectedIndex)
    }
}
