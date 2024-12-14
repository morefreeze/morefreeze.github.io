import unittest
from algorithm_c import CommaFreeCode, Alpha, RED

class TestCommaFreeCode(unittest.TestCase):
    def test_p1_addition(self):
        m = 2
        g = 57
        code = CommaFreeCode(m, g)
        
        # Initialize the code to set up the state and p1
        code.initialize()
        
        # Check that p1 has been populated correctly
        for i in range(code.base_power_4):
            if code.state[i] != RED:
                al = Alpha(i, m)
                alf = code.prefix(al.to_hex())
                self.assertIn(i, code.p1[alf], f"Value {i} not found in p1[{alf}]")

if __name__ == '__main__':
    unittest.main() 