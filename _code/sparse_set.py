class SparseSet:
    def __init__(self, size):
        self.mem = [0] * size
        self.head = 0
        self.tail = 0
        self.ihead = 0

    def add(self, x):
        if self.head <= self.mem[self.ihead + x] < self.tail:
            return
        self.mem[self.tail] = x
        self.mem[self.ihead + x] = self.tail
        self.tail += 1

    def remove(self, x):
        if not (self.head <= self.mem[self.ihead + x] < self.tail):
            return
        if self.head == self.tail:
            return
        p = self.mem[self.ihead + x]  # 记录即将被删元素的指针
        self.tail -= 1
        if p != self.tail:
            y = self.mem[self.tail]
            self.mem[self.tail], self.mem[p] = self.mem[p], y  # 交换被删元素和末尾元素
            self.mem[self.ihead + x], self.mem[self.ihead + y] = self.tail, p  # 交换被删元素和末尾元素反向指针