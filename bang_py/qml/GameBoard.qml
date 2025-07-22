import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: root
    property string theme: "light"
    property real scale: 1.0
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
}
