import QtQuick 2.15
import QtQuick.Controls 2.15

// A reusable themed button with hover effects and optional icon.
Button {
    id: control
    property string theme: "light"
    property url iconSource: ""
    property real scale: 1.0
    implicitHeight: 40 * scale
    implicitWidth: 120 * scale
    hoverEnabled: true

    contentItem: Row {
        spacing: (icon.visible ? 6 : 0) * scale
        anchors.centerIn: parent
        Image {
            id: icon
            source: control.iconSource
            visible: source !== ""
            width: 20 * scale
            height: 20 * scale
            fillMode: Image.PreserveAspectFit
        }
        Text {
            text: control.text
            color: control.theme === "dark" ? "white" : "black"
            font.pointSize: 14 * scale
        }
    }

    background: Rectangle {
        radius: 4 * scale
        border.color: control.theme === "dark" ? "#888888" : "#8b4513"
        color: control.down
               ? (control.theme === "dark" ? "#333333" : "#e39b3a")
               : control.hovered
                 ? (control.theme === "dark" ? "#555555" : "#f0b070")
                 : (control.theme === "dark" ? "#444444" : "#f4a460")
    }
}
