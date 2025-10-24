import unittest
from unittest.mock import MagicMock, patch
from CheeseChase.model.mouse import Mouse
from CheeseChase.model.constants import LEFT, RIGHT, UP, DOWN, STOP, PORTAL, MOUSE, YELLOW

@patch("CheeseChase.model.mouse.MouseSprites")
class TestMouse(unittest.TestCase):
    def setUp(self):
        # Provide every direction as used by the game
        self.mock_neighbors = {
            LEFT: MagicMock(),
            RIGHT: MagicMock(),
            UP: MagicMock(),
            DOWN: MagicMock(),
            STOP: MagicMock(),
            PORTAL: MagicMock()
        }
        self.node = MagicMock()
        self.node.neighbors = self.mock_neighbors
        self.node.position = MagicMock()

    @patch("CheeseChase.model.mouse.Entity.__init__", autospec=True)
    def test_initialization(self, mock_entity_init, MockSprites):
        # When patching Entity.__init__, set self.node manually
        def entity_init_side_effect(self_, node):
            self_.node = node
        mock_entity_init.side_effect = entity_init_side_effect

        mouse = Mouse(self.node)
        mock_entity_init.assert_called_once_with(mouse, self.node)
        self.assertEqual(mouse.name, MOUSE)
        self.assertEqual(mouse.color, YELLOW)
        self.assertEqual(mouse.direction, LEFT)
        self.assertTrue(mouse.alive)
        self.assertTrue(hasattr(mouse, "sprites"))

    @patch("CheeseChase.model.mouse.Entity.reset", autospec=True)
    @patch("CheeseChase.model.mouse.Entity.__init__", autospec=True)
    def test_reset(self, mock_entity_init, mock_entity_reset, MockSprites):
        def entity_init_side_effect(self_, node):
            self_.node = node
        mock_entity_init.side_effect = entity_init_side_effect

        mouse = Mouse(self.node)
        mouse.sprites.getStartImage = MagicMock(return_value="start_image")
        mouse.sprites.reset = MagicMock()
        mouse.direction = RIGHT
        mouse.alive = False
        mouse.image = None
        mouse.reset()
        mock_entity_reset.assert_called_once_with(mouse)
        self.assertEqual(mouse.direction, LEFT)
        self.assertTrue(mouse.alive)
        self.assertEqual(mouse.image, "start_image")
        mouse.sprites.reset.assert_called_once()

    def test_die_sets_alive_false_and_direction_stop(self, MockSprites):
        mouse = Mouse(self.node)
        mouse.direction = LEFT
        mouse.alive = True
        mouse.die()
        self.assertFalse(mouse.alive)
        self.assertEqual(mouse.direction, STOP)

    def test_eatCheeses_returns_cheese_on_collision(self, MockSprites):
        mouse = Mouse(self.node)
        cheese1 = MagicMock()
        cheese2 = MagicMock()
        mouse.collideCheck = MagicMock(side_effect=[False, True])
        result = mouse.eatCheeses([cheese1, cheese2])
        self.assertEqual(result, cheese2)
        mouse.collideCheck.assert_any_call(cheese1)
        mouse.collideCheck.assert_any_call(cheese2)

    def test_eatCheeses_returns_none_if_no_collision(self, MockSprites):
        mouse = Mouse(self.node)
        cheese1 = MagicMock()
        cheese2 = MagicMock()
        mouse.collideCheck = MagicMock(return_value=False)
        result = mouse.eatCheeses([cheese1, cheese2])
        self.assertIsNone(result)

    def test_collideCat_delegates_to_collideCheck(self, MockSprites):
        mouse = Mouse(self.node)
        cat = MagicMock()
        mouse.collideCheck = MagicMock(return_value=True)
        result = mouse.collideCat(cat)
        mouse.collideCheck.assert_called_once_with(cat)
        self.assertTrue(result)

    def test_collideCheck_true_if_within_radius(self, MockSprites):
        mouse = Mouse(self.node)
        other = MagicMock()
        mouse.position = MagicMock()
        other.position = MagicMock()
        mouse.collideRadius = 5
        other.collideRadius = 7
        # Set magnitudeSquared to less than (5+7)^2 = 144
        diff = MagicMock()
        diff.magnitudeSquared.return_value = 100
        mouse.position.__sub__.return_value = diff
        result = mouse.collideCheck(other)
        self.assertTrue(result)

    def test_collideCheck_false_if_outside_radius(self, MockSprites):
        mouse = Mouse(self.node)
        other = MagicMock()
        mouse.position = MagicMock()
        other.position = MagicMock()
        mouse.collideRadius = 5
        other.collideRadius = 7
        # Set magnitudeSquared to greater than (5+7)^2 = 144
        diff = MagicMock()
        diff.magnitudeSquared.return_value = 200
        mouse.position.__sub__.return_value = diff
        result = mouse.collideCheck(other)
        self.assertFalse(result)

    @patch("CheeseChase.model.mouse.pygame.key.get_pressed")
    def test_getValidKey_returns_correct_direction(self, MockGetPressed, MockSprites):
        mouse = Mouse(self.node)

        # Use a dict-like mock that handles large key constants
        class KeyMock(dict):
            def __getitem__(self, key):
                return dict.get(self, key, 0)

        # Use pygame key constants for keys!
        from pygame.locals import K_UP, K_DOWN, K_LEFT, K_RIGHT

        # Test UP
        MockGetPressed.return_value = KeyMock({K_UP: 1})
        self.assertEqual(mouse.getValidKey(), UP)

        # Test DOWN
        MockGetPressed.return_value = KeyMock({K_DOWN: 1})
        self.assertEqual(mouse.getValidKey(), DOWN)

        # Test LEFT
        MockGetPressed.return_value = KeyMock({K_LEFT: 1})
        self.assertEqual(mouse.getValidKey(), LEFT)

        # Test RIGHT
        MockGetPressed.return_value = KeyMock({K_RIGHT: 1})
        self.assertEqual(mouse.getValidKey(), RIGHT)

        # Test STOP (no key pressed)
        MockGetPressed.return_value = KeyMock()
        self.assertEqual(mouse.getValidKey(), STOP)