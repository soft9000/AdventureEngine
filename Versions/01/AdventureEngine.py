# Permission granted by author, Paul McGuire, for re-use. 
# See Ideas.txt for same, as well as an impressive list of
# improvement suggestions.
# ------
# Source:
# https://stackoverflow.com/questions/1547782/mini-languages-in-python
# (Python 2 Source: http://www.ptmcg.com/geo/python/confs/adventureEngine.py.txt)
# ------
# Status:
# NOJ: Converted to Python 3
# NOJ: Replacing pyparsing - not working the same way under 3.
# NOJ: Status - Got 'help' dumbed-up just to get things started. 
# TODO: Need to implement command parsing, for real.

import random

def aOrAn(item):
    if item.desc[0] in "aeiou":
        return "an"
    else:
        return "a"


def enumerateItems(l):
    if len(l) == 0: return "nothing"
    out = []
    for item in l:
        if len(l) > 1 and item == l[-1]:
            out.append("and")
        out.append(aOrAn(item))
        if item == l[-1]:
            out.append(item.desc)
        else:
            if len(l) > 2:
                out.append(item.desc + ",")
            else:
                out.append(item.desc)
    return " ".join(out)


def enumerateDoors(l):
    if len(l) == 0: return ""
    out = []
    for item in l:
        if len(l) > 1 and item == l[-1]:
            out.append("and")
        if item == l[-1]:
            out.append(item)
        else:
            if len(l) > 2:
                out.append(item + ",")
            else:
                out.append(item)
    return " ".join(out)


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
            "There are %s here." % enumerateItems(visibleItems))
        else:
            print(
            "There is %s here." % enumerateItems(visibleItems))


class Exit(Room):
    def __init__(self):
        super(Exit, self).__init__("")

    def enter(self, player):
        player.gameOver = True


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


class Command(object):
    "Base class for commands"

    def __init__(self, verb, *verbProg):
        self.verb = verb
        self.verbProg = verbProg

    def _canParse(self, cmdstr):
        return False

    def helpDescription(self):
        return "Command: No help."

    def _doCommand(self, player):
        pass

    def __call__(self, player):
        print(
        self.verbProg.capitalize() + "...",
        self._doCommand(player))


class MoveCommand(Command):
    def __init__(self, quals):
        super(MoveCommand, self).__init__(quals, "moving")
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


class TakeCommand(Command):
    def __init__(self, quals):
        super(TakeCommand, self).__init__(quals, "taking")

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


class DropCommand(Command):
    def __init__(self, quals):
        super(DropCommand, self).__init__(quals, "dropping")

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
            "You don't have %s %s." % (aOrAn(subj), subj))


class InventoryCommand(Command):
    def __init__(self, quals):
        super(InventoryCommand, self).__init__(quals, "taking inventory")

    def _canParse(self, cmdstr):
        return False

    def helpDescription(self):
        return "INVENTORY or INV or I - lists what items you have"

    def _doCommand(self, player):
        print(
        "You have %s." % enumerateItems(player.inv))


class LookCommand(Command):
    def __init__(self, quals):
        super(LookCommand, self).__init__(quals, "looking")

    def _canParse(self, cmdstr):
        return False

    def helpDescription(self):
        return "LOOK or L - describes the current room and any objects in it"

    def _doCommand(self, player):
        player.room.describe()


class DoorsCommand(Command):
    def __init__(self, quals):
        super(DoorsCommand, self).__init__(quals, "looking for doors")

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
            reply += enumerateDoors(doorNames)
            reply += "."
            print(reply)


class UseCommand(Command):
    def __init__(self, quals):
        super(UseCommand, self).__init__(quals, "using")
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


class OpenCommand(Command):
    def __init__(self, quals):
        super(OpenCommand, self).__init__(quals, "opening")

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


class QuitCommand(Command):
    def __init__(self, quals):
        super(QuitCommand, self).__init__(quals, "quitting")

    def _canParse(self, cmdstr):
        return False

    def helpDescription(self):
        return "QUIT or Q - ends the game"

    def _doCommand(self, player):
        print(
        "Ok....")
        player.gameOver = True


class HelpCommand(Command):
    def __init__(self, quals):
        super(HelpCommand, self).__init__(quals, "helping")

    def _canParse(self, cmdstr):
        return True

    def helpDescription(self):
        return "HELP or H or ? - displays this help message"

    def _doCommand(self, player):
        print(
        "Enter any of the following commands (not case sensitive):")
        for cmd in [
            InventoryCommand(None),
            DropCommand(None),
            TakeCommand(None),
            UseCommand(None),
            OpenCommand(None),
            MoveCommand(None),
            LookCommand(None),
            DoorsCommand(None),
            QuitCommand(None),
            HelpCommand(None),
        ]:
            print(
            "  - %s" % cmd.helpDescription())
        print()


class Parser(object):
    def __init__(self):
        self.cmds = (
            HelpCommand(("?", "H", "HELP")),
            InventoryCommand(('I', "INV", "INVENTORY")),
            DropCommand(('D', "DROP", "LEAVE")),
            TakeCommand(('T', "TAKE", "PICKUP", "PICK", "UP")),
            UseCommand(('U', "USE")),
            OpenCommand(('O' "OPEN")),
            QuitCommand(('Q',"QUIT")),
            LookCommand(('L', "LOOK")),
            DoorsCommand(('X', "DOORS")),
            MoveCommand(('G', "GO", "MOVE")),
            MoveCommand(("N", "NORTH")),
            MoveCommand(("S", "SOUTH")),
            MoveCommand(("E", "EAST")),
            MoveCommand(("W", "WEST"))
        )
        

    def makeCommandParseAction(self, cls):
        def cmdParseAction(s, l, tokens):
            return cls(tokens)
        return cmdParseAction


    def validateItemName(self, s, l, t):
        iname = " ".join(t)
        if iname not in Item.items:
            raise AppParseException(s, l, "No such item '%s'." % iname)
        return iname

    def parseCmd(self, cmdstr):
        for cmd in self.cmds:
            if cmd._canParse(cmdstr) is True:
                return cmd
        result = random.choice(["Sorry, I don't understand that.",
                           "Huh?",
                           "Excuse me?",
                           "???",
                           "What?"])
        print(result)



