import unittest
from algorithm_c import Alpha

class TestAlpha(unittest.TestCase):
    def test_alpha_0to_str(self):
        alpha = Alpha(0, 2)
        self.assertEqual(alpha.to_str(), '0')

    def test_alpha_5to_hex(self):
        alpha = Alpha(5, 2)
        self.assertEqual(alpha.to_hex(), 0x101)

    def test_alpha_to_str(self):
        alpha = Alpha(10, 2)
        self.assertEqual(alpha.to_str(), '1010')

    def test_alpha_to_int(self):
        alpha = Alpha(10, 2)
        self.assertEqual(alpha.to_int(), 10)

    def test_alpha_to_hex(self):
        alpha = Alpha(10, 2)
        self.assertEqual(alpha.to_hex(), 0x1010)

    def test_alpha_to_str_m3(self):
        alpha = Alpha(10, 3)
        self.assertEqual(alpha.to_str(), '101')

    def test_alpha_to_int_m3(self):
        alpha = Alpha(10, 3)
        self.assertEqual(alpha.to_int(), 10)

    def test_alpha_to_hex_m3(self):
        alpha = Alpha(10, 3)
        self.assertEqual(alpha.to_hex(), 0x101)

    def test_alpha_to_str_m4(self):
        alpha = Alpha(10, 4)
        self.assertEqual(alpha.to_str(), '22')

    def test_alpha_to_int_m4(self):
        alpha = Alpha(10, 4)
        self.assertEqual(alpha.to_int(), 10)

    def test_alpha_to_hex_m4(self):
        alpha = Alpha(10, 4)
        self.assertEqual(alpha.to_hex(), 0x22)


if __name__ == '__main__':
    unittest.main()