import enum
import json
from collections import namedtuple


class Opcode(str, enum.Enum):
    DATA = "DATA"
    # addressed commands
    ADD = "ADD"
    SUB = "SUB"
    DIV = "DIV"
    MUL = "MUL"
    MOD = "MOD"
    CMP = "CMP"
    LOOP = "LOOP"
    LD = "LD"
    ST = "ST"
    JUMP = "JUMP"
    BEQ = "BEQ"
    BNE = "BNE"
    BGE = "BGE"
    BLE = "BLE"
    BL = "BL"
    BG = "BG"
    # unaddressed commands
    NOP = "NOP"
    HLT = "HLT"
    CLA = "CLA"
    IN = "IN"
    OUT = "OUT"
    INC = "INC"
    DEC = "DEC"
    NEG = "NEG"


addressed_commands = [Opcode.ADD, Opcode.SUB, Opcode.DIV, Opcode.MUL, Opcode.MOD, Opcode.CMP, Opcode.LOOP, Opcode.LD,
                      Opcode.ST, Opcode.JUMP, Opcode.BEQ, Opcode.BNE, Opcode.BGE, Opcode.BLE, Opcode.BL, Opcode.BG]

unaddressed_commands = [Opcode.NOP, Opcode.HLT, Opcode.CLA, Opcode.IN, Opcode.OUT, Opcode.INC, Opcode.DEC, Opcode.NEG]


class AddressingMode(str, enum.Enum):
    ABSOLUTE = "ABSOLUTE"
    DIRECT = "DIRECT"
    RELATIVE = "RELATIVE"


class Term(namedtuple("Term", "opcode arg arg_mode")):
    """Instruction description"""


def write_code(filename, code):
    with open(filename, "w", encoding="utf-8") as file:
        file.write(json.dumps(code, indent=4))


def read_code(filename):
    with open(filename, encoding="utf-8") as file:
        code = json.loads(file.read())

    for instr in code:
        instr['opcode'] = Opcode(instr['opcode'])
        if 'arg' in instr:
            instr['arg_mode'] = AddressingMode(instr['arg_mode'])

    return code
