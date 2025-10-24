import unittest
from unittest.mock import MagicMock, patch
import numpy as np

from CheeseChase.model.nodes import Node, NodeGroup
from CheeseChase.model.constants import UP, DOWN, LEFT, RIGHT, PORTAL, TILEWIDTH, TILEHEIGHT, MOUSE, CAT1, CAT2, CAT3, CAT4, WHITE, RED

class TestNode(unittest.TestCase):
    def setUp(self):
        self.node = Node(5, 10)
        self.mock_entity = MagicMock()
        self.mock_entity.name = CAT1

    def test_initialization_sets_position_and_neighbors(self):
        # Check that node position is set correctly
        self.assertEqual(self.node.position.x, 5)
        self.assertEqual(self.node.position.y, 10)
        # Ensure neighbors dictionary has all expected directions
        self.assertSetEqual(set(self.node.neighbors.keys()), {UP, DOWN, LEFT, RIGHT, PORTAL})
        # Check initial access lists contain expected entities
        self.assertIn(CAT1, self.node.access[UP])
        self.assertIn(MOUSE, self.node.access[DOWN])

    def test_denyAccess_removes_entity_name(self):
        self.node.access[UP] = [CAT1, CAT2]
        self.node.denyAccess(UP, self.mock_entity)
        self.assertNotIn(CAT1, self.node.access[UP]) # CAT1 should be removed

    def test_allowAccess_adds_entity_name(self):
        self.node.access[UP] = [CAT2]
        self.node.allowAccess(UP, self.mock_entity)
        self.assertIn(CAT1, self.node.access[UP]) # CAT1 should now be added

    @patch("CheeseChase.model.nodes.pygame.draw")
    def test_render_draws_lines_and_circles(self, mock_draw):
        screen = MagicMock()
        neighbor = Node(20, 30)
        self.node.neighbors[RIGHT] = neighbor
        # Mock position methods to return fixed coordinates
        self.node.position.asTuple = MagicMock(return_value=(5, 10))
        neighbor.position.asTuple = MagicMock(return_value=(20, 30))
        self.node.position.asInt = MagicMock(return_value=(5, 10))
        self.node.render(screen)
        # Ensure draw.line and draw.circle are called with expected parameters
        mock_draw.line.assert_called_with(screen, WHITE, (5, 10), (20, 30), 4)
        mock_draw.circle.assert_called_with(screen, RED, (5, 10), 12)

