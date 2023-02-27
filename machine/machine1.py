import logging
import sys

from translator.isa import Opcode, AddressingMode, read_code

WORD_SIZE = 32
MAX_WORD = int(2 ** (WORD_SIZE - 1) - 1)
MIN_WORD = int(-2 ** (WORD_SIZE - 1))
MEMORY_SIZE = 2048


class DataPath:
    def __init__(self, memory_size, input_buffer):
        assert memory_size > 0, "Data_memory size should be non-zero"
        self.memory_size = memory_size
        self.memory = [] * memory_size
        self.addr = 0
        self.acc = 0
        self.ip = 0
        self.step_counter = 0
        self.input_buffer = input_buffer
        self.output_buffer = []

        self.zero = True
        self.overflow = False
        self.negative = False

    def latch_dr(self, term):
        if term[2] == AddressingMode.DIRECT:
            self.dr = term[1]
        elif term[2] == AddressingMode.ABSOLUTE:
            self.dr = self.memory[term[1]]['term'][1]
        else:
            self.dr = self.memory[term[1]]['term'][1]
            self.dr = self.memory[self.dr]['term'][1]

    def latch_acc(self):
        self.acc = self.dr


class ControlUnit():
    def __init__(self, program, data_path):
        self.program = program
        self.data_path = data_path
        self.program_counter = 0
        self._tick = 0

    def tick(self):
        """Счётчик тактов процессора. Вызывается при переходе на следующий такт."""
        self._tick += 1

    def current_tick(self):
        return self._tick

    def latch_program_counter(self, sel_next):
        if sel_next:
            self.program_counter += 1
        else:
            instr = self.program[self.program_counter]
            assert 'arg' in instr, "internal error"
            self.program_counter = instr["arg"]

    def decode_and_execute_instruction(self):
        instr = self.program[self.program_counter]
        opcode = instr["opcode"]
        term = instr['term']

        if opcode is Opcode.HALT:
            raise StopIteration()

        if opcode is Opcode.LD:
            self.data_path.latch_dr(term)
            self.tick()
            self.data_path.latch_acc()
            self.tick()
            self.latch_program_counter(True)

        if opcode is Opcode.ST:
            self.data_path.latch_dr(term)
            self.tick()

    def __repr__(self):
        state = "{{TICK: {}, PC: {}, ADDR: {}, OUT: {}, ACC: {}}}".format(
            self._tick,
            self.program_counter,
            self.data_path.data_address,
            self.data_path.data_memory[self.data_path.data_address],
            self.data_path.acc,
        )

        instr = self.program[self.program_counter]
        opcode = instr["opcode"]
        term = instr['term']
        line = term[0]
        arg = term[1]
        mode = term[2]
        action = "xxx"
        if term is not None:
            action = "{} {} {} {}".format(opcode, line, arg, mode)

        return "{} {}".format(state, action)


def simulation(code, input_tokens, data_memory_size, limit):
    """Запуск симуляции процессора.

    Длительность моделирования ограничена количеством выполненных инструкций.
    """
    data_path = DataPath1(data_memory_size, input_tokens)
    control_unit = ControlUnit(code, data_path)
    instr_counter = 0

    logging.debug('%s', control_unit)
    try:
        while True:
            assert limit > instr_counter, "too long execution, increase limit!"
            control_unit.decode_and_execute_instruction()
            instr_counter += 1
            logging.debug('%s', control_unit)
    except EOFError:
        logging.warning('Input buffer is empty!')
    except StopIteration:
        pass
    logging.info('output_buffer: %s', repr(''.join(data_path.output_buffer)))
    return ''.join(data_path.output_buffer), instr_counter, control_unit.current_tick()


def main(args):
    assert len(args) == 2, "Wrong arguments: machine.py <code_file> <input_file>"
    code_file, input_file = args

    code = read_code(code_file)
    with open(input_file, encoding="utf-8") as file:
        input_text = file.read()
        input_token = []
        for char in input_text:
            input_token.append(char)

    output, instr_counter, ticks = simulation(code,
                                              input_tokens=input_token,
                                              data_memory_size=100, limit=1000)

    print(''.join(output))
    print("instr_counter: ", instr_counter, "ticks:", ticks)


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    main(sys.argv[1:])