class Player(object):
    def __init__(self, name):
        self.name = name
        self.gameOver = False
        self.inv = []

    def moveTo(self, rm):
        self.room = rm
        rm.enter(self)
        if self.gameOver:
            if rm.desc:
                rm.describe()
            print(
            "Game over!")
        else:
            rm.describe()

    def take(self, it):
        if it.isDeadly:
            print(
            "Aaaagh!...., the %s killed me!" % it)
            self.gameOver = True
        else:
            self.inv.append(it)

    def drop(self, it):
        self.inv.remove(it)
        if it.isFragile:
            it.breakItem()


def createRooms(rm):
    """
    create rooms, using multiline string showing map layout
    string contains symbols for the following:
     A-Z, a-z indicate rooms, and rooms will be stored in a dictionary by 
               reference letter
     -, | symbols indicate connection between rooms
     <, >, ^, . symbols indicate one-way connection between rooms
    """
    # start with empty dictionary of rooms
    ret = {}

    # look for room symbols, and initialize dictionary 
    # - exit room is always marked 'Z'
    for c in rm:
        if "A" <= c <= "Z" or "a" <= c <= "z":
            if c != "Z":
                ret[c] = Room(c)
            else:
                ret[c] = Exit()

    # scan through input string looking for connections between rooms
    rows = rm.split("\n")
    for row, line in enumerate(rows):
        for col, c in enumerate(line):
            if "A" <= c <= "Z" or "a" <= c <= "z":
                room = ret[c]
                n = None
                s = None
                e = None
                w = None

                # look in neighboring cells for connection symbols (must take
                # care to guard that neighboring cells exist before testing 
                # contents)
                if col > 0 and line[col - 1] in "<-":
                    other = line[col - 2]
                    w = ret[other]
                if col < len(line) - 1 and line[col + 1] in "->":
                    other = line[col + 2]
                    e = ret[other]
                if row > 1 and col < len(rows[row - 1]) and rows[row - 1][col] in '|^':
                    other = rows[row - 2][col]
                    n = ret[other]
                if row < len(rows) - 1 and col < len(rows[row + 1]) and rows[row + 1][col] in '|.':
                    other = rows[row + 2][col]
                    s = ret[other]

                # set connections to neighboring rooms
                room.doors = [n, s, e, w]

    return ret


# put items in rooms
def putItemInRoom(i, r):
    if isinstance(r, str):
        r = rooms[r]
    r.addItem(Item.items[i])


def playGame(p, startRoom):
    # create parser
    parser = Parser()
    p.moveTo(startRoom)
    while not p.gameOver:
        cmdstr = input(">> ")
        cmd = parser.parseCmd(cmdstr)
        if cmd is not None:
            cmd._doCommand(p)
    print()
    print(
    "You ended the game with:")
    for i in p.inv:
        print(
        " -", aOrAn(i), i)


# ====================
# start game definition
roomMap = """
     d-Z
     |
   f-c-e
   . |
   q<b
     |
     A
"""
rooms = createRooms(roomMap)
rooms["A"].desc = "You are standing at the front door."
rooms["b"].desc = "You are in a garden."
rooms["c"].desc = "You are in a kitchen."
rooms["d"].desc = "You are on the back porch."
rooms["e"].desc = "You are in a library."
rooms["f"].desc = "You are on the patio."
rooms["q"].desc = "You are sinking in quicksand.  You're dead..."
rooms["q"].gameOver = True

# define global variables for referencing rooms
frontPorch = rooms["A"]
garden = rooms["b"]
kitchen = rooms["c"]
backPorch = rooms["d"]
library = rooms["e"]
patio = rooms["f"]

# create items
itemNames = """sword.diamond.apple.flower.coin.shovel.book.mirror.telescope.gold bar""".split(".")
for itemName in itemNames:
    Item(itemName)
Item.items["apple"].isDeadly = True
Item.items["mirror"].isFragile = True
Item.items["coin"].isVisible = False
Item.items["shovel"].usableConditionTest = (lambda p, t: p.room is garden)


def useShovel(p, subj, target):
    coin = Item.items["coin"]
    if not coin.isVisible and coin in p.room.inv:
        coin.isVisible = True


Item.items["shovel"].useAction = useShovel

Item.items["telescope"].isTakeable = False


def useTelescope(p, subj, target):
    print(
    "You don't see anything.")


Item.items["telescope"].useAction = useTelescope

OpenableItem("treasure chest", Item.items["gold bar"])

putItemInRoom("shovel", frontPorch)
putItemInRoom("coin", garden)
putItemInRoom("flower", garden)
putItemInRoom("apple", library)
putItemInRoom("mirror", library)
putItemInRoom("telescope", library)
putItemInRoom("book", kitchen)
putItemInRoom("diamond", backPorch)
putItemInRoom("treasure chest", patio)

# create player
plyr = Player("Bob")
plyr.take(Item.items["sword"])

# start game
playGame(plyr, frontPorch)
