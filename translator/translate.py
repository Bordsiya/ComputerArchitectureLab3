import sys

from translator.isa import write_code
from translator.lex import Lexer
from translator.parse import Parser


def main(args):
    assert len(args) == 2, "Wrong arguments: translate.py <input_file> <target_file>"
    source, target = args

    with open(source, "rt", encoding="utf-8") as f:
        source = f.read()

    lexer = Lexer(source)
    parser = Parser(lexer)

    code = parser.program()
    print("source LoC:", len(source.split("\n")), "| code instr:", len(code))
    write_code(target, code)


if __name__ == '__main__':
    main(sys.argv[1:])
