import unittest
from sparse_set import SparseSet

class TestSparseSet(unittest.TestCase):

    def setUp(self):
        self.sparse_set = SparseSet(10)

    def test_add(self):
        self.sparse_set.add(3)
        self.assertEqual(self.sparse_set.mem[self.sparse_set.tail - 1], 3)

    def test_remove(self):
        self.sparse_set.add(3)
        self.sparse_set.remove(3)
        self.assertNotIn(3, self.sparse_set)

    def test_add_duplicate(self):
        self.sparse_set.add(3)
        self.sparse_set.add(3)
        self.assertEqual(self.sparse_set.tail, 1)

    def test_remove_nonexistent(self):
        self.sparse_set.remove(3)
        self.assertEqual(self.sparse_set.tail, 0)

    def test_add_and_remove_multiple(self):
        elements = [1, 2, 3, 4, 5]
        for elem in elements:
            self.sparse_set.add(elem)
        for elem in elements:
            self.sparse_set.remove(elem)
        self.assertEqual(self.sparse_set.tail, 0)

    def test_complex_operations(self):
        self.sparse_set.add(1)
        self.sparse_set.add(2)
        self.sparse_set.add(3)
        self.assertEqual(self.sparse_set.tail, 3)

        self.sparse_set.remove(2)
        self.assertNotIn(2, self.sparse_set)
        self.assertEqual(self.sparse_set.tail, 2)

        self.sparse_set.add(4)
        self.sparse_set.add(5)
        self.assertEqual(self.sparse_set.tail, 4)

        self.sparse_set.remove(1)
        self.assertNotIn(1, self.sparse_set)
        self.assertEqual(self.sparse_set.tail, 3)

        self.sparse_set.add(6)
        self.assertEqual(self.sparse_set.tail, 4)

        expected_elements = {3, 4, 5, 6}
        actual_elements = set(self.sparse_set)
        self.assertEqual(expected_elements, actual_elements)

    def test_iterator(self):
        elements = [1, 2, 3]
        for elem in elements:
            self.sparse_set.add(elem)
        self.assertEqual(set(self.sparse_set), set(elements))

if __name__ == '__main__':
    unittest.main()