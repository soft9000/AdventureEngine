
class AbsCommand(object):
    "Base class for commands"

    def __init__(self, a_list, state=None):
        self.state = state
        self.verb = None
        self.verbProg = a_list

        if a_list is not None:
            self.verb = a_list[0]

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