class TestNodeGroup(unittest.TestCase):
    def setUp(self):
        # Patch np.loadtxt so we don't need a real file
        self.data = np.array([
            ['+', '.', '+'],
            ['.', '.', '.'],
            ['+', '.', '+']
        ])
        patcher = patch("CheeseChase.model.nodes.np.loadtxt", return_value=self.data)
        self.mock_loadtxt = patcher.start()
        self.addCleanup(patcher.stop)
        self.level = "dummyfile.txt"
        self.ng = NodeGroup(self.level)

    def test_initialization_creates_nodesLUT(self):
        # Should create nodes for every '+'
        expected_nodes = [
            (0 * TILEWIDTH, 0 * TILEHEIGHT),
            (2 * TILEWIDTH, 0 * TILEHEIGHT),
            (0 * TILEWIDTH, 2 * TILEHEIGHT),
            (2 * TILEWIDTH, 2 * TILEHEIGHT)
        ]
        for key in expected_nodes:
            self.assertIn(key, self.ng.nodesLUT)
            self.assertIsInstance(self.ng.nodesLUT[key], Node)

    def test_createNodeTable_adds_nodes(self):
        ng = NodeGroup(self.level)
        ng.nodesLUT.clear()
        ng.createNodeTable(self.data)
        expected_count = np.count_nonzero(self.data == '+')
        self.assertEqual(len(ng.nodesLUT), expected_count) # Ensure correct number of nodes

    def test_constructKey_returns_pixel_coordinates(self):
        self.assertEqual(self.ng.constructKey(5, 3), (5 * TILEWIDTH, 3 * TILEHEIGHT))

    def test_connectHorizontally_and_connectVertically(self):
        # After initialization, check some neighbors
        key1 = self.ng.constructKey(0, 0)
        key2 = self.ng.constructKey(2, 0)
        # Should be connected horizontally
        self.assertIs(self.ng.nodesLUT[key1].neighbors[RIGHT], self.ng.nodesLUT[key2])
        self.assertIs(self.ng.nodesLUT[key2].neighbors[LEFT], self.ng.nodesLUT[key1])
        # Vertically
        key3 = self.ng.constructKey(0, 2)
        self.assertIs(self.ng.nodesLUT[key1].neighbors[DOWN], self.ng.nodesLUT[key3])
        self.assertIs(self.ng.nodesLUT[key3].neighbors[UP], self.ng.nodesLUT[key1])

    def test_getStartTempNode_returns_first_node(self):
        node = self.ng.getStartTempNode()
        self.assertIsInstance(node, Node)
        self.assertIn(node, self.ng.nodesLUT.values())

    def test_setPortalPair_sets_neighbors(self):
        # Ensure portal connections are set correctly
        pair1 = (0, 0)
        pair2 = (2, 2)
        self.ng.setPortalPair(pair1, pair2)
        key1 = self.ng.constructKey(*pair1)
        key2 = self.ng.constructKey(*pair2)
        self.assertIs(self.ng.nodesLUT[key1].neighbors[PORTAL], self.ng.nodesLUT[key2])
        self.assertIs(self.ng.nodesLUT[key2].neighbors[PORTAL], self.ng.nodesLUT[key1])

    def test_createHomeNodes_and_connectHomeNodes(self):
        homekey = self.ng.createHomeNodes(1, 2)
        valid_otherkey = None
        for key in self.ng.nodesLUT.keys():
            if key != homekey:
                valid_otherkey = (key[0] // TILEWIDTH, key[1] // TILEHEIGHT)
                break

        direction = LEFT
        self.ng.connectHomeNodes(homekey, valid_otherkey, direction)
        k_other = self.ng.constructKey(*valid_otherkey)
        self.assertIs(self.ng.nodesLUT[homekey].neighbors[direction], self.ng.nodesLUT[k_other])
        self.assertIs(self.ng.nodesLUT[k_other].neighbors[direction*-1], self.ng.nodesLUT[homekey])

    def test_getNodeFromPixels_and_getNodeFromTiles(self):
        # Use a known node
        key = self.ng.constructKey(0, 0)
        node = self.ng.getNodeFromPixels(*key)
        self.assertIs(node, self.ng.nodesLUT[key])
        node2 = self.ng.getNodeFromTiles(0, 0)
        self.assertIs(node2, self.ng.nodesLUT[key])
        # Non-existent node returns None
        self.assertIsNone(self.ng.getNodeFromPixels(999, 999))
        self.assertIsNone(self.ng.getNodeFromTiles(999, 999))

    def test_denyAccess_and_allowAccess(self):
        key = self.ng.constructKey(0, 0)
        node = self.ng.nodesLUT[key]
        entity = MagicMock()
        entity.name = CAT4
        node.access[UP].append("TEST")
        self.ng.denyAccess(0, 0, UP, entity) # Should remove CAT4 if present
        self.ng.allowAccess(0, 0, UP, entity) # Should add CAT4 back
        self.assertIn(CAT4, node.access[UP])

    def test_denyAccessList_and_allowAccessList(self):
        # Test batch deny/allow access for multiple entities
        key = self.ng.constructKey(0, 0)
        node = self.ng.nodesLUT[key]
        entities = [MagicMock(name=CAT2), MagicMock(name=CAT3)]
        # Add entities to access
        for e in entities:
            node.access[UP].append(e.name)
        self.ng.denyAccessList(0, 0, UP, entities)
        for e in entities:
            self.assertNotIn(e.name, node.access[UP])
        # Test allowAccessList
        self.ng.allowAccessList(0, 0, UP, entities)
        for e in entities:
            self.assertIn(e.name, node.access[UP])

    def test_denyHomeAccess_and_allowHomeAccess(self):
        # Test denying/allowing access to home nodes for a single entity
        homekey = self.ng.createHomeNodes(1, 1)
        entity = MagicMock()
        entity.name = CAT1
        node = self.ng.nodesLUT[homekey]
        node.access[DOWN] = [CAT1]
        self.ng.denyHomeAccess(entity)
        self.assertNotIn(CAT1, node.access[DOWN])
        self.ng.allowHomeAccess(entity)
        self.assertIn(CAT1, node.access[DOWN])

    def test_denyHomeAccessList_and_allowHomeAccessList(self):
        # Test denying/allowing access for multiple entities on home nodes
        homekey = self.ng.createHomeNodes(2, 2)
        node = self.ng.nodesLUT[homekey]
        entities = [MagicMock(name=CAT1), MagicMock(name=CAT2)]
        node.access[DOWN] = [CAT1, CAT2]
        self.ng.denyHomeAccessList(entities)
        for e in entities:
            self.assertNotIn(e.name, node.access[DOWN])
        self.ng.allowHomeAccessList(entities)
        for e in entities:
            self.assertIn(e.name, node.access[DOWN])

    @patch("CheeseChase.model.nodes.Node.render")
    def test_render_calls_render_on_all_nodes(self, mock_render):
        # Ensure NodeGroup calls render() on all nodes
        screen = MagicMock()
        self.ng.render(screen)
        self.assertEqual(mock_render.call_count, len(self.ng.nodesLUT))
