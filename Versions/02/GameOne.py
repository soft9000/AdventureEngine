from AEC1.AERoom import Room
from AEC1.AEExit import Exit
from AEC1.AEItem import Item


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


def playGame(p, startRoom, parser):
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
            " -", Support.Support.aOrAn(i), i)


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


from GameOneCommands import *

from AEC1.AEParser import Parser
parser = Parser()

parser.addCommands((
    HelpCommand(("?", "H", "HELP")),
    InventoryCommand(('I', "INV", "INVENTORY")),
    DropCommand(('D', "DROP", "LEAVE")),
    TakeCommand(('T', "TAKE", "PICKUP", "PICK", "UP")),
    UseCommand(('U', "USE")),
    OpenCommand(('O' "OPEN")),
    QuitCommand(('Q', "QUIT")),
    LookCommand(('L', "LOOK")),
    DoorsCommand(('X', "DOORS")),
    MoveCommand(('G', "GO", "MOVE")),
    MoveCommand(("N", "NORTH")),
    MoveCommand(("S", "SOUTH")),
    MoveCommand(("E", "EAST")),
    MoveCommand(("W", "WEST"))
))


if __name__ == "__main__":
    from AEC1.AEItem import Item
    from AEC1.AEItem import OpenableItem
    from AEC1.AEPlayer import Player

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
    playGame(plyr, frontPorch, parser)
