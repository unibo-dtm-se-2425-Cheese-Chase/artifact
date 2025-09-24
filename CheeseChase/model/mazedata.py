from .constants import *

class MazeBase(object):
    def __init__(self):
        self.portalPairs = {}
        self.homeoffset = (0, 0)
        self.catNodeDeny = {UP:(), DOWN:(), LEFT:(), RIGHT:()}

    def setPortalPairs(self, nodes):
        for pair in list(self.portalPairs.values()):
            nodes.setPortalPair(*pair)

    def connectHomeNodes(self, nodes):
        key = nodes.createHomeNodes(*self.homeoffset)
        nodes.connectHomeNodes(key, self.homenodeconnectLeft, LEFT)
        nodes.connectHomeNodes(key, self.homenodeconnectRight, RIGHT)

    def addOffset(self, x, y):
        return x+self.homeoffset[0], y+self.homeoffset[1]

    def denyCatsAccess(self, cats, nodes):
        nodes.denyAccessList(*(self.addOffset(2, 3) + (LEFT, cats)))
        nodes.denyAccessList(*(self.addOffset(2, 3) + (RIGHT, cats)))

        for direction in list(self.catNodeDeny.keys()):
            for values in self.catNodeDeny[direction]:
                nodes.denyAccessList(*(values + (direction, cats)))


class Maze1(MazeBase):
    def __init__(self):
        MazeBase.__init__(self)
        self.name = "maze1"
        self.portalPairs = {0:((0, 17), (27, 17))}
        self.homeoffset = (11.5, 14)
        self.homenodeconnectLeft = (12, 14)
        self.homenodeconnectRight = (15, 14)
        self.mouseStart = (15, 26)
        self.catNodeDeny = {UP:((12, 14), (15, 14), (12, 26), (15, 26)), LEFT:(self.addOffset(2, 3),),
                              RIGHT:(self.addOffset(2, 3),)}


class Maze2(MazeBase):
    def __init__(self):
        MazeBase.__init__(self)
        self.name = "maze2"
        self.portalPairs = {0:((0, 4), (27, 4)), 1:((0, 26), (27, 26))}
        self.homeoffset = (11.5, 14)
        self.homenodeconnectLeft = (9, 14)
        self.homenodeconnectRight = (18, 14)
        self.mouseStart = (16, 26)
        self.catNodeDeny = {UP:((9, 14), (18, 14), (11, 23), (16, 23)), LEFT:(self.addOffset(2, 3),),
                              RIGHT:(self.addOffset(2, 3),)}


class MazeData(object):
    def __init__(self):
        self.obj = None
        self.mazedict = {0:Maze1, 1:Maze2}

    def loadMaze(self, level):
        self.obj = self.mazedict[level%len(self.mazedict)]()
