import enum
import logging
import sys

from exceptions.exceptions import MachineException
from machine.device import Device
from machine1.config import MEMORY_SIZE, WORD_INIT, START_ADDR, MAX_WORD, MIN_WORD
from translator.isa import read_code, Opcode, Term, AddressingMode, addressed_commands


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


class ControlUnit1:

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
        self.overflow_flag = False

    def tick(self):
        self.tact += 1

    def set_zero_flag(self, val: int):
        self.zero_flag = val == 0

    def set_negative_flag(self, val: int):
        self.negative_flag = val < 0

    def set_overflow_flag(self, val: int):
        self.overflow_flag = val > MAX_WORD or val < MIN_WORD

    def set_ar(self, val: int):
        self.ar = int(val)

    def set_dr(self, val: int):
        self.dr = int(val)

    def latch_acc(self, val: int):
        self.acc = int(val)

    def latch_program_counter(self, sel_next):
        if sel_next:
            self.program_counter += 1
        else:
            self.program_counter = self.dr

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
        self.set_overflow_flag(res)
        return res

    def operand_fetch(self, term):
        if term[2] == AddressingMode.DIRECT:
            self.set_dr(term[1])
            self.tick()
        elif term[2] == AddressingMode.ABSOLUTE:
            self.set_ar(term[1])
            self.tick()
            self.dr = self.memory[self.ar]['term'][1]
            self.tick()
        elif term[2] == AddressingMode.RELATIVE:
            self.set_ar(term[1])
            self.tick()
            self.set_dr(self.memory[self.ar]['term'][1])
            self.tick()
            self.set_ar(self.dr)
            self.tick()
            self.set_dr(self.memory[self.ar]['term'][1])
            self.tick()

    def decode_and_execute_instruction(self):
        instr = self.memory[self.program_counter]
        opcode = instr["opcode"]
        term = instr['term']

        if opcode is Opcode.HLT:
            raise StopIteration()

        elif opcode is Opcode.NOP:
            self.latch_program_counter(True)

        elif opcode is Opcode.LD:
            self.operand_fetch(term)
            res = self.alu_calculate(AluOperation.ADD, False)
            self.latch_acc(res)
            self.tick()

            self.latch_program_counter(True)

        elif opcode is Opcode.ST:
            self.set_ar(term[1])
            self.tick()
            self.memory[self.ar] = {'opcode': Opcode.DATA, 'term': Term(self.ar, self.acc, AddressingMode.DIRECT)}
            self.tick()

            self.latch_program_counter(True)

        elif opcode in [Opcode.ADD, Opcode.SUB, Opcode.MUL, Opcode.DIV, Opcode.MOD, Opcode.CMP]:
            self.operand_fetch(term)
            res = self.alu_calculate(opcode_to_alu_operation[opcode])
            if opcode not in Opcode.CMP:
                self.latch_acc(res)
            self.tick()

            self.latch_program_counter(True)

        elif opcode == Opcode.INC:
            self.set_dr(1)
            self.tick()
            res = self.alu_calculate(Opcode.ADD)
            self.latch_acc(res)
            self.tick()

            self.latch_program_counter(True)

        elif opcode == Opcode.DEC:
            self.set_dr(-1)
            self.tick()
            res = self.alu_calculate(Opcode.ADD)
            self.latch_acc(res)
            self.tick()

            self.latch_program_counter(True)

        elif opcode == Opcode.CLA:
            self.latch_acc(0)
            self.tick()

            self.latch_program_counter(True)

        elif opcode == Opcode.NEG:
            self.set_dr(-1)
            self.tick()
            res = self.alu_calculate(Opcode.MUL)
            self.latch_acc(res)
            self.tick()

            self.latch_program_counter(True)

        elif opcode == Opcode.IN:
            self.device.read()
            val = ord(self.device.io)
            self.latch_acc(val)
            self.tick()

            self.latch_program_counter(True)

        elif opcode == Opcode.OUT:
            val = chr(self.acc) if 255 >= self.acc >= 0 else self.acc
            self.device.io = val
            self.device.write()
            self.tick()

            self.latch_program_counter(True)

        elif opcode == Opcode.JUMP:
            self.operand_fetch(term)

            self.latch_program_counter(False)

        elif opcode == Opcode.LOOP:
            self.operand_fetch(term)
            if self.dr > 0:
                self.latch_program_counter(True)
            self.latch_program_counter(True)

        elif opcode == Opcode.BEQ:
            if self.zero_flag:
                self.operand_fetch(term)
                self.latch_program_counter(False)
            else:
                self.latch_program_counter(True)

        elif opcode == Opcode.BNE:
            if not self.zero_flag:
                self.operand_fetch(term)
                self.latch_program_counter(False)
            else:
                self.latch_program_counter(True)

        elif opcode == Opcode.BGE:
            if not (self.negative_flag ^ self.overflow_flag):
                self.operand_fetch(term)
                self.latch_program_counter(False)
            else:
                self.latch_program_counter(True)

        elif opcode == Opcode.BLE:
            if self.zero_flag | (self.negative_flag ^ self.overflow_flag):
                self.operand_fetch(term)
                self.latch_program_counter(False)
            else:
                self.latch_program_counter(True)

        elif opcode == Opcode.BL:
            if self.negative_flag ^ self.overflow_flag:
                self.operand_fetch(term)
                self.latch_program_counter(False)
            else:
                self.latch_program_counter(True)

        elif opcode == Opcode.BG:
            if not (self.zero_flag | (self.negative_flag ^ self.overflow_flag)):
                self.operand_fetch(term)
                self.latch_program_counter(False)
            else:
                self.latch_program_counter(True)

        elif opcode == Opcode.DATA:
            self.latch_program_counter(True)

    def __repr__(self):
        state = "{{TICK: {}, PC: {}, AR: {}, DR: {}, ACC: {}, IO: {}, N: {}, Z: {}, V: {}}}".format(
            self.tact,
            self.program_counter,
            self.ar,
            self.dr,
            self.acc,
            self.device.io,
            self.negative_flag,
            self.zero_flag,
            self.overflow_flag
        )

        instr = self.memory[self.program_counter]
        opcode = instr['opcode']
        line = instr['term'][0]
        arg = instr['term'][1]
        arg_mode = instr['term'][2]
        action = "{{{}, {}, {}, {}}}".format(
            opcode,
            line,
            arg,
            arg_mode
        )

        return "{} {}".format(state, action)


def simulation(input_buffer, instructions, limit):
    if len(instructions) > MEMORY_SIZE:
        raise MachineException('Program is too large')
    device = Device()
    device.input = input_buffer
    control_unit = ControlUnit1(instructions, device)

    logging.debug(control_unit)
    instr_counter = 0
    try:
        while True:
            if instr_counter > limit:
                raise MachineException('Too long execution! Increase limit')
            control_unit.decode_and_execute_instruction()
            instr_counter += 1
            logging.debug(control_unit)
            logging.debug(control_unit.memory[0:14])
    except StopIteration:
        pass

    output = device.output
    return output


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

    print(code)
    print(input_buffer)

    try:
        print(simulation(input_buffer, code, 10000000))
    except MachineException as exception:
        logging.error(exception.get_msg())


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    main(sys.argv[1:])
