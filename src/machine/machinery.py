# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=too-many-instance-attributes
# pylint: disable=logging-fstring-interpolation
# pylint: disable=logging-not-lazy
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements

import enum
import logging
import sys

from src.exceptions import MachineException
from src.machine.config import MEMORY_SIZE, WORD_INIT, START_ADDR, MAX_WORD, MIN_WORD
from src.isa import read_code, Opcode, AddressingMode
from src.machine.device import Device


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

    def __init__(self, program: list, device: Device):
        self.memory = program
        for _ in range(len(self.memory), MEMORY_SIZE):
            self.memory.append({'opcode': Opcode.DATA, 'arg': WORD_INIT, 'arg_mode': AddressingMode.DIRECT})

        self.program_counter = START_ADDR
        self.acc = 0
        self.addr_reg = 0
        self.data_reg = 0
        self.tact = 0
        self.device = device
        self.zero_flag = False
        self.negative_flag = False

    def __tick(self):
        self.tact += 1

    def set_zero_flag(self, val: int):
        self.zero_flag = val == 0

    def set_negative_flag(self, val: int):
        self.negative_flag = val < 0

    def latch_addr_reg(self, val: int):
        self.addr_reg = int(val)

    def latch_data_reg(self, val: int):
        self.data_reg = int(val)

    def latch_acc(self, val: int):
        self.acc = int(val)

    def latch_program_counter(self, sel_next: bool):
        if sel_next:
            self.program_counter += 1
        else:
            self.program_counter = self.data_reg

    @staticmethod
    def check_value(val: int):
        if val > MAX_WORD or val < MIN_WORD:
            raise MachineException('Overflow error!')
        return val

    def alu_calculate(self, operation: AluOperation, sel_left: bool = True, sel_right: bool = True):
        left_operand = self.acc if sel_left else 0
        right_operand = self.data_reg if sel_right else 0
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

    def operand_fetch(self, arg: int, arg_mode: AddressingMode):
        if arg_mode == AddressingMode.DIRECT:
            self.latch_data_reg(arg)
            self.__tick()
        elif arg_mode == AddressingMode.ABSOLUTE:
            self.latch_addr_reg(arg)
            self.__tick()
            self.latch_data_reg(self.memory[self.addr_reg]['arg'])
            self.__tick()
        elif arg_mode == AddressingMode.RELATIVE:
            self.latch_addr_reg(arg)
            self.__tick()
            self.latch_data_reg(self.memory[self.addr_reg]['arg'])
            self.__tick()
            self.latch_addr_reg(self.data_reg)
            self.__tick()
            self.latch_data_reg(self.memory[self.addr_reg]['arg'])
            self.__tick()

    def decode_and_execute_instruction(self):
        instr = self.memory[self.program_counter]
        opcode = instr['opcode']
        arg = instr['arg'] if 'arg' in instr else None
        arg_mode = instr['arg_mode'] if 'arg' in instr else None

        if opcode is Opcode.HLT:
            raise StopIteration()

        if opcode is Opcode.NOP:
            self.latch_program_counter(True)
            self.__tick()

        elif opcode is Opcode.LD:
            self.operand_fetch(arg, arg_mode)
            res = self.alu_calculate(AluOperation.ADD, False)
            self.latch_acc(res)
            self.__tick()

            self.latch_program_counter(True)
            self.__tick()

        elif opcode is Opcode.ST:
            self.latch_addr_reg(arg)
            self.__tick()
            self.memory[self.addr_reg] = {'opcode': Opcode.DATA, 'arg': self.acc, 'arg_mode': AddressingMode.DIRECT}
            self.__tick()

            self.latch_program_counter(True)
            self.__tick()

        elif opcode in [Opcode.ADD, Opcode.SUB, Opcode.MUL, Opcode.DIV, Opcode.MOD, Opcode.CMP]:
            self.operand_fetch(arg, arg_mode)
            res = self.alu_calculate(opcode_to_alu_operation[opcode])
            if opcode not in Opcode.CMP:
                self.latch_acc(res)
            self.__tick()

            self.latch_program_counter(True)
            self.__tick()

        elif opcode == Opcode.INC:
            self.latch_data_reg(1)
            self.__tick()
            res = self.alu_calculate(AluOperation.ADD)
            self.latch_acc(res)
            self.__tick()

            self.latch_program_counter(True)
            self.__tick()

        elif opcode == Opcode.DEC:
            self.latch_data_reg(-1)
            self.__tick()
            res = self.alu_calculate(AluOperation.ADD)
            self.latch_acc(res)
            self.__tick()

            self.latch_program_counter(True)
            self.__tick()

        elif opcode == Opcode.CLA:
            self.latch_acc(0)
            self.__tick()

            self.latch_program_counter(True)
            self.__tick()

        elif opcode == Opcode.NEG:
            self.latch_data_reg(-1)
            self.__tick()
            res = self.alu_calculate(AluOperation.MUL)
            self.latch_acc(res)
            self.__tick()

            self.latch_program_counter(True)
            self.__tick()

        elif opcode == Opcode.IN:
            self.device.read()
            val = ord(self.device.io)
            logging.info(f"{{info_buffer: {self.device.input} >> {val}}}")
            self.latch_acc(val)
            self.__tick()

            self.latch_program_counter(True)
            self.__tick()

        elif opcode == Opcode.OUTC:
            val = chr(self.acc)
            self.device.io = val
            self.device.write()
            logging.info(f"{{output_buffer: {self.device.output} << {val}}}")
            self.__tick()

            self.latch_program_counter(True)
            self.__tick()

        elif opcode == Opcode.OUT:
            val = str(self.acc)
            self.device.io = val
            self.device.write()
            logging.info(f"{{output_buffer: {self.device.output} << {val}}}")
            self.__tick()

            self.latch_program_counter(True)
            self.__tick()

        elif opcode == Opcode.JUMP:
            self.operand_fetch(arg, arg_mode)

            self.latch_program_counter(False)
            self.__tick()

        elif opcode == Opcode.LOOP:
            self.operand_fetch(arg, arg_mode)
            if self.data_reg > 0:
                self.latch_program_counter(True)
                self.__tick()
            self.latch_program_counter(True)
            self.__tick()

        elif opcode == Opcode.BEQ:
            if self.zero_flag:
                self.operand_fetch(arg, arg_mode)
                self.latch_program_counter(False)
            else:
                self.latch_program_counter(True)
            self.__tick()

        elif opcode == Opcode.BNE:
            if not self.zero_flag:
                self.operand_fetch(arg, arg_mode)
                self.latch_program_counter(False)
            else:
                self.latch_program_counter(True)
            self.__tick()

        elif opcode == Opcode.BGE:
            # ~(n ^ v)
            if not self.negative_flag:
                self.operand_fetch(arg, arg_mode)
                self.latch_program_counter(False)
            else:
                self.latch_program_counter(True)
            self.__tick()

        elif opcode == Opcode.BLE:
            # z | (n ^ v)
            if self.zero_flag | self.negative_flag:
                self.operand_fetch(arg, arg_mode)
                self.latch_program_counter(False)
            else:
                self.latch_program_counter(True)
            self.__tick()

        elif opcode == Opcode.BL:
            # n ^ v
            if self.negative_flag:
                self.operand_fetch(arg, arg_mode)
                self.latch_program_counter(False)
            else:
                self.latch_program_counter(True)
            self.__tick()

        elif opcode == Opcode.BG:
            # ~(z | (n ^ v))
            if not self.zero_flag | self.negative_flag:
                self.operand_fetch(arg, arg_mode)
                self.latch_program_counter(False)
            else:
                self.latch_program_counter(True)
            self.__tick()

        elif opcode == Opcode.DATA:
            self.latch_program_counter(True)
            self.__tick()

    def __repr__(self):
        state = f"{{TICK: {self.tact}, PC: {self.program_counter}, AR: {self.addr_reg}, DR: {self.data_reg}" \
                f", ACC: {self.acc}, IO: {self.device.io}, N: {self.negative_flag}, Z: {self.zero_flag}}}"

        instr = self.memory[self.program_counter]
        opcode = instr['opcode']
        if 'arg' in instr:
            arg = instr['arg']
            arg_mode = instr['arg_mode']
            action = f"{{{opcode}, {arg}, {arg_mode}}}"
        else:
            action = f"{{{opcode}}}"

        return f"{state} {action}"


def simulation(input_buffer: list, instructions: list, limit: int):
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
        output, ticks, instructions = simulation(input_buffer, code, 100000)
        print("Output:", ''.join(output))
        print("Instructions:", instructions)
        print("Ticks:", ticks)
    except MachineException as exception:
        logging.error(exception.get_msg())


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    main(sys.argv[1:])
