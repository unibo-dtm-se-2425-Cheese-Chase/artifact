import unittest
from unittest.mock import MagicMock, patch
from CheeseChase.model.cats import Cat, CatGroup
from CheeseChase.model.constants import *

# Patch ModeController and CatSprites to avoid real game dependencies
@patch("CheeseChase.model.cats.Entity.__init__")
@patch("CheeseChase.model.cats.CatSprites")
@patch("CheeseChase.model.cats.ModeController")

class TestCats(unittest.TestCase):
    """Unit tests for the Cat and CatGroup classes."""

    def setUp(self):
        # Create a mock node and mouse object
        self.node = MagicMock()
        self.mouse = MagicMock()
        self.node.position = MagicMock()
        self.mouse.position = MagicMock()

    # ------------------ Cat class tests ------------------

    def test_cat_initialization(self, MockMode, MockSprites, MockEntityInit):
        """Test __init__() → initializes all attributes properly."""
        cat = Cat(self.node, self.mouse)
        MockEntityInit.assert_called_once_with(cat, self.node)
        self.assertEqual(cat.points, 200)
        self.assertEqual(cat.mouse, self.mouse)
        self.assertEqual(cat.homeNode, self.node)
        self.assertTrue(hasattr(cat, "sprites"))
        self.assertTrue(hasattr(cat, "mode"))


    def test_cat_reset_resets_points_and_direction(self, MockEntity, MockSprites, MockMode):
        """Test reset() → restores points and goalDirection."""
        cat = Cat(self.node, self.mouse)
        cat.startNode = self.node
        cat.setStartNode = MagicMock() 
        cat.goalDirection = MagicMock()
        cat.points = 0
        cat.directionMethod = None

        cat.reset()

        cat.setStartNode.assert_called_once_with(self.node)
        self.assertEqual(cat.points, 200)
        self.assertEqual(cat.directionMethod, cat.goalDirection)

    
    def test_cat_scatter_sets_empty_goal(self, MockEntity, MockSprites, MockMode):
        """Test scatter() → sets goal to empty Vector2."""
        cat = Cat(self.node)
        cat.goal = MagicMock()
        cat.scatter()
        self.assertEqual(cat.goal.x, 0)
        self.assertEqual(cat.goal.y, 0)

    def test_cat_chase_sets_goal_to_mouse_position(self, MockEntity, MockSprites, MockMode):
        """Test chase() → sets goal to mouse position."""
        cat = Cat(self.node, self.mouse)
        cat.chase()
        self.assertEqual(cat.goal, self.mouse.position)

    def test_cat_spawn_sets_goal_to_spawn_position(self, MockEntity, MockSprites, MockMode):
        """Test spawn() → sets goal to spawnNode.position."""
        cat = Cat(self.node)
        cat.spawnNode = MagicMock()
        cat.spawnNode.position = "pos"
        cat.spawn()
        self.assertEqual(cat.goal, "pos")

    def test_cat_setSpawnNode_stores_node(self, MockEntity, MockSprites, MockMode):
        """Test setSpawnNode() → stores the spawn node reference."""
        cat = Cat(self.node)
        node2 = MagicMock()
        cat.setSpawnNode(node2)
        self.assertEqual(cat.spawnNode, node2)

    def test_cat_startFreight_sets_speed_and_random_direction(self, MockEntity, MockSprites, MockMode):
        """Test startFreight() → sets low speed and random direction if mode is FREIGHT."""
        cat = Cat(self.node)
        cat.setSpeed = MagicMock()
        cat.mode.setFreightMode = MagicMock()
        cat.mode.current = FREIGHT

        cat.startFreight()
        cat.setSpeed.assert_called_once_with(50)
        self.assertEqual(cat.directionMethod, cat.randomDirection)

    def test_cat_startSpawn_sets_speed_and_goal(self, MockEntity, MockSprites, MockMode):
        """Test startSpawn() → sets high speed and moves to spawn node when in SPAWN mode."""
        cat = Cat(self.node)
        cat.setSpeed = MagicMock()
        cat.spawn = MagicMock()
        cat.mode.setSpawnMode = MagicMock()
        cat.mode.current = SPAWN

        cat.startSpawn()
        cat.setSpeed.assert_called_once_with(150)
        self.assertEqual(cat.directionMethod, cat.goalDirection)
        cat.spawn.assert_called_once()

    def test_cat_normalMode_resets_speed_and_denies_access(self, MockEntity, MockSprites, MockMode):
        """Test normalMode() → resets to normal speed and denies access in DOWN direction."""
        cat = Cat(self.node)
        cat.homeNode = MagicMock()
        cat.setSpeed = MagicMock()

        cat.normalMode()
        cat.setSpeed.assert_called_once_with(100)
        self.assertEqual(cat.directionMethod, cat.goalDirection)
        cat.homeNode.denyAccess.assert_called_once_with(DOWN, cat)

    # ------------------ CatGroup class tests ------------------

    def test_catgroup_initialization_creates_four_cats(self, MockEntity, MockSprites, MockMode):
        """Test CatGroup() → creates 4 cats with mouse and node references."""
        group = CatGroup(self.node, self.mouse)
        self.assertEqual(len(group.cats), 4)
        for cat in group:
            self.assertEqual(cat.homeNode, self.node)
            self.assertEqual(cat.mouse, self.mouse)

    def test_catgroup_startFreight_calls_each_cat_and_resets_points(self, MockEntity, MockSprites, MockMode):
        """Test startFreight() → calls startFreight() on each cat and resets points."""
        group = CatGroup(self.node, self.mouse)
        for cat in group:
            cat.startFreight = MagicMock()
        group.resetPoints = MagicMock()

        group.startFreight()
        for cat in group:
            cat.startFreight.assert_called_once()
        group.resetPoints.assert_called_once()

    def test_catgroup_resetPoints_sets_points_to_200(self, MockEntity, MockSprites, MockMode):
        """Test resetPoints() → sets all cats’ points back to 200."""
        group = CatGroup(self.node, self.mouse)
        for cat in group:
            cat.points = 800
        group.resetPoints()
        self.assertTrue(all(cat.points == 200 for cat in group))

    def test_catgroup_updatePoints_doubles_points(self, MockEntity, MockSprites, MockMode):
        """Test updatePoints() → doubles each cat’s points."""
        group = CatGroup(self.node, self.mouse)
        for cat in group:
            cat.points = 200
        group.updatePoints()
        self.assertTrue(all(cat.points == 400 for cat in group))

    def test_catgroup_hide_and_show_toggle_visibility(self, MockEntity, MockSprites, MockMode):
        """Test hide() and show() → toggle each cat’s visibility."""
        group = CatGroup(self.node, self.mouse)
        group.hide()
        self.assertTrue(all(cat.visible is False for cat in group))
        group.show()
        self.assertTrue(all(cat.visible is True for cat in group))

    def test_catgroup_reset_calls_reset_on_all_cats(self, MockEntity, MockSprites, MockMode):
        """Test reset() → calls reset() on all cats."""
        group = CatGroup(self.node, self.mouse)
        for cat in group:
            cat.reset = MagicMock()
        group.reset()
        for cat in group:
            cat.reset.assert_called_once()

    def test_catgroup_setSpawnNode_applies_to_all_cats(self, MockEntity, MockSprites, MockMode):
        """Test setSpawnNode() → applies the node to all cats."""
        group = CatGroup(self.node, self.mouse)
        node2 = MagicMock()
        for cat in group:
            cat.setSpawnNode = MagicMock()
        group.setSpawnNode(node2)
        for cat in group:
            cat.setSpawnNode.assert_called_once_with(node2)

