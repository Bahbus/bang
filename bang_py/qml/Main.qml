import QtQuick 2.15
import QtQuick.Controls 2.15

// Styled buttons reside in this directory
import "./"

Item {
    id: root
    width: 1024
    height: 768
    property string theme: "light"
    property string page: "menu"

    signal hostRequested(string name, int port, int maxPlayers, string cert, string key)
    signal joinRequested(string name, string addr, int port, string code, string cafile)
    signal settingsChanged(string theme)

    signal drawCard()
    signal discardCard()
    signal endTurn()
    signal playCard(int index)
    signal discardFromHand(int index)

    Loader {
        id: loader
        anchors.fill: parent
        sourceComponent: page === "menu" ? menuComponent : gameComponent
    }

    Component {
        id: menuComponent
        MainMenu {
            id: menu
            theme: root.theme
            scale: 1.0
            onHostGame: hostDialog.open()
            onJoinGame: joinDialog.open()
            onSettings: settingsDialog.open()
        }
    }

    Component {
        id: gameComponent
        GameBoard {
            id: board
            theme: root.theme
            scale: 1.0
            onDrawCard: root.drawCard()
            onDiscardCard: root.discardCard()
            onEndTurn: root.endTurn()
            onPlayCard: root.playCard(index)
            onDiscardFromHand: root.discardFromHand(index)
            Component.onCompleted: root.gameBoardItem = board
        }
    }

    property var gameBoardItem: null

    function showGame() { page = "game" }

    Dialog {
        id: hostDialog
        modal: true
        title: "Host Game"
        standardButtons: Dialog.Ok | Dialog.Cancel
        contentItem: Column {
            spacing: 8
            TextField { id: portField; placeholderText: "Port"; text: "8765" }
            TextField { id: maxField; placeholderText: "Max Players"; text: "7" }
            TextField { id: certField; placeholderText: "Certificate" }
            TextField { id: keyField; placeholderText: "Key File" }
        }
        onAccepted: root.hostRequested(menu.nameText, portField.text, maxField.text, certField.text, keyField.text)
    }

    Dialog {
        id: joinDialog
        modal: true
        title: "Join Game"
        standardButtons: Dialog.Ok | Dialog.Cancel
        contentItem: Column {
            spacing: 8
            TextField { id: tokenField; placeholderText: "Token" }
            TextField { id: addrField; placeholderText: "Host Address"; text: "localhost" }
            TextField { id: portJoinField; placeholderText: "Port"; text: "8765" }
            TextField { id: codeField; placeholderText: "Room Code" }
            TextField { id: cafileField; placeholderText: "CA File" }
        }
        onAccepted: {
            if (tokenField.text !== "") {
                root.joinRequested(menu.nameText, "", 0, tokenField.text, cafileField.text)
            } else {
                root.joinRequested(menu.nameText, addrField.text, portJoinField.text, codeField.text, cafileField.text)
            }
        }
    }

    Dialog {
        id: settingsDialog
        modal: true
        title: "Settings"
        standardButtons: Dialog.Ok | Dialog.Cancel
        contentItem: Column {
            spacing: 8
            ComboBox {
                id: themeCombo
                model: ["light", "dark"]
                currentIndex: root.theme === "dark" ? 1 : 0
            }
        }
        onAccepted: {
            root.theme = themeCombo.currentText
            root.settingsChanged(root.theme)
        }
    }
}
