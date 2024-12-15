import unittest
from algorithm_c import CommaFreeCode, Alpha, RED

class TestCommaFreeCode(unittest.TestCase):
    def test_p1_addition(self):
        m = 2
        g = 57
        code = CommaFreeCode(m, g)
        
        code.initialize()
        
        for i in range(code.base_power_4):
            al = Alpha(i, m)
            alf = code.prefix(al.to_hex())
            if code.state[i] != RED:
                self.assertIn(i, code.p1, f"Value {i} not found in p1[{alf}]")
                self.assertGreater(len(code.p1), 0, f"p1[{alf}] is unexpectedly empty")
            else:
                self.assertNotIn(i, code.p1, f"Unexpected value {i} found in p1[{alf}]")
        self.assertEqual(code.p1.ss_len(0), 5)
        self.assertEqual(code.p1.ss_len(0b1000), 5)

    def test_p2_addition(self):
        m = 2
        g = 57
        code = CommaFreeCode(m, g)
        
        code.initialize()
        
        for i in range(code.base_power_4):
            al = Alpha(i, m)
            alf = code.prefix2(al.to_hex())
            if code.state[i] != RED:
                self.assertIn(i, code.p2, f"Value {i} not found in p2[{alf}]")
                self.assertGreater(len(code.p2), 0, f"p2[{alf}] is unexpectedly empty")
            else:
                self.assertNotIn(i, code.p2, f"Unexpected value {i} found in p2[{alf}]")
        self.assertEqual(code.p2.ss_len(0), 3)
        self.assertEqual(code.p2.ss_len(0b0100), 2)
        self.assertEqual(code.p2.ss_len(0b1000), 2)
        self.assertEqual(code.p2.ss_len(0b1100), 3)

    def test_p3_addition(self):
        m = 2
        g = 57
        code = CommaFreeCode(m, g)
        
        code.initialize()
        
        for i in range(code.base_power_4):
            al = Alpha(i, m)
            alf = code.prefix3(al.to_hex())
            if code.state[i] != RED:
                self.assertIn(i, code.p3, f"Value {i} not found in p3[{alf}]")
                self.assertGreater(len(code.p3), 0, f"p3[{alf}] is unexpectedly empty")
            else:
                self.assertNotIn(i, code.p3, f"Unexpected value {i} found in p3[{alf}]")
        self.assertEqual(code.p3.ss_len(0), 1)
        self.assertEqual(code.p3.ss_len(0b0010), 2)
        self.assertEqual(code.p3.ss_len(0b0110), 2)
        self.assertEqual(code.p3.ss_len(0b1000), 1)
        self.assertEqual(code.p3.ss_len(0b1010), 1)
        self.assertEqual(code.p3.ss_len(0b1100), 2)
        self.assertEqual(code.p3.ss_len(0b1110), 1)

    def test_s1_addition(self):
        m = 2
        g = 57
        code = CommaFreeCode(m, g)
        
        code.initialize()
        
        for i in range(code.base_power_4):
            al = Alpha(i, m)
            alf = code.suffix(al.to_hex())
            if code.state[i] != RED:
                self.assertIn(i, code.s1, f"Value {i} not found in s1[{alf}]")
                self.assertGreater(len(code.s1), 0, f"s1[{alf}] is unexpectedly empty")
            else:
                self.assertNotIn(i, code.s1, f"Unexpected value {i} found in s1[{alf}]")
        self.assertEqual(code.s1.ss_len(0b0010), 4)
        self.assertEqual(code.s1.ss_len(0b1100), 4)
        self.assertEqual(code.s1.ss_len(0b1), 6)
        self.assertEqual(code.s1.ss_len(0b111), 6)

    def test_s2_addition(self):
        m = 2
        g = 57
        code = CommaFreeCode(m, g)
        
        code.initialize()
        
        for i in range(code.base_power_4):
            al = Alpha(i, m)
            alf = code.suffix2(al.to_hex())
            if code.state[i] != RED:
                self.assertIn(i, code.s2, f"Value {i} not found in s2[{alf}]")
                self.assertGreater(len(code.s2), 0, f"s2[{alf}] is unexpectedly empty")
            else:
                self.assertNotIn(i, code.s2, f"Unexpected value {i} found in s2[{alf}]")
        self.assertEqual(code.s2.ss_len(0b1100), 1)
        self.assertEqual(code.s2.ss_len(0b1), 3)
        self.assertEqual(code.s2.ss_len(0b10), 3)
        self.assertEqual(code.s2.ss_len(0b11), 3)

    def test_s3_addition(self):
        m = 2
        g = 57
        code = CommaFreeCode(m, g)
        
        code.initialize()
        
        for i in range(code.base_power_4):
            al = Alpha(i, m)
            alf = code.suffix3(al.to_hex())
            if code.state[i] != RED:
                self.assertIn(i, code.s3, f"Value {i} not found in s3[{alf}]")
                self.assertGreater(len(code.s3), 0, f"s3[{alf}] is unexpectedly empty")
            else:
                self.assertNotIn(i, code.s3, f"Unexpected value {i} found in s3[{alf}]")
        self.assertEqual(code.s3.ss_len(0b1), 2)
        self.assertEqual(code.s3.ss_len(0b0010), 1)
        self.assertEqual(code.s3.ss_len(0b11), 2)
        self.assertEqual(code.s3.ss_len(0b1100), 1)
        self.assertEqual(code.s3.ss_len(0b1101), 1)
        self.assertEqual(code.s3.ss_len(0b110), 2)
        self.assertEqual(code.s3.ss_len(0b0111), 1)

if __name__ == '__main__':
    unittest.main() 