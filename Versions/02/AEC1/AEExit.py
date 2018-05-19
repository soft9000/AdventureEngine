from AEC1 import AERoom


class Exit(AERoom.Room):
    def __init__(self):
        super(Exit, self).__init__("")

    def enter(self, player):
        player.gameOver = True