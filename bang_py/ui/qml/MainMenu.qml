import QtQuick 2.15
import QtQuick.Controls 2.15

// Styled buttons reside in this directory
import "./"

Rectangle {
    id: root
    property string theme: "light"
    property real scale: 1.0
    width: 400 * scale
    height: 300 * scale
    color: theme === "dark" ? "#333333" : "#deb887"

    signal hostGame()
    signal joinGame()
    signal settings()

    Column {
        anchors.centerIn: parent
        spacing: 10 * scale

        Text {
            text: qsTr("Bang!")
            font.pointSize: 24
            color: theme === "dark" ? "white" : "black"
        }

        TextField {
            id: nameField
            placeholderText: qsTr("Name (max 20 chars)")
            width: 200 * scale
            color: theme === "dark" ? "white" : "black"
            background: Rectangle {
                color: theme === "dark" ? "#3c3c3c" : "#fff8dc"
            }
            validator: RegExpValidator { regExp: /^[\x20-\x7E]{1,20}$/ }
        }

        Label {
            text: qsTr("Use up to 20 printable characters")
            color: "red"
            visible: nameField.text !== "" && !nameField.acceptableInput
        }

        StyledButton {
            text: qsTr("Host Game")
            theme: root.theme
            scale: root.scale
            width: 200 * root.scale
            iconSource: "../assets/icons/host.svg"
            onClicked: root.hostGame()
        }
        StyledButton {
            text: qsTr("Join Game")
            theme: root.theme
            scale: root.scale
            width: 200 * root.scale
            iconSource: "../assets/icons/join.svg"
            onClicked: root.joinGame()
        }
        StyledButton {
            text: qsTr("Settings")
            theme: root.theme
            scale: root.scale
            width: 200 * root.scale
            iconSource: "../assets/icons/settings.svg"
            onClicked: root.settings()
        }
    }
    property alias nameText: nameField.text
}
