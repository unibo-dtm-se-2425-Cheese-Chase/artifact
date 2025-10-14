import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch


class TestEventsManager(unittest.TestCase):
    def setUp(self):
        # Patch LevelManager inside events_manager so constructing EventsManager is isolated
        self.level_manager_patcher = patch(
            "CheeseChase.controller.events_manager.LevelManager", autospec=True
        )
        self.MockLevelManager = self.level_manager_patcher.start()
        self.addCleanup(self.level_manager_patcher.stop)

        # Build a lightweight mocked game controller with all attributes EventsManager touches
        self.gc = MagicMock()

        # Core components used by EventsManager
        self.gc.mouse = MagicMock(alive=True)
        self.gc.cheeses = MagicMock()
        self.gc.cats = MagicMock()
        self.gc.nodes = MagicMock()
        self.gc.textgroup = MagicMock()
        self.gc.pause = MagicMock(paused=False)
        self.gc.showEntities = MagicMock()
        self.gc.hideEntities = MagicMock()
        self.gc.updateScore = MagicMock()

        # GameController also needs a level_manager (used by EventsManager logic)
        self.gc.level_manager = MagicMock()
        self.gc.level_manager.nextLevel = MagicMock()
        self.gc.level_manager.restartGame = MagicMock()
        self.gc.level_manager.resetLevel = MagicMock()

        # Import after preparing patches
        from CheeseChase.controller.events_manager import EventsManager

        self.EventsManager = EventsManager
        self.em = EventsManager(self.gc)

    # ----------------------------------------------------------------------
    # checkEvents()
    # ----------------------------------------------------------------------
    def test_checkEvents_quit_calls_exit(self):
        with patch("CheeseChase.controller.events_manager.QUIT", new=9999), \
             patch("CheeseChase.controller.events_manager.pygame.event.get",
                   return_value=[SimpleNamespace(type=9999)]), \
             patch("builtins.exit") as mock_exit:
            self.em.checkEvents()
            mock_exit.assert_called_once()

    def test_checkEvents_space_key_unpaused_hides_text_and_shows_entities(self):
        # Simulate SPACE keydown when mouse is alive and pause is not active
        self.gc.mouse.alive = True
        self.gc.pause.paused = False

        with patch("CheeseChase.controller.events_manager.KEYDOWN", new=1), \
             patch("CheeseChase.controller.events_manager.K_SPACE", new=2), \
             patch("CheeseChase.controller.events_manager.pygame.event.get",
                   return_value=[SimpleNamespace(type=1, key=2)]):
            self.em.checkEvents()

        self.gc.pause.setPause.assert_called_once_with(playerPaused=True)
        self.gc.textgroup.hideText.assert_called_once()
        self.gc.showEntities.assert_called_once()
        self.gc.textgroup.showText.assert_not_called()

    def test_checkEvents_space_key_paused_shows_pause_text(self):
        # Simulate SPACE keydown when pause becomes active
        self.gc.mouse.alive = True
        self.gc.pause.paused = True

        with patch("CheeseChase.controller.events_manager.KEYDOWN", new=1), \
             patch("CheeseChase.controller.events_manager.K_SPACE", new=2), \
             patch("CheeseChase.controller.events_manager.PAUSETXT", new="PAUSED"), \
             patch("CheeseChase.controller.events_manager.pygame.event.get",
                   return_value=[SimpleNamespace(type=1, key=2)]):
            self.em.checkEvents()

        self.gc.pause.setPause.assert_called_once_with(playerPaused=True)
        self.gc.textgroup.showText.assert_called_once_with("PAUSED")
        self.gc.textgroup.hideText.assert_not_called()
        self.gc.showEntities.assert_not_called()

    # ----------------------------------------------------------------------
    # checkCheeseEvents()
    # ----------------------------------------------------------------------
    def test_checkCheeseEvents_power_cheese_and_board_empty_advances_level(self):
        # Setup a power cheese eaten and board becomes empty
        cheese = SimpleNamespace(points=50, name="POWER")
        self.gc.mouse.eatCheeses.return_value = cheese
        self.gc.cheeses.cheeseList = [cheese]
        self.gc.cheeses.numEaten = 0
        self.gc.cheeses.isEmpty.return_value = True

        with patch("CheeseChase.controller.events_manager.POWERCHEESE", new="POWER"):
            self.em.checkCheeseEvents()

        # Eaten tracking and scoring
        self.assertEqual(self.gc.cheeses.numEaten, 1)
        self.gc.updateScore.assert_called_once_with(50)

        # Power mode for cats
        self.gc.cats.startFreight.assert_called_once()

        # Cheese removed from list
        self.assertEqual(self.gc.cheeses.cheeseList, [])

        # End-of-level flow
        self.assertTrue(self.gc.flashBG)
        self.gc.hideEntities.assert_called_once()
        self.gc.pause.setPause.assert_called_once()
        kwargs = self.gc.pause.setPause.call_args.kwargs
        self.assertEqual(kwargs.get("pauseTime"), 3)
        self.assertIs(kwargs.get("func"), self.gc.level_manager.nextLevel)

    def test_checkCheeseEvents_threshold_30_allows_cat3_right_access(self):
        cheese = SimpleNamespace(points=10, name="NORMAL")
        self.gc.mouse.eatCheeses.return_value = cheese
        self.gc.cheeses.cheeseList = [cheese]
        self.gc.cheeses.numEaten = 29
        self.gc.cheeses.isEmpty.return_value = False

        # Prepare cat3 startNode
        self.gc.cats.cat3 = MagicMock()
        self.gc.cats.cat3.startNode = MagicMock()

        with patch("CheeseChase.controller.events_manager.RIGHT", new="RIGHT_CONST"):
            self.em.checkCheeseEvents()

        self.gc.cats.cat3.startNode.allowAccess.assert_called_once_with(
            "RIGHT_CONST", self.gc.cats.cat3
        )

    def test_checkCheeseEvents_threshold_70_allows_cat4_left_access(self):
        cheese = SimpleNamespace(points=10, name="NORMAL")
        self.gc.mouse.eatCheeses.return_value = cheese
        self.gc.cheeses.cheeseList = [cheese]
        self.gc.cheeses.numEaten = 69
        self.gc.cheeses.isEmpty.return_value = False

        # Prepare cat4 startNode
        self.gc.cats.cat4 = MagicMock()
        self.gc.cats.cat4.startNode = MagicMock()

        with patch("CheeseChase.controller.events_manager.LEFT", new="LEFT_CONST"):
            self.em.checkCheeseEvents()

        self.gc.cats.cat4.startNode.allowAccess.assert_called_once_with(
            "LEFT_CONST", self.gc.cats.cat4
        )

    def test_checkCheeseEvents_no_cheese_no_side_effects(self):
        # No cheese eaten: nothing happens
        self.gc.mouse.eatCheeses.return_value = None
        prev_calls = {
            "updateScore": self.gc.updateScore.call_count,
            "setPause": self.gc.pause.setPause.call_count,
        }

        self.em.checkCheeseEvents()

        self.assertEqual(self.gc.updateScore.call_count, prev_calls["updateScore"])
        self.assertEqual(self.gc.pause.setPause.call_count, prev_calls["setPause"])

    # ----------------------------------------------------------------------
    # checkCatEvents()
    # ----------------------------------------------------------------------
    def test_checkCatEvents_freight_collision_scores_and_respawns_cat(self):
        # Setup one cat in iteration
        cat = MagicMock()
        cat.points = 200
        cat.position = SimpleNamespace(x=10, y=20)
        cat.mode = SimpleNamespace(current=None)

        # Make cats iterable
        self.gc.cats.__iter__.return_value = [cat]
        self.gc.mouse.collideCat.return_value = True

        with patch("CheeseChase.controller.events_manager.FREIGHT", object()), \
             patch("CheeseChase.controller.events_manager.RED", new="RED_CONST") as _:
            # Need identity for FREIGHT: retrieve the patched constant to set mode.current
            from CheeseChase.controller import events_manager as em_mod
            cat.mode.current = em_mod.FREIGHT

            self.em.checkCatEvents()

        # Visibility toggled
        self.assertFalse(self.gc.mouse.visible)
        self.assertFalse(cat.visible)

        # Scoring and text
        self.gc.updateScore.assert_called_once_with(200)
        self.gc.textgroup.addText.assert_called_once()
        text_args, text_kwargs = self.gc.textgroup.addText.call_args
        self.assertEqual(text_args[0], "200")
        self.assertEqual(text_args[1], "RED_CONST")
        self.assertEqual(text_args[2], 10)
        self.assertEqual(text_args[3], 20)
        self.assertEqual(text_args[4], 8)
        self.assertEqual(text_kwargs.get("time"), 1)

        # Points update and pause with callback to showEntities
        self.gc.cats.updatePoints.assert_called_once()
        self.gc.pause.setPause.assert_called_once()
        kwargs = self.gc.pause.setPause.call_args.kwargs
        self.assertEqual(kwargs.get("pauseTime"), 1)
        self.assertIs(kwargs.get("func"), self.gc.showEntities)

        # Respawn and allow home access
        cat.startSpawn.assert_called_once()
        self.gc.nodes.allowHomeAccess.assert_called_once_with(cat)

    def test_checkCatEvents_death_and_game_over(self):
        # Setup one cat and a collision in non-SPAWN mode
        cat = MagicMock()
        cat.mode = SimpleNamespace(current="CHASE")

        self.gc.cats.__iter__.return_value = [cat]
        self.gc.mouse.collideCat.return_value = True
        self.gc.mouse.alive = True
        self.gc.lives = 1  # Will drop to 0 -> game over

        with patch("CheeseChase.controller.events_manager.SPAWN", new=object()), \
             patch("CheeseChase.controller.events_manager.GAMEOVERTXT", new="GAME OVER"):
            self.em.checkCatEvents()

        # Life lost and death sequence
        self.assertEqual(self.gc.lives, 0)
        self.gc.lifesprites.removeImage.assert_called_once()
        self.gc.mouse.die.assert_called_once()
        self.gc.cats.hide.assert_called_once()

        # Game over path
        self.gc.textgroup.showText.assert_called_once_with("GAME OVER")
        self.gc.pause.setPause.assert_called_once()
        kwargs = self.gc.pause.setPause.call_args.kwargs
        self.assertEqual(kwargs.get("pauseTime"), 3)
        self.assertIs(kwargs.get("func"), self.gc.level_manager.restartGame)

    def test_checkCatEvents_death_with_lives_remaining_resets_level(self):
        # Setup one cat and a collision in non-SPAWN mode
        cat = MagicMock()
        cat.mode = SimpleNamespace(current="CHASE")

        self.gc.cats.__iter__.return_value = [cat]
        self.gc.mouse.collideCat.return_value = True
        self.gc.mouse.alive = True
        self.gc.lives = 2  # Will drop to 1 -> reset level, not game over

        with patch("CheeseChase.controller.events_manager.SPAWN", new=object()):
            self.em.checkCatEvents()

        # Life lost and death sequence
        self.assertEqual(self.gc.lives, 1)
        self.gc.lifesprites.removeImage.assert_called_once()
        self.gc.mouse.die.assert_called_once()
        self.gc.cats.hide.assert_called_once()

        # Reset level path (no game over text)
        self.gc.textgroup.showText.assert_not_called()
        self.gc.pause.setPause.assert_called_once()
        kwargs = self.gc.pause.setPause.call_args.kwargs
        self.assertEqual(kwargs.get("pauseTime"), 3)
        self.assertIs(kwargs.get("func"), self.gc.level_manager.resetLevel)