

class UnaddressedCommand:
    mnemonic: str
    binary: chr

    def __init__(self, mnemonic, binary):
        self.mnemonic = mnemonic
        self.binary = binary

    def get_mnemonic(self):
        return self.mnemonic

    def get_binary(self):
        return self.binary


class UnaddressedCommandType:
    NOP = UnaddressedCommand("NOP", '0000')
    HLT = UnaddressedCommand("HLT", '0100')
    CLA = UnaddressedCommand("CLA", '0200')
    IN = UnaddressedCommand("IN", '0300')
    OUT = UnaddressedCommand("OUT", '0400')
    INC = UnaddressedCommand("INC", '0500')
    DEC = UnaddressedCommand("DEC", '0600')
    NEG = UnaddressedCommand("NEG", '0700')
