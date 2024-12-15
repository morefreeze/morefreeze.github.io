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
                self.assertIn(i, code.p1[alf], f"Value {i} not found in p1[{alf}]")
                self.assertGreater(len(code.p1[alf]), 0, f"p1[{alf}] is unexpectedly empty")
            else:
                self.assertNotIn(i, code.p1[alf], f"Unexpected value {i} found in p1[{alf}]")
        self.assertEqual(len(code.p1[Alpha(0x0, 16).to_hex()]), 5)
        self.assertEqual(len(code.p1[Alpha(0x1000, 16).to_hex()]), 5)

    def test_p2_addition(self):
        m = 2
        g = 57
        code = CommaFreeCode(m, g)
        
        code.initialize()
        
        for i in range(code.base_power_4):
            al = Alpha(i, m)
            alf = code.prefix2(al.to_hex())
            if code.state[i] != RED:
                self.assertIn(i, code.p2[alf], f"Value {i} not found in p2[{alf}]")
                self.assertGreater(len(code.p2[alf]), 0, f"p2[{alf}] is unexpectedly empty")
            else:
                self.assertNotIn(i, code.p2[alf], f"Unexpected value {i} found in p2[{alf}]")
        self.assertEqual(len(code.p2[Alpha(0x0, 16).to_hex()]), 3)
        self.assertEqual(len(code.p2[Alpha(0x0100, 16).to_hex()]), 2)
        self.assertEqual(len(code.p2[Alpha(0x1000, 16).to_hex()]), 2)
        self.assertEqual(len(code.p2[Alpha(0x1100, 16).to_hex()]), 3)

    def test_p3_addition(self):
        m = 2
        g = 57
        code = CommaFreeCode(m, g)
        
        code.initialize()
        
        for i in range(code.base_power_4):
            al = Alpha(i, m)
            alf = code.prefix3(al.to_hex())
            if code.state[i] != RED:
                self.assertIn(i, code.p3[alf], f"Value {i} not found in p3[{alf}]")
                self.assertGreater(len(code.p3[alf]), 0, f"p3[{alf}] is unexpectedly empty")
            else:
                self.assertNotIn(i, code.p3[alf], f"Unexpected value {i} found in p3[{alf}]")
        self.assertEqual(len(code.p3[Alpha(0x0, 16).to_hex()]), 1)
        self.assertEqual(len(code.p3[Alpha(0x0010, 16).to_hex()]), 2)
        self.assertEqual(len(code.p3[Alpha(0x0110, 16).to_hex()]), 2)
        self.assertEqual(len(code.p3[Alpha(0x1000, 16).to_hex()]), 1)
        self.assertEqual(len(code.p3[Alpha(0x1010, 16).to_hex()]), 1)
        self.assertEqual(len(code.p3[Alpha(0x1100, 16).to_hex()]), 2)
        self.assertEqual(len(code.p3[Alpha(0x1110, 16).to_hex()]), 1)

    def test_s1_addition(self):
        m = 2
        g = 57
        code = CommaFreeCode(m, g)
        
        code.initialize()
        
        for i in range(code.base_power_4):
            al = Alpha(i, m)
            alf = code.suffix(al.to_hex())
            if code.state[i] != RED:
                self.assertIn(i, code.s1[alf], f"Value {i} not found in s1[{alf}]")
                self.assertGreater(len(code.s1[alf]), 0, f"s1[{alf}] is unexpectedly empty")
            else:
                self.assertNotIn(i, code.s1[alf], f"Unexpected value {i} found in s1[{alf}]")
        self.assertEqual(len(code.s1[Alpha(0x0, 16).to_hex()]), 4)
        self.assertEqual(len(code.s1[Alpha(0x1000, 16).to_hex()]), 6)

    def test_s2_addition(self):
        m = 2
        g = 57
        code = CommaFreeCode(m, g)
        
        code.initialize()
        
        for i in range(code.base_power_4):
            al = Alpha(i, m)
            alf = code.suffix2(al.to_hex())
            if code.state[i] != RED:
                self.assertIn(i, code.s2[alf], f"Value {i} not found in s2[{alf}]")
                self.assertGreater(len(code.s2[alf]), 0, f"s2[{alf}] is unexpectedly empty")
            else:
                self.assertNotIn(i, code.s2[alf], f"Unexpected value {i} found in s2[{alf}]")
        self.assertEqual(len(code.s2[Alpha(0x0, 16).to_hex()]), 1)
        self.assertEqual(len(code.s2[Alpha(0x0100, 16).to_hex()]), 3)
        self.assertEqual(len(code.s2[Alpha(0x1000, 16).to_hex()]), 3)
        self.assertEqual(len(code.s2[Alpha(0x1100, 16).to_hex()]), 3)

    def test_s3_addition(self):
        m = 2
        g = 57
        code = CommaFreeCode(m, g)
        
        code.initialize()
        
        for i in range(code.base_power_4):
            al = Alpha(i, m)
            alf = code.suffix3(al.to_hex())
            if code.state[i] != RED:
                self.assertIn(i, code.s3[alf], f"Value {i} not found in s3[{alf}]")
                self.assertGreater(len(code.s3[alf]), 0, f"s3[{alf}] is unexpectedly empty")
            else:
                self.assertNotIn(i, code.s3[alf], f"Unexpected value {i} found in s3[{alf}]")
        self.assertEqual(len(code.s3[Alpha(0x0010, 16).to_hex()]), 2)
        self.assertEqual(len(code.s3[Alpha(0x0100, 16).to_hex()]), 1)
        self.assertEqual(len(code.s3[Alpha(0x0110, 16).to_hex()]), 2)
        self.assertEqual(len(code.s3[Alpha(0x1000, 16).to_hex()]), 1)
        self.assertEqual(len(code.s3[Alpha(0x1010, 16).to_hex()]), 1)
        self.assertEqual(len(code.s3[Alpha(0x1100, 16).to_hex()]), 2)
        self.assertEqual(len(code.s3[Alpha(0x1110, 16).to_hex()]), 1)

if __name__ == '__main__':
    unittest.main() 