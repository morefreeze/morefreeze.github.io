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

class ThreeLines:
    def __init__(self, m, mask):
        # if mask starts with 1, it is a prefix set
        # if mask starts with 0, it is a suffix set
        self.m = m
        self.base_power_4 = m ** 4
        self.index = [-1] * self.base_power_4
        self.mem = [0] * self.base_power_4
        self.tail = [0] * self.base_power_4
        self.mask = mask
        self.shift = self.calculate_shift(mask)

    def calculate_shift(self, mask):
        if mask == 0x000F:
            return 12
        elif mask == 0x00FF:
            return 8
        elif mask == 0x0FFF:
            return 4
        return 0

    def start(self, x):
        alf = Alpha(x, self.m)
        hex_st = alf.to_hex() & self.mask if self.mask & 0x8000 else (alf.to_hex() & self.mask) << self.shift
        alf = Alpha(hex_st, 16)
        return int(alf.to_str(), self.m)

    def add(self, x):
        # x is hex number
        if self.index[x] == -1:
            st = self.start(x)
            self.index[x] = st + self.tail[st]
            self.mem[self.index[x]] = x
            self.tail[st] += 1

    def __len__(self):
        return sum([self.mem[i] != -1 for i in range(self.base_power_4)])
    
    def remove(self, x):
        if self.index[x] != -1:
            st = self.start(x)
            last_element = self.mem[self.tail[st] - 1]
            pos = self.index[x]
            self.mem[pos] = last_element
            self.index[last_element] = pos
            self.index[x] = -1
            self.tail[st] -= 1

    def ss_len(self, x):
        st = self.start(x)
        return self.tail[st]

    def __iter__(self):
        for i in range(self.base_power_4):
            if self.index[i] != -1:
                yield self.mem[i]

    def __contains__(self, x):
        return self.index[x] != -1

class CommaFreeCode:
    def __init__(self, m, g):
        self.m = m
        self.base_power_4 = m ** 4
        self.code_length = (self.base_power_4 - m ** 2) // 4
        self.memory_size = int(23.5 * self.base_power_4)
        self.state = [BLUE] * self.base_power_4
        self.p1 = ThreeLines(m, 0xF000)
        self.p2 = ThreeLines(m, 0xFF00)
        self.p3 = ThreeLines(m, 0xFFF0)
        self.s1 = ThreeLines(m, 0x000F)
        self.s2 = ThreeLines(m, 0x00FF)
        self.s3 = ThreeLines(m, 0x0FFF)
        # self.cl = ThreeLines(m, 0xFFFF)
        self.alf = [0] * 16**3 * self.m
        self.stamp = [0] * self.memory_size
        self.sigma = 0
        self.poison_value = 22 * self.base_power_4
        self.poison_pointer = self.poison_value - 1
        self.free = [0] * self.code_length
        self.ifree = [0] * self.code_length
        self.level = 0
        self.x = 0 # x is trial word
        self.trial_class = 0
        self.solution = []
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
                self.p1.add(i)
                self.p2.add(i)
                self.p3.add(i)
                self.s1.add(i)
                self.s2.add(i)
                self.s3.add(i)
        # for i in range(self.base_power_4):
        #     if self.state[i] != BLUE or self.
                # self.cl[self.cl(al.to_hex())].add(i)
        
        for i in range(self.code_length):
            self.free[i] = i
            self.ifree[i] = i

        # New initialization for search-related arrays
        self.solution_vector = [-1] * (self.code_length + 1)
        self.current_index = [0] * (self.code_length + 1)
        self.current_state = [0] * (self.code_length + 1)
        self.free_list = list(range(self.code_length))
        self.index_free_list = list(range(self.code_length))
        self.free_index = self.code_length
        self.undo_stack = []
        self.undo_pointer = 0
        self.current_stamp = 1

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

    def search(self):
        self.level = 1
        while True:
            if self.level > self.code_length:
                self.visit_solution()
                self.backtrack()
            else:
                self.enter_level()
                if self.trial_word < 0:
                    self.try_again()
                else:
                    self.make_move()

    def enter_level(self):
        if self.level > self.code_length:
            self.visit_solution()
        else:
            self.level += 1
            self.try_candidate()
            self.level -= 1
        self.backtrack()

    def try_candidate(self):
        self.trial_word = self.free_list[self.free_index]
        self.trial_class = self.index_free_list[self.free_index]
        self.free_index -= 1
        self.slack = self.current_state[self.level]
        self.undo_pointer = self.undo_stack_pointer[self.level]
        self.bump_stamp()
        self.make_red(self.trial_word)

    def try_again(self):
        if self.slack == 0 or self.level == 1:
            self.backtrack()
        else:
            self.slack -= 1

    def make_move(self):
        self.make_green(self.trial_word)
        self.solution_vector[self.level] = self.trial_word
        self.current_index[self.level] = self.trial_class
        self.current_state[self.level] = self.slack
        p = self.index_free_list[self.trial_class]
        self.free_index -= 1
        if p != self.free_index:
            y = self.free_list[self.free_index]
            self.free_list[p] = y
            self.index_free_list[y] = p
            self.free_list[self.free_index] = self.trial_class
            self.index_free_list[self.trial_class] = self.free_index
        self.level += 1

    def backtrack(self):
        self.level -= 1
        if self.level == 0:
            return
        self.trial_word = self.solution_vector[self.level]
        self.trial_class = self.current_index[self.level]
        self.free_index += 1
        if self.trial_word < 0:
            return
        self.slack = self.current_state[self.level]
        self.undo_to(self.undo_stack_pointer[self.level])
        self.bump_stamp()
        self.make_red(self.trial_word)

    def visit_solution(self):
        # Process the solution found
        print("Solution found:", self.solution_vector[1:self.code_length + 1])

    def make_green(self, x):
        # Update data structures to make x green
        self.state[x] = GREEN
        # Additional logic to update other structures if needed
        print(f"Word {x} is now GREEN.")

    def make_red(self, x):
        # Update data structures to make x red
        self.state[x] = RED
        # Additional logic to update other structures if needed
        print(f"Word {x} is now RED.")

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