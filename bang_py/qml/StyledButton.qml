import QtQuick 2.15
import QtQuick.Controls 2.15

// A reusable themed button with hover effects and optional icon.
Button {
    id: control
    property string theme: "light"
    property url iconSource: ""
    implicitHeight: 40
    implicitWidth: 120
    hoverEnabled: true

    contentItem: Row {
        spacing: icon.visible ? 6 : 0
        anchors.centerIn: parent
        Image {
            id: icon
            source: control.iconSource
            visible: source !== ""
            width: 20
            height: 20
            fillMode: Image.PreserveAspectFit
        }
        Text {
            text: control.text
            color: control.theme === "dark" ? "white" : "black"
            font.pointSize: 14
        }
    }

    background: Rectangle {
        radius: 4
        border.color: control.theme === "dark" ? "#888888" : "#8b4513"
        color: control.down
               ? (control.theme === "dark" ? "#333333" : "#e39b3a")
               : control.hovered
                 ? (control.theme === "dark" ? "#555555" : "#f0b070")
                 : (control.theme === "dark" ? "#444444" : "#f4a460")
    }
}
