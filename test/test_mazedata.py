import unittest
from unittest.mock import MagicMock
from CheeseChase.model.mazedata import MazeBase, Maze1, Maze2, MazeData
from CheeseChase.model.constants import UP, DOWN, LEFT, RIGHT

class TestMazeBase(unittest.TestCase):
    def setUp(self):
        self.base = MazeBase()

    def test_initialization(self):
        self.assertEqual(self.base.portalPairs, {})
        self.assertEqual(self.base.homeoffset, (0, 0))
        self.assertEqual(self.base.catNodeDeny, {UP:(), DOWN:(), LEFT:(), RIGHT:()})  # No cat restrictions initially

    def test_setPortalPairs_calls_nodes_setPortalPair(self):
        self.base.portalPairs = {0: ((1,2),(3,4)), 1: ((5,6),(7,8))}
        nodes = MagicMock()
        self.base.setPortalPairs(nodes)
        nodes.setPortalPair.assert_any_call((1,2),(3,4))
        nodes.setPortalPair.assert_any_call((5,6),(7,8))
        self.assertEqual(nodes.setPortalPair.call_count, 2) # Exactly two calls

    def test_connectHomeNodes_calls_nodes_methods(self):
        nodes = MagicMock()
        self.base.homeoffset = (1, 2)
        self.base.homenodeconnectLeft = (3, 4)
        self.base.homenodeconnectRight = (5, 6)
        nodes.createHomeNodes.return_value = "key"
        self.base.connectHomeNodes(nodes)
        nodes.createHomeNodes.assert_called_once_with(1, 2)
        # Ensure home key is connected to left and right nodes
        nodes.connectHomeNodes.assert_any_call("key", (3, 4), LEFT)
        nodes.connectHomeNodes.assert_any_call("key", (5, 6), RIGHT)

    def test_addOffset(self):
        self.base.homeoffset = (5, 6)
        self.assertEqual(self.base.addOffset(2, 3), (7, 9))

    def test_denyCatsAccess_denies_access(self):
        # Test that cat access is denied at specified nodes
        nodes = MagicMock()
        cats = MagicMock()
        self.base.homeoffset = (1, 2)
        self.base.catNodeDeny = {UP:((7, 8),), LEFT:((3, 4),), RIGHT:((9, 10),)}
        # Should call denyAccessList for offsets
        self.base.denyCatsAccess(cats, nodes)
        # Check offset calls
        nodes.denyAccessList.assert_any_call(3, 4, LEFT, cats)
        nodes.denyAccessList.assert_any_call(3, 5, RIGHT, cats)
        # Check direction calls
        nodes.denyAccessList.assert_any_call(7, 8, UP, cats)
        nodes.denyAccessList.assert_any_call(3, 4, LEFT, cats)
        nodes.denyAccessList.assert_any_call(9, 10, RIGHT, cats)

class TestMaze1(unittest.TestCase):
    def setUp(self):
        self.m1 = Maze1()

    def test_maze1_initialization(self):
        self.assertEqual(self.m1.name, "maze1")
        self.assertEqual(self.m1.portalPairs, {0: ((0, 17), (27, 17))})
        self.assertEqual(self.m1.homeoffset, (11.5, 14))
        self.assertEqual(self.m1.homenodeconnectLeft, (12, 14))
        self.assertEqual(self.m1.homenodeconnectRight, (15, 14))
        self.assertEqual(self.m1.mouseStart, (15, 26))
        # Check catNodeDeny keys
        self.assertSetEqual(set(self.m1.catNodeDeny.keys()), {UP, LEFT, RIGHT})

class TestMaze2(unittest.TestCase):
    def setUp(self):
        self.m2 = Maze2()

    def test_maze2_initialization(self):
        self.assertEqual(self.m2.name, "maze2")
        self.assertEqual(self.m2.portalPairs, {0: ((0, 4), (27, 4)), 1: ((0, 26), (27, 26))})
        self.assertEqual(self.m2.homeoffset, (11.5, 14))
        self.assertEqual(self.m2.homenodeconnectLeft, (9, 14))
        self.assertEqual(self.m2.homenodeconnectRight, (18, 14))
        self.assertEqual(self.m2.mouseStart, (16, 26))
        self.assertSetEqual(set(self.m2.catNodeDeny.keys()), {UP, LEFT, RIGHT})

class TestMazeData(unittest.TestCase):
    def setUp(self):
        self.md = MazeData()

    def test_maze_data_initialization(self):
        self.assertIsNone(self.md.obj)
        self.assertSetEqual(set(self.md.mazedict.keys()), {0, 1})
        self.assertIs(self.md.mazedict[0], Maze1)
        self.assertIs(self.md.mazedict[1], Maze2)

    def test_loadMaze_sets_obj_to_maze_instance(self):
        # Loading maze 0 should create Maze1 instance
        self.md.loadMaze(0)
        self.assertIsInstance(self.md.obj, Maze1)
        # Loading maze 1 should create Maze2 instance
        self.md.loadMaze(1)
        self.assertIsInstance(self.md.obj, Maze2)
        # Loading higher indices should wrap around
        self.md.loadMaze(2)
        self.assertIsInstance(self.md.obj, Maze1)
        self.md.loadMaze(3)
        self.assertIsInstance(self.md.obj, Maze2)
