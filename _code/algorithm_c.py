from collections import defaultdict
from sparse_set import SparseSet


BLUE = 0
GREEN = 1
RED = 2
n = 4 # number of bits in the code

class Alpha:
    def __init__(self, x: int, m: int):
        self.x = x
        self.m = m
        self._s = None

    @staticmethod
    def from_str(s, m):
        return Alpha(int(s, m), m)
    
    def to_str(self):
        '''convert to m bit string'''
        if self._s is None:
            if self.x == 0:
                self._s = '0000'
                return self._s
            x = self.x
            s = ''
            while x > 0:
                s = str(x % self.m) + s
                x = x // self.m
            self._s = s.zfill(n)
        return self._s
    
    def to_int(self):
        return self.x
    
    def to_hex(self) -> int:
        hex_str = self.to_str()
        return int(hex_str, 16)

class CommaFreeCode:
    def __init__(self, m, g):
        self.m = m
        self.base_power_4 = m ** 4
        self.code_length = (self.base_power_4 - m ** 2) // 4
        self.memory_size = int(23.5 * self.base_power_4)
        self.state = [BLUE] * self.base_power_4
        self.p1 = defaultdict(lambda : SparseSet(self.base_power_4))
        self.p2 = defaultdict(lambda : SparseSet(self.base_power_4))
        self.p3 = defaultdict(lambda : SparseSet(self.base_power_4))
        self.s1 = defaultdict(lambda : SparseSet(self.base_power_4))
        self.s2 = defaultdict(lambda : SparseSet(self.base_power_4))
        self.s3 = defaultdict(lambda : SparseSet(self.base_power_4))
        self.cl = defaultdict(lambda : SparseSet(self.base_power_4))
        self.alf = [0] * 16**3 * self.m
        self.stamp = [0] * self.memory_size
        self.sigma = 0
        self.poison_value = 22 * self.base_power_4
        self.poison_pointer = self.poison_value - 1
        self.initialize()


    def initialize(self):
        # Initialize ALF, timestamp, and other structures
        for i in range(self.base_power_4):
            alf = Alpha(i, self.m)
            a = alf.to_str()
            if a[:2] == a[-2:]:
                self.state[i] = RED
            else:
                self.state[i] = BLUE
            tt = alf.to_hex()
            self.alf[tt] = alf
        # 0100 is red because I've chosen 0001
        self.state[Alpha.from_str('0100', self.m).to_int()] = RED
        self.state[Alpha.from_str('1000', self.m).to_int()] = RED
        for i in range(self.base_power_4):
            if self.state[i] != RED:
                al = Alpha(i, self.m)
                self.p1[self.prefix(al.to_hex())].add(i)
                self.p2[self.prefix2(al.to_hex())].add(i)
                self.p3[self.prefix3(al.to_hex())].add(i)
                self.s1[self.suffix(al.to_hex())].add(i)
                self.s2[self.suffix2(al.to_hex())].add(i)
                self.s3[self.suffix3(al.to_hex())].add(i)
                # self.cl[self.cl(al.to_hex())].add(i)

    def prefix(self, alpha):
        return (alpha & 0xF000)

    def prefix2(self, alpha):
        return (alpha & 0xFF00)

    def prefix3(self, alpha):
        return (alpha & 0xFFF0)

    def suffix(self, alpha):
        return (alpha & 0x000F) << 12

    def suffix2(self, alpha):
        return (alpha & 0x00FF) << 8

    def suffix3(self, alpha):
        return (alpha & 0x0FFF) << 4

    def cl(self, alpha):
        # Implement the logic to calculate cl(alpha)
        return alpha

    # def search(self):
        # while True:
        #     if self.level > self.code_length:
        #         self.visit_solution()
        #         self.level -= 1
        #         if self.level == 0:
        #             break
        #         self.trial_word = self.solution_vector[self.level]
        #         self.trial_class = self.current_index[self.level]
        #         self.free_index += 1
        #         if self.trial_word < 0:
        #             continue
        #         self.slack = self.current_state[self.level]
        #         self.undo_to(self.undo_stack_pointer[self.level])
        #         self.bump_stamp()
        #         self.redden(self.trial_word)
        #     else:
        #         self.undo_stack_pointer[self.level] = self.undo_pointer
        #         self.current_stamp += 1
        #         if self.trial_word < 0:
        #             if self.slack == 0 or self.level == 1:
        #                 self.level -= 1
        #                 if self.level == 0:
        #                     break
        #                 self.trial_word = self.solution_vector[self.level]
        #                 self.trial_class = self.current_index[self.level]
        #                 self.free_index += 1
        #                 if self.trial_word < 0:
        #                     continue
        #                 self.slack = self.current_state[self.level]
        #                 self.undo_to(self.undo_stack_pointer[self.level])
        #                 self.bump_stamp()
        #                 self.redden(self.trial_word)
        #             else:
        #                 self.slack -= 1
        #         else:
        #             self.make_green(self.trial_word)
        #             self.solution_vector[self.level] = self.trial_word
        #             self.current_index[self.level] = self.trial_class
        #             self.current_state[self.level] = self.slack
        #             p = self.index_free_list[self.trial_class]
        #             self.free_index -= 1
        #             if p != self.free_index:
        #                 y = self.free_list[self.free_index]
        #                 self.free_list[p] = y
        #                 self.index_free_list[y] = p
        #                 self.free_list[self.free_index] = self.trial_class
        #                 self.index_free_list[self.trial_class] = self.free_index
        #             self.level += 1

    def visit_solution(self):
        # Process the solution found
        print("Solution found:", self.solution_vector[1:self.code_length + 1])

    def make_green(self, x):
        # Update data structures to make x green
        pass

    def redden(self, x):
        # Update data structures to make x red
        pass

    def undo_to(self, u0):
        while self.undo_pointer > u0:
            self.undo_pointer -= 1
            packed = self.undo_stack.pop()
            address = packed >> 16
            old_value = packed & 0xFFFF
            self.memory[address] = old_value

    def bump_stamp(self):
        self.current_stamp += 1
        if self.current_stamp == 0:
            self.current_stamp = 1
            self.stamp = [0] * len(self.stamp)

if __name__ == '__main__':
    # Example usage
    code = CommaFreeCode(m=4, g=57)
    code.initialize()
    # code.search()