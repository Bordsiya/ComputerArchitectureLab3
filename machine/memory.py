import enum


class DataRegisterType(enum.Enum):
    AC = "AC"
    DR = "DR"
    CR = "CR"


class AddressRegisterType(enum.Enum):
    IP = "IP"
    AR = "AR"


MEMORY_SIZE = 2048
WORD_SIZE = 32
WORD_INIT = 0
MAX_WORD = int(2 ** (WORD_SIZE - 1) - 1)
MIN_WORD = int(-2 ** (WORD_SIZE - 1))
MAX_ADDR = MEMORY_SIZE - 1


def check_data(data):
    return data


def check_addr(addr):
    if addr > MAX_ADDR:
        return addr % MAX_ADDR
    elif addr < 0:
        return (addr % MAX_ADDR + MAX_ADDR) % MAX_ADDR
    else:
        return addr


class Memory:

    def __init__(self):
        self.memory = [WORD_INIT] * MEMORY_SIZE
        self.negative_flag = 0
        self.zero_flag = 0
        self.overflow_flag = 0

        self.data_registers = {}
        for data_reg_type in DataRegisterType:
            self.data_registers[data_reg_type] = WORD_INIT
        self.addr_registers = {}
        for addr_reg_type in AddressRegisterType:
            self.data_registers[addr_reg_type] = WORD_INIT

    def set_data_registers(self, data_registers):
        self.data_registers = data_registers

    def set_addr_registers(self, addr_registers):
        self.addr_registers = addr_registers

    def __eval_flags(self, x: int):
        self.zero_flag = x == 0
        self.overflow_flag = x > MAX_WORD or x < MIN_WORD
        self.negative_flag = x < 0

    def update_memory(self, addr: int, value: int) -> None:
        self.memory[addr] = value

    def get_from_memory(self, addr: int) -> int:
        return self.memory[addr]

    def __change_data_register(self, data_register: DataRegisterType, value: int) -> None:
        self.data_registers[data_register] = value
        # self.__eval_flags(self.get_register(DataRegisterType.AC))

    def __change_addr_register(self, addr_register: AddressRegisterType, value: int) -> None:
        self.addr_registers[addr_register] = value
        # self.__eval_flags(self.get_register(DataRegisterType.AC))

    def inc_register(self, register) -> None:
        if register in DataRegisterType:
            self.__change_data_register(register, check_data(self.data_registers[register] + 1))
        elif register in AddressRegisterType:
            self.__change_addr_register(register, check_addr(self.addr_registers[register] + 1))

    def dec_register(self, register) -> None:
        if register in DataRegisterType:
            self.__change_data_register(register, check_data(self.data_registers[register] - 1))
        elif register in AddressRegisterType:
            self.__change_addr_register(register, check_addr(self.addr_registers[register] - 1))

    def add_register(self, register, value: int) -> None:
        if register in DataRegisterType:
            self.__change_data_register(register, check_data(self.data_registers[register] + value))
        elif register in AddressRegisterType:
            self.__change_addr_register(register, check_addr(self.addr_registers[register] + value))

    def sub_register(self, register, value: int) -> None:
        if register in DataRegisterType:
            self.__change_data_register(register, check_data(self.data_registers[register] - value))
        elif register in AddressRegisterType:
            self.__change_addr_register(register, check_addr(self.addr_registers[register] - value))

    def mul_register(self, register, value: int) -> None:
        if register in DataRegisterType:
            self.__change_data_register(register, check_data(self.data_registers[register] * value))
        elif register in AddressRegisterType:
            self.__change_addr_register(register, check_addr(self.addr_registers[register] * value))

    def div_register(self, register, value: int) -> None:
        if register in DataRegisterType:
            self.__change_data_register(register, check_data(self.data_registers[register] / value))
        elif register in AddressRegisterType:
            self.__change_addr_register(register, check_addr(self.addr_registers[register] / value))

    def mod_register(self, register, value: int) -> None:
        if register in DataRegisterType:
            self.__change_data_register(register, check_data(self.data_registers[register] % value))
        elif register in AddressRegisterType:
            self.__change_addr_register(register, check_addr(self.addr_registers[register] % value))

    def cmp_register(self, register, value: int):
        if register in DataRegisterType:
            self.__eval_flags(check_data(self.data_registers[register] - value))
        elif register in AddressRegisterType:
            self.__eval_flags(check_addr(self.addr_registers[register] - value))

    def update_register(self, register, value: int) -> None:
        if register in DataRegisterType:
            self.__change_data_register(register, check_data(value))
        elif register in AddressRegisterType:
            self.__change_addr_register(register, check_addr(value))

    def get_register(self, register) -> int:
        if register in DataRegisterType:
            return self.data_registers[register]
        elif register in AddressRegisterType:
            return self.addr_registers[register]
