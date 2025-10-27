import unittest
from unittest.mock import MagicMock
from CheeseChase.model.modes import MainMode, ModeController
from CheeseChase.model.constants import SCATTER, CHASE, FREIGHT, SPAWN

class TestMainMode(unittest.TestCase):
    def test_initialization_sets_scatter(self):
        # MainMode should start in SCATTER mode with default timing
        mode = MainMode()
        self.assertEqual(mode.mode, SCATTER)
        self.assertEqual(mode.time, 7)
        self.assertEqual(mode.timer, 0)

    def test_scatter_sets_mode_and_time(self):
        # Switching to scatter should reset mode, time, and timer
        mode = MainMode()
        mode.chase()  # switch to chase
        mode.scatter() # switch back to scatter
        self.assertEqual(mode.mode, SCATTER)
        self.assertEqual(mode.time, 7)
        self.assertEqual(mode.timer, 0)

    def test_chase_sets_mode_and_time(self):
        # Switching to chase should set correct chase time and reset timer
        mode = MainMode()
        mode.chase()
        self.assertEqual(mode.mode, CHASE)
        self.assertEqual(mode.time, 20)
        self.assertEqual(mode.timer, 0)

    def test_update_switches_from_scatter_to_chase(self):
        # When scatter time is up, update should switch to chase
        mode = MainMode()
        mode.timer = 7
        mode.time = 7
        mode.mode = SCATTER
        mode.update(1)
        self.assertEqual(mode.mode, CHASE)

    def test_update_switches_from_chase_to_scatter(self):
        # When chase time is up, update should switch back to scatter
        mode = MainMode()
        mode.chase()
        mode.timer = 20
        mode.time = 20
        mode.update(1)
        self.assertEqual(mode.mode, SCATTER)

class TestModeController(unittest.TestCase):
    def setUp(self):
        self.entity = MagicMock()
        self.entity.node = "node"
        self.entity.spawnNode = "spawn"
        self.entity.normalMode = MagicMock()
        self.mc = ModeController(self.entity)

    def test_initialization_sets_mainmode_and_current(self):
        mc = self.mc
        self.assertIsInstance(mc.mainmode, MainMode)
        self.assertIn(mc.current, [SCATTER, CHASE])

    def test_update_in_freight_switches_to_mainmode_after_time(self):
        # Freight should revert to main mode when time expires
        mc = self.mc
        mc.current = FREIGHT
        mc.timer = 6
        mc.time = 7
        mc.entity.normalMode = MagicMock()
        mc.mainmode.mode = SCATTER
        mc.update(1.1)
        self.assertIsNone(mc.time)
        mc.entity.normalMode.assert_called_once()
        self.assertEqual(mc.current, mc.mainmode.mode)

    def test_update_in_scatter_or_chase_sets_current_to_mainmode(self):
        # Current mode must always follow MainMode when not in special modes
        mc = self.mc
        mc.current = SCATTER
        mc.mainmode.mode = CHASE
        mc.update(1)
        self.assertEqual(mc.current, CHASE)
        mc.current = CHASE
        mc.mainmode.mode = SCATTER
        mc.update(1)
        self.assertEqual(mc.current, SCATTER)

    def test_update_in_spawn_switches_to_mainmode_if_node_equals_spawnNode(self):
        # When cat reaches spawn point in SPAWN mode, return to mainmode
        mc = self.mc
        mc.current = SPAWN
        self.entity.node = self.entity.spawnNode
        mc.entity.normalMode = MagicMock()
        mc.mainmode.mode = CHASE
        mc.update(1)
        mc.entity.normalMode.assert_called_once()
        self.assertEqual(mc.current, CHASE)

    def test_setFreightMode_from_scatter_or_chase(self):
        # Enter freight mode from SCATTER should reset timer and duration
        mc = self.mc
        mc.current = SCATTER
        mc.setFreightMode()
        self.assertEqual(mc.timer, 0)
        self.assertEqual(mc.time, 7)
        self.assertEqual(mc.current, FREIGHT)
        # Also works if currently in CHASE
        mc.current = CHASE
        mc.setFreightMode()
        self.assertEqual(mc.current, FREIGHT)

    def test_setFreightMode_from_freight_only_resets_timer(self):
        # Re-applying freight just resets timer, not full reinitialization
        mc = self.mc
        mc.current = FREIGHT
        mc.timer = 5
        mc.setFreightMode()
        self.assertEqual(mc.timer, 0)
        self.assertEqual(mc.current, FREIGHT)

    def test_setSpawnMode_sets_current_to_spawn_if_in_freight(self):
        # Only ghosts in freight can be put in spawn mode
        mc = self.mc
        mc.current = FREIGHT
        mc.setSpawnMode()
        self.assertEqual(mc.current, SPAWN)

    def test_setSpawnMode_does_not_change_if_not_freight(self):
        # If not in freight mode, spawn mode should not apply
        mc = self.mc
        mc.current = SCATTER
        mc.setSpawnMode()
        self.assertEqual(mc.current, SCATTER)
