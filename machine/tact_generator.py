
class TactGenerator:

    def __init__(self):
        self.tact = 0

    def set_tact(self, tact):
        self.tact = tact

    def tick(self):
        self.tact += 1

    def clean_tact(self):
        self.tact = 0
