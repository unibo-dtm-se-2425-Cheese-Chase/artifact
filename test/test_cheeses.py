import unittest
from unittest.mock import MagicMock, patch
import numpy as np

from CheeseChase.model.cheeses import Cheese, PowerCheese, CheeseGroup
from CheeseChase.model.constants import CHEESE, POWERCHEESE, TILEWIDTH, TILEHEIGHT

class TestCheese(unittest.TestCase):
    def setUp(self):
        self.row = 2
        self.col = 3
        self.mock_spritesheet = MagicMock()
        self.mock_spritesheet.getImage.return_value = "img"

    def test_cheese_initialization(self):
        cheese = Cheese(self.row, self.col, self.mock_spritesheet)
        self.assertEqual(cheese.name, CHEESE)               # Proper type
        self.assertEqual(cheese.points, 10)                 # Base points
        self.assertTrue(cheese.visible)                     # Visible by default
        self.assertEqual(cheese.image, "img")               # Correct sprite image
        
        # Position calculation
        expected_x = self.col * TILEWIDTH
        expected_y = self.row * TILEHEIGHT
        self.assertEqual(cheese.position.x, expected_x)
        self.assertEqual(cheese.position.y, expected_y)
        # Collide radius and spritesheet linkage
        self.assertEqual(cheese.collideRadius, 2 * TILEWIDTH / 16)
        self.assertEqual(cheese.spritesheet, self.mock_spritesheet)

    def test_cheese_render_if_visible(self):
        # If visible, Cheese should be blitted to screen
        cheese = Cheese(self.row, self.col, self.mock_spritesheet)
        cheese.visible = True
        screen = MagicMock()
        cheese.position.asTuple = MagicMock(return_value=(1,2))
        cheese.render(screen)
        screen.blit.assert_called_once_with("img", (1,2))

    def test_cheese_render_if_not_visible(self):
        # If not visible, render should do nothing
        cheese = Cheese(self.row, self.col, self.mock_spritesheet)
        cheese.visible = False
        screen = MagicMock()
        cheese.position.asTuple = MagicMock(return_value=(1,2))
        cheese.render(screen)
        screen.blit.assert_not_called()

class TestPowerCheese(unittest.TestCase):
    def setUp(self):
        self.row = 1
        self.col = 1
        self.mock_spritesheet = MagicMock()
        self.mock_spritesheet.getImage.return_value = "power_img"

    def test_powercheese_initialization(self):
        pcheese = PowerCheese(self.row, self.col, self.mock_spritesheet)
        self.assertEqual(pcheese.name, POWERCHEESE)
        self.assertEqual(pcheese.points, 50)           # Higher value item
        self.assertEqual(pcheese.flashTime, 0.4)       # Flash frequency
        self.assertEqual(pcheese.timer, 0)
        self.assertEqual(pcheese.image, "power_img")

    def test_powercheese_update_flashes(self):
        pcheese = PowerCheese(self.row, self.col, self.mock_spritesheet)
        # timer less than flashTime; visible stays True
        pcheese.visible = True
        pcheese.timer = 0.3
        pcheese.update(0.05) # timer now 0.35 < flashTime
        self.assertTrue(pcheese.visible)
        self.assertAlmostEqual(pcheese.timer, 0.35)
        # timer reaches/exceeds flashTime; visible toggled
        pcheese.timer = 0.4
        pcheese.visible = True
        pcheese.update(0.05)  # timer now 0.45, should toggle
        self.assertFalse(pcheese.visible)
        self.assertEqual(pcheese.timer, 0)

class TestCheeseGroup(unittest.TestCase):
    def setUp(self):
        self.mock_spritesheet = MagicMock()
        # Patch np.loadtxt to return a fixed array
        self.cheese_map = np.array([
            ['.', '+', 'x'],
            ['P', 'p', ' '],
            ['.', '.', '+']
        ])
        patcher = patch("CheeseChase.model.cheeses.np.loadtxt", return_value=self.cheese_map)
        self.mock_loadtxt = patcher.start()
        self.addCleanup(patcher.stop)

    def test_cheesegroup_initialization_and_createCheeseList(self):
        group = CheeseGroup("fake.txt", self.mock_spritesheet)
        # Should create Cheese and PowerCheese objects according to cheese_map
        # ('.' and '+' → Cheese, 'P' and 'p' → PowerCheese)
        cheese_count = np.count_nonzero(np.isin(self.cheese_map, ['.', '+', 'P', 'p']))
        power_count = np.count_nonzero(np.isin(self.cheese_map, ['P', 'p']))
        self.assertEqual(len(group.cheeseList), cheese_count)
        self.assertEqual(len(group.powercheeses), power_count)
        self.assertEqual(group.spritesheet, self.mock_spritesheet)
        self.assertEqual(group.numEaten, 0)
        # All cheeses should be Cheese or PowerCheese instances
        for cheese in group.cheeseList:
            self.assertTrue(isinstance(cheese, (Cheese, PowerCheese)))
        for power in group.powercheeses:
            self.assertIsInstance(power, PowerCheese)

    def test_cheesegroup_update_calls_update_on_powercheeses(self):
        # PowerCheese items should update each frame
        group = CheeseGroup("fake.txt", self.mock_spritesheet)
        for p in group.powercheeses:
            p.update = MagicMock()
        group.update(0.25)
        for p in group.powercheeses:
            p.update.assert_called_once_with(0.25)

    def test_cheesegroup_isEmpty(self):
        # Empty only when no cheese left to collect
        group = CheeseGroup("fake.txt", self.mock_spritesheet)
        group.cheeseList.clear()
        self.assertTrue(group.isEmpty())
        # Add one cheese, should be not empty
        group.cheeseList.append(MagicMock())
        self.assertFalse(group.isEmpty())

    def test_cheesegroup_render_calls_render_on_all_cheeses(self):
        # Render should call each cheese's render method
        group = CheeseGroup("fake.txt", self.mock_spritesheet)
        for cheese in group.cheeseList:
            cheese.render = MagicMock()
        screen = MagicMock()
        group.render(screen)
        for cheese in group.cheeseList:
            cheese.render.assert_called_once_with(screen)
