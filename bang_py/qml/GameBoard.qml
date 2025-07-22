import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: root
    property string theme: "light"
    property real scale: 1.0
    property var players: []
    property alias logText: logArea.text
    width: 800 * scale
    height: 600 * scale

    Rectangle {
        id: table
        anchors.fill: parent
        color: theme === "dark" ? "#004000" : "#006400"
    }

    Text {
        anchors.centerIn: parent
        text: "Board Prototype"
        color: theme === "dark" ? "white" : "black"
        font.pointSize: 20
    }

    ListView {
        id: playerList
        width: 200 * scale
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        model: players
        delegate: Row {
            spacing: 4
            Text { text: name }
            Repeater {
                model: health
                delegate: Rectangle {
                    width: 8 * scale
                    height: 8 * scale
                    color: "red"
                }
            }
        }
    }

    Rectangle {
        id: logPanel
        width: parent.width * 0.35
        height: parent.height * 0.3
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        color: theme === "dark" ? "#000000" : "#ffffff"
        opacity: 0.7

        TextArea {
            id: logArea
            anchors.fill: parent
            readOnly: true
            wrapMode: TextArea.WrapAnywhere
            background: Rectangle { color: "transparent" }
        }
    }
}
