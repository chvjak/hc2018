class Bitfield:
    def __init__(self, N):
        self.INT_SIZE = 4096 # bits
        self.data = [0] * (N // self.INT_SIZE + 1)

    def set(self, i):
        self.data[i // self.INT_SIZE] |= 1 << (i % self.INT_SIZE)

    def get(self, i):
        return 0 != self.data[i // self.INT_SIZE] & (1 << (i % self.INT_SIZE))

    def merge(self, other):
        for i in range(len(self.data)):
            self.data[i] |= other.data[i]

