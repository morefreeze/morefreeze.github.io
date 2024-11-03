import unittest
from .langford import find_pairs

class TestLangfordPairs(unittest.TestCase):
    def setUp(self):
        """Set up any necessary test fixtures"""
        pass

    def test_invalid_input(self):
        """Test with invalid inputs (n < 1)"""
        self.assertEqual(find_pairs(0), [])
        self.assertEqual(find_pairs(-1), [])

    def test_small_valid_inputs(self):
        """Test with small valid inputs where solutions exist"""
        # Test n=2
        result = find_pairs(2)
        expected = [(2, 1, 2, 1)]
        self.assertEqual(result, expected)

        # Test n=3
        result = find_pairs(3)
        expected = [(3, 1, 2, 1, 3, 2)]
        self.assertEqual(result, expected)

    def test_no_solution_case(self):
        """Test cases where no solution exists"""
        # n=5 has no solution
        self.assertEqual(find_pairs(5), [])

    def test_larger_valid_input(self):
        """Test with a larger valid input (n=4)"""
        result = find_pairs(4)
        expected = [
            (3, 1, 2, 1, 3, 4, 2, 4),
            (2, 3, 1, 2, 1, 4, 3, 4)
        ]
        # Sort both lists to ensure consistent comparison
        self.assertEqual(sorted(result), sorted(expected))

    def test_result_structure(self):
        """Test the structure of the returned results"""
        result = find_pairs(3)
        
        # Check that we get a list of tuples
        self.assertIsInstance(result, list)
        for sequence in result:
            self.assertIsInstance(sequence, tuple)
            
            # Check length is correct (should be 2n)
            self.assertEqual(len(sequence), 6)  # 2 * 3 = 6
            
            # Check that all numbers appear exactly twice
            for i in range(1, 4):
                self.assertEqual(sequence.count(i), 2)

    def test_langford_property(self):
        """Test that the results satisfy the Langford pairing property"""
        result = find_pairs(3)
        for sequence in result:
            # For each number in the sequence
            for num in range(1, 4):
                # Find the positions where this number appears
                positions = [i for i, x in enumerate(sequence) if x == num]
                self.assertEqual(len(positions), 2)  # Should appear exactly twice
                # Check that the gap between positions is num + 1
                self.assertEqual(positions[1] - positions[0], num + 1)

if __name__ == '__main__':
    unittest.main()