import unittest
from unittest.mock import MagicMock, patch
from CheeseChase.model.entity import Entity
from CheeseChase.model.constants import UP, DOWN, LEFT, RIGHT, STOP, TILEWIDTH
from CheeseChase.model.vector import Vector2

class TestEntity(unittest.TestCase):

    def setUp(self):
        """Create a mock node and an Entity instance for testing."""
        self.node = MagicMock()
        self.node.position = Vector2(0, 0)
        # Mock neighbors dictionary for navigation tests
        self.node.neighbors = {UP: None, DOWN: None, LEFT: None, RIGHT: None, 'PORTAL': None}
        # Mock access dictionary (who can pass in which direction)
        self.node.access = {UP: [], DOWN: [], LEFT: [], RIGHT: []}
        self.entity = Entity(self.node)

    # ------------------------------------------------------------
    # 1. Constructor & setStartNode
    # ------------------------------------------------------------
    def test_initialization_sets_basic_attributes(self):
        """Entity should initialize with expected default attributes."""
        self.assertEqual(self.entity.direction, STOP)
        self.assertTrue(hasattr(self.entity, "speed"))
        self.assertTrue(hasattr(self.entity, "node"))
        self.assertTrue(hasattr(self.entity, "target"))
        self.assertEqual(self.entity.node, self.node)

    # ------------------------------------------------------------
    # 2. setSpeed()
    # ------------------------------------------------------------
    def test_setSpeed_converts_value_correctly(self):
        """setSpeed() should convert input speed to scaled internal speed."""
        base_speed = 100
        self.entity.setSpeed(base_speed)
        expected = base_speed * TILEWIDTH / 16
        self.assertEqual(self.entity.speed, expected)

    # ------------------------------------------------------------
    # 3. reset()
    # ------------------------------------------------------------
    def test_reset_restores_defaults(self):
        """reset() should restore position, direction, speed, and visibility."""
        self.entity.direction = LEFT
        self.entity.visible = False
        self.entity.speed = 50
        self.entity.reset()
        self.assertEqual(self.entity.direction, STOP)
        self.assertTrue(self.entity.visible)
        self.assertEqual(self.entity.speed, 100 * TILEWIDTH / 16)
        self.assertEqual(self.entity.node, self.node)

    # ------------------------------------------------------------
    # 4. reverseDirection()
    # ------------------------------------------------------------
    def test_reverseDirection_swaps_node_and_target(self):
        """reverseDirection() should flip node and target."""
        node_a = MagicMock()
        node_b = MagicMock()
        self.entity.node = node_a
        self.entity.target = node_b
        self.entity.direction = RIGHT
        self.entity.reverseDirection()
        self.assertEqual(self.entity.node, node_b)
        self.assertEqual(self.entity.target, node_a)
        self.assertEqual(self.entity.direction, -RIGHT)

    # ------------------------------------------------------------
    # 5. overshotTarget()
    # ------------------------------------------------------------
    def test_overshotTarget_returns_true_when_past_target(self):
        """overshotTarget() should return True when entity has passed its target."""
        node = MagicMock()
        node.position = Vector2(0, 0)
        target = MagicMock()
        target.position = Vector2(10, 0)
        self.entity.node = node
        self.entity.target = target
        self.entity.position = Vector2(15, 0)
        self.assertTrue(self.entity.overshotTarget())

    def test_overshotTarget_returns_false_if_not_reached(self):
        """overshotTarget() should return False if entity hasn’t passed its target."""
        node = MagicMock()
        node.position = Vector2(0, 0)
        target = MagicMock()
        target.position = Vector2(10, 0)
        self.entity.node = node
        self.entity.target = target
        self.entity.position = Vector2(5, 0)
        self.assertFalse(self.entity.overshotTarget())

    # ------------------------------------------------------------
    # 6. validDirection()
    # ------------------------------------------------------------
    def test_validDirection_returns_true_if_accessible(self):
        """validDirection() should return True when neighbor exists and direction is allowed."""
        self.node.access[RIGHT] = [None]
        self.node.neighbors[RIGHT] = MagicMock()
        self.entity.name = None
        result = self.entity.validDirection(RIGHT)
        self.assertTrue(result)

    def test_validDirection_returns_false_if_no_neighbor(self):
        """validDirection() should return False when no neighbor in that direction."""
        self.node.access[RIGHT] = [None]
        self.node.neighbors[RIGHT] = None
        result = self.entity.validDirection(RIGHT)
        self.assertFalse(result)

    # ------------------------------------------------------------
    # 7. goalDirection()
    # ------------------------------------------------------------
    def test_goalDirection_returns_closest_direction(self):
        """goalDirection() should choose direction that minimizes distance to goal."""
        self.entity.goal = Vector2(10, 0)
        self.node.position = Vector2(0, 0)
        directions = [RIGHT, LEFT]
        result = self.entity.goalDirection(directions)
        self.assertEqual(result, RIGHT)

    # ------------------------------------------------------------
    # 8. randomDirection()
    # ------------------------------------------------------------
    @patch("CheeseChase.model.entity.randint", return_value=0)
    def test_randomDirection_returns_expected_direction(self, mock_randint):
        """randomDirection() should return a random direction from available ones."""
        directions = [UP, DOWN, LEFT]
        result = self.entity.randomDirection(directions)
        self.assertEqual(result, UP)
        mock_randint.assert_called_once()
