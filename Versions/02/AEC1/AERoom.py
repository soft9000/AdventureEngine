from AEC1.AESupport import Support


class Room(object):
    def __init__(self, desc):
        self.desc = desc
        self.inv = []
        self.gameOver = False
        self.doors = [None, None, None, None]

    def __getattr__(self, attr):
        return \
            {
                "n": self.doors[0],
                "s": self.doors[1],
                "e": self.doors[2],
                "w": self.doors[3],
            }[attr]

    def enter(self, player):
        if self.gameOver:
            player.gameOver = True

    def addItem(self, it):
        self.inv.append(it)

    def removeItem(self, it):
        self.inv.remove(it)

    def describe(self):
        visibleItems = [it for it in self.inv if it.isVisible]
        print(
            self.desc,
            visibleItems)
        if len(visibleItems) > 1:
            print(
                "There are %s here." % Support.enumerateItems(visibleItems))
        else:
            print(
                "There is %s here." % Support.enumerateItems(visibleItems))
