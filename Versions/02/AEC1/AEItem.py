

class Item(object):
    items = dict()

    def __init__(self, desc):
        self.desc = desc
        self.isDeadly = False
        self.isFragile = False
        self.isBroken = False
        self.isTakeable = True
        self.isVisible = True
        self.isOpenable = False
        self.useAction = None
        self.usableConditionTest = None
        Item.items[desc] = self

    def __str__(self):
        return self.desc

    def breakItem(self):
        if not self.isBroken:
            resp = self.desc = "broken " + self.desc
            print(
                "<Crash!>",
                resp)
            self.isBroken = True

    def isUsable(self, player, target):
        if self.usableConditionTest:
            return self.usableConditionTest(player, target)
        else:
            return False

    def useItem(self, player, target):
        if self.useAction:
            self.useAction(player, self, target)


class OpenableItem(Item):
    def __init__(self, desc, contents=None):
        super(OpenableItem, self).__init__(desc)
        self.isOpenable = True
        self.isOpened = False
        self.contents = contents

    def openItem(self, player):
        if not self.isOpened:
            self.isOpened = True
            self.isOpenable = False
            if self.contents is not None:
                player.room.addItem(self.contents)
            self.desc = "open " + self.desc