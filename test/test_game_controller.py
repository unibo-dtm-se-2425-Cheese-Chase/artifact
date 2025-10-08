import unittest
from unittest.mock import MagicMock, patch
from CheeseChase.controller.game_controller import GameController


class TestGameController(unittest.TestCase):

    def setUp(self):
        # --- Patch all external dependencies ---
        patchers = {
            "Pause": patch("CheeseChase.controller.game_controller.Pause", autospec=True),
            "TextGroup": patch("CheeseChase.controller.game_controller.TextGroup", autospec=True),
            "LifeSprites": patch("CheeseChase.controller.game_controller.LifeSprites", autospec=True),
            "MazeData": patch("CheeseChase.controller.game_controller.MazeData", autospec=True),
            "EventsManager": patch("CheeseChase.controller.game_controller.EventsManager", autospec=True),
            "LevelManager": patch("CheeseChase.controller.game_controller.LevelManager", autospec=True),
            "GameView": patch("CheeseChase.controller.game_controller.GameView", autospec=True),
        }
        self.patches = {name: p.start() for name, p in patchers.items()}
        self.addCleanup(lambda: [p.stop() for p in patchers.values()])

        # --- Create controller instance ---
        self.controller = GameController()

        # --- Mock key runtime attributes ---
        self.controller.mouse = MagicMock(alive=True)
        self.controller.cats = MagicMock()
        self.controller.cheeses = MagicMock()
        self.controller.textgroup = MagicMock()
        self.controller.events_manager = MagicMock()
        self.controller.view = MagicMock()
        self.controller.pause = MagicMock(paused=False, update=MagicMock(return_value=None))
        self.controller.clock = MagicMock()
        self.controller.clock.tick.return_value = 30  # simulate 30ms per frame

    # ----------------------------------------------------------------------
    # Initialization
    # ----------------------------------------------------------------------

    def test_initial_state(self):
        """Ensure initial controller attributes are correctly set."""
        self.assertEqual(self.controller.score, 0)
        self.assertEqual(self.controller.lives, 5)
        self.assertEqual(self.controller.level, 0)
        self.assertIsNotNone(self.controller.pause)
        self.assertIsNotNone(self.controller.textgroup)

    # ----------------------------------------------------------------------
    # startGame()
    # ----------------------------------------------------------------------

    @patch("CheeseChase.controller.game_controller.MazeSprites", autospec=True)
    @patch("CheeseChase.controller.game_controller.CatGroup", autospec=True)
    @patch("CheeseChase.controller.game_controller.CheeseGroup", autospec=True)
    @patch("CheeseChase.controller.game_controller.Mouse", autospec=True)
    @patch("CheeseChase.controller.game_controller.NodeGroup", autospec=True)
    def test_startGame_initializes_all_components(
        self, MockNodeGroup, MockMouse, MockCheeseGroup, MockCatGroup, MockMazeSprites
    ):
        """Ensure startGame builds and links game entities correctly."""
        mock_maze_obj = MagicMock()
        mock_maze_obj.name = "test_maze"
        mock_maze_obj.mouseStart = (1, 1)
        mock_maze_obj.addOffset.side_effect = lambda x, y: (x + 1, y + 1)
        self.controller.mazedata.obj = mock_maze_obj
        self.controller.mazedata.loadMaze = MagicMock()

        mock_nodes = MagicMock()
        MockNodeGroup.return_value = mock_nodes
        mock_nodes.getNodeFromTiles.return_value = "node"
        mock_nodes.getStartTempNode.return_value = "temp_node"

        mock_cats = MagicMock()
        mock_cats.cat1 = MagicMock()
        mock_cats.cat2 = MagicMock()
        mock_cats.cat3 = MagicMock()
        mock_cats.cat4 = MagicMock()
        MockCatGroup.return_value = mock_cats

        self.controller.setBackground = MagicMock()

        self.controller.startGame()

        # MazeData
        self.controller.mazedata.loadMaze.assert_called_once_with(self.controller.level)

        # Instantiated components
        MockMazeSprites.assert_called_once()
        MockNodeGroup.assert_called_once()
        MockMouse.assert_called_once_with(mock_nodes.getNodeFromTiles.return_value)
        MockCheeseGroup.assert_called_once()
        MockCatGroup.assert_called_once_with(mock_nodes.getStartTempNode.return_value, self.controller.mouse)

        # MazeData object logic
        mock_maze_obj.setPortalPairs.assert_called_once_with(mock_nodes)
        mock_maze_obj.connectHomeNodes.assert_called_once_with(mock_nodes)

        # Cats setup
        mock_cats.cat2.setStartNode.assert_called()
        mock_cats.cat3.setStartNode.assert_called()
        mock_cats.cat4.setStartNode.assert_called()
        mock_cats.cat1.setStartNode.assert_called()
        mock_cats.setSpawnNode.assert_called_once()

        # Access restrictions
        mock_nodes.denyHomeAccess.assert_called_once_with(self.controller.mouse)
        mock_nodes.denyHomeAccessList.assert_called_once_with(mock_cats)
        mock_cats.cat3.startNode.denyAccess.assert_called()
        mock_cats.cat4.startNode.denyAccess.assert_called()
        mock_maze_obj.denyCatsAccess.assert_called_once_with(mock_cats, mock_nodes)

    # ----------------------------------------------------------------------
    # setBackground()
    # ----------------------------------------------------------------------

    @patch("CheeseChase.controller.game_controller.pygame.surface.Surface", autospec=True)
    def test_setBackground_constructs_backgrounds(self, mock_surface):
        """Ensure setBackground creates and fills surface backgrounds."""
        mock_surface.return_value.convert.return_value = MagicMock()
        mock_mazesprites = MagicMock()
        mock_mazesprites.constructBackground = MagicMock()
        self.controller.mazesprites = mock_mazesprites

        self.controller.setBackground()

        self.assertFalse(self.controller.flashBG)
        self.assertEqual(self.controller.background, self.controller.background_norm)
        mock_mazesprites.constructBackground.assert_any_call(
            unittest.mock.ANY, self.controller.level % 5
        )
        mock_mazesprites.constructBackground.assert_any_call(unittest.mock.ANY, 5)

    # ----------------------------------------------------------------------
    # update() core logic
    # ----------------------------------------------------------------------

    def test_update_normal_cycle(self):
        """update() should call expected subsystems during normal gameplay."""
        self.controller.update()
        self.controller.textgroup.update.assert_called_once()
        self.controller.cheeses.update.assert_called_once()
        self.controller.cats.update.assert_called_once()
        self.controller.events_manager.checkCheeseEvents.assert_called_once()
        self.controller.events_manager.checkCatEvents.assert_called_once()
        self.controller.mouse.update.assert_called()
        self.controller.view.render.assert_called_once()
        self.controller.events_manager.checkEvents.assert_called_once()

    def test_update_when_mouse_not_alive(self):
        """Even if mouse is dead, update() should still update it."""
        self.controller.mouse.alive = False
        self.controller.update()
        self.controller.mouse.update.assert_called()

    def test_update_skips_cats_when_paused(self):
        """When paused, cats and related events should not update."""
        self.controller.pause.paused = True
        self.controller.update()
        self.controller.cats.update.assert_not_called()
        self.controller.events_manager.checkCheeseEvents.assert_not_called()
        self.controller.events_manager.checkCatEvents.assert_not_called()

    def test_update_flashing_background_toggles(self):
        """Flashing background toggles correctly after flashTime."""
        self.controller.flashBG = True
        self.controller.background_norm = "normal"
        self.controller.background_flash = "flash"
        self.controller.background = "normal"
        self.controller.flashTimer = self.controller.flashTime
        self.controller.update()
        self.assertEqual(self.controller.background, "flash")

    def test_update_calls_afterPauseMethod(self):
        """If pause.update() returns callable, ensure it is executed."""
        called = {"done": False}

        def fake_method():
            called["done"] = True

        self.controller.pause.update.return_value = fake_method
        self.controller.update()
        self.assertTrue(called["done"])

    # ----------------------------------------------------------------------
    # showEntities() / hideEntities()
    # ----------------------------------------------------------------------

    def test_show_and_hide_entities(self):
        """showEntities and hideEntities toggle visibility correctly."""
        self.controller.mouse.visible = False
        self.controller.cats.show = MagicMock()
        self.controller.cats.hide = MagicMock()

        self.controller.showEntities()
        self.assertTrue(self.controller.mouse.visible)
        self.controller.cats.show.assert_called_once()

        self.controller.hideEntities()
        self.assertFalse(self.controller.mouse.visible)
        self.controller.cats.hide.assert_called_once()


    # ----------------------------------------------------------------------
    # updateScore()
    # ----------------------------------------------------------------------

    def test_updateScore_increments_and_calls_textgroup(self):
        """updateScore should increment score and notify TextGroup."""
        self.controller.textgroup.updateScore = MagicMock()
        self.controller.updateScore(200)
        self.assertEqual(self.controller.score, 200)
        self.controller.textgroup.updateScore.assert_called_once_with(200)
