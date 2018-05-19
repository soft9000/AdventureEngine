

class Support:
    @staticmethod
    def aOrAn(item):
        if item.desc[0] in "aeiou":
            return "an"
        else:
            return "a"

    @staticmethod
    def enumerateItems(l):
        if len(l) == 0: return "nothing"
        out = []
        for item in l:
            if len(l) > 1 and item == l[-1]:
                out.append("and")
            out.append(Support.aOrAn(item))
            if item == l[-1]:
                out.append(item.desc)
            else:
                if len(l) > 2:
                    out.append(item.desc + ",")
                else:
                    out.append(item.desc)
        return " ".join(out)


    @staticmethod
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
