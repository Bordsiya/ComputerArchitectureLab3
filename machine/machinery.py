import enum
import logging
import sys

from exceptions import MachineException
from machine.device import Device
from machine.config import MEMORY_SIZE, WORD_INIT, START_ADDR, MAX_WORD, MIN_WORD
from isa import read_code, Opcode, Term, AddressingMode


class AluOperation(str, enum.Enum):
    ADD = "ADD"
    SUB = "SUB"
    MUL = "MUL"
    DIV = "DIV"
    MOD = "MOD"


opcode_to_alu_operation = {
    Opcode.ADD: AluOperation.ADD,
    Opcode.SUB: AluOperation.SUB,
    Opcode.MUL: AluOperation.MUL,
    Opcode.DIV: AluOperation.DIV,
    Opcode.MOD: AluOperation.MOD,
    Opcode.CMP: AluOperation.SUB
}


class ControlUnit:

    def __init__(self, program, device):
        self.memory = program
        for addr in range(len(self.memory), MEMORY_SIZE):
            self.memory.append({'opcode': Opcode.DATA, 'term': Term(addr, WORD_INIT, AddressingMode.DIRECT)})

        self.program_counter = START_ADDR
        self.acc = 0
        self.ar = 0
        self.dr = 0
        self.tact = 0
        self.device = device
        self.zero_flag = False
        self.negative_flag = False

    def tick(self):
        self.tact += 1

    def set_zero_flag(self, val: int):
        self.zero_flag = val == 0

    def set_negative_flag(self, val: int):
        self.negative_flag = val < 0

    def latch_ar(self, val: int):
        self.ar = int(val)

    def latch_dr(self, val: int):
        self.dr = int(val)

    def latch_acc(self, val: int):
        self.acc = int(val)

    def latch_program_counter(self, sel_next):
        if sel_next:
            self.program_counter += 1
        else:
            self.program_counter = self.dr

    @staticmethod
    def check_value(val):
        if val > MAX_WORD or val < MIN_WORD:
            raise MachineException('Overflow error!')
        return val

    def alu_calculate(self, operation, sel_left=True, sel_right=True):
        left_operand = self.acc if sel_left else 0
        right_operand = self.dr if sel_right else 0
        res = None
        if operation == AluOperation.ADD:
            res = left_operand + right_operand

        elif operation == AluOperation.SUB:
            res = left_operand - right_operand

        elif operation == AluOperation.MUL:
            res = left_operand * right_operand

        elif operation == AluOperation.DIV:
            if not right_operand:
                raise MachineException('Error! Trying to get DIV operation from 0')
            res = left_operand // right_operand

        elif operation == AluOperation.MOD:
            if not right_operand:
                raise MachineException('Error! Trying to get MOD operation from 0')
            res = left_operand % right_operand

        self.set_zero_flag(res)
        self.set_negative_flag(res)
        return self.check_value(res)

    def operand_fetch(self, term):
        if term[2] == AddressingMode.DIRECT:
            self.latch_dr(term[1])
            self.tick()
        elif term[2] == AddressingMode.ABSOLUTE:
            self.latch_ar(term[1])
            self.tick()
            self.latch_dr(self.memory[self.ar]['term'][1])
            self.tick()
        elif term[2] == AddressingMode.RELATIVE:
            self.latch_ar(term[1])
            self.tick()
            self.latch_dr(self.memory[self.ar]['term'][1])
            self.tick()
            self.latch_ar(self.dr)
            self.tick()
            self.latch_dr(self.memory[self.ar]['term'][1])
            self.tick()

    def decode_and_execute_instruction(self):
        instr = self.memory[self.program_counter]
        opcode = instr["opcode"]
        term = instr['term']

        if opcode is Opcode.HLT:
            raise StopIteration()

        elif opcode is Opcode.NOP:
            self.latch_program_counter(True)
            self.tick()

        elif opcode is Opcode.LD:
            self.operand_fetch(term)
            res = self.alu_calculate(AluOperation.ADD, False)
            self.latch_acc(res)
            self.tick()

            self.latch_program_counter(True)
            self.tick()

        elif opcode is Opcode.ST:
            self.latch_ar(term[1])
            self.tick()
            self.memory[self.ar] = {'opcode': Opcode.DATA, 'term': Term(self.ar, self.acc, AddressingMode.DIRECT)}
            self.tick()

            self.latch_program_counter(True)
            self.tick()

        elif opcode in [Opcode.ADD, Opcode.SUB, Opcode.MUL, Opcode.DIV, Opcode.MOD, Opcode.CMP]:
            self.operand_fetch(term)
            res = self.alu_calculate(opcode_to_alu_operation[opcode])
            if opcode not in Opcode.CMP:
                self.latch_acc(res)
            self.tick()

            self.latch_program_counter(True)
            self.tick()

        elif opcode == Opcode.INC:
            self.latch_dr(1)
            self.tick()
            res = self.alu_calculate(Opcode.ADD)
            self.latch_acc(res)
            self.tick()

            self.latch_program_counter(True)
            self.tick()

        elif opcode == Opcode.DEC:
            self.latch_dr(-1)
            self.tick()
            res = self.alu_calculate(Opcode.ADD)
            self.latch_acc(res)
            self.tick()

            self.latch_program_counter(True)
            self.tick()

        elif opcode == Opcode.CLA:
            self.latch_acc(0)
            self.tick()

            self.latch_program_counter(True)
            self.tick()

        elif opcode == Opcode.NEG:
            self.latch_dr(-1)
            self.tick()
            res = self.alu_calculate(Opcode.MUL)
            self.latch_acc(res)
            self.tick()

            self.latch_program_counter(True)
            self.tick()

        elif opcode == Opcode.IN:
            self.device.read()
            val = ord(self.device.io)
            self.latch_acc(val)
            self.tick()

            self.latch_program_counter(True)
            self.tick()

        elif opcode == Opcode.OUT:
            val = chr(self.acc) if 255 >= self.acc >= 0 else self.acc
            self.device.io = val
            self.device.write()
            self.tick()

            self.latch_program_counter(True)
            self.tick()

        elif opcode == Opcode.JUMP:
            self.operand_fetch(term)

            self.latch_program_counter(False)
            self.tick()

        elif opcode == Opcode.LOOP:
            self.operand_fetch(term)
            if self.dr > 0:
                self.latch_program_counter(True)
                self.tick()
            self.latch_program_counter(True)
            self.tick()

        elif opcode == Opcode.BEQ:
            if self.zero_flag:
                self.operand_fetch(term)
                self.latch_program_counter(False)
            else:
                self.latch_program_counter(True)
            self.tick()

        elif opcode == Opcode.BNE:
            if not self.zero_flag:
                self.operand_fetch(term)
                self.latch_program_counter(False)
            else:
                self.latch_program_counter(True)
            self.tick()

        elif opcode == Opcode.BGE:
            # ~(n ^ v)
            if not self.negative_flag:
                self.operand_fetch(term)
                self.latch_program_counter(False)
            else:
                self.latch_program_counter(True)
            self.tick()

        elif opcode == Opcode.BLE:
            # z | (n ^ v)
            if self.zero_flag | self.negative_flag:
                self.operand_fetch(term)
                self.latch_program_counter(False)
            else:
                self.latch_program_counter(True)
            self.tick()

        elif opcode == Opcode.BL:
            # n ^ v
            if self.negative_flag:
                self.operand_fetch(term)
                self.latch_program_counter(False)
            else:
                self.latch_program_counter(True)
            self.tick()

        elif opcode == Opcode.BG:
            # ~(z | (n ^ v))
            if not (self.zero_flag | self.negative_flag):
                self.operand_fetch(term)
                self.latch_program_counter(False)
            else:
                self.latch_program_counter(True)
            self.tick()

        elif opcode == Opcode.DATA:
            self.latch_program_counter(True)
            self.tick()

    def __repr__(self):
        state = "{{TICK: {}, PC: {}, AR: {}, DR: {}, ACC: {}, IO: {}, N: {}, Z: {}}}".format(
            self.tact,
            self.program_counter,
            self.ar,
            self.dr,
            self.acc,
            self.device.io,
            self.negative_flag,
            self.zero_flag,
        )

        instr = self.memory[self.program_counter]
        opcode = instr['opcode']
        arg = instr['term'][1]
        arg_mode = instr['term'][2]
        action = "{{{}, {}, {}}}".format(
            opcode,
            arg,
            arg_mode
        )

        return "{} {}".format(state, action)


def simulation(input_buffer, instructions, limit):
    if len(instructions) > MEMORY_SIZE:
        raise MachineException('Program is too large')

    device = Device()
    device.load(input_buffer)
    control_unit = ControlUnit(instructions, device)

    instr_counter = 0
    try:
        while True:
            if instr_counter > limit:
                raise MachineException('Too long execution! Increase limit')

            logging.debug(control_unit)
            control_unit.decode_and_execute_instruction()
            instr_counter += 1
    except StopIteration:
        pass

    return device.output, control_unit.tact, instr_counter


def main(args):
    assert len(args) == 2, "Wrong arguments: machinery.py <code_file> <input_file>"
    code_file, input_file = args

    code = read_code(code_file)
    input_buffer = []
    with open(input_file, encoding="utf-8") as file:
        input_text = file.read()
        for char in input_text:
            input_buffer.append(char)
    input_buffer.append("\0")

    try:
        output, ticks, instructions = simulation(input_buffer, code, 10000000)
        print("Output:", output)
        print("Instructions:", instructions)
        print("Ticks:", ticks)
    except MachineException as exception:
        logging.error(exception.get_msg())


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    main(sys.argv[1:])
