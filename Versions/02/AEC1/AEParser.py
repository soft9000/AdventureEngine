from AEC1.AECommand import AbsCommand
from AEC1.AEItem import Item

import random


class Parser(object):
    cmds = None

    def __init__(self):
        Parser.cmds = list()

    def _addCommand(self, cmd):
        if isinstance(cmd, AbsCommand) is False:
            return False
        Parser.cmds.append(cmd)
        return True

    def addCommands(self, cmds):
        for cmd in cmds:
            if self._addCommand(cmd) is False:
                return False
        return True

    def makeCommandParseAction(self, cls):
        def cmdParseAction(s, l, tokens):
            return cls(tokens)
        return cmdParseAction

    def validateItemName(self, s, l, t):
        iname = " ".join(t)
        if iname not in Item.Item.items:
            return None
        return iname

    def parseCmd(self, cmdstr):
        for cmd in Parser.cmds:
            if cmd._canParse(cmdstr) is True:
                return cmd
        result = random.choice(["Sorry, I don't understand that.",
                                "Huh?",
                                "Excuse me?",
                                "???",
                                "What?"])
        print(result)
