
class Device:

    def __init__(self):
        self.io = 0
        self.input = []
        self.output = []
        self.read_ind = 0

    def read(self):
        if self.read_ind >= len(self.input):
            raise EOFError("Buffer is empty")
        self.io = self.input[self.read_ind]
        self.read_ind += 1

    def write(self):
        self.output.append(self.io)

    def load(self, data):
        self.input = data
        self.read_ind = 0
