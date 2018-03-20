class Bitfield:
    def __init__(self, N):
        self.INT_SIZE = 32   # bits
        self.data = [0] * (N // self.INT_SIZE + 1)

    def set(self, i):
        self.data[i // self.INT_SIZE] |= 1 << (i % self.INT_SIZE)

    def get(self, i):
        return 0 != self.data[i // self.INT_SIZE] & (1 << (i % self.INT_SIZE))

    def merge(self, other):
        for i in range(len(self.data)):
            self.data[i] |= other.data[i]


bf = Bitfield(10)

bf.set(1)
bf.set(5)
bf.set(7)

for i in range(10):
    print(i, bf.get(i))

bf2 = Bitfield(10)

bf2.set(2)
bf2.set(4)
bf2.set(6)

bf.merge(bf2)
print()
for i in range(10):
    print(i, bf.get(i))
