import unittest
from CheeseChase.view.animation import Animator

class TestAnimator(unittest.TestCase):
    def setUp(self):
        # Use simple int frames for clarity
        self.frames = [1, 2, 3]
        self.speed = 2  # 2 frames per second
        self.anim = Animator(frames=self.frames, speed=self.speed, loop=True)

    def test_initialization_defaults(self):
        anim = Animator()
        self.assertEqual(anim.frames, [])
        self.assertEqual(anim.current_frame, 0)
        self.assertEqual(anim.speed, 20)
        self.assertTrue(anim.loop)
        self.assertEqual(anim.dt, 0)
        self.assertFalse(anim.finished)

    def test_reset(self):
        # reset() should restore state to the initial animation position
        self.anim.current_frame = 2
        self.anim.finished = True
        self.anim.reset()
        self.assertEqual(self.anim.current_frame, 0)
        self.assertFalse(self.anim.finished)

    def test_nextFrame_advances_when_dt_enough(self):
        # When enough time has passed (dt >= step time), the frame should advanc
        self.anim.dt = 0.5 # threshold for speed=2 fps
        self.anim.nextFrame(0.5)
        self.assertEqual(self.anim.current_frame, 1)
        self.assertEqual(self.anim.dt, 0)  # dt should reset after step

    def test_nextFrame_not_advance_when_dt_too_small(self):
        # If not enough time passed, it should accumulate dt without frame change
        self.anim.dt = 0.0
        self.anim.nextFrame(0.2)  # 0.2 < 1/2
        self.assertEqual(self.anim.current_frame, 0)
        self.assertAlmostEqual(self.anim.dt, 0.2)

    def test_update_advances_frame_and_loops(self):
        # Simulate update enough times to reach end and loop
        self.anim.dt = 0.5
        self.anim.current_frame = 2 # last frame index
        frame = self.anim.update(0.5)  # Should wrap to 0
        self.assertEqual(self.anim.current_frame, 0) # looped back
        self.assertEqual(frame, 1) # first frame
        self.assertFalse(self.anim.finished) # should not be finished

    def test_update_advances_frame_and_finishes_if_not_loop(self):
        # Without looping, reaching last frame marks animation finished
        anim = Animator(frames=self.frames, speed=self.speed, loop=False)
        anim.current_frame = 2
        anim.dt = 0.5
        frame = anim.update(0.5)  # Should finish
        self.assertEqual(anim.current_frame, 2) # stays at last frame
        self.assertTrue(anim.finished) # should be finished
        self.assertEqual(frame, 3) # last frame

    def test_update_returns_correct_frame(self):
        # update() should always return the current frame's value
        self.anim.current_frame = 1
        frame = self.anim.update(0.1)
        self.assertEqual(frame, 2)

    def test_update_with_empty_frames(self):
        # If no frames exist, update should safely return None instead of crashing
        anim = Animator(frames=[], speed=self.speed)
        frame = anim.update(0.1)
        self.assertEqual(frame, None)  # Should not error
