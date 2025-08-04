import QtQuick 2.15
import QtQuick.Controls 2.15
import QtMultimedia

// Styled buttons reside in this directory
import "./"

Item {
    id: root
    property string theme: "light"
    property real scale: 1.0
    property var players: []
    property var hand: []
    property string selfName: ""
    property alias logText: logArea.text

    signal drawCard()
    signal discardCard()
    signal endTurn()
    signal playCard(int index)
    signal discardFromHand(int index)

    width: 800 * scale
    height: 600 * scale
    property real cardW: 60 * scale
    property real cardH: 90 * scale

    onHandChanged: shuffleSound.play()

    Rectangle {
        anchors.fill: parent
        color: theme === "dark" ? "#004000" : "#006400"
    }

    Canvas {
        id: star
        width: 30 * scale
        height: 30 * scale
        anchors.centerIn: parent
        onPaint: {
            var ctx = getContext("2d")
            ctx.fillStyle = "gold"
            ctx.beginPath()
            for (var i = 0; i < 5; i++) {
                var ang = -Math.PI / 2 + i * 2 * Math.PI / 5
                ctx.lineTo(width / 2 + width / 2 * Math.cos(ang),
                           height / 2 + width / 2 * Math.sin(ang))
                ang += Math.PI / 5
                ctx.lineTo(width / 2 + width / 4 * Math.cos(ang),
                           height / 2 + width / 4 * Math.sin(ang))
            }
            ctx.closePath()
            ctx.fill()
        }
    }

    Rectangle {
        id: drawPile
        width: cardW
        height: cardH
        anchors.centerIn: parent
        anchors.horizontalCenterOffset: -cardW
        color: theme === "dark" ? "#555" : "#bbb"
        border.color: "black"
        radius: 4 * scale
    }
    StyledButton {
        text: "Draw"
        theme: root.theme
        scale: root.scale
        iconSource: "../assets/icons/draw.svg"
        anchors.top: drawPile.bottom
        anchors.horizontalCenter: drawPile.horizontalCenter
        onClicked: { clickSound.play(); drawSound.play(); root.drawCard() }
    }

    Rectangle {
        id: discardPile
        width: cardW
        height: cardH
        anchors.centerIn: parent
        anchors.horizontalCenterOffset: cardW
        color: theme === "dark" ? "#666" : "#ddd"
        border.color: "black"
        radius: 4 * scale
    }
    StyledButton {
        text: "Discard"
        theme: root.theme
        scale: root.scale
        iconSource: "../assets/icons/discard.svg"
        anchors.top: discardPile.bottom
        anchors.horizontalCenter: discardPile.horizontalCenter
        onClicked: { clickSound.play(); discardSound.play(); root.discardCard() }
    }

    Repeater {
        model: players.length
        delegate: Item {
            property var pl: players[index]
            width: cardW
            height: cardH
            property real angleStep: 360 / players.length
            property real ang: (index - root.selfIndex) * angleStep + 90
            property real rad: ang * Math.PI / 180
            property real radius: Math.min(root.width, root.height) * 0.35
            x: root.width / 2 + radius * Math.cos(rad) - width / 2
            y: root.height / 2 + radius * Math.sin(rad) - height / 2

            Rectangle {
                anchors.fill: parent
                color: theme === "dark" ? "#333" : "#ddd"
                border.color: "black"
                radius: 4 * scale
            }
            Row {
                id: bullets
                spacing: 2 * scale
                anchors.top: parent.bottom
                anchors.horizontalCenter: parent.horizontalCenter
                Repeater {
                    model: pl.health
                    delegate: Rectangle {
                        width: 8 * scale
                        height: 8 * scale
                        color: "red"
                        radius: 2 * scale
                    }
                }
            }
            Text {
                text: pl.name
                anchors.top: bullets.bottom
                anchors.horizontalCenter: parent.horizontalCenter
                color: theme === "dark" ? "white" : "black"
                font.pixelSize: 12 * scale
            }
        }
    }
    property int selfIndex: {
        for (var i = 0; i < players.length; i++) {
            if (players[i].name === selfName)
                return i
        }
        return 0
    }

    Rectangle {
        id: logPanel
        width: parent.width * 0.35
        height: parent.height * 0.3
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        color: theme === "dark" ? "#000000" : "#ffffff"
        opacity: 0.7
        border.color: theme === "dark" ? "#444" : "#222"
        TextArea {
            id: logArea
            anchors.fill: parent
            readOnly: true
            wrapMode: TextArea.WrapAnywhere
            color: theme === "dark" ? "white" : "black"
            background: Rectangle { color: "transparent" }
        }
    }

    StyledButton {
        text: "End Turn"
        theme: root.theme
        scale: root.scale
        iconSource: "../assets/icons/end_turn.svg"
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.rightMargin: 10 * scale
        anchors.bottomMargin: 10 * scale
        onClicked: { clickSound.play(); root.endTurn() }
    }

    Row {
        id: handRow
        spacing: 4 * scale
        anchors.bottom: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        Repeater {
            model: hand.length
            delegate: Item {
                width: cardW
                height: cardH
                property var card: hand[index]
                Image {
                    anchors.fill: parent
                    source: card.source
                    fillMode: Image.PreserveAspectFit
                }
                Text {
                    text: card.name
                    anchors.centerIn: parent
                    color: theme === "dark" ? "white" : "black"
                    visible: card.source === ""
                    font.pixelSize: 12 * scale
                }
                MouseArea {
                    anchors.fill: parent
                    acceptedButtons: Qt.LeftButton | Qt.RightButton
                    onClicked: {
                        clickSound.play()
                        if (mouse.button === Qt.RightButton) {
                            discardSound.play()
                            root.discardFromHand(index)
                        } else {
                            playSound.play()
                            root.playCard(index)
                        }
                    }
                }
            }
        }
    }

    SoundEffect { id: clickSound; source: "../assets/audio/ui_click.mp3" }
    SoundEffect { id: drawSound; source: "../assets/audio/draw_card.mp3" }
    SoundEffect { id: discardSound; source: "../assets/audio/discard_card.mp3" }
    SoundEffect { id: playSound; source: "../assets/audio/play_card.mp3" }
    SoundEffect { id: shuffleSound; source: "../assets/audio/shuffle_cards.mp3" }
}
