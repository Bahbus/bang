import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    width: 400
    height: 300
    color: "#333333"

    Column {
        anchors.centerIn: parent
        spacing: 10

        Text {
            text: "Bang!"
            font.pointSize: 24
            color: "white"
        }

        Button { text: "Host Game" }
        Button { text: "Join Game" }
        Button { text: "Settings" }
    }
}
