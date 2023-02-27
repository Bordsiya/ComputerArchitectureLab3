import enum


class Addressing(enum.Enum):
    ABSOLUTE = '$command $$arg'
    DIRECT = '$command #$arg'
    RELATIVE = '$command ($arg)'


class AddressedCommand:
    mnemonic: str
    binary: chr

    def __init__(self, mnemonic, binary):
        self.mnemonic = mnemonic
        self.binary = binary

    def get_mnemonic(self):
        return self.mnemonic

    def get_binary(self):
        return self.binary

    def get_addr_mnemonic(self, arg, addr_type):
        if addr_type == Addressing.ABSOLUTE:
            match_str = Addressing.ABSOLUTE.value
        elif addr_type == Addressing.DIRECT:
            match_str = Addressing.DIRECT.value
        else:
            match_str = Addressing.RELATIVE.value
        ans = match_str.replace('$command', self.mnemonic)
        ans = ans.replace('$arg', arg)
        return ans


class AddressedCommandType:
    ADD = AddressedCommand("ADD", '1')
    SUB = AddressedCommand("SUB", '2')
    DIV = AddressedCommand("DIV", '3')
    MUL = AddressedCommand("MUL", '4')
    MOD = AddressedCommand("MOD", '5')
    CMP = AddressedCommand("CMP", '6')
    LOOP = AddressedCommand("LOOP", '7')
    LD = AddressedCommand("LD", '8')
    ST = AddressedCommand("ST", '9')
    JUMP = AddressedCommand("JUMP", 'A')
    BEQ = AddressedCommand("BEQ", 'F0')
    BNE = AddressedCommand("BNE", 'F1')
    BGE = AddressedCommand("BGE", 'F2')
    BLE = AddressedCommand("BLE", 'F3')
    BL = AddressedCommand("BL", 'F4')
    BG = AddressedCommand("BG", 'F5')


