
from AEC1.AECommand import AbsCommand
from AEC1.AEItem import Item
from AEC1.AESupport import Support


class MoveCommand(AbsCommand):
    def __init__(self, quals):
        super().__init__(quals, state="moving")
        self.direction = quals

    def _canParse(self, cmdstr):
        return False

    def helpDescription(self):
        return """MOVE or GO - go NORTH, SOUTH, EAST, or WEST 
          (can abbreviate as 'GO N' and 'GO W', or even just 'E' and 'S')"""

    def _doCommand(self, player):
        rm = player.room
        nextRoom = rm.doors[
            {
                "N": 0,
                "S": 1,
                "E": 2,
                "W": 3,
            }[self.direction]
        ]
        if nextRoom:
            player.moveTo(nextRoom)
        else:
            print(
                "Can't go that way.")


class TakeCommand(AbsCommand):
    def __init__(self, quals):
        super().__init__(quals, state="taking")

    def _canParse(self, cmdstr):
        return False

    def helpDescription(self):
        return "TAKE or PICKUP or PICK UP - pick up an object (but some are deadly)"

    def _doCommand(self, player):
        rm = player.room
        subj = Item.items[self.subject]
        if subj in rm.inv and subj.isVisible:
            if subj.isTakeable:
                rm.removeItem(subj)
                player.take(subj)
                return subj
            else:
                print(
                    "You can't take that!")
        else:
            print(
                "There is no %s here." % subj)


class DropCommand(AbsCommand):
    def __init__(self, quals):
        super().__init__(quals, state="dropping")

    def _canParse(self, cmdstr):
        return False

    def helpDescription(self):
        return "DROP or LEAVE - drop an object (but fragile items may break)"

    def _doCommand(self, player):
        rm = player.room
        subj = Item.items[self.subject]
        if subj in player.inv:
            rm.addItem(subj)
            player.drop(subj)
        else:
            print(
                "You don't have %s %s." % (Support.aOrAn(subj), subj))


class InventoryCommand(AbsCommand):
    def __init__(self, quals):
        super().__init__(quals, state="taking inventory")

    def _canParse(self, cmdstr):
        return False

    def helpDescription(self):
        return "INVENTORY or INV or I - lists what items you have"

    def _doCommand(self, player):
        print(
            "You have %s." % Support.enumerateItems(player.inv))


class LookCommand(AbsCommand):
    def __init__(self, quals):
        super().__init__(quals, state="looking")

    def _canParse(self, cmdstr):
        return False

    def helpDescription(self):
        return "LOOK or L - describes the current room and any objects in it"

    def _doCommand(self, player):
        player.room.describe()


class DoorsCommand(AbsCommand):
    def __init__(self, quals):
        super().__init__(quals, state="looking for doors")

    def _canParse(self, cmdstr):
        return False

    def helpDescription(self):
        return "DOORS - display what doors are visible from this room"

    def _doCommand(self, player):
        rm = player.room
        numDoors = sum([1 for r in rm.doors if r is not None])
        if numDoors == 0:
            reply = "There are no doors in any direction."
        else:
            if numDoors == 1:
                reply = "There is a door to the "
            else:
                reply = "There are doors to the "
            doorNames = [{0: "north", 1: "south", 2: "east", 3: "west"}[i]
                         for i, d in enumerate(rm.doors) if d is not None]
            # ~ print doorNames
            reply += Support.enumerateDoors(doorNames)
            reply += "."
            print(reply)


class UseCommand(AbsCommand):
    def __init__(self, quals):
        super().__init__(quals, state="using")
        # self.target = Item.items[quals["targetObj"]]
        self.target = None

    def _canParse(self, cmdstr):
        return False

    def helpDescription(self):
        return "USE or U - use an object, optionally IN or ON another object"

    def _doCommand(self, player):
        rm = player.room
        availItems = rm.inv + player.inv
        if self.subject in availItems:
            if self.subject.isUsable(player, self.target):
                self.subject.useItem(player, self.target)
            else:
                print(
                    "You can't use that here.")
        else:
            print(
                "There is no %s here to use." % self.subject)


class OpenCommand(AbsCommand):
    def __init__(self, quals):
        super().__init__(quals, state="opening")

    def _canParse(self, cmdstr):
        return False

    def helpDescription(self):
        return "OPEN or O - open an object"

    def _doCommand(self, player):
        rm = player.room
        availItems = rm.inv + player.inv
        if self.subject in availItems:
            if self.subject.isOpenable:
                self.subject.openItem(player)
            else:
                print(
                    "You can't use that here.")
        else:
            print(
                "There is no %s here to use." % self.subject)


class QuitCommand(AbsCommand):
    def __init__(self, quals):
        super().__init__(quals, state="quitting")

    def _canParse(self, cmdstr):
        return False

    def helpDescription(self):
        return "QUIT or Q - ends the game"

    def _doCommand(self, player):
        print(
            "Ok....")
        player.gameOver = True


class HelpCommand(AbsCommand):
    def __init__(self, quals):
        super().__init__(quals, state="helping")

    def _canParse(self, cmdstr):
        return True

    def helpDescription(self):
        return "HELP or H or ? - displays this help message"

    def _doCommand(self, player):
        from AEC1.AEParser import Parser
        print(
            "Enter any of the following commands (not case sensitive):")
        for cmd in Parser.cmds:
            print(
                "  - %s" % cmd.helpDescription())
        print()
