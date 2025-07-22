import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    width: 800
    height: 600

    Rectangle {
        id: table
        anchors.fill: parent
        color: "#006400"
    }

    Text {
        anchors.centerIn: parent
        text: "Board Prototype"
        color: "white"
        font.pointSize: 20
    }
}
