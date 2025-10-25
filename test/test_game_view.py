import unittest
from unittest.mock import MagicMock, patch
from CheeseChase.view.game_view import GameView
from CheeseChase.model.constants import SCREENHEIGHT

class TestGameView(unittest.TestCase):
    def setUp(self):
        # Create a mock controller with all needed attributes
        self.mock_controller = MagicMock()
        self.mock_controller.screen = MagicMock()
        self.mock_controller.background = MagicMock()
        self.mock_controller.cheeses.render = MagicMock()
        self.mock_controller.mouse.render = MagicMock()
        self.mock_controller.cats.render = MagicMock()
        self.mock_controller.textgroup.render = MagicMock()
        # Setup mock images
        img1 = MagicMock()
        img1.get_width.return_value = 8
        img1.get_height.return_value = 10
        img2 = MagicMock()
        img2.get_width.return_value = 8
        img2.get_height.return_value = 10
        self.mock_controller.lifesprites.images = [img1, img2]
        self.screen = self.mock_controller.screen

        self.view = GameView(self.mock_controller)

    @patch("CheeseChase.view.game_view.pygame.display.update")
    def test_render_calls_all_components(self, mock_update):
        # Call render
        self.view.render()
        # Background blit
        self.screen.blit.assert_any_call(self.mock_controller.background, (0, 0))
        # Components
        self.mock_controller.cheeses.render.assert_called_once_with(self.screen)
        self.mock_controller.mouse.render.assert_called_once_with(self.screen)
        self.mock_controller.cats.render.assert_called_once_with(self.screen)
        self.mock_controller.textgroup.render.assert_called_once_with(self.screen)
        # Lifesprites blit
        calls = [
            ((self.mock_controller.lifesprites.images[0], (0, SCREENHEIGHT - 10)),),
            ((self.mock_controller.lifesprites.images[1], (8, SCREENHEIGHT - 10)),)
        ]
        self.screen.blit.assert_any_call(*calls[0][0])
        self.screen.blit.assert_any_call(*calls[1][0])
        # Display update called
        mock_update.assert_called_once()
