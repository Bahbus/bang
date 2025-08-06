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
        title: qsTr("Host Game")
        standardButtons: Dialog.Ok | Dialog.Cancel
        contentItem: Column {
            spacing: 8
            TextField {
                id: portField
                placeholderText: qsTr("Port (1-65535)")
                text: "8765"
                validator: IntValidator { bottom: 1; top: 65535 }
            }
            Label {
                text: qsTr("Enter a valid port")
                color: "red"
                visible: !portField.acceptableInput
            }
            TextField {
                id: maxField
                placeholderText: qsTr("Max Players (2-8)")
                text: "7"
                validator: IntValidator { bottom: 2; top: 8 }
            }
            Label {
                text: qsTr("Players must be 2-8")
                color: "red"
                visible: !maxField.acceptableInput
            }
            TextField { id: certField; placeholderText: qsTr("Certificate") }
            TextField { id: keyField; placeholderText: qsTr("Key File") }
        }
        onAccepted: {
            if (!portField.acceptableInput || !maxField.acceptableInput) {
                hostDialog.open()
                return
            }
            root.hostRequested(
                menu.nameText,
                portField.text,
                maxField.text,
                certField.text,
                keyField.text,
            )
        }
    }

    Dialog {
        id: joinDialog
        modal: true
        title: qsTr("Join Game")
        standardButtons: Dialog.Ok | Dialog.Cancel
        contentItem: Column {
            spacing: 8
            TextField {
                id: tokenField
                placeholderText: qsTr("Token")
                validator: RegExpValidator { regExp: /^[A-Za-z0-9+\/_=-]{0,256}$/ }
            }
            Label {
                text: qsTr("Invalid token")
                color: "red"
                visible: tokenField.text !== "" && !tokenField.acceptableInput
            }
            TextField { id: addrField; placeholderText: qsTr("Host Address"); text: "localhost" }
            TextField {
                id: portJoinField
                placeholderText: qsTr("Port (1-65535)")
                text: "8765"
                validator: IntValidator { bottom: 1; top: 65535 }
            }
            Label {
                text: qsTr("Enter a valid port")
                color: "red"
                visible: !portJoinField.acceptableInput
            }
            TextField {
                id: codeField
                placeholderText: qsTr("Room Code (6 hex)")
                validator: RegExpValidator { regExp: /^[0-9A-Fa-f]{6}$/ }
            }
            Label {
                text: qsTr("Code must be 6 hex chars")
                color: "red"
                visible: codeField.text !== "" && !codeField.acceptableInput
            }
            TextField { id: cafileField; placeholderText: qsTr("CA File") }
        }
        onAccepted: {
            if (tokenField.text !== "") {
                if (!tokenField.acceptableInput) {
                    joinDialog.open()
                    return
                }
                root.joinRequested(
                    menu.nameText,
                    "",
                    0,
                    tokenField.text,
                    cafileField.text,
                )
            } else {
                if (!portJoinField.acceptableInput || !codeField.acceptableInput) {
                    joinDialog.open()
                    return
                }
                root.joinRequested(
                    menu.nameText,
                    addrField.text,
                    portJoinField.text,
                    codeField.text,
                    cafileField.text,
                )
            }
        }
    }

    Dialog {
        id: settingsDialog
        modal: true
        title: qsTr("Settings")
        standardButtons: Dialog.Ok | Dialog.Cancel
        contentItem: Column {
            spacing: 8
            ComboBox {
                id: themeCombo
                model: [qsTr("light"), qsTr("dark")]
                currentIndex: root.theme === "dark" ? 1 : 0
            }
        }
        onAccepted: {
            root.theme = themeCombo.currentText
            root.settingsChanged(root.theme)
        }
    }
}
