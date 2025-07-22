import QtQuick 2.15
import QtQuick.Controls 2.15

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
        spacing: 10

        Text {
            text: "Bang!"
            font.pointSize: 24
            color: theme === "dark" ? "white" : "black"
        }

        TextField {
            id: nameField
            placeholderText: "Name"
            width: 200 * scale
            color: theme === "dark" ? "white" : "black"
            background: Rectangle {
                color: theme === "dark" ? "#3c3c3c" : "#fff8dc"
            }
        }

        Button {
            text: "Host Game"
            onClicked: root.hostGame()
        }
        Button {
            text: "Join Game"
            onClicked: root.joinGame()
        }
        Button {
            text: "Settings"
            onClicked: root.settings()
        }
    }
    property alias nameText: nameField.text
}
