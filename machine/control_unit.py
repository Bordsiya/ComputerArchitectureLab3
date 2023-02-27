from machine.addressed_commands import AddressedCommandType
from machine.memory import DataRegisterType, AddressRegisterType
from machine.unaddressed_commands import UnaddressedCommandType
from translator.isa import Opcode, AddressingMode, Term
from utils import mask11, bit, mask8


class ControlUnit:

    def __init__(self, tact_generator, memory, device):
        self.tact_generator = tact_generator
        self.memory = memory
        self.device = device
        self.instruction = {}

        self.logs = []

    def clean_logs(self):
        self.logs = []

    def log(self):
        self.logs += (self.tact_generator.tact, self.memory.data_registers, self.memory.addr_registers)

    def set_start_ip(self):
        self.memory.update_register(AddressRegisterType.IP, self.device.io)
        self.tact_generator.tick()

    def input(self):
        self.memory.update_register(DataRegisterType.DR, self.device.io)
        self.memory.update_register(AddressRegisterType.AR, self.memory.get_register(AddressRegisterType.IP))
        self.tact_generator.tick()

        self.memory.inc_register(AddressRegisterType.IP)
        self.memory.update_memory(self.memory.get_register(AddressRegisterType.AR), self.memory.get_register(DataRegisterType.DR))
        self.tact_generator.tick()

    def operand_fetch(self, term):
        if term[2] == AddressingMode.ABSOLUTE:
            self.memory.update_register(DataRegisterType.DR, int(term[1]))
            self.tact_generator.tick()
            self.load_with_dr()
        elif term[2] == AddressingMode.DIRECT:
            self.memory.update_register(DataRegisterType.DR, int(term[1]))
            self.tact_generator.tick()
        else:
            self.memory.update_register(DataRegisterType.DR, int(term[1]))
            self.tact_generator.tick()
            self.load_with_dr()

            self.memory.update_register(DataRegisterType.DR, mask11(self.memory.get_register(DataRegisterType.DR)))
            self.tact_generator.tick()
            self.load_with_dr()

    def command_fetch(self):
        print("----------------------------")
        print('memory: ', self.memory.memory)
        print('ac: ', self.memory.get_register(DataRegisterType.AC))
        print('dr: ', self.memory.get_register(DataRegisterType.DR))
        print('flag_z: ', self.memory.zero_flag)
        print('flag_neg: ', self.memory.negative_flag)
        print('flag_ov: ', self.memory.overflow_flag)
        self.instruction = self.load_with_ip()
        self.memory.inc_register(AddressRegisterType.IP)
        # print('ip: ', self.memory.get_register(AddressRegisterType.IP))
        # print('dr: ', self.memory.get_register(DataRegisterType.DR))
        # print('cr: ', self.memory.get_register(DataRegisterType.CR))
        # self.memory.update_register(DataRegisterType.CR, self.memory.get_register(DataRegisterType.DR))
        # self.tact_generator.tick()

        # instr = self.memory.get_register(DataRegisterType.CR)
        print("instr: ", self.instruction)
        command = self.instruction['opcode']
        term = self.instruction['term']

        if command == Opcode.NOP:
            self.nop_instr()
        elif command == Opcode.HLT:
            self.hlt_instr()
        elif command == Opcode.CLA:
            self.cla_instr()
        elif command == Opcode.IN:
            self.in_instr()
        elif command == Opcode.OUT:
            self.out_instr()
        elif command == Opcode.INC:
            self.inc_instr()
        elif command == Opcode.DEC:
            self.dec_instr()
        elif command == Opcode.NEG:
            self.neg_instr()

        elif command == Opcode.DATA:
            self.command_fetch()

        else:
            if command == Opcode.ADD:
                self.operand_fetch(term)
                self.add_instr()
            elif command == Opcode.SUB:
                self.operand_fetch(term)
                self.sub_instr()
            elif command == Opcode.DIV:
                self.operand_fetch(term)
                self.div_instr()
            elif command == Opcode.MUL:
                self.operand_fetch(term)
                self.mul_instr()
            elif command == Opcode.MOD:
                self.operand_fetch(term)
                self.mod_instr()
            elif command == Opcode.CMP:
                self.operand_fetch(term)
                self.cmp_inst()
            elif command == Opcode.LOOP:
                self.operand_fetch(term)
                self.loop_instr()
            elif command == Opcode.LD:
                self.operand_fetch(term)
                self.ld_instr()
            elif command == Opcode.ST:
                self.st_instr()
            elif command == Opcode.JUMP:
                self.jump_instr()
            elif command == Opcode.BEQ:
                self.beq_instr()
            elif command == Opcode.BNE:
                self.bne_instr()
            elif command == Opcode.BGE:
                self.bge_instr()
            elif command == Opcode.BLE:
                self.ble_instr()
            elif command == Opcode.BL:
                self.bl_instr()
            elif command == Opcode.BG:
                self.bg_instr()

    def load_with_ip(self):
        self.memory.update_register(AddressRegisterType.AR, self.memory.get_register(AddressRegisterType.IP))
        return self.memory.get_from_memory(self.memory.get_register(AddressRegisterType.AR))

    def load_with_dr(self):
        self.memory.update_register(AddressRegisterType.AR, self.memory.get_register(DataRegisterType.DR))
        self.tact_generator.tick()
        self.memory.update_register(DataRegisterType.DR,
                                    self.memory.get_from_memory(self.memory.get_register(AddressRegisterType.AR))['term'][1])
        self.tact_generator.tick()

    def add_instr(self):
        self.memory.add_register(DataRegisterType.AC, self.memory.get_register(DataRegisterType.DR))
        self.tact_generator.tick()
        self.log()
        self.command_fetch()

    def sub_instr(self):
        self.memory.sub_register(DataRegisterType.AC, self.memory.get_register(DataRegisterType.DR))
        self.tact_generator.tick()
        self.log()
        self.command_fetch()

    def mul_instr(self):
        self.memory.mul_register(DataRegisterType.AC, self.memory.get_register(DataRegisterType.DR))
        self.tact_generator.tick()
        self.log()
        self.command_fetch()

    def div_instr(self):
        self.memory.div_register(DataRegisterType.AC, self.memory.get_register(DataRegisterType.DR))
        self.tact_generator.tick()
        self.log()
        self.command_fetch()

    def mod_instr(self):
        self.memory.mod_register(DataRegisterType.AC, self.memory.get_register(DataRegisterType.DR))
        self.tact_generator.tick()
        self.log()
        self.command_fetch()

    def loop_instr(self):
        if self.memory.get_register(DataRegisterType.DR) > 0:
            self.memory.inc_register(AddressRegisterType.IP)
        self.tact_generator.tick()
        self.log()
        self.command_fetch()

    def ld_instr(self):
        self.memory.update_register(DataRegisterType.AC, self.memory.get_register(DataRegisterType.DR))
        self.tact_generator.tick()
        self.log()
        self.command_fetch()

    def st_instr(self):
        self.memory.update_register(DataRegisterType.DR, self.instruction['term'][1])
        self.memory.update_register(AddressRegisterType.AR, self.memory.get_register(DataRegisterType.DR))
        self.memory.update_register(DataRegisterType.DR, self.memory.get_register(DataRegisterType.AC))
        self.tact_generator.tick()
        self.memory.update_memory(self.memory.get_register(AddressRegisterType.AR),
                                  {'opcode': Opcode.DATA,
                                   'term': Term(self.memory.get_register(AddressRegisterType.AR),
                                                self.memory.get_register(DataRegisterType.DR), AddressingMode.DIRECT)})
        self.tact_generator.tick()
        self.log()
        self.command_fetch()

    def hlt_instr(self):
        self.log()
        raise EOFError("Program finished by HLT.")

    def cla_instr(self):
        self.memory.update_register(DataRegisterType.AC, 0)
        self.tact_generator.tick()
        self.log()
        self.command_fetch()

    def inc_instr(self):
        self.memory.inc_register(DataRegisterType.AC)
        self.tact_generator.tick()
        self.log()
        self.command_fetch()

    def dec_instr(self):
        self.memory.dec_register(DataRegisterType.AC)
        self.tact_generator.tick()
        self.log()
        self.command_fetch()

    def out_instr(self):
        self.device.io = self.memory.get_register(DataRegisterType.AC)
        self.device.write()
        self.tact_generator.tick()
        self.log()
        self.command_fetch()

    def in_instr(self):
        self.device.read()
        self.memory.update_register(DataRegisterType.AC, ord(self.device.io))
        self.tact_generator.tick()
        self.log()
        self.command_fetch()

    def nop_instr(self):
        self.log()
        self.command_fetch()

    def neg_instr(self):
        self.memory.mul_register(DataRegisterType.AC, -1)
        self.tact_generator.tick()
        self.log()
        self.command_fetch()

    def cmp_inst(self):
        self.memory.cmp_register(DataRegisterType.AC, self.memory.get_register(DataRegisterType.DR))
        self.log()
        self.command_fetch()

    def jump_instr(self):
        self.memory.update_register(DataRegisterType.DR, mask11(self.instruction['term'][1]))
        self.tact_generator.tick()
        self.memory.update_register(AddressRegisterType.IP, self.memory.get_register(DataRegisterType.DR))
        self.tact_generator.tick()
        self.log()
        self.command_fetch()

    def beq_instr(self):
        if self.memory.zero_flag:
            self.jump_instr()
        else:
            self.log()
            self.command_fetch()

    def bne_instr(self):
        if not self.memory.zero_flag:
            self.jump_instr()
        else:
            self.log()
            self.command_fetch()

    def bge_instr(self):
        if not (self.memory.negative_flag ^ self.memory.overflow_flag):
            self.jump_instr()
        else:
            self.log()
            self.command_fetch()

    def ble_instr(self):
        if self.memory.zero_flag | (self.memory.negative_flag ^ self.memory.overflow_flag):
            self.jump_instr()
        else:
            self.log()
            self.command_fetch()

    def bl_instr(self):
        if self.memory.negative_flag ^ self.memory.overflow_flag:
            self.jump_instr()
        else:
            self.log()
            self.command_fetch()

    def bg_instr(self):
        if not (self.memory.zero_flag | (self.memory.negative_flag ^ self.memory.overflow_flag)):
            self.jump_instr()
        else:
            self.log()
            self.command_fetch()
