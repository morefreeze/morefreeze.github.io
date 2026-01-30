class SparseSet:
    def __init__(self, size):
        self.mem = [0] * size
        self.index = [-1] * size
        self.tail = 0

    def add(self, x):
        if self.index[x] == -1:
            self.mem[self.tail] = x
            self.index[x] = self.tail
            self.tail += 1

    def __len__(self):
        return self.tail

    def remove(self, x):
        if self.index[x] != -1:
            last_element = self.mem[self.tail - 1]
            pos = self.index[x]
            self.mem[pos] = last_element
            self.index[last_element] = pos
            self.index[x] = -1
            self.tail -= 1

    def __iter__(self):
        for i in range(self.tail):
            yield self.mem[i]

    def __contains__(self, x):
        return self.index[x] != -1
