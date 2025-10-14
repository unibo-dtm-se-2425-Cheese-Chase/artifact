import unittest
from unittest.mock import MagicMock, patch
from CheeseChase.controller.levels_manager import LevelManager

class TestLevelManager(unittest.TestCase):
    def setUp(self):
        # Build a lightweight mocked game controller with all attributes LevelManager touches
        self.gc = MagicMock()

        # Nested components used by LevelManager
        self.gc.lifesprites = MagicMock()
        self.gc.textgroup = MagicMock()
        self.gc.mouse = MagicMock()
        self.gc.cats = MagicMock()
        self.gc.pause = MagicMock(paused=False)

        # Methods on the game controller
        self.gc.showEntities = MagicMock()
        self.gc.startGame = MagicMock()

        # Create LevelManager (this calls resetGameState in __init__)
        self.lm = LevelManager(self.gc)

    # ----------------------------------------------------------------------
    # __init__ + resetGameState()
    # ----------------------------------------------------------------------
    def test_init_calls_resetGameState_and_sets_initial_state(self):
        # After initialization, the game state should be reset
        self.assertEqual(self.gc.lives, 5)
        self.assertEqual(self.gc.level, 0)
        self.assertEqual(self.gc.score, 0)

        # And UI elements updated
        self.gc.lifesprites.resetLives.assert_called_with(5)
        self.gc.textgroup.updateScore.assert_called_with(0)
        self.gc.textgroup.updateLevel.assert_called_with(0)

    def test_resetGameState_resets_values_and_updates_ui(self):
        # Change values so we can see them reset
        self.gc.lives = 2
        self.gc.level = 3
        self.gc.score = 999

        # Clear previous init calls
        self.gc.lifesprites.resetLives.reset_mock()
        self.gc.textgroup.updateScore.reset_mock()
        self.gc.textgroup.updateLevel.reset_mock()

        # Act
        self.lm.resetGameState()

        # Assert
        self.assertEqual(self.gc.lives, 5)
        self.assertEqual(self.gc.level, 0)
        self.assertEqual(self.gc.score, 0)
        self.gc.lifesprites.resetLives.assert_called_once_with(5)
        self.gc.textgroup.updateScore.assert_called_once_with(0)
        self.gc.textgroup.updateLevel.assert_called_once_with(0)

    # ----------------------------------------------------------------------
    # resetEntities()
    # ----------------------------------------------------------------------
    def test_resetEntities_calls_mouse_and_cats_reset(self):
        self.lm.resetEntities()
        self.gc.mouse.reset.assert_called_once()
        self.gc.cats.reset.assert_called_once()

    # ----------------------------------------------------------------------
    # nextLevel()
    # ----------------------------------------------------------------------
    def test_nextLevel_increments_level_and_starts_game(self):
        # Clear calls from __init__
        self.gc.textgroup.updateLevel.reset_mock()

        # Precondition
        self.assertEqual(self.gc.level, 0)

        # Act
        self.lm.nextLevel()

        # Assert state
        self.gc.showEntities.assert_called_once()
        self.assertEqual(self.gc.level, 1)
        self.assertTrue(self.gc.pause.paused)
        self.gc.startGame.assert_called_once()
        self.gc.textgroup.updateLevel.assert_called_with(1)

    # ----------------------------------------------------------------------
    # restartGame()
    # ----------------------------------------------------------------------
    def test_restartGame_pauses_resets_starts_and_shows_ready_text(self):
        # Spy on resetGameState to ensure it is called
        with patch.object(self.lm, "resetGameState") as mock_reset, \
             patch("CheeseChase.controller.levels_manager.READYTXT", new="READY"):
            self.lm.restartGame()

            # Paused, reset, started, and "READY" shown
            self.assertTrue(self.gc.pause.paused)
            mock_reset.assert_called_once()
            self.gc.startGame.assert_called_once()
            self.gc.textgroup.showText.assert_called_once_with("READY")

    # ----------------------------------------------------------------------
    # resetLevel()
    # ----------------------------------------------------------------------
    def test_resetLevel_pauses_resets_entities_and_shows_ready_text(self):
        with patch.object(self.lm, "resetEntities") as mock_reset_entities, \
             patch("CheeseChase.controller.levels_manager.READYTXT", new="READY"):
            self.lm.resetLevel()

            self.assertTrue(self.gc.pause.paused)
            mock_reset_entities.assert_called_once()
            self.gc.textgroup.showText.assert_called_once_with("READY")

