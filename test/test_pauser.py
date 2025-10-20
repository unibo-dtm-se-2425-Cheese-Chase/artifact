import unittest

from CheeseChase.controller.pauser import Pause

class TestPause(unittest.TestCase):
    def test_initial_state(self):
        p = Pause()
        self.assertFalse(p.paused)
        self.assertEqual(p.timer, 0)
        self.assertIsNone(p.pauseTime)
        self.assertIsNone(p.func)

    def test_initial_state_paused_true(self):
        p = Pause(paused=True)
        self.assertTrue(p.paused)

    def test_flip(self):
        p = Pause()
        self.assertFalse(p.paused)
        p.flip()
        self.assertTrue(p.paused)
        p.flip()
        self.assertFalse(p.paused)

    def test_setPause_sets_attributes_and_flips(self):
        p = Pause()
        # Start unpaused, flip should make paused True
        def sample_func(): return "done"

        p.setPause(playerPaused=True, pauseTime=2, func=sample_func)
        self.assertEqual(p.timer, 0)
        self.assertEqual(p.func, sample_func)
        self.assertEqual(p.pauseTime, 2)
        self.assertTrue(p.paused)

    def test_update_no_pauseTime_returns_none(self):
        p = Pause()
        result = p.update(1)
        self.assertIsNone(result)

    def test_update_timer_not_enough_returns_none(self):
        p = Pause(paused=True)
        p.func = lambda: "ok"
        p.pauseTime = 5
        p.timer = 2
        result = p.update(2)  # 2+2 = 4 < 5
        self.assertIsNone(result)
        self.assertEqual(p.timer, 4)
        self.assertTrue(p.paused)  # Still paused

    def test_update_timer_enough_returns_func_and_resets(self):
        called = []
        def sample_func(): called.append(True); return "ok"
        p = Pause(paused=True)
        p.func = sample_func
        p.pauseTime = 3
        p.timer = 2
        result = p.update(2)  # 2+2 = 4 >= 3
        self.assertEqual(result, sample_func)
        self.assertEqual(p.timer, 0)
        self.assertFalse(p.paused)
        self.assertIsNone(p.pauseTime)
        # Actually calling the returned function (optional)
        self.assertEqual(result(), "ok")
        self.assertTrue(called)