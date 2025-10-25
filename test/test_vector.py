import unittest
import math
from CheeseChase.model.vector import Vector2

class TestVector2(unittest.TestCase):
    def test_init_defaults(self):
        v = Vector2()
        self.assertEqual(v.x, 0)
        self.assertEqual(v.y, 0)
        self.assertAlmostEqual(v.thresh, 0.000001)

    def test_init_custom(self):
        v = Vector2(3, 4)
        self.assertEqual(v.x, 3)
        self.assertEqual(v.y, 4)

    def test_add(self):
        v1 = Vector2(1, 2)
        v2 = Vector2(3, 4)
        v3 = v1 + v2
        self.assertEqual(v3.x, 4)
        self.assertEqual(v3.y, 6)

    def test_sub(self):
        v1 = Vector2(5, 7)
        v2 = Vector2(2, 3)
        v3 = v1 - v2
        self.assertEqual(v3.x, 3)
        self.assertEqual(v3.y, 4)

    def test_neg(self):
        v = Vector2(2, -3)
        nv = -v
        self.assertEqual(nv.x, -2)
        self.assertEqual(nv.y, 3)

    def test_mul(self):
        v = Vector2(2, 3)
        m = v * 5
        self.assertEqual(m.x, 10)
        self.assertEqual(m.y, 15)

    def test_div(self):
        v = Vector2(10, 20)
        d = v / 5
        self.assertEqual(d.x, 2.0)
        self.assertEqual(d.y, 4.0)

    def test_div_zero(self):
        # Division by zero should safely return None instead of raising
        v = Vector2(1, 1)
        self.assertIsNone(v / 0)

    def test_eq_true(self):
        # Vectors within threshold tolerance should be considered equal
        v1 = Vector2(1.0000001, 2.0000001)
        v2 = Vector2(1.0000002, 2.0000002)
        self.assertTrue(v1 == v2)

    def test_eq_false(self):
        # Different coordinates means not equal
        v1 = Vector2(1, 2)
        v2 = Vector2(2, 1)
        self.assertFalse(v1 == v2)

    def test_magnitudeSquared(self):
        # Magnitude squared should be x² + y²
        v = Vector2(3, 4)
        self.assertEqual(v.magnitudeSquared(), 25)

    def test_magnitude(self):
        # Magnitude should return Euclidean length: sqrt(x² + y²)
        v = Vector2(3, 4)
        self.assertEqual(v.magnitude(), 5)

    def test_copy(self):
        # Copy returns a new Vector2 with the same values but different reference
        v = Vector2(7, 8)
        c = v.copy()
        self.assertEqual(c.x, 7)
        self.assertEqual(c.y, 8)
        self.assertIsInstance(c, Vector2)
        self.assertFalse(c is v)

    def test_asTuple(self):
        # Converts vector to a simple (x, y) tuple
        v = Vector2(5, 6)
        self.assertEqual(v.asTuple(), (5, 6))

    def test_asInt(self):
        # Converts vector to integer tuple by floor-casting components
        v = Vector2(5.9, 6.1)
        self.assertEqual(v.asInt(), (5, 6))

    def test_str(self):
        # String representation should be "<x, y>"
        v = Vector2(2, 3)
        self.assertEqual(str(v), "<2, 3>")
