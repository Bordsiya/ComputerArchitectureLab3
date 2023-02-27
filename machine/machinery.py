import sys

from machine.session import Session
from translator.isa import read_code


def simulation(input_buffer, instructions):
    session = Session()
    session.device.input = input_buffer
    session.load(instructions)
    try:
        session.run(0)
    except EOFError:
        pass
    output = session.device.output
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

    print(simulation(input_buffer, code))

    sum = 0
    i = 0
    while i < 1000:
        if i % 3 == 0 and i % 5 == 0:
            sum += 1
        i += 1
    print(sum)


if __name__ == '__main__':
    # logging.getLogger().setLevel(logging.DEBUG)
    main(sys.argv[1:])
