import unittest
from algorithm_c import ThreeLines

class TestThreeLines(unittest.TestCase):
    def test_start_p1(self):
        # Create an instance of ThreeLines with m=2 and mask=0xF000
        three_lines = ThreeLines(m=2, mask=0xF000)
        
        # Test that start(2) returns 0
        self.assertEqual(three_lines.start(2), 0, "Expected start(2) to return 0 with mask 0xF000")
        self.assertEqual(three_lines.start(8), 8, "Expected start(8) to return 8 with mask 0xF000")
        self.assertEqual(three_lines.start(12), 8, "Expected start(12) to return 8 with mask 0xF000")

    def test_start_method_p2(self):
        # Create an instance of ThreeLines with m=2 and mask=0xFF00
        three_lines = ThreeLines(m=2, mask=0xFF00)
        
        # Test that start(2) returns a different expected value
        self.assertEqual(three_lines.start(2), 0, "Expected start(2) to return 0 with mask 0xFF00")
        self.assertEqual(three_lines.start(0b111), 0b100, "Expected start(0b111) to return 0b100 with mask 0xFF00")
        self.assertEqual(three_lines.start(0b1000), 0b1000, "Expected start(0b1000) to return 0b1000 with mask 0xFF00")
        self.assertEqual(three_lines.start(0b1110), 0b1100, "Expected start(0b1110) to return 0b1100 with mask 0xFF00")

    def test_start_method_s1(self):
        # Create an instance of ThreeLines with m=2 and mask=0x000F
        three_lines = ThreeLines(m=2, mask=0x000F)
        
        # Test that start(2) returns a different expected value
        self.assertEqual(three_lines.start(2), 0, "Expected start(2) to return 0 with mask 0x000F")
        self.assertEqual(three_lines.start(0b110), 0, "Expected start(0b110) to return 0 with mask 0x000F")
        self.assertEqual(three_lines.start(0b1110), 0, "Expected start(0b1110) to return 0 with mask 0x000F")
        self.assertEqual(three_lines.start(0b1), 0b1000, "Expected start(0b1) to return 0b1000 with mask 0x000F")
        self.assertEqual(three_lines.start(0b1101), 0b1000, "Expected start(0b1101) to return 0b1000 with mask 0x000F")

    def test_start_method_s2(self):
        # Create an instance of ThreeLines with m=2 and mask=0x00FF
        three_lines = ThreeLines(m=2, mask=0x00FF)
        
        # Test that start(3) returns a different expected value
        self.assertEqual(three_lines.start(3), 0b1100, "Expected start(3) to return 0b1100 with mask 0x00FF")
        self.assertEqual(three_lines.start(1), 0b100, "Expected start(3) to return 0b1100 with mask 0x00FF")
        self.assertEqual(three_lines.start(0b10), 0b1000, "Expected start(3) to return 0b1100 with mask 0x00FF")
        self.assertEqual(three_lines.start(0b11), 0b1100, "Expected start(3) to return 0b1100 with mask 0x00FF")
        self.assertEqual(three_lines.start(0b1101), 0b100, "Expected start(3) to return 0b1100 with mask 0x00FF")
        self.assertEqual(three_lines.start(0b1011), 0b1100, "Expected start(3) to return 0b1100 with mask 0x00FF")

if __name__ == '__main__':
    unittest.main() 